"""
DNS latency test module for measuring DNS resolution performance.
"""
import logging
import time
import statistics
from typing import Dict, List
import dns.resolver
import dns.exception

logger = logging.getLogger(__name__)


class DNSTest:
    """
    Measures DNS resolution latency for various DNS servers.
    
    Tests multiple domains against different DNS servers to measure
    resolution performance and reliability.
    """
    
    # Common domains to test DNS resolution
    DEFAULT_TEST_DOMAINS = [
        "google.com",
        "cloudflare.com",
        "amazon.com",
        "microsoft.com",
        "github.com"
    ]
    
    def __init__(self, test_domains: List[str] = None, timeout: int = 5):
        """
        Initialize DNS test configuration.
        
        Args:
            test_domains: List of domains to test (default: common domains)
            timeout: Timeout in seconds for DNS queries (default: 5)
        """
        self.test_domains = test_domains or self.DEFAULT_TEST_DOMAINS
        self.timeout = timeout
    
    def run(self, dns_server: str) -> Dict:
        """
        Execute DNS test for a single DNS server.
        
        Args:
            dns_server: DNS server IP address (e.g., "8.8.8.8")
            
        Returns:
            Dict containing DNS test results:
                - dns_server: DNS server IP
                - avg_resolution_ms: Average resolution time in milliseconds
                - min_resolution_ms: Minimum resolution time
                - max_resolution_ms: Maximum resolution time
                - queries_tested: Number of queries attempted
                - successful_queries: Number of successful queries
                - failed_queries: Number of failed queries
                - success_rate: Success rate percentage
                - resolution_times: List of individual resolution times
                
        Example:
            >>> dns_test = DNSTest()
            >>> result = dns_test.run("8.8.8.8")
            >>> print(f"Average DNS resolution: {result['avg_resolution_ms']}ms")
        """
        logger.info(f"Starting DNS test for server: {dns_server}")
        
        resolution_times = []
        successful_queries = 0
        failed_queries = 0
        
        # Create resolver with custom DNS server
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = self.timeout
        resolver.lifetime = self.timeout
        
        try:
            for domain in self.test_domains:
                try:
                    # Measure resolution time
                    start_time = time.time()
                    answers = resolver.resolve(domain, 'A')
                    end_time = time.time()
                    
                    resolution_time_ms = (end_time - start_time) * 1000
                    resolution_times.append(resolution_time_ms)
                    successful_queries += 1
                    
                    logger.debug(
                        f"DNS resolution for {domain} via {dns_server}: "
                        f"{resolution_time_ms:.2f}ms"
                    )
                    
                except dns.exception.Timeout:
                    logger.warning(f"DNS query timeout for {domain} via {dns_server}")
                    failed_queries += 1
                except dns.exception.DNSException as e:
                    logger.warning(f"DNS query failed for {domain} via {dns_server}: {e}")
                    failed_queries += 1
                except Exception as e:
                    logger.error(f"Unexpected error querying {domain} via {dns_server}: {e}")
                    failed_queries += 1
            
            # Calculate statistics
            queries_tested = successful_queries + failed_queries
            success_rate = (successful_queries / queries_tested * 100) if queries_tested > 0 else 0
            
            if resolution_times:
                result = {
                    "dns_server": dns_server,
                    "avg_resolution_ms": round(statistics.mean(resolution_times), 2),
                    "min_resolution_ms": round(min(resolution_times), 2),
                    "max_resolution_ms": round(max(resolution_times), 2),
                    "stddev_resolution_ms": round(statistics.stdev(resolution_times), 2) if len(resolution_times) > 1 else 0.0,
                    "queries_tested": queries_tested,
                    "successful_queries": successful_queries,
                    "failed_queries": failed_queries,
                    "success_rate": round(success_rate, 2),
                    "resolution_times": [round(t, 2) for t in resolution_times]
                }
            else:
                # All queries failed
                result = {
                    "dns_server": dns_server,
                    "avg_resolution_ms": 0.0,
                    "min_resolution_ms": 0.0,
                    "max_resolution_ms": 0.0,
                    "stddev_resolution_ms": 0.0,
                    "queries_tested": queries_tested,
                    "successful_queries": 0,
                    "failed_queries": failed_queries,
                    "success_rate": 0.0,
                    "resolution_times": [],
                    "error": "All DNS queries failed"
                }
            
            logger.info(
                f"DNS test completed for {dns_server}: "
                f"{successful_queries}/{queries_tested} successful, "
                f"avg resolution: {result['avg_resolution_ms']}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"DNS test failed for {dns_server}: {e}")
            return {
                "dns_server": dns_server,
                "avg_resolution_ms": 0.0,
                "min_resolution_ms": 0.0,
                "max_resolution_ms": 0.0,
                "stddev_resolution_ms": 0.0,
                "queries_tested": len(self.test_domains),
                "successful_queries": 0,
                "failed_queries": len(self.test_domains),
                "success_rate": 0.0,
                "resolution_times": [],
                "error": str(e)
            }
    
    def run_multiple(self, dns_servers: List[str]) -> List[Dict]:
        """
        Execute DNS test for multiple DNS servers.
        
        Args:
            dns_servers: List of DNS server IP addresses
            
        Returns:
            List of DNS test result dictionaries
            
        Example:
            >>> dns_test = DNSTest()
            >>> results = dns_test.run_multiple(["8.8.8.8", "1.1.1.1", "208.67.222.222"])
            >>> for result in results:
            ...     print(f"{result['dns_server']}: {result['avg_resolution_ms']}ms")
        """
        logger.info(f"Starting DNS test for {len(dns_servers)} servers")
        results = []
        
        for dns_server in dns_servers:
            result = self.run(dns_server)
            results.append(result)
        
        logger.info(f"Completed DNS test for {len(dns_servers)} servers")
        return results
    
    def compare_dns_servers(self, results: List[Dict]) -> Dict:
        """
        Compare multiple DNS server results and recommend the best one.
        
        Args:
            results: List of DNS test results from run_multiple()
            
        Returns:
            Dict with comparison and recommendation
            
        Example:
            >>> dns_test = DNSTest()
            >>> results = dns_test.run_multiple(["8.8.8.8", "1.1.1.1"])
            >>> comparison = dns_test.compare_dns_servers(results)
            >>> print(f"Recommended DNS: {comparison['recommended_server']}")
        """
        if not results:
            return {"error": "No results to compare"}
        
        # Filter out failed tests
        valid_results = [r for r in results if r.get('successful_queries', 0) > 0]
        
        if not valid_results:
            return {"error": "All DNS tests failed"}
        
        # Find fastest DNS server
        fastest = min(valid_results, key=lambda x: x['avg_resolution_ms'])
        slowest = max(valid_results, key=lambda x: x['avg_resolution_ms'])
        
        # Find most reliable DNS server
        most_reliable = max(valid_results, key=lambda x: x['success_rate'])
        
        return {
            "fastest_server": fastest['dns_server'],
            "fastest_avg_ms": fastest['avg_resolution_ms'],
            "slowest_server": slowest['dns_server'],
            "slowest_avg_ms": slowest['avg_resolution_ms'],
            "most_reliable_server": most_reliable['dns_server'],
            "most_reliable_success_rate": most_reliable['success_rate'],
            "recommended_server": fastest['dns_server'],
            "speed_improvement": round(slowest['avg_resolution_ms'] - fastest['avg_resolution_ms'], 2),
            "all_results": valid_results
        }
    
    def assess_dns_performance(self, avg_resolution_ms: float) -> str:
        """
        Assess DNS performance based on average resolution time.
        
        Args:
            avg_resolution_ms: Average DNS resolution time in milliseconds
            
        Returns:
            String describing DNS performance
        """
        if avg_resolution_ms < 10:
            return "Excellent"
        elif avg_resolution_ms < 20:
            return "Very Good"
        elif avg_resolution_ms < 50:
            return "Good"
        elif avg_resolution_ms < 100:
            return "Fair"
        elif avg_resolution_ms < 200:
            return "Poor"
        else:
            return "Very Poor"


def test_dns_server(dns_server: str, test_domains: List[str] = None, timeout: int = 5) -> Dict:
    """
    Convenience function to test a single DNS server.
    
    Args:
        dns_server: DNS server IP address
        test_domains: List of domains to test
        timeout: Timeout in seconds for DNS queries
        
    Returns:
        Dict containing DNS test results
    """
    dns_test = DNSTest(test_domains=test_domains, timeout=timeout)
    return dns_test.run(dns_server)
