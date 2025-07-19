import streamlit as st
import os

# Function to load CSS from a file
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: CSS file '{file_name}' not found. Make sure it's in the same directory as your app.py.")

# Function to inject custom HTML for body class
def set_body_class(class_name):
    # This script adds/removes a class from the body tag
    # using JavaScript, which is executed when Streamlit renders the markdown.
    js_code = f"""
    <script>
        var body = window.parent.document.querySelector('body');
        if (body) {{
            body.className = ''; // Clear existing classes
            body.classList.add('{class_name}'); // Add the new class
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="ScreenerPro Candidate Portal",
        layout="wide",
        initial_sidebar_state="expanded",
        # Updated Favicon URL
        page_icon="https://raw.githubusercontent.com/manavnagpal08/candi/3b4afa84eed486bc2f70ffe8dc224f0a6a5f30894/logo.png"
    )

    if "current_page" not in st.session_state:
        st.session_state.current_page = "resume_screen"
    if "theme" not in st.session_state:
        st.session_state.theme = "light" # Default to light mode

    # Load the external CSS file once
    load_css("style.css")

    # Set the body class based on the current theme
    if st.session_state.theme == "dark":
        set_body_class("dark-mode")
    else:
        set_body_class("light-mode") # You might not strictly need 'light-mode' class if it's the default, but it's good practice for clarity.

    # Theme toggle in the sidebar
    with st.sidebar:
        st.title("ScreenerPro")
        # Toggle button for theme
        if st.session_state.theme == "light":
            if st.button("🌙 Dark Mode"):
                st.session_state.theme = "dark"
                st.rerun() # Rerun to apply new theme
        else:
            if st.button("☀️ Light Mode"):
                st.session_state.theme = "light"
                st.rerun() # Rerun to apply new theme

        # Display user info if logged in (placeholder)
        if st.session_state.get('logged_in_user'):
            st.markdown(f"""
            <div class="sidebar-user-info">
                Welcome, <strong>{st.session_state.logged_in_user['username']}</strong>!<br>
                Role: {st.session_state.logged_in_user['role'].capitalize()}
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.header("Navigation")
        # Navigation buttons
        if st.button("📄 Resume Screening", key="nav_resume_screen"):
            st.session_state.current_page = "resume_screen"
        if st.button("📊 Analytics Dashboard", key="nav_analytics"):
            st.session_state.current_page = "analytics"
        if st.session_state.get('logged_in_user') and st.session_state.logged_in_user.get('role') == 'hr':
            if st.button("⭐ HR Portal", key="nav_hr_portal", help="Access HR-specific features"):
                st.session_state.current_page = "hr_portal"
        if st.button("⚙️ Settings", key="nav_settings"):
            st.session_state.current_page = "settings"
        if st.button("🚪 Logout", key="nav_logout"):
            # Clear session state on logout
            st.session_state.clear()
            st.session_state.current_page = "login" # Redirect to login
            st.rerun()

    # Main content rendering based on current_page
    if st.session_state.current_page == "login":
        render_login_register()
    elif st.session_state.current_page == "resume_screen":
        if not st.session_state.get('logged_in_user'):
            st.warning("Please login to access the resume screening feature.")
            render_login_register()
        else:
            render_resume_screen()
    elif st.session_state.current_page == "analytics":
        if not st.session_state.get('logged_in_user'):
            st.warning("Please login to access the analytics dashboard.")
            render_login_register()
        else:
            render_analytics_dashboard()
    elif st.session_state.current_page == "hr_portal":
        if not (st.session_state.get('logged_in_user') and st.session_state.logged_in_user.get('role') == 'hr'):
            st.warning("You do not have permission to access the HR Portal. Please login as an HR.")
            render_login_register()
        else:
            render_hr_portal()
    elif st.session_state.current_page == "settings":
        if not st.session_state.get('logged_in_user'):
            st.warning("Please login to access settings.")
            render_login_register()
        else:
            render_settings()

