"""
Packet Loss Advisor Agent - Analyzes packet loss patterns.
"""
import logging
import json
from typing import Dict
import google.generativeai as genai
from ..prompts import (
    PACKET_LOSS_ADVISOR_SYSTEM_PROMPT,
    PACKET_LOSS_ADVISOR_USER_PROMPT,
    format_packet_loss_results
)

logger = logging.getLogger(__name__)


class PacketLossAdvisor:
    """
    Specialized AI agent for analyzing packet loss and network stability.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.agent_name = "PacketLossAdvisor"
    
    def analyze(self, packet_loss_results: Dict) -> Dict:
        """Analyze packet loss results and generate recommendations."""
        logger.info(f"{self.agent_name}: Starting packet loss analysis")
        
        try:
            formatted_results = format_packet_loss_results(packet_loss_results)
            user_prompt = PACKET_LOSS_ADVISOR_USER_PROMPT.format(
                packet_loss_results=formatted_results
            )
            
            prompt = f"{PACKET_LOSS_ADVISOR_SYSTEM_PROMPT}\n\n{user_prompt}\n\nRespond with valid JSON only."
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
            return self._generate_fallback_analysis(packet_loss_results)
    
    def _generate_fallback_analysis(self, packet_loss_results: Dict) -> Dict:
        """Generate rule-based analysis when AI fails."""
        logger.info(f"{self.agent_name}: Generating fallback analysis")
        
        loss_pct = packet_loss_results.get('loss_percentage', 0)
        findings = []
        recommendations = []
        
        if loss_pct == 0:
            findings.append("No packet loss detected")
            recommendations.append({
                "text": "Network stability is excellent. No packet loss detected.",
                "confidence": 0.95,
                "severity": "info",
                "agent_type": self.agent_name
            })
        elif loss_pct < 1:
            findings.append(f"Minimal packet loss: {loss_pct}%")
            recommendations.append({
                "text": "Very low packet loss detected. Network is stable.",
                "confidence": 0.85,
                "severity": "info",
                "agent_type": self.agent_name
            })
        elif loss_pct < 3:
            findings.append(f"Low packet loss: {loss_pct}%")
            recommendations.append({
                "text": "Minor packet loss detected. Monitor for patterns and check WiFi signal if using wireless.",
                "confidence": 0.75,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        elif loss_pct < 5:
            findings.append(f"Moderate packet loss: {loss_pct}%")
            recommendations.append({
                "text": "Moderate packet loss may affect VoIP and gaming. Check router, cables, and consider wired connection.",
                "confidence": 0.85,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        else:
            findings.append(f"High packet loss: {loss_pct}%")
            recommendations.append({
                "text": "Critical packet loss detected. Check hardware connections, router health, and contact ISP if issue persists.",
                "confidence": 0.95,
                "severity": "critical",
                "agent_type": self.agent_name
            })
        
        return {"findings": findings, "recommendations": recommendations}
