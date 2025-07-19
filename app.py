import streamlit as st
import json
import bcrypt
import os
import re
import pandas as pd
import time # For simulation of delays

# Import your page functions
from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from certificate_verify import certificate_verifier_page
from total_screened_page import total_screened_page

# --- Functions from your login.py (included directly for simplicity in this single file structure) ---
USER_DB_FILE = "users.json"
ADMIN_USERNAME = ("admin@forscreenerpro", "admin@forscreenerpro2", "manav.nagpal2005@gmail.com") 

def load_users():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
            for username, data in users.items():
                if isinstance(data, str):
                    users[username] = {"password": data, "status": "active", "company": "N/A"}
                elif "status" not in data:
                    data["status"] = "active"
                if "company" not in data:
                    data["company"] = "N/A"
            return users
    except json.JSONDecodeError:
        st.warning(f"⚠️ '{USER_DB_FILE}' is empty or corrupted. Re-initializing with an empty user database.")
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while loading users: {e}")
        return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.\w+", email)

def register_section():
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
                users = load_users()
                if new_username in users:
                    st.error("Username already exists. Please choose a different one.")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "status": "active",
                        "company": new_company_name
                    }
                    save_users(users)
                    st.success("✅ Registration successful! You are now logged in.")
                    
                    st.session_state.authenticated = True
                    st.session_state.username = new_username
                    st.session_state.user_company = new_company_name
                    st.session_state.current_page = "resume_screen"
                    st.rerun()
                    
def admin_registration_section():
    st.subheader("➕ Create New User Account (Admin Only)")
    with st.form("admin_registration_form", clear_on_submit=True):
        new_username = st.text_input("New User's Username (Email)", key="new_username_admin_reg")
        new_company_name = st.text_input("New User's Company Name", key="new_company_name_admin_reg")
        new_password = st.text_input("New User's Password", type="password", key="new_password_admin_reg")
        admin_register_button = st.form_submit_button("Add New User")

    if admin_register_button:
        if not new_username or not new_password or not new_company_name:
            st.error("Please fill in all fields.")
        elif not is_valid_email(new_username):
            st.error("Please enter a valid email address for the username.")
        else:
            users = load_users()
            if new_username in users:
                st.error(f"User '{new_username}' already exists.")
            else:
                users[new_username] = {
                    "password": hash_password(new_password),
                    "status": "active",
                    "company": new_company_name
                }
                save_users(users)
                st.success(f"✅ User '{new_username}' added successfully!")

def admin_password_reset_section():
    st.subheader("🔑 Reset User Password (Admin Only)")
    users = load_users()
    user_options = [user for user in users.keys() if user not in ADMIN_USERNAME] 
    
    if not user_options:
        st.info("No other users to reset passwords for.")
        return

    with st.form("admin_reset_password_form", clear_on_submit=True):
        selected_user = st.selectbox("Select User to Reset Password For", user_options, key="reset_user_select")
        new_password = st.text_input("New Password", type="password", key="new_password_reset")
        reset_button = st.form_submit_button("Reset Password")

        if reset_button:
            if not new_password:
                st.error("Please enter a new password.")
            else:
                users[selected_user]["password"] = hash_password(new_password)
                save_users(users)
                st.success(f"✅ Password for '{selected_user}' has been reset.")

def admin_disable_enable_user_section():
    st.subheader("⛔ Toggle User Status (Admin Only)")
    users = load_users()
    user_options = [user for user in users.keys() if user not in ADMIN_USERNAME] 

    if not user_options:
        st.info("No other users to manage status for.")
        return
        
    with st.form("admin_toggle_user_status_form", clear_on_submit=False):
        selected_user = st.selectbox("Select User to Toggle Status", user_options, key="toggle_user_select")
        
        current_status = users[selected_user]["status"]
        st.info(f"Current status of '{selected_user}': **{current_status.upper()}**")

        if st.form_submit_button(f"Toggle to {'Disable' if current_status == 'active' else 'Enable'} User"):
            new_status = "disabled" if current_status == "active" else "active"
            users[selected_user]["status"] = new_status
            save_users(users)
            st.success(f"✅ User '{selected_user}' status set to **{new_status.upper()}**.")
            st.rerun()

