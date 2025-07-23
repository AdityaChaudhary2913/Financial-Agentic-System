# main_runner.py

import asyncio
import os
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.data_integration_agent import data_integration_agent
from agents.risk_behavioral_agent import risk_behavioral_agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_agent(runner, session, user_message, user_id):
    """Helper function to run an agent and return its final response."""
    final_response_text = ""
    # --- FIX: Passed 'user_id' to the runner's run_async method ---
    async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=user_message):
        if event.is_final_response():
            final_response_text = event.content.parts[0].text
            break
    return final_response_text

async def main():
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ ERROR: The GOOGLE_API_KEY environment variable is not set.")
        return

    print("🚀 Initializing Project Artha Agent Runner...")
    session_service = InMemorySessionService()
    app_name = "project_artha"
    print("-" * 50)

    while True:
        user_id = input("Enter Phone Number (or 'quit' to exit): ").strip()
        if user_id.lower() == 'quit':
            break
        if not user_id.isdigit() or len(user_id) != 10:
            print("Invalid input. Please enter a 10-digit phone number.")
            continue

        try:
            session = await session_service.create_session(app_name=app_name, user_id=user_id)
            user_message = types.Content(role="user", parts=[types.Part(text=user_id)])

            # --- STAGE 1: DATA INTEGRATION ---
            print("\n STAGE 1: Running Data Integration Agent...")
            data_runner = Runner(agent=data_integration_agent, app_name=app_name, session_service=session_service)
            # --- FIX: Passed 'user_id' to the run_agent call ---
            await run_agent(data_runner, session, user_message, user_id)
            print(f"✅ Data Integration Complete.")

            # --- STAGE 2: IDENTITY GENERATION ---
            print("\n STAGE 2: Running Financial Identity Agent...")
            risk_runner = Runner(agent=risk_behavioral_agent, app_name=app_name, session_service=session_service)
            # --- FIX: Passed 'user_id' to the run_agent call ---
            response2 = await run_agent(risk_runner, session, user_message, user_id)
            print(f"✅ Financial Identity Agent Response:\n{response2}")

            # --- VERIFICATION STEP ---
            print("\n--- Verification of Session State ---")
            updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session.id)
            if updated_session is None:
                print("❌ VERIFICATION FAILED: Could not retrieve session.")
                continue

            financial_state = updated_session.state.get(f"user:financial_state")
            if financial_state:
                print("✅ [Stage 1] VERIFICATION SUCCESS: 'user:financial_state' found.")
            else:
                print("❌ [Stage 1] VERIFICATION FAILED: 'user:financial_state' not found.")

            behavioral_profile = updated_session.state.get(f"user:behavioral_profile")
            if behavioral_profile:
                print("✅ [Stage 2] VERIFICATION SUCCESS: 'user:behavioral_profile' found.")
                identity = behavioral_profile.get('financial_identity', {})
                print(f"    - Persona: {identity.get('persona')}")
                print(f"    - Strengths: {identity.get('strengths')}")
                print(f"    - Opportunities: {identity.get('opportunities')}")
            else:
                print("❌ [Stage 2] VERIFICATION FAILED: 'user:behavioral_profile' not found.")
            
            print("-" * 50)

        except Exception as e:
            logging.error(f"An error occurred in the main loop: {e}", exc_info=True)
            print("\nPlease ensure the Fi MCP development server is running (`go run .`).")
            print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())









# # # main_runner.py

# # import asyncio
# # import json
# # import os
# # import logging
# # from google.adk.runners import Runner
# # from google.adk.sessions import InMemorySessionService
# # from google.genai import types

# # # Import the agents we want to test
# # from agents.data_integration_agent import data_integration_agent
# # from agents.risk_behavioral_agent import risk_behavioral_agent

# # # Configure logging to see detailed output
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # async def run_agent(runner, session, user_message, user_id):
# #     """Helper function to run an agent and return its final response."""
# #     final_response_text = ""
# #     async for event in runner.run_async(session_id=session.id, user_id=user_id, new_message=user_message):
# #         if event.is_final_response():
# #             final_response_text = event.content.parts[0].text
# #             break
# #     return final_response_text

# # async def main():
# #     """Main entry point for running and testing the Project Artha agent pipeline."""
# #     if "GOOGLE_API_KEY" not in os.environ:
# #         print("❌ ERROR: The GOOGLE_API_KEY environment variable is not set.")
# #         return

# #     print("🚀 Initializing Project Artha Agent Runner...")
# #     session_service = InMemorySessionService()
# #     app_name = "project_artha"
# #     print("-" * 50)

# #     while True:
# #         user_id = input("Enter Phone Number (or 'quit' to exit): ").strip()
# #         if user_id.lower() == 'quit':
# #             break

# #         if not user_id.isdigit() or len(user_id) != 10:
# #             print("Invalid input. Please enter a 10-digit phone number.")
# #             continue

# #         try:
# #             session = await session_service.create_session(app_name=app_name, user_id=user_id)
# #             user_message = types.Content(role="user", parts=[types.Part(text=user_id)])

# #             # --- STAGE 1: DATA INTEGRATION ---
# #             print("\n M-b\M-^@\M-^S STAGE 1: Running Data Integration Agent...")
# #             data_runner = Runner(agent=data_integration_agent, app_name=app_name, session_service=session_service)
# #             response1 = await run_agent(data_runner, session, user_message, user_id)
# #             print(f"✅ Data Integration Agent Response: {response1}")

