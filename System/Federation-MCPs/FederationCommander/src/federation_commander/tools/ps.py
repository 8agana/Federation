"""
Process management tool
Replaces: list_processes, kill_process
"""

import psutil
import asyncio
import signal
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseTool

class ProcessTool(BaseTool):
    """Smart process management with Federation awareness"""
    
    @property
    def description(self) -> str:
        return """Manage system processes with Federation context.
        
        Examples:
        - ps() - List all processes
        - ps("python") - Find Python processes
        - ps("federation") - Find Federation-related processes
        - ps(kill=1234) - Kill process by PID
        - ps(port=8080) - Find process using port
        
        Features:
        - Smart filtering and search
        - Federation process detection
        - Port usage detection
        - Safe termination
        - Resource usage info
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Process name or pattern to search"
                },
                "kill": {
                    "type": "integer",
                    "description": "PID to kill"
                },
                "port": {
                    "type": "integer",
                    "description": "Find processes using this port"
                },
                "user": {
                    "type": "string",
                    "description": "Filter by username"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["cpu", "memory", "pid", "name"],
                    "default": "cpu",
                    "description": "Sort results by"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum results to show"
                },
                "tree": {
                    "type": "boolean",
                    "default": False,
                    "description": "Show process tree"
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        # Handle kill request first
        if "kill" in arguments:
            return await self._kill_process(arguments["kill"])
        
        # Handle port search
        if "port" in arguments:
            return await self._find_by_port(arguments["port"])
        
        # List processes
        query = arguments.get("query")
        user = arguments.get("user")
        sort_by = arguments.get("sort_by", "cpu")
        limit = arguments.get("limit", 20)
        tree = arguments.get("tree", False)
        
        return await self._list_processes(query, user, sort_by, limit, tree)
    
    async def _list_processes(
        self, 
        query: Optional[str], 
        user: Optional[str],
        sort_by: str,
        limit: int,
        tree: bool
    ) -> Dict[str, Any]:
        """List processes with filtering"""
        processes = []
        federation_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    info = proc.info
                    
                    # Filter by user
                    if user and info['username'] != user:
                        continue
                    
                    # Get additional info
                    process_data = {
                        "pid": info['pid'],
                        "name": info['name'],
                        "user": info['username'],
                        "cpu": round(info['cpu_percent'] or 0, 1),
                        "memory": round(info['memory_percent'] or 0, 1),
                        "created": datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Try to get command line
                    try:
                        cmdline = proc.cmdline()
                        process_data["command"] = ' '.join(cmdline) if cmdline else info['name']
                        
                        # Check if Federation-related
                        if any('federation' in arg.lower() for arg in cmdline):
                            process_data["federation"] = True
                            federation_processes.append(process_data)
                    except:
                        process_data["command"] = info['name']
                    
                    # Filter by query
                    if query:
                        query_lower = query.lower()
                        if not any(query_lower in str(v).lower() for v in process_data.values()):
                            continue
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu'], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory'], reverse=True)
            elif sort_by == "pid":
                processes.sort(key=lambda x: x['pid'])
            elif sort_by == "name":
                processes.sort(key=lambda x: x['name'].lower())
            
            # Limit results
            limited_processes = processes[:limit]
            
            result = {
                "status": "success",
                "total_found": len(processes),
                "showing": len(limited_processes),
                "processes": limited_processes
            }
            
            # Add Federation summary if any found
            if federation_processes:
                result["federation_processes"] = {
                    "count": len(federation_processes),
                    "pids": [p['pid'] for p in federation_processes],
                    "details": federation_processes[:5]  # Show first 5
                }
            
            # Add system summary
            result["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "total_processes": len(list(psutil.process_iter()))
            }
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            
            # Get process info before killing
            try:
                name = process.name()
                cmdline = ' '.join(process.cmdline())
            except:
                name = "Unknown"
                cmdline = "Unknown"
            
            # Check if it's a critical process
            critical_names = ["kernel", "init", "systemd", "launchd", "loginwindow"]
            if any(crit in name.lower() for crit in critical_names):
                return {
                    "status": "error",
                    "error": f"Cannot kill critical system process: {name}"
                }
            
            # Try graceful termination first
            process.terminate()
            
            # Wait up to 5 seconds for graceful termination
            try:
                process.wait(timeout=5)
                method = "terminated"
            except psutil.TimeoutExpired:
                # Force kill if still running
                process.kill()
                method = "killed"
            
            return {
                "status": "success",
                "message": f"Process {pid} ({name}) {method} successfully",
                "process": {
                    "pid": pid,
                    "name": name,
                    "command": cmdline,
                    "method": method
                }
            }
            
        except psutil.NoSuchProcess:
            return {"status": "error", "error": f"No process found with PID {pid}"}
        except psutil.AccessDenied:
            return {"status": "error", "error": f"Access denied to kill process {pid}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _find_by_port(self, port: int) -> Dict[str, Any]:
        """Find processes using a specific port"""
        processes_on_port = []
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == port:
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_info = {
                                "pid": conn.pid,
                                "name": proc.name(),
                                "user": proc.username(),
                                "status": conn.status,
                                "type": conn.type.name,
                                "family": conn.family.name
                            }
                            
                            # Get command if possible
                            try:
                                process_info["command"] = ' '.join(proc.cmdline())
                            except:
                                process_info["command"] = proc.name()
                            
                            processes_on_port.append(process_info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            processes_on_port.append({
                                "pid": conn.pid,
                                "status": conn.status,
                                "error": "Cannot access process info"
                            })
            
            if processes_on_port:
                return {
                    "status": "success",
                    "port": port,
                    "processes": processes_on_port,
                    "message": f"Found {len(processes_on_port)} process(es) using port {port}"
                }
            else:
                return {
                    "status": "success",
                    "port": port,
                    "processes": [],
                    "message": f"No processes found using port {port}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_federation_info(self, process: psutil.Process) -> Optional[Dict[str, Any]]:
        """Get Federation-specific information about a process"""
        try:
            cmdline = process.cmdline()
            cwd = process.cwd()
            
            federation_info = {}
            
            # Check if running from Federation directory
            if "/Federation/" in cwd:
                federation_info["working_directory"] = cwd
                
                # Identify component
                if "System" in cwd:
                    federation_info["component"] = "system"
                elif "Apps" in cwd:
                    federation_info["component"] = "apps"
                elif "Launcher" in cwd:
                    federation_info["component"] = "launcher"
            
            # Check command line for Federation references
            for arg in cmdline:
                if "federation" in arg.lower():
                    if "component" not in federation_info:
                        federation_info["component"] = "unknown"
                    
                    # Try to identify specific services
                    if "rag" in arg.lower():
                        federation_info["service"] = "rag"
                    elif "chromadb" in arg.lower():
                        federation_info["service"] = "chromadb"
                    elif "mcp" in arg.lower():
                        federation_info["service"] = "mcp"
            
            return federation_info if federation_info else None
            
        except:
            return None