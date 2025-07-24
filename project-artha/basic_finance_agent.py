import asyncio
import aiohttp
import json
import uuid
import sys

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

class BasicFinanceAgent:
    def __init__(self):
        self.mcp_client = FiMCPClient("http://localhost:8080")
        
    async def authenticate_and_fetch(self, phone_number):
        await self.mcp_client.authenticate(phone_number)
        net_worth_data = await self.mcp_client.call_tool("fetch_net_worth")
        
        # Extract the total net worth value
        total_net_worth = net_worth_data.get("netWorthResponse", {}).get("totalNetWorthValue", {}).get("units", 0)
        
        return f"Net worth: ₹{int(total_net_worth):,}"

async def main():
    """Main CLI application"""
    if len(sys.argv) != 2:
        print("Usage: python basic_finance_agent.py <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]
    agent = BasicFinanceAgent()
    
    print("🏦 Welcome to Project Artha - Basic Finance Agent")
    print("=" * 50)
    
    try:
        print(f"🔐 Authenticating and fetching net worth for {phone_number}...")
        net_worth_summary = await agent.authenticate_and_fetch(phone_number)
        print("✅ Success!")
        print(net_worth_summary)
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())