def login_section():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if "active_login_tab_selection" not in st.session_state:
        if not os.path.exists(USER_DB_FILE) or len(load_users()) == 0:
            st.session_state.active_login_tab_selection = "Register"
        else:
            st.session_state.active_login_tab_selection = "Login"

    if st.session_state.authenticated:
        return True

    # Use st.tabs for a modern tabbed interface if supported, otherwise fall back to st.radio
    # Streamlit 1.18.0+ supports st.tabs
    try:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("🔐 HR Login to ScreenerPro")
            st.info("If you don't have an account, please go to the 'Register' tab.")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="username_login")
                password = st.text_input("Password", type="password", key="password_login")
                submitted = st.form_submit_button("Login")

                if submitted:
                    users = load_users()
                    if username not in users:
                        st.error("❌ Invalid username or password. Please register if you don't have an account.")
                    else:
                        user_data = users[username]
                        if user_data["status"] == "disabled":
                            st.error("❌ Your account has been disabled. Please contact an administrator.")
                        elif check_password(password, user_data["password"]):
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_company = user_data.get("company", "N/A")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
        with tab2:
            register_section()
    except AttributeError:
        # Fallback for older Streamlit versions that don't support st.tabs
        tab_selection = st.radio(
            "Select an option:",
            ("Login", "Register"),
            key="login_register_radio",
            index=0 if st.session_state.active_login_tab_selection == "Login" else 1
        )

        if tab_selection == "Login":
            st.subheader("🔐 HR Login to ScreenerPro")
            st.info("If you don't have an account, please go to the 'Register' option first.")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="username_login")
                password = st.text_input("Password", type="password", key="password_login")
                submitted = st.form_submit_button("Login")

                if submitted:
                    users = load_users()
                    if username not in users:
                        st.error("❌ Invalid username or password. Please register if you don't have an account.")
                    else:
                        user_data = users[username]
                        if user_data["status"] == "disabled":
                            st.error("❌ Your account has been disabled. Please contact an administrator.")
                        elif check_password(password, user_data["password"]):
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_company = user_data.get("company", "N/A")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
        elif tab_selection == "Register":
            register_section()

    return st.session_state.authenticated

def is_current_user_admin():
    return st.session_state.get("authenticated", False) and st.session_state.get("username") in ADMIN_USERNAME

def logout_page():
    st.title("👋 Logging Out...")
    st.write("You are about to be logged out. Thank you for using ScreenerPro!")
    if st.button("Confirm Logout"):
        st.session_state.authenticated = False
        st.session_state.pop('username', None)
        st.session_state.pop('user_company', None)
        st.session_state.active_login_tab_selection = "Login"
        st.rerun()
    st.info("You will be redirected to the login page shortly if you don't confirm.")


