import os
import asyncio
import json
import uuid
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# Assuming the other agent files are in the same directory
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient
from agents.risk_profiling_agent import RiskProfilingAgent
from agents.cultural_events_agent import CulturalEventsAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.trust_transparency_agent import TrustTransparencyAgent
from agents.regional_investment_agent import RegionalInvestmentAgent
from agents.debt_management_agent import DebtManagementAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.illiquid_asset_agent import IlliquidAssetAgent

class FinancialAnalysisTool:
    """A tool that encapsulates the logic for financial analysis using specialized agents."""
    def __init__(self):
        self.mcp_client = FiMCPClient()
        self.data_agent = DataIntegrationAgent(self.mcp_client)
        self.risk_agent = RiskProfilingAgent()
        self.cultural_agent = CulturalEventsAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.trust_agent = TrustTransparencyAgent()
        self.regional_agent = RegionalInvestmentAgent()
        self.anomaly_agent = AnomalyDetectionAgent()
        self.debt_agent = DebtManagementAgent()
        self.illiquid_agent = IlliquidAssetAgent()
        print("FinancialAnalysisTool initialized with all required agents.")

    async def analyze_spending(self, user_id: str) -> str:
        """
        Analyzes the user's spending patterns based on their bank transactions.
        """
        print(f"Tool triggered: Analyzing spending for {user_id}")
        try:
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            if not bank_transactions or "error" in bank_transactions:
                return json.dumps({"error": "Bank transaction data is unavailable."})
            profile = self.risk_agent.analyze_spending_patterns(bank_transactions)
            return json.dumps(profile)
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {e}"})

    async def forecast_cultural_spending(self, user_id: str) -> str:
        """
        Provides a forecast for culturally significant expenses.
        """
        print(f"Tool triggered: Forecasting cultural spending for {user_id}")
        try:
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            if not bank_transactions or "error" in bank_transactions:
                return json.dumps({"error": "Bank transaction data is unavailable."})
            forecast = self.cultural_agent.forecast_cultural_expenses(bank_transactions)
            return json.dumps(forecast)
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {e}"})

    async def get_market_data(self, query: str) -> str:
        """
        Fetches real-time market data for a given query.
        """
        print(f"Tool triggered: Getting market data for '{query}'")
        try:
            market_data = await self.market_agent.get_market_info(query)
            return market_data
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {e}"})

    async def get_regional_investment_info(self, query: str) -> str:
        """Uses the web to answer a real estate market query."""
        print(f"Tool triggered: Getting regional investment info for '{query}'")
        try:
            info = await self.regional_agent.get_real_estate_info(query)
            return info
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    async def get_debt_summary(self, user_id: str) -> str:
        """
        Provides an intelligent debt summary with contextual insights and actionable recommendations.
        """
        print(f"Tool triggered: Getting intelligent debt summary for {user_id}")
        try:
            # Step 1: Get comprehensive financial data
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            credit_report = financial_data.get("fetch_credit_report")
            bank_transactions = financial_data.get("fetch_bank_transactions")
            net_worth = financial_data.get("fetch_net_worth")

            if not credit_report or "error" in credit_report:
                return "Credit report data is unavailable for debt analysis."
                
            # Step 2: Multi-agent intelligent analysis
            debt_analysis = self.debt_agent.analyze_debt_summary(credit_report, bank_transactions)
            
            # Step 3: Get behavioral insights from risk agent
            spending_behavior = None
            if bank_transactions and "error" not in bank_transactions:
                spending_behavior = self.risk_agent.analyze_spending_patterns(bank_transactions)
            
            # Step 4: Get market context for debt optimization
            market_context = await self.market_agent.get_market_info("current home loan interest rates India 2025")
            
            # Step 5: Generate intelligent insights
            intelligent_summary = self._synthesize_debt_intelligence(
                debt_analysis, spending_behavior, market_context, net_worth
            )
            
            # Step 6: Add transparency layer
            enriched_response = self.trust_agent.add_debt_analysis_explanations(intelligent_summary)
            
            return enriched_response
            
        except Exception as e:
            print(f"Error during intelligent debt summary: {e}")
            return f"An unexpected error occurred during debt analysis: {e}"


    async def explain_anomaly_detection_process(self, user_id: str) -> str:
        """
        Detects spending anomalies and explains the process to the user.

        Args:
            user_id: The user's phone number for authentication and data fetching.

        Returns:
            A string containing the explanation of the anomaly detection process.
        """
        print(f"Tool triggered: Explaining anomaly detection for {user_id}")
        try:
            # First, get the raw analysis
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            if not bank_transactions or "error" in bank_transactions:
                return "Could not retrieve bank transaction data to analyze."

            anomaly_data = self.anomaly_agent.detect_spending_anomalies(bank_transactions)

            # Now, get the explanation
            explanation = self.trust_agent.explain_anomaly_detection(anomaly_data)
            return explanation
        except Exception as e:
            print(f"Error during anomaly detection explanation: {e}")
            return f"An unexpected error occurred: {e}"

    async def get_risk_analysis_explanation(self, user_id: str) -> str:
        """
        Analyzes a user's spending and provides a human-readable explanation.
        """
        print(f"Tool triggered: Explaining risk analysis for {user_id}")
        try:
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not bank_transactions or "error" in bank_transactions:
                return "Could not retrieve bank transaction data to analyze."
                
            risk_profile = self.risk_agent.analyze_spending_patterns(bank_transactions)
            explanation = self.trust_agent.explain_risk_analysis(risk_profile)
            
            return explanation
            
        except Exception as e:
            return f"An unexpected error occurred: {e}"
        
    def _synthesize_debt_intelligence(self, debt_data, behavior_data, market_context, net_worth_data):
        """Synthesizes multi-agent insights into intelligent recommendations."""
        
        total_debt = debt_data.get('total_outstanding_debt', 0)
        credit_cards = debt_data.get('credit_cards', [])
        loans = debt_data.get('loans', [])
        
        # Intelligent analysis
        insights = []
        
        # Debt utilization intelligence
        if credit_cards:
            for card in credit_cards:
                utilization = card['current_balance'] / card['credit_limit'] * 100 if card['credit_limit'] > 0 else 0
                if utilization > 30:
                    insights.append(f"⚠️ Your {card['issuer']} card is {utilization:.1f}% utilized. High utilization affects credit score - consider paying down to under 30%.")
        
        # Behavioral correlation
        if behavior_data:
            weekend_ratio = behavior_data.get('weekend_weekday_spending_ratio', 0)
            if weekend_ratio > 1.2 and total_debt > 0:
                insights.append(f"💡 Your weekend spending is {weekend_ratio:.1f}x your weekday spending. Reducing discretionary weekend expenses could accelerate debt payoff by ~₹{total_debt * 0.1:,.0f} annually.")
        
        # Market intelligence integration
        if "interest rates" in market_context.lower():
            insights.append(f"📈 Market Intelligence: {market_context[:200]}... Consider refinancing if your loan rates are above current market rates.")
        
        return {
            "debt_summary": debt_data,
            "intelligent_insights": insights,
            "behavioral_correlation": behavior_data,
            "market_context": market_context
        }
    
    async def get_illiquid_asset_optimization(self, user_id: str) -> str:
        """
        Analyzes illiquid and dormant assets with optimization recommendations.
        """
        print(f"Tool triggered: Analyzing illiquid assets for {user_id}")
        try:
            financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
            
            analysis = self.illiquid_agent.analyze_illiquid_assets(financial_data)
            
            # Add transparency layer
            enriched_response = self.trust_agent.add_illiquid_asset_explanations(analysis)
            
            return enriched_response
            
        except Exception as e:
            print(f"Error during illiquid asset analysis: {e}")
            return f"An unexpected error occurred during illiquid asset analysis: {e}"
    

