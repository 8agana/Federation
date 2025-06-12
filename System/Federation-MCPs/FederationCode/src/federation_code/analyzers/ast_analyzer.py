"""AST-based code analyzer."""

import ast
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, AsyncGenerator
import aiofiles

from federation_code.analyzers.base import BaseAnalyzer, AnalysisResult, Issue, Severity, Aspect


class ASTAnalyzer(BaseAnalyzer):
    """AST-based code analysis."""
    
    def __init__(self):
        super().__init__()
        self.parser_cache = {}
        
    def can_stream(self) -> bool:
        """AST analyzer supports streaming for multiple files."""
        return True
        
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Perform AST analysis."""
        start_time = time.time()
        
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        aspect = Aspect(data.get('aspect', 'all'))
        
        issues = []
        files_analyzed = 0
        
        for file_path in files:
            try:
                file_issues = await self._analyze_file(file_path, mode, aspect)
                issues.extend(file_issues)
                files_analyzed += 1
            except Exception as e:
                # Create an error issue for failed files
                issues.append(Issue(
                    id=f"parse_error_{files_analyzed}",
                    file=str(file_path),
                    line=1,
                    column=1,
                    severity=Severity.ERROR,
                    aspect=Aspect.BUGS,
                    type="parse_error",
                    message=f"Failed to parse file: {e}",
                    description=f"Unable to analyze {file_path}: {str(e)}"
                ))
                
        execution_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(issues)
        
        return AnalysisResult(
            summary=summary,
            issues=issues,
            execution_time=execution_time,
            files_analyzed=files_analyzed
        )
        
    async def analyze_stream(self, data: Dict[str, Any]) -> AsyncGenerator[AnalysisResult, None]:
        """Stream analysis results file by file."""
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        aspect = Aspect(data.get('aspect', 'all'))
        
        all_issues = []
        files_analyzed = 0
        start_time = time.time()
        
        for i, file_path in enumerate(files):
            try:
                file_issues = await self._analyze_file(file_path, mode, aspect)
                all_issues.extend(file_issues)
                files_analyzed += 1
                
                # Yield partial result
                progress = (i + 1) / len(files)
                partial_summary = self._generate_summary(file_issues)
                
                yield AnalysisResult(
                    summary=partial_summary,
                    issues=file_issues,
                    execution_time=time.time() - start_time,
                    files_analyzed=1,
                    partial=True,
                    progress=progress
                )
                
                # Allow other tasks to run
                await asyncio.sleep(0)
                
            except Exception as e:
                # Yield error for this file
                error_issue = Issue(
                    id=f"parse_error_{files_analyzed}",
                    file=str(file_path),
                    line=1,
                    column=1,
                    severity=Severity.ERROR,
                    aspect=Aspect.BUGS,
                    type="parse_error",
                    message=f"Failed to parse file: {e}",
                    description=f"Unable to analyze {file_path}: {str(e)}"
                )
                
                yield AnalysisResult(
                    summary={"total_issues": 1, "by_severity": {"error": 1}},
                    issues=[error_issue],
                    execution_time=time.time() - start_time,
                    files_analyzed=1,
                    partial=True,
                    progress=(i + 1) / len(files)
                )
                
        # Final summary
        final_summary = self._generate_summary(all_issues)
        yield AnalysisResult(
            summary=final_summary,
            issues=all_issues,
            execution_time=time.time() - start_time,
            files_analyzed=files_analyzed,
            partial=False,
            progress=1.0
        )
        
    async def _analyze_file(self, file_path: Path, mode: str, aspect: Aspect) -> List[Issue]:
        """Analyze a single file."""
        if not file_path.exists():
            return [Issue(
                id=f"file_not_found_{file_path.name}",
                file=str(file_path),
                line=1,
                column=1,
                severity=Severity.ERROR,
                aspect=Aspect.BUGS,
                type="file_not_found",
                message=f"File not found: {file_path}",
                description=f"The file {file_path} does not exist"
            )]
            
        # Only analyze Python files for now
        if file_path.suffix != '.py':
            return []
            
        try:
            # Read file content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Analyze based on mode
            if mode == 'quick':
                return await self._quick_analysis(tree, file_path, content)
            elif mode == 'deep':
                return await self._deep_analysis(tree, file_path, content, aspect)
            else:  # standard
                return await self._standard_analysis(tree, file_path, content, aspect)
                
        except SyntaxError as e:
            return [Issue(
                id=f"syntax_error_{file_path.name}_{e.lineno}",
                file=str(file_path),
                line=e.lineno or 1,
                column=e.offset or 1,
                severity=Severity.ERROR,
                aspect=Aspect.BUGS,
                type="syntax_error",
                message=f"Syntax error: {e.msg}",
                description=f"Python syntax error in {file_path}: {e.msg}"
            )]
            
    async def _quick_analysis(self, tree: ast.AST, file_path: Path, content: str) -> List[Issue]:
        """Quick analysis - basic syntax and obvious issues."""
        issues = []
        
        class QuickVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for functions without docstrings
                if (not ast.get_docstring(node) and 
                    not node.name.startswith('_') and 
                    len(node.body) > 3):
                    issues.append(Issue(
                        id=f"missing_docstring_{node.name}_{node.lineno}",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.WARNING,
                        aspect=Aspect.STYLE,
                        type="missing_docstring",
                        message=f"Function '{node.name}' missing docstring",
                        description=f"Public function '{node.name}' should have a docstring",
                        suggestion="Add a docstring describing the function's purpose"
                    ))
                    
                self.generic_visit(node)
                
            def visit_Import(self, node):
                # Check for unused imports (basic check)
                for alias in node.names:
                    import_name = alias.asname or alias.name
                    if import_name not in content:
                        issues.append(Issue(
                            id=f"unused_import_{import_name}_{node.lineno}",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            severity=Severity.INFO,
                            aspect=Aspect.STYLE,
                            type="unused_import",
                            message=f"Unused import: {alias.name}",
                            description=f"Import '{alias.name}' appears to be unused",
                            suggestion="Remove unused import",
                            fix_available=True
                        ))
                        
                self.generic_visit(node)
                
        visitor = QuickVisitor()
        visitor.visit(tree)
        
        return issues
        
    async def _standard_analysis(self, tree: ast.AST, file_path: Path, content: str, aspect: Aspect) -> List[Issue]:
        """Standard analysis - comprehensive but not exhaustive."""
        issues = []
        
        # Include quick analysis
        issues.extend(await self._quick_analysis(tree, file_path, content))
        
        class StandardVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check function complexity
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(Issue(
                        id=f"high_complexity_{node.name}_{node.lineno}",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.WARNING,
                        aspect=Aspect.PERFORMANCE,
                        type="high_complexity",
                        message=f"Function '{node.name}' has high complexity ({complexity})",
                        description=f"Function complexity of {complexity} exceeds recommended limit of 10",
                        suggestion="Consider breaking down into smaller functions"
                    ))
                    
                # Check for long parameter lists
                if len(node.args.args) > 5:
                    issues.append(Issue(
                        id=f"too_many_params_{node.name}_{node.lineno}",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.INFO,
                        aspect=Aspect.STYLE,
                        type="too_many_parameters",
                        message=f"Function '{node.name}' has {len(node.args.args)} parameters",
                        description="Functions with many parameters are harder to test and maintain",
                        suggestion="Consider using a configuration object or dataclass"
                    ))
                    
                self.generic_visit(node)
                
            def _calculate_complexity(self, node):
                """Calculate cyclomatic complexity."""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                        complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                    elif isinstance(child, (ast.And, ast.Or)):
                        complexity += 1
                        
                return complexity
                
        visitor = StandardVisitor()
        visitor.visit(tree)
        
        return issues
        
    async def _deep_analysis(self, tree: ast.AST, file_path: Path, content: str, aspect: Aspect) -> List[Issue]:
        """Deep analysis - exhaustive checking."""
        issues = []
        
        # Include standard analysis
        issues.extend(await self._standard_analysis(tree, file_path, content, aspect))
        
        # Add deep analysis specific checks
        class DeepVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Check for potential security issues
                if (isinstance(node.func, ast.Name) and 
                    node.func.id in ['eval', 'exec', 'compile']):
                    issues.append(Issue(
                        id=f"dangerous_call_{node.func.id}_{node.lineno}",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.CRITICAL,
                        aspect=Aspect.SECURITY,
                        type="dangerous_function",
                        message=f"Dangerous function call: {node.func.id}",
                        description=f"Use of {node.func.id} can lead to code injection vulnerabilities",
                        suggestion="Avoid using eval/exec or sanitize input thoroughly"
                    ))
                    
                self.generic_visit(node)
                
            def visit_Str(self, node):
                # Check for hardcoded secrets (basic patterns)
                text = node.s.lower()
                if any(keyword in text for keyword in ['password', 'secret', 'token', 'key']):
                    if '=' in text or ':' in text:
                        issues.append(Issue(
                            id=f"potential_secret_{node.lineno}",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            severity=Severity.WARNING,
                            aspect=Aspect.SECURITY,
                            type="potential_hardcoded_secret",
                            message="Potential hardcoded secret detected",
                            description="String contains keywords suggesting it might be a secret",
                            suggestion="Use environment variables or secure configuration"
                        ))
                        
                self.generic_visit(node)
                
        visitor = DeepVisitor()
        visitor.visit(tree)
        
        return issues
        
    def _resolve_files(self, files_input: Any) -> List[Path]:
        """Resolve file patterns to actual file paths."""
        files = []
        
        if isinstance(files_input, str):
            files_input = [files_input]
            
        for pattern in files_input:
            path = Path(pattern)
            
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                # Get all Python files in directory
                files.extend(path.rglob('*.py'))
            else:
                # Try glob pattern
                files.extend(Path('.').glob(pattern))
                
        return list(set(files))  # Remove duplicates
        
    def _generate_summary(self, issues: List[Issue]) -> Dict[str, Any]:
        """Generate analysis summary."""
        summary = {
            "total_issues": len(issues),
            "by_severity": {
                "critical": 0,
                "error": 0,
                "warning": 0,
                "info": 0
            },
            "by_aspect": {
                "bugs": 0,
                "security": 0,
                "performance": 0,
                "style": 0
            }
        }
        
        for issue in issues:
            summary["by_severity"][issue.severity.value] += 1
            summary["by_aspect"][issue.aspect.value] += 1
            
        return summary
        
    def supports_aspect(self, aspect: Aspect) -> bool:
        """AST analyzer supports all aspects."""
        return True
        
    def estimate_time(self, data: Dict[str, Any]) -> float:
        """Estimate analysis time based on files."""
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        
        # Base time per file
        time_per_file = {
            'quick': 0.1,
            'standard': 0.5,
            'deep': 2.0
        }
        
        return len(files) * time_per_file.get(mode, 0.5)