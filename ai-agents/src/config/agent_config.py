from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    model: str
    tier: str
    max_retries: int = 3
    timeout: int = 30
    confidence_threshold: float = 0.7

# Agent configurations based on Architecture specification[8]
AGENT_CONFIGS = {
    "data_integration": AgentConfig(
        name="data_integration_agent",
        model="gemini-2.0-flash",
        tier="foundation",
        max_retries=3,
        confidence_threshold=0.8
    ),
    "core_advisor": AgentConfig(
        name="core_financial_advisor",
        model="gemini-2.0-flash", 
        tier="foundation",
        max_retries=2,
        confidence_threshold=0.85
    ),
    "risk_profiling": AgentConfig(
        name="risk_profiling_agent",
        model="gemini-2.0-flash",
        tier="intelligence", 
        max_retries=3,
        confidence_threshold=0.75
    )
    # TODO: Add configurations for all 10 agents
}

# MCP Configuration
MCP_CONFIG = {
    "base_url": "http://localhost:8080",
    "timeout": 30,
    "max_connections": 10,
    "retry_attempts": 3,
    "retry_delay": 2
}

# System Configuration  
SYSTEM_CONFIG = {
    "consensus_threshold": 0.7,
    "max_parallel_agents": 5,
    "session_timeout": 3600,  # 1 hour
    "log_level": "INFO"
}
