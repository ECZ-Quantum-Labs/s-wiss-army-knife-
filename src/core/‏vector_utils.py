"""
Vector Utilities for Swiss Army Knife - Public Stub
Lightweight interface for semantic search & knowledge storage.
Private advanced logic (GPU acceleration, custom embeddings) resides in secure module.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class VectorKnowledgeBase:
    """Public stub for vector-based knowledge storage and retrieval."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.persist_dir = Path(config.get("persist_directory", "data/vector_store"))
        self.collection_name = config.get("collection_name", "security_knowledge")
        self.similarity_threshold = config.get("similarity_threshold", 0.85)
        self.max_days = config.get("max_history_days", 90)
        
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        self.collection = None
        
        if CHROMA_AVAILABLE and config.get("enabled", True):
            self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB client (public-safe configuration)."""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(allow_reset=False, anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"[!] Vector DB init warning: {e}")
    
    def _sanitize_for_embedding(self, text: str) -> str:
        """Remove sensitive info before embedding (privacy-first)."""
        # Simple sanitization: remove URLs, IPs, exact paths
        import re
        text = re.sub(r'https?://\S+', '[URL]', text)
        text = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '[IP]', text)
        text = re.sub(r'/[a-zA-Z0-9/_\.-]+\.[a-z]{2,4}', '[PATH]', text)
        return text
    
    def _hash_finding(self, finding: Dict) -> str:
        """Create deterministic hash for deduplication."""
        content = f"{finding.get('endpoint')}_{finding.get('risk_level')}_{finding.get('remediation')}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def store_finding(self, finding: Dict, metadata: Optional[Dict] = None) -> bool:
        """Store a security finding in vector space (public stub)."""
        if not CHROMA_AVAILABLE or not self.collection:
            return False
        
        try:
            # Prepare content for embedding
            content_parts = [
                finding.get("endpoint", ""),
                finding.get("risk_level", ""),
                finding.get("remediation", ""),
                f"score:{finding.get('risk_score', 0)}"
            ]
            content = " | ".join(part for part in content_parts if part)
            content = self._sanitize_for_embedding(content)
            
            # Generate ID
            doc_id = f"finding_{self._hash_finding(finding)}"
            
            # Prepare metadata
            doc_metadata = {
                "risk_level": finding.get("risk_level", "INFO"),
                "risk_score": finding.get("risk_score", 0),
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Add to collection (Chroma auto-handles embedding with default model)
            self.collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"[!] Vector store error: {e}")
            return False
    
    def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for similar past findings (public stub)."""
        if not CHROMA_AVAILABLE or not self.collection:
            return []
        
        try:
            query = self._sanitize_for_embedding(query)
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                include=["metadatas", "documents", "distances"]
            )
            
            findings = []
            if results.get("metadatas") and results["metadatas"][0]:
                for i, meta in enumerate(results["metadatas"][0]):
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    similarity = 1 - distance
                    if similarity >= self.similarity_threshold:
                        findings.append({
                            "similarity": round(similarity, 3),
                            "metadata": meta,
                            "content": results["documents"][0][i] if results.get("documents") else ""
                        })
            return findings
        except Exception as e:
            print(f"[!] Vector search error: {e}")
            return []
    
    def cleanup_old_entries(self) -> int:
        """Remove entries older than max_history_days (public stub)."""
        if not CHROMA_AVAILABLE or not self.collection:
            return 0
        
        try:
            cutoff = datetime.now() - timedelta(days=self.max_days)
            # Note: ChromaDB filtering is limited in public stub; 
            # full implementation uses metadata filtering in private module
            print(f"[i] Cleanup scheduled: entries before {cutoff.isoformat()}")
            return 0  # Placeholder - real logic in private module
        except Exception as e:
            print(f"[!] Cleanup error: {e}")
            return 0

