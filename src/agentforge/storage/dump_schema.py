import sqlite3
import os

# Point this at the active, restored database
DB_PATH = r"C:\AI\AgentForge\db\chroma.sqlite3"


def dump_schema():
    if not os.path.exists(DB_PATH):
        print(f"Could not find database at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    print(f"Inspecting Database: {DB_PATH}")
    print("=" * 50)

    for table in tables:
        print(f"TABLE: {table}")
        cursor.execute(f"PRAGMA table_info({table});")
        for col in cursor.fetchall():
            # col[1] is column name, col[2] is data type
            print(f"  - {col[1]} ({col[2]})")
        print("-" * 30)

    conn.close()


if __name__ == "__main__":
    dump_schema()