"""Async Engine Core - Non-blocking task execution system."""

import asyncio
import uuid
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from queue import PriorityQueue
from typing import Any, Dict, List, Optional, Union
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class Mode(Enum):
    """Execution modes."""
    QUICK = "quick"      # <1s operations
    STANDARD = "standard"  # 1-30s operations
    DEEP = "deep"        # >30s operations


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result container for tasks."""
    task_id: str
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    partial: bool = False
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def is_final(self) -> bool:
        """Check if this is a final result."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


@dataclass
class Task:
    """Base task definition."""
    task_id: str
    task_type: str
    priority: Priority
    mode: Mode
    data: Dict[str, Any]
    stream: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AsyncEngine:
    """Core async execution engine."""
    
    def __init__(self, max_workers: int = 4, max_processes: int = 2):
        self.max_workers = max_workers
        self.max_processes = max_processes
        
        # Execution pools
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        
        # Task management
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.result_streams: Dict[str, Queue] = {}
        self.priority_queue = PriorityQueue()
        
        # Synchronization
        self._lock = threading.RLock()
        self._shutdown = False
        
        # Background processor
        self._processor_task = None
        
    async def start(self):
        """Start the async engine."""
        logger.info("Starting AsyncEngine")
        self._processor_task = asyncio.create_task(self._process_queue())
        
    async def stop(self):
        """Stop the async engine and cleanup."""
        logger.info("Stopping AsyncEngine")
        self._shutdown = True
        
        # Cancel all active tasks
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id, force=True)
            
        # Stop background processor
        if self._processor_task:
            self._processor_task.cancel()
            
        # Shutdown executors
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
    def submit_task(
        self, 
        task_type: str,
        data: Dict[str, Any],
        priority: Priority = Priority.MEDIUM,
        mode: Mode = Mode.STANDARD,
        stream: bool = False
    ) -> str:
        """Submit a task for execution."""
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            mode=mode,
            data=data,
            stream=stream
        )
        
        # Initialize result
        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            start_time=datetime.now()
        )
        
        with self._lock:
            self.task_results[task_id] = result
            
            if stream:
                self.result_streams[task_id] = Queue()
        
        # For quick mode, execute immediately
        if mode == Mode.QUICK:
            asyncio.create_task(self._execute_task_immediate(task))
        else:
            # Queue for background processing
            self.priority_queue.put((priority.value, task.created_at, task))
            
        logger.info(f"Task {task_id} submitted with priority {priority.name}")
        return task_id
        
    async def _execute_task_immediate(self, task: Task):
        """Execute a task immediately (for quick mode)."""
        try:
            # Import here to avoid circular imports
            from federation_code.analyzers import get_analyzer
            
            analyzer = get_analyzer(task.task_type)
            if not analyzer:
                raise ValueError(f"No analyzer found for task type: {task.task_type}")
                
            # Update status
            result = self.task_results[task.task_id]
            result.status = TaskStatus.RUNNING
            
            # Execute
            data = await analyzer.analyze(task.data)
            
            # Complete
            result.status = TaskStatus.COMPLETED
            result.data = data
            result.end_time = datetime.now()
            result.progress = 1.0
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            result = self.task_results[task.task_id]
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            
    async def _process_queue(self):
        """Background task processor."""
        while not self._shutdown:
            try:
                # Check for queued tasks
                if not self.priority_queue.empty():
                    _, _, task = self.priority_queue.get()
                    await self._execute_task_background(task)
                else:
                    # Sleep briefly if no tasks
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(1)
                
    async def _execute_task_background(self, task: Task):
        """Execute a task in background."""
        try:
            # Create async task
            async_task = asyncio.create_task(self._run_task(task))
            
            with self._lock:
                self.active_tasks[task.task_id] = async_task
                
            await async_task
            
        except asyncio.CancelledError:
            logger.info(f"Task {task.task_id} was cancelled")
            result = self.task_results[task.task_id]
            result.status = TaskStatus.CANCELLED
            result.end_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Background task {task.task_id} failed: {e}")
            result = self.task_results[task.task_id]
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            
        finally:
            # Cleanup
            with self._lock:
                self.active_tasks.pop(task.task_id, None)
                
    async def _run_task(self, task: Task):
        """Run a single task."""
        from federation_code.analyzers import get_analyzer
        
        analyzer = get_analyzer(task.task_type)
        if not analyzer:
            raise ValueError(f"No analyzer found for task type: {task.task_type}")
            
        # Update status
        result = self.task_results[task.task_id]
        result.status = TaskStatus.RUNNING
        
        # Stream results if requested
        if task.stream:
            await self._run_streaming_task(task, analyzer)
        else:
            await self._run_standard_task(task, analyzer)
            
    async def _run_streaming_task(self, task: Task, analyzer):
        """Run a task with streaming results."""
        result = self.task_results[task.task_id]
        stream = self.result_streams[task.task_id]
        
        try:
            # Stream results as they come
            async for partial_result in analyzer.analyze_stream(task.data):
                # Update progress
                if hasattr(partial_result, 'progress'):
                    result.progress = partial_result.progress
                    
                # Send to stream
                await stream.put(partial_result)
                
            # Mark complete
            result.status = TaskStatus.COMPLETED
            result.end_time = datetime.now()
            result.progress = 1.0
            
            # Send final marker
            await stream.put(TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                partial=False,
                progress=1.0
            ))
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            
            # Send error to stream
            await stream.put(TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                partial=False
            ))
            
    async def _run_standard_task(self, task: Task, analyzer):
        """Run a standard (non-streaming) task."""
        result = self.task_results[task.task_id]
        
        try:
            # Execute analysis
            data = await analyzer.analyze(task.data)
            
            # Complete
            result.status = TaskStatus.COMPLETED
            result.data = data
            result.end_time = datetime.now()
            result.progress = 1.0
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get current status of a task."""
        with self._lock:
            return self.task_results.get(task_id)
            
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get final result of a completed task."""
        with self._lock:
            result = self.task_results.get(task_id)
            if result and result.is_final:
                return result
            return None
            
    async def get_partial_results(self, task_id: str) -> Optional[TaskResult]:
        """Get partial results if available."""
        with self._lock:
            result = self.task_results.get(task_id)
            if result and result.status == TaskStatus.RUNNING:
                return result
            return None
            
    async def stream_results(self, task_id: str):
        """Stream results for a streaming task."""
        if task_id not in self.result_streams:
            raise ValueError(f"No stream available for task {task_id}")
            
        stream = self.result_streams[task_id]
        
        while True:
            try:
                # Wait for next result
                result = await asyncio.wait_for(stream.get(), timeout=0.1)
                yield result
                
                # Stop if final result
                if result.is_final:
                    break
                    
            except asyncio.TimeoutError:
                # Check if task is still running
                task_result = self.get_task_status(task_id)
                if task_result and task_result.is_final:
                    break
                continue
                
    async def cancel_task(self, task_id: str, force: bool = False) -> bool:
        """Cancel a running task."""
        with self._lock:
            # Check if task exists
            if task_id not in self.task_results:
                return False
                
            result = self.task_results[task_id]
            
            # Can only cancel running or pending tasks
            if result.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
                return False
                
            # Cancel async task if running
            if task_id in self.active_tasks:
                async_task = self.active_tasks[task_id]
                async_task.cancel()
                
            # Update status
            result.status = TaskStatus.CANCELLED
            result.end_time = datetime.now()
            
            # Clean up stream
            if task_id in self.result_streams:
                stream = self.result_streams[task_id]
                await stream.put(TaskResult(
                    task_id=task_id,
                    status=TaskStatus.CANCELLED,
                    partial=False
                ))
                
            logger.info(f"Task {task_id} cancelled")
            return True
            
    def list_active_tasks(self) -> List[str]:
        """List all active task IDs."""
        with self._lock:
            return [
                task_id for task_id, result in self.task_results.items()
                if result.status in (TaskStatus.PENDING, TaskStatus.RUNNING)
            ]
            
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        with self._lock:
            stats = {
                "active_tasks": len(self.active_tasks),
                "total_tasks": len(self.task_results),
                "queued_tasks": self.priority_queue.qsize(),
                "thread_pool_size": self.max_workers,
                "process_pool_size": self.max_processes,
                "status_counts": {}
            }
            
            # Count by status
            for result in self.task_results.values():
                status = result.status.value
                stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1
                
            return stats