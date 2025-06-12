"""
fw_interests tool - Curiosity-driven exploration for intellectual discovery
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import random
import logging
from pathlib import Path

from federation_web.tools.base import BaseTool
from federation_web.core.providers import MultiProviderSearch
from federation_web.core.extraction import ContentExtractor
from federation_web.core.cache import WebCache

class InterestsTool(BaseTool):
    """Exploration and discovery tool for break time and intellectual curiosity"""
    
    def __init__(self, config, context):
        super().__init__(config, context)
        self.search = MultiProviderSearch(config.list())
        self.extractor = ContentExtractor(config.list())
        self.cache = WebCache(config.list())
        self.logger = logging.getLogger("fw_interests")
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Optional starting point for exploration"
                },
                "mode": {
                    "type": "string",
                    "enum": ["explore", "connections", "surprise_me", "visual"],
                    "default": "explore",
                    "description": "Exploration mode"
                },
                "mood": {
                    "type": "string",
                    "enum": ["curious", "deep_dive", "casual", "focused", "collaborative"],
                    "default": "curious",
                    "description": "Current mood/energy level"
                },
                "energy": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                    "description": "Energy level for exploration"
                },
                "time_limit": {
                    "type": "string",
                    "default": "30min",
                    "description": "Time boundary for exploration"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Interest categories to focus on"
                },
                "depth": {
                    "type": "string",
                    "enum": ["surface", "medium", "rabbit_hole"],
                    "default": "medium",
                    "description": "How deep to explore"
                },
                "visual": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include images/videos/diagrams"
                },
                "save_to": {
                    "type": "string",
                    "enum": ["personal", "shared", "both", "auto", "none"],
                    "default": "auto",
                    "description": "Where to save discoveries"
                },
                "recommend_to": {
                    "type": "string",
                    "enum": ["DT", "CC", "all", "auto", "none"],
                    "description": "Who to recommend discoveries to"
                },
                "connect_with": {
                    "type": "string",
                    "default": "auto",
                    "description": "Connect with existing interests"
                },
                "relate_to": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Previous interests to connect with"
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute interest exploration"""
        try:
            mode = arguments.get("mode", "explore")
            mood = arguments.get("mood", "curious")
            
            # Get mood preset settings
            mood_settings = self.config.get(f"mood_presets.{mood}", {
                "depth": "medium",
                "time": 30,
                "variety": "medium"
            })
            
            # Route to appropriate exploration method
            if mode == "surprise_me":
                result = await self._surprise_exploration(arguments, mood_settings)
            elif mode == "connections":
                result = await self._connection_exploration(arguments, mood_settings)
            elif mode == "visual":
                result = await self._visual_exploration(arguments, mood_settings)
            else:  # explore mode
                result = await self._standard_exploration(arguments, mood_settings)
            
            # Save discoveries if requested
            if arguments.get("save_to", "auto") != "none":
                save_result = await self._save_discoveries(
                    discoveries=result.get("discoveries", []),
                    save_to=arguments.get("save_to", "auto"),
                    recommend_to=arguments.get("recommend_to"),
                    session_metadata={
                        "mode": mode,
                        "mood": mood,
                        "timestamp": datetime.now().isoformat(),
                        "query": arguments.get("query", "spontaneous exploration")
                    }
                )
                result["saved_to"] = save_result
            
            return self.create_response(
                status="success",
                mode=mode,
                mood=mood,
                **result
            )
            
        except Exception as e:
            self.logger.error(f"Interest exploration error: {e}")
            return self.create_error_response(str(e))
    
    async def _surprise_exploration(self, arguments: Dict[str, Any], mood_settings: Dict) -> Dict[str, Any]:
        """Random discovery mode"""
        categories = arguments.get("categories") or self.config.get("interest_categories", [])
        
        # Pick random categories if not specified
        if not categories:
            categories = ["science", "art", "technology", "nature", "history"]
        
        chosen_categories = random.sample(categories, min(3, len(categories)))
        
        # Generate surprise queries
        surprise_queries = []
        query_templates = [
            "fascinating facts about {category}",
            "unexpected discoveries in {category}",
            "beautiful examples of {category}",
            "mind-blowing {category} innovations",
            "hidden gems in {category}"
        ]
        
        for category in chosen_categories:
            template = random.choice(query_templates)
            surprise_queries.append(template.format(category=category))
        
        # Search for surprises
        discoveries = []
        for query in surprise_queries:
            try:
                search_result = await self.search.search(query, max_results=3)
                
                # Extract interesting snippets
                for result in search_result.get("results", [])[:2]:
                    discoveries.append({
                        "type": "surprise",
                        "category": category,
                        "title": result.get("title"),
                        "snippet": result.get("snippet"),
                        "url": result.get("url"),
                        "surprise_factor": random.uniform(0.7, 1.0)  # How surprising
                    })
            except Exception as e:
                self.logger.warning(f"Error in surprise search: {e}")
        
        # Add a random "did you know" fact
        discoveries.append({
            "type": "random_fact",
            "content": "The exploration itself is the reward - every curiosity followed leads to new connections.",
            "category": "meta",
            "surprise_factor": 0.8
        })
        
        return {
            "discoveries": discoveries,
            "categories_explored": chosen_categories,
            "surprise_level": "high",
            "next_suggestions": self._generate_follow_up_suggestions(discoveries)
        }
    
    async def _connection_exploration(self, arguments: Dict[str, Any], mood_settings: Dict) -> Dict[str, Any]:
        """Explore connections between interests"""
        query = arguments.get("query", "")
        relate_to = arguments.get("relate_to", [])
        
        if not query and not relate_to:
            # Need something to connect
            return {
                "discoveries": [],
                "error": "Need a query or previous interests to find connections"
            }
        
        # Load previous interests if connecting
        previous_interests = []
        if relate_to:
            # TODO: Load from interest documents
            previous_interests = relate_to  # For now, use as-is
        
        # Generate connection queries
        connection_queries = []
        
        if query and previous_interests:
            for interest in previous_interests[:3]:
                connection_queries.append(f"{query} and {interest}")
                connection_queries.append(f"relationship between {query} and {interest}")
        elif query:
            connection_queries = [
                f"{query} applications",
                f"{query} in unexpected places",
                f"history of {query}",
                f"future of {query}"
            ]
        
        # Search for connections
        discoveries = []
        connection_map = {}
        
        for conn_query in connection_queries[:4]:  # Limit searches
            try:
                search_result = await self.search.search(conn_query, max_results=3)
                
                for result in search_result.get("results", [])[:2]:
                    # Extract content for connection analysis
                    try:
                        extracted = await self.extractor.extract_from_url(result["url"])
                        
                        # Find interesting connections in content
                        connections = self._analyze_connections(
                            content=extracted.get("text_content", ""),
                            query=query,
                            related=previous_interests
                        )
                        
                        discoveries.append({
                            "type": "connection",
                            "title": result.get("title"),
                            "url": result.get("url"),
                            "connections_found": connections,
                            "excerpt": extracted.get("excerpt", ""),
                            "connection_strength": len(connections) / 10.0  # Simple metric
                        })
                        
                        # Build connection map
                        for conn in connections:
                            if conn not in connection_map:
                                connection_map[conn] = []
                            connection_map[conn].append(result.get("title"))
                            
                    except Exception as e:
                        self.logger.warning(f"Error extracting for connections: {e}")
                        
            except Exception as e:
                self.logger.warning(f"Error in connection search: {e}")
        
        return {
            "discoveries": discoveries,
            "connection_map": connection_map,
            "total_connections": sum(len(d.get("connections_found", [])) for d in discoveries),
            "strongest_connections": self._find_strongest_connections(discoveries),
            "next_suggestions": self._generate_connection_suggestions(connection_map)
        }
    
    async def _visual_exploration(self, arguments: Dict[str, Any], mood_settings: Dict) -> Dict[str, Any]:
        """Visual-focused exploration"""
        query = arguments.get("query", "beautiful visualizations")
        
        # Enhance query for visual content
        visual_queries = [
            f"{query} infographic",
            f"{query} visualization",
            f"{query} diagram",
            f"{query} gallery",
            f"{query} visual guide"
        ]
        
        discoveries = []
        
        for vq in visual_queries[:3]:
            try:
                search_result = await self.search.search(vq, max_results=5)
                
                for result in search_result.get("results", []):
                    # Prioritize results that likely have visual content
                    if any(term in result.get("title", "").lower() for term in ["image", "photo", "visual", "diagram", "gallery"]):
                        try:
                            extracted = await self.extractor.extract_from_url(result["url"])
                            
                            if extracted.get("images"):
                                discoveries.append({
                                    "type": "visual",
                                    "title": result.get("title"),
                                    "url": result.get("url"),
                                    "images": extracted.get("images", [])[:5],  # Limit images
                                    "image_count": len(extracted.get("images", [])),
                                    "excerpt": extracted.get("excerpt", ""),
                                    "visual_richness": min(1.0, len(extracted.get("images", [])) / 10)
                                })
                        except Exception as e:
                            self.logger.warning(f"Error extracting visual content: {e}")
                            
            except Exception as e:
                self.logger.warning(f"Error in visual search: {e}")
        
        # Sort by visual richness
        discoveries.sort(key=lambda x: x.get("visual_richness", 0), reverse=True)
        
        return {
            "discoveries": discoveries[:10],  # Top 10 visual discoveries
            "total_images": sum(d.get("image_count", 0) for d in discoveries),
            "visual_categories": self._categorize_visuals(discoveries),
            "next_suggestions": [f"more {query} examples", f"{query} tutorials", f"{query} inspiration"]
        }
    
    async def _standard_exploration(self, arguments: Dict[str, Any], mood_settings: Dict) -> Dict[str, Any]:
        """Standard exploration mode"""
        query = arguments.get("query", "")
        depth = arguments.get("depth", mood_settings.get("depth", "medium"))
        
        if not query:
            # Generate exploration query based on categories
            categories = arguments.get("categories", []) or random.sample(
                self.config.get("interest_categories", []), 1
            )
            if categories:
                query = f"interesting developments in {categories[0]}"
            else:
                query = "fascinating discoveries this week"
        
        # Search
        search_result = await self.search.search(query, max_results=10)
        
        discoveries = []
        
        # Process based on depth
        results_to_process = 3 if depth == "surface" else 5 if depth == "medium" else 8
        
        for result in search_result.get("results", [])[:results_to_process]:
            try:
                extracted = await self.extractor.extract_from_url(result["url"])
                
                discovery = {
                    "type": "exploration",
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "excerpt": extracted.get("excerpt", ""),
                    "word_count": extracted.get("metrics", {}).get("word_count", 0),
                    "has_code": len(extracted.get("code_blocks", [])) > 0,
                    "has_images": len(extracted.get("images", [])) > 0,
                    "interest_score": self._calculate_interest_score(extracted, query)
                }
                
                # Add full content for deep dives
                if depth == "rabbit_hole":
                    discovery["content_preview"] = extracted.get("content", "")[:2000]
                    discovery["key_points"] = self._extract_key_points(extracted.get("text_content", ""))
                
                discoveries.append(discovery)
                
            except Exception as e:
                self.logger.warning(f"Error processing discovery: {e}")
        
        # Sort by interest score
        discoveries.sort(key=lambda x: x.get("interest_score", 0), reverse=True)
        
        return {
            "discoveries": discoveries,
            "exploration_depth": depth,
            "total_found": len(search_result.get("results", [])),
            "processed": len(discoveries),
            "average_interest_score": sum(d.get("interest_score", 0) for d in discoveries) / max(1, len(discoveries)),
            "next_suggestions": self._generate_exploration_suggestions(discoveries, query)
        }
    
    async def _save_discoveries(self, discoveries: List[Dict], save_to: str, 
                              recommend_to: Optional[str], session_metadata: Dict) -> Dict[str, Any]:
        """Save discoveries to SharedVault interest documents"""
        personal_doc = self.context.get_personal_interest_doc()
        shared_doc = self.context.get_shared_interest_doc()
        
        saved_locations = []
        
        # Format discoveries for markdown
        formatted_discoveries = self._format_discoveries_markdown(discoveries, session_metadata)
        
        try:
            # Determine where to save
            if save_to == "auto":
                # Auto-decide based on interest score and collaboration potential
                avg_score = sum(d.get("interest_score", 0.5) for d in discoveries) / max(1, len(discoveries))
                has_connections = any(d.get("type") == "connection" for d in discoveries)
                
                if avg_score > 0.7 or has_connections:
                    save_to = "both"
                else:
                    save_to = "personal"
            
            # Save to personal document
            if save_to in ["personal", "both"]:
                await self._append_to_document(personal_doc, formatted_discoveries)
                saved_locations.append("personal")
            
            # Save to shared document
            if save_to in ["shared", "both"]:
                shared_content = formatted_discoveries
                if recommend_to and recommend_to != "none":
                    shared_content = f"## Recommended by CC to {recommend_to}\n\n{shared_content}"
                
                await self._append_to_document(shared_doc, shared_content)
                saved_locations.append("shared")
            
            # Handle recommendations
            if recommend_to and recommend_to != "none":
                # TODO: Implement wake notifications
                pass
            
            return {
                "locations": saved_locations,
                "documents_updated": len(saved_locations),
                "recommendation_sent": recommend_to if recommend_to != "none" else None
            }
            
        except Exception as e:
            self.logger.error(f"Error saving discoveries: {e}")
            return {
                "locations": [],
                "error": str(e)
            }
    
    def _analyze_connections(self, content: str, query: str, related: List[str]) -> List[str]:
        """Analyze content for connections"""
        connections = []
        content_lower = content.lower()
        
        # Look for query term connections
        if query and query.lower() in content_lower:
            # Find sentences containing the query
            sentences = content.split('.')
            for sentence in sentences:
                if query.lower() in sentence.lower():
                    # Extract key concepts from sentence
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if len(word) > 5 and word.lower() != query.lower():
                            connections.append(word.strip('.,!?'))
                            if len(connections) >= 5:
                                break
        
        # Look for related term connections
        for term in related:
            if term.lower() in content_lower:
                connections.append(f"Links to {term}")
        
        return list(set(connections))[:10]  # Unique connections, max 10
    
    def _calculate_interest_score(self, extracted: Dict[str, Any], query: str) -> float:
        """Calculate how interesting a discovery might be"""
        score = 0.5  # Base score
        
        # Content richness
        word_count = extracted.get("metrics", {}).get("word_count", 0)
        if word_count > 500:
            score += 0.1
        if word_count > 1000:
            score += 0.1
            
        # Media richness
        if extracted.get("images"):
            score += 0.15
        if extracted.get("code_blocks"):
            score += 0.15
            
        # Relevance to query
        content = extracted.get("text_content", "").lower()
        if query and query.lower() in content:
            score += 0.1
            # Multiple mentions increase score
            mentions = content.count(query.lower())
            score += min(0.1, mentions * 0.02)
        
        return min(1.0, score)
    
    def _extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """Extract key points from content"""
        # Simple extraction based on sentences with key indicators
        key_indicators = ["important", "key", "significant", "notable", "interesting", 
                         "fascinating", "discovered", "found that", "shows that", "reveals"]
        
        sentences = content.split('.')
        key_points = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in key_indicators):
                # Clean and add
                point = sentence.strip()
                if len(point) > 20 and len(point) < 200:
                    key_points.append(point)
                    if len(key_points) >= max_points:
                        break
        
        return key_points
    
    def _find_strongest_connections(self, discoveries: List[Dict]) -> List[Dict]:
        """Find the strongest connections from discoveries"""
        strong_connections = []
        
        for discovery in discoveries:
            if discovery.get("connection_strength", 0) > 0.5:
                strong_connections.append({
                    "title": discovery.get("title"),
                    "strength": discovery.get("connection_strength"),
                    "connections": discovery.get("connections_found", [])[:3]
                })
        
        # Sort by strength
        strong_connections.sort(key=lambda x: x["strength"], reverse=True)
        return strong_connections[:3]
    
    def _categorize_visuals(self, discoveries: List[Dict]) -> Dict[str, int]:
        """Categorize visual discoveries"""
        categories = {
            "diagrams": 0,
            "photos": 0,
            "infographics": 0,
            "charts": 0,
            "other": 0
        }
        
        for discovery in discoveries:
            title_lower = discovery.get("title", "").lower()
            if "diagram" in title_lower:
                categories["diagrams"] += 1
            elif "photo" in title_lower or "image" in title_lower:
                categories["photos"] += 1
            elif "infographic" in title_lower:
                categories["infographics"] += 1
            elif "chart" in title_lower or "graph" in title_lower:
                categories["charts"] += 1
            else:
                categories["other"] += 1
                
        return {k: v for k, v in categories.items() if v > 0}
    
    def _generate_follow_up_suggestions(self, discoveries: List[Dict]) -> List[str]:
        """Generate suggestions for follow-up exploration"""
        suggestions = []
        
        # Based on categories found
        categories = set()
        for d in discoveries:
            if d.get("category"):
                categories.add(d["category"])
        
        for category in list(categories)[:3]:
            suggestions.append(f"Deep dive into {category}")
            
        # Add general suggestions
        suggestions.extend([
            "Find connections between these discoveries",
            "Explore the history behind one of these",
            "Look for practical applications"
        ])
        
        return suggestions[:5]
    
    def _generate_connection_suggestions(self, connection_map: Dict) -> List[str]:
        """Generate suggestions based on connections found"""
        suggestions = []
        
        # Most connected concepts
        if connection_map:
            sorted_connections = sorted(connection_map.items(), key=lambda x: len(x[1]), reverse=True)
            for concept, _ in sorted_connections[:3]:
                suggestions.append(f"Explore more about {concept}")
        
        suggestions.append("Find more unexpected connections")
        return suggestions
    
    def _generate_exploration_suggestions(self, discoveries: List[Dict], query: str) -> List[str]:
        """Generate suggestions for continued exploration"""
        suggestions = []
        
        # Based on content types found
        has_code = any(d.get("has_code") for d in discoveries)
        has_images = any(d.get("has_images") for d in discoveries)
        
        if has_code:
            suggestions.append(f"{query} implementation examples")
        if has_images:
            suggestions.append(f"{query} visual gallery")
            
        # Based on interest scores
        high_interest = [d for d in discoveries if d.get("interest_score", 0) > 0.7]
        if high_interest:
            suggestions.append(f"Similar to: {high_interest[0].get('title', '')[:30]}...")
            
        # General suggestions
        suggestions.extend([
            f"{query} recent developments",
            f"{query} beginner's guide",
            f"Surprising facts about {query}"
        ])
        
        return suggestions[:5]
    
    def _format_discoveries_markdown(self, discoveries: List[Dict], metadata: Dict) -> str:
        """Format discoveries for markdown storage"""
        lines = []
        
        # Header with metadata
        lines.append(f"\n## Discovery Session - {metadata['timestamp']}")
        lines.append(f"**Mode**: {metadata['mode']} | **Mood**: {metadata['mood']}")
        if metadata.get('query') != "spontaneous exploration":
            lines.append(f"**Starting point**: {metadata['query']}")
        lines.append("")
        
        # Discoveries
        for i, discovery in enumerate(discoveries, 1):
            lines.append(f"### {i}. {discovery.get('title', 'Untitled Discovery')}")
            
            if discovery.get('url'):
                lines.append(f"🔗 [{discovery['url']}]({discovery['url']})")
                
            if discovery.get('excerpt'):
                lines.append(f"\n{discovery['excerpt']}")
                
            # Type-specific content
            if discovery.get('type') == 'connection':
                if discovery.get('connections_found'):
                    lines.append(f"\n**Connections found**: {', '.join(discovery['connections_found'][:5])}")
                    
            elif discovery.get('type') == 'visual':
                lines.append(f"\n**Visual content**: {discovery.get('image_count', 0)} images")
                
            elif discovery.get('type') == 'surprise':
                lines.append(f"\n**Category**: {discovery.get('category', 'general')}")
                lines.append(f"**Surprise factor**: {'⭐' * int(discovery.get('surprise_factor', 0.5) * 5)}")
                
            # Interest score
            if discovery.get('interest_score'):
                score = discovery['interest_score']
                lines.append(f"\n**Interest level**: {'🔥' * int(score * 5)}")
                
            # Key points for deep dives
            if discovery.get('key_points'):
                lines.append("\n**Key points**:")
                for point in discovery['key_points']:
                    lines.append(f"- {point}")
                    
            lines.append("")  # Blank line between discoveries
        
        # Follow-up suggestions
        if any(d.get('next_suggestions') for d in discoveries):
            lines.append("### 💡 Follow-up Ideas")
            all_suggestions = []
            for d in discoveries:
                if d.get('next_suggestions'):
                    all_suggestions.extend(d['next_suggestions'])
            
            # Unique suggestions
            unique_suggestions = list(set(all_suggestions))[:5]
            for suggestion in unique_suggestions:
                lines.append(f"- {suggestion}")
        
        return '\n'.join(lines)
    
    async def _append_to_document(self, doc_path: Path, content: str) -> None:
        """Append content to a document"""
        # Ensure directory exists
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing content
        existing_content = ""
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Append new content
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(existing_content)
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write(content)
            f.write('\n')