"""
Health check utilities for verifying test component availability.

Checks that required libraries and configurations are available
before running network tests.
"""
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


def check_ping3_available() -> Dict[str, any]:
    """
    Check if ping3 library is available.
    
    Returns:
        Dict with 'available' (bool) and 'message' (str)
    """
    try:
        import ping3
        return {
            "available": True,
            "message": "ping3 library is available",
            "version": getattr(ping3, '__version__', 'unknown')
        }
    except ImportError as e:
        logger.warning(f"ping3 library not available: {e}")
        return {
            "available": False,
            "message": f"ping3 library not found: {e}",
            "error": str(e)
        }


def check_speedtest_available() -> Dict[str, any]:
    """
    Check if speedtest library is available.
    
    Returns:
        Dict with 'available' (bool) and 'message' (str)
    """
    try:
        import speedtest
        return {
            "available": True,
            "message": "speedtest library is available",
            "version": getattr(speedtest, '__version__', 'unknown')
        }
    except ImportError as e:
        logger.warning(f"speedtest library not available: {e}")
        return {
            "available": False,
            "message": f"speedtest library not found: {e}",
            "error": str(e)
        }


def check_gemini_api_key() -> Dict[str, any]:
    """
    Check if Gemini API key is configured.
    
    Returns:
        Dict with 'available' (bool) and 'message' (str)
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        # Don't log the actual key, just confirm it exists
        key_preview = f"{api_key[:8]}..." if len(api_key) > 8 else "***"
        return {
            "available": True,
            "message": f"Gemini API key is configured ({key_preview})",
            "configured": True
        }
    else:
        logger.warning("Gemini API key not configured")
        return {
            "available": False,
            "message": "Gemini API key not found in environment variables",
            "configured": False
        }


def check_supabase_config() -> Dict[str, any]:
    """
    Check if Supabase configuration is available.
    
    Returns:
        Dict with 'available' (bool) and 'message' (str)
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if url and key:
        return {
            "available": True,
            "message": "Supabase configuration is complete",
            "url_configured": True,
            "key_configured": True
        }
    else:
        missing = []
        if not url:
            missing.append("SUPABASE_URL")
        if not key:
            missing.append("SUPABASE_KEY")
        
        logger.warning(f"Supabase configuration incomplete: missing {', '.join(missing)}")
        return {
            "available": False,
            "message": f"Supabase configuration incomplete: missing {', '.join(missing)}",
            "url_configured": bool(url),
            "key_configured": bool(key)
        }


def run_all_health_checks() -> Dict[str, Dict]:
    """
    Run all health checks and return results.
    
    Returns:
        Dict with results for each component
        
    Example:
        >>> health = run_all_health_checks()
        >>> if not health['ping3']['available']:
        ...     print("Warning: ping3 not available")
    """
    logger.info("Running health checks for all components")
    
    results = {
        "ping3": check_ping3_available(),
        "speedtest": check_speedtest_available(),
        "gemini_api": check_gemini_api_key(),
        "supabase": check_supabase_config()
    }
    
    # Log summary
    available_count = sum(1 for r in results.values() if r['available'])
    total_count = len(results)
    
    logger.info(f"Health check complete: {available_count}/{total_count} components available")
    
    # Log warnings for unavailable components
    for component, result in results.items():
        if not result['available']:
            logger.warning(f"Component '{component}' is not available: {result['message']}")
    
    return results


def get_health_status() -> Dict[str, any]:
    """
    Get overall health status.
    
    Returns:
        Dict with overall status and component details
    """
    checks = run_all_health_checks()
    
    # Determine overall status
    critical_components = ['supabase']  # Components required for basic operation
    optional_components = ['ping3', 'speedtest', 'gemini_api']
    
    critical_ok = all(checks[c]['available'] for c in critical_components if c in checks)
    optional_ok = all(checks[c]['available'] for c in optional_components if c in checks)
    
    if critical_ok and optional_ok:
        status = "healthy"
        message = "All components are available"
    elif critical_ok:
        status = "degraded"
        unavailable = [c for c in optional_components if c in checks and not checks[c]['available']]
        message = f"Some optional components unavailable: {', '.join(unavailable)}"
    else:
        status = "unhealthy"
        unavailable = [c for c in critical_components if c in checks and not checks[c]['available']]
        message = f"Critical components unavailable: {', '.join(unavailable)}"
    
    return {
        "status": status,
        "message": message,
        "components": checks,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


def log_startup_health_check():
    """
    Run and log health check at application startup.
    
    This should be called when the application starts to verify
    all components are available.
    """
    logger.info("=" * 60)
    logger.info("STARTUP HEALTH CHECK")
    logger.info("=" * 60)
    
    health = get_health_status()
    
    logger.info(f"Overall Status: {health['status'].upper()}")
    logger.info(f"Message: {health['message']}")
    logger.info("")
    logger.info("Component Status:")
    
    for component, result in health['components'].items():
        status_icon = "✓" if result['available'] else "✗"
        logger.info(f"  {status_icon} {component}: {result['message']}")
    
    logger.info("=" * 60)
    
    return health
