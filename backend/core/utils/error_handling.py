"""
Error handling and retry utilities for network tests.

Provides consistent error logging, exception handling, and retry logic
with exponential backoff for transient failures.
"""
import logging
import asyncio
import traceback
from typing import Dict, Callable, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TestExecutionError(Exception):
    """Base exception for test execution errors."""
    pass


class ValidationError(Exception):
    """Exception for validation failures."""
    pass


def log_and_capture_exception(
    logger_instance: logging.Logger,
    context: str,
    exception: Exception,
    test_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log exception with full context and return error dictionary.
    
    Args:
        logger_instance: Logger instance to use
        context: Context description (e.g., "ping_test", "ai_analysis")
        exception: The exception that occurred
        test_id: Optional test ID for traceability
        
    Returns:
        Dict containing error details:
            - error: String representation of exception
            - error_type: Exception class name
            - context: Context where error occurred
            - timestamp: ISO format timestamp
            - test_id: Test ID if provided
            - traceback: Full traceback string
            
    Example:
        >>> try:
        ...     result = run_test()
        ... except Exception as e:
        ...     error_dict = log_and_capture_exception(logger, "speed_test", e, test_id)
    """
    error_dict = {
        "error": str(exception),
        "error_type": type(exception).__name__,
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
        "traceback": traceback.format_exc()
    }
    
    if test_id:
        error_dict["test_id"] = test_id
    
    # Log with full context
    log_message = (
        f"Error in {context}: {type(exception).__name__}: {str(exception)}"
    )
    
    if test_id:
        log_message = f"[Test {test_id}] {log_message}"
    
    logger_instance.error(
        log_message,
        exc_info=True,
        extra={"context": context, "test_id": test_id}
    )
    
    return error_dict


async def retry_async(
    func: Callable,
    *args,
    max_retries: int = 2,
    delay: float = 2.0,
    exponential_backoff: bool = True,
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts (default: 2)
        delay: Initial delay between retries in seconds (default: 2.0)
        exponential_backoff: Use exponential backoff if True (default: True)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result from successful function execution
        
    Raises:
        Last exception if all retries are exhausted
        
    Example:
        >>> result = await retry_async(
        ...     some_async_function,
        ...     max_retries=3,
        ...     delay=1.0,
        ...     arg1="value"
        ... )
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries} for {func.__name__}")
            
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"{func.__name__} succeeded on retry attempt {attempt}")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate wait time with exponential backoff
                if exponential_backoff:
                    wait_time = delay * (2 ** attempt)
                else:
                    wait_time = delay
                
                logger.warning(
                    f"{func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                )
    
    # All retries exhausted, raise last exception
    raise last_exception


def retry_sync(
    func: Callable,
    *args,
    max_retries: int = 2,
    delay: float = 2.0,
    exponential_backoff: bool = True,
    **kwargs
) -> Any:
    """
    Retry synchronous function with exponential backoff.
    
    Args:
        func: Synchronous function to retry
        max_retries: Maximum number of retry attempts (default: 2)
        delay: Initial delay between retries in seconds (default: 2.0)
        exponential_backoff: Use exponential backoff if True (default: True)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result from successful function execution
        
    Raises:
        Last exception if all retries are exhausted
        
    Example:
        >>> result = retry_sync(
        ...     some_function,
        ...     max_retries=3,
        ...     delay=1.0,
        ...     arg1="value"
        ... )
    """
    import time
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries} for {func.__name__}")
            
            result = func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"{func.__name__} succeeded on retry attempt {attempt}")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate wait time with exponential backoff
                if exponential_backoff:
                    wait_time = delay * (2 ** attempt)
                else:
                    wait_time = delay
                
                logger.warning(
                    f"{func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                
                time.sleep(wait_time)
            else:
                logger.error(
                    f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                )
    
    # All retries exhausted, raise last exception
    raise last_exception


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 2,
        initial_delay: float = 2.0,
        exponential_backoff: bool = True,
        max_delay: float = 30.0
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            exponential_backoff: Use exponential backoff if True
            max_delay: Maximum delay between retries in seconds
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.exponential_backoff = exponential_backoff
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.exponential_backoff:
            delay = self.initial_delay * (2 ** attempt)
        else:
            delay = self.initial_delay
        
        return min(delay, self.max_delay)
