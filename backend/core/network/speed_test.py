"""
Speed test module for measuring network bandwidth.
"""
import logging
from typing import Dict
import speedtest

logger = logging.getLogger(__name__)


class SpeedTest:
    """
    Measures network upload and download speeds using speedtest-cli.
    
    Connects to the nearest speedtest server and measures bandwidth.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize speed test configuration.
        
        Args:
            timeout: Timeout in seconds for speed test (default: 30)
        """
        self.timeout = timeout
    
    def run(self) -> Dict:
        """
        Execute speed test.
        
        Returns:
            Dict containing speed test results:
                - download_mbps: Download speed in Mbps
                - upload_mbps: Upload speed in Mbps
                - ping_ms: Ping latency in milliseconds
                - server_location: Server location (city, country)
                - server_host: Server hostname
                - isp: Internet Service Provider name
                
        Example:
            >>> speed_test = SpeedTest()
            >>> result = speed_test.run()
            >>> print(f"Download: {result['download_mbps']} Mbps")
            >>> print(f"Upload: {result['upload_mbps']} Mbps")
        """
        logger.info("Starting speed test...")
        
        try:
            # Initialize speedtest client
            st = speedtest.Speedtest()
            
            # Get best server based on ping
            logger.info("Finding best server...")
            st.get_best_server()
            
            server = st.results.server
            logger.info(f"Using server: {server['sponsor']} in {server['name']}, {server['country']}")
            
            # Measure download speed
            logger.info("Measuring download speed...")
            download_bps = st.download()
            download_mbps = download_bps / 1_000_000  # Convert to Mbps
            
            # Measure upload speed
            logger.info("Measuring upload speed...")
            upload_bps = st.upload()
            upload_mbps = upload_bps / 1_000_000  # Convert to Mbps
            
            # Get ping
            ping_ms = st.results.ping
            
            result = {
                "download_mbps": round(download_mbps, 2),
                "upload_mbps": round(upload_mbps, 2),
                "ping_ms": round(ping_ms, 2),
                "server_location": f"{server['name']}, {server['country']}",
                "server_host": server['host'],
                "server_sponsor": server['sponsor'],
                "isp": st.results.client.get('isp', 'Unknown'),
                "download_bytes": download_bps,
                "upload_bytes": upload_bps
            }
            
            logger.info(
                f"Speed test completed: "
                f"Download: {download_mbps:.2f} Mbps, "
                f"Upload: {upload_mbps:.2f} Mbps, "
                f"Ping: {ping_ms:.2f} ms"
            )
            
            return result
            
        except speedtest.ConfigRetrievalError as e:
            logger.error(f"Failed to retrieve speedtest configuration: {e}")
            return {
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "ping_ms": 0.0,
                "server_location": "Unknown",
                "server_host": "Unknown",
                "server_sponsor": "Unknown",
                "isp": "Unknown",
                "error": "Configuration retrieval failed"
            }
        except speedtest.SpeedtestException as e:
            logger.error(f"Speed test failed: {e}")
            return {
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "ping_ms": 0.0,
                "server_location": "Unknown",
                "server_host": "Unknown",
                "server_sponsor": "Unknown",
                "isp": "Unknown",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error during speed test: {e}")
            return {
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "ping_ms": 0.0,
                "server_location": "Unknown",
                "server_host": "Unknown",
                "server_sponsor": "Unknown",
                "isp": "Unknown",
                "error": str(e)
            }
    
    def assess_speed_quality(self, download_mbps: float, upload_mbps: float) -> Dict:
        """
        Assess internet speed quality based on download/upload speeds.
        
        Args:
            download_mbps: Download speed in Mbps
            upload_mbps: Upload speed in Mbps
            
        Returns:
            Dict with quality assessment
            
        Example:
            >>> test = SpeedTest()
            >>> assessment = test.assess_speed_quality(95.5, 45.2)
            >>> print(assessment['download_quality'])  # "Excellent"
        """
        def assess_download(speed):
            if speed >= 100:
                return "Excellent"
            elif speed >= 50:
                return "Very Good"
            elif speed >= 25:
                return "Good"
            elif speed >= 10:
                return "Fair"
            elif speed >= 3:
                return "Poor"
            else:
                return "Very Poor"
        
        def assess_upload(speed):
            if speed >= 50:
                return "Excellent"
            elif speed >= 25:
                return "Very Good"
            elif speed >= 10:
                return "Good"
            elif speed >= 5:
                return "Fair"
            elif speed >= 1:
                return "Poor"
            else:
                return "Very Poor"
        
        return {
            "download_quality": assess_download(download_mbps),
            "upload_quality": assess_upload(upload_mbps),
            "suitable_for": self._get_suitable_activities(download_mbps, upload_mbps)
        }
    
    def _get_suitable_activities(self, download_mbps: float, upload_mbps: float) -> list:
        """
        Determine what activities the connection speed is suitable for.
        
        Args:
            download_mbps: Download speed in Mbps
            upload_mbps: Upload speed in Mbps
            
        Returns:
            List of suitable activities
        """
        activities = []
        
        if download_mbps >= 3:
            activities.append("Web browsing")
        if download_mbps >= 5:
            activities.append("SD video streaming")
        if download_mbps >= 10:
            activities.append("HD video streaming")
        if download_mbps >= 25:
            activities.append("4K video streaming")
        if download_mbps >= 50:
            activities.append("Online gaming")
        if download_mbps >= 100 and upload_mbps >= 10:
            activities.append("Video conferencing")
        if download_mbps >= 100 and upload_mbps >= 50:
            activities.append("Large file uploads")
        
        return activities if activities else ["Limited connectivity"]


def run_speed_test(timeout: int = 30) -> Dict:
    """
    Convenience function to run a speed test.
    
    Args:
        timeout: Timeout in seconds for speed test
        
    Returns:
        Dict containing speed test results
    """
    speed_test = SpeedTest(timeout=timeout)
    return speed_test.run()
