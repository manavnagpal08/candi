import streamlit as st

# Session state defaults
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Login"
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

def login_section():
    # ---------- Styles ---------- #
    st.markdown("""
        <style>
            .tab-container {
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin-bottom: 2rem;
            }
            .tab-button {
                padding: 0.6rem 2rem;
                border-radius: 999px;
                background-color: #f0f2f6;
                border: none;
                color: #333;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .tab-button.active {
                background-color: #2c8cff;
                color: white;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            }
            .tab-button:hover {
                background-color: #dbeeff;
            }
            .form-box {
                background-color: white;
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                max-width: 500px;
                margin: auto;
            }
            .forgot-link {
                color: #2c8cff;
                font-weight: 500;
                font-size: 14px;
                text-align: right;
                margin-top: -1.2rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------- Tab Header ---------- #
    st.markdown("<div class='tab-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login"):
            st.session_state.active_tab = "Login"
            st.session_state.show_reset = False
    with col2:
        if st.button("Register"):
            st.session_state.active_tab = "Register"
            st.session_state.show_reset = False
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Login Form ---------- #
    if st.session_state.active_tab == "Login":
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            colA, colB = st.columns([2, 1])
            login_btn = colA.form_submit_button("Login")
            forgot_btn = colB.form_submit_button("Forgot Password?")

        if login_btn:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                st.success("(Simulated) Logged in as " + email)

        if forgot_btn:
            st.session_state.show_reset = True

        if st.session_state.show_reset:
            st.divider()
            st.markdown("#### 🔁 Reset Your Password")
            reset_email = st.text_input("Enter your registered email")
            if st.button("Send Reset Link"):
                if "@" not in reset_email:
                    st.error("Please enter a valid email address.")
                else:
                    st.success("Reset link sent to " + reset_email)
                    st.info("Check your Spam/Junk folder if you don't see the email.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Register Form ---------- #
    elif st.session_state.active_tab == "Register":
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        st.markdown("### 📝 Create Your Account")
        with st.form("register_form"):
            reg_email = st.text_input("Email")
            reg_company = st.text_input("Company")
            reg_password = st.text_input("Password", type="password")
            reg_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")

        if submit:
            if not reg_email or not reg_password or not reg_company:
                st.error("All fields are required.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                st.success("(Simulated) Registered successfully for " + reg_email)
        st.markdown("</div>", unsafe_allow_html=True)

# To use this in main.py or another file:
# from auth_ui import login_section
# login_section()
