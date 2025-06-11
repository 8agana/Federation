#!/usr/bin/env python3
"""
API Standardization utilities for Federation Memory System
Ensures consistent parameter naming, return formats, and error handling
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json


class APIStandardizer:
    """Utilities for standardizing API responses and parameters"""
    
    @staticmethod
    def standardize_memory_response(memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize memory response format across all bridge operations
        
        Args:
            memory_data: Raw memory data from ChromaDB
            
        Returns:
            Standardized memory dictionary
        """
        standardized = {
            'id': memory_data.get('id', ''),
            'content': memory_data.get('content', ''),
            'metadata': memory_data.get('metadata', {}),
            'relevance_score': memory_data.get('relevance_score', memory_data.get('distance', 0.0)),
            'created_at': None,
            'updated_at': None,
            'title': '',
            'tags': [],
            'priority': 1,
            'domain': 'unknown'
        }
        
        # Extract standard fields from metadata
        metadata = memory_data.get('metadata', {})
        if metadata:
            standardized['created_at'] = metadata.get('created_at')
            standardized['updated_at'] = metadata.get('updated_at')
            standardized['title'] = metadata.get('title', '')
            standardized['priority'] = metadata.get('priority', 1)
            standardized['domain'] = metadata.get('domain', 'unknown')
            
            # Parse tags
            tags_str = metadata.get('tags', '')
            if tags_str:
                standardized['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        return standardized
    
    @staticmethod
    def standardize_search_results(results: List[Dict[str, Any]], 
                                 query: str = '', 
                                 n_results: int = 5) -> Dict[str, Any]:
        """
        Standardize search results format
        
        Args:
            results: List of memory dictionaries
            query: Original search query
            n_results: Number of results requested
            
        Returns:
            Standardized search response
        """
        standardized_memories = [
            APIStandardizer.standardize_memory_response(memory) 
            for memory in results
        ]
        
        return {
            'query': query,
            'total_found': len(standardized_memories),
            'requested_count': n_results,
            'memories': standardized_memories,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def standardize_error_response(error: str, operation: str = '', 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Standardize error response format
        
        Args:
            error: Error message
            operation: Name of the operation that failed
            context: Additional context about the error
            
        Returns:
            Standardized error response
        """
        return {
            'success': False,
            'error': str(error),
            'operation': operation,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def standardize_success_response(data: Any, operation: str = '', 
                                   message: str = '') -> Dict[str, Any]:
        """
        Standardize success response format
        
        Args:
            data: The successful result data
            operation: Name of the operation that succeeded
            message: Success message
            
        Returns:
            Standardized success response
        """
        return {
            'success': True,
            'data': data,
            'operation': operation,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def validate_remember_params(content: str, title: str = None, 
                               tags: Union[str, List[str]] = None,
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate and standardize remember operation parameters
        
        Args:
            content: Memory content
            title: Optional title
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Validation result with standardized parameters
        """
        errors = []
        warnings = []
        
        # Validate content
        if not content or not content.strip():
            errors.append("Content cannot be empty")
        elif len(content) > 50000:  # 50KB limit
            warnings.append("Content is very large (>50KB)")
        
        # Standardize title
        clean_title = (title or '').strip()
        if len(clean_title) > 200:
            clean_title = clean_title[:200]
            warnings.append("Title truncated to 200 characters")
        
        # Standardize tags
        clean_tags = []
        if tags:
            if isinstance(tags, str):
                clean_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            elif isinstance(tags, list):
                clean_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
        
        if len(clean_tags) > 20:
            clean_tags = clean_tags[:20]
            warnings.append("Tags limited to 20 maximum")
        
        # Validate metadata
        clean_metadata = metadata or {}
        if not isinstance(clean_metadata, dict):
            errors.append("Metadata must be a dictionary")
            clean_metadata = {}
        
        # Check for required v5 fields
        v5_defaults = {
            'domain': 'technical',
            'category': 'memory',
            'priority': 1,
            'federation_visible': True,
            'is_private': False
        }
        
        for key, default in v5_defaults.items():
            if key not in clean_metadata:
                clean_metadata[key] = default
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'standardized_params': {
                'content': content.strip() if content else '',
                'title': clean_title,
                'tags': clean_tags,
                'metadata': clean_metadata
            }
        }
    
    @staticmethod
    def validate_recall_params(query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Validate and standardize recall operation parameters
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Validation result with standardized parameters
        """
        errors = []
        warnings = []
        
        # Validate query
        if not query or not query.strip():
            errors.append("Query cannot be empty")
        elif len(query) > 1000:
            warnings.append("Query is very long (>1000 characters)")
        
        # Validate n_results
        clean_n_results = n_results
        if not isinstance(n_results, int) or n_results < 1:
            clean_n_results = 5
            warnings.append("n_results set to default (5)")
        elif n_results > 100:
            clean_n_results = 100
            warnings.append("n_results limited to maximum (100)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'standardized_params': {
                'query': query.strip() if query else '',
                'n_results': clean_n_results
            }
        }
    
    @staticmethod
    def create_health_check_response(status: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standardized health check response
        
        Args:
            status: Health status (healthy, warning, critical, error)
            details: Detailed health information
            
        Returns:
            Standardized health response
        """
        return {
            'status': status,
            'health_score': details.get('health_score', 0.0),
            'summary': {
                'total_memories': details.get('total_memories', 0),
                'recent_24h': details.get('recent_24h', 0),
                'collections': details.get('total_collections', 0),
                'errors': details.get('errors', 0)
            },
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'recommendations': APIStandardizer._generate_health_recommendations(status, details)
        }
    
    @staticmethod
    def _generate_health_recommendations(status: str, details: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on status"""
        recommendations = []
        
        if status == 'critical':
            recommendations.append("Immediate attention required - system may be non-functional")
            if details.get('errors', 0) > 0:
                recommendations.append("Check system logs for error details")
        
        elif status == 'warning':
            recommendations.append("System needs monitoring")
            if details.get('duplicates_found', 0) > 0:
                recommendations.append("Consider running duplicate cleanup")
        
        elif status == 'healthy':
            recommendations.append("System operating normally")
            if details.get('total_memories', 0) == 0:
                recommendations.append("Database is empty - consider adding initial memories")
        
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    print("🔧 API Standardization Test")
    print("=" * 40)
    
    # Test parameter validation
    validation = APIStandardizer.validate_remember_params(
        content="Test memory content",
        title="Test Memory",
        tags=["test", "api", "validation"],
        metadata={"domain": "technical", "priority": 2}
    )
    
    print(f"Parameter validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
    print(f"Warnings: {validation['warnings']}")
    
    # Test response standardization
    mock_memory = {
        'id': 'test_123',
        'content': 'Test content',
        'metadata': {
            'title': 'Test',
            'tags': 'test, api',
            'created_at': datetime.now().isoformat(),
            'priority': 2,
            'domain': 'technical'
        },
        'distance': 0.1
    }
    
    standardized = APIStandardizer.standardize_memory_response(mock_memory)
    print(f"Standardized response keys: {list(standardized.keys())}")
    
    print("\n✅ API Standardization utilities ready!")