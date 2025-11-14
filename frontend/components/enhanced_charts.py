"""
Enhanced chart components with Ookla-style visualizations.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import numpy as np


def render_ookla_speedometer(download_mbps: float, upload_mbps: float, ping_ms: float):
    """Render Ookla-style speedometer with animated gauge - DARK THEME."""
    
    # Dark theme speed display
    st.markdown("""
        <style>
        .speed-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%);
            border-radius: 20px;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        .speed-value {
            font-size: 72px;
            font-weight: bold;
            color: white;
            margin: 0;
        }
        .speed-label {
            font-size: 24px;
            color: rgba(255,255,255,0.9);
            margin-top: -10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create circular speedometer
    max_speed = max(200, download_mbps * 1.2)
    
    fig = go.Figure()
    
    # Add gauge for download speed
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=download_mbps,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Download Speed</b>", 'font': {'size': 18, 'color': '#ffffff'}},
        number={'suffix': " Mbps", 'font': {'size': 36, 'color': '#4a9eff'}},
        delta={'reference': 50, 'increasing': {'color': "#4caf50"}},
        gauge={
            'axis': {'range': [None, max_speed], 'tickwidth': 2, 'tickcolor': "#4a9eff", 'tickfont': {'color': '#ffffff'}},
            'bar': {'color': "#4a9eff", 'thickness': 0.75},
            'bgcolor': "#1a1f3a",
            'borderwidth': 3,
            'bordercolor': "#4a9eff",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(244, 67, 54, 0.2)'},
                {'range': [25, 50], 'color': 'rgba(255, 152, 0, 0.2)'},
                {'range': [50, 100], 'color': 'rgba(76, 175, 80, 0.2)'},
                {'range': [100, max_speed], 'color': 'rgba(102, 126, 234, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#00ff00", 'width': 4},
                'thickness': 0.75,
                'value': max_speed * 0.8
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff", 'family': "Arial"}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: #1a1f3a; border-radius: 8px; border: 2px solid #4a9eff;'>
                <div style='font-size: 28px; font-weight: bold; color: white;'>{download_mbps:.1f}</div>
                <div style='font-size: 12px; color: #a0a0a0; margin-top: 5px;'>DOWNLOAD Mbps</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: #1a1f3a; border-radius: 8px; border: 2px solid #4a9eff;'>
                <div style='font-size: 28px; font-weight: bold; color: white;'>{upload_mbps:.1f}</div>
                <div style='font-size: 12px; color: #a0a0a0; margin-top: 5px;'>UPLOAD Mbps</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: #1a1f3a; border-radius: 8px; border: 2px solid #4a9eff;'>
                <div style='font-size: 28px; font-weight: bold; color: white;'>{ping_ms:.0f}</div>
                <div style='font-size: 12px; color: #a0a0a0; margin-top: 5px;'>PING ms</div>
            </div>
        """, unsafe_allow_html=True)


def render_animated_progress(progress: int, status_text: str):
    """Render animated progress indicator."""
    st.markdown(f"""
        <style>
        .progress-container {{
            width: 100%;
            background: #1a1f3a;
            border-radius: 25px;
            padding: 3px;
            margin: 20px 0;
            border: 2px solid #4a9eff;
        }}
        .progress-bar {{
            width: {progress}%;
            height: 30px;
            background: linear-gradient(90deg, #4a9eff 0%, #667eea 100%);
            border-radius: 25px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .status-text {{
            text-align: center;
            margin-top: 10px;
            font-size: 18px;
            color: #4a9eff;
            font-weight: 500;
        }}
        </style>
        <div class="progress-container">
            <div class="progress-bar">{progress}%</div>
        </div>
        <div class="status-text">{status_text}</div>
    """, unsafe_allow_html=True)


def render_continuous_loader(status_text: str, show_spinner: bool = True):
    """
    Render a continuous loader that keeps running until tests complete.
    This loader doesn't show percentage, just an animated spinner and status.
    """
    spinner_html = """
        <div class="spinner"></div>
    """ if show_spinner else ""
    
    st.markdown(f"""
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .loader-container {{
            background: #1a1f3a;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 2px solid #4a9eff;
            text-align: center;
        }}
        
        .spinner {{
            border: 4px solid #1a1f3a;
            border-top: 4px solid #4a9eff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px auto;
        }}
        
        .loader-status {{
            font-size: 18px;
            color: #4a9eff;
            font-weight: 500;
            animation: pulse 2s ease-in-out infinite;
        }}
        
        .loader-subtitle {{
            font-size: 14px;
            color: #a0a0a0;
            margin-top: 10px;
        }}
        </style>
        <div class="loader-container">
            {spinner_html}
            <div class="loader-status">{status_text}</div>
            <div class="loader-subtitle">Please wait while we complete all tests...</div>
        </div>
    """, unsafe_allow_html=True)


def render_modern_ping_chart(ping_results: List[Dict]):
    """Render modern ping latency chart with gradients."""
    if not ping_results:
        st.info("No ping data available")
        return
    
    hosts = [r['host'] for r in ping_results]
    avg_latencies = [r['avg_ms'] for r in ping_results]
    min_latencies = [r.get('min_ms', 0) for r in ping_results]
    max_latencies = [r.get('max_ms', 0) for r in ping_results]
    
    fig = go.Figure()
    
    # Add bars with gradient colors
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    for i, (host, avg, min_val, max_val) in enumerate(zip(hosts, avg_latencies, min_latencies, max_latencies)):
        fig.add_trace(go.Bar(
            x=[host],
            y=[avg],
            name=host,
            marker_color=colors[i % len(colors)],
            error_y=dict(
                type='data',
                symmetric=False,
                array=[max_val - avg],
                arrayminus=[avg - min_val],
                color='rgba(0,0,0,0.3)'
            ),
            hovertemplate=f'<b>{host}</b><br>Avg: {avg:.1f}ms<br>Min: {min_val:.1f}ms<br>Max: {max_val:.1f}ms<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': "<b>Ping Latency Analysis</b>",
            'font': {'size': 20, 'color': '#ffffff'}
        },
        xaxis_title="Host",
        yaxis_title="Latency (ms)",
        height=350,
        showlegend=False,
        plot_bgcolor='#1a1f3a',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial", 'color': '#ffffff', 'size': 12},
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=False, color='#ffffff')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(74,158,255,0.1)', color='#ffffff')
    
    st.plotly_chart(fig, use_container_width=True)


def render_packet_loss_gauge(loss_percentage: float, packets_sent: int, packets_received: int):
    """Render packet loss as a gauge with status indicator."""
    
    # Determine status
    if loss_percentage < 1:
        status = "Excellent"
        color = "#4caf50"
    elif loss_percentage < 2.5:
        status = "Good"
        color = "#8bc34a"
    elif loss_percentage < 5:
        status = "Fair"
        color = "#ff9800"
    else:
        status = "Poor"
        color = "#f44336"
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=loss_percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Packet Loss</b>", 'font': {'size': 24, 'color': '#ffffff'}},
        number={'suffix': "%", 'font': {'size': 48, 'color': color}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 2, 'tickfont': {'color': '#ffffff'}},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "#1a1f3a",
            'borderwidth': 3,
            'bordercolor': color,
            'steps': [
                {'range': [0, 1], 'color': 'rgba(76, 175, 80, 0.2)'},
                {'range': [1, 2.5], 'color': 'rgba(205, 220, 57, 0.2)'},
                {'range': [2.5, 5], 'color': 'rgba(255, 152, 0, 0.2)'},
                {'range': [5, 10], 'color': 'rgba(244, 67, 54, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#ff0000", 'width': 4},
                'thickness': 0.75,
                'value': 5
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': '#ffffff', 'size': 12}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Status card
    st.markdown(f"""
        <div style='text-align: center; padding: 15px; background: {color}; border-radius: 10px; color: white;'>
            <div style='font-size: 24px; font-weight: bold;'>{status}</div>
            <div style='font-size: 14px; margin-top: 5px;'>{packets_received}/{packets_sent} packets received</div>
        </div>
    """, unsafe_allow_html=True)


def render_dns_comparison_modern(dns_results: List[Dict]):
    """Render modern DNS comparison with ranking."""
    if not dns_results:
        st.info("No DNS data available")
        return
    
    # Sort by speed (fastest first)
    sorted_results = sorted(dns_results, key=lambda x: x['avg_resolution_ms'])
    
    servers = [r['dns_server'] for r in sorted_results]
    avg_times = [r['avg_resolution_ms'] for r in sorted_results]
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    colors = ['#4caf50', '#8bc34a', '#cddc39', '#ff9800', '#f44336']
    
    fig.add_trace(go.Bar(
        y=servers,
        x=avg_times,
        orientation='h',
        marker=dict(
            color=colors[:len(servers)],
            line=dict(color='rgba(0,0,0,0.3)', width=2)
        ),
        text=[f"{t:.1f}ms" for t in avg_times],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Resolution Time: %{x:.1f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "<b>DNS Performance Ranking</b>",
            'font': {'size': 24, 'color': '#ffffff'}
        },
        xaxis_title="Resolution Time (ms)",
        yaxis_title="DNS Server",
        height=max(300, len(servers) * 80),
        showlegend=False,
        plot_bgcolor='#1a1f3a',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial", 'color': '#ffffff'}
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(74,158,255,0.1)', color='#ffffff')
    fig.update_yaxes(showgrid=False, color='#ffffff')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Winner card
    fastest = sorted_results[0]
    st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); border-radius: 15px; color: white; margin-top: 20px;'>
            <div style='font-size: 18px; margin-bottom: 10px;'>🏆 Fastest DNS Server</div>
            <div style='font-size: 32px; font-weight: bold;'>{fastest['dns_server']}</div>
            <div style='font-size: 20px; margin-top: 5px;'>{fastest['avg_resolution_ms']:.1f}ms</div>
        </div>
    """, unsafe_allow_html=True)


def render_jitter_analysis(jitter_results: Dict):
    """Render jitter analysis with line chart."""
    avg_jitter = jitter_results.get('avg_jitter_ms', 0)
    max_jitter = jitter_results.get('max_jitter_ms', 0)
    measurements = jitter_results.get('measurements', [])
    
    # Status determination
    if avg_jitter < 20:
        status = "Excellent"
        color = "#4caf50"
    elif avg_jitter < 30:
        status = "Good"
        color = "#8bc34a"
    elif avg_jitter < 50:
        status = "Fair"
        color = "#ff9800"
    else:
        status = "Poor"
        color = "#f44336"
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: #1a1f3a; border-radius: 8px; border: 2px solid {color};'>
                <div style='font-size: 28px; font-weight: bold; color: white;'>{avg_jitter:.1f}</div>
                <div style='font-size: 12px; color: #a0a0a0; margin-top: 5px;'>AVG JITTER ms</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: #1a1f3a; border-radius: 8px; border: 2px solid #4a9eff;'>
                <div style='font-size: 28px; font-weight: bold; color: white;'>{max_jitter:.1f}</div>
                <div style='font-size: 12px; color: #a0a0a0; margin-top: 5px;'>MAX JITTER ms</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: {color}; border-radius: 8px;'>
                <div style='font-size: 20px; font-weight: bold; color: white;'>{status}</div>
                <div style='font-size: 12px; color: white; margin-top: 5px;'>STATUS</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Line chart if measurements available
    if measurements:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=measurements,
            mode='lines+markers',
            name='Jitter',
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}'
        ))
        
        fig.update_layout(
            title="<b>Jitter Over Time</b>",
            xaxis_title="Measurement",
            yaxis_title="Jitter (ms)",
            height=250,
            plot_bgcolor='#1a1f3a',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': "Arial", 'color': '#ffffff', 'size': 12}
        )
        
        fig.update_xaxes(showgrid=False, color='#ffffff')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(74,158,255,0.1)', color='#ffffff')
        
        st.plotly_chart(fig, use_container_width=True)
