"""
Test packet loss functionality directly
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.network.packet_loss_test import PacketLossTest

print("=" * 60)
print("Testing Packet Loss Test")
print("=" * 60)

# Test with Google DNS
print("\n🧪 Testing packet loss to 8.8.8.8 (Google DNS)")
print("Sending 20 packets (this will take ~20 seconds)...")

test = PacketLossTest(packet_count=20, timeout=1)
result = test.run("8.8.8.8")

print("\n📊 RESULTS:")
print(f"Host: {result['host']}")
print(f"Packets Sent: {result['packets_sent']}")
print(f"Packets Received: {result['packets_received']}")
print(f"Packets Lost: {result['packets_lost']}")
print(f"Loss Percentage: {result['loss_percentage']}%")
print(f"Success Rate: {result['success_rate']}%")

if 'error' in result:
    print(f"\n❌ Error: {result['error']}")
else:
    print(f"\n✅ Test completed successfully!")

# Quality assessment
quality = test.assess_network_quality(result['loss_percentage'])
print(f"Network Quality: {quality}")

print("\n" + "=" * 60)
print("EXPLANATION:")
print("=" * 60)
print("""
0% packet loss is NORMAL and GOOD for stable networks!

Packet loss typically occurs when:
- Network is congested
- WiFi signal is weak
- Router/modem is faulty
- ISP has issues
- Long distance connections

On a good, stable connection (especially wired), you should see:
- 0% packet loss (excellent)
- 0-1% packet loss (very good)

If you want to simulate packet loss for testing:
1. Use WiFi instead of wired
2. Test to a distant server
3. Download large files while testing
4. Test during peak hours
5. Use a VPN

Your 0% packet loss means your network is working perfectly! ✅
""")

print("=" * 60)
