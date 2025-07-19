import streamlit as st
import json
import os
import re # Import regex for email validation
import pandas as pd # Ensure pandas is imported for DataFrame display
import requests # Import requests for HTTP calls to Firebase REST API
import base64
import random # Import random for quotes

# Import your page functions from separate files (assuming these are separate Python files)
# Make sure these files (e.g., certificate_verify.py, resume_screen.py) are also in your GitHub repo
from pages.certificate_verify import certificate_verifier_page
from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from total_screened_page import total_screened_page
from generate_fake_data import generate_fake_data_page

# --- Firebase Configuration (for deployment via GitHub/Streamlit Cloud) ---
# These values should be stored in your .streamlit/secrets.toml file or as environment variables
# Example .streamlit/secrets.toml:
# [firebase]
# APIKey = "YOUR_FIREBASE_API_KEY"
# PROJECT_ID = "YOUR_FIREBASE_PROJECT_ID"
# APP_ID = "YOUR_APP_ID_FOR_FIRESTORE_PATH" # Use a consistent ID for your app's data in Firestore

# Get Firebase API Key and Project ID from Streamlit Secrets, matching capitalization
FIREBASE_API_KEY = st.secrets.get('firebase', {}).get('APIKey', '')
FIREBASE_PROJECT_ID = st.secrets.get('firebase', {}).get('PROJECT_ID', '')
APP_ID = st.secrets.get('firebase', {}).get('APP_ID', 'your-default-app-id') # Use a default if not provided

# --- DEBUGGING: Display Firebase Secrets (REMOVE IN PRODUCTION) ---
if not st.session_state.get("authenticated", False):
    st.sidebar.markdown("---")
    st.sidebar.warning("DEBUG INFO (REMOVE IN PRODUCTION):")
    st.sidebar.write(f"st.secrets.get('firebase'): `{st.secrets.get('firebase')}`")
    st.sidebar.write(f"API Key (from secrets): `{FIREBASE_API_KEY}`")
    st.sidebar.write(f"Project ID (from secrets): `{FIREBASE_PROJECT_ID}`")
    st.sidebar.write(f"App ID (from secrets): `{APP_ID}`")
    st.sidebar.markdown("---")
# --- END DEBUGGING ---


# Validate that API Key and Project ID are available
if not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
    st.error("Firebase API Key or Project ID not found. Please configure them in .streamlit/secrets.toml under the [firebase] section with correct capitalization (APIKey, PROJECT_ID, APP_ID).")
    st.stop() # Stop the app if essential keys are missing

# Firebase Authentication REST API Endpoints
AUTH_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
AUTH_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
AUTH_RESET_PASSWORD_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"

# Firestore REST API Base URL for documents
# This path uses the APP_ID from secrets to maintain the structure
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data/user_profiles"

# Define your admin usernames here as a tuple of strings
ADMIN_USERNAME = ("admin@forscreenerpro", "admin@forscreenerpro2", "manav.nagpal2005@gmail.com")

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

    # Ensure Font Awesome is loaded for icons if you use them (e.g., in buttons)
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">',
        unsafe_allow_html=True
    )

