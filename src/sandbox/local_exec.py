"""
Local subprocess-based sandbox execution.

Provides code execution in isolated subprocess with timeout and output limits.
"""

import asyncio
import tempfile
import os
import time
from pathlib import Path
from typing import Optional

from .base import CodeSandbox, ExecutionResult
from src.config import settings


class LocalSandbox(CodeSandbox):
    """
    Local sandbox that executes code in a subprocess.
    
    Features:
    - Timeout enforcement
    - Output size limits
    - Working directory isolation
    - Resource cleanup
    """
    
    def __init__(self):
        self.timeout = settings.SANDBOX_TIMEOUT_SEC
        self.max_output_kb = settings.SANDBOX_MAX_OUTPUT_KB
        self.temp_dirs = []
    
    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code in a subprocess.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout (defaults to settings)
            working_dir: Working directory (creates temp dir if not provided)
            
        Returns:
            ExecutionResult with output and status
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        
        # Create temporary working directory if not provided
        if not working_dir:
            temp_dir = tempfile.mkdtemp(prefix="sandbox_")
            self.temp_dirs.append(temp_dir)
            working_dir = temp_dir
        
        # Determine command based on language
        if language == "python":
            command = ["python", "-c", code]
        elif language == "javascript" or language == "node":
            command = ["node", "-e", code]
        elif language == "bash" or language == "sh":
            command = ["bash", "-c", code]
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported language: {language}"
            )
        
        try:
            # Execute the code
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                # Limit environment variables for security
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": working_dir,
                    "USER": "sandbox"
                }
            )
            
            # Wait for completion with timeout
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
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
                    metadata={"timeout": True}
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
                    "working_dir": working_dir
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=False,
                error=f"Execution failed: {str(e)}",
                execution_time=execution_time,
                metadata={"exception": str(e)}
            )
    
    async def cleanup(self):
        """Clean up temporary directories."""
        import shutil
        
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Failed to clean up {temp_dir}: {e}")
        
        self.temp_dirs.clear()
    
    def is_available(self) -> bool:
        """Check if local sandbox is available (always true for local)."""
        return True
