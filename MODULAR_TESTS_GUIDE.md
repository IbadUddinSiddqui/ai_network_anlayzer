# 🎯 Modular Network Tests - User Guide

## Overview
The AI Network Analyzer now supports **selective test execution**, allowing users to choose which tests to run based on their needs.

## Available Tests

### 🏓 Ping Test
- **Purpose**: Measure latency to target hosts
- **Duration**: ~5-10 seconds
- **Use Case**: Quick connectivity check
- **Output**: Min/Max/Avg latency, packet statistics

### 📊 Jitter Test
- **Purpose**: Measure latency variation over time
- **Duration**: ~10-15 seconds
- **Use Case**: VoIP/video call quality assessment
- **Output**: Average and max jitter values

### 📉 Packet Loss Test
- **Purpose**: Test packet delivery reliability
- **Duration**: ~10-20 seconds (depends on packet count)
- **Use Case**: Network stability assessment
- **Output**: Loss percentage, packets sent/received

### ⚡ Speed Test
- **Purpose**: Measure download/upload speeds
- **Duration**: ~20-30 seconds
- **Use Case**: Bandwidth verification
- **Output**: Download/upload speeds, server location

### 🌐 DNS Test
- **Purpose**: Test DNS resolution performance
- **Duration**: ~5-10 seconds
- **Use Case**: DNS server comparison
- **Output**: Resolution times for multiple DNS servers

## How to Use

### Frontend (Streamlit)

1. **Select Tests**: Check/uncheck the test types you want to run
2. **Quick Actions**:
   - Click "✅ Select All" to enable all tests
   - Click "❌ Clear All" to disable all tests
3. **Configure**: Set target hosts and DNS servers
4. **Run**: Click "🚀 Start Network Test"

### API Usage

```python
import httpx

# Run only ping and DNS tests
response = httpx.post('http://localhost:8000/api/v1/run-test', json={
    'target_hosts': ['8.8.8.8', '1.1.1.1'],
    'dns_servers': ['8.8.8.8', '1.1.1.1'],
    'run_ping': True,
    'run_jitter': False,
    'run_packet_loss': False,
    'run_speed': False,
    'run_dns': True
})
```

## Common Use Cases

### Quick Check (Fast)
- ✅ Ping
- ❌ Jitter
- ❌ Packet Loss
- ❌ Speed
- ✅ DNS
- **Duration**: ~10-15 seconds

### VoIP/Gaming Assessment (Medium)
- ✅ Ping
- ✅ Jitter
- ✅ Packet Loss
- ❌ Speed
- ✅ DNS
- **Duration**: ~30-40 seconds

### Full Diagnostic (Comprehensive)
- ✅ Ping
- ✅ Jitter
- ✅ Packet Loss
- ✅ Speed
- ✅ DNS
- **Duration**: ~60-90 seconds

### Bandwidth Only (Speed Focus)
- ❌ Ping
- ❌ Jitter
- ❌ Packet Loss
- ✅ Speed
- ❌ DNS
- **Duration**: ~20-30 seconds

## Benefits

1. **Faster Results**: Run only what you need
2. **Cost Efficient**: Reduce API calls and compute time
3. **Flexible**: Customize tests for specific scenarios
4. **Better UX**: Users aren't forced to wait for unnecessary tests

## Technical Details

### Backend Changes
- `TestConfig` model now includes boolean flags for each test type
- `NetworkTestRunner.run_all_tests()` accepts test selection parameters
- Progress calculation adjusts based on enabled tests
- Empty results returned for skipped tests

### Frontend Changes
- Checkbox UI for test selection
- Quick action buttons (Select All / Clear All)
- Dynamic tab creation based on available results
- Disabled button when no tests selected

### Validation
- At least one test must be selected
- Frontend validates before sending request
- Backend validates in Pydantic model

## Future Enhancements

- [ ] Save test presets (e.g., "Quick Check", "Full Diagnostic")
- [ ] Scheduled tests with custom configurations
- [ ] Test history with filter by test types
- [ ] Cost estimation based on selected tests
- [ ] Recommended test combinations based on use case
