"""Code analyzers for Federation Code MCP."""

from .base import BaseAnalyzer, AnalysisResult
from .ast_analyzer import ASTAnalyzer
from .security_analyzer import SecurityAnalyzer


def get_analyzer(task_type: str) -> BaseAnalyzer:
    """Get analyzer for task type."""
    analyzers = {
        "analyze": ASTAnalyzer(),
        "security": SecurityAnalyzer(),
        # Add more analyzers as needed
    }
    
    return analyzers.get(task_type)


__all__ = [
    "BaseAnalyzer",
    "AnalysisResult", 
    "ASTAnalyzer",
    "SecurityAnalyzer",
    "get_analyzer"
]