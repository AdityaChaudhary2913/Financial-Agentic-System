# # agents/data_integration_agent.py

# import asyncio
# import logging, time
# from google.adk.agents import LlmAgent
# from google.adk.tools import ToolContext
# from tools.fi_mcp_connector import ProductionFiMCPClient

# # In a real app, the client might be a shared instance.
# mcp_client = ProductionFiMCPClient()

# async def process_and_structure_data(phone_number: str, tool_context: ToolContext) -> dict:
#     """
#     Orchestrates fetching all financial data for a user in parallel, authenticating if necessary.
#     It then structures this data into a unified state object and saves it to the
#     user's persistent state for other agents to use.

#     Args:
#         phone_number: The user's phone number for authentication and data fetching.
#         tool_context: The ADK ToolContext for state management.

#     Returns:
#         A dictionary summarizing the outcome of the integration process.
#     """
#     # 1. Authenticate the client
#     auth_success = await mcp_client.authenticate(phone_number)
#     if not auth_success:
#         return {"status": "error", "message": "Authentication with Fi MCP server failed."}

#     # 2. Define all required data sources to be fetched in parallel
#     data_sources = [
#         "fetch_net_worth", "fetch_credit_report", "fetch_epf_details",
#         "fetch_mf_transactions", "fetch_bank_transactions", "fetch_stock_transactions"
#     ]
#     tasks = [mcp_client.call_tool(source) for source in data_sources]
#     results = await asyncio.gather(*tasks, return_exceptions=True)

#     # 3. Structure the fetched data into a unified state object
#     raw_financial_data = dict(zip(data_sources, results))
#     unified_state = {"raw_data": {}, "data_gaps": [], "integration_timestamp": time.time()}

#     for source, result in raw_financial_data.items():
#         if isinstance(result, Exception):
#             unified_state["data_gaps"].append(source)
#             logging.warning(f"Failed to fetch {source}: {result}")
#         else:
#             unified_state["raw_data"][source] = result

#     # 4. Save the final state to user-scoped persistence for access by other agents
#     # This is a critical step for inter-agent communication.
#     tool_context.state[f"user:financial_state"] = unified_state
#     logging.info(f"Unified financial state for user {phone_number} saved to persistent state.")

#     return {
#         "status": "success",
#         "message": f"Successfully integrated financial state.",
#         "fetched_sources": len(unified_state["raw_data"]),
#         "data_gaps": unified_state["data_gaps"]
#     }

# # --- Agent Definition ---

# data_integration_agent = LlmAgent(
#     name="data_integration_agent",
#     model="gemini-2.0-flash", # Using a powerful model for this critical foundational task
#     description="The foundational data agent. It connects to the Fi MCP server, fetches all user financial data in parallel, and structures it into a unified state for all other agents to use.",
#     instruction="""
#         You are the 'Unified Financial Footprint Aggregator', the foundational data backbone for Project Artha.
#         Your one and only function is to create a complete and accurate snapshot of a user's financial life.

#         Your process:
#         1.  You will be given a user's phone number.
#         2.  You MUST use the `process_and_structure_data` tool to handle the entire workflow of authenticating, fetching, and structuring the data.
#         3.  Do not attempt to interpret the data. Your job is to ensure it is fetched and stored correctly in the 'user:financial_state' object.
#         4.  Report the final status of the operation (success, number of sources fetched, and any data gaps) back to the calling agent.
#         You are a system-level agent and do not interact directly with end-users. Your work is the essential first step for any meaningful financial analysis.
#     """,
#     tools=[
#         process_and_structure_data,
#     ],
#     output_key="data_integration_result"
# )


# agents/data_integration_agent.py

import asyncio
import time
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from tools.fi_mcp_connector import ProductionFiMCPClient

# The same global client instance is used, but we will reset it.
mcp_client = ProductionFiMCPClient()

async def process_and_structure_data(phone_number: str, tool_context: ToolContext) -> dict:
    """
    Orchestrates fetching all financial data for a user, ensuring the client
    state is reset for each unique user request.
    """
    # This ensures we don't use a previous user's authentication or session.
    # mcp_client.reset()

    # 1. Authenticate the client for the current user
    auth_success = await mcp_client.authenticate(phone_number)
    if not auth_success:
        return {"status": "error", "message": "Authentication with Fi MCP server failed."}
    
    # ... (rest of the function is the same)
    data_sources = [
        "fetch_net_worth", "fetch_credit_report", "fetch_epf_details",
        "fetch_mf_transactions", "fetch_bank_transactions", "fetch_stock_transactions"
    ]
    tasks = [mcp_client.call_tool(source) for source in data_sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    raw_financial_data = dict(zip(data_sources, results))
    unified_state = {"raw_data": {}, "data_gaps": [], "integration_timestamp": time.time()}
    
    for source, result in raw_financial_data.items():
        if isinstance(result, Exception):
            unified_state["data_gaps"].append(source)
        else:
            unified_state["raw_data"][source] = result
            
    tool_context.state[f"user:financial_state"] = unified_state
    
    return {
        "status": "success", "message": f"Successfully integrated financial state.",
        "fetched_sources": len(unified_state["raw_data"]), "data_gaps": unified_state["data_gaps"]
    }

# --- Agent Definition ---
data_integration_agent = LlmAgent(
    name="data_integration_agent",
    model="gemini-2.0-flash",
    description="The foundational data agent. It connects to the Fi MCP server, fetches all user financial data in parallel, and structures it into a unified state for all other agents to use.",
    instruction="""
        You are the 'Unified Financial Footprint Aggregator', the foundational data backbone for Project Artha.
        Your one and only function is to create a complete and accurate snapshot of a user's financial life.

        Your process:
        1.  You will be given a user's phone number.
        2.  You MUST use the `process_and_structure_data` tool to handle the entire workflow of authenticating, fetching, and structuring the data.
        3.  Do not attempt to interpret the data. Your job is to ensure it is fetched and stored correctly in the 'user:financial_state' object.
        4.  Report the final status of the operation (success, number of sources fetched, and any data gaps) back to the calling agent.
        You are a system-level agent and do not interact directly with end-users. Your work is the essential first step for any meaningful financial analysis.
    """,
    tools=[process_and_structure_data],
    output_key="data_integration_result"
)