def set_body_class():
    """
    Sets a class on the body element to force light mode styling.
    """
    # Force light mode regardless of Streamlit's theme option
    body_class = "light-mode"
    js_code = f"""
    <script>
        var body = window.parent.document.querySelector('body');
        if (body) {{
            body.className = ''; // Clear existing classes
            body.classList.add('{body_class}'); // Add the light mode class
            // Always set data-theme to 'light'
            body.setAttribute('data-theme', 'light');
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- Firebase REST API Helper Functions ---

def get_firestore_doc_url(uid):
    """Constructs the Firestore document URL for a given UID."""
    return f"{FIRESTORE_BASE_URL}/{uid}"

def get_firestore_collection_url():
    """Constructs the Firestore collection URL."""
    # For listing all documents in a collection, the URL is just the base collection URL
    return FIRESTORE_BASE_URL

def get_user_profile_from_firestore(uid, id_token):
    """Fetches user profile data from Firestore using UID and ID Token."""
    url = get_firestore_doc_url(uid)
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if 'fields' in data:
            # Firestore returns fields as {"fieldName": {"valueType": "value"}}
            profile = {}
            for key, value_obj in data['fields'].items():
                if 'stringValue' in value_obj:
                    profile[key] = value_obj['stringValue']
                elif 'booleanValue' in value_obj:
                    profile[key] = value_obj['booleanValue']
                # Add other types as needed (e.g., integerValue, arrayValue)
            return profile
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user profile from Firestore: {e}")
        print(f"Firestore Fetch Error Response: {response.text if 'response' in locals() else 'No response object'}") # Added for debugging
        return None

def set_user_profile_in_firestore(uid, id_token, profile_data):
    """Sets/updates user profile data in Firestore."""
    url = get_firestore_doc_url(uid)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    # Convert Python dict to Firestore's expected JSON structure
    fields = {}
    for key, value in profile_data.items():
        if isinstance(value, str):
            fields[key] = {"stringValue": value}
        elif isinstance(value, bool):
            fields[key] = {"booleanValue": value}
        # Add other types as needed
    payload = {"fields": fields}

    try:
        response = requests.patch(url, headers=headers, json=payload) # Use PATCH for update, PUT for replace
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error setting user profile in Firestore: {e}")
        print(f"Firestore Set Error Response: {response.text if 'response' in locals() else 'No response object'}") # Added for debugging
        return False

# --- Authentication and User Management Functions ---

def is_valid_email(email):
    """Basic validation for email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_current_user_admin():
    """Checks if the currently logged-in user is an admin."""
    return st.session_state.get("username") in ADMIN_USERNAME

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

        # Store additional profile data in Firestore
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
        if 'response' in locals(): # Check if response object exists
            error_data = response.json()
            print(f"Firebase Auth Registration Error Response: {error_data}") # Added for debugging
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
        if 'response' in locals(): # Check if response object exists
            error_data = response.json()
            print(f"Firebase Auth Sign-in Error Response: {error_data}") # Added for debugging
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
        if 'response' in locals(): # Check if response object exists
            error_data = response.json()
            print(f"Firebase Auth Reset Password Error Response: {error_data}") # Added for debugging
            if "error" in error_data and "message" in error_data["error"]:
                error_message = f"Failed to send password reset email: {error_data['error']['message']}"
        st.error(error_message)
        return False

def get_all_user_profiles_from_firestore():
    """Fetches all user profiles from the Firestore collection.
       Note: This is for admin view. In production, this should be secured
       and potentially paginated via a backend.
    """
    url = get_firestore_collection_url()
    # For listing documents, Firebase Firestore REST API doesn't require an ID token
    # unless security rules enforce it. Assuming public read for this collection for simplicity
    # in this context, but in production, this would need proper authentication.
    # For now, we'll try without a token, as there's no direct client-side way to get
    # an admin ID token without a full admin SDK setup.
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        users_list = []
        if 'documents' in data:
            for doc in data['documents']:
                fields = doc.get('fields', {})
                email = fields.get('email', {}).get('stringValue', 'N/A')
                company = fields.get('company', {}).get('stringValue', 'N/A')
                status = fields.get('status', {}).get('stringValue', 'N/A')
                # Extract UID from document name
                uid = doc['name'].split('/')[-1]
                # We don't store hashed passwords in Firestore for security reasons,
                # so we'll just indicate it's not exposed.
                users_list.append([email, "******** (Not Exposed)", status, company, uid])
        return users_list
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching all user profiles from Firestore: {e}")
        print(f"Firestore Get All Users Error Response: {response.text if 'response' in locals() else 'No response object'}") # Added for debugging
        return []

