"""
SERRA ORGIN Core Framework

The central orchestrator that brings together all components:
- Agent management
- Memory system
- Tool registry
- MCP integration
- RAG system
- Web scraping
- Self-learning capabilities
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from serra_orgin.config import Settings
from serra_orgin.memory import MemorySystem
from serra_orgin.tools import ToolRegistry
from serra_orgin.mcp import MCPManager
from serra_orgin.rag import RAGSystem
from serra_orgin.agents import BaseAgent
from serra_orgin.scraper import WebScraper
from serra_orgin.database import DatabaseManager
from serra_orgin.utils import EventBus, TaskQueue


class CoreStatus(BaseModel):
    """Core system status"""
    initialized: bool = False
    agents_count: int = 0
    memory_size: int = 0
    tools_count: int = 0
    scraper_active: bool = False
    rag_enabled: bool = False
    mcp_connected: bool = False
    last_heartbeat: Optional[datetime] = None


class SerraOrginCore:
    """
    Central core system that orchestrates all SERRA ORGIN components
    
    Inspired by Agent Zero's architecture but enhanced with:
    - Lovable.dev's full-stack generation capabilities
    - Advanced MCP integration
    - Self-learning and improvement
    - Multi-agent swarm coordination
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.status = CoreStatus()
        
        # Core components
        self.database: Optional[DatabaseManager] = None
        self.memory: Optional[MemorySystem] = None
        self.tools: Optional[ToolRegistry] = None
        self.mcp: Optional[MCPManager] = None
        self.rag: Optional[RAGSystem] = None
        self.scraper: Optional[WebScraper] = None
        
        # Active agents
        self.agents: Dict[str, BaseAgent] = {}
        
        # Event system
        self.event_bus = EventBus()
        self.task_queue = TaskQueue()
        
        # Self-learning components
        self.learning_data: Dict[str, Any] = {}
        self.improvement_metrics: Dict[str, float] = {}
        
        logger.info("🌊 SERRA ORGIN Core initialized")
        
    async def initialize(self):
        """Initialize all core components"""
        try:
            logger.info("🔄 Initializing SERRA ORGIN Core components...")
            
            # Initialize database
            self.database = DatabaseManager(self.settings.database_url)
            await self.database.initialize()
            
            # Initialize memory system
            self.memory = MemorySystem(
                db=self.database,
                max_size=self.settings.agent_memory_size
            )
            await self.memory.initialize()
            
            # Initialize tool registry
            self.tools = ToolRegistry(self.settings)
            await self.tools.initialize()
            
            # Initialize MCP manager
            self.mcp = MCPManager(self.settings)
            await self.mcp.initialize()
            
            # Initialize RAG system
            self.rag = RAGSystem(
                embedding_model=self.settings.embedding_model,
                vector_db_path=self.settings.vector_db_path
            )
            await self.rag.initialize()
            
            # Initialize web scraper
            self.scraper = WebScraper(self.settings)
            await self.scraper.initialize()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Update status
            self.status.initialized = True
            self.status.last_heartbeat = datetime.utcnow()
            
            logger.success("✅ SERRA ORGIN Core initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core: {e}")
            raise
    
    async def create_agent(
        self,
        agent_type: str = "general",
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new agent with specified capabilities"""
        
        if len(self.agents) >= self.settings.max_agents:
            raise ValueError(f"Maximum agents limit ({self.settings.max_agents}) reached")
        
        # Generate unique agent ID
        agent_id = f"agent_{len(self.agents) + 1}_{datetime.utcnow().timestamp()}"
        
        # Create agent
        agent = BaseAgent(
            agent_id=agent_id,
            name=name or f"Agent-{len(self.agents) + 1}",
            agent_type=agent_type,
            capabilities=capabilities or [],
            core=self,
            config=config or {}
        )
        
        # Initialize agent
        await agent.initialize()
        
        # Register agent
        self.agents[agent_id] = agent
        self.status.agents_count = len(self.agents)
        
        # Emit event
        await self.event_bus.emit("agent_created", {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "name": agent.name
        })
        
        logger.info(f"🤖 Created agent: {agent.name} ({agent_id})")
        return agent_id
    
    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        await agent.shutdown()
        
        del self.agents[agent_id]
        self.status.agents_count = len(self.agents)
        
        await self.event_bus.emit("agent_removed", {"agent_id": agent_id})
        
        logger.info(f"🗑️  Removed agent: {agent_id}")
        return True
    
    async def process_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user request through the framework
        
        This is the main entry point for all user interactions
        """
        try:
            # Log request
            logger.info(f"📝 Processing request: {request[:100]}...")
            
            # Enhance context with RAG if available
            if self.rag and context:
                enhanced_context = await self.rag.enhance_context(request, context)
                context.update(enhanced_context)
            
            # Select or create appropriate agent
            if agent_id and agent_id in self.agents:
                agent = self.agents[agent_id]
            else:
                # Auto-select best agent or create one
                agent = await self._select_best_agent(request, context)
            
            # Process request through agent
            response = await agent.process_request(request, context)
            
            # Learn from interaction
            await self._learn_from_interaction(request, response, context)
            
            # Update metrics
            await self._update_metrics("request_processed", 1)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_full_stack_app(
        self,
        description: str,
        framework: str = "react",
        backend: str = "fastapi",
        database: str = "sqlite"
    ) -> Dict[str, Any]:
        """
        Generate a complete full-stack application
        Inspired by lovable.dev's capabilities
        """
        logger.info(f"🏗️  Generating full-stack app: {description}")
        
        try:
            # Create specialized agent for app generation
            agent_id = await self.create_agent(
                agent_type="full_stack_developer",
                name="FullStack-Generator",
                capabilities=["code_generation", "testing", "deployment"],
                config={
                    "framework": framework,
                    "backend": backend,
                    "database": database
                }
            )
            
            # Process generation request
            response = await self.process_request(
                f"Generate a complete {framework} + {backend} + {database} application: {description}",
                context={
                    "task_type": "full_stack_generation",
                    "framework": framework,
                    "backend": backend,
                    "database": database
                },
                agent_id=agent_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating app: {e}")
            return {"success": False, "error": str(e)}
    
    async def scrape_and_analyze(
        self,
        url: str,
        analysis_type: str = "content",
        background: bool = False
    ) -> Dict[str, Any]:
        """Scrape web content and perform analysis"""
        if not self.scraper:
            return {"success": False, "error": "Scraper not available"}
        
        try:
            if background:
                # Queue for background processing
                await self.task_queue.add_task("scrape_analyze", {
                    "url": url,
                    "analysis_type": analysis_type
                })
                return {"success": True, "status": "queued"}
            else:
                # Process immediately
                content = await self.scraper.scrape(url)
                
                # Analyze content using RAG
                if self.rag:
                    analysis = await self.rag.analyze_content(content, analysis_type)
                    return {
                        "success": True,
                        "content": content,
                        "analysis": analysis
                    }
                
                return {"success": True, "content": content}
                
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if core system is healthy"""
        return (
            self.status.initialized and
            self.database is not None and
            self.memory is not None and
            self.tools is not None
        )
    
    async def get_status(self) -> CoreStatus:
        """Get current system status"""
        # Update dynamic values
        self.status.memory_size = await self.memory.get_size() if self.memory else 0
        self.status.tools_count = len(self.tools.tools) if self.tools else 0
        self.status.scraper_active = self.scraper.is_active() if self.scraper else False
        self.status.rag_enabled = self.rag is not None
        self.status.mcp_connected = await self.mcp.is_connected() if self.mcp else False
        self.status.last_heartbeat = datetime.utcnow()
        
        return self.status
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("🛑 Shutting down SERRA ORGIN Core...")
        
        # Shutdown all agents
        for agent_id in list(self.agents.keys()):
            await self.remove_agent(agent_id)
        
        # Shutdown components
        if self.scraper:
            await self.scraper.shutdown()
        
        if self.mcp:
            await self.mcp.shutdown()
        
        if self.rag:
            await self.rag.shutdown()
        
        if self.tools:
            await self.tools.shutdown()
        
        if self.memory:
            await self.memory.shutdown()
        
        if self.database:
            await self.database.shutdown()
        
        logger.success("✅ SERRA ORGIN Core shutdown complete")
    
    # Private methods
    
    async def _select_best_agent(
        self,
        request: str,
        context: Optional[Dict[str, Any]]
    ) -> BaseAgent:
        """Select the best agent for a request or create a new one"""
        
        # Simple selection logic - can be enhanced with ML
        if not self.agents:
            # Create first general agent
            agent_id = await self.create_agent()
            return self.agents[agent_id]
        
        # For now, return the first available agent
        # TODO: Implement intelligent agent selection
        return list(self.agents.values())[0]
    
    async def _learn_from_interaction(
        self,
        request: str,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ):
        """Learn from user interactions to improve future responses"""
        
        # Store interaction for learning
        interaction_data = {
            "request": request,
            "response": response,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "success": response.get("success", False)
        }
        
        # Add to memory
        if self.memory:
            await self.memory.store_interaction(interaction_data)
        
        # Update learning metrics
        if response.get("success"):
            self.improvement_metrics["successful_interactions"] = (
                self.improvement_metrics.get("successful_interactions", 0) + 1
            )
        else:
            self.improvement_metrics["failed_interactions"] = (
                self.improvement_metrics.get("failed_interactions", 0) + 1
            )
    
    async def _update_metrics(self, metric_name: str, value: float):
        """Update system metrics"""
        self.improvement_metrics[metric_name] = (
            self.improvement_metrics.get(metric_name, 0) + value
        )
    
    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        
        async def heartbeat_task():
            while True:
                await asyncio.sleep(30)  # Every 30 seconds
                self.status.last_heartbeat = datetime.utcnow()
                
        async def cleanup_task():
            while True:
                await asyncio.sleep(3600)  # Every hour
                if self.memory:
                    await self.memory.cleanup_old_data()
        
        # Start background tasks
        asyncio.create_task(heartbeat_task())
        asyncio.create_task(cleanup_task())
