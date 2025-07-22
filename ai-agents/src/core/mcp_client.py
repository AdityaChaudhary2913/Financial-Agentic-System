import asyncio
import aiohttp
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class MCPResponse:
    """Structured MCP response data"""
    data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    confidence_score: float = 1.0

class FiMCPClient:
    """
    Fi MCP client with connection pooling, error handling, and retry logic.
    Learned from your sample agent's authentication approach.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", max_connections: int = 10):
        self.base_url = base_url
        self.session_id = None
        self.authenticated = False
        self.max_connections = max_connections
        self.connection_pool = []
        self.active_connections = 0
        self.logger = logging.getLogger(__name__)
        
    async def authenticate(self, phone_number: str) -> bool:
        """Enhanced authentication with better error handling"""
        try:
            self.session_id = f"mcp-session-{uuid.uuid4()}"
            
            async with aiohttp.ClientSession() as session:
                # Step 1: Initiate authentication flow
                headers = {
                    "Content-Type": "application/json",
                    "Mcp-Session-Id": self.session_id
                }
                # Use net_worth as auth trigger
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_net_worth",
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

                # Step 2: Complete authentication
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
                        self.logger.info(f"Successfully authenticated for user: {phone_number}")
                        return True
                    else:
                        raise Exception(f"Login failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    async def call_tool_with_retry(self, tool_name: str, arguments: Optional[Dict] = None, max_retries: int = 3) -> MCPResponse:
        """Enhanced tool calling with retry logic and structured responses"""
        for attempt in range(max_retries):
            try:
                result = await self.call_tool(tool_name, arguments)
                return MCPResponse(data=result, success=True)
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to call {tool_name} after {max_retries} attempts: {e}")
                    return MCPResponse(data={}, success=False, error_message=str(e))
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def call_tool(self, tool_name: str, arguments: Optional[Dict] = None) -> Dict[str, Any]:
        """Core tool calling method from your sample implementation"""
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
                content = result.get("result", {}).get("content", [{}])[0]
                return json.loads(content.get("text", "{}"))

    async def get_available_tools(self) -> List[str]:
        """Fetch list of available MCP tools"""
        # TODO: Implement based on MCP server capabilities discovery
        # This would call the MCP server's tools/list method
        return [
            "fetch_net_worth",
            "fetch_credit_report", 
            "fetch_epf_details",
            "fetch_mf_transactions",
            "fetch_bank_transactions"
        ]
