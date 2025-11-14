"""
Test result validation module.

Validates network test results for completeness and correctness,
ensuring all required fields are present and values are valid.
"""
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class TestResultValidator:
    """
    Validates test results for completeness and correctness.
    
    Checks that test results contain all required fields and that
    values are within expected ranges.
    """
    
    def validate_ping_results(self, results: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate ping test results.
        
        Args:
            results: List of ping result dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Example:
            >>> validator = TestResultValidator()
            >>> is_valid, errors = validator.validate_ping_results(ping_results)
        """
        errors = []
        
        if not results:
            errors.append("Ping results are empty")
            return False, errors
        
        if not isinstance(results, list):
            errors.append("Ping results must be a list")
            return False, errors
        
        required_fields = ['host', 'packets_sent', 'packets_received', 'avg_ms']
        
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                errors.append(f"Ping result {i} is not a dictionary")
                continue
            
            # Check required fields
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                errors.append(
                    f"Ping result {i} missing fields: {', '.join(missing_fields)}"
                )
            
            # Validate numeric fields
            if 'packets_sent' in result and not isinstance(result['packets_sent'], (int, float)):
                errors.append(f"Ping result {i}: packets_sent must be numeric")
            
            if 'packets_received' in result and not isinstance(result['packets_received'], (int, float)):
                errors.append(f"Ping result {i}: packets_received must be numeric")
            
            if 'avg_ms' in result and not isinstance(result['avg_ms'], (int, float)):
                errors.append(f"Ping result {i}: avg_ms must be numeric")
            
            # Check for error field
            if 'error' in result:
                errors.append(f"Ping result {i} contains error: {result['error']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_speed_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """
        Validate speed test results.
        
        Args:
            results: Speed test result dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not results:
            errors.append("Speed results are empty")
            return False, errors
        
        if not isinstance(results, dict):
            errors.append("Speed results must be a dictionary")
            return False, errors
        
        required_fields = ['download_mbps', 'upload_mbps', 'ping_ms']
        
        # Check required fields
        missing_fields = [f for f in required_fields if f not in results]
        if missing_fields:
            errors.append(f"Speed results missing fields: {', '.join(missing_fields)}")
        
        # Validate numeric fields
        if 'download_mbps' in results:
            if not isinstance(results['download_mbps'], (int, float)):
                errors.append("download_mbps must be numeric")
            elif results['download_mbps'] < 0:
                errors.append("download_mbps cannot be negative")
        
        if 'upload_mbps' in results:
            if not isinstance(results['upload_mbps'], (int, float)):
                errors.append("upload_mbps must be numeric")
            elif results['upload_mbps'] < 0:
                errors.append("upload_mbps cannot be negative")
        
        if 'ping_ms' in results:
            if not isinstance(results['ping_ms'], (int, float)):
                errors.append("ping_ms must be numeric")
            elif results['ping_ms'] < 0:
                errors.append("ping_ms cannot be negative")
        
        # Check for error field
        if 'error' in results:
            errors.append(f"Speed results contain error: {results['error']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_packet_loss_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """
        Validate packet loss test results.
        
        Args:
            results: Packet loss result dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not results:
            errors.append("Packet loss results are empty")
            return False, errors
        
        if not isinstance(results, dict):
            errors.append("Packet loss results must be a dictionary")
            return False, errors
        
        required_fields = ['packets_sent', 'packets_received', 'loss_percentage']
        
        # Check required fields
        missing_fields = [f for f in required_fields if f not in results]
        if missing_fields:
            errors.append(
                f"Packet loss results missing fields: {', '.join(missing_fields)}"
            )
        
        # Validate numeric fields
        if 'packets_sent' in results:
            if not isinstance(results['packets_sent'], (int, float)):
                errors.append("packets_sent must be numeric")
            elif results['packets_sent'] < 0:
                errors.append("packets_sent cannot be negative")
        
        if 'packets_received' in results:
            if not isinstance(results['packets_received'], (int, float)):
                errors.append("packets_received must be numeric")
            elif results['packets_received'] < 0:
                errors.append("packets_received cannot be negative")
        
        if 'loss_percentage' in results:
            if not isinstance(results['loss_percentage'], (int, float)):
                errors.append("loss_percentage must be numeric")
            elif results['loss_percentage'] < 0 or results['loss_percentage'] > 100:
                errors.append("loss_percentage must be between 0 and 100")
        
        # Check for error field
        if 'error' in results:
            errors.append(f"Packet loss results contain error: {results['error']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_jitter_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """
        Validate jitter test results.
        
        Args:
            results: Jitter result dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not results:
            errors.append("Jitter results are empty")
            return False, errors
        
        if not isinstance(results, dict):
            errors.append("Jitter results must be a dictionary")
            return False, errors
        
        required_fields = ['avg_jitter_ms', 'max_jitter_ms']
        
        # Check required fields
        missing_fields = [f for f in required_fields if f not in results]
        if missing_fields:
            errors.append(f"Jitter results missing fields: {', '.join(missing_fields)}")
        
        # Validate numeric fields
        if 'avg_jitter_ms' in results:
            if not isinstance(results['avg_jitter_ms'], (int, float)):
                errors.append("avg_jitter_ms must be numeric")
            elif results['avg_jitter_ms'] < 0:
                errors.append("avg_jitter_ms cannot be negative")
        
        if 'max_jitter_ms' in results:
            if not isinstance(results['max_jitter_ms'], (int, float)):
                errors.append("max_jitter_ms must be numeric")
            elif results['max_jitter_ms'] < 0:
                errors.append("max_jitter_ms cannot be negative")
        
        # Check for error field
        if 'error' in results:
            errors.append(f"Jitter results contain error: {results['error']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_dns_results(self, results: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate DNS test results.
        
        Args:
            results: List of DNS result dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not results:
            errors.append("DNS results are empty")
            return False, errors
        
        if not isinstance(results, list):
            errors.append("DNS results must be a list")
            return False, errors
        
        required_fields = ['dns_server', 'avg_resolution_ms', 'queries_tested']
        
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                errors.append(f"DNS result {i} is not a dictionary")
                continue
            
            # Check required fields
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                errors.append(
                    f"DNS result {i} missing fields: {', '.join(missing_fields)}"
                )
            
            # Validate numeric fields
            if 'avg_resolution_ms' in result and not isinstance(result['avg_resolution_ms'], (int, float)):
                errors.append(f"DNS result {i}: avg_resolution_ms must be numeric")
            
            if 'queries_tested' in result and not isinstance(result['queries_tested'], (int, float)):
                errors.append(f"DNS result {i}: queries_tested must be numeric")
            
            # Check for error field
            if 'error' in result:
                errors.append(f"DNS result {i} contains error: {result['error']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_all_results(self, test_results: Dict, config: Any) -> Dict:
        """
        Validate all test results based on what was requested.
        
        Args:
            test_results: Complete test results dictionary
            config: TestConfig object with test selection flags
            
        Returns:
            Dict containing:
                - is_complete: bool - All requested tests completed successfully
                - validation_errors: List[str] - All validation errors
                - missing_tests: List[str] - Tests that were requested but missing
                - partial_tests: List[str] - Tests with errors or incomplete data
                - successful_tests: List[str] - Tests that completed successfully
                
        Example:
            >>> validator = TestResultValidator()
            >>> validation = validator.validate_all_results(test_results, config)
            >>> if not validation['is_complete']:
            ...     print(f"Missing: {validation['missing_tests']}")
        """
        validation_errors = []
        missing_tests = []
        partial_tests = []
        successful_tests = []
        
        # Validate ping results
        if config.run_ping:
            ping_results = test_results.get('ping_results', [])
            if not ping_results:
                missing_tests.append('ping')
                validation_errors.append("Ping test was requested but no results found")
            else:
                is_valid, errors = self.validate_ping_results(ping_results)
                if is_valid:
                    successful_tests.append('ping')
                else:
                    partial_tests.append('ping')
                    validation_errors.extend([f"Ping: {e}" for e in errors])
        
        # Validate jitter results
        if config.run_jitter:
            jitter_results = test_results.get('jitter_results', {})
            if not jitter_results:
                missing_tests.append('jitter')
                validation_errors.append("Jitter test was requested but no results found")
            else:
                is_valid, errors = self.validate_jitter_results(jitter_results)
                if is_valid:
                    successful_tests.append('jitter')
                else:
                    partial_tests.append('jitter')
                    validation_errors.extend([f"Jitter: {e}" for e in errors])
        
        # Validate packet loss results
        if config.run_packet_loss:
            packet_loss_results = test_results.get('packet_loss_results', {})
            if not packet_loss_results:
                missing_tests.append('packet_loss')
                validation_errors.append("Packet loss test was requested but no results found")
            else:
                is_valid, errors = self.validate_packet_loss_results(packet_loss_results)
                if is_valid:
                    successful_tests.append('packet_loss')
                else:
                    partial_tests.append('packet_loss')
                    validation_errors.extend([f"Packet loss: {e}" for e in errors])
        
        # Validate speed results
        if config.run_speed:
            speed_results = test_results.get('speed_results', {})
            if not speed_results:
                missing_tests.append('speed')
                validation_errors.append("Speed test was requested but no results found")
            else:
                is_valid, errors = self.validate_speed_results(speed_results)
                if is_valid:
                    successful_tests.append('speed')
                else:
                    partial_tests.append('speed')
                    validation_errors.extend([f"Speed: {e}" for e in errors])
        
        # Validate DNS results
        if config.run_dns:
            dns_results = test_results.get('dns_results', [])
            if not dns_results:
                missing_tests.append('dns')
                validation_errors.append("DNS test was requested but no results found")
            else:
                is_valid, errors = self.validate_dns_results(dns_results)
                if is_valid:
                    successful_tests.append('dns')
                else:
                    partial_tests.append('dns')
                    validation_errors.extend([f"DNS: {e}" for e in errors])
        
        # Determine if complete
        is_complete = len(missing_tests) == 0 and len(partial_tests) == 0
        
        # Log validation summary
        if is_complete:
            logger.info(f"All requested tests completed successfully: {successful_tests}")
        else:
            if missing_tests:
                logger.warning(f"Missing tests: {missing_tests}")
            if partial_tests:
                logger.warning(f"Partial/failed tests: {partial_tests}")
            if validation_errors:
                logger.warning(f"Validation errors: {validation_errors}")
        
        return {
            "is_complete": is_complete,
            "validation_errors": validation_errors,
            "missing_tests": missing_tests,
            "partial_tests": partial_tests,
            "successful_tests": successful_tests
        }
