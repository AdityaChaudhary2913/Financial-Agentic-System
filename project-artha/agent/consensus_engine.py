import asyncio
import json
import time
from typing import Dict, List, Any, Tuple
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Import all our agents
from agents.data_integration_agent import DataIntegrationAgent, FiMCPClient
from agents.risk_profiling_agent import RiskProfilingAgent
from agents.cultural_events_agent import CulturalEventsAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.trust_transparency_agent import TrustTransparencyAgent
from agents.regional_investment_agent import RegionalInvestmentAgent
from agents.debt_management_agent import DebtManagementAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.illiquid_asset_agent import IlliquidAssetAgent

class AgentOutputQuality:
    """Evaluates the quality and reliability of agent outputs"""
    
    @staticmethod
    def evaluate_output_quality(agent_name: str, output: Any, query_context: str) -> Dict[str, float]:
        """
        Evaluates agent output quality across multiple dimensions
        Returns scores between 0.0 and 1.0 for each dimension
        """
        if isinstance(output, str) and ("error" in output.lower() or "unavailable" in output.lower()):
            return {
                "data_availability": 0.0,
                "relevance_score": 0.0,
                "confidence_level": 0.0,
                "actionability": 0.0,
                "specificity": 0.0
            }
        
        # Base quality scores by agent type
        quality_metrics = {
            "data_availability": 1.0,  # Assume data is available if no error
            "relevance_score": AgentOutputQuality._calculate_relevance(agent_name, query_context),
            "confidence_level": AgentOutputQuality._extract_confidence(output),
            "actionability": AgentOutputQuality._assess_actionability(output),
            "specificity": AgentOutputQuality._measure_specificity(output)
        }
        
        return quality_metrics
    
    @staticmethod
    def _calculate_relevance(agent_name: str, query_context: str) -> float:
        """Calculate relevance of agent to query context"""
        query_lower = query_context.lower()
        
        relevance_keywords = {
            "risk_profiling": ["risk", "behavior", "spending", "pattern", "psychology"],
            "debt_management": ["loan", "debt", "emi", "credit", "borrow"],
            "market_intelligence": ["market", "stock", "investment", "price", "trend"],
            "cultural_events": ["festival", "wedding", "diwali", "cultural", "family"],
            "regional_investment": ["property", "real estate", "location", "city", "area"],
            "anomaly_detection": ["unusual", "fraud", "anomaly", "suspicious", "alert"],
            "illiquid_asset": ["gold", "property", "illiquid", "dormant", "monetize"],
            "data_integration": ["data", "account", "balance", "fetch", "integrate"],
            "trust_transparency": ["explain", "why", "how", "transparency", "audit"]
        }
        
        agent_key = agent_name.lower().replace("agent", "").replace("_", "")
        keywords = relevance_keywords.get(agent_key, [])
        
        matches = sum(1 for keyword in keywords if keyword in query_lower)
        max_possible = len(keywords) if keywords else 1
        
        base_relevance = matches / max_possible
        
        # Boost for always-relevant agents
        if agent_key in ["data_integration", "trust_transparency"]:
            base_relevance = max(base_relevance, 0.7)
            
        return min(1.0, base_relevance + 0.2)  # Minimum 0.2 relevance for all agents
    
    @staticmethod
    def _extract_confidence(output: Any) -> float:
        """Extract confidence indicators from output"""
        if isinstance(output, dict):
            # Look for explicit confidence scores
            for key in ["confidence", "confidence_score", "reliability", "accuracy"]:
                if key in output:
                    value = output[key]
                    if isinstance(value, (int, float)):
                        return min(1.0, value / 100.0) if value > 1 else value
                    elif isinstance(value, str) and "%" in value:
                        return float(value.replace("%", "")) / 100.0
            
            # Check for error indicators
            if output.get("error") or output.get("warning"):
                return 0.6
                
            # Check data completeness
            if output.get("data_quality") == "good":
                return 0.9
            elif output.get("data_quality") == "warning":
                return 0.7
            elif output.get("data_quality") == "error":
                return 0.3
        
        return 0.8  # Default confidence
    
    @staticmethod
    def _assess_actionability(output: Any) -> float:
        """Assess how actionable the output is"""
        if isinstance(output, dict):
            actionable_keys = ["recommendations", "actions", "steps", "suggestions", "opportunities"]
            action_score = sum(1 for key in actionable_keys if key in output and output[key])
            
            # Check for specific amounts, dates, percentages
            output_str = str(output).lower()
            specificity_indicators = ["₹", "rs", "%", "month", "year", "days"]
            specificity_score = sum(1 for indicator in specificity_indicators if indicator in output_str)
            
            return min(1.0, (action_score * 0.4 + specificity_score * 0.1))
        
        return 0.5  # Default actionability

    @staticmethod
    def _measure_specificity(output: Any) -> float:
        """Measure how specific and detailed the output is"""
        if isinstance(output, dict):
            # Count specific data points
            numeric_fields = 0
            total_fields = 0
            
            def count_fields(obj, depth=0):
                nonlocal numeric_fields, total_fields
                if depth > 3:  # Prevent infinite recursion
                    return
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        total_fields += 1
                        if isinstance(value, (int, float)):
                            numeric_fields += 1
                        elif isinstance(value, (dict, list)):
                            count_fields(value, depth + 1)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            count_fields(item, depth + 1)
            
            count_fields(output)
            return min(1.0, numeric_fields / max(1, total_fields))
        
        return 0.5


