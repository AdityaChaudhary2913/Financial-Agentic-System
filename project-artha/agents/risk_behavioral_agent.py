# agents/risk_behavioral_agent.py

from google.adk.agents import LlmAgent
from tools.analysis_engines import generate_financial_identity

risk_behavioral_agent = LlmAgent(
    name="risk_behavioral_agent",
    model="gemini-1.5-flash",
    description="Analyzes user financial data to generate a unique, descriptive 'Financial Identity'.",
    instruction="""
        You are the 'Behavioral Nudge Coach', a specialist financial analyst.
        Your goal is to synthesize a unique 'Financial Identity' from a user's financial data.

        Your process:
        1.  You will be given a user's phone number.
        2.  You MUST use the `generate_financial_identity` tool to perform the complete analysis.
        3.  Once the tool returns the profile, your final response should be a clean, user-friendly summary of the generated identity, including their persona, strengths, and opportunities.
        
        You are a backend analysis agent. Do not ask questions. Your role is to derive and present insights from existing data.
    """,
    tools=[
        # Use the new tool
        generate_financial_identity,
    ]
)