def main():
    st.set_page_config(
        page_title="ScreenerPro Candidate Portal",
        layout="wide",
        initial_sidebar_state="expanded",
        # Adding a favicon for branding
        # icon="https://raw.githubusercontent.com/manavnagpal08/yg/main/logo.png" # Uncomment and replace if you have a square icon
    )

    if "current_page" not in st.session_state:
        st.session_state.current_page = "resume_screen"
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    # Apply global CSS based on theme
    if st.session_state.theme == "dark":
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

            :root {
                --primary-color: #00cec9; /* Teal */
                --secondary-color: #00b0a8; /* Darker Teal */
                --accent-color: #ffd700; /* Gold for highlights */
                --background-color-dark: #121212; /* Even darker background */
                --surface-color-dark: #1f1f1f; /* Sidebar, card backgrounds */
                --card-background-dark: #2a2a2a; /* Inner card backgrounds */
                --input-background-dark: #3a3a3a; /* Input fields, alerts */
                --text-color-dark: #e0e0e0;
                --text-secondary-dark: #b0b0b0;
                --border-color-dark: #444444;
                --shadow-light: rgba(0,0,0,0.3);
                --shadow-dark: rgba(0,0,0,0.6); /* Stronger shadow */
            }

            html, body, [data-testid="stAppViewContainer"] {
                font-family: 'Inter', sans-serif;
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
                transition: background-color 0.7s ease-in-out; /* Slower, smoother theme transition */
            }
            [data-testid="stSidebar"] {
                background-color: var(--surface-color-dark);
                color: var(--text-color-dark);
                padding: 2rem 1.2rem; /* More horizontal padding */
                box-shadow: 3px 0 15px var(--shadow-dark); /* Deeper shadow */
                transition: background-color 0.7s ease-in-out, box-shadow 0.4s ease;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Playfair Display', serif;
                color: var(--primary-color);
                margin-top: 1.8rem; /* More spacing */
                margin-bottom: 1.2rem;
                text-shadow: 2px 2px 5px rgba(0,0,0,0.7); /* More pronounced text shadow */
                letter-spacing: 0.02em; /* Subtle letter spacing for headings */
            }
            /* Main Content Area */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            /* Text input, text area, selectbox, etc. */
            .stTextInput>div>div>input,
            .stTextArea>div>div>textarea,
            .stSelectbox>div>div>div>div>span,
            .stMultiSelect>div>div>div>div>span,
            .stSlider .stSliderHandle,
            .stRadio > label > div,
            .stCheckbox > label > div {
                background-color: var(--input-background-dark) !important;
                color: var(--text-color-dark) !important;
                border: 1px solid var(--border-color-dark) !important;
                border-radius: 0.75rem;
                padding: 0.85rem; /* Slightly more padding */
                box-shadow: inset 0 2px 5px rgba(0,0,0,0.3); /* Deeper inner shadow */
                transition: all 0.3s ease-in-out;
            }
            /* Input Field Focus Effect */
            .stTextInput>div>div>input:focus,
            .stTextArea>div>div>textarea:focus,
            .stSelectbox>div>div>div>div>span:focus,
            .stMultiSelect>div>div>div>div>span:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 4px rgba(0,206,201,0.5) !important; /* Brighter, wider glow */
                outline: none;
            }
            /* Labels for inputs */
            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stMultiSelect label,
            .stSlider label,
            .stRadio label,
            .stCheckbox label {
                color: var(--text-color-dark) !important;
                font-weight: 600; /* Bolder labels */
                margin-bottom: 0.6rem;
                text-shadow: 0 1px 2px rgba(0,0,0,0.4);
            }
            /* Buttons */
            .stButton>button {
                background-image: linear-gradient(45deg, var(--primary-color) 0%, var(--secondary-color) 100%); /* Subtle gradient */
                color: white;
                border: none;
                border-radius: 0.75rem;
                padding: 0.9rem 1.8rem; /* More prominent buttons */
                font-weight: 700; /* Bolder text */
                letter-spacing: 0.08em; /* More letter spacing */
                text-transform: uppercase; /* Uppercase for buttons */
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                box-shadow: 0 8px 25px var(--shadow-light); /* Even more pronounced initial shadow */
                width: 100%;
                margin-bottom: 0.85rem;
            }
            .stButton>button:hover {
                background-image: linear-gradient(45deg, var(--secondary-color) 0%, var(--primary-color) 100%); /* Reverse gradient on hover */
                transform: translateY(-6px) scale(1.02); /* Larger lift and slight scale */
                box-shadow: 0 15px 30px var(--shadow-dark); /* Deeper shadow on hover */
            }
            .stButton>button:active {
                transform: translateY(-2px);
                box-shadow: 0 4px 10px var(--shadow-light);
            }

            /* Expander background */
            .streamlit-expanderHeader {
                background-color: var(--input-background-dark);
                color: var(--text-color-dark);
                border-radius: 0.75rem;
                padding: 0.9rem 1.2rem;
                font-weight: 600;
                border: 1px solid var(--border-color-dark);
                box-shadow: 0 3px 10px var(--shadow-light);
                transition: all 0.3s ease-in-out;
            }
            .streamlit-expanderHeader:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 8px 20px var(--shadow-dark);
            }
            .streamlit-expanderContent {
                background-color: var(--card-background-dark);
                color: var(--text-color-dark);
                border-radius: 0.75rem;
                padding: 1.2rem;
                margin-top: 0.6rem;
                border: 1px solid var(--border-color-dark);
                box-shadow: 0 3px 10px var(--shadow-light);
            }
            /* Info/Success/Error boxes */
            .stAlert {
                background-color: var(--input-background-dark);
                color: var(--text-color-dark);
                border-radius: 0.75rem;
                padding: 1.2rem;
                border: 1px solid var(--border-color-dark);
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            .stAlert > div > div > div > div {
                color: var(--text-color-dark);
            }
            .stAlert [data-testid="stMarkdownContainer"] p {
                color: var(--text-color-dark) !important;
            }
            /* Dataframe styling */
            .stDataFrame {
                border-radius: 0.75rem;
                overflow: hidden;
                box-shadow: 0 5px 18px rgba(0,0,0,0.3);
                border: 1px solid var(--border-color-dark);
                transition: all 0.3s ease-in-out;
            }
            .stDataFrame:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            }
            .stDataFrame section.main tr:nth-child(even) {
                background-color: var(--surface-color-dark);
            }
            /* Metric boxes */
            .stMetric {
                background-color: var(--card-background-dark);
                border-radius: 0.75rem;
                padding: 1.8rem; /* Even more padding */
                border: 1px solid var(--border-color-dark);
                box-shadow: 0 5px 18px rgba(0,0,0,0.3);
                transition: all 0.3s ease-in-out;
            }
            .stMetric:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            }
            .stMetric > div > label {
                color: var(--text-secondary-dark) !important;
                font-size: 1em; /* Slightly larger label */
                margin-bottom: 0.6rem;
                font-weight: 500;
            }
            .stMetric > div > div {
                font-size: 2.5em !important; /* Larger value */
                font-weight: 800; /* Extra bold */
                color: var(--primary-color);
            }

            /* Radio buttons and checkboxes */
            .stRadio div[role="radiogroup"] label, .stCheckbox label {
                padding: 0.6rem 0;
                transition: color 0.2s ease;
            }
            .stRadio div[role="radiogroup"] label:hover, .stCheckbox label:hover {
                color: var(--primary-color) !important;
            }
            
            /* Horizontal Rule (st.divider) */
            hr {
                border-top: 1px solid var(--border-color-dark);
                margin: 2rem 0; /* More vertical space */
            }
            /* Specific style for the HR Portal button in sidebar */
            .hr-portal-button button {
                background-image: linear-gradient(45deg, #4CAF50 0%, #388E3C 100%) !important; /* Green gradient */
                box-shadow: 0 8px 25px rgba(76,175,80,0.4) !important;
            }
            .hr-portal-button button:hover {
                background-image: linear-gradient(45deg, #388E3C 0%, #4CAF50 100%) !important;
                transform: translateY(-6px) scale(1.02) !important;
                box-shadow: 0 15px 30px rgba(76,175,80,0.6) !important;
            }

            /* --- Custom Animations / Elements --- */

            /* Hero Section Text Animation */
            @keyframes fadeInSlideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .hero-title {
                font-size: 3.5em; /* Larger title */
                font-weight: 800;
                text-align: center;
                margin-bottom: 0.5em;
                animation: fadeInSlideIn 1s ease-out forwards;
                color: var(--primary-color);
                text-shadow: 3px 3px 8px rgba(0,0,0,0.7);
            }
            .hero-subtitle {
                font-size: 1.5em;
                text-align: center;
                color: var(--text-secondary-dark);
                animation: fadeInSlideIn 1.2s ease-out forwards;
                animation-delay: 0.2s; /* Delay for subtitle */
                opacity: 0; /* Start hidden */
            }
            .stAlert.info {
                background-color: var(--card-background-dark);
            }

            /* Loader (could be replaced by Lottie animation) */
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }
            .stSpinner > div { /* Target Streamlit's default spinner */
                color: var(--primary-color) !important;
            }
            [data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"] p {
                color: var(--text-color-dark) !important; /* Text inside st.spinner */
                animation: pulse 1.5s infinite ease-in-out;
            }

            /* Sidebar custom styling for logged in user info */
            .sidebar-user-info {
                padding: 1rem 0.5rem;
                background-color: var(--card-background-dark);
                border-radius: 0.75rem;
                border: 1px solid var(--border-color-dark);
                margin-top: 1rem;
                box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
                color: var(--text-secondary-dark);
            }
            .sidebar-user-info strong {
                color: var(--primary-color);
            }
            .sidebar-user-info .stAlert { /* Adjust alerts inside sidebar */
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0.5rem 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else: # Light Mode
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

            :root {
                --primary-color: #00cec9;
                --secondary-color: #00b0a8;
                --accent-color: #ff9800;
                --background-color-light: #e8eef4; /* Lighter background */
                --surface-color-light: #ffffff;
                --card-background-light: #f8f8f8;
                --input-background-light: #ffffff;
                --text-color-light: #222222; /* Darker text for better contrast */
                --text-secondary-light: #666666;
                --border-color-light: #d0d0d0;
                --shadow-light: rgba(0,0,0,0.1);
                --shadow-dark: rgba(0,0,0,0.25);
            }

            html, body, [data-testid="stAppViewContainer"] {
                font-family: 'Inter', sans-serif;
                background-color: var(--background-color-light);
                color: var(--text-color-light);
                transition: background-color 0.7s ease-in-out;
            }
            [data-testid="stSidebar"] {
                background-color: var(--surface-color-light);
                color: var(--text-color-light);
                padding: 2rem 1.2rem;
                box-shadow: 3px 0 15px var(--shadow-light);
                transition: background-color 0.7s ease-in-out, box-shadow 0.4s ease;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Playfair Display', serif;
                color: var(--primary-color);
                margin-top: 1.8rem;
                margin-bottom: 1.2rem;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                letter-spacing: 0.02em;
            }
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            /* Text input, text area, selectbox, etc. */
            .stTextInput>div>div>input,
            .stTextArea>div>div>textarea,
            .stSelectbox>div>div>div>div>span,
            .stMultiSelect>div>div>div>div>span,
            .stSlider .stSliderHandle,
            .stRadio > label > div,
            .stCheckbox > label > div {
                background-color: var(--input-background-light) !important;
                color: var(--text-color-light) !important;
                border: 1px solid var(--border-color-light) !important;
                border-radius: 0.75rem;
                padding: 0.85rem;
                box-shadow: inset 0 2px 5px rgba(0,0,0,0.08);
                transition: all 0.3s ease-in-out;
            }
            /* Input Field Focus Effect */
            .stTextInput>div>div>input:focus,
            .stTextArea>div>div>textarea:focus,
            .stSelectbox>div>div>div>div>span:focus,
            .stMultiSelect>div>div>div>div>span:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 4px rgba(0,206,201,0.2) !important;
                outline: none;
            }
            /* Labels for inputs */
            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stMultiSelect label,
            .stSlider label,
            .stRadio label,
            .stCheckbox label {
                color: var(--text-color-light) !important;
                font-weight: 600;
                margin-bottom: 0.6rem;
                text-shadow: 0 1px 2px rgba(255,255,255,0.7);
            }
            /* Buttons */
            .stButton>button {
                background-image: linear-gradient(45deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                border: none;
                border-radius: 0.75rem;
                padding: 0.9rem 1.8rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                box-shadow: 0 8px 25px var(--shadow-light);
                width: 100%;
                margin-bottom: 0.85rem;
            }
            .stButton>button:hover {
                background-image: linear-gradient(45deg, var(--secondary-color) 0%, var(--primary-color) 100%);
                transform: translateY(-6px) scale(1.02);
                box-shadow: 0 15px 30px var(--shadow-dark);
            }
            .stButton>button:active {
                transform: translateY(-2px);
                box-shadow: 0 4px 10px var(--shadow-light);
            }
            /* Expander background */
            .streamlit-expanderHeader {
                background-color: #e0e0e0;
                color: var(--text-color-light);
                border-radius: 0.75rem;
                padding: 0.9rem 1.2rem;
                font-weight: 600;
                border: 1px solid var(--border-color-light);
                box-shadow: 0 3px 10px var(--shadow-light);
                transition: all 0.3s ease-in-out;
            }
            .streamlit-expanderHeader:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 8px 20px var(--shadow-dark);
            }
            .streamlit-expanderContent {
                background-color: var(--card-background-light);
                color: var(--text-color-light);
                border-radius: 0.75rem;
                padding: 1.2rem;
                margin-top: 0.6rem;
                border: 1px solid var(--border-color-light);
                box-shadow: 0 3px 10px var(--shadow-light);
            }
            /* Info/Success/Error boxes */
            .stAlert {
                background-color: var(--input-background-light);
                color: var(--text-color-light);
                border-radius: 0.75rem;
                padding: 1.2rem;
                border: 1px solid var(--border-color-light);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .stAlert > div > div > div > div {
                color: var(--text-color-light);
            }
            .stAlert [data-testid="stMarkdownContainer"] p {
                color: var(--text-color-light) !important;
            }
            /* Dataframe styling */
            .stDataFrame {
                border-radius: 0.75rem;
                overflow: hidden;
                box-shadow: 0 5px 18px rgba(0,0,0,0.15);
                border: 1px solid var(--border-color-light);
                transition: all 0.3s ease-in-out;
            }
            .stDataFrame:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .stDataFrame section.main tr:nth-child(even) {
                background-color: #f5f5f5;
            }
            /* Metric boxes */
            .stMetric {
                background-color: var(--card-background-light);
                border-radius: 0.75rem;
                padding: 1.8rem;
                border: 1px solid var(--border-color-light);
                box-shadow: 0 5px 18px rgba(0,0,0,0.15);
                transition: all 0.3s ease-in-out;
            }
            .stMetric:hover {
                 transform: translateY(-3px);
                 box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .stMetric > div > label {
                color: var(--text-secondary-light) !important;
                font-size: 1em;
                margin-bottom: 0.6rem;
                font-weight: 500;
            }
            .stMetric > div > div {
                font-size: 2.5em !important;
                font-weight: 800;
                color: var(--primary-color);
            }
            /* Radio buttons and checkboxes */
            .stRadio div[role="radiogroup"] label, .stCheckbox label {
                padding: 0.6rem 0;
                transition: color 0.2s ease;
            }
            .stRadio div[role="radiogroup"] label:hover, .stCheckbox label:hover {
                color: var(--primary-color) !important;
            }
            /* Horizontal Rule (st.divider) */
            hr {
                border-top: 1px solid var(--border-color-light);
                margin: 2rem 0;
            }
            /* Specific style for the HR Portal button in sidebar */
            .hr-portal-button button {
                background-image: linear-gradient(45deg, #4CAF50 0%, #388E3C 100%) !important;
                box-shadow: 0 8px 25px rgba(76,175,80,0.2) !important;
            }
            .hr-portal-button button:hover {
                background-image: linear-gradient(45deg, #388E3C 0%, #4CAF50 100%) !important;
                transform: translateY(-6px) scale(1.02) !important;
                box-shadow: 0 15px 30px rgba(76,175,80,0.3) !important;
            }

            /* --- Custom Animations / Elements --- */

            /* Hero Section Text Animation */
            @keyframes fadeInSlideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .hero-title {
                font-size: 3.5em;
                font-weight: 800;
                text-align: center;
                margin-bottom: 0.5em;
                animation: fadeInSlideIn 1s ease-out forwards;
                color: var(--primary-color);
                text-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            .hero-subtitle {
                font-size: 1.5em;
                text-align: center;
                color: var(--text-secondary-light);
                animation: fadeInSlideIn 1.2s ease-out forwards;
                animation-delay: 0.2s;
                opacity: 0;
            }
            .stAlert.info {
                background-color: var(--card-background-light);
            }

            /* Loader (could be replaced by Lottie animation) */
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }
            .stSpinner > div {
                color: var(--primary-color) !important;
            }
            [data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"] p {
                color: var(--text-color-light) !important;
                animation: pulse 1.5s infinite ease-in-out;
            }

            /* Sidebar custom styling for logged in user info */
            .sidebar-user-info {
                padding: 1rem 0.5rem;
                background-color: var(--card-background-light);
                border-radius: 0.75rem;
                border: 1px solid var(--border-color-light);
                margin-top: 1rem;
                box-shadow: inset 0 0 5px rgba(0,0,0,0.08);
                color: var(--text-secondary-light);
            }
            .sidebar-user-info strong {
                color: var(--primary-color);
            }
            .sidebar-user-info .stAlert {
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0.5rem 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


    # Ensure all admin users exist for testing/initial setup
    users = load_users()
    default_admin_password = "adminpass" 
    for admin_user in ADMIN_USERNAME:
        if admin_user not in users:
            users[admin_user] = {"password": hash_password(default_admin_password), "status": "active", "company": "AdminCo"}
            st.sidebar.info(f"Created default admin user: {admin_user} with password '{default_admin_password}'")
    save_users(users)

    # Authentication section
    is_authenticated = login_section()

    if not is_authenticated:
        st.sidebar.write("---")
        st.sidebar.info("Please log in or register to access the portal features.")
        return

    # --- ONLY RENDER BELOW THIS IF AUTHENTICATED ---
    # Sidebar Header with Logo and Title
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="https://raw.githubusercontent.com/manavnagpal08/yg/main/logo.png" alt="ScreenerPro Logo" style="height: 80px; margin-bottom: 10px;">
            <h1 style="color: var(--primary-color); font-size: 2em; margin: 0; text-shadow: none;">ScreenerPro</h1>
            <p style="color: var(--text-secondary-dark); font-size: 0.8em; margin: 0; font-weight: 300;">Candidate Portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    dark_mode_checkbox = st.sidebar.checkbox("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    if dark_mode_checkbox:
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

    st.sidebar.markdown("---")
    # HR Portal Button with Icon
    st.sidebar.markdown(
        """
        <div class="hr-portal-button">
            <a href="https://screenerpro.streamlit.app/" target="_blank">
                <button>
                    <i class="fas fa-external-link-alt" style="margin-right:8px;"></i> Open HR Portal
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    st.sidebar.subheader("Main Navigation")
    
    # Navigation buttons with icons
    if st.sidebar.button("📄 Resume Screen", key="nav_resume", help="Screen candidates using AI"):
        st.session_state.current_page = "resume_screen"
    if st.sidebar.button("🏆 Top Leaderboard", key="nav_leaderboard", help="View top-performing candidates"):
        st.session_state.current_page = "top_leaderboard"
    if st.sidebar.button("✅ Verify Certificate", key="nav_certificate_verify", help="Verify authenticity of certificates"):
        st.session_state.current_page = "certificate_verify"
    if st.sidebar.button("📊 Total Screened Data", key="nav_total_screened", help="Overview of all screened resumes"):
        st.session_state.current_page = "total_screened"
    
    st.sidebar.markdown("---") # Visual divider

    st.sidebar.subheader("About & Support")
    if st.sidebar.button("ℹ️ About ScreenerPro", key="nav_about_us", help="Learn more about this application"):
        st.session_state.current_page = "about_us"

    if st.sidebar.button("💬 Feedback & Help", key="nav_feedback_form", help="Provide feedback or ask for help"):
        st.session_state.current_page = "feedback_form"
    
    st.sidebar.markdown("---") # Visual divider

    # Logged In User Info
    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-info">
            <p>Logged in as: <strong>{st.session_state.username}</strong></p>
            <p>Company: <strong>{st.session_state.user_company}</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("➡️ Logout", key="nav_logout", help="Log out of your account"):
        st.session_state.current_page = "logout"

    # --- Main Content Area ---
    # Hero Section for the main (first) page after login
    if st.session_state.current_page == "resume_screen":
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 3rem;">
                <h1 class="hero-title">Welcome to ScreenerPro, {st.session_state.username.split('@')[0].capitalize()}!</h1>
                <p class="hero-subtitle">Your intelligent partner for efficient candidate screening.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.divider() # New visual divider
        resume_screener_page()
    elif st.session_state.current_page == "top_leaderboard":
        st.header(f"🏆 Top Leaderboard")
        st.markdown(f"Hello, {st.session_state.username}!")
        st.divider()
        leaderboard_page()
    elif st.session_state.current_page == "certificate_verify":
        st.header(f"✅ Certificate Verification")
        st.markdown(f"Hello, {st.session_state.username}!")
        st.divider()
        certificate_verifier_page()
    elif st.session_state.current_page == "total_screened":
        st.header(f"📊 Total Resumes Screened Overview")
        st.markdown(f"Hello, {st.session_state.username}!")
        st.divider()
        total_screened_page()
    elif st.session_state.current_page == "about_us":
        st.header(f"ℹ️ About ScreenerPro")
        st.markdown(f"Hello, {st.session_state.username}!")
        st.divider()
        about_us_page()
    elif st.session_state.current_page == "feedback_form":
        st.header(f"💬 Feedback & Help")
        st.markdown(f"Hello, {st.session_state.username}!")
        st.divider()
        feedback_and_help_page()
    elif st.session_state.current_page == "logout":
        logout_page()

    # Admin Section
    if is_current_user_admin():
        st.sidebar.markdown("---")
        st.sidebar.subheader("Admin Panel")
        admin_tab_selection = st.sidebar.radio(
            "Admin Actions:",
            ("➕ Create User", "🔑 Reset Password", "⛔ Toggle User Status", "👥 View All Users"),
            key="admin_tabs"
        )
        
        st.divider() # Main content divider for admin section
        st.header("⚙️ Admin Management")
        
        if admin_tab_selection == "➕ Create User":
            admin_registration_section()
        elif admin_tab_selection == "🔑 Reset Password":
            admin_password_reset_section()
        elif admin_tab_selection == "⛔ Toggle User Status":
            admin_disable_enable_user_section()
        elif admin_tab_selection == "👥 View All Users":
            st.subheader("👥 All Registered Users:")
            try:
                users_data = load_users()
                if users_data:
                    display_users = []
                    for user, data in users_data.items():
                        hashed_pass = data.get("password", data) if isinstance(data, dict) else data
                        status = data.get("status", "N/A") if isinstance(data, dict) else "N/A"
                        company = data.get("company", "N/A") 
                        display_users.append([user, hashed_pass, status, company]) 
                    st.dataframe(pd.DataFrame(display_users, columns=["Email/Username", "Hashed Password (DO NOT EXPOSE)", "Status", "Company"]), use_container_width=True) 
                else:
                    st.info("No users registered yet.")
            except Exception as e:
                st.error(f"Error loading user data for admin view: {e}")

if __name__ == "__main__":
    main()
