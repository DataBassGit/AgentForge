from typing import Optional, Union, Dict, Any, List
import re
from datetime import datetime

from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.agent import Agent
from agentforge.storage.memory import Memory
import agentforge.tools.semantic_chunk as chunker


class EpisodicMemory(Memory):
    """
    EpisodicMemory class for storing and retrieving memories related to specific events or interactions.
    
    This class provides:
    1. Storage of complete memory episodes with timestamps and contextual metadata
    2. Semantic chunk-based retrieval for finding relevant memories
    3. Smart consolidation of related memories
    4. Importance scoring for memories to prioritize retrieval
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initialize the EpisodicMemory storage.
        
        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Identifier for the collection (defaults to "episodic").
        """
        # If no collection_id is provided, use "episodic" as default
        if not collection_id:
            collection_id = "episodic"
            
        super().__init__(cog_name, persona, collection_id)
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()
        
        # Define collection names
        self.episodes_collection = f"{self.collection_name}_episodes"
        self.chunks_collection = f"{self.collection_name}_chunks"
        
        # Default settings
        self.importance_threshold = 0.7  # Threshold for deciding if a memory is important
        self.relevance_threshold = 0.65  # Threshold for considering a memory relevant during recall
        self.max_episodes_per_query = 5  # Maximum number of episodes to return per query
        
    def query_memory(self, query_text: Union[str, list[str]], num_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Query the episodic memory for relevant episodes.
        
        Args:
            query_text (Union[str, list[str]]): The text to search for or a list containing
                                               [query, importance_override, context].
            num_results (int): Number of results to return (defaults to 5).
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing relevant memories and metadata.
        """
        # Process query input
        query = ""
        importance_override = None
        context_filter = None
        
        if isinstance(query_text, list):
            query = query_text[0] if len(query_text) > 0 else ""
            if len(query_text) > 1:
                try:
                    importance_override = float(query_text[1])
                except (ValueError, TypeError):
                    pass
            if len(query_text) > 2:
                context_filter = query_text[2]
        else:
            query = query_text
            
        self.logger.debug(f"Querying episodic memory: {query}")
        
        # Adjust num_results if needed
        if num_results > self.max_episodes_per_query:
            num_results = self.max_episodes_per_query
            
        # Query the chunk collection
        chunks = self.storage.query_storage(
            collection_name=self.chunks_collection,
            query=query,
            num_results=num_results * 2  # Query more chunks to find distinct episodes
        )
        
        # If no chunks found, return empty result
        if not chunks or 'ids' not in chunks:
            self.logger.debug("No relevant memory chunks found")
            self.store = {'episodes': [], 'formatted': "No relevant memories found."}
            return self.store
            
        # Extract episodes from chunks
        episode_ids = set()
        if isinstance(chunks.get('metadatas', {}), dict):  # Handle single result
            if 'Episode_ID' in chunks['metadatas']:
                episode_ids.add(chunks['metadatas']['Episode_ID'])
        else:  # Handle multiple results
            for metadata in chunks.get('metadatas', []):
                if 'Episode_ID' in metadata:
                    episode_ids.add(metadata['Episode_ID'])
        
        # Fetch the complete episodes
        episodes = []
        for episode_id in episode_ids:
            # Skip if we already have enough episodes
            if len(episodes) >= num_results:
                break
                
            # Fetch the episode
            filters = {"id": {"$eq": episode_id}}
            episode = self.storage.load_collection(
                collection_name=self.episodes_collection,
                where=filters
            )
            
            if episode and episode.get('documents'):
                # Check context filter if provided
                if context_filter and episode.get('metadatas'):
                    if not self._matches_context_filter(episode['metadatas'][0], context_filter):
                        continue
                        
                # Check importance threshold
                importance = float(episode['metadatas'][0].get('importance', 0))
                if importance_override is not None:
                    if importance < importance_override:
                        continue
                elif importance < self.importance_threshold:
                    continue
                    
                episodes.append({
                    'id': episode['ids'][0],
                    'content': episode['documents'][0],
                    'metadata': episode['metadatas'][0]
                })
                
        # Format episodes for output
        formatted_episodes = self._format_episodes(episodes)
        
        # Store in memory's store attribute
        self.store = {
            'episodes': episodes,
            'formatted': formatted_episodes
        }
        
        return self.store
            
    def update_memory(self, data: dict, context: Optional[dict] = None, 
                      ids: Optional[Union[str, list[str]]] = None,
                      metadata: Optional[list[dict]] = None) -> None:
        """
        Store a new episodic memory.
        
        Args:
            data (dict): Dictionary containing the memory data.
            context (dict, optional): Contextual information about the memory.
            ids (Union[str, list[str]], optional): IDs for the memory (not used directly).
            metadata (list[dict], optional): Additional metadata (not used directly).
        """
        # Extract the memory content
        content = None
        for key in ['memory', 'content', 'text', 'episode', 'message']:
            if key in data:
                content = data[key]
                break
                
        if not content:
            self.logger.warning("No memory content provided")
            return
            
        # Generate default metadata
        episode_metadata = {
            'timestamp': datetime.now().isoformat(),
            'importance': 0.5,  # Default importance
        }
        
        # Extract additional metadata from context
        if context:
            self._extract_metadata_from_context(context, episode_metadata)
            
        # Calculate importance if not provided
        if 'importance' not in episode_metadata or episode_metadata['importance'] == 0.5:
            importance = self._calculate_importance(content, context)
            episode_metadata['importance'] = importance
            
        # Save the episode
        self._save_episode(content, episode_metadata)
        
    def _save_episode(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Save an episode to storage with proper chunking for retrieval.
        
        Args:
            content (str): The content of the episode.
            metadata (Dict[str, Any]): Metadata for the episode.
            
        Returns:
            str: The ID of the saved episode.
        """
        # Generate a unique ID for the episode
        episode_count = self.storage.count_collection(self.episodes_collection)
        episode_id = episode_count + 1
        episode_id_str = str(episode_id)
        
        # Add ID to metadata
        metadata["id"] = episode_id
        
        # Save the full episode
        self.storage.save_to_storage(
            collection_name=self.episodes_collection,
            data=[content],
            ids=[episode_id_str],
            metadata=[metadata]
        )
        
        self.logger.debug(f"Saved episode {episode_id}: {content[:50]}...")
        
        # Create semantic chunks for better retrieval
        chunks = chunker.semantic_chunk(content)
        
        # Save each chunk with reference to the episode
        for i, chunk in enumerate(chunks):
            chunk_id = f"{episode_id}_{i+1}"
            chunk_metadata = {
                "id": chunk_id,
                "Episode_ID": episode_id,
                "Chunk_Number": i+1,
                "Total_Chunks": len(chunks)
            }
            # Copy important metadata fields from the episode to the chunk
            for key in ['timestamp', 'importance', 'context', 'source', 'participants']:
                if key in metadata:
                    chunk_metadata[key] = metadata[key]
                    
            self.storage.save_to_storage(
                collection_name=self.chunks_collection,
                data=[chunk.content],
                ids=[chunk_id],
                metadata=[chunk_metadata]
            )
            
        return episode_id_str
        
    def _calculate_importance(self, content: str, context: Optional[Dict] = None) -> float:
        """
        Calculate the importance of a memory based on its content and context.
        
        Args:
            content (str): The content of the memory.
            context (Optional[Dict]): Optional contextual information.
            
        Returns:
            float: Importance score between 0.0 and 1.0.
        """
        # This is a simple implementation - in a real system this could use LLM or rules
        # to determine importance based on content analysis
        
        # Look for explicit importance in content
        importance_match = re.search(r'importance[:\s]+(\d+\.?\d*)', content.lower())
        if importance_match:
            try:
                importance = float(importance_match.group(1))
                return min(max(importance, 0.0), 1.0)  # Ensure value is between 0 and 1
            except (ValueError, IndexError):
                pass
                
        # Check length (assuming longer content is more important)
        length_score = min(len(content) / 1000, 0.5)  # Max 0.5 for length
        
        # Check for important keywords
        important_keywords = ["critical", "important", "urgent", "significant", "remember", "key", "vital"]
        keyword_count = sum(1 for keyword in important_keywords if keyword in content.lower())
        keyword_score = min(keyword_count * 0.1, 0.5)  # Max 0.5 for keywords
        
        # Combine scores
        importance = length_score + keyword_score
        
        # Ensure value is between 0 and 1
        return min(max(importance, 0.0), 1.0)
        
    def _extract_metadata_from_context(self, context: dict, metadata: dict) -> None:
        """
        Extract metadata from context and update the metadata dictionary.
        
        Args:
            context (dict): The context dictionary.
            metadata (dict): The metadata dictionary to update.
        """
        # Try to extract source/channel information
        if 'external' in context:
            for key in ['source', 'channel', 'platform']:
                if key in context['external']:
                    metadata['source'] = context['external'][key]
                    break
                    
        # Try to extract participants (user and any other participants)
        participants = []
        
        # Extract user
        if 'external' in context and 'user' in context['external']:
            participants.append(context['external']['user'])
        elif 'external' in context and 'username' in context['external']:
            participants.append(context['external']['username'])
            
        # Extract other participants if mentioned in the data
        if 'internal' in context:
            for agent_id, agent_data in context['internal'].items():
                if isinstance(agent_data, dict) and 'participants' in agent_data:
                    if isinstance(agent_data['participants'], list):
                        participants.extend(agent_data['participants'])
                    elif isinstance(agent_data['participants'], str):
                        participants.append(agent_data['participants'])
                        
        if participants:
            metadata['participants'] = list(set(participants))  # Remove duplicates
            
        # Try to extract other context information
        context_info = {}
        
        # Internal context from each agent
        if 'internal' in context:
            for agent_id, agent_data in context['internal'].items():
                if isinstance(agent_data, dict):
                    # Copy relevant fields avoiding large data structures
                    for key, value in agent_data.items():
                        if key in ['intent', 'goal', 'task', 'summary'] and isinstance(value, str):
                            context_info[f"{agent_id}_{key}"] = value
                            
        if context_info:
            metadata['context'] = context_info
            
    def _matches_context_filter(self, metadata: dict, context_filter: str) -> bool:
        """
        Check if the episode metadata matches the context filter.
        
        Args:
            metadata (dict): The episode metadata.
            context_filter (str): The context filter string.
            
        Returns:
            bool: True if the metadata matches the filter.
        """
        if not context_filter:
            return True
            
        # Check source
        if 'source' in metadata and context_filter.lower() in metadata['source'].lower():
            return True
            
        # Check participants
        if 'participants' in metadata:
            if isinstance(metadata['participants'], list):
                for participant in metadata['participants']:
                    if context_filter.lower() in participant.lower():
                        return True
            elif isinstance(metadata['participants'], str):
                if context_filter.lower() in metadata['participants'].lower():
                    return True
                    
        # Check context information
        if 'context' in metadata and isinstance(metadata['context'], dict):
            for key, value in metadata['context'].items():
                if isinstance(value, str) and context_filter.lower() in value.lower():
                    return True
                    
        return False
        
    def _format_episodes(self, episodes: List[Dict[str, Any]]) -> str:
        """
        Format episodes for display.
        
        Args:
            episodes (List[Dict[str, Any]]): List of episode dictionaries.
            
        Returns:
            str: Formatted string representation of the episodes.
        """
        if not episodes:
            return "No relevant memories found."
            
        formatted_episodes = []
        
        for episode in episodes:
            # Format timestamp
            timestamp = episode.get('metadata', {}).get('timestamp', 'Unknown time')
            if isinstance(timestamp, str) and len(timestamp) > 10:
                # Try to format ISO timestamp to a more readable format
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    pass
                    
            # Extract metadata fields
            metadata_lines = []
            
            # Add importance if available
            if 'importance' in episode.get('metadata', {}):
                importance = float(episode['metadata']['importance'])
                importance_str = f"{importance:.1f}"
                metadata_lines.append(f"Importance: {importance_str}")
                
            # Add source if available
            if 'source' in episode.get('metadata', {}):
                metadata_lines.append(f"Source: {episode['metadata']['source']}")
                
            # Add participants if available
            if 'participants' in episode.get('metadata', {}):
                if isinstance(episode['metadata']['participants'], list):
                    participants = ", ".join(episode['metadata']['participants'])
                else:
                    participants = str(episode['metadata']['participants'])
                metadata_lines.append(f"Participants: {participants}")
                
            # Format the episode
            formatted_episode = f"[{timestamp}]\n"
            if metadata_lines:
                formatted_episode += f"{' | '.join(metadata_lines)}\n"
            formatted_episode += f"\n{episode['content']}"
            
            formatted_episodes.append(formatted_episode)
            
        return "\n\n---\n\n".join(formatted_episodes)
    
    def delete(self, ids: Union[str, list[str]] = None) -> None:
        """
        Delete episodes from memory.
        
        Args:
            ids (Union[str, list[str]], optional): IDs of episodes to delete.
                If None, deletes all episodes.
        """
        if ids is None:
            # Delete all episodes
            self.storage.delete_collection(self.episodes_collection)
            self.storage.delete_collection(self.chunks_collection)
            self.logger.info("Deleted all episodic memory collections")
        else:
            # Convert to list if a single ID
            if not isinstance(ids, list):
                ids = [ids]
                
            # Delete specific episodes
            self.storage.delete_from_storage(collection_name=self.episodes_collection, ids=ids)
            
            # Delete associated chunks
            for episode_id in ids:
                # Find all chunks for this episode
                filters = {"Episode_ID": {"$eq": int(episode_id)}}
                chunks = self.storage.load_collection(
                    collection_name=self.chunks_collection,
                    where=filters
                )
                
                if chunks and chunks.get('ids'):
                    self.storage.delete_from_storage(collection_name=self.chunks_collection, ids=chunks['ids'])
                    
            self.logger.info(f"Deleted episodes with IDs: {ids}")
            
    def consolidate_memories(self, threshold: float = 0.8) -> None:
        """
        Consolidate related memories to reduce redundancy and create higher-level episodic memories.
        
        Args:
            threshold (float): The similarity threshold for consolidation (0.0 to 1.0).
                              Higher values make consolidation more selective.
        """
        # This is a placeholder for a more sophisticated consolidation algorithm
        # In a full implementation, this would:
        # 1. Find related memories based on semantic similarity
        # 2. Use an LLM to create a consolidated memory that captures the essence of the related memories
        # 3. Save the consolidated memory as a new episode with higher importance
        
        self.logger.warning("Memory consolidation not yet implemented")
        pass 