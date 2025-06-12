"""
fw_research tool - Work-focused web research with ReAct orchestration
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from federation_web.tools.base import BaseTool
from federation_web.core.providers import MultiProviderSearch
from federation_web.core.extraction import ContentExtractor
from federation_web.core.cache import WebCache
from federation_web.core.react import ReactOrchestrator, ActionType

class ResearchTool(BaseTool):
    """Task-driven web research tool"""
    
    def __init__(self, config, context):
        super().__init__(config, context)
        self.search = MultiProviderSearch(config.list())
        self.extractor = ContentExtractor(config.list())
        self.cache = WebCache(config.list())
        self.logger = logging.getLogger("fw_research")
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query or research question"
                },
                "mode": {
                    "type": "string",
                    "enum": ["auto", "search", "extract", "analyze"],
                    "default": "auto",
                    "description": "Research mode"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["auto"],
                    "description": "Search sources (brave, duckduckgo, google, or auto)"
                },
                "extract": {
                    "type": "string",
                    "enum": ["smart", "full", "summary", "structured"],
                    "default": "smart",
                    "description": "Content extraction mode"
                },
                "chunk_strategy": {
                    "type": "string",
                    "enum": ["auto", "fixed", "content-aware"],
                    "default": "auto",
                    "description": "Chunking strategy for content"
                },
                "memorize": {
                    "type": "boolean",
                    "default": True,
                    "description": "Auto-save important findings to memory"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID to link related searches"
                },
                "context": {
                    "type": "string",
                    "description": "Task or project context"
                },
                "fallback": {
                    "type": "boolean",
                    "default": True,
                    "description": "Use fallback search providers if primary fails"
                },
                "max_results": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Maximum search results to process"
                },
                "max_extractions": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Maximum pages to extract content from"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute research with ReAct orchestration"""
        try:
            self.validate_arguments(arguments)
            
            # Set up session
            session_id = arguments.get("session_id") or f"research_{uuid.uuid4().hex[:8]}"
            if arguments.get("context"):
                self.context.set_session(session_id, task=arguments.get("context"))
            
            # Check cache first
            cache_key = {
                "tool": "fw_research",
                "query": arguments["query"],
                "sources": arguments.get("sources", ["auto"]),
                "mode": arguments.get("mode", "auto")
            }
            
            cached_result = await self.cache.get(cache_key)
            if cached_result and not arguments.get("force_refresh", False):
                self.logger.info(f"Returning cached result for: {arguments['query']}")
                return self.create_response(
                    status="success",
                    source="cache",
                    **cached_result
                )
            
            # Set up ReAct orchestrator
            orchestrator = ReactOrchestrator(self.config.list())
            
            # Define action handlers
            action_handlers = {
                ActionType.SEARCH: lambda params: self._handle_search(params),
                ActionType.EXTRACT: lambda params: self._handle_extract(params),
                ActionType.CHUNK: lambda params: self._handle_chunk(params),
                ActionType.MEMORIZE: lambda params: self._handle_memorize(params),
                ActionType.CACHE: lambda params: self._handle_cache(cache_key, params)
            }
            
            # Run orchestration
            orchestration_result = await orchestrator.orchestrate(
                query=arguments["query"],
                context={
                    "sources": arguments.get("sources", ["auto"]),
                    "max_results": arguments.get("max_results", 10),
                    "max_extractions": arguments.get("max_extractions", 3),
                    "extract_mode": arguments.get("extract", "smart"),
                    "preserve_code": True,  # Always preserve for work research
                    "fallback": arguments.get("fallback", True),
                    "min_good_results": 1
                },
                action_handlers=action_handlers
            )
            
            # Process results based on mode
            mode = arguments.get("mode", "auto")
            processed_results = await self._process_results(
                mode=mode,
                orchestration=orchestration_result,
                extract_mode=arguments.get("extract", "smart"),
                chunk_strategy=arguments.get("chunk_strategy", "auto")
            )
            
            # Auto-memorize if enabled and results are good
            if arguments.get("memorize", True) and processed_results.get("quality_score", 0) > 0.7:
                memory_result = await self._memorize_findings(
                    query=arguments["query"],
                    results=processed_results,
                    context=arguments.get("context"),
                    session_id=session_id
                )
                processed_results["memory_id"] = memory_result.get("id")
            
            # Cache successful results
            if processed_results.get("success"):
                await self.cache.set(cache_key, processed_results, ttl=300)  # 5 min cache
            
            return self.create_response(
                status="success",
                session_id=session_id,
                **processed_results
            )
            
        except Exception as e:
            self.logger.error(f"Research error: {e}")
            return self.create_error_response(str(e))
    
    async def _handle_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search action"""
        return await self.search.search(
            query=params["query"],
            sources=params.get("sources", ["auto"]),
            max_results=params.get("max_results", 10)
        )
    
    async def _handle_extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content extraction"""
        return await self.extractor.extract_from_url(params["url"])
    
    async def _handle_chunk(self, params: Dict[str, Any]) -> List[str]:
        """Handle content chunking"""
        content = params.get("content", "")
        strategy = params.get("strategy", "auto")
        
        if strategy == "content-aware" or (strategy == "auto" and len(content) > 5000):
            # Use smart chunking
            return self.extractor.chunk_content(
                content,
                chunk_size=params.get("chunk_size", 1000),
                chunk_overlap=params.get("chunk_overlap", 200)
            )
        else:
            # Simple fixed-size chunking
            chunk_size = params.get("chunk_size", 1000)
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunks.append(content[i:i + chunk_size])
            return chunks
    
    async def _handle_memorize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory storage"""
        # TODO: Integrate with Federation memory system
        # For now, return mock result
        return {
            "id": f"mem_{uuid.uuid4().hex[:8]}",
            "status": "stored",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_cache(self, cache_key: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Handle caching"""
        await self.cache.set(cache_key, params["data"], ttl=params.get("ttl", 300))
        return True
    
    async def _process_results(self, mode: str, orchestration: Dict[str, Any], 
                              extract_mode: str, chunk_strategy: str) -> Dict[str, Any]:
        """Process orchestration results based on mode"""
        results = orchestration.get("results", [])
        
        if mode == "search" or (mode == "auto" and not any(r.get("content") for r in results)):
            # Return search results only
            search_results = [r for r in results if r.get("results")]
            return {
                "mode": "search",
                "results": search_results[0]["results"] if search_results else [],
                "total_results": sum(len(r.get("results", [])) for r in search_results),
                "providers_used": search_results[0].get("providers_used", []) if search_results else [],
                "quality_score": 0.8 if search_results else 0.2,
                "success": bool(search_results)
            }
        
        elif mode == "extract" or mode == "auto":
            # Return extracted content
            extracted_results = [r for r in results if r.get("content")]
            
            if extract_mode == "summary":
                # Summarize extracted content
                summaries = []
                for result in extracted_results:
                    summaries.append({
                        "url": result["url"],
                        "title": result.get("title", ""),
                        "excerpt": result.get("excerpt", ""),
                        "word_count": result.get("metrics", {}).get("word_count", 0)
                    })
                
                return {
                    "mode": "extract_summary",
                    "summaries": summaries,
                    "total_extracted": len(summaries),
                    "quality_score": min(1.0, len(summaries) / 3),
                    "success": bool(summaries)
                }
                
            elif extract_mode == "structured":
                # Return structured data
                structured_data = []
                for result in extracted_results:
                    structured_data.append({
                        "url": result["url"],
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "code_blocks": result.get("code_blocks", []),
                        "images": result.get("images", []),
                        "links": result.get("links", []),
                        "metrics": result.get("metrics", {})
                    })
                
                return {
                    "mode": "extract_structured",
                    "data": structured_data,
                    "total_extracted": len(structured_data),
                    "quality_score": min(1.0, len(structured_data) / 2),
                    "success": bool(structured_data)
                }
                
            else:  # smart or full
                # Return full extracted content with smart processing
                processed_content = []
                for result in extracted_results:
                    content = result.get("content", "")
                    
                    # Chunk if needed
                    if chunk_strategy != "none" and len(content) > 2000:
                        chunks = await self._handle_chunk({
                            "content": content,
                            "strategy": chunk_strategy
                        })
                        processed_content.append({
                            "url": result["url"],
                            "title": result.get("title", ""),
                            "chunks": chunks,
                            "chunk_count": len(chunks),
                            "original_length": len(content),
                            "code_blocks": result.get("code_blocks", [])
                        })
                    else:
                        processed_content.append({
                            "url": result["url"],
                            "title": result.get("title", ""),
                            "content": content,
                            "code_blocks": result.get("code_blocks", [])
                        })
                
                return {
                    "mode": "extract_smart" if extract_mode == "smart" else "extract_full",
                    "content": processed_content,
                    "total_extracted": len(processed_content),
                    "quality_score": min(1.0, len(processed_content) / 2),
                    "success": bool(processed_content)
                }
        
        else:  # analyze mode
            # Return analysis of results
            analysis = {
                "search_performed": any(r.get("results") for r in results),
                "content_extracted": any(r.get("content") for r in results),
                "total_sources": len([r for r in results if r.get("url")]),
                "code_found": any(r.get("code_blocks") for r in results),
                "average_content_length": sum(r.get("metrics", {}).get("word_count", 0) for r in results) / max(1, len(results)),
                "orchestration": orchestration
            }
            
            return {
                "mode": "analyze",
                "analysis": analysis,
                "quality_score": orchestration.get("success", False) * 0.9,
                "success": orchestration.get("success", False)
            }
    
    async def _memorize_findings(self, query: str, results: Dict[str, Any], 
                               context: Optional[str], session_id: str) -> Dict[str, Any]:
        """Store important findings in memory"""
        # TODO: Integrate with ChromaDB memory system
        # For now, return mock result
        memory_content = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "session_id": session_id,
            "result_summary": {
                "mode": results.get("mode"),
                "total_results": results.get("total_results", 0),
                "quality_score": results.get("quality_score", 0),
                "key_findings": self._extract_key_findings(results)
            }
        }
        
        return {
            "id": f"mem_{uuid.uuid4().hex[:8]}",
            "content": memory_content,
            "tags": ["research", "fw_research", context] if context else ["research", "fw_research"]
        }
    
    def _extract_key_findings(self, results: Dict[str, Any]) -> List[str]:
        """Extract key findings from results"""
        findings = []
        
        if results.get("mode") == "search":
            # Top search results
            for result in results.get("results", [])[:3]:
                findings.append(f"{result.get('title')} - {result.get('url')}")
                
        elif "extract" in results.get("mode", ""):
            # Key extracted content
            if results.get("summaries"):
                for summary in results.get("summaries", [])[:3]:
                    findings.append(f"{summary.get('title')} ({summary.get('word_count')} words)")
            elif results.get("content"):
                for content in results.get("content", [])[:3]:
                    title = content.get("title", "Unknown")
                    findings.append(f"{title} - {content.get('url')}")
                    
        return findings