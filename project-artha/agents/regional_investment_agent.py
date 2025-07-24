import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

class RegionalInvestmentAgent:
    def __init__(self):
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="regional_investment_agent",
            instruction=(
                "You are a real estate market analyst specializing in the Indian market. "
                "Your purpose is to answer questions about real estate trends, opportunities, and prices "
                "in specific Indian cities and regions using the google_search tool. Provide detailed, "
                "data-driven answers and cite your sources."
            ),
            tools=[google_search],
        )
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent, 
            app_name="regional_investments", 
            session_service=self.session_service
        )
        print("RegionalInvestmentAgent initialized.")

    async def get_real_estate_info(self, query: str) -> str:
        """Uses the web to answer a real estate market query."""
        session = await self.session_service.create_session(app_name="regional_investments", user_id="user_1")
        request_content = Content(role="user", parts=[Part(text=query)])
        response_text = ""

        print(f"\nExecuting real estate query: '{query}'")
        async for event in self.runner.run_async(
            user_id="user_1", 
            session_id=session.id,
            new_message=request_content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        return response_text or "Could not get real estate information at this time."

async def main():
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return

    regional_agent = RegionalInvestmentAgent()
    
    query = "What are the real estate investment opportunities and trends in the area between Chennai and Bangalore?"

    try:
        response = await regional_agent.get_real_estate_info(query)
        print("\n" + "="*60)
        print(f"QUERY: {query}")
        print("-"*60)
        print(f"RESPONSE: {response}")
        print("="*60)
    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
