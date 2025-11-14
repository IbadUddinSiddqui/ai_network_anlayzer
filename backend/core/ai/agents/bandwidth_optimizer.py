"""
Bandwidth Optimizer Agent - Analyzes speed test results.
"""
import logging
import json
from typing import Dict
import google.generativeai as genai
from ..prompts import (
    BANDWIDTH_OPTIMIZER_SYSTEM_PROMPT,
    BANDWIDTH_OPTIMIZER_USER_PROMPT,
    format_speed_results
)

logger = logging.getLogger(__name__)


class BandwidthOptimizer:
    """
    Specialized AI agent for analyzing bandwidth and speed metrics.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.agent_name = "BandwidthOptimizer"
    
    def analyze(self, speed_results: Dict) -> Dict:
        """Analyze speed test results and generate recommendations."""
        logger.info(f"{self.agent_name}: Starting bandwidth analysis")
        
        try:
            formatted_results = format_speed_results(speed_results)
            user_prompt = BANDWIDTH_OPTIMIZER_USER_PROMPT.format(
                speed_results=formatted_results
            )
            
            prompt = f"{BANDWIDTH_OPTIMIZER_SYSTEM_PROMPT}\n\n{user_prompt}\n\nRespond with valid JSON only."
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
            return self._generate_fallback_analysis(speed_results)
    
    def _generate_fallback_analysis(self, speed_results: Dict) -> Dict:
        """Generate rule-based analysis when AI fails."""
        logger.info(f"{self.agent_name}: Generating fallback analysis")
        
        download = speed_results.get('download_mbps', 0)
        upload = speed_results.get('upload_mbps', 0)
        findings = []
        recommendations = []
        
        # Analyze download speed
        if download >= 100:
            findings.append(f"Excellent download speed: {download} Mbps")
        elif download >= 50:
            findings.append(f"Good download speed: {download} Mbps")
            recommendations.append({
                "text": "Download speed is good for most activities. Consider upgrading for 4K streaming or large file transfers.",
                "confidence": 0.70,
                "severity": "info",
                "agent_type": self.agent_name
            })
        elif download >= 25:
            findings.append(f"Fair download speed: {download} Mbps")
            recommendations.append({
                "text": "Download speed is adequate for HD streaming. Upgrade recommended for multiple users or 4K content.",
                "confidence": 0.75,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        else:
            findings.append(f"Low download speed: {download} Mbps")
            recommendations.append({
                "text": "Download speed is below recommended levels. Contact ISP about plan upgrade or check for service issues.",
                "confidence": 0.90,
                "severity": "critical",
                "agent_type": self.agent_name
            })
        
        # Analyze upload speed
        if upload < 10:
            findings.append(f"Low upload speed: {upload} Mbps")
            recommendations.append({
                "text": "Upload speed may limit video conferencing and file uploads. Consider plan upgrade if these are important.",
                "confidence": 0.80,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        
        return {"findings": findings, "recommendations": recommendations}
