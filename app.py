import streamlit as st
import json
import bcrypt
import os
import re # Import regex for email validation
import pandas as pd # Ensure pandas is imported for DataFrame display
from pages.certificate_verify import certificate_verifier_page
# Import your page functions from separate files
from resume_screen import resume_screener_page
from top_leaderboard import leaderboard_page
from about_us import about_us_page
from feedback_form import feedback_and_help_page
from certificate_verify import certificate_verifier_page
from total_screened_page import total_screened_page

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
    Sets a class on the body element based on the Streamlit theme
    to enable light/dark mode styling.
    """
    is_dark = st.get_option("theme.base") == "dark"
    body_class = "dark-mode" if is_dark else "light-mode"
    # Inject JavaScript to add the class to the body tag of the parent window
    js_code = f"""
    <script>
        var body = window.parent.document.querySelector('body');
        if (body) {{
            body.className = ''; // Clear existing classes
            body.classList.add('{body_class}'); // Add the new class
            // Also set a data-theme attribute for CSS targeting
            body.setAttribute('data-theme', '{'dark' if is_dark else 'light'}');
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


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

def is_current_user_admin():
    """Checks if the currently logged-in user is an admin."""
    return st.session_state.get("username") in ADMIN_USERNAME

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
                    st.success("✅ Registration successful! You are now logged in.")

                    # Automatically log in the user
                    st.session_state.authenticated = True
                    st.session_state.username = new_username
                    st.session_state.user_company = new_company_name
                    st.session_state.current_page = "resume_screen" # Redirect to Resume Screener after registration
                    st.rerun() # Rerun to apply the login and redirect

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


# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="ScreenerPro Candidate Portal", layout="wide", initial_sidebar_state="expanded")

    # Initialize session state for current page and theme
    if "current_page" not in st.session_state:
        st.session_state.current_page = "resume_screen" # Default page after login, changed from Dashboard
    if "theme" not in st.session_state:
        st.session_state.theme = "light" # Default to light mode

    # Load the external CSS file
    load_css("style.css")

    # Set the body class based on the current theme
    # This needs to be called after load_css and theme is set
    set_body_class()

    # Ensure all admin users exist for testing/initial setup
    users = load_users()
    default_admin_password = "adminpass"
    for admin_user in ADMIN_USERNAME:
        if admin_user not in users:
            users[admin_user] = {"password": bcrypt.hashpw(default_admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "status": "active", "company": "AdminCo"}
            st.sidebar.info(f"Created default admin user: {admin_user} with password '{default_admin_password}'")
    save_users(users)

    # Authentication section
    is_authenticated = login_section()

    if not is_authenticated:
        st.sidebar.write("---")
        st.sidebar.info("Please log in or register to access the portal features.")
        return # Stop execution if not authenticated

    # --- ONLY RENDER BELOW THIS IF AUTHENTICATED ---
    # Sidebar Dark Mode Toggle
    with st.sidebar:
        # Streamlit's native toggle widget for Dark Mode
        st.toggle("Dark Mode", value=(st.session_state.theme == "dark"), key="sidebar_dark_mode_toggle")
        if st.session_state.sidebar_dark_mode_toggle:
            if st.session_state.theme != "dark":
                st.session_state.theme = "dark"
                st.rerun()
        else:
            if st.session_state.theme != "light":
                st.session_state.theme = "light"
                st.rerun()

        # Logo and Name as seen in image
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        logo_path = "screenerpro_logo.png" # Assuming logo is in the same directory
        if os.path.exists(logo_path):
            st.image(logo_path, width=35)
        else:
            st.markdown(f'<img src="https://placehold.co/35x35/00cec9/ffffff?text=SP" alt="ScreenerPro Logo" style="height:35px; object-fit:contain;">', unsafe_allow_html=True)
        st.markdown('<span>ScreenerPro</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<p>Navigate</p>", unsafe_allow_html=True)

        # Navigation Buttons (using st.button and wrapping in custom div for styling)
        # Removed Dashboard Button as requested

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
                ("Create User", "Reset Password", "Toggle User Status", "View All Users"),
                key="admin_tabs"
            )

    # --- Main Content Area ---
    # The main content area will change based on the selected sidebar page

    # New Beautiful Greeting Card
    if st.session_state.get("authenticated") and st.session_state.get("username"):
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


    # The Dashboard content block is removed as requested
    # if st.session_state.current_page == "Dashboard":
    #     # ... (Dashboard content) ...

    if st.session_state.current_page == "resume_screen":
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
        elif st.session_state.get("admin_tabs") == "View All Users":
            st.subheader("👥 All Registered Users:")
            try:
                users_data = load_users()
                if users_data:
                    display_users = []
                    for user, data in users_data.items():
                        # Ensure data is a dictionary before accessing keys
                        hashed_pass = data.get("password", "") if isinstance(data, dict) else data
                        status = data.get("status", "N/A") if isinstance(data, dict) else "N/A"
                        company = data.get("company", "N/A") if isinstance(data, dict) else "N/A"
                        display_users.append([user, hashed_pass, status, company])
                    st.dataframe(pd.DataFrame(display_users, columns=["Email/Username", "Hashed Password (DO NOT EXPOSE)", "Status", "Company"]), use_container_width=True)
                else:
                    st.info("No users registered yet.")
            except Exception as e:
                st.error(f"Error loading user data for admin view: {e}")

if __name__ == "__main__":
    main()
