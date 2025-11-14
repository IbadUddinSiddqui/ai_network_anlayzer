"""
Network test orchestrator that runs all network tests and aggregates results.
"""
import logging
import asyncio
from typing import Dict, List, Tuple, Optional, Callable
from datetime import datetime
from uuid import uuid4
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from .ping_test import PingTest
from .jitter_test import JitterTest
from .packet_loss_test import PacketLossTest
from .speed_test import SpeedTest
from .dns_test import DNSTest
from core.validation.test_results import TestResultValidator
from core.utils.error_handling import log_and_capture_exception, retry_async

logger = logging.getLogger(__name__)


class NetworkTestRunner:
    """
    Orchestrates all network tests and aggregates results.
    
    Runs ping, jitter, packet loss, speed, and DNS tests in a coordinated manner,
    handling errors gracefully and providing progress updates with retry logic.
    """
    
    def __init__(self):
        """Initialize the network test runner."""
        self.test_id = None
        self.progress_callback = None
        self.validator = TestResultValidator()
        self.max_retries = 2
        self.retry_delay = 2.0
    
    def set_progress_callback(self, callback):
        """
        Set a callback function for progress updates.
        
        Args:
            callback: Function that accepts (step: str, progress: float) parameters
        """
        self.progress_callback = callback
    
    def _update_progress(self, step: str, progress: float):
        """
        Update progress if callback is set.
        
        Args:
            step: Description of current step
            progress: Progress percentage (0-100)
        """
        if self.progress_callback:
            self.progress_callback(step, progress)
        logger.info(f"Progress: {step} ({progress}%)")
    
    async def _run_test_with_retry(
        self,
        test_func: Callable,
        test_name: str,
        *args,
        **kwargs
    ) -> Tuple[Optional[Dict], Optional[str], str]:
        """
        Run a test with retry logic.
        
        Args:
            test_func: Test function to execute
            test_name: Name of the test for logging
            *args: Positional arguments for test_func
            **kwargs: Keyword arguments for test_func
            
        Returns:
            Tuple of (result_dict, error_message, status)
            status can be: "success", "failed", "skipped"
        """
        try:
            result = await retry_async(
                test_func,
                max_retries=self.max_retries,
                delay=self.retry_delay,
                *args,
                **kwargs
            )
            
            # Check if result contains error
            if isinstance(result, dict) and 'error' in result:
                error_msg = result['error']
                logger.warning(f"{test_name} completed with error: {error_msg}")
                return result, error_msg, "failed"
            
            logger.info(f"{test_name} completed successfully")
            return result, None, "success"
            
        except Exception as e:
            error_dict = log_and_capture_exception(
                logger,
                test_name,
                e,
                self.test_id
            )
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"{test_name} failed after {self.max_retries + 1} attempts: {error_msg}")
            return None, error_msg, "failed"
    
    async def run_all_tests(
        self,
        target_hosts: List[str] = None,
        dns_servers: List[str] = None,
        packet_count: int = 100,
        run_ping: bool = True,
        run_jitter: bool = True,
        run_packet_loss: bool = True,
        run_speed: bool = True,
        run_dns: bool = True
    ) -> Dict:
        """
        Execute selected network tests asynchronously.
        
        Args:
            target_hosts: List of hosts to ping (default: ["8.8.8.8", "1.1.1.1"])
            dns_servers: List of DNS servers to test (default: ["8.8.8.8", "1.1.1.1"])
            packet_count: Number of packets for packet loss test (default: 100)
            run_ping: Whether to run ping test (default: True)
            run_jitter: Whether to run jitter test (default: True)
            run_packet_loss: Whether to run packet loss test (default: True)
            run_speed: Whether to run speed test (default: True)
            run_dns: Whether to run DNS test (default: True)
            
        Returns:
            Dict containing selected test results in JSON format
            
        Example:
            >>> runner = NetworkTestRunner()
            >>> results = await runner.run_all_tests(run_speed=False, run_dns=False)
            >>> print(f"Test ID: {results['test_id']}")
        """
        # Set defaults
        target_hosts = target_hosts or ["8.8.8.8", "1.1.1.1"]
        dns_servers = dns_servers or ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        
        # Generate test ID
        self.test_id = str(uuid4())
        test_timestamp = datetime.utcnow()
        
        # Count enabled tests for progress calculation
        enabled_tests = sum([run_ping, run_jitter, run_packet_loss, run_speed, run_dns])
        progress_per_test = 90 / enabled_tests if enabled_tests > 0 else 0
        current_progress = 5
        
        logger.info(f"Starting network test suite (ID: {self.test_id}) - {enabled_tests} tests enabled")
        self._update_progress("Initializing tests", 0)
        
        results = {
            "test_id": self.test_id,
            "timestamp": test_timestamp.isoformat(),
            "status": "running",
            "ping_results": [],
            "jitter_results": {},
            "packet_loss_results": {},
            "speed_results": {},
            "dns_results": [],
            "test_status": {
                "ping": "skipped",
                "jitter": "skipped",
                "packet_loss": "skipped",
                "speed": "skipped",
                "dns": "skipped"
            },
            "errors": {
                "ping": None,
                "jitter": None,
                "packet_loss": None,
                "speed": None,
                "dns": None
            }
        }
        
        try:
            # Step 1: Ping Test
            if run_ping:
                self._update_progress("Running ping tests", current_progress)
                ping_results, ping_error, ping_status = await self._run_ping_tests(target_hosts)
                results["ping_results"] = ping_results
                results["test_status"]["ping"] = ping_status
                results["errors"]["ping"] = ping_error
                current_progress += progress_per_test
                self._update_progress("Ping tests completed", current_progress)
            else:
                logger.info("Ping test skipped")
            
            # Step 2: Jitter Test
            if run_jitter:
                self._update_progress("Running jitter tests", current_progress)
                jitter_results, jitter_error, jitter_status = await self._run_jitter_tests(target_hosts[0])
                results["jitter_results"] = jitter_results
                results["test_status"]["jitter"] = jitter_status
                results["errors"]["jitter"] = jitter_error
                current_progress += progress_per_test
                self._update_progress("Jitter tests completed", current_progress)
            else:
                logger.info("Jitter test skipped")
            
            # Step 3: Packet Loss Test
            if run_packet_loss:
                self._update_progress("Running packet loss tests", current_progress)
                packet_loss_results, packet_loss_error, packet_loss_status = await self._run_packet_loss_test(target_hosts[0], packet_count)
                results["packet_loss_results"] = packet_loss_results
                results["test_status"]["packet_loss"] = packet_loss_status
                results["errors"]["packet_loss"] = packet_loss_error
                current_progress += progress_per_test
                self._update_progress("Packet loss tests completed", current_progress)
            else:
                logger.info("Packet loss test skipped")
            
            # Step 4: Speed Test
            if run_speed:
                self._update_progress("Running speed test", current_progress)
                speed_results, speed_error, speed_status = await self._run_speed_test()
                results["speed_results"] = speed_results
                results["test_status"]["speed"] = speed_status
                results["errors"]["speed"] = speed_error
                current_progress += progress_per_test
                self._update_progress("Speed test completed", current_progress)
            else:
                logger.info("Speed test skipped")
            
            # Step 5: DNS Test
            if run_dns:
                self._update_progress("Running DNS tests", current_progress)
                dns_results, dns_error, dns_status = await self._run_dns_tests(dns_servers)
                results["dns_results"] = dns_results
                results["test_status"]["dns"] = dns_status
                results["errors"]["dns"] = dns_error
                current_progress += progress_per_test
                self._update_progress("DNS tests completed", current_progress)
            else:
                logger.info("DNS test skipped")
            
            # Determine overall status based on individual test results
            test_statuses = results["test_status"]
            successful_tests = [k for k, v in test_statuses.items() if v == "success"]
            failed_tests = [k for k, v in test_statuses.items() if v == "failed"]
            
            if failed_tests and successful_tests:
                results["status"] = "partial"
                logger.warning(f"Test suite partially completed. Failed: {failed_tests}, Succeeded: {successful_tests}")
            elif failed_tests and not successful_tests:
                results["status"] = "failed"
                logger.error(f"All tests failed: {failed_tests}")
            else:
                results["status"] = "completed"
                logger.info(f"All tests completed successfully: {successful_tests}")
            
            self._update_progress("All tests completed", 100)
            
            logger.info(f"Network test suite finished (ID: {self.test_id}, Status: {results['status']})")
            
        except Exception as e:
            error_dict = log_and_capture_exception(logger, "test_suite", e, self.test_id)
            results["status"] = "failed"
            results["error"] = str(e)
            self._update_progress("Tests failed", 100)
        
        return results
    
    async def _run_ping_tests(self, hosts: List[str]) -> Tuple[List[Dict], Optional[str], str]:
        """
        Run ping tests for multiple hosts with retry logic.
        
        Returns:
            Tuple of (results_list, error_message, status)
        """
        logger.info(f"Running ping tests for {len(hosts)} hosts")
        ping_test = PingTest(packet_count=10)
        
        # Run tests in parallel with retry for each host
        processed_results = []
        has_errors = False
        error_messages = []
        
        for host in hosts:
            result, error, status = await self._run_test_with_retry(
                asyncio.to_thread,
                f"ping_test_{host}",
                ping_test.run,
                host
            )
            
            if result:
                processed_results.append(result)
            else:
                # Add placeholder result with error
                processed_results.append({
                    "host": host,
                    "error": error or "Unknown error",
                    "packets_sent": 0,
                    "packets_received": 0,
                    "min_ms": 0.0,
                    "max_ms": 0.0,
                    "avg_ms": 0.0,
                    "stddev_ms": 0.0
                })
                has_errors = True
                error_messages.append(f"{host}: {error}")
        
        overall_status = "failed" if has_errors and not processed_results else "success"
        overall_error = "; ".join(error_messages) if error_messages else None
        
        return processed_results, overall_error, overall_status
    
    async def _run_jitter_tests(self, host: str) -> Tuple[Dict, Optional[str], str]:
        """
        Run jitter test for a single host with retry logic.
        
        Returns:
            Tuple of (result_dict, error_message, status)
        """
        logger.info(f"Running jitter test for {host}")
        jitter_test = JitterTest(measurement_count=20)
        
        result, error, status = await self._run_test_with_retry(
            asyncio.to_thread,
            "jitter_test",
            jitter_test.run,
            host
        )
        
        if not result:
            result = {
                "host": host,
                "avg_jitter_ms": 0.0,
                "max_jitter_ms": 0.0,
                "min_jitter_ms": 0.0,
                "error": error or "Unknown error"
            }
        
        return result, error, status
    
    async def _run_packet_loss_test(self, host: str, packet_count: int) -> Tuple[Dict, Optional[str], str]:
        """
        Run packet loss test for a single host with retry logic.
        
        Returns:
            Tuple of (result_dict, error_message, status)
        """
        logger.info(f"Running packet loss test for {host}")
        packet_test = PacketLossTest(packet_count=packet_count)
        
        result, error, status = await self._run_test_with_retry(
            asyncio.to_thread,
            "packet_loss_test",
            packet_test.run,
            host
        )
        
        if not result:
            result = {
                "host": host,
                "packets_sent": 0,
                "packets_received": 0,
                "packets_lost": 0,
                "loss_percentage": 0.0,
                "error": error or "Unknown error"
            }
        
        return result, error, status
    
    async def _run_speed_test(self) -> Tuple[Dict, Optional[str], str]:
        """
        Run internet speed test with retry logic.
        
        Returns:
            Tuple of (result_dict, error_message, status)
        """
        logger.info("Running speed test")
        speed_test = SpeedTest()
        
        result, error, status = await self._run_test_with_retry(
            asyncio.to_thread,
            "speed_test",
            speed_test.run
        )
        
        if not result:
            result = {
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "ping_ms": 0.0,
                "server_location": "Unknown",
                "error": error or "Unknown error"
            }
        
        return result, error, status
    
    async def _run_dns_tests(self, dns_servers: List[str]) -> Tuple[List[Dict], Optional[str], str]:
        """
        Run DNS tests for multiple servers with retry logic.
        
        Returns:
            Tuple of (results_list, error_message, status)
        """
        logger.info(f"Running DNS tests for {len(dns_servers)} servers")
        dns_test = DNSTest()
        
        # Run tests with retry for each server
        processed_results = []
        has_errors = False
        error_messages = []
        
        for server in dns_servers:
            result, error, status = await self._run_test_with_retry(
                asyncio.to_thread,
                f"dns_test_{server}",
                dns_test.run,
                server
            )
            
            if result:
                processed_results.append(result)
            else:
                # Add placeholder result with error
                processed_results.append({
                    "dns_server": server,
                    "avg_resolution_ms": 0.0,
                    "queries_tested": 0,
                    "successful_queries": 0,
                    "error": error or "Unknown error"
                })
                has_errors = True
                error_messages.append(f"{server}: {error}")
        
        overall_status = "failed" if has_errors and not processed_results else "success"
        overall_error = "; ".join(error_messages) if error_messages else None
        
        return processed_results, overall_error, overall_status
    
    def run_all_tests_sync(
        self,
        target_hosts: List[str] = None,
        dns_servers: List[str] = None,
        packet_count: int = 100
    ) -> Dict:
        """
        Synchronous wrapper for run_all_tests.
        
        Args:
            target_hosts: List of hosts to ping
            dns_servers: List of DNS servers to test
            packet_count: Number of packets for packet loss test
            
        Returns:
            Dict containing all test results
        """
        return asyncio.run(self.run_all_tests(target_hosts, dns_servers, packet_count))
    
    def export_results_json(self, results: Dict, filepath: str):
        """
        Export test results to JSON file.
        
        Args:
            results: Test results dictionary
            filepath: Path to output JSON file
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export results: {e}")


# Convenience function
async def run_network_tests(
    target_hosts: List[str] = None,
    dns_servers: List[str] = None,
    packet_count: int = 100
) -> Dict:
    """
    Convenience function to run all network tests.
    
    Args:
        target_hosts: List of hosts to ping
        dns_servers: List of DNS servers to test
        packet_count: Number of packets for packet loss test
        
    Returns:
        Dict containing all test results
    """
    runner = NetworkTestRunner()
    return await runner.run_all_tests(target_hosts, dns_servers, packet_count)
