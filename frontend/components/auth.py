"""
Authentication components.
"""
import streamlit as st
from utils.session import login, signup


def render_auth():
    """Render login/signup page."""
    st.title("🌐 AI Network Analyzer")
    st.markdown("### Monitor, Analyze, and Optimize Your Network")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        render_login()
    
    with tab2:
        render_signup()


def render_login():
    """Render login form."""
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                if login(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")


def render_signup():
    """Render signup form."""
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if signup(email, password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Signup failed")
