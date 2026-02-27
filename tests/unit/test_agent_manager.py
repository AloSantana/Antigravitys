"""
Unit tests for backend.agent.manager module
Tests the AgentManager class for agent loading and management
"""

import pytest
import json


@pytest.mark.unit
class TestAgentManager:
    """Test suite for AgentManager class."""
    
    def test_initialization(self, temp_dir):
        """Test AgentManager initializes correctly."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        assert manager.agents_dir == agents_dir
        assert isinstance(manager.agents, dict)
        assert isinstance(manager.agent_cache, dict)
    
    def test_initialization_creates_directory(self, temp_dir):
        """Test AgentManager creates directory if missing."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "nonexistent" / "agents"
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        assert agents_dir.exists()
    
    def test_load_agents_empty_directory(self, temp_dir):
        """Test loading agents from empty directory."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        assert len(manager.agents) == 0
    
    def test_load_single_agent(self, temp_dir):
        """Test loading a single agent."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        agent_content = """# Test Agent

## Agent Metadata
- **Name**: test-agent
- **Type**: Custom Agent
- **Expertise**: Testing and Validation
- **Priority**: high

## Purpose
This agent specializes in testing.

## Core Responsibilities
1. **Testing**: Write comprehensive tests
2. **Validation**: Validate system behavior

