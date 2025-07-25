import streamlit as st
import json
import os
import re
import pandas as pd
import requests
import base64
import random


from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from total_screened_page import total_screened_page
from generate_fake_data import generate_fake_data_page
from certificate_verifier import certificate_verifier_page

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
def load_css_and_fonts():
    """
    Loads custom CSS from style.css and ensures Font Awesome is loaded.
    Also includes custom CSS to hide specific Streamlit elements and
    add styling for login/register pages.
    """
    st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)
    
    # Load the external style.css file
    try:
        current_dir = os.path.dirname(__file__)
        css_file_path = os.path.join(current_dir, "style.css")
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Error: 'style.css' not found. Please ensure it's in the same directory as app.py.")
    except Exception as e:
        st.error(f"An error occurred while loading style.css: {e}")

    # Custom CSS to hide Streamlit toolbar buttons and style login/register
    st.markdown(
        """
        <style>
        /* Hide the 'Deploy' button */
        div[data-testid="stToolbarActionButton"] {
            display: none !important;
        }
        /* Hide the three dots menu button in the header */
        button[data-testid="stBaseButton-header"] {
            display: none !important;
        }

        /* General body styling for login/register pages */
        .login-page-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh; /* Adjust as needed */
            background: linear-gradient(135deg, #f0f2f5 0%, #e0e5ec 100%);
            padding: 20px;
        }
        html[data-theme="dark"] .login-page-container {
            background: linear-gradient(135deg, #2c2c44 0%, #3a3a50 100%);
        }

        .login-card {
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            padding: 40px;
            width: 100%;
            max-width: 450px;
            text-align: center;
            animation: fadeIn 0.8s ease-out;
        }
        html[data-theme="dark"] .login-card {
            background-color: #3b3b55;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .login-card h2 {
            color: #333333;
            margin-bottom: 30px;
            font-size: 2em;
            font-weight: 700;
        }
        html[data-theme="dark"] .login-card h2 {
            color: #e0e0e0;
        }

        .login-card label {
            font-weight: 600;
            color: #555555;
            margin-bottom: 8px;
            display: block;
            text-align: left;
        }
        html[data-theme="dark"] .login-card label {
            color: #b0b0b0;
        }

        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #cccccc;
            padding: 12px 15px;
            width: 100%;
            margin-bottom: 15px;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        .stTextInput > div > div > input:focus {
            border-color: #00cec9;
            box-shadow: 0 0 0 3px rgba(0, 206, 201, 0.2);
            outline: none;
        }
        html[data-theme="dark"] .stTextInput > div > div > input {
            background-color: #4a4a60;
            border-color: #555570;
            color: #e0e0e0;
        }
        html[data-theme="dark"] .stTextInput > div > div > input:focus {
            border-color: #6fa8f7;
            box-shadow: 0 0 0 3px rgba(111, 168, 247, 0.2);
        }

        .stButton > button {
            background-color: #00cec9;
            color: white;
            padding: 12px 25px;
            border-radius: 8px;
            border: none;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            width: 100%;
            margin-top: 20px;
            box-shadow: 0 4px 10px rgba(0, 206, 201, 0.2);
        }

        .stButton > button:hover {
            background-color: #00b3a8;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 206, 201, 0.3);
        }
        html[data-theme="dark"] .stButton > button {
            background-color: #6fa8f7;
            box-shadow: 0 4px 10px rgba(111, 168, 247, 0.2);
        }
        html[data-theme="dark"] .stButton > button:hover {
            background-color: #5a94e0;
            box-shadow: 0 6px 15px rgba(111, 168, 247, 0.3);
        }

        .stRadio > label {
            font-weight: 600;
            color: #333333;
            margin-bottom: 15px;
            display: block;
            text-align: center;
        }
        html[data-theme="dark"] .stRadio > label {
            color: #e0e0e0;
        }
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 25px;
        }
        .stRadio > div > label > div {
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .stRadio > div > label > div:hover {
            background-color: #f0f0f0;
            border-color: #00cec9;
        }
        .stRadio > div > label[data-baseweb="radio"] > div[aria-checked="true"] {
            background-color: #00cec9 !important;
            color: white !important;
            border-color: #00cec9 !important;
            box-shadow: 0 2px 8px rgba(0, 206, 201, 0.2);
        }
        html[data-theme="dark"] .stRadio > div > label > div {
            background-color: #4a4a60;
            border-color: #555570;
            color: #e0e0e0;
        }
        html[data-theme="dark"] .stRadio > div > label > div:hover {
            background-color: #5a5a70;
            border-color: #6fa8f7;
        }
        html[data-theme="dark"] .stRadio > div > label[data-baseweb="radio"] > div[aria-checked="true"] {
            background-color: #6fa8f7 !important;
            color: white !important;
            border-color: #6fa8f7 !important;
            box-shadow: 0 2px 8px rgba(111, 168, 247, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def set_body_class():
    """
    Sets a class on the body element to force light mode styling.
    This function is kept for consistency but the main CSS is now inline.
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
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True) # Close login-card

