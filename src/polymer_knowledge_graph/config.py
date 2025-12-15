"""
Configuration management for the Polymer Knowledge Graph system.

This module provides centralized configuration management for the polymer
knowledge graph application, including database connections, API settings,
logging configuration, and system parameters.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
import logging


class Environment(Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", 5432)))
    username: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("DB_NAME", "polymer_kg"))
    pool_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", 10)))
    max_overflow: int = field(default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", 20)))
    echo: bool = field(default_factory=lambda: os.getenv("DB_ECHO", "false").lower() == "true")
    
    @property
    def connection_string(self) -> str:
        """Generate database connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


@dataclass
class GraphConfig:
    """Knowledge graph configuration settings."""
    
    backend: str = field(default_factory=lambda: os.getenv("GRAPH_BACKEND", "neo4j"))
    host: str = field(default_factory=lambda: os.getenv("GRAPH_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("GRAPH_PORT", 7687)))
    username: str = field(default_factory=lambda: os.getenv("GRAPH_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("GRAPH_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("GRAPH_DATABASE", "polymer"))
    encrypted: bool = field(default_factory=lambda: os.getenv("GRAPH_ENCRYPTED", "false").lower() == "true")
    trust_cert: str = field(default_factory=lambda: os.getenv("GRAPH_TRUST_CERT", "TRUST_ALL_CERTIFICATES"))
    
    @property
    def connection_uri(self) -> str:
        """Generate graph database connection URI."""
        protocol = "neo4j+s" if self.encrypted else "neo4j"
        return f"{protocol}://{self.host}:{self.port}"


@dataclass
class APIConfig:
    """API configuration settings."""
    
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", 8000)))
    debug: bool = field(default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true")
    workers: int = field(default_factory=lambda: int(os.getenv("API_WORKERS", 4)))
    timeout: int = field(default_factory=lambda: int(os.getenv("API_TIMEOUT", 30)))
    max_connections: int = field(default_factory=lambda: int(os.getenv("API_MAX_CONNECTIONS", 100)))
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    output_file: str = field(default_factory=lambda: os.getenv("LOG_FILE", "logs/polymer_kg.log"))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_SIZE", 10485760)))  # 10MB
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", 5)))
    console_output: bool = field(default_factory=lambda: os.getenv("LOG_CONSOLE", "true").lower() == "true")


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    
    enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")
    backend: str = field(default_factory=lambda: os.getenv("CACHE_BACKEND", "redis"))
    host: str = field(default_factory=lambda: os.getenv("CACHE_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("CACHE_PORT", 6379)))
    database: int = field(default_factory=lambda: int(os.getenv("CACHE_DB", 0)))
    ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", 3600)))  # 1 hour
    max_size: int = field(default_factory=lambda: int(os.getenv("CACHE_MAX_SIZE", 1000)))


@dataclass
class PolymersConfig:
    """Polymer-specific configuration settings."""
    
    default_language: str = field(default_factory=lambda: os.getenv("POLYMER_LANGUAGE", "en"))
    max_description_length: int = field(default_factory=lambda: int(os.getenv("POLYMER_MAX_DESC", 5000)))
    enable_validation: bool = field(default_factory=lambda: os.getenv("POLYMER_VALIDATION", "true").lower() == "true")
    supported_properties: list = field(
        default_factory=lambda: [
            "name", "molecular_formula", "molecular_weight", "glass_transition_temperature",
            "melting_point", "density", "elasticity", "thermal_conductivity",
            "electrical_conductivity", "tensile_strength", "elongation_at_break"
        ]
    )
    batch_import_size: int = field(default_factory=lambda: int(os.getenv("POLYMER_BATCH_SIZE", 500)))


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key"))
    algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    token_expiration_hours: int = field(default_factory=lambda: int(os.getenv("TOKEN_EXPIRATION", 24)))
    enable_api_key_auth: bool = field(default_factory=lambda: os.getenv("ENABLE_API_KEY", "true").lower() == "true")
    enable_jwt_auth: bool = field(default_factory=lambda: os.getenv("ENABLE_JWT", "true").lower() == "true")
    rate_limit_enabled: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    rate_limit_requests: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", 100)))
    rate_limit_period_seconds: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", 60)))


class Config:
    """Main configuration class for the Polymer Knowledge Graph system."""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    graph: GraphConfig = GraphConfig()
    api: APIConfig = APIConfig()
    logging: LoggingConfig = LoggingConfig()
    cache: CacheConfig = CacheConfig()
    polymers: PolymersConfig = PolymersConfig()
    security: SecurityConfig = SecurityConfig()
    
    # Application metadata
    app_name: str = "Polymer Knowledge Graph"
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    app_description: str = "A comprehensive knowledge graph system for polymer materials and properties"
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_environment()
        self._validate_config()
    
    def _load_environment(self) -> None:
        """Load environment-specific configuration."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        try:
            self.environment = Environment(env_str)
        except ValueError:
            self.environment = Environment.DEVELOPMENT
            logging.warning(f"Invalid environment '{env_str}', defaulting to development")
        
        # Re-initialize configs with environment
        self.database = DatabaseConfig()
        self.graph = GraphConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        self.cache = CacheConfig()
        self.polymers = PolymersConfig()
        self.security = SecurityConfig()
    
    def _validate_config(self) -> None:
        """Validate critical configuration values."""
        errors = []
        
        if not self.database.host:
            errors.append("Database host is required")
        
        if not self.graph.host:
            errors.append("Graph database host is required")
        
        if self.api.port < 1 or self.api.port > 65535:
            errors.append(f"Invalid API port: {self.api.port}")
        
        if len(self.security.secret_key) < 8 and self.environment == Environment.PRODUCTION:
            errors.append("Secret key must be at least 8 characters in production")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
            },
            "graph": {
                "backend": self.graph.backend,
                "host": self.graph.host,
                "port": self.graph.port,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
            },
        }
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.logging.level))
        
        formatter = logging.Formatter(self.logging.format)
        
        # Console handler
        if self.logging.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        os.makedirs(os.path.dirname(self.logging.output_file), exist_ok=True)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.logging.output_file,
            maxBytes=self.logging.max_file_size,
            backupCount=self.logging.backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global _config
    _config = Config()
    return _config
