"""
Demo script for the multi-agent swarm system.

Shows how to use the swarm orchestrator to execute tasks
using multiple specialized agents.
"""

import asyncio
from src.swarm import SwarmOrchestrator


async def demo_basic_task():
    """Demo: Basic task execution."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Task Execution")
    print("="*70)
    
    orchestrator = SwarmOrchestrator()
    
    task = "Create a Python function to calculate Fibonacci numbers and review it for performance"
    
    result = await orchestrator.execute(task, verbose=True)
    
    print("\n📊 Final Result:")
    print(f"Success: {result['success']}")
    print(f"Workers Used: {', '.join(result['workers_used'])}")
    print(f"Messages Exchanged: {result['message_count']}")
    
    print("\n📝 Synthesis:")
    print(result['synthesis'])


async def demo_code_review():
    """Demo: Code review task."""
    print("\n" + "="*70)
    print("DEMO 2: Code Review Task")
    print("="*70)
    
    orchestrator = SwarmOrchestrator()
    
    task = "Review this code for security vulnerabilities and suggest improvements"
    
    result = await orchestrator.execute(task, verbose=True)
    
    print("\n📊 Final Result:")
    print(f"Success: {result['success']}")
    print(f"Delegation Plan: {list(result['delegation_plan'].keys())}")


async def demo_research_task():
    """Demo: Research task."""
    print("\n" + "="*70)
    print("DEMO 3: Research Task")
    print("="*70)
    
    orchestrator = SwarmOrchestrator()
    
    task = "Research best practices for implementing microservices architecture"
    
    result = await orchestrator.execute(task, verbose=True)
    
    print("\n📊 Final Result:")
    print(f"Success: {result['success']}")


async def demo_complex_task():
    """Demo: Complex multi-agent task."""
    print("\n" + "="*70)
    print("DEMO 4: Complex Task (All Agents)")
    print("="*70)
    
    orchestrator = SwarmOrchestrator()
    
    task = """
    I need to implement a new authentication system. First, research current best practices
    for JWT-based authentication. Then write the implementation code. Finally, review the
    code for security vulnerabilities.
    """
    
    result = await orchestrator.execute(task, verbose=True)
    
    print("\n📊 Final Result:")
    print(f"Success: {result['success']}")
    print(f"Workers Used: {', '.join(result['workers_used'])}")
    
    # Show message log
    print("\n📨 Message Log:")
    for i, msg in enumerate(orchestrator.get_message_log(), 1):
        print(f"{i}. [{msg['sender']}] {msg['content'][:60]}...")


async def demo_agent_capabilities():
    """Demo: Show agent capabilities."""
    print("\n" + "="*70)
    print("DEMO 5: Agent Capabilities")
    print("="*70)
    
    orchestrator = SwarmOrchestrator()
    
    capabilities = orchestrator.get_agent_capabilities()
    
    for agent_name, capability_desc in capabilities.items():
        print(f"\n{capability_desc}")


async def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("MULTI-AGENT SWARM SYSTEM DEMO")
    print("="*70)
    
    # Run demos
    await demo_basic_task()
    await demo_code_review()
    await demo_research_task()
    await demo_complex_task()
    await demo_agent_capabilities()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
