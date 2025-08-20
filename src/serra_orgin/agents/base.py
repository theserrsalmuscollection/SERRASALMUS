"""
Base Agent Implementation

Core agent class that provides the foundation for all specialized agents.
Inspired by Agent Zero's dynamic tool creation but enhanced with self-learning.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass

from loguru import logger
from pydantic import BaseModel

from serra_orgin.tools import Tool, ToolResult
from serra_orgin.memory import AgentMemory


@dataclass
class AgentCapability:
    """Represents an agent capability"""
    name: str
    description: str
    confidence: float  # 0.0 to 1.0
    usage_count: int = 0


class AgentStatus(BaseModel):
    """Agent status information"""
    agent_id: str
    name: str
    type: str
    status: str  # "idle", "thinking", "working", "error"
    current_task: Optional[str] = None
    capabilities: List[str] = []
    created_at: datetime
    last_activity: datetime
    total_tasks: int = 0
    successful_tasks: int = 0
    error_count: int = 0


class BaseAgent(ABC):
    """
    Base Agent class that provides core functionality for all agents
    
    Key features:
    - Dynamic tool creation and usage
    - Self-learning from interactions
    - Memory management
    - Task execution with error handling
    - Communication with other agents
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[str],
        core: 'SerraOrginCore',
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.core = core
        self.config = config or {}
        
        # Status tracking
        self.status = AgentStatus(
            agent_id=agent_id,
            name=name,
            type=agent_type,
            status="idle",
            capabilities=capabilities,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Capabilities management
        self.capabilities: Dict[str, AgentCapability] = {}
        for cap in capabilities:
            self.capabilities[cap] = AgentCapability(
                name=cap,
                description=f"Capability: {cap}",
                confidence=0.7  # Initial confidence
            )
        
        # Tools and memory
        self.tools: Dict[str, Tool] = {}
        self.memory: Optional[AgentMemory] = None
        
        # Learning data
        self.learning_data: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        
        # Communication
        self.message_handlers: Dict[str, Callable] = {}
        
        logger.info(f"🤖 Agent {self.name} ({self.agent_id}) created")
    
    async def initialize(self):
        """Initialize the agent with core tools and memory"""
        try:
            # Initialize memory
            self.memory = AgentMemory(
                agent_id=self.agent_id,
                database=self.core.database
            )
            await self.memory.initialize()
            
            # Load default tools
            await self._load_default_tools()
            
            # Initialize specialized components
            await self._initialize_specialized()
            
            # Set up message handlers
            self._setup_message_handlers()
            
            logger.info(f"✅ Agent {self.name} initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent {self.name}: {e}")
            raise
    
    async def process_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user request
        
        This is the main entry point for all agent interactions
        """
        self.status.status = "thinking"
        self.status.current_task = request[:50] + "..." if len(request) > 50 else request
        self.status.last_activity = datetime.utcnow()
        
        try:
            logger.info(f"🧠 Agent {self.name} processing: {request}")
            
            # Store request in memory
            await self.memory.store_request(request, context)
            
            # Analyze request
            analysis = await self._analyze_request(request, context)
            
            # Plan execution
            plan = await self._create_execution_plan(analysis)
            
            # Execute plan
            self.status.status = "working"
            result = await self._execute_plan(plan)
            
            # Learn from execution
            await self._learn_from_execution(request, result, context)
            
            # Update metrics
            self.status.total_tasks += 1
            if result.get("success", False):
                self.status.successful_tasks += 1
            else:
                self.status.error_count += 1
            
            self.status.status = "idle"
            self.status.current_task = None
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} error: {e}")
            self.status.status = "error"
            self.status.error_count += 1
            
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_tool(
        self,
        name: str,
        description: str,
        code: str,
        tool_type: str = "python"
    ) -> bool:
        """
        Dynamically create a new tool
        Inspired by Agent Zero's tool creation capability
        """
        try:
            logger.info(f"🔧 Agent {self.name} creating tool: {name}")
            
            # Create tool instance
            tool = Tool(
                name=name,
                description=description,
                code=code,
                tool_type=tool_type,
                agent_id=self.agent_id
            )
            
            # Validate tool
            if await tool.validate():
                self.tools[name] = tool
                
                # Store tool in memory for future use
                await self.memory.store_tool(tool)
                
                # Update capabilities
                if name not in self.capabilities:
                    self.capabilities[name] = AgentCapability(
                        name=name,
                        description=description,
                        confidence=0.5  # New tools start with lower confidence
                    )
                
                logger.success(f"✅ Tool {name} created successfully")
                return True
            else:
                logger.warning(f"⚠️  Tool {name} validation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating tool {name}: {e}")
            return False
    
    async def use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> ToolResult:
        """Use a tool with given parameters"""
        if tool_name not in self.tools:
            # Try to load from memory or core tools
            tool = await self._find_tool(tool_name)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Tool {tool_name} not found",
                    agent_id=self.agent_id
                )
            self.tools[tool_name] = tool
        
        try:
            tool = self.tools[tool_name]
            result = await tool.execute(params)
            
            # Update tool usage statistics
            if tool_name in self.capabilities:
                self.capabilities[tool_name].usage_count += 1
                # Adjust confidence based on success
                if result.success:
                    self.capabilities[tool_name].confidence = min(
                        1.0,
                        self.capabilities[tool_name].confidence + 0.01
                    )
                else:
                    self.capabilities[tool_name].confidence = max(
                        0.1,
                        self.capabilities[tool_name].confidence - 0.05
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error using tool {tool_name}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                agent_id=self.agent_id
            )
    
    async def communicate_with_agent(
        self,
        target_agent_id: str,
        message: str,
        message_type: str = "general"
    ) -> Dict[str, Any]:
        """Communicate with another agent"""
        try:
            target_agent = await self.core.get_agent(target_agent_id)
            if not target_agent:
                return {
                    "success": False,
                    "error": f"Agent {target_agent_id} not found"
                }
            
            # Send message
            response = await target_agent.receive_message(
                sender_id=self.agent_id,
                message=message,
                message_type=message_type
            )
            
            # Store communication in memory
            await self.memory.store_communication(
                target_agent_id, message, response
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Communication error: {e}")
            return {"success": False, "error": str(e)}
    
    async def receive_message(
        self,
        sender_id: str,
        message: str,
        message_type: str = "general"
    ) -> Dict[str, Any]:
        """Receive a message from another agent"""
        logger.info(f"📨 Agent {self.name} received message from {sender_id}")
        
        # Handle message based on type
        if message_type in self.message_handlers:
            return await self.message_handlers[message_type](
                sender_id, message
            )
        else:
            # Default handler
            return await self._handle_general_message(sender_id, message)
    
    async def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        logger.info(f"🛑 Shutting down agent {self.name}")
        
        self.status.status = "shutdown"
        
        # Save learning data
        if self.memory:
            await self.memory.save_learning_data(self.learning_data)
            await self.memory.shutdown()
        
        # Cleanup tools
        for tool in self.tools.values():
            await tool.cleanup()
        
        logger.success(f"✅ Agent {self.name} shutdown complete")
    
    # Abstract methods that specialized agents must implement
    
    @abstractmethod
    async def _initialize_specialized(self):
        """Initialize specialized components for this agent type"""
        pass
    
    @abstractmethod
    async def _analyze_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze incoming request and determine intent"""
        pass
    
    # Private methods
    
    async def _load_default_tools(self):
        """Load default tools from the core tool registry"""
        if not self.core.tools:
            return
        
        # Get tools relevant to this agent's capabilities
        for capability in self.capabilities:
            tools = await self.core.tools.get_tools_for_capability(capability)
            for tool in tools:
                self.tools[tool.name] = tool
    
    async def _find_tool(self, tool_name: str) -> Optional[Tool]:
        """Find a tool from memory or core registry"""
        # First check memory
        if self.memory:
            tool = await self.memory.get_tool(tool_name)
            if tool:
                return tool
        
        # Check core tool registry
        if self.core.tools:
            return await self.core.tools.get_tool(tool_name)
        
        return None
    
    async def _create_execution_plan(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an execution plan based on request analysis"""
        # Default implementation - specialized agents can override
        return {
            "steps": [
                {
                    "action": "respond",
                    "data": analysis
                }
            ],
            "estimated_time": 5.0,
            "complexity": analysis.get("complexity", "medium")
        }
    
    async def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned steps"""
        results = []
        
        try:
            for step in plan.get("steps", []):
                action = step.get("action")
                data = step.get("data", {})
                
                if action == "respond":
                    result = await self._generate_response(data)
                elif action == "use_tool":
                    tool_name = step.get("tool_name")
                    params = step.get("params", {})
                    result = await self.use_tool(tool_name, params)
                elif action == "create_tool":
                    tool_data = step.get("tool_data", {})
                    result = await self._handle_tool_creation(tool_data)
                else:
                    result = {"success": False, "error": f"Unknown action: {action}"}
                
                results.append(result)
                
                # Stop on first failure unless plan specifies continue
                if not result.get("success", False) and not plan.get("continue_on_error", False):
                    break
            
            # Compile final result
            success = all(r.get("success", False) for r in results)
            return {
                "success": success,
                "results": results,
                "agent_id": self.agent_id,
                "execution_time": plan.get("estimated_time", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Plan execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "partial_results": results
            }
    
    async def _generate_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response based on analysis data"""
        # Default implementation - specialized agents should override
        return {
            "success": True,
            "response": f"Agent {self.name} processed the request",
            "data": data
        }
    
    async def _handle_tool_creation(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dynamic tool creation"""
        name = tool_data.get("name")
        description = tool_data.get("description")
        code = tool_data.get("code")
        
        if not all([name, description, code]):
            return {
                "success": False,
                "error": "Missing required tool data (name, description, code)"
            }
        
        success = await self.create_tool(name, description, code)
        return {
            "success": success,
            "message": f"Tool {name} {'created' if success else 'creation failed'}"
        }
    
    async def _learn_from_execution(
        self,
        request: str,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ):
        """Learn from task execution to improve future performance"""
        learning_entry = {
            "request": request,
            "result": result,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_type": self.agent_type,
            "success": result.get("success", False)
        }
        
        # Store in memory
        await self.memory.store_learning_entry(learning_entry)
        
        # Update performance metrics
        execution_time = result.get("execution_time", 0)
        self.performance_metrics["avg_execution_time"] = (
            self.performance_metrics.get("avg_execution_time", 0) * 0.9 +
            execution_time * 0.1
        )
        
        if result.get("success", False):
            self.performance_metrics["success_rate"] = (
                self.performance_metrics.get("success_rate", 0.5) * 0.95 + 0.05
            )
        else:
            self.performance_metrics["success_rate"] = (
                self.performance_metrics.get("success_rate", 0.5) * 0.95
            )
    
    def _setup_message_handlers(self):
        """Set up message handlers for inter-agent communication"""
        self.message_handlers.update({
            "general": self._handle_general_message,
            "task_request": self._handle_task_request,
            "collaboration": self._handle_collaboration_request,
            "data_share": self._handle_data_sharing
        })
    
    async def _handle_general_message(
        self,
        sender_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Handle general messages from other agents"""
        return {
            "success": True,
            "response": f"Message received by {self.name}",
            "sender_id": sender_id
        }
    
    async def _handle_task_request(
        self,
        sender_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Handle task requests from other agents"""
        # Parse task request and delegate if appropriate
        return {
            "success": True,
            "response": f"Task request processed by {self.name}",
            "task_accepted": True
        }
    
    async def _handle_collaboration_request(
        self,
        sender_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Handle collaboration requests"""
        return {
            "success": True,
            "response": f"Collaboration request accepted by {self.name}",
            "collaboration_id": f"collab_{self.agent_id}_{sender_id}_{datetime.utcnow().timestamp()}"
        }
    
    async def _handle_data_sharing(
        self,
        sender_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Handle data sharing between agents"""
        try:
            # Parse shared data (assuming JSON format)
            data = json.loads(message)
            
            # Store in memory for future use
            await self.memory.store_shared_data(sender_id, data)
            
            return {
                "success": True,
                "response": "Data received and stored",
                "data_size": len(str(data))
            }
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON data format"
            }
