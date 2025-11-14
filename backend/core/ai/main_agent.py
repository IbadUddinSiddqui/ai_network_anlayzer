"""
Main Orchestrator Agent - Coordinates all sub-agents and synthesizes insights.
"""
import logging
import json
import asyncio
from typing import Dict, List
import google.generativeai as genai

from .agents.latency_diagnoser import LatencyDiagnoser
from .agents.packet_loss_advisor import PacketLossAdvisor
from .agents.bandwidth_optimizer import BandwidthOptimizer
from .agents.dns_routing_advisor import DNSRoutingAdvisor
from .prompts import (
    MAIN_ORCHESTRATOR_SYSTEM_PROMPT,
    MAIN_ORCHESTRATOR_USER_PROMPT,
    format_test_summary,
    FALLBACK_RECOMMENDATIONS
)

logger = logging.getLogger(__name__)


class MainAgent:
    """
    Main orchestrator agent that coordinates all specialized sub-agents.
    
    Delegates analysis to sub-agents, merges their insights, and generates
    a unified, prioritized set of recommendations.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize the main orchestrator agent.
        
        Args:
            gemini_api_key: Google Gemini API key
            model: Gemini model to use (default: gemini-pro)
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.agent_name = "MainOrchestrator"
        
        # Initialize sub-agents
        self.latency_diagnoser = LatencyDiagnoser(gemini_api_key, model)
        self.packet_loss_advisor = PacketLossAdvisor(gemini_api_key, model)
        self.bandwidth_optimizer = BandwidthOptimizer(gemini_api_key, model)
        self.dns_routing_advisor = DNSRoutingAdvisor(gemini_api_key, model)
    
    async def analyze(self, test_results: Dict) -> Dict:
        """
        Analyze network test results using all sub-agents.
        
        Args:
            test_results: Complete network test results
            
        Returns:
            Dict containing unified analysis and prioritized recommendations
            
        Example:
            >>> main_agent = MainAgent(api_key)
            >>> analysis = await main_agent.analyze(test_results)
            >>> print(analysis['summary'])
        """
        logger.info(f"{self.agent_name}: Starting comprehensive network analysis")
        
        try:
            # Run all sub-agents in parallel
            logger.info(f"{self.agent_name}: Delegating to sub-agents")
            
            latency_task = asyncio.to_thread(
                self.latency_diagnoser.analyze,
                test_results.get('ping_results', [])
            )
            packet_loss_task = asyncio.to_thread(
                self.packet_loss_advisor.analyze,
                test_results.get('packet_loss_results', {})
            )
            bandwidth_task = asyncio.to_thread(
                self.bandwidth_optimizer.analyze,
                test_results.get('speed_results', {})
            )
            dns_task = asyncio.to_thread(
                self.dns_routing_advisor.analyze,
                test_results.get('dns_results', [])
            )
            
            # Wait for all analyses to complete
            latency_analysis, packet_loss_analysis, bandwidth_analysis, dns_analysis = \
                await asyncio.gather(
                    latency_task,
                    packet_loss_task,
                    bandwidth_task,
                    dns_task,
                    return_exceptions=True
                )
            
            # Handle exceptions
            if isinstance(latency_analysis, Exception):
                logger.error(f"Latency analysis failed: {latency_analysis}")
                latency_analysis = {"findings": [], "recommendations": []}
            
            if isinstance(packet_loss_analysis, Exception):
                logger.error(f"Packet loss analysis failed: {packet_loss_analysis}")
                packet_loss_analysis = {"findings": [], "recommendations": []}
            
            if isinstance(bandwidth_analysis, Exception):
                logger.error(f"Bandwidth analysis failed: {bandwidth_analysis}")
                bandwidth_analysis = {"findings": [], "recommendations": []}
            
            if isinstance(dns_analysis, Exception):
                logger.error(f"DNS analysis failed: {dns_analysis}")
                dns_analysis = {"findings": [], "recommendations": []}
            
            logger.info(f"{self.agent_name}: Sub-agent analyses complete, synthesizing results")
            
            # Synthesize all analyses
            unified_analysis = await self._synthesize_analyses(
                test_results,
                latency_analysis,
                packet_loss_analysis,
                bandwidth_analysis,
                dns_analysis
            )
            
            logger.info(
                f"{self.agent_name}: Analysis complete. "
                f"Generated {len(unified_analysis.get('recommendations', []))} recommendations"
            )
            
            return unified_analysis
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Comprehensive analysis failed: {e}")
            return self._generate_fallback_analysis()
    
    async def _synthesize_analyses(
        self,
        test_results: Dict,
        latency_analysis: Dict,
        packet_loss_analysis: Dict,
        bandwidth_analysis: Dict,
        dns_analysis: Dict
    ) -> Dict:
        """
        Synthesize all sub-agent analyses into unified recommendations.
        
        Args:
            test_results: Original test results
            latency_analysis: Latency diagnoser results
            packet_loss_analysis: Packet loss advisor results
            bandwidth_analysis: Bandwidth optimizer results
            dns_analysis: DNS routing advisor results
            
        Returns:
            Dict with synthesized analysis and prioritized recommendations
        """
        try:
            # Prepare synthesis prompt
            user_prompt = MAIN_ORCHESTRATOR_USER_PROMPT.format(
                latency_analysis=json.dumps(latency_analysis, indent=2),
                packet_loss_analysis=json.dumps(packet_loss_analysis, indent=2),
                bandwidth_analysis=json.dumps(bandwidth_analysis, indent=2),
                dns_analysis=json.dumps(dns_analysis, indent=2),
                test_summary=format_test_summary(test_results)
            )
            
            # Call Gemini API for synthesis
            prompt = f"{MAIN_ORCHESTRATOR_SYSTEM_PROMPT}\n\n{user_prompt}\n\nRespond with valid JSON only."
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={'temperature': 0.3, 'max_output_tokens': 1500}
            )
            
            # Parse synthesized analysis
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            synthesis = json.loads(response_text.strip())
            
            # Ensure all recommendations have required fields
            if 'recommendations' in synthesis:
                for i, rec in enumerate(synthesis['recommendations']):
                    if 'priority' not in rec:
                        rec['priority'] = i + 1
                    if 'agent_source' not in rec:
                        rec['agent_source'] = self.agent_name
            
            return synthesis
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Synthesis failed, using simple merge: {e}")
            return self._simple_merge_analyses(
                latency_analysis,
                packet_loss_analysis,
                bandwidth_analysis,
                dns_analysis
            )
    
    def _simple_merge_analyses(
        self,
        latency_analysis: Dict,
        packet_loss_analysis: Dict,
        bandwidth_analysis: Dict,
        dns_analysis: Dict
    ) -> Dict:
        """
        Simple merge of all analyses when AI synthesis fails.
        
        Args:
            latency_analysis: Latency diagnoser results
            packet_loss_analysis: Packet loss advisor results
            bandwidth_analysis: Bandwidth optimizer results
            dns_analysis: DNS routing advisor results
            
        Returns:
            Dict with merged recommendations
        """
        logger.info(f"{self.agent_name}: Performing simple merge of analyses")
        
        all_recommendations = []
        
        # Collect all recommendations
        for analysis in [latency_analysis, packet_loss_analysis, bandwidth_analysis, dns_analysis]:
            if 'recommendations' in analysis:
                all_recommendations.extend(analysis['recommendations'])
        
        # Sort by severity and confidence
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        all_recommendations.sort(
            key=lambda x: (
                severity_order.get(x.get('severity', 'info'), 2),
                -x.get('confidence', 0)
            )
        )
        
        # Add priority
        for i, rec in enumerate(all_recommendations):
            rec['priority'] = i + 1
        
        # Identify critical issues
        critical_issues = [
            rec['text'] for rec in all_recommendations
            if rec.get('severity') == 'critical'
        ]
        
        return {
            "summary": self._generate_summary(all_recommendations),
            "critical_issues": critical_issues[:3],  # Top 3 critical issues
            "recommendations": all_recommendations[:10]  # Top 10 recommendations
        }
    
    def _generate_summary(self, recommendations: List[Dict]) -> str:
        """
        Generate a brief summary based on recommendations.
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            String summary of network health
        """
        if not recommendations:
            return "Network analysis complete. No significant issues detected."
        
        critical_count = sum(1 for r in recommendations if r.get('severity') == 'critical')
        warning_count = sum(1 for r in recommendations if r.get('severity') == 'warning')
        
        if critical_count > 0:
            return f"Network has {critical_count} critical issue(s) requiring immediate attention."
        elif warning_count > 0:
            return f"Network is functional but has {warning_count} area(s) for improvement."
        else:
            return "Network performance is good. Minor optimizations available."
    
    def _generate_fallback_analysis(self) -> Dict:
        """
        Generate fallback analysis when all else fails.
        
        Returns:
            Dict with generic fallback recommendations
        """
        logger.warning(f"{self.agent_name}: Using fallback recommendations")
        
        return {
            "summary": "Unable to perform detailed analysis. Using generic recommendations.",
            "critical_issues": [],
            "recommendations": FALLBACK_RECOMMENDATIONS
        }
