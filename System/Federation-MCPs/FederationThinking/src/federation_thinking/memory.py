"""
Memory integration for FederationThinking
Connects with Federation ChromaDB for persistence and pattern analysis
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.config import Settings

from federation_thinking.models import Thought, ThinkingSession
from federation_thinking.config import Config

class ThinkingMemory:
    """Manages persistence and retrieval of thoughts in ChromaDB"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize ChromaDB clients
        self.cc_client = chromadb.PersistentClient(
            path=str(config.cc_memory_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collections
        self.thoughts_collection = self.cc_client.get_or_create_collection(
            name="thinking_thoughts",
            metadata={"description": "Individual thoughts from thinking sessions"}
        )
        
        self.sessions_collection = self.cc_client.get_or_create_collection(
            name="thinking_sessions",
            metadata={"description": "Complete thinking sessions"}
        )
        
        self.patterns_collection = self.cc_client.get_or_create_collection(
            name="thinking_patterns",
            metadata={"description": "Recognized thinking patterns"}
        )
    
    def save_thought(self, thought: Thought) -> str:
        """Save a thought to memory"""
        thought_dict = thought.to_dict()
        
        # Prepare document for ChromaDB
        document = json.dumps({
            "content": thought.content,
            "type": thought.type,
            "framework": thought.framework,
            "confidence": thought.confidence,
            "evidence": thought.evidence,
            "tags": thought.tags
        })
        
        # Metadata for ChromaDB
        metadata = {
            "thought_id": thought.id,
            "session_id": thought.session_id,
            "thought_number": thought.thought_number,
            "type": thought.type,
            "framework": thought.framework or "",
            "confidence": thought.confidence,
            "timestamp": thought.timestamp.isoformat(),
            "is_revision": thought.is_revision,
            "has_evidence": len(thought.evidence) > 0,
            "tag_count": len(thought.tags),
            "shared_with": ",".join(thought.shared_with) if thought.shared_with else ""
        }
        
        # Add to ChromaDB
        self.thoughts_collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[thought.id]
        )
        
        thought.saved_to_memory = True
        thought.memory_id = thought.id
        
        return thought.id
    
    def save_session(self, session: ThinkingSession) -> str:
        """Save a complete thinking session"""
        session_dict = session.to_dict()
        
        # Prepare document
        document = json.dumps({
            "title": session.title,
            "context": session.context,
            "framework": session.framework,
            "total_thoughts": session.total_thoughts,
            "average_confidence": session.average_confidence,
            "thought_summary": self._summarize_thoughts(session.thoughts)
        })
        
        # Metadata
        metadata = {
            "session_id": session.id,
            "title": session.title,
            "framework": session.framework or "",
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "total_thoughts": session.total_thoughts,
            "total_revisions": session.total_revisions,
            "total_branches": session.total_branches,
            "average_confidence": session.average_confidence,
            "task_id": session.task_id or "",
            "shared_with": ",".join(session.shared_with) if session.shared_with else ""
        }
        
        # Add to ChromaDB
        self.sessions_collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[session.id]
        )
        
        return session.id
    
    def search_thoughts(
        self, 
        query: str, 
        n_results: int = 10,
        session_id: Optional[str] = None,
        thought_type: Optional[str] = None,
        framework: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar thoughts"""
        where_clause = {}
        
        if session_id:
            where_clause["session_id"] = session_id
        if thought_type:
            where_clause["type"] = thought_type
        if framework:
            where_clause["framework"] = framework
        if min_confidence is not None:
            where_clause["confidence"] = {"$gte": min_confidence}
        
        results = self.thoughts_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        thoughts = []
        for i in range(len(results["ids"][0])):
            thought_data = json.loads(results["documents"][0][i])
            thought_data.update(results["metadatas"][0][i])
            thought_data["distance"] = results["distances"][0][i]
            thoughts.append(thought_data)
        
        return thoughts
    
    def get_session_thoughts(self, session_id: str) -> List[Thought]:
        """Get all thoughts from a session"""
        results = self.thoughts_collection.get(
            where={"session_id": session_id}
        )
        
        thoughts = []
        for i in range(len(results["ids"])):
            thought_data = json.loads(results["documents"][i])
            thought_data.update(results["metadatas"][i])
            # Reconstruct thought object
            thoughts.append(thought_data)
        
        return thoughts
    
    def analyze_patterns(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze thinking patterns"""
        # Get thoughts to analyze
        if session_id:
            where_clause = {"session_id": session_id}
        else:
            where_clause = None
        
        results = self.thoughts_collection.get(where=where_clause)
        
        if not results["ids"]:
            return {"error": "No thoughts found to analyze"}
        
        patterns = {
            "total_thoughts": len(results["ids"]),
            "type_distribution": {},
            "framework_usage": {},
            "confidence_stats": {
                "average": 0,
                "min": 1.0,
                "max": 0.0
            },
            "revision_rate": 0,
            "branching_rate": 0,
            "evidence_usage_rate": 0,
            "common_tags": {}
        }
        
        confidences = []
        revision_count = 0
        evidence_count = 0
        
        for i in range(len(results["ids"])):
            metadata = results["metadatas"][i]
            
            # Type distribution
            thought_type = metadata.get("type", "unknown")
            patterns["type_distribution"][thought_type] = patterns["type_distribution"].get(thought_type, 0) + 1
            
            # Framework usage
            framework = metadata.get("framework", "none")
            if framework:
                patterns["framework_usage"][framework] = patterns["framework_usage"].get(framework, 0) + 1
            
            # Confidence stats
            confidence = float(metadata.get("confidence", 0))
            confidences.append(confidence)
            patterns["confidence_stats"]["min"] = min(patterns["confidence_stats"]["min"], confidence)
            patterns["confidence_stats"]["max"] = max(patterns["confidence_stats"]["max"], confidence)
            
            # Revision rate
            if metadata.get("is_revision", False):
                revision_count += 1
            
            # Evidence usage
            if metadata.get("has_evidence", False):
                evidence_count += 1
        
        # Calculate averages and rates
        if confidences:
            patterns["confidence_stats"]["average"] = sum(confidences) / len(confidences)
        
        patterns["revision_rate"] = revision_count / patterns["total_thoughts"] if patterns["total_thoughts"] > 0 else 0
        patterns["evidence_usage_rate"] = evidence_count / patterns["total_thoughts"] if patterns["total_thoughts"] > 0 else 0
        
        return patterns
    
    def _summarize_thoughts(self, thoughts: List[Thought]) -> str:
        """Create a summary of thoughts for search"""
        if not thoughts:
            return "Empty thinking session"
        
        # Get key insights (high confidence thoughts)
        key_thoughts = [t for t in thoughts if t.confidence >= 0.7]
        if not key_thoughts:
            key_thoughts = thoughts[:5]  # First 5 if no high confidence
        
        summary_parts = []
        for thought in key_thoughts[:3]:  # Top 3 key thoughts
            summary_parts.append(f"{thought.type}: {thought.content[:100]}")
        
        return " | ".join(summary_parts)
    
    def get_related_memories(self, thought: Thought, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find memories related to a thought"""
        # Search in general CC memories
        try:
            general_collection = self.cc_client.get_collection("cc_memories")
            
            # Search using thought content and tags
            search_query = f"{thought.content} {' '.join(thought.tags)}"
            
            results = general_collection.query(
                query_texts=[search_query],
                n_results=n_results
            )
            
            memories = []
            for i in range(len(results["ids"][0])):
                memory = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            # Collection might not exist
            return []