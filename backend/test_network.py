"""
Quick test to verify network tests are working
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.network.test_runner import NetworkTestRunner
import json

async def main():
    print("=" * 60)
    print("Testing Network Test Runner")
    print("=" * 60)
    
    runner = NetworkTestRunner()
    
    print("\n🚀 Starting network tests...")
    print("Target hosts: 8.8.8.8, 1.1.1.1")
    print("DNS servers: 8.8.8.8, 1.1.1.1")
    
    results = await runner.run_all_tests(
        target_hosts=["8.8.8.8", "1.1.1.1"],
        dns_servers=["8.8.8.8", "1.1.1.1"],
        packet_count=10
    )
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    
    print(f"\n✅ Status: {results['status']}")
    print(f"✅ Test ID: {results['test_id']}")
    
    print(f"\n📊 Ping Results: {len(results.get('ping_results', []))} hosts")
    for ping in results.get('ping_results', []):
        print(f"  - {ping['host']}: {ping['avg_ms']}ms (received {ping['packets_received']}/{ping['packets_sent']})")
    
    print(f"\n📊 Jitter Results:")
    jitter = results.get('jitter_results', {})
    if jitter:
        print(f"  - Avg: {jitter.get('avg_jitter_ms', 0)}ms")
        print(f"  - Max: {jitter.get('max_jitter_ms', 0)}ms")
    else:
        print("  - No jitter data")
    
    print(f"\n📊 Packet Loss Results:")
    packet_loss = results.get('packet_loss_results', {})
    if packet_loss:
        print(f"  - Loss: {packet_loss.get('loss_percentage', 0)}%")
        print(f"  - Sent: {packet_loss.get('packets_sent', 0)}")
        print(f"  - Received: {packet_loss.get('packets_received', 0)}")
    else:
        print("  - No packet loss data")
    
    print(f"\n📊 Speed Test Results:")
    speed = results.get('speed_results', {})
    if speed:
        print(f"  - Download: {speed.get('download_mbps', 0)} Mbps")
        print(f"  - Upload: {speed.get('upload_mbps', 0)} Mbps")
        print(f"  - Ping: {speed.get('ping_ms', 0)}ms")
        print(f"  - Server: {speed.get('server_location', 'Unknown')}")
    else:
        print("  - No speed test data")
    
    print(f"\n📊 DNS Results: {len(results.get('dns_results', []))} servers")
    for dns in results.get('dns_results', []):
        print(f"  - {dns['dns_server']}: {dns['avg_resolution_ms']}ms")
    
    print("\n" + "=" * 60)
    print("Full JSON output:")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
