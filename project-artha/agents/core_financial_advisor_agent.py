import os
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Import all our specialized agents
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient
from agents.risk_profiling_agent import RiskProfilingAgent
from agents.cultural_events_agent import CulturalEventsAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.trust_transparency_agent import TrustTransparencyAgent
from agents.regional_investment_agent import RegionalInvestmentAgent
from agents.debt_management_agent import DebtManagementAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.illiquid_asset_agent import IlliquidAssetAgent


class FinancialAnalysisTool:
    """Enhanced Financial Analysis Tool with Smart Agent Coordination"""
    
    def __init__(self):
        self.mcp_client = FiMCPClient()
        self.data_agent = DataIntegrationAgent(self.mcp_client)
        self.risk_agent = RiskProfilingAgent()
        self.cultural_agent = CulturalEventsAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.trust_agent = TrustTransparencyAgent()
        self.regional_agent = RegionalInvestmentAgent()
        self.anomaly_agent = AnomalyDetectionAgent()
        self.debt_agent = DebtManagementAgent()
        self.illiquid_agent = IlliquidAssetAgent()
        
        # Agent context tracking for intelligent coordination
        self.agent_context = {
            "last_analysis_time": 0,
            "cached_financial_data": None,
            "agent_performance": {},
            "query_patterns": []
        }
        
        print("🎭 Enhanced FinancialAnalysisTool with Smart Coordination initialized.")

    def _assess_query_complexity(self, query: str) -> Dict[str, Any]:
        """Assess query complexity and determine which agents are most relevant"""
        query_lower = query.lower()
        
        # Agent relevance keywords
        agent_relevance = {
            "debt_management": ["loan", "debt", "emi", "credit", "borrow", "mortgage", "home loan"],
            "illiquid_asset": ["optimize", "portfolio", "assets", "gold", "property", "idle", "dormant"],
            "risk_profiling": ["risk", "spending", "behavior", "pattern", "discipline"],
            "market_intelligence": ["market", "stock", "investment", "fund", "returns"],
            "cultural_events": ["festival", "wedding", "diwali", "cultural", "celebration"],
            "regional_investment": ["property", "real estate", "bangalore", "mumbai", "location"],
            "anomaly_detection": ["unusual", "fraud", "suspicious", "alert", "strange"]
        }
        
        # Calculate relevance scores
        relevance_scores = {}
        for agent, keywords in agent_relevance.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            relevance_scores[agent] = score / len(keywords) if keywords else 0
        
        # Determine primary agents (score > 0.2)
        primary_agents = [agent for agent, score in relevance_scores.items() if score > 0.2]
        
        # Always include data_integration as foundation
        if "data_integration" not in primary_agents:
            primary_agents.insert(0, "data_integration")
        
        return {
            "complexity": "high" if len(primary_agents) > 3 else "medium" if len(primary_agents) > 1 else "simple",
            "primary_agents": primary_agents,
            "relevance_scores": relevance_scores,
            "needs_comprehensive": any(word in query_lower for word in ["comprehensive", "complete", "all agents", "full analysis"])
        }

    async def analyze_spending(self, user_id: str) -> str:
        """Enhanced spending analysis with contextual insights"""
        print(f"🔍 Smart spending analysis for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not bank_transactions or "error" in bank_transactions:
                return json.dumps({"error": "Bank transaction data is unavailable.", "data_quality": "error"})
            
            # Core analysis
            profile = self.risk_agent.analyze_spending_patterns(bank_transactions)
            
            # Add contextual insights from other agents
            insights = {"primary_analysis": profile, "contextual_insights": []}
            
            # Add cultural context if relevant
            try:
                cultural_forecast = self.cultural_agent.forecast_cultural_expenses(bank_transactions)
                if cultural_forecast and not isinstance(cultural_forecast, str):
                    insights["contextual_insights"].append({
                        "source": "cultural_intelligence",
                        "insight": f"Cultural spending shows {cultural_forecast.get('confidence_level', 'moderate')} predictability"
                    })
            except:
                pass
            
            # Add anomaly context
            try:
                anomalies = self.anomaly_agent.detect_spending_anomalies(bank_transactions)
                if anomalies and not isinstance(anomalies, str):
                    alert_count = len(anomalies.get('spending_anomalies', []))
                    if alert_count > 0:
                        insights["contextual_insights"].append({
                            "source": "anomaly_detection",
                            "insight": f"{alert_count} spending anomalies detected - review recommended"
                        })
            except:
                pass
            
            insights["data_quality"] = "good"
            insights["confidence"] = 0.85
            
            return self.trust_agent.add_risk_explanations(insights)
            
        except Exception as e:
            print(f"Error in spending analysis: {e}")
            return json.dumps({"error": f"Analysis failed: {e}", "data_quality": "error"})

    async def get_comprehensive_financial_insights(self, user_id: str, query: str) -> str:
        """New comprehensive analysis tool that intelligently coordinates all agents"""
        print(f"🎯 Comprehensive financial insights for: {query}")
        
        start_time = time.time()
        
        try:
            # Assess query complexity
            query_analysis = self._assess_query_complexity(query)
            print(f"📊 Query complexity: {query_analysis['complexity']}, Primary agents: {query_analysis['primary_agents']}")
            
            # Get foundational data
            financial_data = await self._get_or_fetch_data(user_id)
            
            # Coordinate relevant agents based on query
            agent_results = {}
            confidence_scores = {}
            
            # Always include data foundation
            agent_results["data_foundation"] = self._extract_key_financial_metrics(financial_data)
            confidence_scores["data_foundation"] = 0.95
            
            # Execute primary agents based on relevance
            if "debt_management" in query_analysis['primary_agents']:
                credit_report = financial_data.get("fetch_credit_report")
                bank_transactions = financial_data.get("fetch_bank_transactions")
                if credit_report and "error" not in credit_report:
                    debt_analysis = self.debt_agent.analyze_debt_summary(credit_report, bank_transactions)
                    agent_results["debt_intelligence"] = debt_analysis
                    confidence_scores["debt_intelligence"] = 0.9
            
            if "illiquid_asset" in query_analysis['primary_agents']:
                illiquid_analysis = self.illiquid_agent.analyze_illiquid_assets(financial_data)
                agent_results["asset_optimization"] = illiquid_analysis
                confidence_scores["asset_optimization"] = 0.85
            
            if "risk_profiling" in query_analysis['primary_agents']:
                bank_transactions = financial_data.get("fetch_bank_transactions")
                if bank_transactions and "error" not in bank_transactions:
                    risk_analysis = self.risk_agent.analyze_spending_patterns(bank_transactions)
                    agent_results["behavioral_insights"] = risk_analysis
                    confidence_scores["behavioral_insights"] = 0.8
            
            if "market_intelligence" in query_analysis['primary_agents']:
                market_analysis = await self.market_agent.get_market_info(query)
                agent_results["market_intelligence"] = market_analysis
                confidence_scores["market_intelligence"] = 0.75
            
            if "regional_investment" in query_analysis['primary_agents']:
                regional_analysis = await self.regional_agent.get_real_estate_info(query)
                agent_results["location_intelligence"] = regional_analysis
                confidence_scores["location_intelligence"] = 0.7
            
            # Generate intelligent synthesis
            analysis_time = time.time() - start_time
            synthesis = self._synthesize_agent_results(agent_results, confidence_scores, query, analysis_time)
            
            return synthesis
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return f"I encountered an error while analyzing your request: {str(e)}. Please try again or rephrase your question."

    async def _get_or_fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Smart data fetching with caching"""
        current_time = time.time()
        
        # Use cached data if recent (within 5 minutes)
        if (self.agent_context["cached_financial_data"] and 
            current_time - self.agent_context["last_analysis_time"] < 300):
            print("📋 Using cached financial data")
            return self.agent_context["cached_financial_data"]
        
        # Fetch fresh data
        print("📊 Fetching fresh financial data...")
        financial_data = await self.data_agent.get_comprehensive_data(user_id, force_refresh=True)
        
        # Cache for future use
        self.agent_context["cached_financial_data"] = financial_data
        self.agent_context["last_analysis_time"] = current_time
        
        return financial_data

    def _extract_key_financial_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key financial metrics for synthesis"""
        metrics = {}
        
        # Net worth
        net_worth_data = financial_data.get('fetch_net_worth', {})
        if net_worth_data.get('netWorthResponse'):
            total_value = net_worth_data['netWorthResponse'].get('totalNetWorthValue', {})
            if total_value:
                metrics['net_worth'] = float(total_value.get('units', 0))
        
        # Income estimation (from bank transactions)
        bank_transactions = financial_data.get('fetch_bank_transactions', {})
        if bank_transactions.get('bankTransactions'):
            total_credits = 0
            credit_count = 0
            
            for bank in bank_transactions['bankTransactions']:
                for txn in bank.get('txns', []):
                    try:
                        amount_str, _, _, txn_type, _, _ = txn
                        if int(txn_type) == 1:  # CREDIT
                            total_credits += float(amount_str)
                            credit_count += 1
                    except:
                        continue
            
            if credit_count > 0:
                # Rough monthly income estimate
                estimated_months = max(1, credit_count / 15)  # ~15 credits per month
                metrics['estimated_monthly_income'] = total_credits / estimated_months
        
        # Credit score
        credit_report = financial_data.get('fetch_credit_report', {})
        if credit_report.get('creditScore'):
            score_data = credit_report['creditScore'].get('bureauScore', {})
            if score_data:
                metrics['credit_score'] = int(score_data.get('score', 0))
        
        return metrics

    def _synthesize_agent_results(self, agent_results: Dict[str, Any], confidence_scores: Dict[str, float],
                                query: str, analysis_time: float) -> str:
        """Intelligently synthesize results from multiple agents"""
        
        synthesis_parts = []
        
        # Header with query context
        synthesis_parts.append(f"**🎯 Comprehensive Financial Analysis**")
        synthesis_parts.append(f"Query: {query}")
        synthesis_parts.append(f"Analysis completed in {analysis_time:.1f}s using {len(agent_results)} intelligence sources\n")
        
        # Key financial foundation
        if "data_foundation" in agent_results:
            foundation = agent_results["data_foundation"]
            net_worth = foundation.get('net_worth', 0)
            income = foundation.get('estimated_monthly_income', 0)
            credit_score = foundation.get('credit_score', 0)
            
            synthesis_parts.append("**📊 Financial Foundation:**")
            if net_worth > 0:
                synthesis_parts.append(f"• Net Worth: ₹{net_worth/100000:.1f}L")
            if income > 0:
                synthesis_parts.append(f"• Estimated Monthly Income: ₹{income:,.0f}")
            if credit_score > 0:
                synthesis_parts.append(f"• Credit Score: {credit_score}")
            synthesis_parts.append("")
        
        # Debt analysis (if relevant)
        if "debt_intelligence" in agent_results:
            debt_data = agent_results["debt_intelligence"]
            if isinstance(debt_data, dict):
                synthesis_parts.append("**💳 Debt Analysis:**")
                total_debt = debt_data.get('total_outstanding_debt', 0)
                if total_debt > 0:
                    synthesis_parts.append(f"• Total Outstanding Debt: ₹{total_debt:,.0f}")
                
                recommendations = debt_data.get('debt_optimization_recommendations', [])
                if recommendations:
                    synthesis_parts.append("• Key Recommendations:")
                    for rec in recommendations[:2]:  # Top 2
                        synthesis_parts.append(f"  - {rec}")
                synthesis_parts.append("")
        
        # Asset optimization (if relevant)
        if "asset_optimization" in agent_results:
            asset_data = agent_results["asset_optimization"]
            if isinstance(asset_data, dict):
                synthesis_parts.append("**💎 Asset Optimization:**")
                liquidity_score = asset_data.get('liquidity_score', 0)
                if liquidity_score > 0:
                    synthesis_parts.append(f"• Portfolio Liquidity Score: {liquidity_score}/100")
                
                opportunities = asset_data.get('optimization_opportunities', [])
                if opportunities:
                    synthesis_parts.append("• Optimization Opportunities:")
                    for opp in opportunities[:2]:  # Top 2
                        action = opp.get('action', 'Review recommended')
                        impact = opp.get('impact', 'medium')
                        synthesis_parts.append(f"  - {action} (Impact: {impact})")
                synthesis_parts.append("")
        
        # Behavioral insights (if relevant) 
        if "behavioral_insights" in agent_results:
            behavioral_data = agent_results["behavioral_insights"]
            if isinstance(behavioral_data, dict):
                synthesis_parts.append("**🧠 Behavioral Intelligence:**")
                
                spending_ratio = behavioral_data.get('weekend_weekday_spending_ratio', 0)
                if spending_ratio > 0:
                    discipline_level = "High" if spending_ratio < 1.2 else "Moderate" if spending_ratio < 1.8 else "Needs Improvement"
                    synthesis_parts.append(f"• Spending Discipline: {discipline_level} ({spending_ratio:.1f}x weekend ratio)")
                
                risk_tolerance = behavioral_data.get('risk_tolerance_indicator', 'moderate')
                synthesis_parts.append(f"• Risk Profile: {risk_tolerance.title()}")
                synthesis_parts.append("")
        
        # Market context (if relevant)
        if "market_intelligence" in agent_results:
            market_data = agent_results["market_intelligence"] 
            if isinstance(market_data, str) and len(market_data) > 50:
                synthesis_parts.append("**📈 Market Intelligence:**")
                # Extract key insights from market data (first 200 chars)
                market_summary = market_data[:200] + "..." if len(market_data) > 200 else market_data
                synthesis_parts.append(f"• {market_summary}")
                synthesis_parts.append("")
        
        # Confidence and transparency
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        high_confidence_agents = [name for name, score in confidence_scores.items() if score > 0.8]
        
        synthesis_parts.append("**🔍 Analysis Transparency:**")
        synthesis_parts.append(f"• Overall Confidence: {overall_confidence:.0%}")
        synthesis_parts.append(f"• High-Confidence Sources: {len(high_confidence_agents)}/{len(agent_results)}")
        synthesis_parts.append(f"• Primary Intelligence: {', '.join(high_confidence_agents)}")
        
        return "\n".join(synthesis_parts)

    # Keep all existing individual tool methods
    async def forecast_cultural_spending(self, user_id: str) -> str:
        """Provides a forecast for culturally significant expenses."""
        print(f"Tool triggered: Cultural spending forecast for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not bank_transactions or "error" in bank_transactions:
                return json.dumps({"error": "Bank transaction data is unavailable."})
                
            forecast = self.cultural_agent.forecast_cultural_expenses(bank_transactions)
            enriched_response = self.trust_agent.add_cultural_explanations(forecast)
            return enriched_response
            
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {e}"})

    async def get_market_data(self, query: str) -> str:
        """Fetches current market intelligence and trends."""
        print(f"Tool triggered: Market data for query: {query}")
        try:
            market_info = await self.market_agent.get_market_info(query)
            return market_info
        except Exception as e:
            return f"Market data unavailable: {e}"

    async def get_regional_investment_info(self, query: str) -> str:
        """Provides regional investment insights."""
        print(f"Tool triggered: Regional investment info for: {query}")
        try:
            regional_info = await self.regional_agent.get_real_estate_info(query)
            return regional_info
        except Exception as e:
            return f"Regional investment data unavailable: {e}"

    async def get_debt_summary(self, user_id: str) -> str:
        """Analyzes debt obligations and optimization strategies."""
        print(f"Tool triggered: Debt analysis for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            credit_report = financial_data.get("fetch_credit_report")
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not credit_report or "error" in credit_report:
                return json.dumps({"error": "Credit report data is unavailable."})
                
            debt_analysis = self.debt_agent.analyze_debt_summary(credit_report, bank_transactions)
            enriched_response = self.trust_agent.add_debt_explanations(debt_analysis)
            return enriched_response
            
        except Exception as e:
            return json.dumps({"error": f"Debt analysis failed: {e}"})

    async def get_risk_analysis_explanation(self, user_id: str) -> str:
        """Provides detailed risk profiling with explanations."""
        print(f"Tool triggered: Risk analysis explanation for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not bank_transactions or "error" in bank_transactions:
                return "Risk analysis unavailable due to insufficient transaction data."
                
            risk_profile = self.risk_agent.analyze_spending_patterns(bank_transactions)
            return self.trust_agent.add_risk_explanations(risk_profile)
            
        except Exception as e:
            return f"Risk analysis error: {e}"

    async def explain_anomaly_detection_process(self, user_id: str) -> str:
        """Explains the anomaly detection process and findings."""
        print(f"Tool triggered: Anomaly detection explanation for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            bank_transactions = financial_data.get("fetch_bank_transactions")
            
            if not bank_transactions or "error" in bank_transactions:
                return "Anomaly detection unavailable due to insufficient transaction data."
                
            anomalies = self.anomaly_agent.detect_spending_anomalies(bank_transactions)
            return self.trust_agent.add_anomaly_explanations(anomalies)
            
        except Exception as e:
            return f"Anomaly detection error: {e}"

    async def get_illiquid_asset_optimization(self, user_id: str) -> str:
        """Analyzes illiquid and dormant assets with optimization recommendations."""
        print(f"Tool triggered: Illiquid asset optimization for {user_id}")
        try:
            financial_data = await self._get_or_fetch_data(user_id)
            analysis = self.illiquid_agent.analyze_illiquid_assets(financial_data)
            enriched_response = self.trust_agent.add_illiquid_asset_explanations(analysis)
            return enriched_response
            
        except Exception as e:
            return f"Illiquid asset analysis error: {e}"


class CoreFinancialAdvisorAgent:
    """Enhanced Core Financial Advisor with Intelligent Multi-Agent Coordination"""
    
    def __init__(self):
        self.analysis_tool = FinancialAnalysisTool()
        
        # Enhanced agent with intelligent tool selection
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="core_financial_advisor",
            instruction=(
                "You are an intelligent financial advisor powered by 10 specialized AI agents. "
                "Your role is to provide comprehensive, contextual financial insights by intelligently "
                "coordinating multiple agents based on the user's specific needs.\n\n"
                
                "INTELLIGENT COORDINATION PRINCIPLES:\n"
                "• Use get_comprehensive_financial_insights for complex queries requiring multiple agents\n"
                "• Use specific tools (analyze_spending, get_debt_summary, etc.) for focused questions\n"
                "• Always provide context and reasoning behind recommendations\n"
                "• Quantify impacts with specific amounts and timelines\n"
                "• Highlight both opportunities and risks\n"
                "• Ensure recommendations are culturally appropriate for Indian context\n\n"
                
                "TOOL SELECTION STRATEGY:\n"
                "Complex/broad queries → get_comprehensive_financial_insights\n"
                "Spending analysis → analyze_spending\n"
                "Debt questions → get_debt_summary\n"
                "Market queries → get_market_data\n"
                "Property/location → get_regional_investment_info\n"
                "Asset optimization → get_illiquid_asset_optimization\n"
                "Risk profiling → get_risk_analysis_explanation\n\n"
                
                "Always explain your reasoning and provide actionable next steps."
            ),
            tools=[
                self.analysis_tool.get_comprehensive_financial_insights,  # Primary orchestrator
                self.analysis_tool.analyze_spending,
                self.analysis_tool.forecast_cultural_spending,
                self.analysis_tool.get_market_data,
                self.analysis_tool.get_regional_investment_info,
                self.analysis_tool.get_debt_summary,
                self.analysis_tool.get_risk_analysis_explanation,
                self.analysis_tool.explain_anomaly_detection_process,
                self.analysis_tool.get_illiquid_asset_optimization
            ]
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="project_artha_advisor",
            session_service=self.session_service
        )
        
        print("CoreFinancialAdvisorAgent initialized with intelligent coordination.")

    async def process_query(self, user_query: str, user_id: str) -> str:
        """Enhanced query processing with intelligent agent coordination"""
        
        print(f"Processing query for {user_id}: '{user_query}'")
        
        session = await self.session_service.create_session(
            app_name="project_artha_advisor",
            user_id=user_id
        )
        
        # Enhanced prompt that guides intelligent tool selection
        enhanced_query = f"""
        Financial Query: {user_query}
        User ID: {user_id}
        
        Please analyze this query and use the most appropriate combination of tools to provide 
        comprehensive, actionable financial advice. For complex queries involving multiple 
        financial aspects, use get_comprehensive_financial_insights. For specific focused 
        questions, use the relevant specialized tools.
        
        Ensure your response includes:
        1. Clear recommendations with specific amounts/timelines
        2. Risk considerations and mitigation strategies  
        3. Reasoning behind your advice
        4. Immediate actionable next steps
        """
        
        content = Content(role="user", parts=[Part(text=enhanced_query)])
        
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text if event.content.parts else ""
                break
        
        # Add final transparency layer  
        enriched_response = self.analysis_tool.trust_agent.add_financial_explanations(
            response_text if response_text else "I could not process your request at this time."
        )

        return enriched_response


async def main():
    import sys
    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python -m agents.core_financial_advisor_agent <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]
    advisor_agent = CoreFinancialAdvisorAgent()

    # Test with a comprehensive query
    query = "Can I afford a ₹50L home loan? Please provide comprehensive analysis from all relevant agents."
    
    try:
        final_response = await advisor_agent.process_query(user_query=query, user_id=phone_number)
        
        print("\n" + "="*60)
        print("🤖 CORE FINANCIAL ADVISOR RESPONSE")
        print("="*60)
        print(final_response)
        print("="*60)

    except Exception as e:
        print(f"\n❌ A critical error occurred in the main loop: {e}")

if __name__ == "__main__":
    asyncio.run(main())