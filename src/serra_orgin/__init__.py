"""
SERRA ORGIN - A Comprehensive AI Agent Framework

Combining the best features from Agent Zero, same.new, and lovable.dev to create
a fully autonomous AI development platform capable of handling end-to-end
software development lifecycle automation.

Author: SERRA ORGIN Team
Email: polerbear1973@gmail.com, theserralmuscollectionllc@gmail.com
License: MIT
"""

__version__ = "1.0.0"
__author__ = "SERRA ORGIN Team"
__email__ = "polerbear1973@gmail.com"
__license__ = "MIT"

from serra_orgin.core import SerraOrginCore
from serra_orgin.agents import BaseAgent, AgentSwarm
from serra_orgin.memory import MemorySystem
from serra_orgin.tools import ToolRegistry
from serra_orgin.mcp import MCPClient, MCPServer
from serra_orgin.rag import RAGSystem
from serra_orgin.scraper import WebScraper

__all__ = [
    "SerraOrginCore",
    "BaseAgent",
    "AgentSwarm", 
    "MemorySystem",
    "ToolRegistry",
    "MCPClient",
    "MCPServer",
    "RAGSystem",
    "WebScraper",
]
