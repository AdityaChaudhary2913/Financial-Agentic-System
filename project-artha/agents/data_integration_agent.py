import asyncio
import aiohttp
import json
import uuid
import time

class ServiceUnavailableError(Exception):
    """Custom exception for service timeouts."""
    pass

async def call_with_circuit_breaker(func, *args, **kwargs):
    try:
        return await asyncio.wait_for(func(*args, **kwargs), timeout=30)
    except asyncio.TimeoutError:
        raise ServiceUnavailableError("Fi MCP service timeout")
    except Exception as e:
        # In a real-world scenario, you might want to log this error.
        # For now, we'll just re-raise it.
        raise

class FiMCPClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session_id = None
        self.authenticated = False

    async def authenticate(self, phone_number):
        self.session_id = f"mcp-session-{uuid.uuid4()}"
        
        # Wrap the authentication steps with the circuit breaker
        async def _authenticate_steps():
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Mcp-Session-Id": self.session_id
                }
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "fetch_net_worth", "arguments": {}}
                }
                async with session.post(f"{self.base_url}/mcp/stream", headers=headers, json=payload) as response:
                    result = await response.json()
                    content = result.get("result", {}).get("content", [{}])[0]
                    login_data = json.loads(content.get("text", "{}"))
                    if login_data.get("status") != "login_required":
                        raise Exception("Authentication flow error: Did not get login_required status.")

                login_form_data = {
                    "sessionId": self.session_id,
                    "phoneNumber": phone_number
                }
                async with session.post(f"{self.base_url}/login", data=login_form_data, headers={"Content-Type": "application/x-www-form-urlencoded"}) as response:
                    if response.status == 200:
                        self.authenticated = True
                        return True
                    else:
                        raise Exception(f"Login failed with status: {response.status}")
        
        return await call_with_circuit_breaker(_authenticate_steps)

    async def call_tool(self, tool_name, arguments=None):
        if not self.authenticated:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        async def _call_tool_steps():
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments or {}}
            }
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": self.session_id
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/mcp/stream", headers=headers, json=payload) as response:
                    result = await response.json()
                    content = result.get("result", {}).get("content", [{}])[0]
                    return json.loads(content.get("text", "{}"))
        
        return await call_with_circuit_breaker(_call_tool_steps)

class DataIntegrationAgent:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.data_cache = {}
        self.last_sync = {}

    async def get_comprehensive_data(self, user_id, force_refresh=False):
        """
        Fetches all available financial data for a user from the Fi MCP server.
        Implements caching to avoid redundant API calls.
        """
        cache_age = time.time() - self.last_sync.get(user_id, 0)
        if not force_refresh and user_id in self.data_cache and cache_age < 3600: # 1 hour cache
            print("Returning cached data.")
            return self.data_cache[user_id]

        print("Fetching fresh data from Fi MCP server...")
        if not self.mcp_client.authenticated:
            await self.mcp_client.authenticate(user_id)

        data_sources = [
            "fetch_net_worth",
            "fetch_credit_report",
            "fetch_epf_details",
            "fetch_mf_transactions",
            "fetch_bank_transactions",
            "fetch_stock_transactions"
        ]
        
        user_data = {}
        for source in data_sources:
            try:
                print(f"  - Fetching {source}...")
                data = await self.mcp_client.call_tool(source)
                user_data[source] = data
            except Exception as e:
                print(f"  - Error fetching {source}: {e}")
                user_data[source] = {"error": str(e), "available": False}
        
        self.data_cache[user_id] = user_data
        self.last_sync[user_id] = time.time()
        return user_data

async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python data_integration_agent.py <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    
    print("🚀 Initializing Data Integration Agent...")
    
    try:
        comprehensive_data = await data_agent.get_comprehensive_data(phone_number)
        print("\n✅ Successfully fetched comprehensive financial data!")
        
        print("\n" + "="*50)
        print("DATA SUMMARY")
        print("="*50)
        for key, value in comprehensive_data.items():
            status = "✅ Fetched" if "error" not in value else "❌ Error"
            print(f"- {key}: {status}")
        print("="*50)

        # Optionally, print the full data for inspection
        # print("\n" + json.dumps(comprehensive_data, indent=2))

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())