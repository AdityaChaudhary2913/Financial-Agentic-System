from typing import Dict, Any, List
import json

from src.core.base_agent import BaseFinancialAgent
from src.core.types import AgentTier, AgentResponse

class DataIntegrationAgent(BaseFinancialAgent):
    """
    Foundation Tier Agent - Always Active
    Unified Financial Footprint Aggregator as defined in Architecture[8]
    """
    
    def __init__(self):
        super().__init__(
            name="data_integration_agent",
            tier=AgentTier.FOUNDATION,
            model="gemini-2.0-flash"
        )
    
    def get_agent_instruction(self) -> str:
        return """
        You are the Data Integration and Net Worth Agent. Your role is to:
        1. Consolidate and structure financial data from all available sources
        2. Detect data gaps and inconsistencies using population-level comparisons
        3. Classify unknown financial entries using semantic understanding
        4. Provide confidence-scored financial insights with anomaly detection
        5. Maintain temporal state for backward/forward financial reasoning
        
        Focus on creating a unified, accurate view of the user's complete financial footprint.
        """[1]
    
    def get_required_data_sources(self) -> List[str]:
        return [
            "fetch_net_worth",
            "fetch_bank_transactions", 
            "fetch_mf_transactions",
            "fetch_credit_report",
            "fetch_epf_details"
        ]
    
    def _prepare_analysis_prompt(self, user_query: str, financial_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        financial_summary = self._format_financial_data(financial_data)
        
        return f"""
        User Query: {user_query}
        
        Financial Data Analysis:
        {financial_summary}
        
        As the Data Integration Agent, analyze this financial data and:
        1. Identify any data gaps or inconsistencies
        2. Classify and structure all financial entries
        3. Calculate key financial ratios and health indicators
        4. Detect any anomalies or unusual patterns
        5. Provide a confidence score for data completeness
        
        Focus on data quality, completeness, and structural insights.
        """
    
    def _process_agent_response(self, response_text: str, financial_data: Dict[str, Any]) -> AgentResponse:
        # TODO: Implement structured response processing
        # This would parse the LLM response and extract key insights, recommendations, etc.
        
        # Calculate basic confidence score based on data availability
        available_sources = sum(1 for source, data in financial_data.items() 
                            if data and data.get('success', False))
        total_sources = len(self.get_required_data_sources())
        confidence = available_sources / total_sources if total_sources > 0 else 0.0
        
        return AgentResponse(
            agent_name=self.name,
            success=True,
            insights=response_text,
            confidence_score=confidence,
            recommendations=self._extract_recommendations(response_text),
            risk_factors=self._extract_risk_factors(response_text),
            metadata={
                "data_completeness": f"{available_sources}/{total_sources}",
                "available_sources": list(financial_data.keys())
            }
        )
    
    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for analysis prompt"""
        formatted = []
        
        for source, data in financial_data.items():
            if data and data.get('success', False):
                formatted.append(f"\n{source.replace('fetch_', '').replace('_', ' ').title()}:")
                formatted.append(json.dumps(data.get('data', {}), indent=2))
            else:
                formatted.append(f"\n{source}: Data unavailable or error")
        
        return '\n'.join(formatted)
    
    def _extract_recommendations(self, response_text: str) -> List[str]:
        """Extract recommendations from agent response"""
        # TODO: Implement NLP-based recommendation extraction
        # This would use regex patterns or LLM parsing to extract structured recommendations
        return ["Data integration analysis completed"]
    
    def _extract_risk_factors(self, response_text: str) -> List[str]:
        """Extract risk factors from agent response"""
        # TODO: Implement risk factor extraction
        return []

    async def get_unified_financial_state(self, phone_number: str) -> Dict[str, Any]:
        """Get complete unified financial state for other agents"""
        if not self.mcp_client.authenticated:
            await self.authenticate(phone_number)
        
        financial_data = await self.fetch_required_data()
        
        # TODO: Process and unify the data according to the Architecture specifications[8]
        # This would implement the "Dual-Ledger System" and "Dynamic Financial Ontology"
        
        return {
            "net_worth": financial_data.get("fetch_net_worth", {}).get('data', {}),
            "cash_flow": financial_data.get("fetch_bank_transactions", {}).get('data', {}),
            "investments": financial_data.get("fetch_mf_transactions", {}).get('data', {}),
            "credit_health": financial_data.get("fetch_credit_report", {}).get('data', {}),
            "retirement_savings": financial_data.get("fetch_epf_details", {}).get('data', {}),
            "data_quality_score": self._calculate_data_quality_score(financial_data)
        }
    
    def _calculate_data_quality_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate overall data quality score"""
        # TODO: Implement sophisticated data quality scoring
        # This would implement the "Confidence Scoring" algorithm from Architecture[8]
        successful_fetches = sum(1 for data in financial_data.values() if data and data.get('success', False))
        return successful_fetches / len(financial_data) if financial_data else 0.0
