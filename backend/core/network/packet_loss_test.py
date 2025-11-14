"""
Packet loss test module for measuring network reliability.
"""
import logging
from typing import Dict
from ping3 import ping
import time

logger = logging.getLogger(__name__)


class PacketLossTest:
    """
    Measures packet loss percentage using ICMP ping.
    
    Sends a configurable number of packets and tracks how many
    are successfully received to calculate packet loss percentage.
    
    Note: On some systems, this may require administrator/root privileges.
    """
    
    def __init__(self, packet_count: int = 100, timeout: int = 2):
        """
        Initialize packet loss test configuration.
        
        Args:
            packet_count: Number of packets to send (default: 100)
            timeout: Timeout in seconds for each packet (default: 2)
        """
        self.packet_count = packet_count
        self.timeout = timeout
    
    def run(self, host: str) -> Dict:
        """
        Execute packet loss test for a single host.
        
        Args:
            host: Target host IP address or hostname
            
        Returns:
            Dict containing packet loss statistics:
                - host: Target host
                - packets_sent: Number of packets sent
                - packets_received: Number of packets received
                - packets_lost: Number of packets lost
                - loss_percentage: Packet loss percentage
                - success_rate: Success rate percentage
                
        Example:
            >>> packet_test = PacketLossTest(packet_count=100)
            >>> result = packet_test.run("8.8.8.8")
            >>> print(f"Packet loss: {result['loss_percentage']}%")
        """
        logger.info(f"Starting packet loss test for host: {host} ({self.packet_count} packets)")
        
        packets_sent = 0
        packets_received = 0
        
        try:
            for i in range(self.packet_count):
                packets_sent += 1
                
                try:
                    # Send ping packet
                    response = ping(host, timeout=self.timeout, unit='ms')
                    
                    if response is not None:
                        packets_received += 1
                    
                    # Log progress every 20 packets
                    if (i + 1) % 20 == 0:
                        current_loss = ((packets_sent - packets_received) / packets_sent) * 100
                        logger.debug(
                            f"Progress: {i+1}/{self.packet_count} packets sent, "
                            f"current loss: {current_loss:.1f}%"
                        )
                    
                    # Small delay to avoid overwhelming the network
                    time.sleep(0.01)
                    
                except Exception as e:
                    logger.debug(f"Packet {i+1} to {host} failed: {e}")
            
            # Calculate statistics
            packets_lost = packets_sent - packets_received
            loss_percentage = (packets_lost / packets_sent) * 100 if packets_sent > 0 else 0
            success_rate = (packets_received / packets_sent) * 100 if packets_sent > 0 else 0
            
            result = {
                "host": host,
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "packets_lost": packets_lost,
                "loss_percentage": round(loss_percentage, 2),
                "success_rate": round(success_rate, 2)
            }
            
            logger.info(
                f"Packet loss test completed for {host}: "
                f"{packets_received}/{packets_sent} packets received, "
                f"loss: {loss_percentage:.2f}%"
            )
            
            return result
            
        except PermissionError as e:
            logger.error(
                f"Permission denied for packet loss test on {host}. "
                "Administrator/root privileges may be required."
            )
            return {
                "host": host,
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "packets_lost": packets_sent - packets_received,
                "loss_percentage": 100.0,
                "success_rate": 0.0,
                "error": "Permission denied - requires administrator privileges"
            }
        except Exception as e:
            logger.error(f"Packet loss test failed for {host}: {e}")
            return {
                "host": host,
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "packets_lost": packets_sent - packets_received,
                "loss_percentage": 100.0 if packets_sent > 0 else 0.0,
                "success_rate": 0.0,
                "error": str(e)
            }
    
    def assess_network_quality(self, loss_percentage: float) -> str:
        """
        Assess network quality based on packet loss percentage.
        
        Args:
            loss_percentage: Packet loss percentage
            
        Returns:
            String describing network quality
            
        Example:
            >>> test = PacketLossTest()
            >>> quality = test.assess_network_quality(2.5)
            >>> print(quality)  # "Good"
        """
        if loss_percentage == 0:
            return "Excellent"
        elif loss_percentage < 1:
            return "Very Good"
        elif loss_percentage < 3:
            return "Good"
        elif loss_percentage < 5:
            return "Fair"
        elif loss_percentage < 10:
            return "Poor"
        else:
            return "Very Poor"


def test_packet_loss(host: str, packet_count: int = 100, timeout: int = 2) -> Dict:
    """
    Convenience function to test packet loss for a single host.
    
    Args:
        host: Target host IP address or hostname
        packet_count: Number of packets to send
        timeout: Timeout in seconds for each packet
        
    Returns:
        Dict containing packet loss statistics
    """
    packet_test = PacketLossTest(packet_count=packet_count, timeout=timeout)
    return packet_test.run(host)
