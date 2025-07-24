import streamlit as st
import json
import os
import re
import pandas as pd
import requests
import base64
import random

from pages.certificate_verify import certificate_verifier_page
from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from total_screened_page import total_screened_page
from generate_fake_data import generate_fake_data_page

# --- Firebase Configuration ---
FIREBASE_API_KEY = st.secrets.get('FIREBASE_API_KEY', '')
FIREBASE_PROJECT_ID = st.secrets.get('FIREBASE_PROJECT_ID', '')
APP_ID = st.secrets.get('FIREBASE_APP_ID', 'your-default-app-id')

if not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
    st.error("Firebase API Key or Project ID not found. Please ensure they are configured directly at the top level of your .streamlit/secrets.toml file with correct capitalization (FIREBASE_API_KEY, FIREBASE_PROJECT_ID, FIREBASE_APP_ID).")
    st.stop()

# Firebase Authentication REST API Endpoints
AUTH_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
AUTH_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
AUTH_RESET_PASSWORD_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"

# Firestore REST API Base URL for documents
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data/user_profiles"

# --- CSS Loading and Body Class Functions ---
def load_css(file_name="style.css"):
    """
    Loads a CSS file from the same directory as the app.py.
    Also ensures Font Awesome is loaded for icons.
    """
    try:
        current_dir = os.path.dirname(__file__)
        css_file_path = os.path.join(current_dir, file_name)
        with open(css_file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: '{file_name}' not found. Please ensure it's in the same directory as app.py.")

    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">',
        unsafe_allow_html=True
    )

