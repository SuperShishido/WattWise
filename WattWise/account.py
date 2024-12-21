import streamlit as st
import firebase_admin
from firebase_admin import firestore, credentials, auth
from datetime import datetime
import bcrypt
from login import validate_password, verify_password, hash_password, check_session_validity

def app():
    if 'user' not in st.session_state:
        st.session_state['page'] = 'Login'
        st.rerun()
        return
    
    # check session validity
    if not check_session_validity():
        for key in ['user', 'username', 'login-time']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state['page'] = 'login'
        st.rerun()
        return

    # Initialize Firebase
    db = firestore.client()
    user_id = st.session_state['user']

    # Get user data
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()

        # profile header
        st.title("My Profile")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.image("https://via.placeholder.com/150", width=150)

        with col2:
            st.subheader(user_data.get('username', 'Username not set'))
            st.write(f"📧 {user_data.get('email', 'Email not available')}")
            st.write(f"📅 Member since: {user_data.get('created_at', 'Date not available').strftime('%B %d, %Y')}")
            st.write(f"🔒 Last login: {user_data.get('last_login', 'Date not available').strftime('%B %d, %Y %H:%M')}")

        with col3:
            if st.button("🚪 Logout", key='logout_button'):
                for key in ['user', 'username', 'login-time']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state['page'] = 'login'
                st.rerun()

        # Account Statistics
        st.markdown("---")
        st.header("📊 Account Statistics")
        stats_col1, stats_col2 = st.columns(2)

        with stats_col1:
            devices = db.collection("users").document(user_id).collection("devices").stream()
            device_count = sum(1 for _ in devices)
            st.metric("Total devices", device_count)

        with stats_col2:
            st.metric("Energy Saved", "Coming soon")