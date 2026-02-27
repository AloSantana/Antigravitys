"""
Code execution tool for agents.

Provides safe code execution via sandbox.
"""

import asyncio
from typing import Optional, Dict, Any

from src.sandbox import get_sandbox, ExecutionResult


async def run_python_code(
    code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute Python code in a sandbox.
    
    Args:
        code: Python code to execute
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary with execution results
    """
    sandbox = get_sandbox()
    
    try:
        result = await sandbox.execute(code, language="python", timeout=timeout)
        return result.to_dict()
    finally:
        await sandbox.cleanup()


async def run_javascript_code(
    code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute JavaScript code in a sandbox.
    
    Args:
        code: JavaScript code to execute
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary with execution results
    """
    sandbox = get_sandbox()
    
    try:
        result = await sandbox.execute(code, language="javascript", timeout=timeout)
        return result.to_dict()
    finally:
        await sandbox.cleanup()


async def run_bash_code(
    code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute Bash commands in a sandbox.
    
    Args:
        code: Bash commands to execute
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary with execution results
    """
    sandbox = get_sandbox()
    
    try:
        result = await sandbox.execute(code, language="bash", timeout=timeout)
        return result.to_dict()
    finally:
        await sandbox.cleanup()


def run_python_code_sync(code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Synchronous version of run_python_code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_python_code(code, timeout))


def run_javascript_code_sync(code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Synchronous version of run_javascript_code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_javascript_code(code, timeout))


def run_bash_code_sync(code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Synchronous version of run_bash_code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_bash_code(code, timeout))


# Example usage
if __name__ == "__main__":
    async def test_execution():
        """Test the execution tool."""
        print("Testing Python execution:")
        result = await run_python_code("print('Hello from sandbox!')")
        print(f"Success: {result['success']}")
        print(f"Output: {result['stdout']}")
        
        print("\nTesting JavaScript execution:")
        result = await run_javascript_code("console.log('Hello from sandbox!');")
        print(f"Success: {result['success']}")
        print(f"Output: {result['stdout']}")
        
        print("\nTesting Bash execution:")
        result = await run_bash_code("echo 'Hello from sandbox!'")
        print(f"Success: {result['success']}")
        print(f"Output: {result['stdout']}")
    
    asyncio.run(test_execution())
