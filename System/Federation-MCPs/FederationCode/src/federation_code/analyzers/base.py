"""Base analyzer interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Aspect(Enum):
    """Analysis aspects."""
    BUGS = "bugs"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    ALL = "all"


@dataclass
class Issue:
    """Code issue representation."""
    id: str
    file: str
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    severity: Severity = Severity.INFO
    aspect: Aspect = Aspect.BUGS
    type: str = ""
    message: str = ""
    description: str = ""
    suggestion: Optional[str] = None
    fix_available: bool = False
    context: List[str] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = []
        if self.references is None:
            self.references = []


@dataclass
class AnalysisResult:
    """Analysis result container."""
    summary: Dict[str, Any]
    issues: List[Issue]
    execution_time: float
    files_analyzed: int
    cache_hits: int = 0
    partial: bool = False
    progress: float = 1.0


class BaseAnalyzer(ABC):
    """Base class for all code analyzers."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Perform analysis on the given data."""
        pass
    
    @abstractmethod
    def can_stream(self) -> bool:
        """Check if this analyzer supports streaming."""
        pass
        
    async def analyze_stream(self, data: Dict[str, Any]) -> AsyncGenerator[AnalysisResult, None]:
        """Stream analysis results (override if streaming is supported)."""
        if not self.can_stream():
            # Fall back to regular analysis
            result = await self.analyze(data)
            yield result
        else:
            raise NotImplementedError("Streaming analysis not implemented")
            
    def supports_aspect(self, aspect: Aspect) -> bool:
        """Check if analyzer supports the given aspect."""
        return True  # Override in subclasses
        
    def estimate_time(self, data: Dict[str, Any]) -> float:
        """Estimate analysis time in seconds."""
        return 1.0  # Override in subclasses