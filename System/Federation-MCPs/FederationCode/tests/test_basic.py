"""Basic tests for Federation Code MCP."""

import pytest
import asyncio
from pathlib import Path

from federation_code.core import AsyncEngine, Priority, Mode
from federation_code.analyzers.ast_analyzer import ASTAnalyzer
from federation_code.tools.analyze import AnalyzeTool


@pytest.fixture
async def engine():
    """Create test async engine."""
    engine = AsyncEngine(max_workers=2, max_processes=1)
    await engine.start()
    yield engine
    await engine.stop()


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "test_sample.py"
    content = '''
def unused_import_example():
    import os  # This import is unused
    return "hello"

def high_complexity_function(a, b, c, d, e, f):
    """Function with high complexity."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return f
    return 0

eval("print('dangerous')")  # Security issue
'''
    file_path.write_text(content)
    return file_path


class TestASTAnalyzer:
    """Test AST analyzer functionality."""
    
    @pytest.mark.asyncio
    async def test_quick_analysis(self, sample_python_file):
        """Test quick analysis mode."""
        analyzer = ASTAnalyzer()
        
        result = await analyzer.analyze({
            'files': [str(sample_python_file)],
            'mode': 'quick',
            'aspect': 'all'
        })
        
        assert result.files_analyzed == 1
        assert len(result.issues) > 0
        
        # Should find unused import
        unused_imports = [i for i in result.issues if i.type == 'unused_import']
        assert len(unused_imports) > 0
        
    @pytest.mark.asyncio 
    async def test_deep_analysis(self, sample_python_file):
        """Test deep analysis mode."""
        analyzer = ASTAnalyzer()
        
        result = await analyzer.analyze({
            'files': [str(sample_python_file)],
            'mode': 'deep',
            'aspect': 'all'
        })
        
        assert result.files_analyzed == 1
        assert len(result.issues) > 0
        
        # Should find security issues
        security_issues = [i for i in result.issues if i.aspect.value == 'security']
        assert len(security_issues) > 0
        
        # Should find dangerous eval call
        eval_issues = [i for i in result.issues if 'eval' in i.message.lower()]
        assert len(eval_issues) > 0
        
    @pytest.mark.asyncio
    async def test_streaming_analysis(self, sample_python_file):
        """Test streaming analysis."""
        analyzer = ASTAnalyzer()
        
        results = []
        async for result in analyzer.analyze_stream({
            'files': [str(sample_python_file)],
            'mode': 'standard',
            'aspect': 'all'
        }):
            results.append(result)
            
        assert len(results) >= 2  # At least partial + final
        
        # Last result should be final
        final_result = results[-1]
        assert not final_result.partial
        assert final_result.progress == 1.0


class TestAsyncEngine:
    """Test async engine functionality."""
    
    @pytest.mark.asyncio
    async def test_quick_task_submission(self, engine, sample_python_file):
        """Test quick task submission and execution."""
        task_id = engine.submit_task(
            task_type="analyze",
            data={
                'files': [str(sample_python_file)],
                'mode': 'quick',
                'aspect': 'all'
            },
            mode=Mode.QUICK
        )
        
        # Wait briefly for execution
        await asyncio.sleep(0.2)
        
        # Should be completed
        status = engine.get_task_status(task_id)
        assert status is not None
        
        # For quick mode, should complete quickly
        result = engine.get_task_result(task_id)
        if result:
            assert result.data is not None
            assert result.data.files_analyzed == 1
            
    @pytest.mark.asyncio
    async def test_async_task_submission(self, engine, sample_python_file):
        """Test async task submission."""
        task_id = engine.submit_task(
            task_type="analyze",
            data={
                'files': [str(sample_python_file)],
                'mode': 'standard',
                'aspect': 'all'
            },
            mode=Mode.STANDARD
        )
        
        # Should get a task ID
        assert task_id is not None
        assert task_id.startswith("analyze_")
        
        # Should be able to get status
        status = engine.get_task_status(task_id)
        assert status is not None
        assert status.task_id == task_id
        
    @pytest.mark.asyncio
    async def test_task_cancellation(self, engine):
        """Test task cancellation."""
        # Submit a long-running task
        task_id = engine.submit_task(
            task_type="analyze",
            data={
                'files': ['*.py'],  # Might take a while
                'mode': 'deep',
                'aspect': 'all'
            },
            mode=Mode.DEEP
        )
        
        # Cancel immediately
        cancelled = await engine.cancel_task(task_id)
        assert cancelled
        
        # Status should show cancelled
        status = engine.get_task_status(task_id)
        assert status.status.value == "cancelled"


class TestAnalyzeTool:
    """Test analyze tool functionality."""
    
    @pytest.mark.asyncio
    async def test_tool_execution_quick(self, engine, sample_python_file):
        """Test tool execution in quick mode."""
        tool = AnalyzeTool(engine)
        
        result = await tool.execute({
            "files": str(sample_python_file),
            "mode": "quick",
            "aspect": "all"
        })
        
        assert not result.isError
        assert len(result.content) > 0
        
        # Should contain JSON result
        import json
        content_text = result.content[0].text
        parsed = json.loads(content_text)
        
        assert "status" in parsed
        assert "summary" in parsed
        assert "issues" in parsed
        
    @pytest.mark.asyncio
    async def test_tool_execution_async(self, engine, sample_python_file):
        """Test tool execution in async mode."""
        tool = AnalyzeTool(engine)
        
        result = await tool.execute({
            "files": str(sample_python_file),
            "mode": "standard",
            "aspect": "all",
            "async": True
        })
        
        assert not result.isError
        
        # Should get handle
        import json
        content_text = result.content[0].text
        parsed = json.loads(content_text)
        
        assert "handle" in parsed
        assert "status" in parsed
        assert parsed["status"] == "started"
        
    def test_tool_validation(self, engine):
        """Test tool argument validation."""
        tool = AnalyzeTool(engine)
        
        # Missing required files parameter
        with pytest.raises(ValueError, match="'files' parameter is required"):
            tool.validate_arguments({})
            
        # Invalid aspect
        with pytest.raises(ValueError, match="Invalid aspect"):
            tool.validate_arguments({"files": "test.py", "aspect": "invalid"})
            
        # Invalid mode
        with pytest.raises(ValueError, match="Invalid mode"):
            tool.validate_arguments({"files": "test.py", "mode": "invalid"})


if __name__ == "__main__":
    pytest.main([__file__])