# Define your other rendering functions (render_login_register, render_resume_screen, etc.) here
# ... (These functions would contain the actual Streamlit UI elements for each page) ...
def render_login_register():
    st.markdown("<h1 class='hero-title'>Welcome to ScreenerPro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Your ultimate AI-powered candidate screening solution.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_button"):
                # Simple authentication (replace with actual backend/DB lookup)
                if username == "user" and password == "pass":
                    st.session_state.logged_in_user = {"username": username, "role": "candidate"}
                    st.success("Logged in successfully as Candidate!")
                    st.session_state.current_page = "resume_screen"
                    st.rerun()
                elif username == "hr" and password == "hrpass":
                    st.session_state.logged_in_user = {"username": username, "role": "hr"}
                    st.success("Logged in successfully as HR!")
                    st.session_state.current_page = "hr_portal"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with col2:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True) # Spacer
            st.info("Hint: Try 'user' / 'pass' for Candidate or 'hr' / 'hrpass' for HR")

    with tab2:
        st.header("Register")
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
        role = st.selectbox("Register as", ["Candidate", "HR"], key="register_role")

        if st.button("Register", key="register_button"):
            if new_password == confirm_password:
                # In a real app, you'd save this to a database
                st.success(f"User '{new_username}' registered as {role.lower()}. Please login.")
                st.session_state.current_page = "login"
                st.rerun()
            else:
                st.error("Passwords do not match.")

def render_resume_screen():
    st.markdown("<h1 class='hero-title'>Resume Screening</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Upload a resume and job description for AI-powered matching.</p>", unsafe_allow_html=True)

    st.warning("This is a placeholder for the Resume Screening feature.")
    st.write("Upload your resume (PDF) and provide a job description. Our AI will analyze and score the match.")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Job Description", height=200, placeholder="Paste your job description here...")

    if uploaded_file and job_description:
        st.success("Files uploaded and job description provided. Processing...")
        # Placeholder for AI processing
        with st.spinner("Analyzing resume and job description..."):
            import time
            time.sleep(3) # Simulate processing time
        st.info("Analysis complete! (Detailed results would appear here)")
        st.metric(label="Match Score", value="85%", delta="Excellent Match!")
        st.json({"Extracted Skills": ["Python", "Machine Learning", "Data Analysis"], "Missing Skills": ["Cloud Computing"]})


def render_analytics_dashboard():
    st.markdown("<h1 class='hero-title'>Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Insights into your candidate pipeline and screening performance.</p>", unsafe_allow_html=True)

    st.warning("This is a placeholder for the Analytics Dashboard.")
    st.write("Here you would see charts and graphs related to candidate demographics, screening efficiency, skill gaps, etc.")

    st.metric("Total Candidates Processed", "1,234")
    st.metric("Average Match Score", "72%", "📈 +5% from last month")

    st.subheader("Candidate Status Distribution")
    # Placeholder for a bar chart
    st.bar_chart({"Applied": 500, "Screened": 300, "Interviewed": 150, "Hired": 50})

    st.subheader("Top Skills Identified")
    # Placeholder for a table or list
    st.dataframe({"Skill": ["Python", "SQL", "Project Management", "Communication"], "Count": [800, 650, 400, 700]})


def render_hr_portal():
    st.markdown("<h1 class='hero-title'>HR Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Exclusive tools for HR professionals.</p>", unsafe_allow_html=True)

    st.success("Welcome to the HR Portal! This is only visible to HR users.")
    st.write("This section could include features like managing job postings, reviewing all candidates, setting screening criteria, etc.")

    st.subheader("Manage Job Postings")
    job_title = st.text_input("New Job Title")
    job_desc = st.text_area("New Job Description (for AI screening)")
    if st.button("Create Job Posting"):
        st.info(f"Job '{job_title}' created. (Placeholder: In a real app, this would be saved).")

    st.subheader("View All Candidates")
    st.dataframe({
        "Candidate Name": ["Alice", "Bob", "Charlie"],
        "Last Scored Job": ["Software Engineer", "Data Scientist", "Product Manager"],
        "Match Score": ["92%", "78%", "85%"],
        "Status": ["Interviewing", "Screened", "Hired"]
    })

def render_settings():
    st.markdown("<h1 class='hero-title'>Settings</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Adjust your application preferences.</p>", unsafe_allow_html=True)

    st.warning("This is a placeholder for user settings.")

    st.subheader("Account Settings")
    st.text_input("Email", value="user@example.com")
    st.text_input("Change Password", type="password")
    if st.button("Update Account"):
        st.success("Account settings updated.")

    st.subheader("Notification Preferences")
    st.checkbox("Receive email notifications for new matches", value=True)
    st.checkbox("Receive daily summary reports")
    if st.button("Save Preferences"):
        st.success("Notification preferences saved.")


if __name__ == "__main__":
    main()
