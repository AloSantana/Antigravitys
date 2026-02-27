"""
Agent Management System for Antigravity Workspace
Dynamically loads and manages custom coding agents
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import re

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Agent metadata structure"""
    name: str
    type: str
    expertise: str
    priority: str
    description: str
    capabilities: List[str]
    tools: List[str]
    file_path: str


class AgentManager:
    """
    Manages custom coding agents for the workspace
    Provides dynamic loading, querying, and orchestration
    """
    
    def __init__(self, agents_dir: str = ".github/agents"):
        """
        Initialize the agent manager
        
        Args:
            agents_dir: Directory containing agent definition files
        """
        self.agents_dir = Path(agents_dir)
        self.agents: Dict[str, AgentMetadata] = {}
        self.agent_cache: Dict[str, str] = {}  # Cache full agent content
        
        if not self.agents_dir.exists():
            logger.warning(f"Agents directory not found: {agents_dir}")
            self.agents_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_agents()
    
    def load_agents(self) -> None:
        """Load all agent definitions from the agents directory"""
        logger.info(f"Loading agents from {self.agents_dir}")
        
        agent_files = list(self.agents_dir.glob("*.agent.md"))
        
        for agent_file in agent_files:
            try:
                agent_metadata = self._parse_agent_file(agent_file)
                if agent_metadata:
                    self.agents[agent_metadata.name] = agent_metadata
                    logger.info(f"Loaded agent: {agent_metadata.name}")
            except Exception as e:
                logger.error(f"Failed to load agent {agent_file}: {e}")
        
        logger.info(f"Successfully loaded {len(self.agents)} agents")
    
    def _parse_agent_file(self, file_path: Path) -> Optional[AgentMetadata]:
        """
        Parse an agent definition file and extract metadata
        
        Args:
            file_path: Path to the agent definition file
            
        Returns:
            AgentMetadata object or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache the full content
            agent_name = file_path.stem.replace('.agent', '')
            self.agent_cache[agent_name] = content
            
            # Extract metadata from the file
            metadata = {
                'name': agent_name,
                'type': 'Custom Agent',
                'expertise': '',
                'priority': 'medium',
                'description': '',
                'capabilities': [],
                'tools': [],
                'file_path': str(file_path)
            }
            
            # Parse metadata section
            metadata_section = re.search(
                r'## Agent Metadata\s*(.*?)\s*##',
                content,
                re.DOTALL
            )
            
            if metadata_section:
                meta_text = metadata_section.group(1)
                
                # Extract fields
                for field in ['Name', 'Type', 'Expertise', 'Priority']:
                    pattern = rf'-\s*\*\*{field}\*\*:\s*(.+?)(?:\n|$)'
                    match = re.search(pattern, meta_text)
                    if match:
                        metadata[field.lower()] = match.group(1).strip()
            
            # Extract description from Purpose section
            purpose_section = re.search(
                r'## Purpose\s*(.*?)\s*##',
                content,
                re.DOTALL
            )
            if purpose_section:
                metadata['description'] = purpose_section.group(1).strip()
            
            # Extract capabilities from Core Responsibilities
            resp_section = re.search(
                r'## Core Responsibilities\s*(.*?)\s*##',
                content,
                re.DOTALL
            )
            if resp_section:
                resp_text = resp_section.group(1)
                capabilities = re.findall(r'\d+\.\s*\*\*(.+?)\*\*:', resp_text)
                metadata['capabilities'] = capabilities
            
            # Extract tools from Available Tools
            tools_section = re.search(
                r'## Available Tools\s*(.*?)\s*##',
                content,
                re.DOTALL
            )
            if tools_section:
                tools_text = tools_section.group(1)
                tools = re.findall(r'-\s*(\w+):', tools_text)
                metadata['tools'] = tools
            
            return AgentMetadata(**metadata)
            
        except Exception as e:
            logger.error(f"Error parsing agent file {file_path}: {e}")
            return None
    
    def get_agent(self, name: str) -> Optional[AgentMetadata]:
        """
        Get agent metadata by name
        
        Args:
            name: Agent name
            
        Returns:
            AgentMetadata or None
        """
        return self.agents.get(name)
    
    def get_agent_content(self, name: str) -> Optional[str]:
        """
        Get full agent definition content
        
        Args:
            name: Agent name
            
        Returns:
            Agent definition as string or None
        """
        return self.agent_cache.get(name)
    
    def list_agents(self) -> List[AgentMetadata]:
        """
        Get list of all available agents
        
        Returns:
            List of agent metadata
        """
        return list(self.agents.values())
    
    def find_agents_by_capability(self, capability: str) -> List[AgentMetadata]:
        """
        Find agents with a specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of matching agents
        """
        matching_agents = []
        capability_lower = capability.lower()
        
        for agent in self.agents.values():
            for cap in agent.capabilities:
                if capability_lower in cap.lower():
                    matching_agents.append(agent)
                    break
        
        return matching_agents
    
    def find_agents_by_tool(self, tool: str) -> List[AgentMetadata]:
        """
        Find agents that use a specific tool
        
        Args:
            tool: Tool name to search for
            
        Returns:
            List of matching agents
        """
        return [
            agent for agent in self.agents.values()
            if tool in agent.tools
        ]
    
    # Expanded keyword vocabulary for all agents with weighted scoring
    AGENT_KEYWORDS = {
        'full-stack-developer': {
            'keywords': ['api', 'frontend', 'backend', 'database', 'endpoint', 'crud',
                         'rest', 'graphql', 'component', 'route', 'middleware', 'schema',
                         'migration', 'model', 'view', 'controller', 'service', 'build',
                         'create', 'implement', 'develop', 'feature', 'app', 'application'],
            'strong': ['full-stack', 'fullstack', 'web app', 'webapp'],
            'reason': 'Full-stack development covering frontend and backend'
        },
        'devops-infrastructure': {
            'keywords': ['docker', 'deploy', 'ci/cd', 'kubernetes', 'container', 'pipeline',
                         'infrastructure', 'terraform', 'aws', 'gcp', 'azure', 'helm',
                         'nginx', 'ssl', 'dns', 'monitoring', 'logging', 'scaling',
                         'load balancer', 'cluster', 'server', 'cloud', 'devops'],
            'strong': ['ci/cd', 'kubernetes', 'k8s', 'infrastructure as code'],
            'reason': 'DevOps, infrastructure, and deployment expertise'
        },
        'testing-stability-expert': {
            'keywords': ['test', 'testing', 'stability', 'reliability', 'unit test',
                         'integration test', 'e2e', 'coverage', 'mock', 'fixture',
                         'assert', 'spec', 'qa', 'regression', 'flaky', 'pytest',
                         'jest', 'playwright', 'cypress', 'selenium'],
            'strong': ['test suite', 'test coverage', 'tdd', 'bdd'],
            'reason': 'Testing, QA, and stability engineering'
        },
        'performance-optimizer': {
            'keywords': ['performance', 'optimize', 'speed', 'efficiency', 'slow',
                         'memory', 'cpu', 'latency', 'throughput', 'cache', 'bottleneck',
                         'profiling', 'benchmark', 'bundle size', 'lazy', 'async',
                         'concurrent', 'parallel', 'fast', 'lag', 'timeout'],
            'strong': ['performance optimization', 'profiling', 'memory leak'],
            'reason': 'Performance analysis and optimization'
        },
        'code-reviewer': {
            'keywords': ['review', 'security', 'quality', 'vulnerability', 'audit',
                         'code smell', 'refactor', 'clean code', 'best practice',
                         'lint', 'static analysis', 'owasp', 'xss', 'injection',
                         'sanitize', 'validate', 'pattern', 'anti-pattern'],
            'strong': ['code review', 'security audit', 'vulnerability scan'],
            'reason': 'Code review, security analysis, and quality assurance'
        },
        'docs-master': {
            'keywords': ['documentation', 'docs', 'readme', 'guide', 'tutorial',
                         'comment', 'docstring', 'jsdoc', 'swagger', 'openapi',
                         'changelog', 'wiki', 'explain', 'document', 'write up'],
            'strong': ['api docs', 'documentation', 'readme'],
            'reason': 'Documentation and technical writing'
        },
        'repo-optimizer': {
            'keywords': ['structure', 'setup', 'organization', 'tooling', 'config',
                         'monorepo', 'workspace', 'linter', 'formatter', 'prettier',
                         'eslint', 'husky', 'git hooks', 'package.json', 'tsconfig',
                         'project structure', 'scaffold', 'boilerplate', 'template'],
            'strong': ['repo structure', 'project setup', 'monorepo'],
            'reason': 'Repository structure and tooling optimization'
        },
        'debug-detective': {
            'keywords': ['bug', 'debug', 'error', 'fix', 'crash', 'broken', 'issue',
                         'traceback', 'exception', 'stack trace', 'not working',
                         'fails', 'failing', 'investigate', 'diagnose', 'wrong',
                         'unexpected', 'undefined', 'null', 'nan', 'corrupt'],
            'strong': ['debug', 'root cause', 'stack trace', 'investigate'],
            'reason': 'Debugging and root cause analysis'
        },
        'architect': {
            'keywords': ['architecture', 'design', 'pattern', 'microservice', 'monolith',
                         'event driven', 'cqrs', 'saga', 'domain', 'ddd', 'clean arch',
                         'hexagonal', 'layer', 'module', 'decouple', 'scale', 'system design'],
            'strong': ['system design', 'architecture', 'design pattern'],
            'reason': 'System architecture and design patterns'
        },
        'jules': {
            'keywords': ['plan', 'coordinate', 'orchestrate', 'multi-agent', 'workflow',
                         'pipeline', 'strategy', 'roadmap', 'milestone', 'sprint',
                         'breakdown', 'decompose', 'prioritize', 'scope'],
            'strong': ['project plan', 'orchestrate', 'coordinate agents'],
            'reason': 'Project planning and multi-agent coordination'
        },
        'rapid-implementer': {
            'keywords': ['quick', 'fast', 'rapid', 'prototype', 'mvp', 'scaffold',
                         'generate', 'bootstrap', 'starter', 'skeleton', 'simple',
                         'straightforward', 'basic', 'small change', 'tweak'],
            'strong': ['prototype', 'mvp', 'quick fix', 'rapid'],
            'reason': 'Rapid prototyping and fast implementation'
        },
    }

    # Auto-select threshold: confidence >= this value auto-selects the agent
    AUTO_SELECT_THRESHOLD = 80

    def _score_agents(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Score all agents against a task description.
        
        Returns:
            Sorted list of { name, score, confidence, reason } dicts (highest first)
        """
        task_lower = task_description.lower()
        word_count = max(len(task_lower.split()), 1)
        
        scored = []
        for agent_name, config in self.AGENT_KEYWORDS.items():
            keywords = config['keywords']
            strong = config.get('strong', [])
            
            # Base keyword score
            base_hits = sum(1 for kw in keywords if kw in task_lower)
            
            # Strong keyword bonus (count double)
            strong_hits = sum(1 for kw in strong if kw in task_lower)
            
            raw_score = base_hits + (strong_hits * 2)
            
            if raw_score > 0:
                # Normalize to 0-100 confidence
                # Factors: keyword density relative to available keywords and query length
                keyword_coverage = raw_score / len(keywords)
                length_bonus = min(raw_score / max(word_count * 0.3, 1), 1.0)
                confidence = min(int((keyword_coverage * 60) + (length_bonus * 40)), 100)
                
                # Check if the agent is actually loaded
                agent_loaded = agent_name in self.agents
                
                scored.append({
                    'name': agent_name,
                    'raw_score': raw_score,
                    'confidence': confidence,
                    'reason': config['reason'],
                    'loaded': agent_loaded
                })
        
        scored.sort(key=lambda x: x['confidence'], reverse=True)
        return scored

    def suggest_agents(self, task_description: str, limit: int = 3, 
                       min_confidence: int = 0) -> List[Dict[str, Any]]:
        """
        Suggest the best agents for a task with confidence scores.
        
        Args:
            task_description: Description of the task
            limit: Maximum number of suggestions (default 3)
            min_confidence: Minimum confidence threshold (default 0)
            
        Returns:
            List of suggestions: [{ agent_name, confidence, reason, auto_select }]
        """
        if not task_description or len(task_description.strip()) < 3:
            return []

        scored = self._score_agents(task_description)
        
        suggestions = []
        for item in scored[:limit]:
            if item['confidence'] >= min_confidence:
                meta = self.agents.get(item['name'])
                suggestions.append({
                    'agent_name': item['name'],
                    'confidence': item['confidence'],
                    'reason': item['reason'],
                    'auto_select': item['confidence'] >= self.AUTO_SELECT_THRESHOLD,
                    'expertise': meta.expertise if meta else item['reason'],
                    'loaded': item['loaded']
                })
        
        return suggestions

    def recommend_agent(self, task_description: str) -> Optional[AgentMetadata]:
        """
        Recommend the best agent for a given task (backward compatible).
        
        Args:
            task_description: Description of the task
            
        Returns:
            Recommended agent or None
        """
        suggestions = self.suggest_agents(task_description, limit=1)
        
        if suggestions:
            agent_name = suggestions[0]['agent_name']
            return self.agents.get(agent_name)
        
        return None
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded agents
        
        Returns:
            Dictionary with agent statistics
        """
        return {
            'total_agents': len(self.agents),
            'agents_by_priority': {
                'high': len([a for a in self.agents.values() if a.priority.lower() == 'high']),
                'medium': len([a for a in self.agents.values() if a.priority.lower() == 'medium']),
                'low': len([a for a in self.agents.values() if a.priority.lower() == 'low'])
            },
            'unique_capabilities': len(set(
                cap for agent in self.agents.values() for cap in agent.capabilities
            )),
            'unique_tools': len(set(
                tool for agent in self.agents.values() for tool in agent.tools
            ))
        }
    
    def export_agent_catalog(self, output_path: str) -> None:
        """
        Export agent catalog to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        catalog = {
            'agents': [asdict(agent) for agent in self.agents.values()],
            'stats': self.get_agent_stats()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2)
        
        logger.info(f"Agent catalog exported to {output_path}")
    
    def validate_agents(self) -> Dict[str, List[str]]:
        """
        Validate all agents and return any issues
        
        Returns:
            Dictionary mapping agent names to lists of issues
        """
        issues = {}
        
        for name, agent in self.agents.items():
            agent_issues = []
            
            # Check for required fields
            if not agent.expertise:
                agent_issues.append("Missing expertise field")
            
            if not agent.description:
                agent_issues.append("Missing description")
            
            if not agent.capabilities:
                agent_issues.append("No capabilities defined")
            
            if not agent.tools:
                agent_issues.append("No tools defined")
            
            # Check if file exists
            if not Path(agent.file_path).exists():
                agent_issues.append(f"Agent file not found: {agent.file_path}")
            
            if agent_issues:
                issues[name] = agent_issues
        
        return issues


