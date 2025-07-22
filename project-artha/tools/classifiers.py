# tools/classifiers.py

from google.adk.tools import ToolContext

class SemanticClassifier:
    """
    Intelligently classifies unknown financial entries using LLM reasoning,
    as defined in the agent architecture[cite: 1].
    """
    def __init__(self, model):
        self.model = model

    async def classify_entry(self, entry_text: str, context: str) -> dict:
        """
        Uses a Gemini model to perform semantic classification on a financial entry.

        This is superior to simple keyword matching, enabling understanding of entries
        like informal loans or chit funds[cite: 1].

        Args:
            entry_text: The text of the financial entry to classify (e.g., "CHITFUND_PAY_MAY").
            context: Additional context to aid classification.

        Returns:
            A dictionary with the classification and a confidence score.
        """
        prompt = f"""
        Analyze the following financial transaction entry and classify it.
        Entry: "{entry_text}"
        Context: {context}

        Based on Indian financial context, classify this into one of the following categories:
        [formal_investment, informal_investment, personal_spending, income, loan_payment, family_obligation, other]

        Return a single JSON object with two keys: "classification" and "confidence_score" (0.0 to 1.0).
        """
        # In a real implementation, this would be an LLM call.
        # response = await self.model.generate_content_async(prompt)
        # For now, we simulate the response.
        if "chitfund" in entry_text.lower():
            return {"classification": "informal_investment", "confidence_score": 0.85}
        return {"classification": "other", "confidence_score": 0.5}


class ConfidenceScorer:
    """
    Calculates a confidence score for each piece of financial data based on its
    source, age, and verification, per the architecture document[cite: 2].
    """
    def score_data_point(self, data_source: str, data_age_days: int, verification_count: int) -> float:
        """
        Applies a Bayesian-inspired confidence scoring model.

        Args:
            data_source: The source of the data (e.g., "bank_accounts", "user_input").
            data_age_days: How old the data is in days.
            verification_count: How many times this data has been cross-verified.

        Returns:
            A confidence score between 0.0 and 1.0.
        """
        source_reliability = {"bank_accounts": 0.95, "mutual_funds": 0.98, "user_input": 0.70}
        base_confidence = source_reliability.get(data_source, 0.6)
        age_factor = max(0.5, 1 - (data_age_days / 365))
        verification_factor = min(1.2, 1 + (verification_count / 10)) # Small boost for verification

        return min(1.0, base_confidence * age_factor * verification_factor)