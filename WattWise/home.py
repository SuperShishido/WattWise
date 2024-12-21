import streamlit as st
import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timedelta
from utils import switch_page
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_user_name(db, user_id):
    try:
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get('username', 'User')
    except Exception as e:
        st.error(f"Error retrieving user data: {str(e)}")
    return 'User'

def app():
    if 'user' not in st.session_state:
        st.error("You need to login to view your dashboard")
        return
    
    # Initialize Firebase
    db = firestore.client()
    user_id = st.session_state['user']
    username = st.session_state.get('username') or get_user_name(db, user_id)

    # Curr time for greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = 'Good Morning'
    elif 12 <= current_hour < 17:
        greeting = 'Good Afternoon'
    else:
        greeting = 'Good Evening'

    # Welcome message
    st.markdown(f"""
                <h1 style='text-align: center;'>{greeting}, {username}! 👋</h1>
                <p style='text-align: center;'>Let's make energy-saving decisions today.</p>
                """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("Add a new device to your energy tracking list.")
        if st.button("➕ Add Device", use_container_width=True):
            switch_page('device')
    with col2:
        st.caption("Explore energy-saving trends and insights.")
        if st.button("📉 View Analytics", use_container_width=True):
            switch_page('trending')
    with col3:
        st.caption("Manage your account and profile details.")
        if st.button("🔒 Account", use_container_width=True):
            switch_page('account')