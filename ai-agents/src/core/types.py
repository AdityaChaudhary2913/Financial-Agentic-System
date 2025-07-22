from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

class AgentTier(Enum):
    FOUNDATION = "foundation"
    INTELLIGENCE = "intelligence"
    STRATEGIC = "strategic"

class AgentState(Enum):
    INITIALIZED = "initialized"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    INACTIVE = "inactive"

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    agent_name: str
    success: bool
    insights: str
    confidence_score: float
    recommendations: List[str]
    risk_factors: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class UserContext:
    """User context for agent operations"""
    user_id: str
    phone_number: str
    session_id: str
    preferences: Dict[str, Any]
    financial_goals: List[str]
    risk_tolerance: str
    
@dataclass
class AgentCoordinationMessage:
    """Message format for inter-agent communication"""
    sender_agent: str
    recipient_agent: str
    message_type: str
    data: Dict[str, Any]
    priority: int = 1
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
