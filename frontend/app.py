"""
Main Streamlit application with enhanced UI.
"""
import streamlit as st
import asyncio
import time
from utils.session import init_session, logout
from utils.api_client import APIClient
from components.auth import render_auth
from components.enhanced_charts import (
    render_ookla_speedometer,
    render_animated_progress,
    render_continuous_loader,
    render_modern_ping_chart,
    render_packet_loss_gauge,
    render_dns_comparison_modern,
    render_jitter_analysis
)
from components.realtime_speedometer import (
    render_live_testing_display,
    animate_speed_test
)

# Helper function to check if results are ready
def check_results_ready(results):
    """
    Check if test results are ready to display.
    Returns: (ready: bool, has_data: bool, has_ai: bool, message: str)
    """
    if not results:
        return False, False, False, "No results received"
    
    test_data = results.get('test_results', {})
    
    # Check for ANY test data - handle both dict and object formats
    has_ping = False
    has_speed = False
    has_packet_loss = False
    has_dns = False
    has_jitter = False
    
    # Check ping results
    ping_results = test_data.get('ping_results') if isinstance(test_data, dict) else getattr(test_data, 'ping_results', None)
    if ping_results and len(ping_results) > 0:
        has_ping = True
    
    # Check speed results
    speed_results = test_data.get('speed_results') if isinstance(test_data, dict) else getattr(test_data, 'speed_results', None)
    if speed_results and isinstance(speed_results, dict):
        if speed_results.get('download_mbps') is not None or speed_results.get('upload_mbps') is not None:
            has_speed = True
    
    # Check packet loss results
    packet_loss_results = test_data.get('packet_loss_results') if isinstance(test_data, dict) else getattr(test_data, 'packet_loss_results', None)
    if packet_loss_results and isinstance(packet_loss_results, dict):
        if packet_loss_results.get('packets_sent') is not None:
            has_packet_loss = True
    
    # Check DNS results
    dns_results = test_data.get('dns_results') if isinstance(test_data, dict) else getattr(test_data, 'dns_results', None)
    if dns_results and len(dns_results) > 0:
        has_dns = True
    
    # Check jitter results
    jitter_results = test_data.get('jitter_results') if isinstance(test_data, dict) else getattr(test_data, 'jitter_results', None)
    if jitter_results and isinstance(jitter_results, dict):
        if jitter_results.get('avg_jitter_ms') is not None:
            has_jitter = True
    
    has_data = has_ping or has_speed or has_packet_loss or has_dns or has_jitter
    
    # Check for AI recommendations
    ai_recs = results.get('ai_recommendations', [])
    has_ai = ai_recs and len(ai_recs) > 0
    
    # Ready if we have data, regardless of AI status
    ready = has_data
    
    # Build status message
    if ready:
        data_types = []
        if has_ping: data_types.append("ping")
        if has_speed: data_types.append("speed")
        if has_packet_loss: data_types.append("packet_loss")
        if has_dns: data_types.append("dns")
        if has_jitter: data_types.append("jitter")
        message = f"Results ready: {', '.join(data_types)}"
    else:
        message = "No test data available yet"
    
    return ready, has_data, has_ai, message

