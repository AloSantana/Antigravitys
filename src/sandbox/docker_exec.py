"""
Docker-based sandbox execution.

Provides code execution in isolated Docker containers with enhanced security.
"""

import asyncio
import time
import json
from typing import Optional

from .base import CodeSandbox, ExecutionResult
from src.config import settings


class DockerSandbox(CodeSandbox):
    """
    Docker-based sandbox for secure code execution.
    
    Features:
    - Container isolation
    - Network controls
    - CPU and memory limits
    - Dropped capabilities
    - Read-only file system (where possible)
    """
    
    def __init__(self):
        self.image = settings.DOCKER_IMAGE
        self.timeout = settings.SANDBOX_TIMEOUT_SEC
        self.max_output_kb = settings.SANDBOX_MAX_OUTPUT_KB
        self.network_enabled = settings.DOCKER_NETWORK_ENABLED
        self.cpu_limit = settings.DOCKER_CPU_LIMIT
        self.memory_limit = settings.DOCKER_MEMORY_LIMIT
        self._docker_available = None
    
    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code in a Docker container.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout (defaults to settings)
            working_dir: Working directory (unused for Docker)
            
        Returns:
            ExecutionResult with output and status
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                error="Docker is not available or image is not built"
            )
        
        timeout = timeout or self.timeout
        start_time = time.time()
        
        # Determine command based on language
        if language == "python":
            cmd = ["python", "-c", code]
        elif language == "javascript" or language == "node":
            cmd = ["node", "-e", code]
        elif language == "bash" or language == "sh":
            cmd = ["bash", "-c", code]
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported language: {language}"
            )
        
        # Build docker run command
        docker_cmd = [
            "docker", "run",
            "--rm",  # Remove container after execution
            "--network", "none" if not self.network_enabled else "bridge",
            "--cpus", self.cpu_limit,
            "--memory", self.memory_limit,
            "--cap-drop", "ALL",  # Drop all capabilities
            "--security-opt", "no-new-privileges",  # Prevent privilege escalation
            "--read-only",  # Read-only root filesystem
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=100m",  # Writable /tmp
            self.image
        ]
        docker_cmd.extend(cmd)
        
        try:
            # Execute in Docker container
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill the container if it times out
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                
                execution_time = time.time() - start_time
                
                return ExecutionResult(
                    success=False,
                    error=f"Execution timed out after {timeout} seconds",
                    execution_time=execution_time,
                    metadata={"timeout": True, "sandbox": "docker"}
                )
            
            # Decode output
            stdout = stdout_data.decode('utf-8', errors='replace')
            stderr = stderr_data.decode('utf-8', errors='replace')
            
            # Truncate output if too large
            max_bytes = self.max_output_kb * 1024
            truncated = False
            
            if len(stdout) > max_bytes:
                stdout = stdout[:max_bytes] + f"\n... (truncated, {len(stdout)} bytes total)"
                truncated = True
            
            if len(stderr) > max_bytes:
                stderr = stderr[:max_bytes] + f"\n... (truncated, {len(stderr)} bytes total)"
                truncated = True
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=(process.returncode == 0),
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode or 0,
                execution_time=execution_time,
                truncated=truncated,
                metadata={
                    "language": language,
                    "sandbox": "docker",
                    "image": self.image
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=False,
                error=f"Execution failed: {str(e)}",
                execution_time=execution_time,
                metadata={
                    "exception": str(e),
                    "sandbox": "docker"
                }
            )
    
    async def cleanup(self):
        """Clean up Docker resources (containers are auto-removed with --rm)."""
        # Containers are automatically removed with --rm flag
        pass
    
    def is_available(self) -> bool:
        """Check if Docker is available and the image exists."""
        if self._docker_available is not None:
            return self._docker_available
        
        try:
            # Check if docker command exists
            import subprocess
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                self._docker_available = False
                return False
            
            # Check if image exists
            result = subprocess.run(
                ["docker", "images", "-q", self.image],
                capture_output=True,
                timeout=5
            )
            
            self._docker_available = bool(result.stdout.strip())
            return self._docker_available
            
        except Exception:
            self._docker_available = False
            return False
