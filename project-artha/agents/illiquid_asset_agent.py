import asyncio
import json
from datetime import datetime, timedelta
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient

class IlliquidAssetAgent:
    def __init__(self):
        # Asset liquidity classifications and typical conversion times
        self.asset_liquidity_map = {
            "ASSET_TYPE_SAVINGS_ACCOUNTS": {"liquidity": "high", "conversion_days": 1},
            "ASSET_TYPE_MUTUAL_FUND": {"liquidity": "medium", "conversion_days": 3},
            "ASSET_TYPE_INDIAN_SECURITIES": {"liquidity": "medium", "conversion_days": 2},
            "ASSET_TYPE_US_SECURITIES": {"liquidity": "medium", "conversion_days": 5},
            "ASSET_TYPE_EPF": {"liquidity": "low", "conversion_days": 30},
            "ASSET_TYPE_GOLD": {"liquidity": "medium", "conversion_days": 7},
            "ASSET_TYPE_REAL_ESTATE": {"liquidity": "very_low", "conversion_days": 180},
            "ASSET_TYPE_FIXED_DEPOSITS": {"liquidity": "medium", "conversion_days": 1}
        }
        
        # Idle cash thresholds based on Indian context
        self.idle_cash_threshold = 100000  # ₹1L as minimum working capital
        self.emergency_fund_months = 6

    def analyze_illiquid_assets(self, financial_data: dict) -> dict:
        """
        Comprehensive analysis of illiquid and dormant assets with optimization recommendations.
        """
        if not financial_data:
            return {"error": "No financial data available for illiquid asset analysis."}

        net_worth_data = financial_data.get('fetch_net_worth', {})
        bank_transactions = financial_data.get('fetch_bank_transactions', {})
        mf_transactions = financial_data.get('fetch_mf_transactions', {})

        analysis = {
            "asset_liquidity_breakdown": {},
            "dormant_assets": [],
            "idle_cash_analysis": {},
            "optimization_opportunities": [],
            "monetization_strategies": [],
            "liquidity_score": 0,
            "emergency_readiness": {},
            "asset_rebalancing_suggestions": []
        }

        # Analyze asset liquidity breakdown
        if net_worth_data.get('netWorthResponse'):
            analysis["asset_liquidity_breakdown"] = self._analyze_asset_liquidity(net_worth_data)
            analysis["liquidity_score"] = self._calculate_liquidity_score(analysis["asset_liquidity_breakdown"])

        # Identify dormant assets
        analysis["dormant_assets"] = self._identify_dormant_assets(
            net_worth_data, bank_transactions, mf_transactions
        )

        # Analyze idle cash
        analysis["idle_cash_analysis"] = self._analyze_idle_cash(bank_transactions)

        # Generate optimization opportunities
        analysis["optimization_opportunities"] = self._generate_optimization_opportunities(
            analysis["asset_liquidity_breakdown"], 
            analysis["dormant_assets"],
            analysis["idle_cash_analysis"]
        )

        # Generate monetization strategies
        analysis["monetization_strategies"] = self._generate_monetization_strategies(
            analysis["asset_liquidity_breakdown"],
            analysis["dormant_assets"]
        )

        # Emergency readiness assessment
        analysis["emergency_readiness"] = self._assess_emergency_readiness(
            analysis["asset_liquidity_breakdown"],
            bank_transactions
        )

        # Asset rebalancing suggestions
        analysis["asset_rebalancing_suggestions"] = self._suggest_asset_rebalancing(
            analysis["asset_liquidity_breakdown"]
        )

        return analysis

    def _analyze_asset_liquidity(self, net_worth_data: dict) -> dict:
        """Analyze assets by liquidity categories."""
        liquidity_breakdown = {
            "high_liquidity": {"value": 0, "assets": []},
            "medium_liquidity": {"value": 0, "assets": []},
            "low_liquidity": {"value": 0, "assets": []},
            "very_low_liquidity": {"value": 0, "assets": []}
        }

        assets = net_worth_data.get('netWorthResponse', {}).get('assetValues', [])
        
        for asset in assets:
            asset_type = asset.get('netWorthAttribute')
            value = float(asset.get('value', {}).get('units', 0))
            
            if asset_type in self.asset_liquidity_map:
                liquidity_level = self.asset_liquidity_map[asset_type]["liquidity"]
                conversion_days = self.asset_liquidity_map[asset_type]["conversion_days"]
                
                if liquidity_level == "high":
                    liquidity_breakdown["high_liquidity"]["value"] += value
                    liquidity_breakdown["high_liquidity"]["assets"].append({
                        "type": asset_type,
                        "value": value,
                        "conversion_days": conversion_days
                    })
                elif liquidity_level == "medium":
                    liquidity_breakdown["medium_liquidity"]["value"] += value
                    liquidity_breakdown["medium_liquidity"]["assets"].append({
                        "type": asset_type,
                        "value": value,
                        "conversion_days": conversion_days
                    })
                elif liquidity_level == "low":
                    liquidity_breakdown["low_liquidity"]["value"] += value
                    liquidity_breakdown["low_liquidity"]["assets"].append({
                        "type": asset_type,
                        "value": value,
                        "conversion_days": conversion_days
                    })
                else:  # very_low
                    liquidity_breakdown["very_low_liquidity"]["value"] += value
                    liquidity_breakdown["very_low_liquidity"]["assets"].append({
                        "type": asset_type,
                        "value": value,
                        "conversion_days": conversion_days
                    })

        return liquidity_breakdown

    def _calculate_liquidity_score(self, liquidity_breakdown: dict) -> float:
        """Calculate overall portfolio liquidity score (0-100)."""
        total_value = sum(category["value"] for category in liquidity_breakdown.values())
        
        if total_value == 0:
            return 0

        # Weighted scoring: high=100, medium=70, low=40, very_low=10
        weighted_score = (
            liquidity_breakdown["high_liquidity"]["value"] * 100 +
            liquidity_breakdown["medium_liquidity"]["value"] * 70 +
            liquidity_breakdown["low_liquidity"]["value"] * 40 +
            liquidity_breakdown["very_low_liquidity"]["value"] * 10
        ) / total_value

        return round(weighted_score, 2)

    def _identify_dormant_assets(self, net_worth_data: dict, bank_transactions: dict, mf_transactions: dict) -> list:
        """Identify assets that are dormant or underutilized."""
        dormant_assets = []

        # Check for excessive cash in savings
        assets = net_worth_data.get('netWorthResponse', {}).get('assetValues', [])
        for asset in assets:
            if asset.get('netWorthAttribute') == 'ASSET_TYPE_SAVINGS_ACCOUNTS':
                savings_value = float(asset.get('value', {}).get('units', 0))
                if savings_value > self.idle_cash_threshold * 3:  # More than 3L in savings
                    dormant_assets.append({
                        "type": "excessive_savings",
                        "value": savings_value,
                        "opportunity_cost": self._calculate_opportunity_cost(savings_value),
                        "recommendation": "Move excess to liquid funds or short-term debt funds"
                    })

        # Check for dormant mutual funds (no transactions in 12+ months)
        if mf_transactions.get('transactions'):
            recent_transactions = []
            cutoff_date = datetime.now() - timedelta(days=365)
            
            for transaction in mf_transactions['transactions']:
                try:
                    transaction_date = datetime.strptime(transaction['transactionDate'], '%Y-%m-%dT%H:%M:%SZ')
                    if transaction_date > cutoff_date:
                        recent_transactions.append(transaction['isinNumber'])
                except:
                    continue

            # Check MF holdings for dormant funds
            mf_analytics = net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
            for scheme in mf_analytics:
                isin = scheme.get('schemeDetail', {}).get('isinNumber')
                if isin not in recent_transactions:
                    current_value = float(scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {}).get('currentValue', {}).get('units', 0))
                    if current_value > 50000:  # Dormant if > ₹50K and no activity
                        dormant_assets.append({
                            "type": "dormant_mutual_fund",
                            "scheme_name": scheme.get('schemeDetail', {}).get('schemeName'),
                            "value": current_value,
                            "recommendation": "Review performance and consider rebalancing"
                        })

        return dormant_assets

    def _analyze_idle_cash(self, bank_transactions: dict) -> dict:
        """Analyze cash patterns to identify idle funds."""
        analysis = {
            "average_monthly_balance": 0,
            "peak_balance": 0,
            "idle_amount": 0,
            "efficiency_score": 0
        }

        if not bank_transactions.get('bankTransactions'):
            return analysis

        # Simplified analysis - in reality, would track daily balances
        monthly_debits = 0
        transaction_count = 0

        all_txns = []
        for bank in bank_transactions['bankTransactions']:
            all_txns.extend(bank.get('txns', []))

        for txn in all_txns:
            try:
                amount_str, _, _, txn_type, _, _ = txn
                if int(txn_type) == 2:  # DEBIT
                    monthly_debits += float(amount_str)
                    transaction_count += 1
            except:
                continue

        if transaction_count > 0:
            # Estimate average monthly expenses
            avg_monthly_expense = monthly_debits / max(1, transaction_count / 30)
            recommended_emergency_fund = avg_monthly_expense * self.emergency_fund_months
            
            analysis["average_monthly_balance"] = avg_monthly_expense * 2  # Rough estimate
            analysis["recommended_emergency_fund"] = recommended_emergency_fund
            
            # If current savings > emergency fund + buffer, flag as idle
            current_savings = analysis["average_monthly_balance"]
            if current_savings > recommended_emergency_fund + 100000:
                analysis["idle_amount"] = current_savings - recommended_emergency_fund - 100000
                analysis["efficiency_score"] = 60  # Moderate efficiency
            else:
                analysis["efficiency_score"] = 85  # Good efficiency

        return analysis

    def _calculate_opportunity_cost(self, amount: float) -> dict:
        """Calculate opportunity cost of keeping money idle."""
        # Assuming 4% savings rate vs 7% liquid fund rate
        annual_opportunity_cost = amount * 0.03  # 3% difference
        
        return {
            "annual_cost": round(annual_opportunity_cost, 2),
            "monthly_cost": round(annual_opportunity_cost / 12, 2),
            "assumption": "3% opportunity cost vs liquid funds"
        }

    def _generate_optimization_opportunities(self, liquidity_breakdown: dict, dormant_assets: list, idle_cash: dict) -> list:
        """Generate specific optimization opportunities."""
        opportunities = []

        # Excessive cash optimization
        if idle_cash.get("idle_amount", 0) > 0:
            opportunities.append({
                "type": "idle_cash_optimization",
                "impact": "high",
                "action": f"Move ₹{idle_cash['idle_amount']:,.0f} to liquid funds",
                "expected_gain": self._calculate_opportunity_cost(idle_cash["idle_amount"])["annual_cost"],
                "timeline": "immediate"
            })

        # Low liquidity rebalancing
        total_value = sum(category["value"] for category in liquidity_breakdown.values())
        if total_value > 0:
            very_low_percentage = (liquidity_breakdown["very_low_liquidity"]["value"] / total_value) * 100
            if very_low_percentage > 40:  # Too much in illiquid assets
                opportunities.append({
                    "type": "liquidity_rebalancing",
                    "impact": "medium",
                    "action": f"Consider liquidating {very_low_percentage:.1f}% illiquid assets",
                    "reason": "Portfolio lacks emergency liquidity",
                    "timeline": "3-6 months"
                })

        # Dormant asset activation
        for asset in dormant_assets:
            if asset["type"] == "dormant_mutual_fund" and asset["value"] > 100000:
                opportunities.append({
                    "type": "dormant_fund_review",
                    "impact": "medium",
                    "action": f"Review {asset['scheme_name']} performance",
                    "value": asset["value"],
                    "timeline": "1 month"
                })

        return opportunities

    def _generate_monetization_strategies(self, liquidity_breakdown: dict, dormant_assets: list) -> list:
        """Generate strategies to monetize illiquid assets."""
        strategies = []

        # Gold monetization if significant gold holdings
        for category in liquidity_breakdown.values():
            for asset in category["assets"]:
                if asset["type"] == "ASSET_TYPE_GOLD" and asset["value"] > 200000:
                    strategies.append({
                        "asset_type": "gold",
                        "strategy": "gold_monetization_scheme",
                        "value": asset["value"],
                        "options": [
                            "Gold ETF conversion for liquidity",
                            "Gold loan against physical gold",
                            "Partial liquidation for portfolio rebalancing"
                        ],
                        "estimated_liquidity": round(asset["value"] * 0.85, 2)  # 85% of gold value
                    })

        # Real estate monetization
        for category in liquidity_breakdown.values():
            for asset in category["assets"]:
                if asset["type"] == "ASSET_TYPE_REAL_ESTATE":
                    strategies.append({
                        "asset_type": "real_estate",
                        "strategy": "property_monetization",
                        "value": asset["value"],
                        "options": [
                            "Rent generation if self-occupied",
                            "Loan against property (LAP)",
                            "REITs investment for diversification"
                        ],
                        "estimated_monthly_income": round(asset["value"] * 0.005, 2)  # 6% annual yield
                    })

        return strategies

    def _assess_emergency_readiness(self, liquidity_breakdown: dict, bank_transactions: dict) -> dict:
        """Assess portfolio's emergency liquidity readiness."""
        high_liquid = liquidity_breakdown["high_liquidity"]["value"]
        medium_liquid = liquidity_breakdown["medium_liquidity"]["value"]
        
        # Estimate monthly expenses from bank transactions
        monthly_expense = self._estimate_monthly_expense(bank_transactions)
        recommended_emergency_fund = monthly_expense * self.emergency_fund_months
        
        immediately_available = high_liquid
        available_within_week = high_liquid + medium_liquid
        
        readiness_score = min(100, (immediately_available / recommended_emergency_fund) * 100)
        
        return {
            "monthly_expense": monthly_expense,
            "recommended_emergency_fund": recommended_emergency_fund,
            "immediately_available": immediately_available,
            "available_within_week": available_within_week,
            "readiness_score": round(readiness_score, 2),
            "status": "excellent" if readiness_score >= 100 else "good" if readiness_score >= 75 else "needs_improvement"
        }

    def _estimate_monthly_expense(self, bank_transactions: dict) -> float:
        """Estimate monthly expenses from bank transaction data."""
        if not bank_transactions.get('bankTransactions'):
            return 50000  # Default assumption

        total_debits = 0
        transaction_count = 0

        all_txns = []
        for bank in bank_transactions['bankTransactions']:
            all_txns.extend(bank.get('txns', []))

        for txn in all_txns:
            try:
                amount_str, _, _, txn_type, _, _ = txn
                if int(txn_type) == 2:  # DEBIT
                    total_debits += float(amount_str)
                    transaction_count += 1
            except:
                continue

        if transaction_count == 0:
            return 50000

        # Rough estimate: total debits / estimated months of data
        estimated_months = max(1, transaction_count / 20)  # Assuming ~20 transactions per month
        return total_debits / estimated_months

    def _suggest_asset_rebalancing(self, liquidity_breakdown: dict) -> list:
        """Suggest asset rebalancing for optimal liquidity."""
        suggestions = []
        total_value = sum(category["value"] for category in liquidity_breakdown.values())
        
        if total_value == 0:
            return suggestions

        # Calculate current percentages
        high_percent = (liquidity_breakdown["high_liquidity"]["value"] / total_value) * 100
        medium_percent = (liquidity_breakdown["medium_liquidity"]["value"] / total_value) * 100
        low_percent = (liquidity_breakdown["low_liquidity"]["value"] / total_value) * 100
        very_low_percent = (liquidity_breakdown["very_low_liquidity"]["value"] / total_value) * 100

        # Ideal allocation: 20% high, 50% medium, 20% low, 10% very low
        if high_percent < 15:
            suggestions.append({
                "type": "increase_liquidity",
                "current": f"{high_percent:.1f}%",
                "target": "20%",
                "action": "Increase emergency fund in savings/liquid funds"
            })

        if very_low_percent > 30:
            suggestions.append({
                "type": "reduce_illiquid_exposure",
                "current": f"{very_low_percent:.1f}%",
                "target": "≤25%",
                "action": "Consider reducing exposure to very illiquid assets"
            })

        if medium_percent < 30:
            suggestions.append({
                "type": "increase_medium_liquidity",
                "current": f"{medium_percent:.1f}%",
                "target": "40-50%",
                "action": "Increase allocation to mutual funds and stocks"
            })

        return suggestions


async def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m agents.illiquid_asset_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]

    print(f"🚀 Initializing Illiquid Asset Agent for {phone_number}...")
    
    mcp_client = FiMCPClient()
    data_agent = DataIntegrationAgent(mcp_client)
    illiquid_agent = IlliquidAssetAgent()

    try:
        # 1. Fetch comprehensive financial data
        financial_data = await data_agent.get_comprehensive_data(phone_number, force_refresh=True)

        # 2. Analyze illiquid assets
        print("\n🔬 Analyzing illiquid and dormant assets...")
        analysis = illiquid_agent.analyze_illiquid_assets(financial_data)
        
        print("\n" + "="*60)
        print("ILLIQUID ASSET OPTIMIZATION REPORT")
        print("="*60)
        print(json.dumps(analysis, indent=2))
        print("="*60)

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())