# Page config
st.set_page_config(
    page_title="AI Network Analyzer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for PROFESSIONAL DARK theme
st.markdown("""
    <style>
    /* Professional 3-color palette */
    :root {
        --jet-black: #0a0e27;
        --dark-navy: #1a1f3a;
        --modern-white: #ffffff;
        --accent-blue: #4a9eff;
        --text-gray: #a0a0a0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Professional dark background */
    .stApp {
        background: #0a0e27;
    }
    
    /* All text white */
    .stApp, .stApp p, .stApp span, .stApp div {
        color: #ffffff !important;
    }
    
    /* Header styling */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 20px 0;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #ffffff !important;
    }
    
    /* Button styling - Professional */
    .stButton>button {
        background: #4a9eff !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #3a8eef !important;
        transform: translateY(-1px);
    }
    
    /* Checkbox styling - Professional */
    .stCheckbox {
        background: #1a1f3a;
        padding: 10px;
        border-radius: 8px;
    }
    
    .stCheckbox label {
        color: #ffffff !important;
    }
    
    /* Input styling - Professional */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #4a9eff;
        background: #1a1f3a !important;
        color: #ffffff !important;
    }
    
    .stTextInput label {
        color: #ffffff !important;
    }
    
    /* Tab styling - Professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #0a0e27;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1a1f3a !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: #a0a0a0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4a9eff !important;
        color: white !important;
    }
    
    /* Metric styling - Professional */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #4a9eff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
    }
    
    /* Expander styling - Professional */
    .streamlit-expanderHeader {
        background: #1a1f3a !important;
        border-radius: 8px;
        font-weight: 600;
        color: #ffffff !important;
    }
    
    /* Success/Error/Warning boxes - Professional */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 15px;
        background: #1a1f3a !important;
    }
    
    /* Sidebar - Professional */
    [data-testid="stSidebar"] {
        background: #1a1f3a !important;
    }
    
    /* Select box - Professional */
    .stSelectbox label, .stSlider label {
        color: #ffffff !important;
    }
    
    /* Text area - Professional */
    .stTextArea textarea {
        background: #1a1f3a !important;
        color: #ffffff !important;
        border: 1px solid #4a9eff;
        border-radius: 8px;
    }
    
    .stTextArea label {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session
init_session()

# Main app logic
if not st.session_state.authenticated:
    render_auth()
else:
    # Professional header
    st.markdown(f"""
        <div style='background: #1a1f3a; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #4a9eff;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 32px;'>🌐 AI Network Analyzer</h1>
                    <p style='color: #a0a0a0; margin: 5px 0 0 0; font-size: 14px;'>Welcome, {st.session_state.user_email}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("### User Menu")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        
        # Add refresh option if there's a current test
        if 'current_test_id' in st.session_state:
            st.divider()
            st.markdown("### 🔄 Test Results")
            st.caption(f"Test ID: {st.session_state.current_test_id[:8]}...")
            if st.button("Refresh Results", use_container_width=True):
                try:
                    results = asyncio.run(api_client.get_results(st.session_state.current_test_id))
                    st.session_state.test_results = results
                    st.success("✅ Refreshed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
    
    # Create API client
    api_client = APIClient(access_token=st.session_state.access_token)
    
    # Professional test section header
    st.markdown("""
        <div style='text-align: center; padding: 20px; background: #1a1f3a; border-radius: 8px; margin: 15px 0; border-top: 3px solid #4a9eff;'>
            <h1 style='margin: 0; color: white; font-size: 28px;'>
                🌐 Network Performance Test
            </h1>
            <p style='color: #a0a0a0; font-size: 14px; margin-top: 8px;'>Select tests and analyze your network in real-time</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Test Selection with modern cards
    st.markdown("<h2 style='text-align: center; margin: 30px 0 20px 0;'>📋 Select Tests to Run</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
            <div style='background: #1a1f3a; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; border: 1px solid #4a9eff;'>
                <div style='font-size: 28px;'>🏓</div>
                <div style='color: white; font-weight: 600; font-size: 14px;'>Ping</div>
            </div>
        """, unsafe_allow_html=True)
        run_ping = st.checkbox("Enable Ping", value=True, help="Measure latency to target hosts", label_visibility="collapsed", key="ping_check")
    
    with col2:
        st.markdown("""
            <div style='background: #1a1f3a; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; border: 1px solid #4a9eff;'>
                <div style='font-size: 28px;'>📊</div>
                <div style='color: white; font-weight: 600; font-size: 14px;'>Jitter</div>
            </div>
        """, unsafe_allow_html=True)
        run_jitter = st.checkbox("Enable Jitter", value=True, help="Measure latency variation", label_visibility="collapsed", key="jitter_check")
    
    with col3:
        st.markdown("""
            <div style='background: #1a1f3a; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; border: 1px solid #4a9eff;'>
                <div style='font-size: 28px;'>📉</div>
                <div style='color: white; font-weight: 600; font-size: 14px;'>Packet Loss</div>
            </div>
        """, unsafe_allow_html=True)
        run_packet_loss = st.checkbox("Enable Packet Loss", value=True, help="Test packet delivery reliability", label_visibility="collapsed", key="loss_check")
    
    with col4:
        st.markdown("""
            <div style='background: #1a1f3a; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; border: 1px solid #4a9eff;'>
                <div style='font-size: 28px;'>⚡</div>
                <div style='color: white; font-weight: 600; font-size: 14px;'>Speed</div>
            </div>
        """, unsafe_allow_html=True)
        run_speed = st.checkbox("Enable Speed", value=True, help="Test download/upload speeds", label_visibility="collapsed", key="speed_check")
    
    with col5:
        st.markdown("""
            <div style='background: #1a1f3a; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; border: 1px solid #4a9eff;'>
                <div style='font-size: 28px;'>🌐</div>
                <div style='color: white; font-weight: 600; font-size: 14px;'>DNS</div>
            </div>
        """, unsafe_allow_html=True)
        run_dns = st.checkbox("Enable DNS", value=True, help="Test DNS resolution performance", label_visibility="collapsed", key="dns_check")
    
    # Quick selection buttons
    col_a, col_b, col_c = st.columns([1, 1, 4])
    with col_a:
        if st.button("✅ Select All"):
            st.session_state.select_all = True
            st.rerun()
    with col_b:
        if st.button("❌ Clear All"):
            st.session_state.clear_all = True
            st.rerun()
    
    # Apply quick selections
    if st.session_state.get('select_all'):
        run_ping = run_jitter = run_packet_loss = run_speed = run_dns = True
        st.session_state.select_all = False
    if st.session_state.get('clear_all'):
        run_ping = run_jitter = run_packet_loss = run_speed = run_dns = False
        st.session_state.clear_all = False
    
    st.divider()
    
    # Configuration
    st.subheader("⚙️ Test Configuration")
    col1, col2 = st.columns(2)
    with col1:
        target_hosts = st.text_input(
            "Target Hosts (comma-separated)",
            value="8.8.8.8,1.1.1.1",
            help="IP addresses or hostnames to test"
        )
    with col2:
        dns_servers = st.text_input(
            "DNS Servers (comma-separated)",
            value="8.8.8.8,1.1.1.1,208.67.222.222",
            help="DNS servers to test resolution speed"
        )
    
    # Validate at least one test is selected
    if not any([run_ping, run_jitter, run_packet_loss, run_speed, run_dns]):
        st.warning("⚠️ Please select at least one test to run")
    
    # Test button
    start_test = st.button("🚀 Start Network Test", type="primary", disabled=not any([run_ping, run_jitter, run_packet_loss, run_speed, run_dns]))
    
    if start_test:
        with st.spinner("Running selected network tests..."):
            try:
                # Parse inputs
                hosts = [h.strip() for h in target_hosts.split(',')]
                dns = [d.strip() for d in dns_servers.split(',')]
                
                # Run test with selected options
                result = asyncio.run(api_client.run_test(
                    hosts, 
                    dns,
                    run_ping=run_ping,
                    run_jitter=run_jitter,
                    run_packet_loss=run_packet_loss,
                    run_speed=run_speed,
                    run_dns=run_dns
                ))
                test_id = result['test_id']
                
                st.success(f"✅ Test initiated! Test ID: {test_id}")
                st.session_state.current_test_id = test_id
                
                # Show live testing display with animated speedometer
                if run_speed:
                    # Real-time speedometer animation
                    speedometer_placeholder, download_stat, upload_stat, ping_stat, status_placeholder = render_live_testing_display()
                    
                    # Animate speed test for 30 seconds
                    animate_speed_test(speedometer_placeholder, download_stat, upload_stat, ping_stat, status_placeholder, duration=30)
                    
                    # After animation, poll for actual results
                    progress_container = st.empty()
                    max_attempts = 40  # 2 more minutes after animation
                    
                    for i in range(max_attempts):
                        time.sleep(3)
                        
                        try:
                            results = asyncio.run(api_client.get_results(test_id))
                            ready, has_data, has_ai, message = check_results_ready(results)
                            
                            if ready and has_data:
                                st.session_state.test_results = results
                                with progress_container.container():
                                    st.success("✅ Test completed! Displaying results...")
                                time.sleep(1)
                                st.rerun()
                                break
                        except Exception as poll_error:
                            if i % 10 == 0:
                                print(f"[Speed test poll {i+1}] Error: {str(poll_error)}")
                            continue
                    
                    # If timed out
                    if 'test_results' not in st.session_state:
                        with progress_container.container():
                            st.warning("⏳ Results are taking longer than expected. Use the refresh button to check.")
                
                else:
                    # Wait indefinitely until results are complete with continuous loader
                    loader_container = st.empty()
                    
                    # Dynamic status messages based on test phase
                    status_messages = {
                        0: "🚀 Initializing network tests...",
                        1: "🏓 Running ping tests...",
                        2: "� Measupring jitter...",
                        3: "📉 Testing packet loss...",
                        4: "⚡ Running speed test (this may take 30-60s)...",
                        5: "🌐 Testing DNS resolution...",
                        6: "🤖 Analyzing results with AI...",
                        7: "💡 Generating recommendations...",
                        8: "✨ Finalizing report..."
                    }
                    
                    # Poll continuously until results are ready
                    max_attempts = 100  # 5 minutes max (100 * 3 seconds)
                    
                    for i in range(max_attempts):  # Wait up to 5 minutes
                        # Determine current phase based on time elapsed
                        phase = min(i // 5, 8)
                        status_msg = status_messages.get(phase, "⏳ Processing...")
                        
                        # Show continuous loader
                        with loader_container.container():
                            render_continuous_loader(status_msg)
                        
                        time.sleep(3)
                        
                        try:
                            results = asyncio.run(api_client.get_results(test_id))
                            
                            # Use helper function to check if results are ready
                            ready, has_data, has_ai, message = check_results_ready(results)
                            
                            # Log status for debugging
                            if i % 5 == 0:  # Log every 5 attempts (15 seconds)
                                print(f"[Poll {i+1}] Status: {message}, has_data={has_data}, has_ai={has_ai}")
                            
                            # Display results as soon as we have test data
                            if ready and has_data:
                                st.session_state.test_results = results
                                
                                # Show completion message with loader
                                test_status = results.get('status', 'completed')
                                with loader_container.container():
                                    if test_status == 'completed':
                                        render_continuous_loader("✅ Test completed successfully! Loading results...", show_spinner=False)
                                    elif test_status == 'partial':
                                        render_continuous_loader("⚠️ Test partially completed! Loading results...", show_spinner=False)
                                    else:
                                        render_continuous_loader("✅ Test data available! Loading results...", show_spinner=False)
                                
                                # Show AI status if recommendations are missing
                                if not has_ai:
                                    st.info("💡 AI recommendations are still being generated. They will appear when ready.")
                                
                                time.sleep(1)
                                st.rerun()
                                break
                            
                            # Check if test failed completely
                            test_status = results.get('status', 'running')
                            if test_status == 'failed' and not has_data:
                                st.session_state.test_results = results
                                with loader_container.container():
                                    render_continuous_loader("❌ Test failed!", show_spinner=False)
                                time.sleep(1)
                                st.rerun()
                                break
                                        
                        except Exception as poll_error:
                            # Show error but continue polling
                            error_str = str(poll_error)
                            print(f"[Poll {i+1}] Error: {error_str}")
                            
                            # Stop polling for fatal errors
                            if "404" in error_str or "403" in error_str:
                                with loader_container.container():
                                    render_continuous_loader(f"❌ Cannot access test results", show_spinner=False)
                                    st.error(f"Error: {error_str}")
                                break
                            
                            # Continue polling for transient errors
                            if i % 10 == 0:
                                with loader_container.container():
                                    render_continuous_loader(f"⏳ Checking for results... (attempt {i+1}/100)")
                                    st.caption(f"Temporary error: {error_str}")
                            continue
                
                # If timed out after 5 minutes
                if 'test_results' not in st.session_state:
                    st.error("❌ Test timed out after 5 minutes.")
                    st.info("💡 The test may still be running. Use the sidebar 'Refresh Results' button to check later.")
                
            except Exception as e:
                st.error(f"Test failed: {str(e)}")
    
    # Results Section
    if 'test_results' in st.session_state:
        st.divider()
        
        # Header with Fetch Results button
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.header("📊 Test Results")
        with col_header2:
            if 'current_test_id' in st.session_state:
                if st.button("🔄 Fetch Latest", use_container_width=True, key="fetch_latest_results"):
                    with st.spinner("Fetching..."):
                        try:
                            results = asyncio.run(api_client.get_results(st.session_state.current_test_id))
                            st.session_state.test_results = results
                            st.success("✅ Updated!")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {str(e)}")
        
        results = st.session_state.test_results
        
        # Debug: Show what we received
        # st.write("DEBUG - Full response:", results)
        
        test_data = results.get('test_results', {})
        
        # Check if test is still running - check both locations for status
        test_status = test_data.get('status') or results.get('status')
        
        if test_status == 'running':
            st.info("⏳ Test is still running. Results will appear when complete.")
        else:
            # Display overall test status
            overall_status = test_data.get('status', 'unknown')
            status_colors = {
                'completed': '#4caf50',
                'partial': '#ff9800',
                'failed': '#f44336'
            }
            status_icons = {
                'completed': '✅',
                'partial': '⚠️',
                'failed': '❌'
            }
            status_messages = {
                'completed': 'All tests completed successfully',
                'partial': 'Some tests completed with issues',
                'failed': 'Tests failed'
            }
            
            status_color = status_colors.get(overall_status, '#9e9e9e')
            status_icon = status_icons.get(overall_status, '❓')
            status_message = status_messages.get(overall_status, 'Unknown status')
            
            st.markdown(f"""
                <div style='background: #1a1f3a; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid {status_color};'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <div style='font-size: 32px;'>{status_icon}</div>
                        <div>
                            <div style='color: white; font-size: 18px; font-weight: 600;'>{status_message}</div>
                            <div style='color: #a0a0a0; font-size: 14px; margin-top: 5px;'>Test Status: {overall_status.title()}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display individual test status if available
            if 'test_status' in test_data and test_data['test_status']:
                st.markdown("### 📋 Individual Test Status")
                
                status_icons_map = {
                    'success': '✅',
                    'failed': '❌',
                    'skipped': '⏭️'
                }
                
                status_colors_map = {
                    'success': '#4caf50',
                    'failed': '#f44336',
                    'skipped': '#9e9e9e'
                }
                
                cols = st.columns(5)
                test_types = ['ping', 'jitter', 'packet_loss', 'speed', 'dns']
                test_names = ['Ping', 'Jitter', 'Packet Loss', 'Speed', 'DNS']
                
                for col, test_type, test_name in zip(cols, test_types, test_names):
                    status = test_data['test_status'].get(test_type, 'skipped')
                    icon = status_icons_map.get(status, '❓')
                    color = status_colors_map.get(status, '#9e9e9e')
                    
                    with col:
                        st.markdown(f"""
                            <div style='background: #1a1f3a; border-radius: 8px; padding: 15px; text-align: center; border-top: 3px solid {color};'>
                                <div style='font-size: 32px; margin-bottom: 8px;'>{icon}</div>
                                <div style='color: white; font-weight: 600; font-size: 14px;'>{test_name}</div>
                                <div style='color: {color}; font-size: 12px; margin-top: 5px;'>{status.title()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Determine which tabs to show based on available results
            available_tabs = []
            tab_names = []
            
            # Check ping results
            ping_results = test_data.get('ping_results', [])
            if ping_results and len(ping_results) > 0:
                available_tabs.append('ping')
                tab_names.append("🏓 Latency")
            
            # Check speed results - be more lenient
            speed_results = test_data.get('speed_results')
            if speed_results and isinstance(speed_results, dict):
                if speed_results.get('download_mbps') is not None or speed_results.get('upload_mbps') is not None:
                    available_tabs.append('speed')
                    tab_names.append("⚡ Speed")
            
            # Check packet loss results - be more lenient
            packet_loss_results = test_data.get('packet_loss_results')
            if packet_loss_results and isinstance(packet_loss_results, dict):
                if packet_loss_results.get('packets_sent') is not None or packet_loss_results.get('loss_percentage') is not None:
                    available_tabs.append('packet_loss')
                    tab_names.append("📉 Packet Loss")
            
            # Check DNS results
            dns_results = test_data.get('dns_results', [])
            if dns_results and len(dns_results) > 0:
                available_tabs.append('dns')
                tab_names.append("🌐 DNS")
            
            # Check jitter results - be more lenient
            jitter_results = test_data.get('jitter_results')
            if jitter_results and isinstance(jitter_results, dict):
                if jitter_results.get('avg_jitter_ms') is not None or jitter_results.get('max_jitter_ms') is not None:
                    available_tabs.append('jitter')
                    tab_names.append("📊 Jitter")
            
            if not available_tabs:
                st.warning("⚠️ No test results available to display.")
                st.info("💡 This could mean: tests are still running, tests failed, or no tests were selected.")
                
                # Show what we actually have
                st.write("**Available data:**")
                st.write(f"- Ping results: {len(ping_results)} hosts")
                st.write(f"- Speed results: {'Yes' if speed_results else 'No'}")
                st.write(f"- Packet loss results: {'Yes' if packet_loss_results else 'No'}")
                st.write(f"- DNS results: {len(dns_results)} servers")
                st.write(f"- Jitter results: {'Yes' if jitter_results else 'No'}")
            else:
                # Create tabs dynamically based on available results
                tabs = st.tabs(tab_names)
                
                for i, tab_type in enumerate(available_tabs):
                    with tabs[i]:
                        if tab_type == 'ping':
                            render_modern_ping_chart(test_data['ping_results'])
                        
                        elif tab_type == 'speed':
                            speed = test_data['speed_results']
                            render_ookla_speedometer(
                                speed['download_mbps'],
                                speed['upload_mbps'],
                                speed.get('ping_ms', 0)
                            )
                            st.markdown(f"""
                                <div style='text-align: center; padding: 15px; background: blue; border-radius: 10px; margin-top: 20px;'>
                                    <div style='color:  #0a0e27; font-size: 16px;'>Test Server</div>
                                    <div style='color: #667eea; font-size: 20px; font-weight: 600;'>{speed.get('server_location', 'Unknown')}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        elif tab_type == 'packet_loss':
                            loss = test_data['packet_loss_results']
                            render_packet_loss_gauge(
                                loss['loss_percentage'],
                                loss.get('packets_sent', 0),
                                loss.get('packets_received', 0)
                            )
                        
                        elif tab_type == 'dns':
                            render_dns_comparison_modern(test_data['dns_results'])
                        
                        elif tab_type == 'jitter':
                            jitter = test_data['jitter_results']
                            render_jitter_analysis(jitter)
            
            # Display errors if any
            if 'errors' in test_data and test_data['errors']:
                errors_dict = test_data['errors']
                # Check if there are any non-None errors
                has_errors = any(v for v in errors_dict.values() if v)
                
                if has_errors:
                    st.divider()
                    with st.expander("⚠️ View Test Errors and Issues", expanded=False):
                        st.markdown("""
                            <div style='background: #1a1f3a; border-radius: 8px; padding: 15px; margin-bottom: 15px;'>
                                <div style='color: #ff9800; font-weight: 600; margin-bottom: 10px;'>
                                    ⚠️ Some tests encountered errors
                                </div>
                                <div style='color: #a0a0a0; font-size: 14px;'>
                                    The following tests had issues. Review the details below:
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        for test_type, error in errors_dict.items():
                            if error:
                                test_names_map = {
                                    'ping': '🏓 Ping Test',
                                    'jitter': '📊 Jitter Test',
                                    'packet_loss': '📉 Packet Loss Test',
                                    'speed': '⚡ Speed Test',
                                    'dns': '🌐 DNS Test'
                                }
                                test_name = test_names_map.get(test_type, test_type.title())
                                
                                st.markdown(f"""
                                    <div style='background: #2a1f1f; border-left: 4px solid #f44336; border-radius: 4px; padding: 15px; margin: 10px 0;'>
                                        <div style='color: #f44336; font-weight: 600; margin-bottom: 8px;'>
                                            {test_name}
                                        </div>
                                        <div style='color: #ffffff; font-size: 14px; font-family: monospace;'>
                                            {error}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Add troubleshooting tips
                        st.markdown("""
                            <div style='background: #1a1f3a; border-radius: 8px; padding: 15px; margin-top: 20px;'>
                                <div style='color: #4a9eff; font-weight: 600; margin-bottom: 10px;'>
                                    💡 Troubleshooting Tips
                                </div>
                                <ul style='color: #a0a0a0; font-size: 14px; margin-left: 20px;'>
                                    <li>Check your internet connection</li>
                                    <li>Verify firewall settings aren't blocking tests</li>
                                    <li>Some tests may require administrator privileges</li>
                                    <li>Try running the test again</li>
                                    <li>If issues persist, contact support</li>
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Show warning for partial results
            if test_data.get('status') == 'partial':
                st.warning("⚠️ **Partial Results:** Some tests completed successfully while others failed. Review the test status above for details.")
        
        # AI Recommendations with modern cards
        st.divider()
        st.markdown("""
            <div style='text-align: center; margin: 40px 0 30px 0;'>
                <h2 style='color: white;'>
                    🤖 AI-Powered Recommendations
                </h2>
                <p style='color: #a0a0a0; font-size: 14px;'>Intelligent insights from our multi-agent AI system</p>
            </div>
        """, unsafe_allow_html=True)
        
        recommendations = results.get('ai_recommendations', [])
        
        if recommendations:
            for idx, rec in enumerate(recommendations):
                severity_colors = {
                    'critical': {'bg': '#f44336', 'icon': '🔴', 'label': 'CRITICAL'},
                    'warning': {'bg': '#ff9800', 'icon': '🟡', 'label': 'WARNING'},
                    'info': {'bg': '#4caf50', 'icon': '🟢', 'label': 'INFO'}
                }
                
                severity_info = severity_colors.get(rec['severity'], {'bg': '#9e9e9e', 'icon': '⚪', 'label': 'UNKNOWN'})
                confidence_pct = int(rec['confidence_score'] * 100)
                
                st.markdown(f"""
                    <div style='background: #1a1f3a; border-radius: 8px; padding: 20px; margin: 15px 0; border-left: 4px solid {severity_info['bg']};'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                            <div>
                                <span style='background: {severity_info['bg']}; color: white; padding: 5px 15px; border-radius: 4px; font-size: 12px; font-weight: 600;'>
                                    {severity_info['icon']} {severity_info['label']}
                                </span>
                                <span style='background: #4a9eff; color: white; padding: 5px 15px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 10px;'>
                                    {confidence_pct}% Confidence
                                </span>
                            </div>
                            <div style='color: #a0a0a0; font-size: 12px;'>Agent: {rec['agent_type']}</div>
                        </div>
                        <div style='color: #ffffff; font-size: 14px; line-height: 1.6;'>
                            {rec['recommendation_text']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("✅ Apply", key=f"apply_{rec['id']}", use_container_width=True):
                        try:
                            asyncio.run(api_client.apply_optimization(
                                rec['id'],
                                "Applied from dashboard"
                            ))
                            st.success("✅ Optimization recorded!")
                        except Exception as e:
                            st.error(f"❌ Failed: {str(e)}")
        else:
            # Check if AI is still processing
            test_status = results.get('status', 'completed')
            if test_status in ['completed', 'partial']:
                # Test is done but no AI recommendations yet
                st.markdown("""
                    <div style='text-align: center; padding: 40px; background: #1a1f3a; border-radius: 8px; border: 2px dashed #4a9eff;'>
                        <div style='font-size: 48px; margin-bottom: 10px;'>🤖</div>
                        <div style='color: #ffffff; font-size: 16px;'>AI Analysis in Progress...</div>
                        <div style='color: #a0a0a0; font-size: 14px; margin-top: 5px;'>Recommendations will appear here shortly</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Add refresh button
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("🔄 Refresh AI", use_container_width=True, key="refresh_ai_recs"):
                        with st.spinner("Fetching AI recommendations..."):
                            try:
                                updated_results = asyncio.run(api_client.get_results(st.session_state.current_test_id))
                                st.session_state.test_results = updated_results
                                st.success("✅ Updated!")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to refresh: {str(e)}")
            else:
                # Test failed or still running
                st.markdown("""
                    <div style='text-align: center; padding: 40px; background: #1a1f3a; border-radius: 8px;'>
                        <div style='font-size: 48px; margin-bottom: 10px;'>🤖</div>
                        <div style='color: #ffffff; font-size: 16px;'>No recommendations available</div>
                        <div style='color: #a0a0a0; font-size: 14px; margin-top: 5px;'>AI analysis will appear here after test completion</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Feedback section with modern design
        st.divider()
        st.markdown("""
            <div style='text-align: center; margin: 40px 0 30px 0;'>
                <h2 style='color: white;'>
                    💬 Share Your Feedback
                </h2>
                <p style='color: #a0a0a0; font-size: 14px;'>Help us improve your experience</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
                <div style='background: #1a1f3a; border-radius: 8px; padding: 30px;'>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("<div style='margin-bottom: 10px; font-weight: 600; color: #4a9eff;'>Rate Your Experience</div>", unsafe_allow_html=True)
                rating = st.select_slider(
                    "Rating",
                    options=[1, 2, 3, 4, 5],
                    value=5,
                    format_func=lambda x: "⭐" * x,
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("<div style='margin-bottom: 10px; font-weight: 600; color: #4a9eff;'>Additional Comments (Optional)</div>", unsafe_allow_html=True)
                comment = st.text_area(
                    "Comment",
                    placeholder="Tell us what you think...",
                    label_visibility="collapsed",
                    height=100
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📤 Submit Feedback", use_container_width=True):
                    try:
                        asyncio.run(api_client.submit_feedback(
                            test_data['test_id'],
                            rating,
                            comment if comment else None
                        ))
                        st.success("🎉 Thank you for your feedback!")
                    except Exception as e:
                        st.error(f"❌ Failed to submit feedback: {str(e)}")