# #             # --- STAGE 2: BEHAVIORAL ANALYSIS ---
# #             print("\n M-b\M-^@\M-^S STAGE 2: Running Risk & Behavioral Analysis Agent...")
# #             risk_runner = Runner(agent=risk_behavioral_agent, app_name=app_name, session_service=session_service)
# #             response2 = await run_agent(risk_runner, session, user_message, user_id)
# #             print(f"✅ Risk & Behavioral Agent Response: {response2}")


# #             # --- VERIFICATION STEP ---
# #             print("\n--- Verification of Session State ---")
# #             updated_session = await session_service.get_session(app_name="project-artha", user_id=user_id, session_id=session.id)
            
# #             # Verify Stage 1 output
# #             financial_state = updated_session.state.get(f"user:financial_state")
# #             if financial_state:
# #                 print("✅ [Stage 1] VERIFICATION SUCCESS: 'user:financial_state' found.")
# #             else:
# #                 print("❌ [Stage 1] VERIFICATION FAILED: 'user:financial_state' not found.")

# #             # Verify Stage 2 output
# #             behavioral_profile = updated_session.state.get(f"user:behavioral_profile")
# #             if behavioral_profile:
# #                 print("✅ [Stage 2] VERIFICATION SUCCESS: 'user:behavioral_profile' found.")
# #                 print(f"    - Archetype: {behavioral_profile.get('archetype')} (Confidence: {behavioral_profile.get('archetype_confidence')})")
# #             else:
# #                 print("❌ [Stage 2] VERIFICATION FAILED: 'user:behavioral_profile' not found.")
            
# #             print("-" * 50)

# #         except Exception as e:
# #             logging.error(f"An error occurred in the main loop: {e}", exc_info=True)
# #             print("\nPlease ensure the Fi MCP development server is running (`go run .`).")
# #             print("-" * 50)


# # if __name__ == "__main__":
# #     asyncio.run(main())


# # main_runner.py

# import asyncio
# import json
# import os
# import logging
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# # Import the agents
# from agents.data_integration_agent import data_integration_agent
# from agents.risk_behavioral_agent import risk_behavioral_agent

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# async def run_agent(runner, session, user_message, user_id):
#     """Helper function to run an agent and return its final response."""
#     final_response_text = ""
#     async for event in runner.run_async(session_id=session.id, user_id=user_id, new_message=user_message):
#         if event.is_final_response():
#             final_response_text = event.content.parts[0].text
#             break
#     return final_response_text

# async def main():
#     if "GOOGLE_API_KEY" not in os.environ:
#         print("❌ ERROR: The GOOGLE_API_KEY environment variable is not set.")
#         return

#     print("🚀 Initializing Project Artha Agent Runner...")
#     session_service = InMemorySessionService()
#     app_name = "project_artha"
#     print("-" * 50)

#     while True:
#         user_id = input("Enter Phone Number (or 'quit' to exit): ").strip()
#         if user_id.lower() == 'quit':
#             break
#         if not user_id.isdigit() or len(user_id) != 10:
#             print("Invalid input. Please enter a 10-digit phone number.")
#             continue

#         try:
#             session = await session_service.create_session(app_name=app_name, user_id=user_id)
#             user_message = types.Content(role="user", parts=[types.Part(text=user_id)])

#             # --- STAGE 1: DATA INTEGRATION ---
#             print("\n STAGE 1: Running Data Integration Agent...")
#             data_runner = Runner(agent=data_integration_agent, app_name=app_name, session_service=session_service)
#             response1 = await run_agent(data_runner, session, user_message, user_id)
#             print(f"✅ Data Integration Agent Response: {response1}")

#             # --- STAGE 2: BEHAVIORAL ANALYSIS ---
#             print("\n STAGE 2: Running Risk & Behavioral Analysis Agent...")
#             risk_runner = Runner(agent=risk_behavioral_agent, app_name=app_name, session_service=session_service)
#             response2 = await run_agent(risk_runner, session, user_message, user_id)
#             print(f"✅ Risk & Behavioral Agent Response: {response2}")

#             # --- VERIFICATION STEP ---
#             print("\n--- Verification of Session State ---")

#             # --- FIX: Added app_name and user_id to the get_session call ---
#             updated_session = await session_service.get_session(
#                 app_name=app_name,
#                 user_id=user_id,
#                 session_id=session.id
#             )
            
#             if updated_session is None:
#                 print("❌ VERIFICATION FAILED: Could not retrieve session.")
#                 continue

#             financial_state = updated_session.state.get(f"user:financial_state")
#             if financial_state:
#                 print("✅ [Stage 1] VERIFICATION SUCCESS: 'user:financial_state' found.")
#             else:
#                 print("❌ [Stage 1] VERIFICATION FAILED: 'user:financial_state' not found.")

#             behavioral_profile = updated_session.state.get(f"user:behavioral_profile")
#             if behavioral_profile:
#                 print("✅ [Stage 2] VERIFICATION SUCCESS: 'user:behavioral_profile' found.")
#                 print(f"    - Archetype: {behavioral_profile.get('archetype')} (Confidence: {behavioral_profile.get('archetype_confidence')})")
#                 print(f"    - Calculated Summary: {behavioral_profile.get('financial_summary')}")
#             else:
#                 print("❌ [Stage 2] VERIFICATION FAILED: 'user:behavioral_profile' not found.")
            
#             print("-" * 50)

#         except Exception as e:
#             logging.error(f"An error occurred in the main loop: {e}", exc_info=True)
#             print("\nPlease ensure the Fi MCP development server is running (`go run .`).")
#             print("-" * 50)

# if __name__ == "__main__":
#     asyncio.run(main())