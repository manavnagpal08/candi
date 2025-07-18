import streamlit as st
import json
import bcrypt
import os
import re # Import regex for email validation
import pandas as pd # Ensure pandas is imported for DataFrame display

# Import your page functions
# Ensure these files are in a 'pages' subdirectory relative to app.py
from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from certificate_verify import certificate_verification_page # New import

# --- Functions from your login.py (included directly for simplicity in this single file structure) ---

# File to store user credentials
USER_DB_FILE = "users.json"
# Define your admin usernames here as a tuple of strings
ADMIN_USERNAME = ("admin@forscreenerpro", "admin@forscreenerpro2", "manav.nagpal2005@gmail.com") 

def load_users():
    """Loads user data from the JSON file, handling potential corruption or emptiness."""
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {} # Return empty dict if file was just created

    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
            # Ensure each user has a 'status' key and 'company' key for backward compatibility
            for username, data in users.items():
                if isinstance(data, str): # Old format: "username": "hashed_password"
                    users[username] = {"password": data, "status": "active", "company": "N/A"}
                elif "status" not in data:
                    data["status"] = "active"
                if "company" not in data: # Add company field if missing
                    data["company"] = "N/A"
            return users
    except json.JSONDecodeError:
        # If the file is empty or malformed JSON, re-initialize it
        st.warning(f"⚠️ '{USER_DB_FILE}' is empty or corrupted. Re-initializing with an empty user database.")
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while loading users: {e}")
        return {}


def save_users(users):
    """Saves user data to the JSON file."""
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    """Checks a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def is_valid_email(email):
    """Basic validation for email format."""
    # Regex for a simple email check (covers @ and at least one . after @)
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

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
                users = load_users()
                if new_username in users:
                    st.error("Username already exists. Please choose a different one.")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "status": "active",
                        "company": new_company_name # Store company name
                    }
                    save_users(users)
                    st.success("✅ Registration successful! You can now switch to the 'Login' option.")
                    # Manually set the session state to switch to Login option
                    st.session_state.active_login_tab_selection = "Login"

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
    """Admin-driven password reset form."""
    st.subheader("🔑 Reset User Password (Admin Only)")
    users = load_users()
    # Exclude all admin usernames from the list of users whose passwords can be reset
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
    """Admin-driven user disable/enable form."""
    st.subheader("⛔ Toggle User Status (Admin Only)")
    users = load_users()
    # Exclude all admin usernames from the list of users whose status can be toggled
    user_options = [user for user in users.keys() if user not in ADMIN_USERNAME] 

    if not user_options:
        st.info("No other users to manage status for.")
        return
        
    with st.form("admin_toggle_user_status_form", clear_on_submit=False): # Keep values after submit for easier toggling
        selected_user = st.selectbox("Select User to Toggle Status", user_options, key="toggle_user_select")
        
        current_status = users[selected_user]["status"]
        st.info(f"Current status of '{selected_user}': **{current_status.upper()}**")

        if st.form_submit_button(f"Toggle to {'Disable' if current_status == 'active' else 'Enable'} User"):
            new_status = "disabled" if current_status == "active" else "active"
            users[selected_user]["status"] = new_status
            save_users(users)
            st.success(f"✅ User '{selected_user}' status set to **{new_status.upper()}**.")
            st.rerun() # Rerun to update the displayed status immediately


def login_section():
    """Handles user login and public registration."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    
    # Initialize active_login_tab_selection if not present
    if "active_login_tab_selection" not in st.session_state:
        # Default to 'Register' if no users, otherwise 'Login'
        if not os.path.exists(USER_DB_FILE) or len(load_users()) == 0:
            st.session_state.active_login_tab_selection = "Register"
        else:
            st.session_state.active_login_tab_selection = "Login"


    if st.session_state.authenticated:
        return True

    # Use st.radio to simulate tabs if st.tabs() default_index is not supported
    tab_selection = st.radio(
        "Select an option:",
        ("Login", "Register"),
        key="login_register_radio",
        index=0 if st.session_state.active_login_tab_selection == "Login" else 1
    )

    if tab_selection == "Login":
        st.subheader("🔐 HR Login")
        st.info("If you don't have an account, please go to the 'Register' option first.") # Added instructional message
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
                        st.session_state.user_company = user_data.get("company", "N/A") # Store company name
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
    
    elif tab_selection == "Register": # This will be the initially selected option for new users
        register_section()

    return st.session_state.authenticated

# Helper function to check if the current user is an admin
def is_current_user_admin():
    # Check if the current username is in the ADMIN_USERNAME tuple
    return st.session_state.get("authenticated", False) and st.session_state.get("username") in ADMIN_USERNAME

# --- Candidate Portal Pages (now imported) ---
# The functions resume_screener_page, leaderboard_page, about_us_page, feedback_and_help_page
# are now imported from their respective files in the 'pages' directory.

