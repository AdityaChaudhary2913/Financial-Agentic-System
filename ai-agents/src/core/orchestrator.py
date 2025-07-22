import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_agent import BaseFinancialAgent
from .types import UserContext, AgentResponse, AgentCoordinationMessage
from src.agents.foundation.data_integration_agent import DataIntegrationAgent
from src.agents.foundation.core_financial_advisor import CoreFinancialAdvisorAgent
from src.agents.intelligence.risk_profiling_agent import RiskProfilingAgent

class MultiAgentOrchestrator:
    """
    Central orchestrator for the 10-agent financial AI system
    Manages agent lifecycle, coordination, and consensus building
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseFinancialAgent] = {}
        self.logger = logging.getLogger(__name__)
        self.message_queue = []
        self.consensus_threshold = 0.7
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents in the system"""
        try:
            # Foundation Tier - Always Active
            self.agents["data_integration"] = DataIntegrationAgent()
            self.agents["core_advisor"] = CoreFinancialAdvisorAgent()
            # TODO: Add TrustTransparencyAgent()
            
            # Intelligence Tier - Query Triggered
            self.agents["risk_profiling"] = RiskProfilingAgent()
            # TODO: Add AnomalyDetectionAgent(), RegionalInvestmentAgent()
            
            # Strategic Tier - Goal Oriented
            # TODO: Add all strategic agents as defined in Architecture[8]
            
            self.logger.info(f"Initialized {len(self.agents)} agents successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def authenticate_all_agents(self, phone_number: str) -> bool:
        """Authenticate all agents with Fi MCP"""
        authentication_results = []
        
        for name, agent in self.agents.items():
            try:
                result = await agent.authenticate(phone_number)
                authentication_results.append(result)
                self.logger.info(f"Agent {name} authentication: {'Success' if result else 'Failed'}")
            except Exception as e:
                self.logger.error(f"Authentication failed for {name}: {e}")
                authentication_results.append(False)
        
        return all(authentication_results)
    
    async def process_user_query(self, user_query: str, context: UserContext) -> Dict[str, Any]:
        """
        Main entry point for processing user queries through the multi-agent system
        """
        try:
            self.logger.info(f"Processing query: {user_query[:100]}...")
            
            # Step 1: Authenticate all agents
            auth_success = await self.authenticate_all_agents(context.phone_number)
            if not auth_success:
                return {"error": "Authentication failed for one or more agents"}
            
            # Step 2: Get unified financial data from Data Integration Agent
            financial_data = await self.agents["data_integration"].get_unified_financial_state(
                context.phone_number
            )
            
            # Step 3: Determine which agents to activate based on query analysis
            active_agents = await self._determine_active_agents(user_query, financial_data)
            
            # Step 4: Execute parallel agent analysis
            agent_responses = await self._execute_parallel_analysis(
                user_query, financial_data, context, active_agents
            )
            
            # Step 5: Build consensus from agent responses
            consensus = await self._build_consensus(agent_responses, context)
            
            # Step 6: Generate final unified response
            final_response = await self._generate_unified_response(
                user_query, agent_responses, consensus, context
            )
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return {
                "error": f"Processing failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _determine_active_agents(self, user_query: str, financial_data: Dict[str, Any]) -> List[str]:
        """Determine which agents should be activated based on query analysis"""
        # TODO: Implement intelligent agent selection based on query type and content
        # This would implement the "Agent Routing" logic from Architecture[8]
        
        # For now, activate core agents for demonstration
        active_agents = ["data_integration", "core_advisor"]
        
        # Simple keyword-based routing (to be enhanced with LLM-based routing)
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["risk", "invest", "sip", "market"]):
            active_agents.append("risk_profiling")
        
        # TODO: Add more sophisticated routing logic
        
        return active_agents
    
    async def _execute_parallel_analysis(self, 
                                       user_query: str, 
                                       financial_data: Dict[str, Any],
                                       context: UserContext,
                                       active_agents: List[str]) -> Dict[str, AgentResponse]:
        """Execute analysis across multiple agents in parallel"""
        
        analysis_tasks = {}
        context_dict = {
            "user_id": context.user_id,
            "preferences": context.preferences,
            "risk_tolerance": context.risk_tolerance
        }
        
        # Create analysis tasks for each active agent
        for agent_name in active_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                task = agent.analyze(user_query, financial_data, context_dict)
                analysis_tasks[agent_name] = task
        
        # Execute all analyses in parallel
        results = await asyncio.gather(*analysis_tasks.values(), return_exceptions=True)
        
        # Map results back to agent names
        agent_responses = {}
        for agent_name, result in zip(analysis_tasks.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent_name} analysis failed: {result}")
                agent_responses[agent_name] = AgentResponse(
                    agent_name=agent_name,
                    success=False,
                    insights="Analysis failed",
                    confidence_score=0.0,
                    recommendations=[],
                    risk_factors=[f"Agent error: {str(result)}"],
                    metadata={"error": str(result)}
                )
            else:
                agent_responses[agent_name] = result
        
        return agent_responses
    
    async def _build_consensus(self, 
                             agent_responses: Dict[str, AgentResponse], 
                             context: UserContext) -> Dict[str, Any]:
        """Build consensus from agent responses using weighted voting"""
        # TODO: Implement sophisticated consensus algorithm from Architecture[8]
        # This would implement "Weighted Expertise Voting" and "Conflict Resolution"
        
        successful_responses = {name: resp for name, resp in agent_responses.items() if resp.success}
        
        if not successful_responses:
            return {"consensus_reached": False, "reason": "No successful agent responses"}
        
        # Simple consensus for now - to be enhanced with sophisticated algorithms
        avg_confidence = sum(resp.confidence_score for resp in successful_responses.values()) / len(successful_responses)
        all_recommendations = []
        all_risks = []
        
        for response in successful_responses.values():
            all_recommendations.extend(response.recommendations)
            all_risks.extend(response.risk_factors)
        
        return {
            "consensus_reached": avg_confidence >= self.consensus_threshold,
            "overall_confidence": avg_confidence,
            "unified_recommendations": list(set(all_recommendations)),
            "unified_risks": list(set(all_risks)),
            "participating_agents": list(successful_responses.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _generate_unified_response(self, 
                                       user_query: str,
                                       agent_responses: Dict[str, AgentResponse],
                                       consensus: Dict[str, Any],
                                       context: UserContext) -> Dict[str, Any]:
        """Generate final unified response combining all agent insights"""
        
        return {
            "user_query": user_query,
            "unified_insights": self._synthesize_insights(agent_responses),
            "recommendations": consensus.get("unified_recommendations", []),
            "risk_factors": consensus.get("unified_risks", []),
            "confidence_score": consensus.get("overall_confidence", 0.0),
            "consensus_reached": consensus.get("consensus_reached", False),
            "agent_breakdown": {
                name: {
                    "success": resp.success,
                    "confidence": resp.confidence_score,
                    "key_insights": resp.insights[:200] + "..." if len(resp.insights) > 200 else resp.insights
                }
                for name, resp in agent_responses.items()
            },
            "metadata": {
                "active_agents": list(agent_responses.keys()),
                "processing_time": "calculated_processing_time",  # TODO: Implement timing
                "data_sources_used": "list_of_mcp_sources",  # TODO: Track data sources
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _synthesize_insights(self, agent_responses: Dict[str, AgentResponse]) -> str:
        """Synthesize insights from all successful agent responses"""
        successful_insights = [
            f"**{resp.agent_name.replace('_', ' ').title()}**: {resp.insights}"
            for resp in agent_responses.values() 
            if resp.success and resp.insights
        ]
        
        return "\n\n".join(successful_insights) if successful_insights else "No insights generated."
