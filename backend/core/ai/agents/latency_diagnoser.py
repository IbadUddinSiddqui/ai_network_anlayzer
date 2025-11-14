"""
Latency Diagnoser Agent - Analyzes ping latency patterns.
"""
import logging
import json
from typing import Dict, List
import google.generativeai as genai
from ..prompts import (
    LATENCY_DIAGNOSER_SYSTEM_PROMPT,
    LATENCY_DIAGNOSER_USER_PROMPT,
    format_ping_results
)

logger = logging.getLogger(__name__)


class LatencyDiagnoser:
    """
    Specialized AI agent for analyzing network latency patterns.
    
    Identifies high latency issues, analyzes consistency, and provides
    actionable recommendations for latency optimization.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize the Latency Diagnoser agent.
        
        Args:
            gemini_api_key: Google Gemini API key
            model: Gemini model to use (default: gemini-1.5-flash)
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.agent_name = "LatencyDiagnoser"
    
    def analyze(self, ping_results: List[Dict]) -> Dict:
        """
        Analyze ping latency results and generate recommendations.
        
        Args:
            ping_results: List of ping test results
            
        Returns:
            Dict containing findings and recommendations with confidence scores
            
        Example:
            >>> diagnoser = LatencyDiagnoser(api_key)
            >>> results = diagnoser.analyze(ping_results)
            >>> for rec in results['recommendations']:
            ...     print(f"{rec['text']} (confidence: {rec['confidence']})")
        """
        logger.info(f"{self.agent_name}: Starting latency analysis")
        
        try:
            # Format ping results for the prompt
            formatted_results = format_ping_results(ping_results)
            
            # Prepare the user prompt
            user_prompt = LATENCY_DIAGNOSER_USER_PROMPT.format(
                ping_results=formatted_results
            )
            
            # Call Gemini API
            prompt = f"{LATENCY_DIAGNOSER_SYSTEM_PROMPT}\n\n{user_prompt}\n\nRespond with valid JSON only."
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 1000,
                }
            )
            
            # Parse response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            analysis = json.loads(response_text.strip())
            
            # Add agent metadata to recommendations
            if 'recommendations' in analysis:
                for rec in analysis['recommendations']:
                    rec['agent_type'] = self.agent_name
            
            logger.info(
                f"{self.agent_name}: Analysis complete. "
                f"Generated {len(analysis.get('recommendations', []))} recommendations"
            )
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.agent_name}: Failed to parse AI response: {e}")
            return self._generate_fallback_analysis(ping_results)
        except Exception as e:
            logger.error(f"{self.agent_name}: Analysis failed: {e}")
            return self._generate_fallback_analysis(ping_results)
    
    def _generate_fallback_analysis(self, ping_results: List[Dict]) -> Dict:
        """
        Generate rule-based analysis when AI fails.
        
        Args:
            ping_results: List of ping test results
            
        Returns:
            Dict with fallback recommendations
        """
        logger.info(f"{self.agent_name}: Generating fallback analysis")
        
        findings = []
        recommendations = []
        
        # Calculate average latency across all hosts
        avg_latencies = [r.get('avg_ms', 0) for r in ping_results if r.get('avg_ms', 0) > 0]
        
        if not avg_latencies:
            return {
                "findings": ["No valid ping results available"],
                "recommendations": [{
                    "text": "Unable to measure latency. Check network connectivity.",
                    "confidence": 0.90,
                    "severity": "critical",
                    "agent_type": self.agent_name
                }]
            }
        
        overall_avg = sum(avg_latencies) / len(avg_latencies)
        
        # Analyze latency levels
        if overall_avg > 200:
            findings.append(f"Very high latency detected: {overall_avg:.1f}ms average")
            recommendations.append({
                "text": "Critical latency issue detected. Check for network congestion, ISP problems, or routing issues. Consider contacting your ISP.",
                "confidence": 0.95,
                "severity": "critical",
                "agent_type": self.agent_name
            })
        elif overall_avg > 100:
            findings.append(f"High latency detected: {overall_avg:.1f}ms average")
            recommendations.append({
                "text": "High latency may impact real-time applications. Check WiFi signal strength, router placement, and consider using wired connection.",
                "confidence": 0.85,
                "severity": "warning",
                "agent_type": self.agent_name
            })
        elif overall_avg > 50:
            findings.append(f"Moderate latency: {overall_avg:.1f}ms average")
            recommendations.append({
                "text": "Latency is acceptable but could be improved. Optimize router settings and reduce network congestion.",
                "confidence": 0.70,
                "severity": "info",
                "agent_type": self.agent_name
            })
        else:
            findings.append(f"Good latency: {overall_avg:.1f}ms average")
            recommendations.append({
                "text": "Latency is within excellent range. No action needed.",
                "confidence": 0.90,
                "severity": "info",
                "agent_type": self.agent_name
            })
        
        # Check for consistency (standard deviation)
        for result in ping_results:
            stddev = result.get('stddev_ms', 0)
            if stddev > 20:
                findings.append(f"Inconsistent latency to {result.get('host')}: {stddev:.1f}ms std dev")
                recommendations.append({
                    "text": f"Latency to {result.get('host')} is unstable. This may indicate network congestion or routing issues.",
                    "confidence": 0.75,
                    "severity": "warning",
                    "agent_type": self.agent_name
                })
        
        return {
            "findings": findings,
            "recommendations": recommendations
        }
