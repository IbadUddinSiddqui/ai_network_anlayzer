"""
API client for backend communication.
"""
import httpx
import os
import streamlit as st
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIClient:
    """Client for communicating with the backend API."""
    
    def __init__(self, base_url: str = None, access_token: str = None):
        """
        Initialize API client.
        
        Args:
            base_url: Backend API URL
            access_token: JWT access token
        """
        # Try Streamlit secrets first, then environment variables
        try:
            default_url = st.secrets.get("BACKEND_API_URL") or os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        except:
            default_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        
        self.base_url = base_url or default_url
        self.access_token = access_token
        self.headers = {}
        
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
    
    def set_token(self, token: str):
        """Set authentication token."""
        self.access_token = token
        self.headers['Authorization'] = f'Bearer {token}'
    
    async def run_test(
        self, 
        target_hosts: List[str], 
        dns_servers: List[str],
        run_ping: bool = True,
        run_jitter: bool = True,
        run_packet_loss: bool = True,
        run_speed: bool = True,
        run_dns: bool = True
    ) -> Dict:
        """Initiate a network test with selected test types."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/api/v1/run-test',
                json={
                    'target_hosts': target_hosts,
                    'dns_servers': dns_servers,
                    'run_ping': run_ping,
                    'run_jitter': run_jitter,
                    'run_packet_loss': run_packet_loss,
                    'run_speed': run_speed,
                    'run_dns': run_dns
                },
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_results(self, test_id: str) -> Dict:
        """Get test results."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/api/v1/get-results/{test_id}',
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def apply_optimization(self, recommendation_id: str, action_taken: str, notes: str = None) -> Dict:
        """Record optimization action."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/api/v1/apply-optimization',
                json={
                    'recommendation_id': recommendation_id,
                    'action_taken': action_taken,
                    'notes': notes
                },
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def submit_feedback(self, test_id: str, rating: int, comment: str = None) -> Dict:
        """Submit feedback."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/api/v1/feedback',
                json={
                    'test_id': test_id,
                    'rating': rating,
                    'comment': comment
                },
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
