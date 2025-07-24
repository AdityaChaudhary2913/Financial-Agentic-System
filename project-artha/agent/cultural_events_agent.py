import asyncio
import json
from datetime import datetime
from collections import defaultdict
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient

class CulturalEventsAgent:
    def __init__(self):
        # A simple model of major Indian festivals and their typical months.
        # This can be expanded with regional variations and more sophisticated logic.
        self.festival_months = {
            3: ["Holi"],
            8: ["Raksha Bandhan"],
            9: ["Ganesh Chaturthi"],
            10: ["Navaratri", "Dussehra"],
            11: ["Diwali"],
        }

    def forecast_cultural_expenses(self, bank_transactions_data: dict) -> dict:
        """
        Analyzes transaction data to provide a simple forecast for months with major festivals.
        """
        if not bank_transactions_data or 'bankTransactions' not in bank_transactions_data:
            return {"error": "Bank transaction data is unavailable."}

        monthly_spending = defaultdict(float)
        all_txns = []
        for bank in bank_transactions_data['bankTransactions']:
            all_txns.extend(bank.get('txns', []))

        for txn in all_txns:
            try:
                amount_str, _, date_str, txn_type, _, _ = txn
                if int(txn_type) == 2: # DEBIT
                    amount = float(amount_str)
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                    monthly_spending[transaction_date.month] += amount
            except (ValueError, IndexError) as e:
                print(f"Skipping malformed transaction {txn}: {e}")
                continue

        if not monthly_spending:
            return {"warning": "No spending data available to analyze."}

        # Calculate average monthly spending
        average_spending = sum(monthly_spending.values()) / len(monthly_spending)

        forecast = {
            "average_monthly_spending": round(average_spending, 2),
            "upcoming_festival_months_analysis": []
        }

        current_month = datetime.now().month
        for month_num, festivals in self.festival_months.items():
            if month_num >= current_month:
                analysis = {
                    "month": month_num,
                    "festivals": festivals,
                    "forecast": f"Expect potentially higher spending in {datetime(1, month_num, 1).strftime('%B')} for {', '.join(festivals)}."
                }
                forecast["upcoming_festival_months_analysis"].append(analysis)

        return forecast

async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m agents.cultural_events_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]

    print(f"🚀 Initializing agents to generate a cultural expense forecast for {phone_number}...")
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    cultural_agent = CulturalEventsAgent()

    try:
        # 1. Fetch data
        financial_data = await data_agent.get_comprehensive_data(phone_number, force_refresh=True)
        bank_transactions = financial_data.get("fetch_bank_transactions")

        # 2. Analyze data
        if bank_transactions and "error" not in bank_transactions:
            print("\n🔬 Analyzing for cultural expense patterns...")
            forecast_data = cultural_agent.forecast_cultural_expenses(bank_transactions)
            
            print("\n" + "="*60)
            print("CULTURAL EVENTS EXPENSE FORECAST")
            print("="*60)
            print(json.dumps(forecast_data, indent=2))
            print("="*60)
        else:
            print("\nCould not generate forecast: Bank transaction data is unavailable.")

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
