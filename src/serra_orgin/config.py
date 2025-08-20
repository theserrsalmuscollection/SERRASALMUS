"""
SERRA ORGIN Configuration Management

Handles all configuration settings for the framework including:
- Environment variables
- Database connections  
- API settings
- Agent configurations
- MCP settings
"""

import os
from functools import lru_cache
from typing import Optional, List
from pathlib import Path

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Main configuration settings for SERRA ORGIN"""
    
    # Application settings
    app_name: str = "SERRA ORGIN"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    websocket_port: int = Field(default=8001, env="WEBSOCKET_PORT")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./data/serra_orgin.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # AI Model settings
    default_model: str = Field(default="gpt-3.5-turbo", env="DEFAULT_MODEL")
    model_temperature: float = Field(default=0.7, env="MODEL_TEMPERATURE")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    
    # OpenAI API (optional - for enhanced capabilities)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Anthropic API (optional)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Local model settings
    local_model_path: str = Field(default="./models", env="LOCAL_MODEL_PATH")
    use_local_models: bool = Field(default=True, env="USE_LOCAL_MODELS")
    
    # Agent settings
    max_agents: int = Field(default=10, env="MAX_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")  # seconds
    agent_memory_size: int = Field(default=1000, env="AGENT_MEMORY_SIZE")
    
    # Scraper settings
    scraper_user_agent: str = Field(
        default="SERRA ORGIN Web Scraper 1.0", 
        env="SCRAPER_USER_AGENT"
    )
    scraper_delay_min: float = Field(default=1.0, env="SCRAPER_DELAY_MIN")
    scraper_delay_max: float = Field(default=5.0, env="SCRAPER_DELAY_MAX")
    max_concurrent_scrapes: int = Field(default=5, env="MAX_CONCURRENT_SCRAPES")
    
    # MCP settings
    mcp_server_port: int = Field(default=9000, env="MCP_SERVER_PORT")
    mcp_enabled_tools: List[str] = Field(
        default=[
            "github",
            "filesystem",
            "web_search",
            "code_execution",
            "database",
            "docker"
        ],
        env="MCP_ENABLED_TOOLS"
    )
    
    # RAG settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_db_path: str = Field(default="./data/vectordb", env="VECTOR_DB_PATH")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Security settings
    secret_key: str = Field(default="serra-orgin-secret-key", env="SECRET_KEY")
    jwt_expiry_hours: int = Field(default=24, env="JWT_EXPIRY_HOURS")
    
    # File paths
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    logs_dir: Path = Field(default=Path("./logs"), env="LOGS_DIR")
    temp_dir: Path = Field(default=Path("./temp"), env="TEMP_DIR")
    uploads_dir: Path = Field(default=Path("./uploads"), env="UPLOADS_DIR")
    
    # GitHub integration (optional)
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    default_github_user: Optional[str] = Field(default=None, env="DEFAULT_GITHUB_USER")
    
    # Docker settings
    docker_socket: str = Field(default="unix://var/run/docker.sock", env="DOCKER_SOCKET")
    docker_registry: Optional[str] = Field(default=None, env="DOCKER_REGISTRY")
    
    # Deployment settings
    deployment_environments: List[str] = Field(
        default=["development", "staging", "production"],
        env="DEPLOYMENT_ENVIRONMENTS"
    )
    auto_deploy: bool = Field(default=False, env="AUTO_DEPLOY")
    
    # UI settings
    web_ui_port: int = Field(default=3000, env="WEB_UI_PORT")
    ui_theme: str = Field(default="dark", env="UI_THEME")
    
    @validator('data_dir', 'logs_dir', 'temp_dir', 'uploads_dir')
    def create_directories(cls, v):
        """Ensure directories exist"""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
        
    @validator('mcp_enabled_tools', pre=True)
    def parse_mcp_tools(cls, v):
        """Parse MCP tools from string or list"""
        if isinstance(v, str):
            return [tool.strip() for tool in v.split(',')]
        return v
        
    @validator('deployment_environments', pre=True)
    def parse_deployment_envs(cls, v):
        """Parse deployment environments from string or list"""
        if isinstance(v, str):
            return [env.strip() for env in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """Development-specific settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    auto_deploy: bool = False


class ProductionSettings(Settings):
    """Production-specific settings"""
    debug: bool = False
    log_level: str = "WARNING"
    host: str = "0.0.0.0"


class TestingSettings(Settings):
    """Testing-specific settings"""
    environment: str = "testing"
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/1"  # Use different Redis DB for tests


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