def login_section():
    """Handles user login and public registration."""
    st.markdown('<div class="login-page-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    if "active_login_tab_selection" not in st.session_state:
        st.session_state.active_login_tab_selection = "Login"

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
                        st.session_state.current_page = "Resume Screener"
                        st.rerun()
    elif tab_selection == "Register":
        # This will now be handled by the register_section which also has the card
        st.markdown('</div>', unsafe_allow_html=True) # Close login-card for the radio part
        st.markdown('</div>', unsafe_allow_html=True) # Close login-page-container for the radio part
        register_section() # Call register section which now includes its own card
        return # Exit to prevent double rendering of the container/card

    st.markdown('</div>', unsafe_allow_html=True) # Close login-card
    st.markdown('</div>', unsafe_allow_html=True) # Close login-page-container


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
        st.session_state.current_page = "Login / Register" # Redirect to public login page
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
    # Initialize sidebar state
    if "sidebar_expanded" not in st.session_state:
        st.session_state.sidebar_expanded = True # Default to expanded

    st.set_page_config(
        page_title="ScreenerPro Candidate Portal",
        layout="wide",
        initial_sidebar_state="expanded" if st.session_state.sidebar_expanded else "collapsed"
    )

    st.session_state.theme = "light"
    st._config.set_option("theme.base", "light")
    st.info("To expand or collapse the navigation sidebar, simply click the >> or << arrow icon located in the top-left corner of the main content area.") 

    # Initialize session state variables if they don't exist
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
    if "current_page" not in st.session_state:
        # Changed default page for unauthenticated users from "Login / Register" to "About Us"
        st.session_state.current_page = "About Us" # Default for unauthenticated

    load_css_and_fonts()
    set_body_class()

    # --- Sidebar Toggle (icon with text, triggering a hidden button for state sync) ---
    col1, col2 = st.columns([1, 10])
    with col1:
        # Create a hidden button that will actually trigger the Streamlit rerun and state change
        # This button's click event will be triggered by the visible HTML element.
        # Its label is used for targeting via aria-label.
        

        # Visible toggle element (icon + text) with JavaScript to click the hidden button
        
        

        st.markdown(
            f"""
            <div style="cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 1.1rem; font-weight: 600; color: #00cec9; user-select: none; padding: 5px 0;"
                 onclick="document.querySelector('button[aria-label*=\"Internal_Toggle_Sidebar_Button\"]').click();">
                
                
            </div>
            """,
            unsafe_allow_html=True
        )

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

        st.sidebar.title("🧠 ScreenerPro")
        st.sidebar.write("---")

    # --- Main Content Area Logic based on Authentication ---
    if not st.session_state.authenticated:
        # If not authenticated, display public navigation and content
        with st.sidebar:
            st.markdown("### Navigate")
            current_sidebar_options = [
                "Login / Register",
                "Verify Certificate",
                "About Us",
                "Feedback Form",
            ]
            default_sidebar_index = current_sidebar_options.index(st.session_state.current_page) if st.session_state.current_page in current_sidebar_options else 0

            selected_tab = st.sidebar.radio(
                "Select Page",
                current_sidebar_options,
                index=default_sidebar_index,
                key="public_nav_radio"
            )
            st.session_state.current_page = selected_tab

        if st.session_state.current_page == "Login / Register":
            login_section() # Call login_section only when this tab is selected
        elif st.session_state.current_page == "Verify Certificate":
            st.markdown('<h2 class="overview-dashboard-header">Certificate Verifier</h2>', unsafe_allow_html=True)
            certificate_verifier_page()
        elif st.session_state.current_page == "About Us":
            st.markdown('<h2 class="overview-dashboard-header">About Us</h2>', unsafe_allow_html=True)
            about_us_page()
        elif st.session_state.current_page == "Feedback Form":
            st.markdown('<h2 class="overview-dashboard-header">Feedback & Help</h2>', unsafe_allow_html=True)
            feedback_and_help_page()
        else: # Default public home if no specific page is selected or initial load
            st.title("Welcome to ScreenerPro - Public Access")
            st.info("Please login or register to access the full HR dashboard features.")
            st.write("---")
            st.subheader("What is ScreenerPro?")
            st.write("ScreenerPro is an AI-powered platform designed to streamline your HR processes, from resume screening to candidate management.")

    else:
        # If authenticated, display authenticated navigation and content
        with st.sidebar:
            st.markdown("### Navigate")
            current_sidebar_options = [
                "Resume Screener",
                "Top Leaderboard",
                "Verify Certificate",
                "Total Resumes Screened",
                "About Us",
                "Feedback Form",
                "Logout"
            ]
            default_sidebar_index = current_sidebar_options.index(st.session_state.current_page) if st.session_state.current_page in current_sidebar_options else 0

            selected_tab = st.sidebar.radio(
                "Select Page",
                current_sidebar_options,
                index=default_sidebar_index,
                key="main_nav_radio" # Unique key for authenticated sidebar radio
            )
            st.session_state.current_page = selected_tab

            st.sidebar.markdown("---")
            st.sidebar.success(f"Logged in as: **{st.session_state.username}**")
            if st.session_state.get('user_company'):
                st.sidebar.info(f"Company: **{st.session_state.user_company}**")

        if st.session_state.current_page == "Resume Screener":
            st.markdown('<h2 class="overview-dashboard-header">Resume Screener</h2>', unsafe_allow_html=True)
            resume_screener_page()
        elif st.session_state.current_page == "Top Leaderboard":
            st.markdown('<h2 class="overview-dashboard-header">Top Leaderboard</h2>', unsafe_allow_html=True)
            leaderboard_page()
        elif st.session_state.current_page == "Verify Certificate":
            st.markdown('<h2 class="overview-dashboard-header">Certificate Verifier</h2>', unsafe_allow_html=True)
            certificate_verifier_page()
        elif st.session_state.current_page == "Total Resumes Screened":
            st.markdown('<h2 class="overview-dashboard-header">Total Resumes Screened</h2>', unsafe_allow_html=True)
            total_screened_page()
        elif st.session_state.current_page == "About Us":
            st.markdown('<h2 class="overview-dashboard-header">About Us</h2>', unsafe_allow_html=True)
            about_us_page()
        elif st.session_state.current_page == "Feedback Form":
            st.markdown('<h2 class="overview-dashboard-header">Feedback & Help</h2>', unsafe_allow_html=True)
            feedback_and_help_page()
        elif st.session_state.current_page == "Logout":
            logout_page()


if __name__ == "__main__":
    main()
