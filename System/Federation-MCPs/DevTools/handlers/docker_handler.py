"""
Docker Handler for DevTools MCP
Manages Docker operations using docker-py library
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import docker
    from docker.errors import DockerException, APIError, NotFound
except ImportError:
    raise ImportError("docker package not installed. Install with: pip install docker")

logger = logging.getLogger("devtools.docker")


class DockerHandler:
    """Handle Docker operations"""
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            self.available = True
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            logger.warning(f"Docker not available: {e}")
            self.client = None
            self.available = False
        except Exception as e:
            logger.warning(f"Docker connection failed: {e}")
            self.client = None
            self.available = False
    
    def _check_availability(self) -> Optional[str]:
        """Check if Docker is available, return error message if not"""
        if not self.available:
            return json.dumps({"error": "Docker not available - Docker Desktop may not be running"})
        return None
    
    async def list_containers(self, all: bool = False) -> str:
        """List Docker containers"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            containers = await asyncio.to_thread(self.client.containers.list, all=all)
            
            result = []
            for container in containers:
                info = {
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "status": container.status,
                    "created": container.attrs['Created'],
                    "ports": container.ports,
                }
                result.append(info)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return f"Error listing containers: {str(e)}"
    
    async def create_container(self, params: Dict[str, Any]) -> str:
        """Create and start a new container"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            # Extract parameters
            image = params["image"]
            name = params.get("name")
            ports = params.get("ports", {})
            environment = params.get("environment", {})
            volumes = params.get("volumes", [])
            command = params.get("command")
            
            # Convert volumes from list to dict format
            volume_dict = {}
            for vol in volumes:
                if ":" in vol:
                    host, container = vol.split(":", 1)
                    volume_dict[host] = {"bind": container, "mode": "rw"}
            
            # Create container
            container = await asyncio.to_thread(
                self.client.containers.run,
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volume_dict,
                command=command,
                detach=True,
                remove=False
            )
            
            # Get container info
            container.reload()
            
            result = {
                "id": container.short_id,
                "name": container.name,
                "status": "created",
                "message": f"Container {container.name} created and started successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except APIError as e:
            logger.error(f"Docker API error: {e}")
            return f"Docker API error: {str(e)}"
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            return f"Error creating container: {str(e)}"
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> str:
        """Stop a running container"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            container = await asyncio.to_thread(self.client.containers.get, container_id)
            await asyncio.to_thread(container.stop, timeout=timeout)
            
            return json.dumps({
                "status": "stopped",
                "message": f"Container {container.name} stopped successfully"
            }, indent=2)
            
        except NotFound:
            return f"Container {container_id} not found"
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return f"Error stopping container: {str(e)}"
    
    async def remove_container(self, container_id: str, force: bool = False) -> str:
        """Remove a container"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            container = await asyncio.to_thread(self.client.containers.get, container_id)
            await asyncio.to_thread(container.remove, force=force)
            
            return json.dumps({
                "status": "removed",
                "message": f"Container {container.name} removed successfully"
            }, indent=2)
            
        except NotFound:
            return f"Container {container_id} not found"
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return f"Error removing container: {str(e)}"
    
    async def get_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> str:
        """Get container logs"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            container = await asyncio.to_thread(self.client.containers.get, container_id)
            
            if follow:
                # For follow mode, collect logs for up to 5 seconds
                logs = []
                start_time = asyncio.get_event_loop().time()
                
                async def collect_logs():
                    for line in container.logs(stream=True, tail=tail):
                        logs.append(line.decode('utf-8').strip())
                        if asyncio.get_event_loop().time() - start_time > 5:
                            break
                
                await asyncio.to_thread(collect_logs)
                return "\n".join(logs)
            else:
                # Get static logs
                log_bytes = await asyncio.to_thread(container.logs, tail=tail)
                return log_bytes.decode('utf-8')
                
        except NotFound:
            return f"Container {container_id} not found"
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return f"Error getting logs: {str(e)}"
    
    async def exec_command(self, container_id: str, command: str, workdir: Optional[str] = None) -> str:
        """Execute command in container"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            container = await asyncio.to_thread(self.client.containers.get, container_id)
            
            # Execute command
            result = await asyncio.to_thread(
                container.exec_run,
                command,
                workdir=workdir,
                demux=True
            )
            
            exit_code = result.exit_code
            stdout = result.output[0].decode('utf-8') if result.output[0] else ""
            stderr = result.output[1].decode('utf-8') if result.output[1] else ""
            
            return json.dumps({
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": exit_code == 0
            }, indent=2)
            
        except NotFound:
            return f"Container {container_id} not found"
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
    
    async def list_images(self, filter_name: Optional[str] = None) -> str:
        """List Docker images"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            images = await asyncio.to_thread(self.client.images.list)
            
            result = []
            for image in images:
                # Skip if filter doesn't match
                if filter_name:
                    if not any(filter_name in tag for tag in image.tags):
                        continue
                
                info = {
                    "id": image.short_id,
                    "tags": image.tags,
                    "created": image.attrs['Created'],
                    "size": f"{image.attrs['Size'] / 1024 / 1024:.1f} MB"
                }
                result.append(info)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return f"Error listing images: {str(e)}"
    
    async def pull_image(self, image_name: str) -> str:
        """Pull Docker image"""
        error = self._check_availability()
        if error:
            return error
        
        try:
            # Pull image with progress
            logger.info(f"Pulling image: {image_name}")
            
            # This is a blocking operation, run in thread
            image = await asyncio.to_thread(self.client.images.pull, image_name)
            
            return json.dumps({
                "status": "success",
                "message": f"Successfully pulled {image_name}",
                "id": image.short_id,
                "tags": image.tags
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error pulling image: {e}")
            return f"Error pulling image: {str(e)}"