class ConsensusEngine:
    """
    Advanced consensus mechanism that orchestrates all 10 agents with dynamic weighting,
    conflict resolution, and intelligent synthesis
    """
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        
        # Initialize all agents
        self.agents = {
            "data_integration": DataIntegrationAgent(mcp_client),
            "risk_profiling": RiskProfilingAgent(),
            "cultural_events": CulturalEventsAgent(),
            "market_intelligence": MarketIntelligenceAgent(),
            "trust_transparency": TrustTransparencyAgent(),
            "regional_investment": RegionalInvestmentAgent(),
            "debt_management": DebtManagementAgent(),
            "anomaly_detection": AnomalyDetectionAgent(),
            "illiquid_asset": IlliquidAssetAgent()
        }
        
        # Initialize consensus reasoning agent
        self.consensus_agent = LlmAgent(
            model="gemini-2.0-flash",
            name="consensus_orchestrator",
            instruction="""
            You are the Ultimate Financial Consensus Orchestrator. Your role is to analyze outputs 
            from multiple specialized financial agents and create intelligent, weighted recommendations.
            
            CORE RESPONSIBILITIES:
            1. **Dynamic Weighting**: Assign contextual weights to each agent's output based on:
               - Relevance to the user's query
               - Quality and confidence of the data
               - Agent's domain expertise for this specific question
               - Potential impact of the recommendation
            
            2. **Conflict Resolution**: When agents disagree:
               - Identify the source of disagreement
               - Evaluate evidence quality from each side
               - Consider risk implications
               - Provide nuanced recommendations that acknowledge trade-offs
            
            3. **Intelligent Synthesis**: Create coherent recommendations that:
               - Combine insights from multiple agents
               - Prioritize by impact and feasibility
               - Provide specific, actionable next steps
               - Explain the reasoning process transparently
            
            DECISION FRAMEWORK:
            - High Impact + High Confidence = Immediate Action
            - High Impact + Low Confidence = Cautious Recommendation
            - Low Impact + High Confidence = Secondary Suggestion
            - Low Impact + Low Confidence = Monitor/Research
            
            Always explain WHY you weighted certain agents higher and HOW conflicts were resolved.
            """,
            output_key="consensus_result"
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.consensus_agent,
            app_name="consensus_engine",
            session_service=self.session_service
        )

    async def orchestrate_comprehensive_analysis(self, user_id: str, user_query: str) -> Dict[str, Any]:
        """
        Main orchestration method that coordinates all agents and creates consensus
        """
        print(f"🎭 Starting comprehensive multi-agent analysis for: {user_query}")
        
        analysis_start_time = time.time()
        
        # Step 1: Gather data from all agents
        agent_outputs = await self._gather_agent_outputs(user_id, user_query)
        
        # Step 2: Evaluate output quality
        quality_scores = self._evaluate_all_outputs(agent_outputs, user_query)
        
        # Step 3: Determine agent relevance and weights
        dynamic_weights = await self._calculate_dynamic_weights(agent_outputs, quality_scores, user_query)
        
        # Step 4: Detect and resolve conflicts
        conflicts = self._detect_conflicts(agent_outputs, dynamic_weights)
        conflict_resolutions = await self._resolve_conflicts(conflicts, user_query)
        
        # Step 5: Generate consensus recommendation
        consensus_result = await self._generate_consensus(
            agent_outputs, dynamic_weights, conflict_resolutions, user_query
        )
        
        analysis_time = time.time() - analysis_start_time
        
        # Step 6: Package final result
        final_result = {
            "consensus_recommendation": consensus_result,
            "agent_outputs": agent_outputs,
            "quality_scores": quality_scores,
            "dynamic_weights": dynamic_weights,
            "conflicts_detected": conflicts,
            "conflict_resolutions": conflict_resolutions,
            "analysis_metadata": {
                "total_agents_consulted": len([o for o in agent_outputs.values() if o is not None]),
                "analysis_time_seconds": round(analysis_time, 2),
                "consensus_confidence": self._calculate_overall_confidence(dynamic_weights, quality_scores),
                "primary_agents": [name for name, weight in dynamic_weights.items() if weight > 0.7]
            }
        }
        
        return final_result

    async def _gather_agent_outputs(self, user_id: str, user_query: str) -> Dict[str, Any]:
        """Gather outputs from all relevant agents"""
        outputs = {}
        
        # Always get foundational data
        try:
            print("📊 Gathering foundational data...")
            financial_data = await self.agents["data_integration"].get_comprehensive_data(user_id, force_refresh=True)
            outputs["data_integration"] = financial_data
        except Exception as e:
            print(f"⚠️ Data integration failed: {e}")
            outputs["data_integration"] = None
            return outputs  # Can't proceed without data
        
        # Gather intelligence from specialized agents
        agent_tasks = [
            ("risk_profiling", self._get_risk_analysis, financial_data),
            ("cultural_events", self._get_cultural_analysis, financial_data),
            ("market_intelligence", self._get_market_analysis, user_query),
            ("regional_investment", self._get_regional_analysis, user_query),
            ("debt_management", self._get_debt_analysis, financial_data),
            ("anomaly_detection", self._get_anomaly_analysis, financial_data),
            ("illiquid_asset", self._get_illiquid_analysis, financial_data)
        ]
        
        # Execute agent tasks concurrently for speed
        results = await asyncio.gather(
            *[task_func(task_data) for _, task_func, task_data in agent_tasks],
            return_exceptions=True
        )
        
        # Map results back to agent names
        for i, (agent_name, _, _) in enumerate(agent_tasks):
            result = results[i]
            if isinstance(result, Exception):
                print(f"⚠️ {agent_name} failed: {result}")
                outputs[agent_name] = None
            else:
                outputs[agent_name] = result
                print(f"✅ {agent_name} completed")
        
        return outputs

    async def _get_risk_analysis(self, financial_data: dict) -> Any:
        """Get risk profiling analysis"""
        bank_transactions = financial_data.get("fetch_bank_transactions")
        if bank_transactions and "error" not in bank_transactions:
            return self.agents["risk_profiling"].analyze_spending_patterns(bank_transactions)
        return None

    async def _get_cultural_analysis(self, financial_data: dict) -> Any:
        """Get cultural events analysis"""
        bank_transactions = financial_data.get("fetch_bank_transactions")
        if bank_transactions and "error" not in bank_transactions:
            return self.agents["cultural_events"].forecast_cultural_expenses(bank_transactions)
        return None

    async def _get_market_analysis(self, query: str) -> Any:
        """Get market intelligence"""
        return await self.agents["market_intelligence"].get_market_info(query)

    async def _get_regional_analysis(self, query: str) -> Any:
        """Get regional investment analysis"""
        return await self.agents["regional_investment"].get_real_estate_info(query)

    async def _get_debt_analysis(self, financial_data: dict) -> Any:
        """Get debt management analysis"""
        credit_report = financial_data.get("fetch_credit_report")
        bank_transactions = financial_data.get("fetch_bank_transactions")
        if credit_report and "error" not in credit_report:
            return self.agents["debt_management"].analyze_debt_summary(credit_report, bank_transactions)
        return None

    async def _get_anomaly_analysis(self, financial_data: dict) -> Any:
        """Get anomaly detection analysis"""
        bank_transactions = financial_data.get("fetch_bank_transactions")
        if bank_transactions and "error" not in bank_transactions:
            return self.agents["anomaly_detection"].detect_spending_anomalies(bank_transactions)
        return None

    async def _get_illiquid_analysis(self, financial_data: dict) -> Any:
        """Get illiquid asset analysis"""
        return self.agents["illiquid_asset"].analyze_illiquid_assets(financial_data)

    def _evaluate_all_outputs(self, agent_outputs: Dict[str, Any], user_query: str) -> Dict[str, Dict[str, float]]:
        """Evaluate quality of all agent outputs"""
        quality_scores = {}
        
        for agent_name, output in agent_outputs.items():
            if output is not None:
                quality_scores[agent_name] = AgentOutputQuality.evaluate_output_quality(
                    agent_name, output, user_query
                )
            else:
                quality_scores[agent_name] = {
                    "data_availability": 0.0,
                    "relevance_score": 0.0,
                    "confidence_level": 0.0,
                    "actionability": 0.0,
                    "specificity": 0.0
                }
        
        return quality_scores

    async def _calculate_dynamic_weights(self, agent_outputs: Dict[str, Any], 
                                       quality_scores: Dict[str, Dict[str, float]], 
                                       user_query: str) -> Dict[str, float]:
        """Calculate dynamic weights for each agent based on context and quality"""
        
        # Prepare weight calculation context
        weight_context = {
            "user_query": user_query,
            "agent_quality_summary": {},
            "available_agents": []
        }
        
        for agent_name, scores in quality_scores.items():
            if agent_outputs.get(agent_name) is not None:
                weight_context["available_agents"].append(agent_name)
                weight_context["agent_quality_summary"][agent_name] = {
                    "overall_quality": sum(scores.values()) / len(scores),
                    "relevance": scores["relevance_score"],
                    "confidence": scores["confidence_level"],
                    "actionability": scores["actionability"]
                }
        
        # Use LLM to determine contextual weights
        session = await self.session_service.create_session(
            app_name="consensus_engine",
            user_id="weight_calculator"
        )
        
        weight_prompt = f"""
        Analyze this financial query and determine optimal weights for each agent:
        
        Query: "{user_query}"
        
        Available Agents and Their Quality Scores:
        {json.dumps(weight_context["agent_quality_summary"], indent=2)}
        
        Consider:
        1. Which agents are most relevant to this specific query?
        2. Which agents have the highest quality data?
        3. What's the potential impact of each agent's recommendations?
        4. Are there synergies between certain agents?
        
        Provide weights (0.0 to 1.0) for each agent. Higher weights = more influence on final decision.
        Focus on expertise relevance and data quality.
        
        Respond with a JSON object containing agent weights and brief reasoning.
        """
        
        content = Content(role="user", parts=[Part(text=weight_prompt)])
        response_text = ""
        
        async for event in self.runner.run_async(
            user_id="weight_calculator",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text if event.content.parts else ""
                break
        
        # Parse weights from LLM response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                weights_data = json.loads(json_match.group())
                
                # Normalize weights
                total_weight = sum(float(w) for w in weights_data.values() if isinstance(w, (int, float)))
                if total_weight > 0:
                    normalized_weights = {
                        agent: float(weight) / total_weight 
                        for agent, weight in weights_data.items() 
                        if isinstance(weight, (int, float))
                    }
                    return normalized_weights
        except:
            pass
        
        # Fallback: Calculate weights based on quality scores
        fallback_weights = {}
        for agent_name in weight_context["available_agents"]:
            quality = weight_context["agent_quality_summary"][agent_name]
            weight = (quality["relevance"] * 0.4 + 
                     quality["confidence"] * 0.3 + 
                     quality["actionability"] * 0.3)
            fallback_weights[agent_name] = weight
        
        # Normalize fallback weights
        total = sum(fallback_weights.values())
        if total > 0:
            return {agent: weight/total for agent, weight in fallback_weights.items()}
        
        return {}

    def _detect_conflicts(self, agent_outputs: Dict[str, Any], weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect conflicts between agent recommendations"""
        conflicts = []
        
        # Look for contradictory recommendations
        high_weight_agents = [name for name, weight in weights.items() if weight > 0.3]
        
        # Example conflict detection logic (can be expanded)
        for i, agent1 in enumerate(high_weight_agents):
            for agent2 in high_weight_agents[i+1:]:
                output1 = agent_outputs.get(agent1)
                output2 = agent_outputs.get(agent2)
                
                if output1 and output2:
                    conflict = self._analyze_agent_conflict(agent1, output1, agent2, output2)
                    if conflict:
                        conflicts.append(conflict)
        
        return conflicts

    def _analyze_agent_conflict(self, agent1: str, output1: Any, agent2: str, output2: Any) -> Dict[str, Any]:
        """Analyze potential conflict between two agents"""
        # This is a simplified conflict detection - can be made more sophisticated
        
        # Check for opposite recommendations
        str1 = str(output1).lower()
        str2 = str(output2).lower()
        
        opposing_pairs = [
            ("buy", "sell"), ("increase", "decrease"), ("invest", "divest"),
            ("recommend", "avoid"), ("good", "bad"), ("high", "low")
        ]
        
        for word1, word2 in opposing_pairs:
            if word1 in str1 and word2 in str2:
                return {
                    "type": "opposing_recommendation",
                    "agent1": agent1,
                    "agent2": agent2,
                    "conflict_area": f"{word1} vs {word2}",
                    "severity": "medium"
                }
        
        return None

    async def _resolve_conflicts(self, conflicts: List[Dict[str, Any]], user_query: str) -> Dict[str, Any]:
        """Resolve conflicts between agents using LLM reasoning"""
        if not conflicts:
            return {"resolution": "No conflicts detected", "strategy": "proceed_with_consensus"}
        
        session = await self.session_service.create_session(
            app_name="consensus_engine",
            user_id="conflict_resolver"
        )
        
        conflict_prompt = f"""
        Resolve these conflicts between financial agents for query: "{user_query}"
        
        Detected Conflicts:
        {json.dumps(conflicts, indent=2)}
        
        For each conflict, provide:
        1. Root cause analysis
        2. Which perspective has stronger evidence
        3. Recommended resolution strategy
        4. How to communicate this to the user
        
        Focus on risk management and user's best interests.
        """
        
        content = Content(role="user", parts=[Part(text=conflict_prompt)])
        response_text = ""
        
        async for event in self.runner.run_async(
            user_id="conflict_resolver",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text if event.content.parts else ""
                break
        
        return {
            "conflicts_analyzed": len(conflicts),
            "resolution_strategy": response_text,
            "confidence": "high" if len(conflicts) <= 2 else "medium"
        }

    async def _generate_consensus(self, agent_outputs: Dict[str, Any], weights: Dict[str, float],
                                conflict_resolutions: Dict[str, Any], user_query: str) -> str:
        """Generate final consensus recommendation"""
        
        session = await self.session_service.create_session(
            app_name="consensus_engine",
            user_id="final_synthesis"
        )
        
        # Prepare synthesis context
        weighted_outputs = []
        for agent_name, output in agent_outputs.items():
            if output is not None and weights.get(agent_name, 0) > 0:
                weighted_outputs.append({
                    "agent": agent_name,
                    "weight": weights[agent_name],
                    "output": output
                })
        
        # Sort by weight (highest first)
        weighted_outputs.sort(key=lambda x: x["weight"], reverse=True)
        
        synthesis_prompt = f"""
        Create a comprehensive financial recommendation by synthesizing these weighted agent outputs:
        
        Original Query: "{user_query}"
        
        Agent Outputs (ordered by importance weight):
        {json.dumps(weighted_outputs[:5], indent=2, default=str)}  # Top 5 agents
        
        Conflict Resolutions:
        {conflict_resolutions.get("resolution_strategy", "No conflicts")}
        
        Create a response that:
        1. **Executive Summary**: Clear answer to the user's question
        2. **Key Recommendations**: Top 3-5 actionable items with specific amounts/timelines
        3. **Supporting Analysis**: How different agents contributed to this conclusion
        4. **Risk Considerations**: Potential downsides and mitigation strategies
        5. **Next Steps**: Immediate actions the user can take
        
        Make it personal, specific, and actionable. Use ₹ amounts and specific timelines where possible.
        """
        
        content = Content(role="user", parts=[Part(text=synthesis_prompt)])
        response_text = ""
        
        async for event in self.runner.run_async(
            user_id="final_synthesis",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text if event.content.parts else ""
                break
        
        return response_text

    def _calculate_overall_confidence(self, weights: Dict[str, float], 
                                    quality_scores: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall confidence in the consensus"""
        if not weights:
            return 0.0
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for agent_name, weight in weights.items():
            if agent_name in quality_scores:
                agent_confidence = quality_scores[agent_name].get("confidence_level", 0.0)
                weighted_confidence += weight * agent_confidence
                total_weight += weight
        
        return round(weighted_confidence / total_weight if total_weight > 0 else 0.0, 2)


class UltimateConsensusOrchestrator:
    """
    The ultimate financial advisor that orchestrates all agents with intelligent consensus
    """
    
    def __init__(self, mcp_base_url: str = "http://localhost:8080"):
        self.mcp_client = FiMCPClient(mcp_base_url)
        self.consensus_engine = ConsensusEngine(self.mcp_client)
        self.trust_agent = TrustTransparencyAgent()

    async def process_financial_query(self, user_id: str, user_query: str) -> str:
        """
        Main entry point for comprehensive multi-agent financial analysis
        """
        try:
            print(f"🎯 Processing query: {user_query}")
            print(f"👤 User: {user_id}")
            
            # Execute comprehensive multi-agent analysis
            consensus_result = await self.consensus_engine.orchestrate_comprehensive_analysis(
                user_id, user_query
            )
            
            # Add transparency layer
            enriched_response = self._add_transparency_layer(consensus_result)
            
            print(f"✅ Analysis complete with {consensus_result['analysis_metadata']['consensus_confidence']:.0%} confidence")
            
            return enriched_response
            
        except Exception as e:
            print(f"❌ Critical error in consensus orchestration: {e}")
            return f"I apologize, but I encountered an error while analyzing your request. Please try again or contact support. Error: {str(e)}"

    def _add_transparency_layer(self, consensus_result: Dict[str, Any]) -> str:
        """Add transparency information to the final response"""
        
        recommendation = consensus_result["consensus_recommendation"]
        metadata = consensus_result["analysis_metadata"]
        weights = consensus_result["dynamic_weights"]
        
        # Create transparency section
        transparency_info = [
            "\n" + "="*60,
            "🔍 ANALYSIS TRANSPARENCY",
            "="*60,
            f"🤖 Agents Consulted: {metadata['total_agents_consulted']}/9 available",
            f"⏱️ Analysis Time: {metadata['analysis_time_seconds']}s",
            f"🎯 Consensus Confidence: {metadata['consensus_confidence']:.0%}",
            f"⭐ Primary Experts: {', '.join(metadata['primary_agents'])}"
        ]
        
        # Add agent weights
        transparency_info.append("\n📊 AGENT INFLUENCE WEIGHTS:")
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for agent, weight in sorted_weights[:5]:  # Top 5
            transparency_info.append(f"   • {agent.replace('_', ' ').title()}: {weight:.1%}")
        
        # Add conflict information
        if consensus_result["conflicts_detected"]:
            transparency_info.append(f"\n⚖️ Conflicts Resolved: {len(consensus_result['conflicts_detected'])}")
        
        transparency_info.append("="*60)
        
        return recommendation + "\n".join(transparency_info)


# Example usage and testing
async def main():
    """Example usage of the Ultimate Consensus Engine"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python consensus_engine.py <phone_number>")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    
    # Initialize the ultimate orchestrator
    orchestrator = UltimateConsensusOrchestrator()
    
    # Test queries
    test_queries = [
        "Can I afford a ₹50L home loan for a property in Whitefield, Bangalore?",
        "Help me optimize my portfolio - I have ₹8L idle in savings and some underperforming mutual funds",
        "What should be my strategy for the next 6 months considering upcoming wedding expenses?",
        "I want to plan for early retirement by age 45. What changes should I make to my current investments?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"TESTING QUERY: {query}")
        print(f"{'='*80}")
        
        try:
            result = await orchestrator.process_financial_query(phone_number, query)
            print(result)
            print(f"\n{'='*80}")
            
            # Small delay between queries
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Error processing query: {e}")


if __name__ == "__main__":
    asyncio.run(main())