def set_body_class():
    """
    Sets a class on the body element to force light mode styling.
    """
    body_class = "light-mode"
    js_code = f"""
    <script>
        var body = window.parent.document.querySelector('body');
        if (body) {{
            body.className = '';
            body.classList.add('{body_class}');
            body.setAttribute('data-theme', 'light');
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- Firebase REST API Helper Functions ---

def get_firestore_doc_url(uid):
    """Constructs the Firestore document URL for a given UID."""
    return f"{FIRESTORE_BASE_URL}/{uid}"

def get_user_profile_from_firestore(uid, id_token):
    """Fetches user profile data from Firestore using UID and ID Token."""
    url = get_firestore_doc_url(uid)
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'fields' in data:
            profile = {}
            for key, value_obj in data['fields'].items():
                if 'stringValue' in value_obj:
                    profile[key] = value_obj['stringValue']
                elif 'booleanValue' in value_obj:
                    profile[key] = value_obj['booleanValue']
            return profile
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user profile from Firestore: {e}")
        print(f"Firestore Fetch Error Response: {response.text if 'response' in locals() else 'No response object'}")
        return None

def set_user_profile_in_firestore(uid, id_token, profile_data):
    """Sets/updates user profile data in Firestore."""
    url = get_firestore_doc_url(uid)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    fields = {}
    for key, value in profile_data.items():
        if isinstance(value, str):
            fields[key] = {"stringValue": value}
        elif isinstance(value, bool):
            fields[key] = {"booleanValue": value}
    payload = {"fields": fields}

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error setting user profile in Firestore: {e}")
        print(f"Firestore Set Error Response: {response.text if 'response' in locals() else 'No response object'}")
        return False

# --- Authentication and User Management Functions ---

def is_valid_email(email):
    """Basic validation for email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def register_user_firebase(email, password, company_name):
    """Registers a new user with Firebase Auth and stores profile in Firestore."""
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    try:
        response = requests.post(AUTH_SIGNUP_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        id_token = data['idToken']
        uid = data['localId']

        profile_data = {
            "email": email,
            "company": company_name,
            "status": "active"
        }
        if set_user_profile_in_firestore(uid, id_token, profile_data):
            return {"success": True, "idToken": id_token, "uid": uid, "email": email, "company": company_name, "status": "active"}
        else:
            return {"success": False, "message": "Failed to save user profile to Firestore."}
    except requests.exceptions.RequestException as e:
        error_message = "Registration failed."
        if 'response' in locals():
            error_data = response.json()
            print(f"Firebase Auth Registration Error Response: {error_data}")
            if "error" in error_data and "message" in error_data["error"]:
                error_message = f"Registration failed: {error_data['error']['message']}"
        st.error(error_message)
        return {"success": False, "message": error_message}

def sign_in_user_firebase(email, password):
    """Signs in a user with Firebase Auth and fetches profile from Firestore."""
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    try:
        response = requests.post(AUTH_SIGNIN_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        id_token = data['idToken']
        uid = data['localId']

        user_profile = get_user_profile_from_firestore(uid, id_token)
        if user_profile:
            if user_profile.get("status") == "disabled":
                st.error("❌ Your account has been disabled. Please contact an administrator.")
                return {"success": False, "message": "Account disabled."}
            return {"success": True, "idToken": id_token, "uid": uid, "email": email, "company": user_profile.get("company", "N/A"), "status": user_profile.get("status", "active")}
        else:
            st.warning("User profile not found in Firestore. Please contact support.")
            return {"success": False, "message": "User profile not found."}
    except requests.exceptions.RequestException as e:
        error_message = "Login failed."
        if 'response' in locals():
            error_data = response.json()
            print(f"Firebase Auth Sign-in Error Response: {error_data}")
            if "error" in error_data and "message" in error_data["error"]:
                error_message = f"Login failed: {error_data['error']['message']}"
        st.error(error_message)
        return {"success": False, "message": error_message}

def send_password_reset_email_firebase(email):
    """Sends a password reset email via Firebase Auth REST API."""
    payload = json.dumps({
        "requestType": "PASSWORD_RESET",
        "email": email
    })
    try:
        response = requests.post(AUTH_RESET_PASSWORD_URL, data=payload)
        response.raise_for_status()
        st.success(f"✅ Password reset email sent to {email}. Please check your inbox.")
        return True
    except requests.exceptions.RequestException as e:
        error_message = "Failed to send password reset email."
        if 'response' in locals():
            error_data = response.json()
            print(f"Firebase Auth Reset Password Error Response: {error_data}")
            if "error" in error_data and "message" in error_data["error"]:
                error_message = f"Failed to send password reset email: {error_data['error']['message']}"
        st.error(error_message)
        return False

def register_section():
    """Public self-registration form."""
    st.subheader("📝 Create New Account")
    with st.form("registration_form", clear_on_submit=True):
        new_username = st.text_input("Choose Username (Email address required)", key="new_username_reg_public")
        new_company_name = st.text_input("Company Name", key="new_company_name_reg_public")
        new_password = st.text_input("Choose Password", type="password", key="new_password_reg_public")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password_reg_public")
        register_button = st.form_submit_button("Register New Account")

        if register_button:
            if not new_username or not new_password or not confirm_password or not new_company_name:
                st.error("Please fill in all fields.")
            elif not is_valid_email(new_username):
                st.error("Please enter a valid email address for the username.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                result = register_user_firebase(new_username, new_password, new_company_name)
                if result["success"]:
                    st.success("✅ Registration successful! You are now logged in.")
                    st.session_state.authenticated = True
                    st.session_state.username = result["email"]
                    st.session_state.user_company = result["company"]
                    st.session_state.user_uid = result["uid"]
                    st.session_state.id_token = result["idToken"]
                    st.session_state.current_page = "welcome_dashboard"
                    st.rerun()

def login_section():
    """Handles user login and public registration."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_company" not in st.session_state:
        st.session_state.user_company = None
    if "user_uid" not in st.session_state:
        st.session_state.user_uid = None
    if "id_token" not in st.session_state:
        st.session_state.id_token = None

    if "active_login_tab_selection" not in st.session_state:
        st.session_state.active_login_tab_selection = "Login"

    if st.session_state.authenticated:
        return True

    tab_selection = st.radio(
        "Select an option:",
        ("Login", "Register"),
        key="login_register_radio",
        index=0 if st.session_state.active_login_tab_selection == "Login" else 1
    )

    if tab_selection == "Login":
        st.subheader("🔐 HR Login")
        st.info("If you don't have an account, please go to the 'Register' option first.")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username (Email)", key="username_login")
            password = st.text_input("Password", type="password", key="password_login")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    result = sign_in_user_firebase(username, password)
                    if result["success"]:
                        st.success("✅ Login successful!")
                        st.session_state.authenticated = True
                        st.session_state.username = result["email"]
                        st.session_state.user_company = result["company"]
                        st.session_state.user_uid = result["uid"]
                        st.session_state.id_token = result["idToken"]
                        st.session_state.current_page = "welcome_dashboard"
                        st.rerun()
    elif tab_selection == "Register":
        register_section()

    return st.session_state.authenticated

def logout_page():
    st.title("👋 Logging Out...")
    st.write("You are about to be logged out. Thank you for using ScreenerPro!")
    if st.button("Confirm Logout"):
        st.session_state.authenticated = False
        st.session_state.pop('username', None)
        st.session_state.pop('user_company', None)
        st.session_state.pop('user_uid', None)
        st.session_state.pop('id_token', None)
        st.session_state.pop('current_quote', None)
        st.session_state.active_login_tab_selection = "Login"
        st.rerun()
    st.info("You will be redirected to the login page shortly if you don't confirm.")

# List of quotes for the welcome message
QUOTES = [
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. – Winston Churchill",
    "The best way to predict the future is to create it. – Peter Drucker",
    "Innovation distinguishes between a leader and a follower. – Steve Jobs",
    "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work. – Steve Jobs",
    "The mind is everything. What you think you become. – Buddha",
    "Strive not to be a success, but rather to be of value. – Albert Einstein",
    "The journey of a thousand miles begins with a single step. – Lao Tzu"
]

def display_welcome_dashboard():
    """Displays the welcome message and a random quote."""
    if "current_quote" not in st.session_state:
        st.session_state.current_quote = random.choice(QUOTES)

    st.markdown(
        f"""
        <style>
            @keyframes fadeInScale {{
                from {{ opacity: 0; transform: scale(0.9); }}
                to {{ opacity: 1; transform; scale(1); }}
            }}

            .beautiful-greeting-card {{
                background: linear-gradient(135deg, #f0f2f5 0%, #e0e5ec 100%);
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                text-align: center;
                animation: fadeInScale 0.7s ease-out forwards;
                position: relative;
                overflow: hidden;
            }}

            .beautiful-greeting-card::before {{
                content: '✨';
                position: absolute;
                top: 10px;
                left: 10px;
                font-size: 2em;
                opacity: 0.2;
                pointer-events: none;
            }}
            .beautiful-greeting-card::after {{
                content: '🌟';
                position: absolute;
                bottom: 10px;
                right: 10px;
                font-size: 2em;
                opacity: 0.2;
                pointer-events: none;
            }}

            .beautiful-greeting-title {{
                font-size: 2.2em;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
            }}

            .beautiful-username {{
                color: #3498db;
                font-weight: 800;
            }}

            .beautiful-welcome-text {{
                font-size: 1.15em;
                color: #555555;
                line-height: 1.6;
                margin-top: 15px;
            }}
            .beautiful-quote {{
                font-style: italic;
                color: #666;
                margin-top: 20px;
                font-size: 1.05em;
            }}

            .beautiful-emoji {{
                font-size: 1.6em;
                vertical-align: middle;
                margin: 0 5px;
            }}
            /* Dark mode adjustments for the greeting card */
            html[data-theme="dark"] .beautiful-greeting-card {{
                background: linear-gradient(135deg, #2c2c44 0%, #3a3a50 100%);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
            }}
            html[data-theme="dark"] .beautiful-greeting-title {{
                color: #e0e0e0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}
            html[data-theme="dark"] .beautiful-username {{
                color: #6fa8f7;
            }}
            html[data-theme="dark"] .beautiful-welcome-text {{
                color: #a0a0a0;
            }}
            html[data-theme="dark"] .beautiful-quote {{
                color: #b0b0b0;
            }}
        </style>

        <div class="beautiful-greeting-card">
            <h1 class="beautiful-greeting-title">
                Welcome, <span class="beautiful-username">{st.session_state.username}</span>!
            </h1>
            <p class="beautiful-welcome-text">
                <span class="beautiful-emoji">👋</span> We're absolutely thrilled to have you here!
                Your journey with us officially begins now. <span class="beautiful-emoji">🚀</span>
                Get ready to explore! <span class="beautiful-emoji">🎉</span>
            </p>
            <p class="beautiful-quote">
                "{st.session_state.current_quote}"
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="ScreenerPro Candidate Portal", layout="wide", initial_sidebar_state="expanded")

    st.session_state.theme = "light"
    st._config.set_option("theme.base", "light")

    load_css("style.css")

    set_body_class()

    st.markdown("""
    <style>
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }

    .main .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    header {
        visibility: visible !important;
        height: auto !important;
        display: block !important;
        margin: initial !important;
        padding: initial !important;
        position: initial !important;
        top: initial !important;
    }

    [data-testid="stSidebar"] {
        position: relative !important;
        display: block !important;
        visibility: visible !important;
        width: auto !important;
        height: auto !important;
        top: auto !important;
        left: auto !important;
        z-index: auto !important;
    }

    .st-emotion-cache-1wbqy5l,
    #_link_gzau3_10,
    .st-emotion-cache-h6us5p
    {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Permanent Sidebar Content ---
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        logo_path = "logo.png"

        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                st.markdown(f"""
                <a href="https://screenerpro.streamlit.app/" target="_self">
                    <img src="data:image/png;base64,{encoded_string}" alt="Go to HR Portal" width="215">
                </a>
                """, unsafe_allow_html=True)
            except FileNotFoundError:
                st.warning(f"Logo file not found at: {logo_path}")
            except Exception as e:
                st.error(f"An error occurred while processing the logo: {e}")
                st.info("Please ensure 'logo.png' is a valid PNG image.")
        else:
            st.warning(f"Logo file not found at: {logo_path}")

        st.sidebar.write("---")

    # --- Main Content Area Logic ---
    is_authenticated = login_section()

    if is_authenticated:
        with st.sidebar:
            st.markdown("<p>Navigate</p>", unsafe_allow_html=True)

            if st.button("Resume Screener", key="nav_resume_screen"):
                st.session_state.current_page = "resume_screen"
                st.rerun()
            if st.session_state.current_page == "resume_screen":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_resume_screen"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_resume_screen"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_resume_screen"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_resume_screen"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("Top Leaderboard", key="nav_top_leaderboard"):
                st.session_state.current_page = "top_leaderboard"
                st.rerun()
            if st.session_state.current_page == "top_leaderboard":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_top_leaderboard"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_top_leaderboard"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_top_leaderboard"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_top_leaderboard"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("Verify Certificate", key="nav_certificate_verify"):
                st.session_state.current_page = "certificate_verify"
                st.rerun()
            if st.session_state.current_page == "certificate_verify":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_certificate_verify"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_certificate_verify"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_certificate_verify"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_certificate_verify"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("Total Resumes Screened", key="nav_total_screened"):
                st.session_state.current_page = "total_screened"
                st.rerun()
            if st.session_state.current_page == "total_screened":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_total_screened"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_total_screened"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_total_screened"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_total_screened"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("About Us", key="nav_about_us"):
                st.session_state.current_page = "about_us"
                st.rerun()
            if st.session_state.current_page == "about_us":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_about_us"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_about_us"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_about_us"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_about_us"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("Feedback Form", key="nav_feedback_form"):
                st.session_state.current_page = "feedback_form"
                st.rerun()
            if st.session_state.current_page == "feedback_form":
                st.markdown(f"""
                <style>
                    div[data-testid="stButton-nav_feedback_form"] > button {{
                        background-color: #00cec9 !important;
                        color: white !important;
                        font-weight: 700 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.25) !important;
                        border: none !important;
                    }}
                    div[data-testid="stButton-nav_feedback_form"] > button:hover {{
                        background-color: #00b0a8 !important;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
                    }}
                    div[data-testid="stButton-nav_feedback_form"] > button:active {{
                        background-color: #009a93 !important;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_feedback_form"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            if st.button("Logout", key="nav_logout"):
                st.session_state.current_page = "logout"
                st.rerun()
            st.markdown(f'<style>div[data-testid="stButton-nav_logout"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            st.sidebar.markdown("---")
            st.sidebar.success(f"Logged in as: **{st.session_state.username}**")
            if st.session_state.get('user_company'):
                st.sidebar.info(f"Company: **{st.session_state.user_company}**")

        if st.session_state.current_page == "welcome_dashboard":
            display_welcome_dashboard()
        elif st.session_state.current_page == "resume_screen":
            st.markdown('<h2 class="overview-dashboard-header">Resume Screener</h2>', unsafe_allow_html=True)
            resume_screener_page()
        elif st.session_state.current_page == "top_leaderboard":
            st.markdown('<h2 class="overview-dashboard-header">Top Leaderboard</h2>', unsafe_allow_html=True)
            leaderboard_page()
        elif st.session_state.current_page == "certificate_verify":
            st.markdown('<h2 class="overview-dashboard-header">Certificate Verifier</h2>', unsafe_allow_html=True)
            certificate_verifier_page()
        elif st.session_state.current_page == "total_screened":
            st.markdown('<h2 class="overview-dashboard-header">Total Resumes Screened</h2>', unsafe_allow_html=True)
            total_screened_page()
        elif st.session_state.current_page == "about_us":
            st.markdown('<h2 class="overview-dashboard-header">About Us</h2>', unsafe_allow_html=True)
            about_us_page()
        elif st.session_state.current_page == "feedback_form":
            st.markdown('<h2 class="overview-dashboard-header">Feedback & Help</h2>', unsafe_allow_html=True)
            feedback_and_help_page()
        elif st.session_state.current_page == "logout":
            logout_page()
        elif st.session_state.current_page == "generate_fake_data":
            st.markdown('<h2 class="overview-dashboard-header">Generate Fake Data</h2>', unsafe_allow_html=True)
            generate_fake_data_page()

    else:
        pass

if __name__ == "__main__":
    main()
