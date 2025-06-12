"""
Session management for FederationThinking
Handles thinking sessions, collaboration, and state management
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from federation_thinking.models import ThinkingSession, Thought, Framework, ThoughtType
from federation_thinking.memory import ThinkingMemory
from federation_thinking.config import Config

class SessionManager:
    """Manages thinking sessions and collaborative features"""
    
    def __init__(self, config: Config, memory: ThinkingMemory):
        self.config = config
        self.memory = memory
        
        # Session storage
        self.sessions_path = Path.home() / ".federation" / "thinking_sessions"
        self.sessions_path.mkdir(parents=True, exist_ok=True)
        
        # Active sessions cache
        self.active_sessions: Dict[str, ThinkingSession] = {}
        
        # Load any active sessions from disk
        self._load_active_sessions()
    
    def start_session(
        self,
        title: str,
        context: Optional[str] = None,
        framework: Optional[str] = None,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> ThinkingSession:
        """Start a new thinking session"""
        session = ThinkingSession(
            title=title,
            context=context,
            framework=Framework(framework) if framework else None,
            task_id=task_id,
            project_id=project_id
        )
        
        self.active_sessions[session.id] = session
        self._save_session_to_disk(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[ThinkingSession]:
        """Get a session by ID"""
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Try to load from disk
        session_file = self.sessions_path / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            session = ThinkingSession.from_dict(session_data)
            self.active_sessions[session_id] = session
            return session
        
        return None
    
    def add_thought(
        self,
        session_id: str,
        content: str,
        thought_type: str = "analysis",
        framework_step: Optional[str] = None,
        confidence: float = 0.5,
        evidence: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_revision: bool = False,
        revises_thought: Optional[str] = None,
        branch_from_thought: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> Thought:
        """Add a thought to a session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create thought
        thought = Thought(
            session_id=session_id,
            content=content,
            thought_number=session.get_current_thought_number(),
            type=ThoughtType(thought_type),
            framework=session.framework,
            framework_step=framework_step,
            confidence=confidence,
            evidence=evidence or [],
            tags=tags or [],
            is_revision=is_revision,
            revises_thought=revises_thought,
            branch_from_thought=branch_from_thought,
            references=references or [],
            task_id=session.task_id,
            project_id=session.project_id
        )
        
        # Handle branching
        if branch_from_thought:
            if not thought.branch_id:
                thought.branch_id = str(uuid.uuid4())
        
        # Add to session
        session.add_thought(thought)
        
        # Save thought to memory if confidence meets threshold
        if (confidence >= self.config.get("min_confidence_to_save", 0.5) and 
            self.config.get("auto_save_thoughts", True)):
            self.memory.save_thought(thought)
        
        # Update session on disk
        self._save_session_to_disk(session)
        
        return thought
    
    def end_session(self, session_id: str) -> ThinkingSession:
        """End a thinking session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = "completed"
        session.updated_at = datetime.now()
        
        # Save to long-term memory
        self.memory.save_session(session)
        
        # Update on disk
        self._save_session_to_disk(session)
        
        # Remove from active sessions if not shared
        if not session.shared_with:
            self.active_sessions.pop(session_id, None)
        
        return session
    
    def share_session(
        self, 
        session_id: str, 
        share_with: List[str],
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Share a session with other instances"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.shared_with.extend(share_with)
        session.updated_at = datetime.now()
        
        # Create sharing message
        share_data = {
            "type": "thinking_session_share",
            "session_id": session_id,
            "title": session.title,
            "context": session.context,
            "shared_by": "CC",  # Could be made dynamic
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "session_data": session.to_dict()
        }
        
        # Save to shared location (SharedVault)
        share_file = self.config.shared_vault / "🧠 ThinkingSessions" / f"{session_id}_shared.json"
        share_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(share_file, 'w') as f:
            json.dump(share_data, f, indent=2)
        
        self._save_session_to_disk(session)
        
        return {
            "status": "shared",
            "shared_with": share_with,
            "share_file": str(share_file),
            "session_id": session_id
        }
    
    def list_sessions(
        self,
        status: Optional[str] = None,
        framework: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List thinking sessions"""
        sessions = []
        
        # Check active sessions
        for session in self.active_sessions.values():
            if status and session.status != status:
                continue
            if framework and session.framework != framework:
                continue
            sessions.append(session.to_dict())
        
        # Check disk sessions
        for session_file in self.sessions_path.glob("*.json"):
            if len(sessions) >= limit:
                break
            
            session_id = session_file.stem
            if session_id in self.active_sessions:
                continue  # Already included
            
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                if status and session_data.get("status") != status:
                    continue
                if framework and session_data.get("framework") != framework:
                    continue
                
                sessions.append(session_data)
            except Exception:
                continue
        
        # Sort by updated_at
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        
        return sessions[:limit]
    
    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """Analyze a thinking session for patterns and insights"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        analysis = {
            "session_id": session_id,
            "title": session.title,
            "metrics": {
                "total_thoughts": session.total_thoughts,
                "total_revisions": session.total_revisions,
                "total_branches": session.total_branches,
                "average_confidence": session.average_confidence,
                "duration_minutes": self._calculate_duration(session)
            },
            "thought_progression": self._analyze_thought_progression(session),
            "framework_analysis": self._analyze_framework_usage(session),
            "confidence_evolution": self._analyze_confidence_evolution(session),
            "branching_points": self._analyze_branching(session),
            "key_insights": self._extract_key_insights(session)
        }
        
        return analysis
    
    def resume_session(self, session_id: str) -> ThinkingSession:
        """Resume a paused session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = "active"
        session.updated_at = datetime.now()
        
        self.active_sessions[session_id] = session
        self._save_session_to_disk(session)
        
        return session
    
    def _save_session_to_disk(self, session: ThinkingSession):
        """Save session to disk"""
        session_file = self.sessions_path / f"{session.id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def _load_active_sessions(self):
        """Load active sessions from disk"""
        timeout = timedelta(minutes=self.config.get("session_timeout_minutes", 60))
        now = datetime.now()
        
        for session_file in self.sessions_path.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session = ThinkingSession.from_dict(session_data)
                
                # Check if session is still active and not timed out
                if (session.status == "active" and 
                    now - session.updated_at < timeout):
                    self.active_sessions[session.id] = session
                    
            except Exception:
                continue
    
    def _calculate_duration(self, session: ThinkingSession) -> float:
        """Calculate session duration in minutes"""
        duration = session.updated_at - session.created_at
        return duration.total_seconds() / 60
    
    def _analyze_thought_progression(self, session: ThinkingSession) -> Dict[str, Any]:
        """Analyze how thoughts progressed"""
        if not session.thoughts:
            return {"error": "No thoughts to analyze"}
        
        progression = {
            "thought_types": [],
            "confidence_trend": [],
            "evidence_usage": [],
            "revision_points": []
        }
        
        for thought in session.thoughts:
            progression["thought_types"].append(thought.type)
            progression["confidence_trend"].append(thought.confidence)
            progression["evidence_usage"].append(len(thought.evidence))
            
            if thought.is_revision:
                progression["revision_points"].append(thought.thought_number)
        
        return progression
    
    def _analyze_framework_usage(self, session: ThinkingSession) -> Dict[str, Any]:
        """Analyze framework usage patterns"""
        if not session.framework:
            return {"framework": None, "usage": "No framework used"}
        
        framework_config = self.config.get_framework(session.framework.value)
        if not framework_config:
            return {"framework": session.framework.value, "usage": "Unknown framework"}
        
        steps = framework_config.get("steps", [])
        step_usage = {step: 0 for step in steps}
        
        for thought in session.thoughts:
            if thought.framework_step and thought.framework_step in step_usage:
                step_usage[thought.framework_step] += 1
        
        return {
            "framework": session.framework.value,
            "expected_steps": steps,
            "step_usage": step_usage,
            "completion": len([s for s in step_usage.values() if s > 0]) / len(steps) if steps else 0
        }
    
    def _analyze_confidence_evolution(self, session: ThinkingSession) -> List[float]:
        """Track confidence evolution over time"""
        return [thought.confidence for thought in session.thoughts]
    
    def _analyze_branching(self, session: ThinkingSession) -> List[Dict[str, Any]]:
        """Analyze branching patterns"""
        branching_points = []
        
        for thought in session.thoughts:
            if thought.branch_from_thought:
                branching_points.append({
                    "branch_point": thought.branch_from_thought,
                    "branch_id": thought.branch_id,
                    "branch_thought": thought.thought_number,
                    "content": thought.content[:100] + "..." if len(thought.content) > 100 else thought.content
                })
        
        return branching_points
    
    def _extract_key_insights(self, session: ThinkingSession) -> List[Dict[str, Any]]:
        """Extract key insights from the session"""
        insights = []
        
        # High confidence thoughts
        high_confidence = [t for t in session.thoughts if t.confidence >= 0.8]
        for thought in high_confidence[:3]:  # Top 3
            insights.append({
                "type": "high_confidence",
                "content": thought.content,
                "confidence": thought.confidence,
                "thought_number": thought.thought_number
            })
        
        # Thoughts with evidence
        evidenced = [t for t in session.thoughts if t.evidence]
        for thought in evidenced[:2]:  # Top 2
            insights.append({
                "type": "well_evidenced",
                "content": thought.content,
                "evidence_count": len(thought.evidence),
                "thought_number": thought.thought_number
            })
        
        # Decision points
        decisions = [t for t in session.thoughts if t.type == ThoughtType.DECISION]
        for thought in decisions:
            insights.append({
                "type": "decision",
                "content": thought.content,
                "thought_number": thought.thought_number
            })
        
        return insights