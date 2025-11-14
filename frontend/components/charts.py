"""
Chart components for visualizations.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List


def render_ping_chart(ping_results: List[Dict]):
    """Render ping latency chart."""
    if not ping_results:
        st.info("No ping data available")
        return
    
    hosts = [r['host'] for r in ping_results]
    avg_latencies = [r['avg_ms'] for r in ping_results]
    
    fig = go.Figure(data=[
        go.Bar(x=hosts, y=avg_latencies, marker_color='lightblue')
    ])
    
    fig.update_layout(
        title="Ping Latency by Host",
        xaxis_title="Host",
        yaxis_title="Latency (ms)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_speed_gauge(download_mbps: float, upload_mbps: float):
    """Render speed gauges."""
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=download_mbps,
            title={'text': "Download Speed (Mbps)"},
            gauge={'axis': {'range': [None, 200]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 25], 'color': "lightgray"},
                       {'range': [25, 100], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=upload_mbps,
            title={'text': "Upload Speed (Mbps)"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkgreen"},
                   'steps': [
                       {'range': [0, 10], 'color': "lightgray"},
                       {'range': [10, 50], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}}
        ))
        st.plotly_chart(fig, use_container_width=True)


def render_packet_loss_indicator(loss_percentage: float):
    """Render packet loss indicator."""
    color = "green" if loss_percentage < 1 else "orange" if loss_percentage < 5 else "red"
    
    st.metric(
        label="Packet Loss",
        value=f"{loss_percentage}%",
        delta=f"{'Good' if loss_percentage < 1 else 'Poor'}"
    )


def render_dns_comparison(dns_results: List[Dict]):
    """Render DNS comparison chart."""
    if not dns_results:
        st.info("No DNS data available")
        return
    
    servers = [r['dns_server'] for r in dns_results]
    avg_times = [r['avg_resolution_ms'] for r in dns_results]
    
    fig = go.Figure(data=[
        go.Bar(x=servers, y=avg_times, marker_color='lightgreen')
    ])
    
    fig.update_layout(
        title="DNS Resolution Time Comparison",
        xaxis_title="DNS Server",
        yaxis_title="Resolution Time (ms)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