def logout_page():
    st.title("👋 Logging Out...")
    st.write("You are about to be logged out. Thank you for using ScreenerPro!")
    if st.button("Confirm Logout"):
        st.session_state.authenticated = False
        st.session_state.pop('username', None)
        st.session_state.pop('user_company', None)
        st.session_state.active_login_tab_selection = "Login" # Reset to login tab
        st.rerun()
    st.info("You will be redirected to the login page shortly if you don't confirm.")

def display_greeting_card():
    """
    Displays a beautiful greeting card with the authenticated username.
    This function should be called at the beginning of each page after authentication.
    """
    if st.session_state.get("authenticated") and st.session_state.get("username"):
        st.markdown(
            f"""
            <style>
            @keyframes fadeInScale {{
                from {{ opacity: 0; transform: scale(0.9); }}
                to {{ opacity: 1; transform: scale(1); }}
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
            /* Dark mode adjustments for greeting card */
            .stApp.dark-mode .beautiful-greeting-card {{
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            }}
            .stApp.dark-mode .beautiful-greeting-title {{
                color: #00cec9; /* Match sidebar title color in dark mode */
            }}
            .stApp.dark-mode .beautiful-welcome-text {{
                color: #bbbbbb;
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
                content: '�'; /* Another sparkle */
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

            .beautiful-emoji {{
                font-size: 1.6em; /* Larger, more impactful emojis */
                vertical-align: middle;
                margin: 0 5px;
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
            </div>
            """,
            unsafe_allow_html=True
        )


# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="ScreenerPro Candidate Portal", layout="wide", initial_sidebar_state="expanded")

    # Initialize session state for current page and theme
    if "current_page" not in st.session_state:
        st.session_state.current_page = "resume_screen" # Default page after login
    if "theme" not in st.session_state:
        st.session_state.theme = "light" # Default to light mode

    # Apply global CSS based on theme
    if st.session_state.theme == "dark":
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            html, body, .stApp {
                font-family: 'Inter', sans-serif;
                background-color: #1a1a1a;
                color: #f0f0f0;
            }
            .stApp { /* Add dark-mode class to stApp for conditional styling */
                background-color: #1a1a1a;
                color: #f0f0f0;
            }
            .stApp.dark-mode {
                /* This class will be added by JS below */
            }
            .stSidebar {
                background-color: #262626;
                color: #f0f0f0;
                padding-top: 2rem;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #00cec9; /* Accent color for headers */
            }
            /* Text input, text area, selectbox, etc. */
            .stTextInput>div>div>input,
            .stTextArea>div>div>textarea,
            .stSelectbox>div>div>div>div>span,
            .stMultiSelect>div>div>div>div>span,
            .stSlider .stSliderHandle,
            .stRadio > label > div,
            .stCheckbox > label > div {
                background-color: #3A3A3A !important;
                color: #f0f0f0 !important;
                border: 1px solid #555555 !important;
                border-radius: 0.5rem;
            }
            /* Labels for inputs */
            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stMultiSelect label,
            .stSlider label,
            .stRadio label,
            .stCheckbox label {
                color: #f0f0f0 !important;
                font-weight: 500;
            }
            /* Buttons */
            .stButton>button {
                background-color: #00cec9;
                color: white;
                border: none;
                border-radius: 0.5rem;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                transition: all 0.2s ease-in-out;
            }
            .stButton>button:hover {
                background-color: #00b0a8;
                transform: translateY(-1px);
            }
            /* Expander background */
            .streamlit-expanderHeader {
                background-color: #3A3A3A;
                color: #f0f0f0;
                border-radius: 0.5rem;
                padding: 0.8rem 1rem;
            }
            .streamlit-expanderContent {
                background-color: #2D2D2D;
                color: #f0f0f0;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-top: -0.5rem; /* Overlap with header border-radius */
            }
            /* Info/Success/Error boxes */
            .stAlert {
                background-color: #3A3A3A;
                color: #f0f0f0;
                border-radius: 0.5rem;
            }
            .stAlert > div > div > div > div {
                color: #f0f0f0; /* Text inside alert */
            }
            /* Dataframe styling */
            .stDataFrame {
                border-radius: 0.5rem;
                overflow: hidden; /* Ensures rounded corners are applied */
            }
            /* Metric boxes */
            .stMetric {
                background-color: #2D2D2D;
                border-radius: 0.5rem;
                padding: 1rem;
                border: 1px solid #555555;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Add JS to apply dark-mode class to stApp
        st.markdown(
            """
            <script>
            const body = window.parent.document.querySelector('.stApp');
            if (body) {
                body.classList.add('dark-mode');
            }
            </script>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            html, body, .stApp {
                font-family: 'Inter', sans-serif;
                background-color: #f0f2f6;
                color: #333333;
            }
            .stApp { /* Remove dark-mode class from stApp */
                background-color: #f0f2f6;
                color: #333333;
            }
            .stApp.dark-mode {
                /* This class will be removed by JS below */
            }
            .stSidebar {
                background-color: #ffffff;
                color: #333333;
                padding-top: 2rem;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #00cec9; /* Accent color for headers */
            }
            /* Text input, text area, selectbox, etc. */
            .stTextInput>div>div>input,
            .stTextArea>div>div>textarea,
            .stSelectbox>div>div>div>div>span,
            .stMultiSelect>div>div>div>div>span,
            .stSlider .stSliderHandle,
            .stRadio > label > div,
            .stCheckbox > label > div {
                background-color: #ffffff !important;
                color: #333333 !important;
                border: 1px solid #ccc !important;
                border-radius: 0.5rem;
            }
            /* Labels for inputs */
            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stMultiSelect label,
            .stSlider label,
            .stRadio label,
            .stCheckbox label {
                color: #333333 !important;
                font-weight: 500;
            }
            /* Buttons */
            .stButton>button {
                background-color: #00cec9;
                color: white;
                border: none;
                border-radius: 0.5rem;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                transition: all 0.2s ease-in-out;
            }
            .stButton>button:hover {
                background-color: #00b0a8;
                transform: translateY(-1px);
            }
            /* Expander background */
            .streamlit-expanderHeader {
                background-color: #e0e0e0;
                color: #333333;
                border-radius: 0.5rem;
                padding: 0.8rem 1rem;
            }
            .streamlit-expanderContent {
                background-color: #f8f8f8;
                color: #333333;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-top: -0.5rem; /* Overlap with header border-radius */
            }
            /* Info/Success/Error boxes */
            .stAlert {
                background-color: #ffffff;
                color: #333333;
                border-radius: 0.5rem;
            }
            .stAlert > div > div > div > div {
                color: #333333; /* Text inside alert */
            }
            /* Dataframe styling */
            .stDataFrame {
                border-radius: 0.5rem;
                overflow: hidden; /* Ensures rounded corners are applied */
            }
            /* Metric boxes */
            .stMetric {
                background-color: #ffffff;
                border-radius: 0.5rem;
                padding: 1rem;
                border: 1px solid #ccc;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Add JS to remove dark-mode class from stApp
        st.markdown(
            """
            <script>
            const body = window.parent.document.querySelector('.stApp');
            if (body) {
                body.classList.remove('dark-mode');
            }
            </script>
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
    # This must run first to determine authentication status
    is_authenticated = login_section()

    if not is_authenticated:
        # Only show this message if not authenticated
        st.sidebar.write("---")
        st.sidebar.info("Please log in or register to access the portal features.")
        return # Stop execution if not authenticated

    # --- ONLY RENDER BELOW THIS IF AUTHENTICATED ---
    st.sidebar.title("ScreenerPro Portal") # Moved inside authenticated block

    # Dark Mode Toggle in Sidebar (Moved inside authenticated block)
    st.sidebar.markdown("---")
    dark_mode_checkbox = st.sidebar.checkbox("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    if dark_mode_checkbox:
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.session_state.get('user_company'):
        st.sidebar.info(f"Company: {st.session_state.user_company}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    
    # Navigation buttons (already conditional by being after the return)
    if st.sidebar.button("📄 Resume Screen", key="nav_resume"):
        st.session_state.current_page = "resume_screen"
    if st.sidebar.button("🏆 Top Leaderboard", key="nav_leaderboard"):
        st.session_state.current_page = "top_leaderboard"
    if st.sidebar.button("✅ Verify Certificate", key="nav_certificate_verify"): # New button
        st.session_state.current_page = "certificate_verify"
    if st.sidebar.button("ℹ️ About Us", key="nav_about_us"):
        st.session_state.current_page = "about_us"
    if st.sidebar.button("💬 Feedback Form", key="nav_feedback_form"):
        st.session_state.current_page = "feedback_form"
    
    st.sidebar.markdown("---")
    if st.sidebar.button("➡️ Logout", key="nav_logout"):
        st.session_state.current_page = "logout"
        # Logout logic handled by logout_page function

    # Render the selected page
    if st.session_state.current_page == "resume_screen":
        resume_screener_page()
    elif st.session_state.current_page == "top_leaderboard":
        leaderboard_page()
    elif st.session_state.current_page == "certificate_verify": # New page rendering
        certificate_verification_page()
    elif st.session_state.current_page == "about_us":
        about_us_page()
    elif st.session_state.current_page == "feedback_form":
        feedback_and_help_page()
    elif st.session_state.current_page == "logout":
        logout_page()

    # Admin Section (only visible to admins)
    if is_current_user_admin():
        st.sidebar.markdown("---")
        st.sidebar.subheader("Admin Panel")
        admin_tab_selection = st.sidebar.radio(
            "Admin Actions:",
            ("Create User", "Reset Password", "Toggle User Status", "View All Users"),
            key="admin_tabs"
        )
        
        st.markdown("---") # Separator for admin content in main area
        st.header("Admin Management")
        
        if admin_tab_selection == "Create User":
            admin_registration_section()
        elif admin_tab_selection == "Reset Password":
            admin_password_reset_section()
        elif admin_tab_selection == "Toggle User Status":
            admin_disable_enable_user_section()
        elif admin_tab_selection == "View All Users":
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
