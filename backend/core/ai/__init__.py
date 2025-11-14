"""
AI analysis module with multi-agent system for network diagnostics.
"""
import logging
import asyncio
import os
from typing import Dict, List
from datetime import datetime

from .main_agent import MainAgent
from .prompts import FALLBACK_RECOMMENDATIONS

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    Main interface for AI-powered network analysis.
    
    Provides a clean API for invoking the multi-agent analysis system
    with rate limiting, retry logic, and error handling.
    """
    
    def __init__(
        self,
        gemini_api_key: str = None,
        model: str = "gemini-1.5-flash",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the AI analyzer.
        
        Args:
            gemini_api_key: Google Gemini API key (defaults to env variable)
            model: Gemini model to use
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key must be provided or set in GEMINI_API_KEY environment variable")
        
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize main agent
        self.main_agent = MainAgent(self.api_key, self.model)
        
        logger.info("AIAnalyzer initialized successfully")
    
    async def analyze(self, test_results: Dict) -> Dict:
        """
        Analyze network test results using AI agents with enhanced error handling.
        
        Args:
            test_results: Complete network test results from NetworkTestRunner
            
        Returns:
            Dict containing AI analysis with recommendations
            
        Raises:
            AIAnalysisException: If analysis fails after all retries
            
        Example:
            >>> analyzer = AIAnalyzer()
            >>> analysis = await analyzer.analyze(test_results)
            >>> for rec in analysis['recommendations']:
            ...     print(f"{rec['text']} (confidence: {rec['confidence']})")
        """
        logger.info("Starting AI analysis of network test results")
        
        # Validate test results
        if not test_results:
            logger.error("AI analysis failed: test results are empty")
            raise AIAnalysisException("Test results cannot be empty")
        
        # Check if API key is available
        if not self.api_key:
            logger.error("AI analysis failed: Gemini API key not configured")
            return self._generate_fallback_analysis(test_results)
        
        # Attempt analysis with retries
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"AI analysis attempt {attempt}/{self.max_retries}")
                
                # Run analysis
                analysis = await self.main_agent.analyze(test_results)
                
                # Validate analysis response
                if not analysis:
                    raise AIAnalysisException("Analysis returned None")
                
                if 'recommendations' not in analysis:
                    logger.warning("Analysis missing 'recommendations' key, adding empty list")
                    analysis['recommendations'] = []
                
                # Validate recommendations structure
                if not isinstance(analysis['recommendations'], list):
                    logger.warning("Recommendations is not a list, converting")
                    analysis['recommendations'] = []
                
                # Add metadata
                analysis['analyzed_at'] = datetime.utcnow().isoformat()
                analysis['model_used'] = self.model
                analysis['attempt'] = attempt
                
                logger.info(
                    f"AI analysis completed successfully on attempt {attempt}. "
                    f"Generated {len(analysis['recommendations'])} recommendations"
                )
                return analysis
                
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                logger.error(
                    f"AI analysis attempt {attempt}/{self.max_retries} failed: "
                    f"{error_type}: {str(e)}",
                    exc_info=True
                )
                
                # Check for rate limit errors
                if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                    logger.warning("Rate limit detected, using fallback immediately")
                    return self._generate_fallback_analysis(test_results)
                
                if attempt < self.max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    # All retries exhausted, use fallback
                    logger.error("All AI analysis attempts failed, using fallback recommendations")
                    return self._generate_fallback_analysis(test_results)
    
    def analyze_sync(self, test_results: Dict) -> Dict:
        """
        Synchronous wrapper for analyze method.
        
        Args:
            test_results: Complete network test results
            
        Returns:
            Dict containing AI analysis with recommendations
        """
        return asyncio.run(self.analyze(test_results))
    
    def _generate_fallback_analysis(self, test_results: Dict) -> Dict:
        """
        Generate enhanced fallback analysis when AI fails.
        
        Creates basic rule-based recommendations based on test results.
        
        Args:
            test_results: Network test results
            
        Returns:
            Dict with fallback recommendations
        """
        logger.warning("Generating enhanced fallback analysis based on test results")
        
        recommendations = []
        
        # Check speed results
        speed_results = test_results.get('speed_results', {})
        if speed_results and not speed_results.get('error'):
            download = speed_results.get('download_mbps', 0)
            upload = speed_results.get('upload_mbps', 0)
            
            if download < 10:
                recommendations.append({
                    "text": f"Your download speed ({download:.1f} Mbps) is below recommended levels. Consider upgrading your internet plan or checking for network issues.",
                    "agent_type": "fallback_analyzer",
                    "confidence": 0.8,
                    "severity": "warning"
                })
            
            if upload < 5:
                recommendations.append({
                    "text": f"Your upload speed ({upload:.1f} Mbps) is low. This may affect video calls and file uploads.",
                    "agent_type": "fallback_analyzer",
                    "confidence": 0.8,
                    "severity": "info"
                })
        
        # Check packet loss
        packet_loss = test_results.get('packet_loss_results', {})
        if packet_loss and not packet_loss.get('error'):
            loss_pct = packet_loss.get('loss_percentage', 0)
            if loss_pct > 5:
                recommendations.append({
                    "text": f"High packet loss detected ({loss_pct}%). This indicates network instability. Check your connection and router.",
                    "agent_type": "fallback_analyzer",
                    "confidence": 0.9,
                    "severity": "critical"
                })
            elif loss_pct > 1:
                recommendations.append({
                    "text": f"Moderate packet loss detected ({loss_pct}%). Monitor your connection for stability issues.",
                    "agent_type": "fallback_analyzer",
                    "confidence": 0.8,
                    "severity": "warning"
                })
        
        # Check ping latency
        ping_results = test_results.get('ping_results', [])
        if ping_results:
            avg_latencies = [p.get('avg_ms', 0) for p in ping_results if not p.get('error')]
            if avg_latencies:
                avg_latency = sum(avg_latencies) / len(avg_latencies)
                if avg_latency > 100:
                    recommendations.append({
                        "text": f"High latency detected ({avg_latency:.1f}ms average). This may affect real-time applications like gaming and video calls.",
                        "agent_type": "fallback_analyzer",
                        "confidence": 0.8,
                        "severity": "warning"
                    })
        
        # If no specific issues found, add generic recommendation
        if not recommendations:
            recommendations.extend(FALLBACK_RECOMMENDATIONS)
        
        logger.info(f"Generated {len(recommendations)} fallback recommendations")
        
        return {
            "summary": "AI analysis unavailable. Using rule-based recommendations based on your test results.",
            "critical_issues": [r['text'] for r in recommendations if r.get('severity') == 'critical'],
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow().isoformat(),
            "model_used": "fallback",
            "fallback": True
        }
    
    async def batch_analyze(self, test_results_list: List[Dict]) -> List[Dict]:
        """
        Analyze multiple test results in batch.
        
        Args:
            test_results_list: List of network test results
            
        Returns:
            List of AI analyses
        """
        logger.info(f"Starting batch analysis of {len(test_results_list)} test results")
        
        tasks = [self.analyze(test_results) for test_results in test_results_list]
        analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_analyses = []
        for i, analysis in enumerate(analyses):
            if isinstance(analysis, Exception):
                logger.error(f"Batch analysis {i} failed: {analysis}")
                processed_analyses.append(self._generate_fallback_analysis(test_results_list[i]))
            else:
                processed_analyses.append(analysis)
        
        logger.info(f"Batch analysis complete: {len(processed_analyses)} results")
        return processed_analyses


class AIAnalysisException(Exception):
    """Exception raised when AI analysis fails."""
    pass


# Convenience function
async def analyze_network_test(test_results: Dict, gemini_api_key: str = None) -> Dict:
    """
    Convenience function to analyze network test results.
    
    Args:
        test_results: Network test results
        gemini_api_key: Google Gemini API key (optional)
        
    Returns:
        Dict containing AI analysis
    """
    analyzer = AIAnalyzer(gemini_api_key=gemini_api_key)
    return await analyzer.analyze(test_results)
