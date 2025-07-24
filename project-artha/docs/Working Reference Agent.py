import asyncio
import aiohttp
import json
import uuid
import time
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

class FiMCPClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session_id = None
        self.authenticated = False

    async def authenticate(self, phone_number):
        """Complete 3-step authentication following your API documentation"""
        # Use same session ID format that worked in curl
        self.session_id = f"mcp-session-{uuid.uuid4()}"
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Get login URL (this is working in your curl)
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": self.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "fetch_bank_transactions",  # or any tool name
                    "arguments": {}
                }
            }
            
            async with session.post(
                f"{self.base_url}/mcp/stream", 
                headers=headers, 
                json=payload
            ) as response:
                result = await response.json()
                content = result.get("result", {}).get("content", [{}])[0]
                login_data = json.loads(content.get("text", "{}"))
                
                if login_data.get("status") != "login_required":
                    raise Exception("Authentication flow error")

            # Step 2: Authorize session using extracted session ID
            login_data = {
                "sessionId": self.session_id,
                "phoneNumber": phone_number
            }
            
            async with session.post(
                f"{self.base_url}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    self.authenticated = True
                    return True
                else:
                    raise Exception(f"Login failed: {response.status}")

    async def call_tool(self, tool_name, arguments=None):
        """Make authenticated tool call using JSON-RPC 2.0"""
        if not self.authenticated:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": self.session_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/mcp/stream",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                # Extract the actual data from JSON-RPC response
                content = result.get("result", {}).get("content", [{}])[0]
                return json.loads(content.get("text", "{}"))

class FinancialAgent:
    def __init__(self):
        self.mcp_client = FiMCPClient()
        self.setup_agent()

    def setup_agent(self):
        """Set up Google ADK agent with Gemini"""
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="financial_advisor",
            instruction="""
            You are a personal financial advisor. When users ask about their finances,
            analyze their financial data and provide personalized, actionable insights.
            Focus on practical advice for wealth building, risk management, and financial planning.
            """,
            tools=[]  # We'll handle MCP calls manually due to protocol specifics
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent, 
            app_name="financial_advisor", 
            session_service=self.session_service
        )

    async def get_financial_data(self, phone_number, data_types=None):
        """Fetch comprehensive financial data from MCP server"""
        if not self.mcp_client.authenticated:
            await self.mcp_client.authenticate(phone_number)
        
        if data_types is None:
            data_types = [
                "fetch_net_worth",
                "fetch_credit_report", 
                "fetch_epf",
                "fetch_mutual_funds",
                "fetch_bank_transactions"
            ]
        
        financial_data = {}
        
        for data_type in data_types:
            try:
                data = await self.mcp_client.call_tool(data_type)
                financial_data[data_type] = data
            except Exception as e:
                print(f"Warning: Could not fetch {data_type}: {e}")
                financial_data[data_type] = None
        
        return financial_data

    async def generate_insights(self, user_query, financial_data, user_id):
        """Generate personalized insights using Gemini via ADK - Fixed for current API"""
        financial_summary = self._format_financial_data(financial_data)
        
        prompt = f"""
        User Question: {user_query}
        
        Financial Data:
        {financial_summary}
        
        Based on this financial information, provide personalized, actionable advice.
        Consider the user's current financial position, potential risks, and opportunities for growth.
        """
        
        try:
            # Create ADK session
            session = await self.session_service.create_session(
                app_name="financial_advisor", 
                user_id=user_id
            )
            
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            response_text = ""
            
            # Updated: Compatible ADK event handling pattern
            async for event in self.runner.run_async(
                user_id=user_id, 
                session_id=session.id,
                new_message=content
            ):
                # Fixed: Use direct attribute access instead of deprecated methods
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content is not None:
                        try:
                            # Try multiple patterns for content extraction
                            content_obj = event.content
                            
                            # Pattern 1: Direct parts access
                            if hasattr(content_obj, 'parts') and content_obj.parts:
                                response_text = ''.join([
                                    part.text for part in content_obj.parts 
                                    if hasattr(part, 'text') and part.text
                                ])
                            
                            # Pattern 2: Get method with parts
                            elif hasattr(content_obj, 'get'):
                                inner_content = content_obj.get()
                                if hasattr(inner_content, 'parts') and inner_content.parts:
                                    response_text = ''.join([
                                        part.text for part in inner_content.parts 
                                        if hasattr(part, 'text') and part.text
                                    ])
                            
                            # Pattern 3: Direct text access
                            elif hasattr(content_obj, 'text'):
                                response_text = content_obj.text
                            
                            if response_text:
                                break
                                
                        except Exception as content_error:
                            print(f"Content extraction error: {content_error}")
                            continue
            
            return response_text if response_text else "I apologize, but I couldn't generate insights at the moment."
        
        except Exception as e:
            print(f"Debug: ADK error details: {e}")

    def _format_financial_data(self, financial_data):
        """Format financial data for Gemini prompt"""
        formatted = []
        
        for data_type, data in financial_data.items():
            if data:
                formatted.append(f"{data_type.replace('fetch_', '').replace('_', ' ').title()}:")
                formatted.append(json.dumps(data, indent=2))
                formatted.append("")
        
        return "\n".join(formatted)

async def main():
    """Main CLI application"""
    agent = FinancialAgent()
    
    print("🏦 Welcome to Fi Financial Advisor")
    print("=" * 50)
    
    while True:
        print("\n--- Authentication Required ---")
        phone_number = input("Enter your phone number (e.g., 1414141414): ").strip()
        
        if phone_number.lower() in ['quit', 'exit']:
            print("Goodbye! 👋")
            break
            
        try:
            print("🔐 Authenticating...")
            await agent.mcp_client.authenticate(phone_number)
            print("✅ Authentication successful!")
            
            # Main conversation loop
            while True:
                print(f"\n--- Logged in as {phone_number} ---")
                user_query = input("\nAsk me about your finances (or 'logout'/'quit'): ").strip()
                
                if user_query.lower() == 'logout':
                    agent.mcp_client.authenticated = False
                    break
                elif user_query.lower() in ['quit', 'exit']:
                    print("Goodbye! 👋")
                    return
                elif not user_query:
                    continue
                
                try:
                    print("📊 Fetching your financial data...")
                    financial_data = await agent.get_financial_data(phone_number)
                    print("✅ Financial data retrieved successfully!")
                    
                    print("🤖 Generating personalized insights...")
                    insights = await agent.generate_insights(
                        user_query, 
                        financial_data, 
                        phone_number
                    )
                    print("✅ Insights generated successfully!", insights)

                    print("\n" + "="*60)
                    print("📈 FINANCIAL INSIGHTS")
                    print("="*60)
                    print(insights)
                    print("="*60)
                    
                except Exception as e:
                    print(f"❌ Error processing your request: {e}")
                    
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("Please make sure:")
            print("- Fi MCP server is running (go run .)")
            print("- Phone number exists in test_data_dir/")

if __name__ == "__main__":
    asyncio.run(main())