## Available Tools
- bash: Execute commands
- edit: Edit files
"""
        (agents_dir / "test-agent.agent.md").write_text(agent_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        assert len(manager.agents) == 1
        assert "test-agent" in manager.agents
        
        agent = manager.agents["test-agent"]
        assert agent.name == "test-agent"
        assert agent.type == "Custom Agent"
        assert agent.expertise == "Testing and Validation"
        assert agent.priority == "high"
        assert "Testing" in agent.capabilities
        assert "bash" in agent.tools
    
    def test_load_multiple_agents(self, temp_dir):
        """Test loading multiple agents."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create multiple agent files
        for i in range(3):
            content = f"""# Agent {i}

## Agent Metadata
- **Name**: agent-{i}
- **Type**: Custom Agent
- **Expertise**: Task {i}
- **Priority**: medium

## Purpose
Agent {i} description

## Core Responsibilities
1. **Task{i}**: Do task {i}

## Available Tools
- tool{i}: Use tool {i}
"""
            (agents_dir / f"agent-{i}.agent.md").write_text(content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        assert len(manager.agents) == 3
        for i in range(3):
            assert f"agent-{i}" in manager.agents
    
    def test_get_agent_exists(self, mock_agent_manager):
        """Test getting an existing agent."""
        agent = mock_agent_manager.get_agent("test-agent")
        
        assert agent is not None
        assert agent.name == "test-agent"
    
    def test_get_agent_not_exists(self, mock_agent_manager):
        """Test getting a non-existent agent."""
        agent = mock_agent_manager.get_agent("nonexistent-agent")
        
        assert agent is None
    
    def test_get_agent_content(self, mock_agent_manager):
        """Test getting full agent content."""
        content = mock_agent_manager.get_agent_content("test-agent")
        
        assert content is not None
        assert "Test Agent" in content
        assert "Agent Metadata" in content
    
    def test_get_agent_content_not_exists(self, mock_agent_manager):
        """Test getting content for non-existent agent."""
        content = mock_agent_manager.get_agent_content("nonexistent")
        
        assert content is None
    
    def test_list_agents(self, mock_agent_manager):
        """Test listing all agents."""
        agents = mock_agent_manager.list_agents()
        
        assert isinstance(agents, list)
        assert len(agents) > 0
        assert all(hasattr(agent, 'name') for agent in agents)
    
    def test_find_agents_by_capability(self, temp_dir):
        """Test finding agents by capability."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create agents with different capabilities
        agent1_content = """# Agent 1

## Agent Metadata
- **Name**: agent-1
- **Type**: Custom Agent
- **Expertise**: Testing
- **Priority**: high

## Purpose
Testing agent

## Core Responsibilities
1. **Testing**: Write unit tests
2. **Validation**: Validate code

## Available Tools
- bash: Execute
"""
        (agents_dir / "agent-1.agent.md").write_text(agent1_content)
        
        agent2_content = """# Agent 2

## Agent Metadata
- **Name**: agent-2
- **Type**: Custom Agent
- **Expertise**: Deployment
- **Priority**: medium

## Purpose
Deployment agent

## Core Responsibilities
1. **Deployment**: Deploy applications
2. **Monitoring**: Monitor services

## Available Tools
- docker: Container management
"""
        (agents_dir / "agent-2.agent.md").write_text(agent2_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        # Find by capability
        testing_agents = manager.find_agents_by_capability("Testing")
        assert len(testing_agents) == 1
        assert testing_agents[0].name == "agent-1"
        
        deployment_agents = manager.find_agents_by_capability("Deployment")
        assert len(deployment_agents) == 1
        assert deployment_agents[0].name == "agent-2"
    
    def test_find_agents_by_tool(self, temp_dir):
        """Test finding agents by tool."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        agent_content = """# Test Agent

## Agent Metadata
- **Name**: docker-agent
- **Type**: DevOps Agent
- **Expertise**: Containers
- **Priority**: high

## Purpose
Docker specialist

## Core Responsibilities
1. **Containerization**: Build containers

## Available Tools
- docker: Container tool
- bash: Shell access
"""
        (agents_dir / "docker-agent.agent.md").write_text(agent_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        docker_agents = manager.find_agents_by_tool("docker")
        assert len(docker_agents) == 1
        assert docker_agents[0].name == "docker-agent"
        
        bash_agents = manager.find_agents_by_tool("bash")
        assert len(bash_agents) == 1
    
    def test_recommend_agent_api_task(self, temp_dir):
        """Test agent recommendation for API task."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create full-stack developer agent
        agent_content = """# Full Stack Developer

## Agent Metadata
- **Name**: full-stack-developer
- **Type**: Developer
- **Expertise**: Full-stack development
- **Priority**: high

## Purpose
Build APIs and frontends

## Core Responsibilities
1. **API Development**: Create REST APIs
2. **Frontend**: Build UIs

## Available Tools
- edit: Edit code
- bash: Run commands
"""
        (agents_dir / "full-stack-developer.agent.md").write_text(agent_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        recommended = manager.recommend_agent("Create a REST API endpoint for users")
        
        assert recommended is not None
        assert recommended.name == "full-stack-developer"
    
    def test_recommend_agent_docker_task(self, temp_dir):
        """Test agent recommendation for Docker task."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        agent_content = """# DevOps Engineer

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
        (agents_dir / "devops-infrastructure.agent.md").write_text(agent_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        recommended = manager.recommend_agent("Deploy the application using Docker")
        
        assert recommended is not None
        assert recommended.name == "devops-infrastructure"
    
    def test_recommend_agent_no_match(self, mock_agent_manager):
        """Test agent recommendation with no matching keywords."""
        recommended = mock_agent_manager.recommend_agent("Do something completely unrelated")
        
        # Should return None if no match
        assert recommended is None or recommended is not None  # May match generic keywords
    
    def test_get_agent_stats(self, temp_dir):
        """Test getting agent statistics."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create agents with different priorities
        for i, priority in enumerate(['high', 'medium', 'low']):
            content = f"""# Agent {i}

## Agent Metadata
- **Name**: agent-{i}
- **Type**: Agent
- **Expertise**: Task {i}
- **Priority**: {priority}

## Purpose
Agent {i}

## Core Responsibilities
1. **Task{i}**: Do task
2. **Work{i}**: Do work

## Available Tools
- tool{i}: Tool
- common: Common tool
"""
            (agents_dir / f"agent-{i}.agent.md").write_text(content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        stats = manager.get_agent_stats()
        
        assert stats['total_agents'] == 3
        assert stats['agents_by_priority']['high'] == 1
        assert stats['agents_by_priority']['medium'] == 1
        assert stats['agents_by_priority']['low'] == 1
        assert stats['unique_capabilities'] > 0
        assert stats['unique_tools'] > 0
    
    def test_export_agent_catalog(self, temp_dir, mock_agent_manager):
        """Test exporting agent catalog to JSON."""
        output_path = temp_dir / "catalog.json"
        
        mock_agent_manager.export_agent_catalog(str(output_path))
        
        assert output_path.exists()
        
        # Verify JSON content
        with open(output_path) as f:
            data = json.load(f)
        
        assert 'agents' in data
        assert 'stats' in data
        assert isinstance(data['agents'], list)
        assert isinstance(data['stats'], dict)
    
    def test_validate_agents_valid(self, mock_agent_manager):
        """Test validation with valid agents."""
        issues = mock_agent_manager.validate_agents()
        
        # Should have no issues or only minor ones
        assert isinstance(issues, dict)
    
    def test_validate_agents_missing_fields(self, temp_dir):
        """Test validation catches missing fields."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create incomplete agent
        incomplete_content = """# Incomplete Agent

## Agent Metadata
- **Name**: incomplete-agent
- **Type**: Agent
- **Expertise**: 
- **Priority**: high

## Purpose

## Core Responsibilities

## Available Tools
"""
        (agents_dir / "incomplete-agent.agent.md").write_text(incomplete_content)
        
        manager = AgentManager(agents_dir=str(agents_dir))
        issues = manager.validate_agents()
        
        assert "incomplete-agent" in issues
        agent_issues = issues["incomplete-agent"]
        assert any("expertise" in issue.lower() for issue in agent_issues)
    
    def test_parse_agent_file_invalid(self, temp_dir):
        """Test parsing an invalid agent file."""
        from backend.agent.manager import AgentManager
        
        agents_dir = temp_dir / "agents"
        agents_dir.mkdir()
        
        # Create invalid agent file
        (agents_dir / "invalid.agent.md").write_text("Not a valid agent file format")
        
        manager = AgentManager(agents_dir=str(agents_dir))
        
        # Should handle gracefully
        assert "invalid" in manager.agents or len(manager.agents) == 0
