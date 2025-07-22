from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .mcp_client import FiMCPClient, MCPResponse
from .types import AgentTier, AgentState, AgentResponse

class BaseFinancialAgent(ABC):
    """
    Abstract base class for all financial agents in the system.
    Provides common functionality and enforces consistent interface.
    """
    
    def __init__(self, name: str, tier: AgentTier, model: str = "gemini-2.0-flash"):
        self.name = name
        self.tier = tier
        self.model = model
        self.state = AgentState.INITIALIZED
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Initialize MCP client
        self.mcp_client = FiMCPClient()
        
        # Setup ADK components
        self.session_service = InMemorySessionService()
        self.agent = None
        self.runner = None
        
        self._setup_agent()
    
    def _setup_agent(self):
        """Setup Google ADK agent with proper configuration"""
        try:
            self.agent = LlmAgent(
                model=self.model,
                name=self.name,
                instruction=self.get_agent_instruction(),
                tools=[]  # MCP tools handled separately for flexibility
            )
            
            self.runner = Runner(
                agent=self.agent,
                app_name=f"{self.name}_app",
                session_service=self.session_service
            )
            
            self.state = AgentState.READY
            self.logger.info(f"Agent {self.name} initialized successfully")
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Failed to setup agent {self.name}: {e}")
    
    @abstractmethod
    def get_agent_instruction(self) -> str:
        """Return the system instruction for this agent"""
        pass
    
    @abstractmethod
    def get_required_data_sources(self) -> List[str]:
        """Return list of MCP data sources this agent requires"""
        pass
    
    async def authenticate(self, phone_number: str) -> bool:
        """Authenticate with Fi MCP server"""
        return await self.mcp_client.authenticate(phone_number)
    
    async def fetch_required_data(self) -> Dict[str, MCPResponse]:
        """Fetch all data sources required by this agent"""
        data = {}
        required_sources = self.get_required_data_sources()
        
        for source in required_sources:
            try:
                result = await self.mcp_client.call_tool_with_retry(source)
                data[source] = result
                self.logger.debug(f"Fetched {source}: {'Success' if result.success else 'Failed'}")
            except Exception as e:
                self.logger.error(f"Failed to fetch {source}: {e}")
                data[source] = MCPResponse(data={}, success=False, error_message=str(e))
        
        return data
    
    async def analyze(self, user_query: str, financial_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResponse:
        """Core analysis method that each agent must implement"""
        try:
            # Prepare analysis prompt
            prompt = self._prepare_analysis_prompt(user_query, financial_data, context)
            
            # Create session for this analysis
            session = await self.session_service.create_session(
                app_name=f"{self.name}_app",
                user_id=context.get("user_id", "unknown")
            )
            
            # Generate insights using ADK
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            response_text = await self._generate_adk_response(session, content, context.get("user_id"))
            
            # Process and structure the response
            return self._process_agent_response(response_text, financial_data)
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {self.name}: {e}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                insights="Analysis failed due to technical error",
                confidence_score=0.0,
                recommendations=[],
                risk_factors=[f"Technical error: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    async def _generate_adk_response(self, session, content, user_id: str) -> str:
        """Generate response using ADK runner - improved from your sample"""
        response_text = ""
        
        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content is not None:
                        content_obj = event.content
                        
                        # Multiple extraction patterns for robustness
                        if hasattr(content_obj, 'parts') and content_obj.parts:
                            response_text = ''.join([
                                part.text for part in content_obj.parts 
                                if hasattr(part, 'text') and part.text
                            ])
                        elif hasattr(content_obj, 'get'):
                            inner_content = content_obj.get()
                            if hasattr(inner_content, 'parts') and inner_content.parts:
                                response_text = ''.join([
                                    part.text for part in inner_content.parts 
                                    if hasattr(part, 'text') and part.text
                                ])
                        elif hasattr(content_obj, 'text'):
                            response_text = content_obj.text
                        
                        if response_text:
                            break
                            
        except Exception as e:
            self.logger.error(f"ADK response generation failed: {e}")
            response_text = f"Error generating response: {str(e)}"
        
        return response_text or "Unable to generate response at this time."
    
    @abstractmethod
    def _prepare_analysis_prompt(self, user_query: str, financial_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Prepare the analysis prompt specific to this agent"""
        pass
    
    @abstractmethod
    def _process_agent_response(self, response_text: str, financial_data: Dict[str, Any]) -> AgentResponse:
        """Process the raw response into structured AgentResponse"""
        pass
