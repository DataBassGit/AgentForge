import os
import time
import json
import struct
import shutil
import sqlite3
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Dict, List, Tuple, Optional

# Setup standalone logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("ChromaRecover")


class RecoveryStats:
    """Tracks and formats live statistics during the recovery process."""

    def __init__(self, total_items: int):
        self.total_items = total_items
        self.items_fixed = 0
        self.start_time = time.time()

    def update(self, count: int):
        self.items_fixed += count
        elapsed = time.time() - self.start_time

        rate = self.items_fixed / elapsed if elapsed > 0 else 0
        remaining = self.total_items - self.items_fixed
        eta_seconds = remaining / rate if rate > 0 else 0

        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
        percent = (self.items_fixed / self.total_items) * 100 if self.total_items > 0 else 100

        print(f"\r[Recovery Progress] "
              f"Fixed: {self.items_fixed}/{self.total_items} ({percent:.1f}%) | "
              f"Rate: {rate:.1f} items/sec | "
              f"ETA: {eta_str}", end="", flush=True)

    def finish(self):
        elapsed = time.time() - self.start_time
        print(f"\n[Recovery Complete] Restored {self.items_fixed} vectors in {elapsed:.2f} seconds.")


def get_collection_info(db_path: str, collection_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Queries SQLite to find the canonical UUIDs for a collection and its vector segment."""
    sqlite_path = os.path.join(db_path, "chroma.sqlite3")
    if not os.path.exists(sqlite_path):
        logger.error(f"Could not find chroma.sqlite3 at user-provided path: {db_path}")
        return None, None

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM collections WHERE name = ?", (collection_name,))
        row = cursor.fetchone()
        if not row:
            logger.error(f"Collection '{collection_name}' not found in SQLite table.")
            return None, None
        collection_uuid = row[0]

        try:
            cursor.execute("SELECT id FROM segments WHERE collection = ? AND scope = 'VECTOR'", (collection_uuid,))
            seg_row = cursor.fetchone()
            segment_uuid = seg_row[0] if seg_row else None
        except sqlite3.OperationalError:
            segment_uuid = None

        return collection_uuid, segment_uuid
    except sqlite3.Error as e:
        logger.error(f"SQLite error while looking up collection: {e}")
        return None, None
    finally:
        conn.close()


def backup_target_files(db_path: str, segment_uuid: Optional[str]) -> str:
    """Backs up only the specific files being modified to a .dbbackup directory."""
    sqlite_path = os.path.join(db_path, "chroma.sqlite3")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(db_path, '.dbbackup', f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    try:
        shutil.copy2(sqlite_path, backup_dir)
        logger.info(f"Backed up chroma.sqlite3 to {backup_dir}")

        if segment_uuid:
            hnsw_dir = os.path.join(db_path, segment_uuid)
            if os.path.exists(hnsw_dir):
                shutil.copytree(hnsw_dir, os.path.join(backup_dir, segment_uuid))
                logger.info(f"Backed up HNSW segment {segment_uuid}")

        return backup_dir
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise RuntimeError("Aborting recovery: Backup failed.")


def extract_raw_data(db_path: str, collection_uuid: str) -> Dict[str, List[Any]]:
    """Dynamically extracts IDs, Documents, and Metadata using exact schema bindings."""
    sqlite_path = os.path.join(db_path, "chroma.sqlite3")
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    data = {'ids': [], 'documents': [], 'metadatas': [], 'embeddings': []}

    logger.info("Extracting data based on exact DB Schema...")

    # 1. Map internal integer IDs to the user's string IDs
    cursor.execute("""
        SELECT e.id, e.embedding_id 
        FROM embeddings e 
        JOIN segments s ON e.segment_id = s.id 
        WHERE s.collection = ?
    """, (collection_uuid,))

    id_map = {row[0]: row[1] for row in cursor.fetchall()}
    internal_ids = list(id_map.keys())

    doc_dict = {}
    meta_dict = {}

    if internal_ids:
        chunk_size = 900
        for i in range(0, len(internal_ids), chunk_size):
            chunk = internal_ids[i:i + chunk_size]
            placeholders = ",".join(["?"] * len(chunk))

            # 2. Extract Metadata
            cursor.execute(f"""
                SELECT id, key, string_value, int_value, float_value, bool_value 
                FROM embedding_metadata 
                WHERE id IN ({placeholders})
            """, chunk)

            for row_id, key, str_val, int_val, float_val, bool_val in cursor.fetchall():
                # Determine value type dynamically
                if str_val is not None:
                    val = str_val
                elif int_val is not None:
                    val = int_val
                elif float_val is not None:
                    val = float_val
                elif bool_val is not None:
                    val = bool(bool_val)
                else:
                    val = None

                if key == "chroma:document":
                    doc_dict[row_id] = val
                else:
                    if row_id not in meta_dict:
                        meta_dict[row_id] = {}
                    meta_dict[row_id][key] = val

            # 3. Extract Documents from FTS Content table
            try:
                cursor.execute(f"""
                    SELECT id, c0 
                    FROM embedding_fulltext_search_content 
                    WHERE id IN ({placeholders})
                """, chunk)
                for row_id, doc in cursor.fetchall():
                    if row_id not in doc_dict:
                        doc_dict[row_id] = doc
            except sqlite3.OperationalError:
                pass

    # Assemble the final payload
    for internal_id, user_string_id in id_map.items():
        data['ids'].append(user_string_id)  # Pass the string ID back!
        data['documents'].append(doc_dict.get(internal_id, ""))

        meta = meta_dict.get(internal_id, {})
        if not meta:
            meta = {"source": "auto-recovered"}
        data['metadatas'].append(meta)

        data['embeddings'].append(None)  # Force Local SentenceTransformer to rebuild

    conn.close()
    return data


def recover_collection(client: Any, db_path: str, collection_name: str, embedding_function: Any = None) -> bool:
    print(f"\n--- Initiating Chroma Auto-Recovery for '{collection_name}' ---")

    col_uuid, seg_uuid = get_collection_info(db_path, collection_name)
    if not col_uuid:
        logger.error("Could not locate collection UUID in database.")
        return False

    logger.info("Safeguarding data...")
    backup_target_files(db_path, seg_uuid)

    logger.info("Extracting text and metadata from SQLite...")
    raw_data = extract_raw_data(db_path, col_uuid)
    total_records = len(raw_data.get('ids', []))

    if total_records == 0:
        logger.warning("No records found to recover in any segment.")
        return False

    try:
        logger.info(f"Deleting corrupted HNSW index...")
        client.delete_collection(name=collection_name)

        logger.info("Rebuilding collection framework...")
        new_col = client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    except Exception as e:
        logger.error(f"Failed to reset collection: {e}")
        return False

    logger.info("Injecting data and regenerating vectors (this may take a moment)...")
    batch_size = 500
    stats = RecoveryStats(total_items=total_records)

    for i in range(0, total_records, batch_size):
        end_idx = min(i + batch_size, total_records)

        batch_ids = raw_data['ids'][i:end_idx]
        batch_docs = raw_data['documents'][i:end_idx]
        batch_metas = raw_data['metadatas'][i:end_idx]

        new_col.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas
        )

        stats.update(end_idx - i)

    stats.finish()
    return True


def auto_recover(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "hnsw" in error_msg or "compactor" in error_msg:
                collection_name = kwargs.get('collection_name')
                if not collection_name and len(args) > 0:
                    collection_name = args[0]

                if collection_name and isinstance(collection_name, str):
                    logger.warning(f"Detected HNSW corruption in '{collection_name}'. Triggering Auto-Recovery...")

                    client = getattr(self, 'client', None)
                    db_path = getattr(self, 'db_path', None)
                    embedding_func = getattr(self, 'embedding', None)

                    # Manual Path Resolution Loop
                    while True:
                        if db_path and os.path.exists(os.path.join(db_path, "chroma.sqlite3")):
                            break

                        logger.error(f"Could not find 'chroma.sqlite3' in: {db_path}")
                        # Using logger.warning to bypass PyCharm's stream buffering issue on input()
                        logger.warning("\n" + "=" * 60)
                        logger.warning("CRITICAL: Manual Intervention Required for Auto-Recovery")
                        logger.warning("The recovery tool needs the exact folder containing 'chroma.sqlite3'.")
                        logger.warning("Example: C:\\AI\\AgentForge\\db")
                        logger.warning("=" * 60)

                        db_path = input("Enter the absolute path: ").strip()

                        if db_path.startswith('"') and db_path.endswith('"'):
                            db_path = db_path[1:-1]
                        elif db_path.startswith("'") and db_path.endswith("'"):
                            db_path = db_path[1:-1]

                    if not client:
                        logger.error("Auto-recover could not determine the client.")
                        raise e

                    success = recover_collection(client, db_path, collection_name, embedding_func)

                    if success:
                        logger.info("Recovery successful. Retrying original operation...")
                        return func(self, *args, **kwargs)
                    else:
                        logger.error("Auto-Recovery failed. Cannot complete operation.")
                        raise e
                else:
                    logger.error("Caught HNSW error but could not determine collection_name to repair.")
                    raise e
            else:
                raise e

    return wrapper