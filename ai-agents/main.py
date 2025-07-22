import asyncio
import logging
import os
from typing import Dict, Any

from src.core.orchestrator import MultiAgentOrchestrator
from src.core.types import UserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectArthaApp:
    """
    Main application for Project Artha Multi-Agent Financial AI System
    """
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        logger.info("Project Artha initialized successfully")
    
    async def run_interactive_session(self):
        """Run interactive CLI session for testing"""
        print("🏦 Welcome to Project Artha - Multi-Agent Financial AI")
        print("=" * 60)
        print("Built with Google ADK and Fi MCP integration")
        print("10 AI agents working in harmony for your financial success")
        print("=" * 60)
        
        while True:
            print("\n--- Authentication Required ---")
            phone_number = input("Enter your phone number (e.g., 2222222222): ").strip()
            
            if phone_number.lower() in ['quit', 'exit']:
                print("Goodbye! 👋")
                break
            
            # Create user context
            context = UserContext(
                user_id=f"user_{phone_number}",
                phone_number=phone_number,
                session_id=f"session_{phone_number}",
                preferences={"language": "english", "detail_level": "moderate"},
                financial_goals=["wealth_building", "retirement_planning"],
                risk_tolerance="moderate"
            )
            
            try:
                print("🔐 Authenticating with all agents...")
                auth_success = await self.orchestrator.authenticate_all_agents(phone_number)
                
                if not auth_success:
                    print("❌ Authentication failed. Please ensure Fi MCP server is running.")
                    continue
                
                print("✅ Authentication successful!")
                print(f"Active agents: {len(self.orchestrator.agents)}")
                
                # Main conversation loop
                while True:
                    print(f"\n--- Multi-Agent Financial AI Session ---")
                    user_query = input("\nAsk about your finances (or 'logout'/'quit'): ").strip()
                    
                    if user_query.lower() == 'logout':
                        break
                    elif user_query.lower() in ['quit', 'exit']:
                        print("Goodbye! 👋")
                        return
                    elif not user_query:
                        continue
                    
                    try:
                        print("🤖 Activating multi-agent analysis...")
                        print("   📊 Data Integration Agent: Fetching financial data")
                        print("   🧠 Core Advisor Agent: Strategic analysis")
                        print("   🎯 Risk Profiling Agent: Behavioral assessment")
                        print("   ⚡ Building consensus...")
                        
                        # Process query through multi-agent system
                        response = await self.orchestrator.process_user_query(user_query, context)
                        
                        if "error" in response:
                            print(f"❌ Error: {response['error']}")
                            continue
                        
                        # Display results
                        print("\n" + "="*80)
                        print("🎯 MULTI-AGENT FINANCIAL ANALYSIS")
                        print("="*80)
                        
                        print(f"\n📋 **Analysis Summary:**")
                        print(f"Confidence Score: {response['confidence_score']:.2f}")
                        print(f"Consensus Reached: {'✅' if response['consensus_reached'] else '❌'}")
                        
                        print(f"\n💡 **Unified Insights:**")
                        print(response['unified_insights'])
                        
                        if response['recommendations']:
                            print(f"\n🎯 **Recommendations:**")
                            for i, rec in enumerate(response['recommendations'], 1):
                                print(f"{i}. {rec}")
                        
                        if response['risk_factors']:
                            print(f"\n⚠️ **Risk Factors:**")
                            for i, risk in enumerate(response['risk_factors'], 1):
                                print(f"{i}. {risk}")
                        
                        print(f"\n🔍 **Agent Breakdown:**")
                        for agent_name, breakdown in response['agent_breakdown'].items():
                            status = "✅" if breakdown['success'] else "❌"
                            confidence = breakdown['confidence']
                            print(f"   {status} {agent_name.replace('_', ' ').title()}: {confidence:.2f} confidence")
                        
                        print("="*80)
                        
                    except Exception as e:
                        print(f"❌ Error processing query: {e}")
                        logger.error(f"Query processing error: {e}")
                        
            except Exception as e:
                print(f"❌ Session error: {e}")
                logger.error(f"Session error: {e}")

    async def run_demo_scenarios(self):
        """Run predefined demo scenarios for testing"""
        demo_scenarios = [
            {
                "phone_number": "2222222222",  # All assets connected profile
                "query": "Should I invest 50,000 bonus in mutual funds or pay off credit card debt?",
                "description": "Investment vs Debt Decision"
            },
            {
                "phone_number": "7777777777",  # Debt-heavy profile
                "query": "Help me optimize my debt repayment strategy",
                "description": "Debt Optimization"
            },
            {
                "phone_number": "1313131313",  # Balanced profile
                "query": "Plan my retirement strategy for the next 20 years", 
                "description": "Retirement Planning"
            }
        ]
        
        print("🎭 Running Demo Scenarios")
        print("=" * 50)
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n--- Demo Scenario {i}: {scenario['description']} ---")
            
            context = UserContext(
                user_id=f"demo_user_{i}",
                phone_number=scenario['phone_number'],
                session_id=f"demo_session_{i}",
                preferences={"language": "english", "detail_level": "detailed"},
                financial_goals=["demo_analysis"],
                risk_tolerance="moderate"
            )
            
            try:
                response = await self.orchestrator.process_user_query(scenario['query'], context)
                
                print(f"Query: {scenario['query']}")
                print(f"Confidence: {response.get('confidence_score', 0):.2f}")
                print(f"Agents Activated: {len(response.get('agent_breakdown', {}))}")
                print(f"Success: {'✅' if not response.get('error') else '❌'}")
                
            except Exception as e:
                print(f"❌ Demo scenario {i} failed: {e}")

async def main():
    """Main entry point"""
    app = ProjectArthaApp()
    
    # Check command line arguments for demo mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await app.run_demo_scenarios()
    else:
        await app.run_interactive_session()

if __name__ == "__main__":
    asyncio.run(main())
