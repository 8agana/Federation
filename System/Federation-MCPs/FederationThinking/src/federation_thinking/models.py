"""
Data models for FederationThinking
"""
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class ThoughtType(str, Enum):
    """Types of thoughts"""
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    HYPOTHESIS = "hypothesis"
    QUESTION = "question"
    PROPOSAL = "proposal"
    DECISION = "decision"
    REFLECTION = "reflection"
    REVISION = "revision"
    BRANCH = "branch"

class Framework(str, Enum):
    """Available thinking frameworks"""
    OODA = "ooda"
    SOCRATIC = "socratic"
    FIRST_PRINCIPLES = "first_principles"
    FIVE_WHYS = "five_whys"
    SWOT = "swot"
    DEVILS_ADVOCATE = "devils_advocate"
    LATERAL = "lateral"
    SYSTEMS = "systems"

@dataclass
class Thought:
    """Individual thought in a thinking session"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    content: str = ""
    thought_number: int = 1
    total_thoughts: int = 1
    type: ThoughtType = ThoughtType.ANALYSIS
    framework: Optional[Framework] = None
    framework_step: Optional[str] = None
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Revision and branching
    is_revision: bool = False
    revises_thought: Optional[str] = None
    branch_from_thought: Optional[str] = None
    branch_id: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    shared_with: List[str] = field(default_factory=list)
    saved_to_memory: bool = False
    memory_id: Optional[str] = None
    
    # Connections
    references: List[str] = field(default_factory=list)  # Other thought IDs
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "thought_number": self.thought_number,
            "total_thoughts": self.total_thoughts,
            "type": self.type.value if isinstance(self.type, ThoughtType) else self.type,
            "framework": self.framework.value if isinstance(self.framework, Framework) else self.framework,
            "framework_step": self.framework_step,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "tags": self.tags,
            "is_revision": self.is_revision,
            "revises_thought": self.revises_thought,
            "branch_from_thought": self.branch_from_thought,
            "branch_id": self.branch_id,
            "timestamp": self.timestamp.isoformat(),
            "shared_with": self.shared_with,
            "saved_to_memory": self.saved_to_memory,
            "memory_id": self.memory_id,
            "references": self.references,
            "task_id": self.task_id,
            "project_id": self.project_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Thought':
        """Create from dictionary"""
        # Convert string types back to enums
        if "type" in data and isinstance(data["type"], str):
            data["type"] = ThoughtType(data["type"])
        if "framework" in data and data["framework"] and isinstance(data["framework"], str):
            data["framework"] = Framework(data["framework"])
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)

@dataclass
class ThinkingSession:
    """A complete thinking session"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    context: Optional[str] = None
    framework: Optional[Framework] = None
    thoughts: List[Thought] = field(default_factory=list)
    branches: Dict[str, List[Thought]] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: Literal["active", "paused", "completed"] = "active"
    
    # Integration
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    shared_with: List[str] = field(default_factory=list)
    
    # Metrics
    total_thoughts: int = 0
    total_revisions: int = 0
    total_branches: int = 0
    average_confidence: float = 0.0
    
    def add_thought(self, thought: Thought):
        """Add a thought to the session"""
        thought.session_id = self.id
        self.thoughts.append(thought)
        self.updated_at = datetime.now()
        self.total_thoughts += 1
        
        # Update metrics
        if thought.is_revision:
            self.total_revisions += 1
        if thought.branch_id and thought.branch_id not in self.branches:
            self.branches[thought.branch_id] = []
            self.total_branches += 1
        if thought.branch_id:
            self.branches[thought.branch_id].append(thought)
            
        # Update average confidence
        confidences = [t.confidence for t in self.thoughts if t.confidence > 0]
        if confidences:
            self.average_confidence = sum(confidences) / len(confidences)
    
    def get_current_thought_number(self) -> int:
        """Get the current thought number"""
        if not self.thoughts:
            return 1
        return max(t.thought_number for t in self.thoughts) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "title": self.title,
            "context": self.context,
            "framework": self.framework.value if isinstance(self.framework, Framework) else self.framework,
            "thoughts": [t.to_dict() for t in self.thoughts],
            "branches": {
                bid: [t.to_dict() for t in thoughts]
                for bid, thoughts in self.branches.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "task_id": self.task_id,
            "project_id": self.project_id,
            "shared_with": self.shared_with,
            "total_thoughts": self.total_thoughts,
            "total_revisions": self.total_revisions,
            "total_branches": self.total_branches,
            "average_confidence": self.average_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThinkingSession':
        """Create from dictionary"""
        # Convert framework
        if "framework" in data and data["framework"] and isinstance(data["framework"], str):
            data["framework"] = Framework(data["framework"])
        
        # Convert timestamps
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # Convert thoughts
        if "thoughts" in data:
            data["thoughts"] = [Thought.from_dict(t) for t in data["thoughts"]]
        
        # Convert branches
        if "branches" in data:
            data["branches"] = {
                bid: [Thought.from_dict(t) for t in thoughts]
                for bid, thoughts in data["branches"].items()
            }
        
        return cls(**data)