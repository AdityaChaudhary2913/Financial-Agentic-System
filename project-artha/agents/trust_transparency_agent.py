import re

class TrustTransparencyAgent:
    def __init__(self):
        # This dictionary maps keywords found in the text to their explanation templates.
        # We use regex to find the numbers associated with these keywords.
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

# Example of how this agent will be used
if __name__ == '__main__':
    agent = TrustTransparencyAgent()
    
    # This is a sample response from the CoreFinancialAdvisorAgent
    sample_llm_response = "OK. I have analyzed your spending habits. Here is a summary: Your weekend spending is $5500.0, and your weekday spending is $309050.0. The ratio of weekend to weekday spending is 0.02. Your total debits are $314550.0, and your largest debit transaction was $72000.0. You had 9 debit transactions."

    enriched_response = agent.add_financial_explanations(sample_llm_response)
    
    print(enriched_response)