"""
Real-time animated speedometer for live testing.
"""
import streamlit as st
import plotly.graph_objects as go
import time
import random


def render_realtime_speedometer(current_speed: float = 0, max_speed: float = 200, test_type: str = "download"):
    """
    Render real-time animated speedometer that updates during testing.
    
    Args:
        current_speed: Current speed value
        max_speed: Maximum speed for gauge
        test_type: Type of test (download/upload/ping)
    """
    
    # Color scheme based on test type
    colors = {
        "download": {"primary": "#667eea", "secondary": "#764ba2"},
        "upload": {"primary": "#f093fb", "secondary": "#f5576c"},
        "ping": {"primary": "#4facfe", "secondary": "#00f2fe"}
    }
    
    color = colors.get(test_type, colors["download"])
    
    # Create animated gauge
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=current_speed,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<b>{test_type.upper()}</b>",
            'font': {'size': 20, 'color': '#ffffff'}
        },
        number={
            'suffix': " Mbps" if test_type != "ping" else " ms",
            'font': {'size': 40, 'color': color["primary"]},
            'valueformat': '.1f'
        },
        delta={
            'reference': max_speed * 0.5,
            'increasing': {'color': "#4caf50"},
            'decreasing': {'color': "#f44336"}
        },
        gauge={
            'axis': {
                'range': [None, max_speed],
                'tickwidth': 3,
                'tickcolor': color["primary"],
                'tickfont': {'color': '#ffffff', 'size': 14}
            },
            'bar': {
                'color': color["primary"],
                'thickness': 0.8
            },
            'bgcolor': "#1e2130",
            'borderwidth': 3,
            'bordercolor': color["primary"],
            'steps': [
                {'range': [0, max_speed * 0.25], 'color': 'rgba(244, 67, 54, 0.2)'},
                {'range': [max_speed * 0.25, max_speed * 0.5], 'color': 'rgba(255, 152, 0, 0.2)'},
                {'range': [max_speed * 0.5, max_speed * 0.75], 'color': 'rgba(76, 175, 80, 0.2)'},
                {'range': [max_speed * 0.75, max_speed], 'color': 'rgba(102, 126, 234, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#00ff00", 'width': 6},
                'thickness': 0.85,
                'value': max_speed * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff", 'family': "Arial, sans-serif"}
    )
    
    return fig


def render_live_testing_display():
    """
    Render live testing display with animated speedometer.
    Shows real-time updates during network testing.
    """
    
    st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%); border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.5); margin: 15px 0;'>
            <h1 style='margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px;'>
                ⚡ TESTING IN PROGRESS
            </h1>
            <p style='color: #b0b3c1; font-size: 14px; margin-top: 8px;'>Analyzing your network performance...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create placeholder for speedometer
    speedometer_placeholder = st.empty()
    
    # Create placeholders for stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        download_stat = st.empty()
    with col2:
        upload_stat = st.empty()
    with col3:
        ping_stat = st.empty()
    
    # Status placeholder
    status_placeholder = st.empty()
    
    return speedometer_placeholder, download_stat, upload_stat, ping_stat, status_placeholder


def animate_speed_test(speedometer_placeholder, download_stat, upload_stat, ping_stat, status_placeholder, duration=30):
    """
    Animate the speedometer during speed test.
    Simulates real-time speed testing with smooth animations.
    
    Args:
        speedometer_placeholder: Streamlit placeholder for speedometer
        download_stat: Placeholder for download stat
        upload_stat: Placeholder for upload stat
        ping_stat: Placeholder for ping stat
        status_placeholder: Placeholder for status message
        duration: Duration of animation in seconds
    """
    
    # Simulate speed test phases
    phases = [
        {"name": "Connecting to server...", "duration": 3, "speed_range": (0, 10)},
        {"name": "Testing download speed...", "duration": 12, "speed_range": (10, 100)},
        {"name": "Testing upload speed...", "duration": 10, "speed_range": (5, 50)},
        {"name": "Measuring latency...", "duration": 5, "speed_range": (0, 5)}
    ]
    
    download_speed = 0
    upload_speed = 0
    ping_ms = 0
    
    for phase in phases:
        phase_steps = int(phase["duration"] * 2)  # 2 updates per second
        
        for step in range(phase_steps):
            # Update status
            with status_placeholder.container():
                st.markdown(f"""
                    <div style='text-align: center; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin: 15px 0;'>
                        <div style='color: white; font-size: 16px; font-weight: 600;'>{phase['name']}</div>
                        <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 3px;'>
                            Step {step + 1} of {phase_steps}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Simulate speed increase
            if "download" in phase["name"]:
                download_speed = min(phase["speed_range"][1], 
                                   download_speed + random.uniform(2, 8))
                current_speed = download_speed
                test_type = "download"
                max_speed = 200
                
            elif "upload" in phase["name"]:
                upload_speed = min(phase["speed_range"][1],
                                 upload_speed + random.uniform(1, 4))
                current_speed = upload_speed
                test_type = "upload"
                max_speed = 100
                
            elif "latency" in phase["name"]:
                ping_ms = random.uniform(10, 50)
                current_speed = ping_ms
                test_type = "ping"
                max_speed = 100
            
            else:
                current_speed = random.uniform(phase["speed_range"][0], phase["speed_range"][1])
                test_type = "download"
                max_speed = 200
            
            # Update speedometer
            with speedometer_placeholder.container():
                fig = render_realtime_speedometer(current_speed, max_speed, test_type)
                st.plotly_chart(fig, use_container_width=True)
            
            # Update stats
            with download_stat.container():
                st.markdown(f"""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px;'>
                        <div style='font-size: 28px; font-weight: bold; color: white;'>{download_speed:.1f}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.9); margin-top: 5px;'>DOWNLOAD Mbps</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with upload_stat.container():
                st.markdown(f"""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px;'>
                        <div style='font-size: 28px; font-weight: bold; color: white;'>{upload_speed:.1f}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.9); margin-top: 5px;'>UPLOAD Mbps</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with ping_stat.container():
                st.markdown(f"""
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px;'>
                        <div style='font-size: 28px; font-weight: bold; color: white;'>{ping_ms:.0f}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.9); margin-top: 5px;'>PING ms</div>
                    </div>
                """, unsafe_allow_html=True)
            
            time.sleep(0.5)  # Update every 0.5 seconds
    
    # Final status
    with status_placeholder.container():
        st.markdown("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); border-radius: 12px; margin: 15px 0;'>
                <div style='color: white; font-size: 18px; font-weight: 600;'>✅ Test Complete!</div>
                <div style='color: rgba(255,255,255,0.9); font-size: 14px; margin-top: 5px;'>
                    Analyzing results with AI...
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    return download_speed, upload_speed, ping_ms
