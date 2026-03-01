"""Debug script for manager.py test failures"""
import re, sys, os, tempfile
from pathlib import Path

# Test 1: Expertise regex matching
meta_text = '- **Name**: incomplete-agent\n- **Type**: Agent\n- **Expertise**: \n- **Priority**: high'
for field in ['Name', 'Type', 'Expertise', 'Priority']:
    pattern = rf'-\s*\*\*{field}\*\*:\s*(.+?)(?:\n|$)'
    match = re.search(pattern, meta_text)
    val = repr(match.group(1).strip()) if match else "NO MATCH"
    print(f"{field}: {val}")

print()

# Test 2: Check AgentMetadata
sys.path.insert(0, 'backend')
from agent.manager import AgentManager, AgentMetadata

# Test 3: Create incomplete agent and validate
with tempfile.TemporaryDirectory() as td:
    agents_dir = Path(td) / 'agents'
    agents_dir.mkdir()
    content = """# Incomplete Agent

## Agent Metadata
- **Name**: incomplete-agent
- **Type**: Agent
- **Expertise**: 
- **Priority**: high

## Purpose

## Core Responsibilities

## Available Tools
"""
    (agents_dir / 'incomplete-agent.agent.md').write_text(content)
    mgr = AgentManager(agents_dir=str(agents_dir))
    
    print(f"Agents loaded: {list(mgr.agents.keys())}")
    if 'incomplete-agent' in mgr.agents:
        a = mgr.agents['incomplete-agent']
        print(f"expertise: {repr(a.expertise)}")
        print(f"description: {repr(a.description)}")
        print(f"capabilities: {a.capabilities}")
        print(f"tools: {a.tools}")
    
    issues = mgr.validate_agents()
    print(f"Issues: {issues}")

print("\n--- Test recommend_agent ---")
# Test 4: recommend_agent with devops
with tempfile.TemporaryDirectory() as td:
    agents_dir = Path(td) / 'agents'
    agents_dir.mkdir()
    content = """# DevOps Engineer

## Agent Metadata
- **Name**: devops-infrastructure
- **Type**: DevOps
- **Expertise**: Infrastructure
- **Priority**: high

## Purpose
Manage infrastructure

## Core Responsibilities
1. **Containerization**: Docker containers
2. **CI/CD**: Pipeline management

## Available Tools
- docker: Container tool
"""
    (agents_dir / 'devops-infrastructure.agent.md').write_text(content)
    mgr = AgentManager(agents_dir=str(agents_dir))
    
    print(f"Agents loaded: {list(mgr.agents.keys())}")
    if 'devops-infrastructure' in mgr.agents:
        a = mgr.agents['devops-infrastructure']
        print(f"tools: {a.tools}")
        print(f"expertise: {repr(a.expertise)}")
    
    # Check scoring
    scored = mgr._score_agents("Deploy the application using Docker")
    print(f"Scored agents (top 5): {scored[:5]}")
    
    suggestions = mgr.suggest_agents("Deploy the application using Docker", limit=1)
    print(f"Suggestions: {suggestions}")
    
    recommended = mgr.recommend_agent("Deploy the application using Docker")
    print(f"Recommended: {recommended}")
