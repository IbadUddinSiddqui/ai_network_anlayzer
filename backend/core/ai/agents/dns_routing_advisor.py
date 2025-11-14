"""
DNS & Routing Advisor Agent - Analyzes DNS performance.
"""
import logging
import json
from typing import Dict, List
import google.generativeai as genai
from ..prompts import (
    DNS_ROUTING_ADVISOR_SYSTEM_PROMPT,
    DNS_ROUTING_ADVISOR_USER_PROMPT,
    format_dns_results
)

logger = logging.getLogger(__name__)


class DNSRoutingAdvisor:
    """
    Specialized AI agent for analyzing DNS resolution performance.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.agent_name = "DNSRoutingAdvisor"
    
    def analyze(self, dns_results: List[Dict]) -> Dict:
        """Analyze DNS test results and generate recommendations."""
        logger.info(f"{self.agent_name}: Starting DNS analysis")
        
        try:
            formatted_results = format_dns_results(dns_results)
            user_prompt = DNS_ROUTING_ADVISOR_USER_PROMPT.format(
                dns_results=formatted_results
            )
            
            prompt = f"{DNS_ROUTING_ADVISOR_SYSTEM_PROMPT}\n\n{user_prompt}\n\nRespond with valid JSON only."
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.3, 'max_output_tokens': 1000}
            )
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            analysis = json.loads(response_text.strip())
            
            if 'recommendations' in analysis:
                for rec in analysis['recommendations']:
                    rec['agent_type'] = self.agent_name
            
            logger.info(f"{self.agent_name}: Analysis complete")
            return analysis
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Analysis failed: {e}")
            return self._generate_fallback_analysis(dns_results)
    
    def _generate_fallback_analysis(self, dns_results: List[Dict]) -> Dict:
        """Generate rule-based analysis when AI fails."""
        logger.info(f"{self.agent_name}: Generating fallback analysis")
        
        findings = []
        recommendations = []
        
        # Find fastest DNS server
        valid_results = [r for r in dns_results if r.get('avg_resolution_ms', 0) > 0]
        
        if not valid_results:
            return {
                "findings": ["No valid DNS results"],
                "recommendations": [{
                    "text": "Unable to test DNS servers. Check network connectivity.",
                    "confidence": 0.80,
                    "severity": "warning",
                    "agent_type": self.agent_name
                }]
            }
        
        fastest = min(valid_results, key=lambda x: x['avg_resolution_ms'])
        slowest = max(valid_results, key=lambda x: x['avg_resolution_ms'])
        
        findings.append(f"Fastest DNS: {fastest['dns_server']} ({fastest['avg_resolution_ms']}ms)")
        findings.append(f"Slowest DNS: {slowest['dns_server']} ({slowest['avg_resolution_ms']}ms)")
        
        if fastest['avg_resolution_ms'] < 20:
            recommendations.append({
                "text": f"DNS performance is excellent with {fastest['dns_server']}. Current configuration is optimal.",
                "confidence": 0.90,
                "severity": "info",
                "agent_type": self.agent_name
            })
        else:
            recommendations.append({
                "text": f"Consider switching to {fastest['dns_server']} for {slowest['avg_resolution_ms'] - fastest['avg_resolution_ms']:.1f}ms faster DNS resolution.",
                "confidence": 0.85,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        
        return {"findings": findings, "recommendations": recommendations}