def main():
    """Main function for testing agent manager"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    manager = AgentManager()
    
    # Display loaded agents
    print("\n=== Loaded Agents ===")
    for agent in manager.list_agents():
        print(f"\n{agent.name}")
        print(f"  Type: {agent.type}")
        print(f"  Priority: {agent.priority}")
        print(f"  Expertise: {agent.expertise}")
        print(f"  Capabilities: {', '.join(agent.capabilities[:3])}...")
        print(f"  Tools: {', '.join(agent.tools[:5])}...")
    
    # Display statistics
    print("\n=== Agent Statistics ===")
    stats = manager.get_agent_stats()
    print(f"Total agents: {stats['total_agents']}")
    print(f"By priority: {stats['agents_by_priority']}")
    print(f"Unique capabilities: {stats['unique_capabilities']}")
    print(f"Unique tools: {stats['unique_tools']}")
    
    # Test recommendation
    print("\n=== Agent Recommendations ===")
    test_tasks = [
        "Create a REST API endpoint for user management",
        "Setup Docker containers for the application",
        "Write comprehensive tests for the auth module",
        "Optimize the database query performance"
    ]
    
    for task in test_tasks:
        recommended = manager.recommend_agent(task)
        if recommended:
            print(f"\nTask: {task}")
            print(f"Recommended: {recommended.name}")
    
    # Validate agents
    print("\n=== Agent Validation ===")
    issues = manager.validate_agents()
    if issues:
        for name, agent_issues in issues.items():
            print(f"\n{name}:")
            for issue in agent_issues:
                print(f"  - {issue}")
    else:
        print("All agents valid ✓")
    
    # Export catalog
    manager.export_agent_catalog('agent_catalog.json')
    print("\n✓ Agent catalog exported to agent_catalog.json")


if __name__ == "__main__":
    main()