def get_uid_from_email_firestore(email):
    """
    Attempts to find a user's UID by their email from Firestore.
    This is a workaround as Firebase Auth REST API doesn't offer email-to-UID mapping directly for client-side.
    Requires Firestore security rules to allow querying by email.
    """
    url = f"{FIRESTORE_BASE_URL}:runQuery"
    query_payload = {
        "structuredQuery": {
            "from": [{"collectionId": "user_profiles"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "email"},
                    "op": "EQUAL",
                    "value": {"stringValue": email}
                }
            },
            "limit": 1
        }
    }
    try:
        response = requests.post(url, json=query_payload)
        response.raise_for_status()
        results = response.json()
        if results and len(results) > 0 and 'document' in results[0]:
            doc_name = results[0]['document']['name']
            uid = doc_name.split('/')[-1]
            return uid
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error finding UID by email in Firestore: {e}")
        print(f"Firestore Get UID by Email Error Response: {response.text if 'response' in locals() else 'No response object'}") # Added for debugging
        return None

def register_section():
    """Public self-registration form."""
    st.subheader("📝 Create New Account")
    with st.form("registration_form", clear_on_submit=True):
        new_username = st.text_input("Choose Username (Email address required)", key="new_username_reg_public")
        new_company_name = st.text_input("Company Name", key="new_company_name_reg_public") # New field
        new_password = st.text_input("Choose Password", type="password", key="new_password_reg_public")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password_reg_public")
        register_button = st.form_submit_button("Register New Account")

        if register_button:
            if not new_username or not new_password or not confirm_password or not new_company_name:
                st.error("Please fill in all fields.")
            elif not is_valid_email(new_username): # Email format validation
                st.error("Please enter a valid email address for the username.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Attempt to register with Firebase Auth
                result = register_user_firebase(new_username, new_password, new_company_name)
                if result["success"]:
                    st.success("✅ Registration successful! You are now logged in.")
                    # Automatically log in the user
                    st.session_state.authenticated = True
                    st.session_state.username = result["email"]
                    st.session_state.user_company = result["company"]
                    st.session_state.user_uid = result["uid"] # Store UID
                    st.session_state.id_token = result["idToken"] # Store ID Token
                    st.session_state.current_page = "welcome_dashboard" # Redirect
                    st.rerun()
                # Error message is handled within register_user_firebase


def admin_registration_section():
    """Admin-driven user creation form."""
    st.subheader("➕ Create New User Account (Admin Only)")
    with st.form("admin_registration_form", clear_on_submit=True):
        new_username = st.text_input("New User's Username (Email)", key="new_username_admin_reg")
        new_company_name = st.text_input("New User's Company Name", key="new_company_name_admin_reg") # New field
        new_password = st.text_input("New User's Password", type="password", key="new_password_admin_reg")
        admin_register_button = st.form_submit_button("Add New User")

    if admin_register_button:
        if not new_username or not new_password or not new_company_name:
            st.error("Please fill in all fields.")
        elif not is_valid_email(new_username): # Email format validation
            st.error("Please enter a valid email address for the username.")
        else:
            # Attempt to register with Firebase Auth
            result = register_user_firebase(new_username, new_password, new_company_name)
            if result["success"]:
                st.success(f"✅ User '{new_username}' added successfully!")
            # Error message is handled within register_user_firebase

def admin_password_reset_section():
    """Admin-driven password reset form."""
    st.subheader("🔑 Reset User Password (Admin Only)")
    # Fetch all users from Firestore to populate the selectbox
    users_data = get_all_user_profiles_from_firestore()
    user_options = [user[0] for user in users_data if user[0] not in ADMIN_USERNAME] # user[0] is email

    if not user_options:
        st.info("No other users to reset passwords for.")
        return

    with st.form("admin_reset_password_form", clear_on_submit=True):
        selected_user_email = st.selectbox("Select User to Reset Password For", user_options, key="reset_user_select")
        # Note: Firebase Auth REST API for password reset sends an email,
        # it does not allow setting a new password directly from client-side.
        st.info("A password reset email will be sent to the selected user.")
        reset_button = st.form_submit_button("Send Password Reset Email")

        if reset_button:
            if not selected_user_email:
                st.error("Please select a user.")
            else:
                send_password_reset_email_firebase(selected_user_email)

def admin_disable_enable_user_section():
    """Admin-driven user disable/enable form."""
    st.subheader("⛔ Toggle User Status (Admin Only)")
    users_data = get_all_user_profiles_from_firestore()
    user_options = [user[0] for user in users_data if user[0] not in ADMIN_USERNAME]

    if not user_options:
        st.info("No other users to manage status for.")
        return

    with st.form("admin_toggle_user_status_form", clear_on_submit=False):
        selected_user_email = st.selectbox("Select User to Toggle Status", user_options, key="toggle_user_select")

        # Find current status for the selected user
        current_status = "N/A"
        selected_user_uid = None
        for user_info in users_data:
            if user_info[0] == selected_user_email:
                current_status = user_info[2] # Status is at index 2
                selected_user_uid = user_info[4] # UID is at index 4
                break

        if selected_user_email and selected_user_uid:
            st.info(f"Current status of '{selected_user_email}': **{current_status.upper()}**")

            if st.form_submit_button(f"Toggle to {'Disable' if current_status == 'active' else 'Enable'} User"):
                new_status = "disabled" if current_status == "active" else "active"
                # Need an ID token to update Firestore.
                # For admin actions, ideally, this would be handled by a secure backend
                # that uses Firebase Admin SDK to get an admin ID token.
                # For this client-side example, we'll use the logged-in admin's token.
                admin_id_token = st.session_state.get('id_token')
                if admin_id_token:
                    profile_data = {
                        "status": new_status,
                        # Keep other fields as they are, or fetch them first and then update
                        "email": selected_user_email, # Ensure email is also in the update payload
                        "company": next((u[3] for u in users_data if u[0] == selected_user_email), "N/A")
                    }
                    if set_user_profile_in_firestore(selected_user_uid, admin_id_token, profile_data):
                        st.success(f"✅ User '{selected_user_email}' status set to **{new_status.upper()}**.")
                        st.rerun()
                    else:
                        st.error("Failed to update user status in Firestore.")
                else:
                    st.error("Admin ID token not found. Please log in as admin.")
        else:
            st.warning("Selected user not found or UID missing.")


def login_section():
    """Handles user login and public registration."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_company" not in st.session_state:
        st.session_state.user_company = None
    if "user_uid" not in st.session_state: # Store Firebase UID
        st.session_state.user_uid = None
    if "id_token" not in st.session_state: # Store Firebase ID Token
        st.session_state.id_token = None

    # Initialize active_login_tab_selection if not present
    if "active_login_tab_selection" not in st.session_state:
        st.session_state.active_login_tab_selection = "Login" # Default to Login

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
                    # Error message is handled within sign_in_user_firebase
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
        st.session_state.pop('current_quote', None) # Clear the quote on logout
        st.session_state.active_login_tab_selection = "Login" # Reset to login tab
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
    # Select a new quote if not already in session state
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
                background: linear-gradient(135deg, #f0f2f5 0%, #e0e5ec 100%); /* Soft gradient background */
                border-radius: 12px; /* More rounded corners */
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); /* Deeper, softer shadow */
                text-align: center;
                animation: fadeInScale 0.7s ease-out forwards; /* Apply animation */
                position: relative; /* For the sparkle effect */
                overflow: hidden; /* To contain the sparkle */
            }}

            .beautiful-greeting-card::before {{
                content: '✨'; /* Add a subtle sparkle effect */
                position: absolute;
                top: 10px;
                left: 10px;
                font-size: 2em;
                opacity: 0.2;
                pointer-events: none;
            }}
            .beautiful-greeting-card::after {{
                content: '🌟'; /* Another sparkle */
                position: absolute;
                bottom: 10px;
                right: 10px;
                font-size: 2em;
                opacity: 0.2;
                pointer-events: none;
            }}

            .beautiful-greeting-title {{
                font-size: 2.2em; /* Larger title */
                font-weight: 700; /* Bolder */
                color: #2c3e50; /* Darker, more prominent color */
                margin-bottom: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.05); /* Subtle text shadow */
            }}

            .beautiful-username {{
                color: #3498db; /* Vibrant blue for username */
                font-weight: 800; /* Extra bold */
            }}

            .beautiful-welcome-text {{
                font-size: 1.15em; /* Slightly larger body text */
                color: #555555; /* Softer text color */
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
                font-size: 1.6em; /* Larger, more impactful emojis */
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
                color: #6fa8f7; /* Lighter blue for dark mode */
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
    # Set initial page config. We will override theme later.
    st.set_page_config(page_title="ScreenerPro Candidate Portal", layout="wide", initial_sidebar_state="expanded")

    # Force theme to light mode
    st.session_state.theme = "light"
    # Streamlit's internal theme option should also be set to light
    st._config.set_option("theme.base", "light")


    # Load the external CSS file
    load_css("style.css")

    # Set the body class based on the current theme (which is now forced to light)
    set_body_class()

    # --- Permanent Sidebar Content (Always Visible) ---
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        logo_path = "logo.png"  # Assuming logo is in the same directory

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
            st.warning(f"Logo file not found at: {logo_path}") # More specific message

        st.sidebar.write("---")

    # --- Main Content Area Logic ---
    is_authenticated = login_section() # Call login_section first

    if is_authenticated:
        # If authenticated, display conditional sidebar content
        with st.sidebar:
            st.markdown("<p>Navigate</p>", unsafe_allow_html=True)

            # Navigation Buttons (using st.button and wrapping in custom div for styling)
            # Resume Screener Button
            if st.button("Resume Screener", key="nav_resume_screen"):
                st.session_state.current_page = "resume_screen"
            st.markdown(f'<style>div[data-testid="stButton-nav_resume_screen"] > button {{ background-color: {"var(--color-accent-pink-soft)" if st.session_state.current_page == "resume_screen" else "transparent"} !important; color: {"var(--color-accent-pink)" if st.session_state.current_page == "resume_screen" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "resume_screen" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "resume_screen" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_resume_screen"] > button i {{ color: {"var(--color-accent-pink)" if st.session_state.current_page == "resume_screen" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_resume_screen"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # Top Leaderboard Button
            if st.button("Top Leaderboard", key="nav_top_leaderboard"):
                st.session_state.current_page = "top_leaderboard"
            st.markdown(f'<style>div[data-testid="stButton-nav_top_leaderboard"] > button {{ background-color: {"var(--color-accent-orange-soft)" if st.session_state.current_page == "top_leaderboard" else "transparent"} !important; color: {"var(--color-accent-orange)" if st.session_state.current_page == "top_leaderboard" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "top_leaderboard" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "top_leaderboard" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_top_leaderboard"] > button i {{ color: {"var(--color-accent-orange)" if st.session_state.current_page == "top_leaderboard" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_top_leaderboard"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # Certificate Verify Button
            if st.button("Verify Certificate", key="nav_certificate_verify"):
                st.session_state.current_page = "certificate_verify"
            st.markdown(f'<style>div[data-testid="stButton-nav_certificate_verify"] > button {{ background-color: {"var(--color-accent-blue-soft)" if st.session_state.current_page == "certificate_verify" else "transparent"} !important; color: {"var(--color-accent-blue)" if st.session_state.current_page == "certificate_verify" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "certificate_verify" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "certificate_verify" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_certificate_verify"] > button i {{ color: {"var(--color-accent-blue)" if st.session_state.current_page == "certificate_verify" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_certificate_verify"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # Total Resumes Screened Button
            if st.button("Total Resumes Screened", key="nav_total_screened"):
                st.session_state.current_page = "total_screened"
            st.markdown(f'<style>div[data-testid="stButton-nav_total_screened"] > button {{ background-color: {"var(--color-accent-blue-soft)" if st.session_state.current_page == "total_screened" else "transparent"} !important; color: {"var(--color-accent-blue)" if st.session_state.current_page == "total_screened" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "total_screened" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "total_screened" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_total_screened"] > button i {{ color: {"var(--color-accent-blue)" if st.session_state.current_page == "total_screened" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_total_screened"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # About Us Button
            if st.button("About Us", key="nav_about_us"):
                st.session_state.current_page = "about_us"
            st.markdown(f'<style>div[data-testid="stButton-nav_about_us"] > button {{ background-color: {"var(--color-accent-blue-soft)" if st.session_state.current_page == "about_us" else "transparent"} !important; color: {"var(--color-accent-blue)" if st.session_state.current_page == "about_us" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "about_us" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "about_us" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_about_us"] > button i {{ color: {"var(--color-accent-blue)" if st.session_state.current_page == "about_us" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_about_us"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # Feedback Form Button
            if st.button("Feedback Form", key="nav_feedback_form"):
                st.session_state.current_page = "feedback_form"
            st.markdown(f'<style>div[data-testid="stButton-nav_feedback_form"] > button {{ background-color: {"var(--color-accent-blue-soft)" if st.session_state.current_page == "feedback_form" else "transparent"} !important; color: {"var(--color-accent-blue)" if st.session_state.current_page == "feedback_form" else "var(--color-text-primary-light)"} !important; font-weight: {"600" if st.session_state.current_page == "feedback_form" else "500"} !important; box-shadow: {"var(--shadow-card)" if st.session_state.current_page == "feedback_form" else "none"} !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_feedback_form"] > button i {{ color: {"var(--color-accent-blue)" if st.session_state.current_page == "feedback_form" else "var(--color-text-primary-light)"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_feedback_form"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)

            # Logout Button
            if st.button("Logout", key="nav_logout"):
                st.session_state.current_page = "logout"
            st.markdown(f'<style>div[data-testid="stButton-nav_logout"] > button {{ background-color: transparent !important; color: var(--color-text-primary-light) !important; font-weight: 500 !important; box-shadow: none !important; border-radius: 9999px !important; padding: 0.7rem 1.2rem !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 0.8rem !important; width: 100% !important; }} div[data-testid="stButton-nav_logout"] > button i {{ color: var(--color-text-primary-light) !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<style>div[data-testid="stButton-nav_logout"] {{ margin: 0.3rem 0; }}</style>', unsafe_allow_html=True)


            # Logged in as: and Company: info
            st.sidebar.markdown("---")
            st.sidebar.success(f"Logged in as: **{st.session_state.username}**")
            if st.session_state.get('user_company'):
                st.sidebar.info(f"Company: **{st.session_state.user_company}**")

            # Admin Section in Sidebar
            if is_current_user_admin():
                st.sidebar.markdown("---")
                st.sidebar.subheader("Admin Panel")
                admin_tab_selection = st.sidebar.radio(
                    "Admin Actions:",
                    ("Create User", "Reset Password", "Toggle User Status", "View All Users", "Generate Fake Data"),
                    key="admin_tabs"
                )

        # Content for authenticated users
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

        # Admin Section (only visible to admins)
        if is_current_user_admin():
            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
            st.header("Admin Management")

            # Admin actions are controlled by the sidebar radio buttons
            if st.session_state.get("admin_tabs") == "Create User":
                admin_registration_section()
            elif st.session_state.get("admin_tabs") == "Reset Password":
                admin_password_reset_section()
            elif st.session_state.get("admin_tabs") == "Toggle User Status":
                admin_disable_enable_user_section()
            elif st.session_state.get("admin_tabs") == "Generate Fake Data":
                generate_fake_data_page()
            elif st.session_state.get("admin_tabs") == "View All Users":
                st.subheader("👥 All Registered Users:")
                try:
                    users_data = get_all_user_profiles_from_firestore()
                    if users_data:
                        # Ensure 'UID' column is included for admin view
                        df = pd.DataFrame(users_data, columns=["Email/Username", "Password (Not Exposed)", "Status", "Company", "UID"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No users registered yet.")
                except Exception as e:
                    st.error(f"Error loading user data for admin view: {e}")
    else:
        # If not authenticated, only show the login/registration section
        pass # login_section() is called before this block and handles non-authenticated display

if __name__ == "__main__":
    main()
