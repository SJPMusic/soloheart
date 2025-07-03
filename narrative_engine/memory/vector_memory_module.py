import os
import json
import time
from typing import List, Dict, Any, Optional

try:
    import faiss
    import numpy as np
    # Note: OpenAI embeddings removed - using simple fallback approach
    # This could be replaced with a local embedding model in the future
except ImportError:
    faiss = None
    np = None

class VectorMemoryModule:
    def __init__(self, campaign_id: str, db_path: str = "vector_memory.index"):
        self.campaign_id = campaign_id
        self.db_path = db_path
        self.index = None
        self.memories: List[Dict[str, Any]] = []  # Store metadata for each vector
        self.available = faiss is not None and np is not None
        if self.available:
            self._init_index()
        else:
            print("[VectorMemoryModule] FAISS or numpy not available. Vector memory disabled.")

    def _init_index(self):
        # Use 1536 for text-embedding-3-small
        dim = 1536
        if os.path.exists(self.db_path):
            self.index = faiss.read_index(self.db_path)
            self._load_metadata()
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.memories = []

    def _save_index(self):
        if self.index:
            faiss.write_index(self.index, self.db_path)
            self._save_metadata()

    def _save_metadata(self):
        meta_path = self.db_path + ".meta.json"
        with open(meta_path, "w") as f:
            json.dump(self.memories, f)

    def _load_metadata(self):
        meta_path = self.db_path + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                self.memories = json.load(f)
        else:
            self.memories = []

    def _embed(self, text: str) -> Optional[Any]:
        if not self.available:
            return None
        # Simple fallback: use basic text features for similarity
        # In a production system, this would use a local embedding model
        try:
            # For now, return None to use fallback retrieval
            return None
        except Exception as e:
            print(f"[VectorMemoryModule] Embedding error: {e}")
            return None

    def store_memory(self, text: str, metadata: Dict[str, Any]) -> bool:
        # Ensure character_id is present in metadata
        character_id = metadata.get('character_id') or metadata.get('user_id') or 'player'
        metadata['character_id'] = character_id
        if not self.available:
            # Fallback: store as dict with campaign_id and importance
            entry = {
                'text': text,
                'metadata': metadata.copy() if metadata else {},
                'campaign_id': self.campaign_id,
                'character_id': character_id
            }
            if 'importance' not in entry['metadata']:
                entry['metadata']['importance'] = 0.5
            self.memories.append(entry)
            return True
        vec = self._embed(text)
        if vec is None:
            return False
        self.index.add(np.expand_dims(vec, axis=0))
        entry = metadata.copy()
        entry.update({
            "text": text,
            "timestamp": time.time(),
            "campaign_id": self.campaign_id,
            "character_id": character_id,
            "importance": metadata.get("importance", 1.0)
        })
        self.memories.append(entry)
        self._save_index()
        return True

    def retrieve_similar(self, query: str, top_n: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.available:
            # Fallback: return top_n by importance if available
            if not self.memories:
                return []
            filtered = self.memories
            if filters:
                for k, v in filters.items():
                    filtered = [m for m in filtered if m['metadata'].get(k) == v or m.get(k) == v]
            sorted_mem = sorted(filtered, key=lambda m: m['metadata'].get('importance', 0), reverse=True)
            return sorted_mem[:top_n]
        vec = self._embed(query)
        if vec is None:
            return []
        D, I = self.index.search(np.expand_dims(vec, axis=0), top_n)
        results = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.memories):
                continue
            mem = self.memories[idx]
            if filters:
                if any(mem.get(k) != v and mem.get('metadata', {}).get(k) != v for k, v in filters.items()):
                    continue
            results.append({k: mem[k] for k in mem if k != "importance"})
        return results

    def decay_memory(self, decay_rate: float = 0.01):
        if not self.available:
            for m in self.memories:
                if 'importance' in m['metadata']:
                    m['metadata']['importance'] *= (1 - decay_rate)
            return
        now = time.time()
        for mem in self.memories:
            age = now - mem["timestamp"]
            mem["importance"] *= (1.0 - decay_rate) ** (age / 3600)  # decay per hour
        self._save_metadata()

    def is_available(self) -> bool:
        return self.available 