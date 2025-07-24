import asyncio
import json
from datetime import datetime
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient

class RiskProfilingAgent:
    def analyze_spending_patterns(self, bank_transactions_data):
        """
        Analyzes spending patterns from bank transactions for behavioral insights.
        For now, it calculates the ratio of weekend to weekday spending.
        """
        patterns = {
            'weekend_spending': 0.0,
            'weekday_spending': 0.0,
            'weekend_weekday_spending_ratio': 0.0,
            'total_debits': 0.0,
            'largest_debit': 0.0,
            'debit_transactions_count': 0
        }

        if not bank_transactions_data or 'bankTransactions' not in bank_transactions_data:
            return patterns

        all_txns = []
        for bank in bank_transactions_data['bankTransactions']:
            all_txns.extend(bank.get('txns', []))

        largest_debit_amount = 0.0

        for txn in all_txns:
            try:
                amount_str, _, date_str, txn_type, _, _ = txn
                amount = float(amount_str)
                
                # We only care about debits (spending)
                if int(txn_type) == 2: # DEBIT
                    patterns['total_debits'] += amount
                    patterns['debit_transactions_count'] += 1
                    if amount > largest_debit_amount:
                        largest_debit_amount = amount

                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Monday is 0 and Sunday is 6
                    if transaction_date.weekday() >= 5: # Saturday or Sunday
                        patterns['weekend_spending'] += amount
                    else:
                        patterns['weekday_spending'] += amount
            except (ValueError, IndexError) as e:
                print(f"Skipping malformed transaction {txn}: {e}")
                continue

        if patterns['weekday_spending'] > 0:
            patterns['weekend_weekday_spending_ratio'] = round(
                patterns['weekend_spending'] / patterns['weekday_spending'], 2
            )
        
        patterns['largest_debit'] = largest_debit_amount

        return patterns

async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python agents/risk_profiling_agent.py <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]

    print(f"🚀 Initializing agents to generate a risk profile for {phone_number}...")
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    risk_agent = RiskProfilingAgent()

    try:
        # 1. Fetch data using DataIntegrationAgent
        financial_data = await data_agent.get_comprehensive_data(phone_number, force_refresh=True)
        bank_transactions = financial_data.get("fetch_bank_transactions")

        # 2. Analyze data using RiskProfilingAgent
        if bank_transactions and "error" not in bank_transactions:
            print("\n🔬 Analyzing spending patterns...")
            profile = risk_agent.analyze_spending_patterns(bank_transactions)
            
            print("\n" + "="*50)
            print("RISK PROFILE ANALYSIS (SPENDING PATTERNS)")
            print("="*50)
            print(json.dumps(profile, indent=2))
            print("="*50)
        else:
            print("\nCould not analyze risk profile: Bank transaction data is unavailable.")

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
