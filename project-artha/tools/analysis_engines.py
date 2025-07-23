# tools/analysis_engines.py

import json
import logging
import time
from typing import Dict, Any
from google.adk.tools import ToolContext
from tools.classifiers import get_gemini_json_response

def _calculate_financial_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a summary of the user's financial health from raw data sources.
    This version has a corrected liability calculation.
    """
    summary = {
        "asset_allocation_equity_pct": 0.0, "debt_to_asset_ratio": 0.0,
        "credit_score": 0, "sip_consistency": "low", "has_diversified_assets": False,
    }

    # --- Asset Calculation (from Net Worth data) ---
    net_worth_data = raw_data.get('fetch_net_worth', {})
    total_assets = 0
    equity_assets_value = 0
    assets_raw = []
    if net_worth_data:
        assets_raw = net_worth_data.get('netWorthResponse', {}).get('assetValues', [])
        # Assets are all positive values in the list.
        total_assets = sum(float(a.get('value', {}).get('units', 0)) for a in assets_raw if float(a.get('value', {}).get('units', 0)) > 0)
        equity_assets_value = sum(
            float(a.get('value', {}).get('units', 0)) for a in assets_raw
            if a.get('netWorthAttribute') in ["ASSET_TYPE_EQUITY", "ASSET_TYPE_US_EQUITY"]
        )

    # --- Liability and Credit Score Calculation (from Credit Report) ---
    credit_report_data = raw_data.get('fetch_credit_report', {})
    total_liabilities = 0
    if credit_report_data and credit_report_data.get('creditReports'):
        credit_report = credit_report_data['creditReports'][0].get('creditReportData', {})
        
        # Use the detailed account list for the most accurate liability total.
        account_details = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
        total_liabilities = sum(float(acc.get('currentBalance', 0)) for acc in account_details)

        score_str = credit_report.get('score', {}).get('bureauScore', '0')
        summary["credit_score"] = int(score_str)

    # --- Final Ratio Calculations ---
    if total_assets > 0:
        summary["asset_allocation_equity_pct"] = round((equity_assets_value / total_assets) * 100, 2)
        summary["debt_to_asset_ratio"] = round(total_liabilities / total_assets, 2)
    summary["has_diversified_assets"] = len([a for a in assets_raw if float(a.get('value', {}).get('units', 0)) > 0]) > 2

    # --- SIP Consistency Calculation ---
    mf_transactions = raw_data.get('fetch_mf_transactions', {})
    if mf_transactions and mf_transactions.get('transactions'):
        sips = [t for t in mf_transactions['transactions'] if t.get('transactionMode') == 'S']
        if len(sips) > 10: summary["sip_consistency"] = "high"
        elif len(sips) > 2: summary["sip_consistency"] = "medium"
        
    return summary

async def generate_financial_identity(phone_number: str, tool_context: ToolContext) -> dict:
    """
    Analyzes a user's financial state to generate a dynamic, descriptive "Financial Identity".
    This replaces the rigid archetype classification.
    """
    financial_state = tool_context.state.get(f"user:financial_state")
    if not financial_state or not financial_state.get("raw_data"):
        return {"status": "error", "message": "Financial state not found. Run Data Integration Agent first."}

    summary = _calculate_financial_summary(financial_state["raw_data"])
    logging.info(f"Generated financial summary for identity generation: {summary}")

    # --- THE NEW CORE LOGIC ---
    # Instead of classifying, we ask Gemini to synthesize a unique identity.
    prompt = f"""
    You are an expert financial analyst. Based on the following financial data summary for an Indian user, generate a concise "Financial Identity" profile.
    This profile must be a JSON object with three keys: "persona", "strengths", and "opportunities".
    - "persona": A short, descriptive title for this user's financial character. Be direct and don't soften the description. For example, if a user is overwhelmed by debt, a persona like 'The Debt-Burdened Professional' is more accurate than 'Cautious but Vulnerable'.
    - "strengths": A bulleted list (as a single string) of what the user is doing well. If there are no clear strengths, it's okay to state that.
    - "opportunities": A bulleted list (as a single string) of the most critical areas where they could improve or grow.

    Financial Data Summary:
    {json.dumps(summary, indent=2)}

    Analyze the data and create a truly personalized identity. For example, a user with a debt-to-asset ratio over 5 is in a precarious financial situation. Reflect these nuances in the persona and opportunities.
    """
    
    identity_result = await get_gemini_json_response(prompt)
    logging.info(f"Generated Financial Identity: {identity_result}")

    # Assemble the behavioral profile with the new dynamic identity
    behavioral_profile = {
        "financial_identity": identity_result,
        "financial_summary": summary,
        "profile_timestamp": time.time()
    }
    
    tool_context.state[f"user:behavioral_profile"] = behavioral_profile
    logging.info(f"Behavioral profile for user {phone_number} saved to persistent state.")
    
    return {"status": "success", "profile": behavioral_profile}