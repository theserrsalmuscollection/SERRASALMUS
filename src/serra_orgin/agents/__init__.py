"""
SERRA ORGIN Agents Module

Implements the core agent system inspired by Agent Zero but enhanced with:
- Self-learning capabilities
- Multi-agent coordination
- Specialized agent types
- Tool creation and management
"""

from serra_orgin.agents.base import BaseAgent
from serra_orgin.agents.swarm import AgentSwarm
from serra_orgin.agents.specialized import (
    FullStackDeveloperAgent,
    WebScrapingAgent,
    DataAnalysisAgent,
    DeploymentAgent,
    TestingAgent
)

__all__ = [
    "BaseAgent",
    "AgentSwarm", 
    "FullStackDeveloperAgent",
    "WebScrapingAgent",
    "DataAnalysisAgent",
    "DeploymentAgent",
    "TestingAgent"
]
