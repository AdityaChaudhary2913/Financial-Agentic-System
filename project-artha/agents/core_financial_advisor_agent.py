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
from agents.anomaly_detection_agent import AnomalyDetectionAgent

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

class CoreFinancialAdvisorAgent:
    def __init__(self):
        self.analysis_tool = FinancialAnalysisTool()
        self.trust_agent = TrustTransparencyAgent()
        
        # Define the high-level agent using Google ADK
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="core_financial_advisor",
            instruction=(
                "You are a core financial advisor. Your job is to understand user requests "
                "and use the available tools to provide them with financial insights. "
                "The user ID will be provided in the prompt. You must extract this ID and use it "
                "when calling any tools that require a 'user_id'."
            ),
            tools=[
                self.analysis_tool.analyze_spending, 
                self.analysis_tool.forecast_cultural_spending, 
                self.analysis_tool.get_market_data,
                self.analysis_tool.get_regional_investment_info,
                self.analysis_tool.explain_anomaly_detection_process
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
                response_text = event.content.parts[0].text
                break
        
        # Pass the response to the Trust and Transparency Agent for enrichment
        enriched_response = self.trust_agent.add_financial_explanations(response_text)

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

    # This is the complex query that will trigger multiple agents
    query = "First, explain my spending habits to me in simple terms. Then, tell me about real estate investment opportunities in the area between Chennai and Bangalore."
    
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