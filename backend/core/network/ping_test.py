"""
Ping test module for measuring network latency.
"""
import logging
import statistics
from typing import Dict, List
from ping3 import ping
import time

logger = logging.getLogger(__name__)


class PingTest:
    """
    Measures network latency using ICMP ping.
    
    Sends multiple ping packets to target hosts and calculates
    min, max, average, and standard deviation of latency.
    """
    
    def __init__(self, packet_count: int = 10, timeout: int = 2):
        """
        Initialize ping test configuration.
        
        Args:
            packet_count: Number of ping packets to send (default: 10)
            timeout: Timeout in seconds for each ping (default: 2)
        """
        self.packet_count = packet_count
        self.timeout = timeout
    
    def run(self, host: str) -> Dict:
        """
        Execute ping test for a single host.
        
        Args:
            host: Target host IP address or hostname
            
        Returns:
            Dict containing ping statistics:
                - host: Target host
                - packets_sent: Number of packets sent
                - packets_received: Number of packets received
                - min_ms: Minimum latency in milliseconds
                - max_ms: Maximum latency in milliseconds
                - avg_ms: Average latency in milliseconds
                - stddev_ms: Standard deviation of latency
                
        Example:
            >>> ping_test = PingTest(packet_count=10)
            >>> result = ping_test.run("8.8.8.8")
            >>> print(f"Average latency: {result['avg_ms']}ms")
        """
        logger.info(f"Starting ping test for host: {host}")
        
        latencies = []
        packets_sent = 0
        packets_received = 0
        
        try:
            for i in range(self.packet_count):
                packets_sent += 1
                
                try:
                    # Perform ping and get latency in seconds
                    latency = ping(host, timeout=self.timeout, unit='ms')
                    
                    if latency is not None:
                        packets_received += 1
                        latencies.append(latency)
                        logger.debug(f"Ping {i+1}/{self.packet_count} to {host}: {latency:.2f}ms")
                    else:
                        logger.warning(f"Ping {i+1}/{self.packet_count} to {host}: No response")
                    
                    # Small delay between pings
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error during ping {i+1} to {host}: {e}")
            
            # Calculate statistics
            if latencies:
                result = {
                    "host": host,
                    "packets_sent": packets_sent,
                    "packets_received": packets_received,
                    "min_ms": round(min(latencies), 2),
                    "max_ms": round(max(latencies), 2),
                    "avg_ms": round(statistics.mean(latencies), 2),
                    "stddev_ms": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0.0
                }
            else:
                # All pings failed
                result = {
                    "host": host,
                    "packets_sent": packets_sent,
                    "packets_received": 0,
                    "min_ms": 0.0,
                    "max_ms": 0.0,
                    "avg_ms": 0.0,
                    "stddev_ms": 0.0
                }
            
            logger.info(
                f"Ping test completed for {host}: "
                f"{packets_received}/{packets_sent} packets received, "
                f"avg latency: {result['avg_ms']}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ping test failed for {host}: {e}")
            # Return error result
            return {
                "host": host,
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "avg_ms": 0.0,
                "stddev_ms": 0.0,
                "error": str(e)
            }
    
    def run_multiple(self, hosts: List[str]) -> List[Dict]:
        """
        Execute ping test for multiple hosts.
        
        Args:
            hosts: List of target host IP addresses or hostnames
            
        Returns:
            List of ping result dictionaries
            
        Example:
            >>> ping_test = PingTest()
            >>> results = ping_test.run_multiple(["8.8.8.8", "1.1.1.1"])
            >>> for result in results:
            ...     print(f"{result['host']}: {result['avg_ms']}ms")
        """
        logger.info(f"Starting ping test for {len(hosts)} hosts")
        results = []
        
        for host in hosts:
            result = self.run(host)
            results.append(result)
        
        logger.info(f"Completed ping test for {len(hosts)} hosts")
        return results


def ping_host(host: str, packet_count: int = 10, timeout: int = 2) -> Dict:
    """
    Convenience function to ping a single host.
    
    Args:
        host: Target host IP address or hostname
        packet_count: Number of ping packets to send
        timeout: Timeout in seconds for each ping
        
    Returns:
        Dict containing ping statistics
    """
    ping_test = PingTest(packet_count=packet_count, timeout=timeout)
    return ping_test.run(host)
