# # tools/classifiers.py

# import os
# import json
# import logging
# import google.generativeai as genai
# from typing import Dict, Any

# # --- Gemini API Configuration ---
# # This configures the client using your environment variable.
# # Ensure 'GOOGLE_API_KEY' is set in your environment.
# try:
#     genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
#     gemini_model = genai.GenerativeModel('gemini-2.0-flash')
#     logging.info("Gemini client configured successfully.")
# except Exception as e:
#     logging.error(f"Failed to configure Gemini client: {e}")
#     gemini_model = None

# async def get_gemini_json_response(prompt: str) -> Dict[str, Any]:
#     """
#     Calls the Gemini API with a specific prompt and expects a JSON response.
#     Includes error handling and ensures a valid JSON object is returned.
#     """
#     if not gemini_model:
#         raise ConnectionError("Gemini client is not configured. Please set GOOGLE_API_KEY.")
    
#     try:
#         response = await gemini_model.generate_content_async(
#             prompt,
#             generation_config=genai.types.GenerationConfig(
#                 response_mime_type="application/json"
#             )
#         )
#         # The API returns a JSON string, so we need to parse it.
#         return json.loads(response.text)
#     except Exception as e:
#         logging.error(f"Error calling Gemini API: {e}")
#         # Return a default error structure
#         return {"error": str(e), "classification": "error", "confidence_score": 0.0}

# # --- Classifier Classes ---

# class SemanticClassifier:
#     """
#     Uses live Gemini calls to classify ambiguous financial entries.
#     """
#     async def classify_entry(self, entry_text: str, context: str) -> Dict[str, Any]:
#         """
#         Performs semantic classification on a financial transaction description.

#         Args:
#             entry_text: The transaction description (e.g., "UPI/PAY/8J291BC").
#             context: Additional context to aid classification.

#         Returns:
#             A dictionary with the classification and confidence score.
#         """
#         prompt = f"""
#         Analyze the following financial transaction entry from an Indian user's statement.
#         Entry: "{entry_text}"
#         Context: {context}

#         Based on common financial behaviors and terminology in India, classify this into one of the following categories:
#         [formal_investment, informal_investment, personal_spending, income, loan_payment, family_obligation, other]

#         Return a single JSON object with two keys: "classification" and "confidence_score" (a float between 0.0 and 1.0).
#         """
#         return await get_gemini_json_response(prompt)

# class IndianArchetypeClassifier:
#     """
#     Classifies a user into a financial archetype based on their unified financial state using a live Gemini call.
#     """
#     async def classify_archetype(self, financial_state_summary: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Analyzes a user's financial data to determine their archetype.

#         Args:
#             financial_state_summary: A summary of the user's financial data.

#         Returns:
#             A dictionary with the determined archetype and confidence score.
#         """
#         prompt = f"""
#         Analyze the following summary of a user's financial data to classify them into one of the defined Indian financial archetypes.

#         Financial Data Summary:
#         {json.dumps(financial_state_summary, indent=2)}

#         Archetype Definitions:
#         - The Disciplined Accumulator: Systematic, goal-oriented, consistent SIPs, high savings rate.
#         - The Traditionalist Anchor: Prioritizes safety. High allocation to debt, FDs, gold. Low equity (<20%).
#         - The Balanced Compounder: Diversified, informed. High equity (>70%), multiple asset classes, good credit score (>750).
#         - The High-Beta Voyager: Aggressive, high-risk. Volatile assets (small-cap, crypto), high transaction frequency.
#         - The Debt-Conscious Strategist: Focused on liabilities. High debt-to-asset ratio (>0.5), low credit score (<650).
#         - The Unsettled Professional: Irregular income, needs liquidity. Inconsistent SIPs, high bank balances.

#         Based on the provided data, determine the most fitting archetype. Return a single JSON object with two keys: "archetype" and "confidence_score" (a float between 0.0 and 1.0).
#         """
#         return await get_gemini_json_response(prompt)



# tools/classifiers.py

import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any

# --- Gemini API Client (Lazy Initialization) ---
# We will initialize the model only when it's first needed.
_gemini_model = None

def _get_gemini_model():
    """Initializes and returns the Gemini model client, ensuring it only happens once."""
    global _gemini_model
    if _gemini_model is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ConnectionError(
                "GOOGLE_API_KEY environment variable not set. "
                "Please set it to your Google AI API key."
            )
        try:
            genai.configure(api_key=api_key)
            _gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            logging.info("Gemini client configured successfully.")
        except Exception as e:
            logging.error(f"Failed to configure Gemini client: {e}")
            raise ConnectionError(f"Failed to configure Gemini client: {e}")
    return _gemini_model

async def get_gemini_json_response(prompt: str) -> Dict[str, Any]:
    """Calls the Gemini API and ensures a valid JSON object is returned."""
    model = _get_gemini_model() # This will initialize the model on the first call
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return {"error": str(e), "classification": "error", "confidence_score": 0.0}

# --- Classifier Classes ---

class SemanticClassifier:
    """Uses live Gemini calls to classify ambiguous financial entries."""
    async def classify_entry(self, entry_text: str, context: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following financial transaction entry from an Indian user's statement.
        Entry: "{entry_text}"
        Context: {context}
        Classify this into one of: [formal_investment, informal_investment, personal_spending, income, loan_payment, family_obligation, other].
        Return a single JSON object with two keys: "classification" and "confidence_score" (a float between 0.0 and 1.0).
        """
        return await get_gemini_json_response(prompt)

class IndianArchetypeClassifier:
    """Classifies a user into a financial archetype based on their unified financial state."""
    async def classify_archetype(self, financial_state_summary: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze the JSON summary of a user's financial data to classify them into one of the defined Indian financial archetypes.
        Financial Data Summary: {json.dumps(financial_state_summary, indent=2)}
        Archetype Definitions:
        - The Disciplined Accumulator: Systematic, consistent SIPs, high savings rate.
        - The Traditionalist Anchor: Prioritizes safety. High allocation to debt, FDs, gold. Low equity (<20%).
        - The Balanced Compounder: Diversified, informed. High equity (>70%), multiple asset classes, good credit score (>750).
        - The High-Beta Voyager: Aggressive, high-risk. Volatile assets (small-cap, crypto), high transaction frequency.
        - The Debt-Conscious Strategist: Focused on liabilities. High debt-to-asset ratio (>0.5), low credit score (<650).
        - The Unsettled Professional: Irregular income, needs liquidity. Inconsistent SIPs, high bank balances.
        Based on the data, return a single JSON object with two keys: "archetype" and "confidence_score" (a float between 0.0 and 1.0).
        """
        return await get_gemini_json_response(prompt)