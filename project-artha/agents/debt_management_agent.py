import asyncio
import json
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient

class DebtManagementAgent:
    def analyze_debt_summary(self, credit_report_data: dict, bank_transactions_data: dict) -> dict:
        """
        Analyzes credit report and bank transactions to provide a summary of the user's debt.
        """
        debt_summary = {
            "total_outstanding_debt": 0.0,
            "credit_cards": [],
            "loans": [],
            "past_due_accounts": []
        }

        # Process Credit Report Data
        if credit_report_data and 'creditReports' in credit_report_data:
            for report in credit_report_data['creditReports']:
                credit_accounts = report.get('creditReportData', {}).get('creditAccount', {}).get('creditAccountDetails', [])
                for account in credit_accounts:
                    account_type = account.get('accountType')
                    current_balance = float(account.get('currentBalance', 0))
                    amount_past_due = float(account.get('amountPastDue', 0))
                    subscriber_name = account.get('subscriberName')
                    
                    if account_type == "10": # Credit Card
                        debt_summary['credit_cards'].append({
                            "issuer": subscriber_name,
                            "current_balance": current_balance,
                            "credit_limit": float(account.get('creditLimitAmount', 0)),
                            "past_due": amount_past_due
                        })
                        debt_summary['total_outstanding_debt'] += current_balance
                    elif account_type in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"]: # Various Loan Types
                        debt_summary['loans'].append({
                            "type": subscriber_name,
                            "current_balance": current_balance,
                            "original_amount": float(account.get('highestCreditOrOriginalLoanAmount', 0)),
                            "past_due": amount_past_due
                        })
                        debt_summary['total_outstanding_debt'] += current_balance
                    
                    if amount_past_due > 0:
                        debt_summary['past_due_accounts'].append({
                            "account_type": subscriber_name,
                            "amount": amount_past_due
                        })
        
        # Process Bank Transactions for EMIs (optional, as credit report is primary)
        # This part can be enhanced later to identify recurring EMI payments not explicitly in credit report
        
        return debt_summary

async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m agents.debt_management_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]

    print(f"🚀 Initializing Debt Management Agent for {phone_number}...")
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    debt_agent = DebtManagementAgent()

    try:
        # 1. Fetch data
        financial_data = await data_agent.get_comprehensive_data(phone_number, force_refresh=True)
        credit_report = financial_data.get("fetch_credit_report")
        bank_transactions = financial_data.get("fetch_bank_transactions")

        # 2. Analyze data
        if credit_report and "error" not in credit_report:
            print("\n🔬 Analyzing debt summary...")
            summary = debt_agent.analyze_debt_summary(credit_report, bank_transactions)
            
            print("\n" + "="*60)
            print("DEBT SUMMARY REPORT")
            print("="*60)
            print(json.dumps(summary, indent=2))
            print("="*60)
        else:
            print("\nCould not generate debt summary: Credit report data is unavailable.")

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
