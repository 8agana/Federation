"""Security-focused code analyzer."""

import re
import ast
import time
from pathlib import Path
from typing import Dict, Any, List, AsyncGenerator, Pattern
import aiofiles

from federation_code.analyzers.base import BaseAnalyzer, AnalysisResult, Issue, Severity, Aspect


class SecurityAnalyzer(BaseAnalyzer):
    """Security vulnerability analyzer."""
    
    def __init__(self):
        super().__init__()
        self.vulnerability_patterns = self._load_patterns()
        
    def can_stream(self) -> bool:
        """Security analyzer supports streaming."""
        return True
        
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Perform security analysis."""
        start_time = time.time()
        
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        
        issues = []
        files_analyzed = 0
        
        for file_path in files:
            try:
                file_issues = await self._analyze_file(file_path, mode)
                issues.extend(file_issues)
                files_analyzed += 1
            except Exception as e:
                # Create error issue
                issues.append(Issue(
                    id=f"security_scan_error_{files_analyzed}",
                    file=str(file_path),
                    line=1,
                    column=1,
                    severity=Severity.ERROR,
                    aspect=Aspect.SECURITY,
                    type="scan_error",
                    message=f"Security scan failed: {e}",
                    description=f"Unable to scan {file_path} for security issues"
                ))
                
        execution_time = time.time() - start_time
        summary = self._generate_summary(issues)
        
        return AnalysisResult(
            summary=summary,
            issues=issues,
            execution_time=execution_time,
            files_analyzed=files_analyzed
        )
        
    async def analyze_stream(self, data: Dict[str, Any]) -> AsyncGenerator[AnalysisResult, None]:
        """Stream security analysis results."""
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        
        all_issues = []
        files_analyzed = 0
        start_time = time.time()
        
        for i, file_path in enumerate(files):
            try:
                file_issues = await self._analyze_file(file_path, mode)
                all_issues.extend(file_issues)
                files_analyzed += 1
                
                # Stream critical issues immediately
                critical_issues = [
                    issue for issue in file_issues 
                    if issue.severity == Severity.CRITICAL
                ]
                
                if critical_issues:
                    yield AnalysisResult(
                        summary={"critical_issues": len(critical_issues)},
                        issues=critical_issues,
                        execution_time=time.time() - start_time,
                        files_analyzed=1,
                        partial=True,
                        progress=(i + 1) / len(files)
                    )
                    
            except Exception as e:
                # Stream error
                error_issue = Issue(
                    id=f"security_scan_error_{files_analyzed}",
                    file=str(file_path),
                    line=1,
                    column=1,
                    severity=Severity.ERROR,
                    aspect=Aspect.SECURITY,
                    type="scan_error",
                    message=f"Security scan failed: {e}",
                    description=f"Unable to scan {file_path} for security issues"
                )
                
                yield AnalysisResult(
                    summary={"scan_errors": 1},
                    issues=[error_issue],
                    execution_time=time.time() - start_time,
                    files_analyzed=1,
                    partial=True,
                    progress=(i + 1) / len(files)
                )
                
        # Final result
        final_summary = self._generate_summary(all_issues)
        yield AnalysisResult(
            summary=final_summary,
            issues=all_issues,
            execution_time=time.time() - start_time,
            files_analyzed=files_analyzed,
            partial=False,
            progress=1.0
        )
        
    async def _analyze_file(self, file_path: Path, mode: str) -> List[Issue]:
        """Analyze a file for security vulnerabilities."""
        if not file_path.exists():
            return []
            
        issues = []
        
        try:
            # Read file content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            # Pattern-based analysis
            issues.extend(await self._pattern_analysis(file_path, content))
            
            # AST-based analysis for Python files
            if file_path.suffix == '.py':
                issues.extend(await self._ast_security_analysis(file_path, content))
                
            # Deep analysis if requested
            if mode == 'deep':
                issues.extend(await self._deep_security_analysis(file_path, content))
                
        except Exception:
            # Skip files that can't be read
            pass
            
        return issues
        
    async def _pattern_analysis(self, file_path: Path, content: str) -> List[Issue]:
        """Pattern-based vulnerability detection."""
        issues = []
        lines = content.split('\n')
        
        for pattern_info in self.vulnerability_patterns:
            pattern = pattern_info['pattern']
            vuln_type = pattern_info['type']
            severity = pattern_info['severity']
            description = pattern_info['description']
            suggestion = pattern_info['suggestion']
            
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    issues.append(Issue(
                        id=f"{vuln_type}_{file_path.name}_{line_num}_{match.start()}",
                        file=str(file_path),
                        line=line_num,
                        column=match.start(),
                        end_column=match.end(),
                        severity=severity,
                        aspect=Aspect.SECURITY,
                        type=vuln_type,
                        message=f"Potential {vuln_type}: {match.group()}",
                        description=description,
                        suggestion=suggestion,
                        context=[line.strip()]
                    ))
                    
        return issues
        
    async def _ast_security_analysis(self, file_path: Path, content: str) -> List[Issue]:
        """AST-based security analysis for Python."""
        issues = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            
            class SecurityVisitor(ast.NodeVisitor):
                def visit_Call(self, node):
                    # Check for dangerous function calls
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        
                        if func_name in ['eval', 'exec', 'compile']:
                            issues.append(Issue(
                                id=f"dangerous_eval_{func_name}_{node.lineno}",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                severity=Severity.CRITICAL,
                                aspect=Aspect.SECURITY,
                                type="code_injection",
                                message=f"Dangerous use of {func_name}()",
                                description=f"Use of {func_name}() can lead to code injection vulnerabilities",
                                suggestion="Avoid dynamic code execution or sanitize input thoroughly"
                            ))
                            
                    # Check for subprocess with shell=True
                    elif isinstance(node.func, ast.Attribute):
                        if (hasattr(node.func.value, 'id') and 
                            node.func.value.id == 'subprocess' and
                            node.func.attr in ['run', 'call', 'Popen']):
                            
                            # Check for shell=True
                            for keyword in node.keywords:
                                if (keyword.arg == 'shell' and 
                                    isinstance(keyword.value, ast.Constant) and
                                    keyword.value.value is True):
                                    
                                    issues.append(Issue(
                                        id=f"shell_injection_{node.lineno}",
                                        file=str(file_path),
                                        line=node.lineno,
                                        column=node.col_offset,
                                        severity=Severity.HIGH,
                                        aspect=Aspect.SECURITY,
                                        type="shell_injection",
                                        message="subprocess call with shell=True",
                                        description="Using shell=True can lead to shell injection attacks",
                                        suggestion="Use shell=False and pass commands as list"
                                    ))
                                    
                    self.generic_visit(node)
                    
                def visit_Str(self, node):
                    # Check for SQL injection patterns
                    sql_patterns = [
                        r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*%s',
                        r'INSERT\s+INTO\s+.*\s+VALUES\s+.*%s',
                        r'UPDATE\s+.*\s+SET\s+.*%s',
                        r'DELETE\s+FROM\s+.*\s+WHERE\s+.*%s'
                    ]
                    
                    for pattern in sql_patterns:
                        if re.search(pattern, node.s, re.IGNORECASE):
                            issues.append(Issue(
                                id=f"sql_injection_{node.lineno}",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                severity=Severity.HIGH,
                                aspect=Aspect.SECURITY,
                                type="sql_injection",
                                message="Potential SQL injection vulnerability",
                                description="SQL query uses string formatting which can lead to injection",
                                suggestion="Use parameterized queries or ORM methods"
                            ))
                            break
                            
                    self.generic_visit(node)
                    
            visitor = SecurityVisitor()
            visitor.visit(tree)
            
        except SyntaxError:
            # Skip files with syntax errors
            pass
            
        return issues
        
    async def _deep_security_analysis(self, file_path: Path, content: str) -> List[Issue]:
        """Deep security analysis."""
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "hardcoded_password"),
            (r'secret\s*=\s*["\'][^"\']{16,}["\']', "hardcoded_secret"),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', "hardcoded_token"),
            (r'api_key\s*=\s*["\'][^"\']{16,}["\']', "hardcoded_api_key"),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, vuln_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        id=f"{vuln_type}_{line_num}",
                        file=str(file_path),
                        line=line_num,
                        column=1,
                        severity=Severity.HIGH,
                        aspect=Aspect.SECURITY,
                        type=vuln_type,
                        message=f"Potential {vuln_type.replace('_', ' ')} detected",
                        description="Hardcoded secrets should not be stored in source code",
                        suggestion="Use environment variables or secure configuration",
                        context=[line.strip()]
                    ))
                    
        return issues
        
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load vulnerability detection patterns."""
        return [
            {
                'pattern': re.compile(r'eval\s*\(', re.IGNORECASE),
                'type': 'code_injection',
                'severity': Severity.CRITICAL,
                'description': 'Use of eval() function can lead to code injection',
                'suggestion': 'Avoid eval() or sanitize input thoroughly'
            },
            {
                'pattern': re.compile(r'exec\s*\(', re.IGNORECASE),
                'type': 'code_injection', 
                'severity': Severity.CRITICAL,
                'description': 'Use of exec() function can lead to code injection',
                'suggestion': 'Avoid exec() or sanitize input thoroughly'
            },
            {
                'pattern': re.compile(r'shell=True', re.IGNORECASE),
                'type': 'shell_injection',
                'severity': Severity.HIGH,
                'description': 'subprocess with shell=True can lead to shell injection',
                'suggestion': 'Use shell=False and pass commands as list'
            },
            {
                'pattern': re.compile(r'pickle\.loads?\s*\(', re.IGNORECASE),
                'type': 'deserialization',
                'severity': Severity.HIGH,
                'description': 'Pickle deserialization can execute arbitrary code',
                'suggestion': 'Use safe serialization formats like JSON'
            },
            {
                'pattern': re.compile(r'input\s*\([^)]*\)', re.IGNORECASE),
                'type': 'user_input',
                'severity': Severity.WARNING,
                'description': 'Unvalidated user input can be dangerous',
                'suggestion': 'Validate and sanitize all user input'
            }
        ]
        
    def _resolve_files(self, files_input: Any) -> List[Path]:
        """Resolve file patterns to actual paths."""
        files = []
        
        if isinstance(files_input, str):
            files_input = [files_input]
            
        for pattern in files_input:
            path = Path(pattern)
            
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                # Get common source files
                for ext in ['*.py', '*.js', '*.ts', '*.java', '*.php', '*.rb']:
                    files.extend(path.rglob(ext))
            else:
                files.extend(Path('.').glob(pattern))
                
        return list(set(files))
        
    def _generate_summary(self, issues: List[Issue]) -> Dict[str, Any]:
        """Generate security analysis summary."""
        summary = {
            "total_vulnerabilities": len(issues),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "warning": 0,
                "info": 0
            },
            "by_type": {}
        }
        
        for issue in issues:
            severity = issue.severity.value
            if severity == "error":
                severity = "high"  # Map error to high for security
                
            summary["by_severity"][severity] += 1
            
            vuln_type = issue.type
            summary["by_type"][vuln_type] = summary["by_type"].get(vuln_type, 0) + 1
            
        return summary
        
    def supports_aspect(self, aspect: Aspect) -> bool:
        """Security analyzer only supports security aspect."""
        return aspect in (Aspect.SECURITY, Aspect.ALL)
        
    def estimate_time(self, data: Dict[str, Any]) -> float:
        """Estimate security scan time."""
        files = self._resolve_files(data.get('files', []))
        mode = data.get('mode', 'standard')
        
        time_per_file = {
            'quick': 0.2,
            'standard': 1.0,
            'deep': 3.0
        }
        
        return len(files) * time_per_file.get(mode, 1.0)