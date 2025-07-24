import asyncio
import os
import json
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

class MarketIntelligenceAgent:
    def __init__(self):
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="market_intelligence_agent",
            instruction=(
                "You are a world-class financial market analyst. Your sole purpose is to "
                "accurately answer questions about financial markets by using the provided "
                "google_search tool. Provide concise, data-driven answers based on the search results. "
                "Cite your sources by providing the URL from the search results."
            ),
            tools=[google_search],
        )
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent, 
            app_name="market_intelligence", 
            session_service=self.session_service
        )
        print("MarketIntelligenceAgent initialized.")

    async def get_market_info(self, query: str) -> str:
        """Uses the web to answer a financial market query."""
        session = await self.session_service.create_session(app_name="market_intelligence", user_id="user_1")
        request_content = Content(role="user", parts=[Part(text=query)])
        response_text = ""

        print(f"\nExecuting market query: '{query}'")
        async for event in self.runner.run_async(
            user_id="user_1", 
            session_id=session.id,
            new_message=request_content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        return response_text or "Could not get market information at this time."

async def main():
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return

    market_agent = MarketIntelligenceAgent()
    
    queries = [
        "What is the current price of 24K gold per gram in India in INR?",
        "What is the current value of the NIFTY 50 index?",
        "What are good places to invest around Greater Noida Sector CHI-4?"
    ]

    for query in queries:
        try:
            response = await market_agent.get_market_info(query)
            print("\n" + "="*60)
            print(f"QUERY: {query}")
            print("-"*60)
            print(f"RESPONSE: {response}")
            print("="*60)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())