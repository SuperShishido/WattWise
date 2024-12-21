import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta
import bcrypt
import re
from utils import switch_page

# Initialize Firebase if not initialized already
def initialize_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("correct.json") # Add path to Firebase service account key
        firebase_admin.initialize_app(cred)
    return firestore.client()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search("[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search("[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search("[0-9]", password):
        return False, "Password must contain numbers"
    return True, "Password is strong"

def validate_email(email):
    """Validate email address"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    return False

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed_password):
    """Verify password using bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def check_session_validity():
    """Check if user is logged in"""
    if 'login-time' not in st.session_state:
        return False
    
    session_duration = timedelta(minutes=10)
    current_time = datetime.now()
    login_time = st.session_state['login-time']

    return current_time - login_time <= session_duration

def app():
    # Initialize Firebase
    db = initialize_firebase()

    if 'user' in st.session_state:
        if not check_session_validity():
            # Clear session if expired
            for key in ['user', 'username', 'login-time']:
                # if key in st.session_state:
                #     del st.session_state[key]
                st.session_state.pop(key, None)
            st.warning('Session expired. Please login again.')
            switch_page('login')

    if 'user' not in st.session_state:
        st.title("Welcome to :green[Watt Wise]")

        # Create tabs for Login and Signup
        tab1, tab2 = st.tabs(['Login', 'Signup'])

        # Login tab
        with tab1:
            st.header("Login")
            email = st.text_input('Email Address', key='login_email')
            password = st.text_input('Password', type='password', key='login_password')

            if st.button('Login', key='login_button'):
                if not email or not password:
                    st.error('Please fill in all fields')
                else:
                    try:
                        # Get user from Firebase auth
                        user = auth.get_user_by_email(email)

                        # Get user data from Firestore
                        user_doc = db.collection('users').document(user.uid).get()

                        if user_doc.exists:
                            user_data = user_doc.to_dict()
                            stored_hash = user_data.get('password_hash')

                            if verify_password(password, stored_hash):
                                st.success('Login successful')
                                st.session_state['user'] = user.uid
                                st.session_state['username'] = user_data.get('username')
                                st.session_state['login-time'] = datetime.now()

                                # Update last login time in Firestore
                                db.collection('users').document(user.uid).update({
                                    'last_login': datetime.now()
                                })
                                switch_page('home')
                            else:
                                st.error('Invalid password')
                        else:
                            st.error('User not found. Please sign up')
                    except auth.UserNotFoundError:
                        st.error('User not found. Please check your email or sign up.')
                    except Exception as e:
                        st.error(f'An error occurred: {str(e)}')

        # Signup tab
        with tab2:
            st.header("Sign up")
            new_email = st.text_input('Email Address', key='signup_email')
            new_password = st.text_input('Password', type='password', key='signup_password')
            username = st.text_input('Create a Username')

            if st.button('Sign up', key='signup_button'):
                if not all([new_email, new_password, username]):
                    st.error('Please fill in all fields')
                elif not validate_email(new_email):
                    st.error('Please enter a valid email address')
                else:
                    # Validate password strength
                    is_valid, msg = validate_password(new_password)
                    if not is_valid:
                        st.error(msg)
                        return
                    
                    try:
                        # Create user in Firebase auth
                        user = auth.create_user(
                            email=new_email,
                            password=new_password,
                            display_name=username
                        )

                        # Hash password and store additional user data in Firestore
                        password_hash = hash_password(new_password)
                        user_data = {
                            'username': username,
                            'email': new_email,
                            'password_hash': password_hash,
                            'created_at': datetime.now(),
                            'last_login': datetime.now()
                        }

                        db.collection('users').document(user.uid).set(user_data)

                        st.success('Account created successfully')
                        st.balloons()

                    except auth.EmailAlreadyExistsError:
                        st.error('Email address already in use')
                    except Exception as e:
                        st.error(f'An error occurred: {str(e)}')