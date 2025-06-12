"""
ReAct (Reasoning + Acting) orchestrator for FederationWeb
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

class ThoughtType(Enum):
    """Types of thoughts in ReAct cycle"""
    INITIAL = "initial"
    OBSERVATION = "observation"
    REASONING = "reasoning"
    PLANNING = "planning"
    EVALUATION = "evaluation"
    CONCLUSION = "conclusion"

class ActionType(Enum):
    """Types of actions that can be taken"""
    SEARCH = "search"
    EXTRACT = "extract"
    CHUNK = "chunk"
    MEMORIZE = "memorize"
    CACHE = "cache"
    FALLBACK = "fallback"
    COMPLETE = "complete"

@dataclass
class Thought:
    """A thought in the ReAct process"""
    type: ThoughtType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class Action:
    """An action to be taken"""
    type: ActionType
    parameters: Dict[str, Any]
    timestamp: datetime
    result: Any = None
    error: Optional[str] = None

@dataclass
class Observation:
    """An observation from action results"""
    action: Action
    content: str
    quality_score: float  # 0-1 score of result quality
    timestamp: datetime
    metadata: Dict[str, Any] = None

class ReactOrchestrator:
    """Orchestrates the ReAct pattern for web research"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.thoughts: List[Thought] = []
        self.actions: List[Action] = []
        self.observations: List[Observation] = []
        self.max_iterations = 5
        self.min_quality_threshold = 0.7
        
    def think(self, thought_type: ThoughtType, content: str, metadata: Dict[str, Any] = None) -> Thought:
        """Record a thought"""
        thought = Thought(
            type=thought_type,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.thoughts.append(thought)
        self.logger.info(f"Thought [{thought_type.value}]: {content}")
        return thought
    
    def plan_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> Action:
        """Plan an action to take"""
        action = Action(
            type=action_type,
            parameters=parameters,
            timestamp=datetime.now()
        )
        self.actions.append(action)
        self.logger.info(f"Action planned [{action_type.value}]: {parameters}")
        return action
    
    def observe(self, action: Action, result: Any, error: Optional[str] = None) -> Observation:
        """Record observation from action result"""
        action.result = result
        action.error = error
        
        # Evaluate quality of result
        quality_score = self._evaluate_result_quality(action, result, error)
        
        # Generate observation content
        if error:
            content = f"Action {action.type.value} failed: {error}"
        else:
            content = self._summarize_result(action, result)
        
        observation = Observation(
            action=action,
            content=content,
            quality_score=quality_score,
            timestamp=datetime.now(),
            metadata={"has_error": bool(error)}
        )
        
        self.observations.append(observation)
        self.logger.info(f"Observation [quality={quality_score:.2f}]: {content}")
        return observation
    
    def _evaluate_result_quality(self, action: Action, result: Any, error: Optional[str]) -> float:
        """Evaluate the quality of an action result"""
        if error:
            return 0.0
            
        if action.type == ActionType.SEARCH:
            # Evaluate search results
            if isinstance(result, dict):
                num_results = len(result.get("results", []))
                if num_results == 0:
                    return 0.1
                elif num_results < 3:
                    return 0.5
                else:
                    return min(1.0, num_results / 10)
            return 0.0
            
        elif action.type == ActionType.EXTRACT:
            # Evaluate extracted content
            if isinstance(result, dict):
                word_count = result.get("metrics", {}).get("word_count", 0)
                has_content = bool(result.get("content"))
                has_code = len(result.get("code_blocks", [])) > 0
                
                score = 0.0
                if has_content:
                    score += 0.5
                if word_count > 100:
                    score += 0.3
                if has_code and action.parameters.get("preserve_code"):
                    score += 0.2
                    
                return min(1.0, score)
            return 0.0
            
        elif action.type in [ActionType.MEMORIZE, ActionType.CACHE]:
            # Success/failure for storage actions
            return 1.0 if result else 0.0
            
        else:
            # Default quality assessment
            return 0.5 if result else 0.0
    
    def _summarize_result(self, action: Action, result: Any) -> str:
        """Summarize action result for observation"""
        if action.type == ActionType.SEARCH:
            num_results = len(result.get("results", []))
            providers = result.get("providers_used", [])
            return f"Found {num_results} results using {', '.join(providers)}"
            
        elif action.type == ActionType.EXTRACT:
            metrics = result.get("metrics", {})
            return f"Extracted {metrics.get('word_count', 0)} words with {metrics.get('code_block_count', 0)} code blocks"
            
        elif action.type == ActionType.CHUNK:
            if isinstance(result, list):
                return f"Created {len(result)} chunks"
            return "Chunking completed"
            
        elif action.type == ActionType.MEMORIZE:
            return f"Memorized with ID: {result.get('id', 'unknown')}"
            
        else:
            return f"Action {action.type.value} completed"
    
    async def orchestrate(self, query: str, context: Dict[str, Any], 
                         action_handlers: Dict[ActionType, Callable]) -> Dict[str, Any]:
        """Orchestrate a complete ReAct cycle"""
        start_time = datetime.now()
        
        # Initial thought
        self.think(
            ThoughtType.INITIAL,
            f"Need to research: {query}",
            {"query": query, "context": context}
        )
        
        # Plan initial action
        initial_action = self.plan_action(
            ActionType.SEARCH,
            {
                "query": query,
                "sources": context.get("sources", ["auto"]),
                "max_results": context.get("max_results", 10)
            }
        )
        
        iteration = 0
        results = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Execute planned actions
            for action in self.actions:
                if action.result is None and action.error is None:
                    # Execute action
                    handler = action_handlers.get(action.type)
                    if handler:
                        try:
                            result = await handler(action.parameters)
                            observation = self.observe(action, result)
                            results.append(result)
                            
                            # Think about observation
                            if observation.quality_score < self.min_quality_threshold:
                                self.think(
                                    ThoughtType.EVALUATION,
                                    f"Result quality is low ({observation.quality_score:.2f}), need to try alternative approach"
                                )
                                
                                # Plan fallback action
                                if action.type == ActionType.SEARCH and context.get("fallback", True):
                                    fallback_sources = self._get_fallback_sources(action.parameters.get("sources", []))
                                    if fallback_sources:
                                        self.plan_action(
                                            ActionType.SEARCH,
                                            {
                                                **action.parameters,
                                                "sources": fallback_sources
                                            }
                                        )
                            else:
                                # Good quality result
                                self.think(
                                    ThoughtType.OBSERVATION,
                                    f"Good result from {action.type.value}: {observation.content}"
                                )
                                
                                # Plan follow-up actions based on results
                                if action.type == ActionType.SEARCH and result.get("results"):
                                    # Plan extraction for top results
                                    for i, search_result in enumerate(result["results"][:3]):
                                        self.plan_action(
                                            ActionType.EXTRACT,
                                            {
                                                "url": search_result["url"],
                                                "preserve_code": context.get("preserve_code", True)
                                            }
                                        )
                                        
                        except Exception as e:
                            self.observe(action, None, str(e))
                            self.logger.error(f"Action {action.type.value} failed: {e}")
            
            # Evaluate if we have enough good results
            good_results = [obs for obs in self.observations if obs.quality_score >= self.min_quality_threshold]
            
            if len(good_results) >= context.get("min_good_results", 1):
                self.think(
                    ThoughtType.CONCLUSION,
                    f"Found {len(good_results)} good results, completing research"
                )
                break
            
            # Check if all actions are complete
            pending_actions = [a for a in self.actions if a.result is None and a.error is None]
            if not pending_actions:
                self.think(
                    ThoughtType.REASONING,
                    "All planned actions complete, evaluating if more needed"
                )
                
                # If we don't have good results, we might need to stop
                if not good_results:
                    self.think(
                        ThoughtType.CONCLUSION,
                        "Unable to find good results after all attempts"
                    )
                    break
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "query": query,
            "thoughts": [{"type": t.type.value, "content": t.content} for t in self.thoughts],
            "actions": [{"type": a.type.value, "success": a.error is None} for a in self.actions],
            "observations": [{"content": o.content, "quality": o.quality_score} for o in self.observations],
            "results": results,
            "iterations": iteration,
            "duration_seconds": duration,
            "success": len(good_results) > 0
        }
    
    def _get_fallback_sources(self, current_sources: List[str]) -> List[str]:
        """Get fallback sources not yet tried"""
        all_sources = self.config.get("fallback_chain", ["brave", "duckduckgo", "google"])
        return [s for s in all_sources if s not in current_sources]