# tools/fi_mcp_connector.py

import asyncio
import aiohttp
import json
import uuid
import time
import logging
from typing import Dict, Any, Optional

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProductionFiMCPClient:
    """
    Production-ready Fi MCP client with authentication, caching, and error handling.
    This is based on the Fi MCP Development Server Manual and the provided working reference agent.
    """
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.authenticated = False
        self.response_cache: Dict[str, Any] = {}
        logging.info("ProductionFiMCPClient initialized.")
    
    # def reset(self):                                                                                   
    #     """Resets the client's authentication state and session ID."""                                 
    #     self.authenticated = False                                                                     
    #     self.session_id = None                                                                         
    #     logging.info("ProductionFiMCPClient state has been reset.") 

    async def authenticate(self, phone_number: str) -> bool:
        """
        Performs the complete 3-step authentication with the Fi MCP server.
        Args:
            phone_number: The user's phone number corresponding to a test_data_dir directory.
        Returns:
            True if authentication is successful, False otherwise.
        """
        if self.authenticated:
            return True

        self.session_id = f"mcp-session-{uuid.uuid4()}"
        logging.info(f"Attempting authentication for {phone_number} with session ID {self.session_id}")

        async with aiohttp.ClientSession() as session:
            # Step 1: Initiate the session to get the login requirement
            headers = {"Content-Type": "application/json", "Mcp-Session-Id": self.session_id}
            payload = {
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "fetch_net_worth", "arguments": {}}
            }
            try:
                async with session.post(f"{self.base_url}/mcp/stream", headers=headers, json=payload) as response:
                    if response.status != 200:
                        logging.error(f"Auth Step 1 Failed: HTTP {response.status}")
                        return False
                    result = await response.json()
                    content = result.get("result", {}).get("content", [{}])[0]
                    login_data = json.loads(content.get("text", "{}"))
                    if login_data.get("status") != "login_required":
                        logging.error("Authentication flow error: Did not receive 'login_required' status.")
                        return False

                # Step 2: Submit the phone number to authorize the session
                login_payload = {"sessionId": self.session_id, "phoneNumber": phone_number}
                async with session.post(f"{self.base_url}/login", data=login_payload) as login_response:
                    if login_response.status == 200:
                        self.authenticated = True
                        logging.info(f"✅ Authentication successful for {phone_number}.")
                        return True
                    else:
                        logging.error(f"Auth Step 2 Failed: HTTP {login_response.status}")
                        self.authenticated = False
                        return False
            except aiohttp.ClientConnectorError as e:
                logging.error(f"Connection Error: Could not connect to the Fi MCP server at {self.base_url}. Is it running?")
                return False

    async def call_tool(self, tool_name: str, arguments: Optional[Dict] = None, cache_ttl: int = 300) -> Dict[str, Any]:
        """
        Makes an authenticated tool call to the Fi MCP server with caching.
        Args:
            tool_name: The name of the MCP tool to call (e.g., 'fetch_credit_report').
            arguments: A dictionary of arguments for the tool.
            cache_ttl: Time-to-live for the cache in seconds.
        Returns:
            A dictionary containing the tool's response data.
        """
        if not self.authenticated:
            raise Exception("Client is not authenticated. Call authenticate() first.")

        cache_key = f"{self.session_id}:{tool_name}:{json.dumps(arguments or {}, sort_keys=True)}"
        if cache_key in self.response_cache:
            cache_entry = self.response_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < cache_ttl:
                logging.info(f"CACHE HIT for tool: {tool_name}")
                return cache_entry['data']

        logging.info(f"API CALL for tool: {tool_name}")
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}}
        }
        headers = {"Content-Type": "application/json", "Mcp-Session-Id": self.session_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/mcp/stream", headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Tool call failed with status {response.status}: {await response.text()}")
                result = await response.json()
                content = result.get("result", {}).get("content", [{}])[0]
                data = json.loads(content.get("text", "{}"))

                # Cache the successful response
                self.response_cache[cache_key] = {'data': data, 'timestamp': time.time()}
                return data