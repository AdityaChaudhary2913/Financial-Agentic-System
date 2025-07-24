import json
import re

class TrustTransparencyAgent:
    def __init__(self):
        """Initializes the agent with explanation patterns."""
        self.explanation_patterns = {
            "weekend/weekday spending ratio": {
                "regex": r"weekend spending is only about (\\d+)% of your weekday spending",
                "template": "A Weekend spending of {value}% of your weekday spending indicates a significant difference in your spending patterns between weekdays and weekends. This often suggests that most of your essential expenses occur during the week, while weekend spending is comparatively lower."
            },
            "largest debit": {
                "regex": r"largest single debit transaction was [\\$₹]([\\d,.]+)",
                "template": "Your largest single transaction was for ₹{value}. High-value transactions are important to track as they significantly impact your monthly cash flow."
            },
            "weekend spending": {
                "regex": r"weekend spending is [\\$₹]([\\d,.]+)",
                "template": "Your weekend spending of ₹{value} represents your expenses incurred during non-working days. This often includes leisure, entertainment, and personal activities."
            },
            "weekday spending": {
                "regex": r"weekday spending is [\\$₹]([\\d,.]+)",
                "template": "Your weekday spending of ₹{value} typically covers essential expenses like commuting, work-related costs, and daily necessities."
            },
            "total debits": {
                "regex": r"total debits are [\\$₹]([\\d,.]+)",
                "template": "Your total debits of ₹{value} represent the total outflow of money from your account during the analyzed period. This is a key indicator of your overall expenditure."
            },
            "average monthly spending": {
                "regex": r"average monthly spending is ([\\d,.]+)",
                "template": "An average monthly spend of ₹{value} serves as your financial baseline. Understanding this helps in budgeting for future goals and identifying unusual spending months."
            }
        }

    def explain_risk_analysis(self, risk_profile_data: dict) -> str:
        """
        Generates a human-readable explanation of a risk profile analysis.
        """
        if not risk_profile_data or "error" in risk_profile_data:
            return "I could not generate an explanation because the risk analysis data is unavailable."

        try:
            explanation = ["Here's a simple breakdown of your spending behavior:\n"]
            ratio = risk_profile_data.get('weekend_weekday_spending_ratio', 0)
            largest_debit = risk_profile_data.get('largest_debit', 0)
            debit_count = risk_profile_data.get('debit_transactions_count', 0)

            explanation.append(f"- **Spending Ratio:** Your weekend vs. weekday spending ratio is {ratio}. A value above 1.0 often indicates significant discretionary (non-essential) spending.")
            explanation.append(f"- **Largest Transaction:** Your single largest expense was for ₹{largest_debit:,.2f}. High-value transactions are important to track as they significantly impact your monthly cash flow.")
            explanation.append(f"- **Transaction Volume:** You had {debit_count} spending transactions in the analyzed period.")

            return "\n".join(explanation)
        except Exception as e:
            return f"An error occurred while generating the explanation: {e}"

    def explain_anomaly_detection(self, anomaly_data: dict) -> str:
        """
        Generates a human-readable explanation of the anomaly detection logic.
        """
        if not anomaly_data or "error" in anomaly_data:
            return "I could not generate an explanation because the anomaly detection data is unavailable."
        
        try:
            explanation = ["Of course. Here is how I detected the spending anomaly step-by-step:\n"]
            mean = anomaly_data.get('mean_spending', 0)
            std_dev = anomaly_data.get('std_dev_spending', 0)
            threshold = anomaly_data.get('anomaly_threshold', 0)
            
            explanation.append(f"1.  **Calculate Your Baseline:** First, I analyzed all your debit transactions to find your average spending per transaction, which is ₹{mean:,.2f}.")
            explanation.append(f"2.  **Measure Spending Volatility:** Next, I calculated the standard deviation (a measure of how spread out your spending is), which is ₹{std_dev:,.2f}.")
            explanation.append(f"3.  **Set the Anomaly Threshold:** I set a threshold for what would be considered an unusually large transaction. This is calculated as: Average + (2 * Standard Deviation) = ₹{threshold:,.2f}.")
            
            anomalies = anomaly_data.get("detected_anomalies", [])
            if anomalies:
                explanation.append(f"4.  **Identify the Anomaly:** Finally, I flagged the transaction of ₹{anomalies[0]['amount']:,.2f} because it exceeded this threshold.")
            else:
                explanation.append("4.  **Conclusion:** I did not find any transactions that exceeded this threshold. All your spending was within your normal, established pattern.")

            return "\n".join(explanation)
        except Exception as e:
            return f"An error occurred while generating the anomaly explanation: {e}"

    def add_financial_explanations(self, response_text: str) -> str:
        """
        Scans the final response text for financial metrics and appends explanations.
        """
        explanations = []
        for keyword, pattern_info in self.explanation_patterns.items():
            match = re.search(pattern_info["regex"], response_text, re.IGNORECASE)
            if match:
                value = match.group(1)
                explanation = pattern_info["template"].format(value=value)
                explanations.append(explanation)
        
        if explanations:
            # Append the explanations to the original response text
            final_response = [response_text, "\n" + "-"*60, "FINANCIAL RATIONALE", "-"*60]
            final_response.extend(explanations)
            return "\n".join(final_response)
        else:
            # If no financial terms were found, return the original text
            return response_text