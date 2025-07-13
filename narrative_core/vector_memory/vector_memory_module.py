#!/usr/bin/env python3
"""
Vector Memory Module
Handles semantic memory storage and retrieval using FAISS for similarity search.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pickle
from dataclasses import dataclass, asdict
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class MemoryItem:
    """Represents a single memory item with metadata."""
    id: str
    content: str
    embedding: Optional[np.ndarray] = None
    memory_type: str = "semantic"
    layer: str = "long_term"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    emotional_weight: float = 0.5
    thematic_tags: List[str] = None
    created_at: datetime = None
    last_accessed: datetime = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.thematic_tags is None:
            self.thematic_tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = datetime.now()

class VectorMemoryModule:
    """
    Vector-based memory storage and retrieval system using FAISS.
    Provides semantic similarity search and memory management.
    """
    
    def __init__(self, index_path: str = "vector_memory", dimension: int = 384):
        self.index_path = index_path
        self.dimension = dimension
        self.model = None
        self.index = None
        self.memory_items: Dict[str, MemoryItem] = {}
        self.metadata_file = f"{index_path}/metadata.json"
        
        # Ensure directory exists
        os.makedirs(index_path, exist_ok=True)
        
        # Initialize the system
        self._initialize_model()
        self._load_or_create_index()
        self._load_metadata()
        
        logger.info(f"🔧 Initialized Vector Memory Module: {index_path}")
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load sentence transformer: {e}")
            raise
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        index_file = f"{self.index_path}/faiss_index.bin"
        
        if os.path.exists(index_file):
            try:
                self.index = faiss.read_index(index_file)
                logger.info(f"✅ Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        logger.info("✅ Created new FAISS index")
    
    def _load_metadata(self):
        """Load memory metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Convert back to MemoryItem objects
                for item_id, item_data in metadata.items():
                    item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                    item_data['last_accessed'] = datetime.fromisoformat(item_data['last_accessed'])
                    self.memory_items[item_id] = MemoryItem(**item_data)
                
                logger.info(f"✅ Loaded {len(self.memory_items)} memory items")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load metadata: {e}")
    
    def _save_metadata(self):
        """Save memory metadata to file."""
        try:
            # Convert MemoryItem objects to dict for JSON serialization
            metadata = {}
            for item_id, item in self.memory_items.items():
                item_dict = asdict(item)
                item_dict['created_at'] = item.created_at.isoformat()
                item_dict['last_accessed'] = item.last_accessed.isoformat()
                item_dict['embedding'] = None  # Don't save embeddings in metadata
                metadata[item_id] = item_dict
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Saved metadata for {len(self.memory_items)} items")
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {e}")
    
    def _save_index(self):
        """Save FAISS index to file."""
        try:
            index_file = f"{self.index_path}/faiss_index.bin"
            faiss.write_index(self.index, index_file)
            logger.info("✅ Saved FAISS index")
        except Exception as e:
            logger.error(f"❌ Failed to save index: {e}")
    
    def add_memory(self, content: str, memory_type: str = "semantic", 
                   layer: str = "long_term", user_id: Optional[str] = None,
                   session_id: Optional[str] = None, emotional_weight: float = 0.5,
                   thematic_tags: List[str] = None) -> str:
        """
        Add a new memory item to the vector store.
        
        Args:
            content: The memory content
            memory_type: Type of memory (semantic, episodic, etc.)
            layer: Memory layer (short_term, mid_term, long_term)
            user_id: User identifier
            session_id: Session identifier
            emotional_weight: Emotional weight (0.0 to 1.0)
            thematic_tags: List of thematic tags
            
        Returns:
            Memory item ID
        """
        try:
            # Generate embedding
            embedding = self.model.encode([content])[0]
            
            # Create memory item
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.memory_items)}"
            memory_item = MemoryItem(
                id=memory_id,
                content=content,
                embedding=embedding,
                memory_type=memory_type,
                layer=layer,
                user_id=user_id,
                session_id=session_id,
                emotional_weight=emotional_weight,
                thematic_tags=thematic_tags or []
            )
            
            # Add to FAISS index
            self.index.add(embedding.reshape(1, -1))
            
            # Store metadata
            self.memory_items[memory_id] = memory_item
            
            # Save to disk
            self._save_metadata()
            self._save_index()
            
            logger.info(f"✅ Added memory: {memory_id} ({len(content)} chars)")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add memory: {e}")
            raise
    
    def search_memories(self, query: str, top_k: int = 5, 
                       memory_type: Optional[str] = None,
                       layer: Optional[str] = None,
                       user_id: Optional[str] = None) -> List[Tuple[MemoryItem, float]]:
        """
        Search for similar memories using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            memory_type: Filter by memory type
            layer: Filter by memory layer
            user_id: Filter by user ID
            
        Returns:
            List of (MemoryItem, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Search FAISS index
            similarities, indices = self.index.search(
                query_embedding.reshape(1, -1), 
                min(top_k * 2, self.index.ntotal)  # Get more results for filtering
            )
            
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue
                
                # Get memory item by index
                memory_id = list(self.memory_items.keys())[idx]
                memory_item = self.memory_items[memory_id]
                
                # Apply filters
                if memory_type and memory_item.memory_type != memory_type:
                    continue
                if layer and memory_item.layer != layer:
                    continue
                if user_id and memory_item.user_id != user_id:
                    continue
                
                # Apply decay based on time since last access
                decay_factor = self._calculate_decay(memory_item.last_accessed)
                adjusted_similarity = similarity * decay_factor
                
                results.append((memory_item, adjusted_similarity))
                
                if len(results) >= top_k:
                    break
            
            # Sort by similarity and update access times
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Update access times for retrieved items
            for memory_item, _ in results:
                memory_item.last_accessed = datetime.now()
                memory_item.access_count += 1
            
            self._save_metadata()
            
            logger.info(f"🔍 Found {len(results)} memories for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search memories: {e}")
            return []
    
    def _calculate_decay(self, last_accessed: datetime) -> float:
        """
        Calculate decay factor based on time since last access.
        Uses exponential decay with half-life of 30 days.
        """
        days_since = (datetime.now() - last_accessed).days
        half_life = 30  # days
        decay_factor = 0.5 ** (days_since / half_life)
        return max(decay_factor, 0.1)  # Minimum decay factor of 0.1
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a specific memory item by ID."""
        return self.memory_items.get(memory_id)
    
    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """Update a memory item."""
        if memory_id not in self.memory_items:
            return False
        
        memory_item = self.memory_items[memory_id]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(memory_item, key):
                setattr(memory_item, key, value)
        
        # Update embedding if content changed
        if 'content' in kwargs:
            new_embedding = self.model.encode([memory_item.content])[0]
            memory_item.embedding = new_embedding
            
            # Update FAISS index (this is simplified - in production you'd need to handle index updates)
            logger.warning("⚠️ Content updates require index rebuild - not implemented")
        
        self._save_metadata()
        return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item."""
        if memory_id not in self.memory_items:
            return False
        
        del self.memory_items[memory_id]
        self._save_metadata()
        
        # Note: FAISS doesn't support deletion easily, so we'd need to rebuild the index
        logger.warning("⚠️ Memory deletion requires index rebuild - not implemented")
        return True
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        total_memories = len(self.memory_items)
        memory_types = {}
        layers = {}
        users = {}
        
        for item in self.memory_items.values():
            memory_types[item.memory_type] = memory_types.get(item.memory_type, 0) + 1
            layers[item.layer] = layers.get(item.layer, 0) + 1
            if item.user_id:
                users[item.user_id] = users.get(item.user_id, 0) + 1
        
        return {
            'total_memories': total_memories,
            'memory_types': memory_types,
            'layers': layers,
            'users': users,
            'index_size': self.index.ntotal if self.index else 0
        }
    
    def cleanup_old_memories(self, days_old: int = 90) -> int:
        """Remove memories older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        to_delete = []
        
        for memory_id, item in self.memory_items.items():
            if item.created_at < cutoff_date:
                to_delete.append(memory_id)
        
        for memory_id in to_delete:
            del self.memory_items[memory_id]
        
        if to_delete:
            self._save_metadata()
            logger.info(f"🧹 Cleaned up {len(to_delete)} old memories")
        
        return len(to_delete)
    
    def export_memories(self, filepath: str):
        """Export all memories to a file."""
        try:
            export_data = {
                'metadata': {k: asdict(v) for k, v in self.memory_items.items()},
                'stats': self.get_memory_stats(),
                'export_date': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"✅ Exported memories to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to export memories: {e}")
    
    def import_memories(self, filepath: str):
        """Import memories from a file."""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing memories
            self.memory_items.clear()
            
            # Import new memories
            for memory_id, item_data in import_data['metadata'].items():
                item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                item_data['last_accessed'] = datetime.fromisoformat(item_data['last_accessed'])
                self.memory_items[memory_id] = MemoryItem(**item_data)
            
            # Rebuild FAISS index
            self._rebuild_index()
            
            logger.info(f"✅ Imported {len(self.memory_items)} memories from {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to import memories: {e}")
    
    def _rebuild_index(self):
        """Rebuild the FAISS index from memory items."""
        if not self.memory_items:
            self._create_new_index()
            return
        
        # Create new index
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Add all embeddings
        embeddings = []
        for item in self.memory_items.values():
            if item.embedding is not None:
                embeddings.append(item.embedding)
            else:
                # Regenerate embedding if missing
                item.embedding = self.model.encode([item.content])[0]
                embeddings.append(item.embedding)
        
        if embeddings:
            embeddings_array = np.array(embeddings)
            self.index.add(embeddings_array)
        
        self._save_index()
        logger.info(f"✅ Rebuilt index with {len(embeddings)} vectors") 