class CoreFinancialAdvisorAgent:
    def __init__(self):
        self.analysis_tool = FinancialAnalysisTool()
        self.trust_agent = TrustTransparencyAgent()
        
        # Define the high-level agent using Google ADK
        # Update the agent instruction in CoreFinancialAdvisorAgent.__init__

        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="core_financial_advisor",
            instruction=(
                "You are an intelligent financial advisor orchestrating a team of AI specialists. "
                "Your role is to provide comprehensive, contextual financial insights by coordinating "
                "multiple agents and synthesizing their expertise into actionable advice.\n\n"
                
                "INTELLIGENCE PRINCIPLES:\n"
                "• Always provide context and 'why' behind every recommendation\n"
                "• Correlate behavioral patterns with financial data\n"
                "• Identify optimization opportunities across all financial aspects\n"
                "• Offer specific, actionable steps with quantified impacts\n"
                "• Highlight risks and opportunities proactively\n\n"
                "• Optimize illiquid and dormant assets for better returns\n\n"
                
                "When processing requests:\n"
                "1. Extract user_id from the prompt\n"
                "2. Use multiple agents to gather comprehensive insights\n"
                "3. Synthesize findings into intelligent recommendations\n"
                "4. Always explain your reasoning and cite agent contributions\n"
                "5. Provide immediate actions the user can take\n\n"
                "6. Consider liquidity optimization and asset monetization opportunities\n\n"
                
                "Your responses should demonstrate the collective intelligence of all agents working together."
            ),
            tools=[
                self.analysis_tool.analyze_spending, 
                self.analysis_tool.forecast_cultural_spending, 
                self.analysis_tool.get_market_data,
                self.analysis_tool.get_regional_investment_info,
                self.analysis_tool.get_debt_summary,
                self.analysis_tool.get_risk_analysis_explanation,
                self.analysis_tool.explain_anomaly_detection_process,
                self.analysis_tool.get_illiquid_asset_optimization
            ]
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent, 
            app_name="project_artha", 
            session_service=self.session_service
        )
        print("CoreFinancialAdvisorAgent initialized with ADK Runner.")

    async def process_query(self, user_query: str, user_id: str) -> str:
        """Processes a user's query using the ADK agent and its tools."""
        session = await self.session_service.create_session(app_name="project_artha", user_id=user_id)
        
        # Prepend the user_id to the query to make it available to the LLM
        prompt_with_context = f"User ID: {user_id}\n\nQuery: {user_query}"
        request_content = Content(role="user", parts=[Part(text=prompt_with_context)])
        response_text = ""

        print(f"\nProcessing query for {user_id}: '{user_query}'")
        async for event in self.runner.run_async(
            user_id=user_id, 
            session_id=session.id,
            new_message=request_content
        ):
            if event.is_final_response():
                if event.content is not None and hasattr(event.content, 'parts') and event.content.parts:
                    response_text = event.content.parts[0].text
                else:
                    response_text = "No response content available."
                break
        
        # Pass the response to the Trust and Transparency Agent for enrichment
        enriched_response = self.trust_agent.add_financial_explanations(response_text if response_text is not None else "")

        return enriched_response or "I could not process your request at this time."

async def main():
    import sys
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python -m agents.core_financial_advisor_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]
    advisor_agent = CoreFinancialAdvisorAgent()

    # This is the query that will trigger the debt summary tool
    # query = "Can I afford a 3 BHK home in Greater Noida around Pari Chowk? What are my current debts and how can I optimize them?"    
    query = "Help me find good ways to optimize my assets, especially illiquid ones."
    try:
        final_response = await advisor_agent.process_query(user_query=query, user_id=phone_number)
        
        print("\n" + "="*60)
        print("🤖 CORE FINANCIAL ADVISOR RESPONSE")
        print("="*60)
        print(final_response)
        print("="*60)

    except Exception as e:
        print(f"\n❌ A critical error occurred in the main loop: {e}")

if __name__ == "__main__":
    asyncio.run(main())