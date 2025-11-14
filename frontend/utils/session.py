"""
Session management for Streamlit.
"""
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def init_session():
    """Initialize session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None


def get_supabase_client() -> Client:
    """Get Supabase client."""
    # Try to get from Streamlit secrets first, then environment variables
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv('SUPABASE_URL')
        key = st.secrets.get("SUPABASE_KEY") or os.getenv('SUPABASE_KEY')
    except:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        st.error("⚠️ Supabase credentials not found! Please configure .env file or Streamlit secrets.")
        st.stop()
    
    return create_client(url, key)


def login(email: str, password: str) -> bool:
    """
    Login user.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.session_state.authenticated = True
            st.session_state.user_id = response.user.id
            st.session_state.access_token = response.session.access_token
            st.session_state.user_email = response.user.email
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False


def signup(email: str, password: str) -> bool:
    """
    Sign up new user.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": None
            }
        })
        
        if response.user:
            st.success("Account created! Please check your email to confirm, or disable email confirmation in Supabase settings for testing.")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False


def logout():
    """Logout user."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.access_token = None
    st.session_state.user_email = None
