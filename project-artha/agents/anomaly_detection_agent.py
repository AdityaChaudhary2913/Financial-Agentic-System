import asyncio
import json
import numpy as np
from datetime import datetime
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient

class AnomalyDetectionAgent:
    def detect_spending_anomalies(self, bank_transactions_data: dict) -> dict:
        """
        Analyzes debit transactions to find statistical anomalies.
        An anomaly is defined as a transaction amount that is more than
        2 standard deviations above the average transaction amount.
        """
        if not bank_transactions_data or 'bankTransactions' not in bank_transactions_data:
            return {"error": "Bank transaction data is unavailable."}

        all_txns = []
        for bank in bank_transactions_data['bankTransactions']:
            all_txns.extend(bank.get('txns', []))

        debit_amounts = []
        debit_txns = []
        for txn in all_txns:
            try:
                amount_str, _, _, txn_type, _, _ = txn
                if int(txn_type) == 2: # DEBIT
                    amount = float(amount_str)
                    debit_amounts.append(amount)
                    debit_txns.append(txn)
            except (ValueError, IndexError) as e:
                print(f"Skipping malformed transaction {txn}: {e}")
                continue

        if len(debit_amounts) < 5: # Need enough data for meaningful analysis
            return {"warning": "Not enough debit transactions to perform anomaly detection."}

        # Calculate statistical baseline
        mean_spending = np.mean(debit_amounts)
        std_dev_spending = np.std(debit_amounts)
        anomaly_threshold = mean_spending + (2 * std_dev_spending)

        anomalies = []
        for i, amount in enumerate(debit_amounts):
            if amount > anomaly_threshold:
                anomalies.append({
                    "transaction": debit_txns[i],
                    "amount": amount,
                    "reason": f"Exceeds anomaly threshold of {anomaly_threshold:,.2f}"
                })

        return {
            "mean_spending": round(mean_spending, 2),
            "std_dev_spending": round(std_dev_spending, 2),
            "anomaly_threshold": round(anomaly_threshold, 2),
            "detected_anomalies": anomalies,
            "anomaly_count": len(anomalies)
        }

async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m agents.anomaly_detection_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]

    print(f"🚀 Initializing agents to detect spending anomalies for {phone_number}...")
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    anomaly_agent = AnomalyDetectionAgent()

    try:
        # 1. Fetch data
        financial_data = await data_agent.get_comprehensive_data(phone_number, force_refresh=True)
        bank_transactions = financial_data.get("fetch_bank_transactions")

        # 2. Analyze data
        if bank_transactions and "error" not in bank_transactions:
            print("\n🔬 Detecting spending anomalies...")
            analysis = anomaly_agent.detect_spending_anomalies(bank_transactions)
            
            print("\n" + "="*60)
            print("SPENDING ANOMALY DETECTION REPORT")
            print("="*60)
            print(json.dumps(analysis, indent=2))
            print("="*60)
        else:
            print("\nCould not perform anomaly detection: Bank transaction data is unavailable.")

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())