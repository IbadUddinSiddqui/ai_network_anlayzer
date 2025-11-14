"""
Jitter test module for measuring network latency variation.
"""
import logging
import statistics
from typing import Dict, List
from ping3 import ping
import time

logger = logging.getLogger(__name__)


class JitterTest:
    """
    Measures network jitter (latency variation).
    
    Jitter is calculated as the absolute difference between consecutive
    ping latencies, indicating network stability.
    """
    
    def __init__(self, measurement_count: int = 20, timeout: int = 2):
        """
        Initialize jitter test configuration.
        
        Args:
            measurement_count: Number of consecutive pings (default: 20)
            timeout: Timeout in seconds for each ping (default: 2)
        """
        self.measurement_count = measurement_count
        self.timeout = timeout
    
    def run(self, host: str) -> Dict:
        """
        Execute jitter test for a single host.
        
        Args:
            host: Target host IP address or hostname
            
        Returns:
            Dict containing jitter statistics:
                - host: Target host
                - avg_jitter_ms: Average jitter in milliseconds
                - max_jitter_ms: Maximum jitter in milliseconds
                - measurements: List of latency measurements
                - jitter_values: List of calculated jitter values
                
        Example:
            >>> jitter_test = JitterTest(measurement_count=20)
            >>> result = jitter_test.run("8.8.8.8")
            >>> print(f"Average jitter: {result['avg_jitter_ms']}ms")
        """
        logger.info(f"Starting jitter test for host: {host}")
        
        latencies = []
        
        try:
            # Collect consecutive latency measurements
            for i in range(self.measurement_count):
                try:
                    latency = ping(host, timeout=self.timeout, unit='ms')
                    
                    if latency is not None:
                        latencies.append(latency)
                        logger.debug(
                            f"Measurement {i+1}/{self.measurement_count} "
                            f"for {host}: {latency:.2f}ms"
                        )
                    else:
                        logger.warning(
                            f"Measurement {i+1}/{self.measurement_count} "
                            f"for {host}: No response"
                        )
                    
                    # Small delay between measurements
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error during measurement {i+1} to {host}: {e}")
            
            # Calculate jitter from consecutive latencies
            if len(latencies) >= 2:
                jitter_values = []
                
                for i in range(1, len(latencies)):
                    # Jitter is the absolute difference between consecutive latencies
                    jitter = abs(latencies[i] - latencies[i-1])
                    jitter_values.append(jitter)
                
                result = {
                    "host": host,
                    "avg_jitter_ms": round(statistics.mean(jitter_values), 2),
                    "max_jitter_ms": round(max(jitter_values), 2),
                    "min_jitter_ms": round(min(jitter_values), 2),
                    "measurements": [round(l, 2) for l in latencies],
                    "jitter_values": [round(j, 2) for j in jitter_values],
                    "successful_measurements": len(latencies),
                    "total_measurements": self.measurement_count
                }
                
                logger.info(
                    f"Jitter test completed for {host}: "
                    f"avg jitter: {result['avg_jitter_ms']}ms, "
                    f"max jitter: {result['max_jitter_ms']}ms"
                )
            else:
                # Not enough measurements
                logger.warning(
                    f"Insufficient measurements for {host}: "
                    f"only {len(latencies)} successful"
                )
                result = {
                    "host": host,
                    "avg_jitter_ms": 0.0,
                    "max_jitter_ms": 0.0,
                    "min_jitter_ms": 0.0,
                    "measurements": latencies,
                    "jitter_values": [],
                    "successful_measurements": len(latencies),
                    "total_measurements": self.measurement_count,
                    "error": "Insufficient measurements"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Jitter test failed for {host}: {e}")
            return {
                "host": host,
                "avg_jitter_ms": 0.0,
                "max_jitter_ms": 0.0,
                "min_jitter_ms": 0.0,
                "measurements": [],
                "jitter_values": [],
                "successful_measurements": 0,
                "total_measurements": self.measurement_count,
                "error": str(e)
            }
    
    def run_multiple(self, hosts: List[str]) -> List[Dict]:
        """
        Execute jitter test for multiple hosts.
        
        Args:
            hosts: List of target host IP addresses or hostnames
            
        Returns:
            List of jitter result dictionaries
            
        Example:
            >>> jitter_test = JitterTest()
            >>> results = jitter_test.run_multiple(["8.8.8.8", "1.1.1.1"])
            >>> for result in results:
            ...     print(f"{result['host']}: {result['avg_jitter_ms']}ms jitter")
        """
        logger.info(f"Starting jitter test for {len(hosts)} hosts")
        results = []
        
        for host in hosts:
            result = self.run(host)
            results.append(result)
        
        logger.info(f"Completed jitter test for {len(hosts)} hosts")
        return results
    
    @staticmethod
    def calculate_jitter_from_latencies(latencies: List[float]) -> Dict:
        """
        Calculate jitter statistics from a list of latencies.
        
        Args:
            latencies: List of latency measurements in milliseconds
            
        Returns:
            Dict with jitter statistics
            
        Example:
            >>> latencies = [10.5, 12.3, 11.8, 13.2, 10.9]
            >>> stats = JitterTest.calculate_jitter_from_latencies(latencies)
            >>> print(f"Average jitter: {stats['avg_jitter_ms']}ms")
        """
        if len(latencies) < 2:
            return {
                "avg_jitter_ms": 0.0,
                "max_jitter_ms": 0.0,
                "min_jitter_ms": 0.0,
                "jitter_values": []
            }
        
        jitter_values = []
        for i in range(1, len(latencies)):
            jitter = abs(latencies[i] - latencies[i-1])
            jitter_values.append(jitter)
        
        return {
            "avg_jitter_ms": round(statistics.mean(jitter_values), 2),
            "max_jitter_ms": round(max(jitter_values), 2),
            "min_jitter_ms": round(min(jitter_values), 2),
            "jitter_values": [round(j, 2) for j in jitter_values]
        }


def measure_jitter(host: str, measurement_count: int = 20, timeout: int = 2) -> Dict:
    """
    Convenience function to measure jitter for a single host.
    
    Args:
        host: Target host IP address or hostname
        measurement_count: Number of consecutive pings
        timeout: Timeout in seconds for each ping
        
    Returns:
        Dict containing jitter statistics
    """
    jitter_test = JitterTest(measurement_count=measurement_count, timeout=timeout)
    return jitter_test.run(host)
