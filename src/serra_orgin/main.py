#!/usr/bin/env python3
"""
SERRA ORGIN Main Application Entry Point

This module starts the complete SERRA ORGIN framework including:
- Core agent framework
- Web UI server
- MCP server
- Background scrapers
- Agent swarm coordination
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI
from loguru import logger

from serra_orgin.core import SerraOrginCore
from serra_orgin.config import get_settings
from serra_orgin.api import create_api_router
from serra_orgin.websocket import create_websocket_manager
from serra_orgin.agents import AgentSwarm
from serra_orgin.scraper import BackgroundScraper
from serra_orgin.deployment import DeploymentManager


class SerraOrginApp:
    """Main SERRA ORGIN Application"""
    
    def __init__(self):
        self.settings = get_settings()
        self.core: Optional[SerraOrginCore] = None
        self.app: Optional[FastAPI] = None
        self.swarm: Optional[AgentSwarm] = None
        self.scraper: Optional[BackgroundScraper] = None
        self.deployment: Optional[DeploymentManager] = None
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🌊 Starting SERRA ORGIN - Autonomous AI Development Framework")
        
        # Initialize core system
        self.core = SerraOrginCore(self.settings)
        await self.core.initialize()
        
        # Initialize agent swarm
        self.swarm = AgentSwarm(self.core)
        await self.swarm.initialize()
        
        # Initialize background scraper
        self.scraper = BackgroundScraper(self.core)
        await self.scraper.start()
        
        # Initialize deployment manager
        self.deployment = DeploymentManager(self.core)
        await self.deployment.initialize()
        
        # Create FastAPI app
        self.app = self._create_app()
        
        logger.success("✅ SERRA ORGIN initialized successfully")
        
    def _create_app(self) -> FastAPI:
        """Create FastAPI application with all routes and middleware"""
        app = FastAPI(
            title="SERRA ORGIN API",
            description="Autonomous AI Development Framework",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        
        # Add CORS middleware
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on environment
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Include API routes
        api_router = create_api_router(self.core)
        app.include_router(api_router, prefix="/api/v1")
        
        # Include WebSocket routes
        websocket_manager = create_websocket_manager(self.core)
        app.include_router(websocket_manager.router, prefix="/ws")
        
        # Health check endpoint
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "core": self.core.is_healthy() if self.core else False,
                    "swarm": self.swarm.is_healthy() if self.swarm else False,
                    "scraper": self.scraper.is_healthy() if self.scraper else False,
                    "deployment": self.deployment.is_healthy() if self.deployment else False,
                }
            }
            
        return app
        
    async def run(self):
        """Run the complete SERRA ORGIN system"""
        await self.initialize()
        
        # Set up signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._signal_handler)
        
        # Start the server
        config = uvicorn.Config(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
            log_level="info",
            access_log=True,
            reload=self.settings.environment == "development"
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"🚀 SERRA ORGIN server starting on {self.settings.host}:{self.settings.port}")
        
        # Run server until shutdown
        await server.serve()
        
    def _signal_handler(self):
        """Handle shutdown signals"""
        logger.info("🛑 Shutdown signal received")
        self._shutdown_event.set()
        
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("🔄 Starting graceful shutdown...")
        
        if self.scraper:
            await self.scraper.stop()
            
        if self.swarm:
            await self.swarm.shutdown()
            
        if self.deployment:
            await self.deployment.shutdown()
            
        if self.core:
            await self.core.shutdown()
            
        logger.success("✅ SERRA ORGIN shutdown complete")


async def main():
    """Main entry point"""
    app = SerraOrginApp()
    try:
        await app.run()
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    finally:
        await app.shutdown()
    
    return 0


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/serra_orgin.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="30 days"
    )
    
    # Run the application
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
