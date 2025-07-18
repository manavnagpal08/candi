import streamlit as st
import requests
from datetime import datetime # Import datetime for logging

# --- Logging Function ---
def log_user_action(user_email, action, details=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if details:
        print(f"LOG: [{timestamp}] User '{user_email}' performed action '{action}' with details: {details}")
    else:
        print(f"LOG: [{timestamp}] User '{user_email}' performed action '{action}'")

# --- Feedback Page Function ---
def feedback_and_help_page():
    user_email = st.session_state.get('user_email', 'anonymous')
    log_user_action(user_email, "FEEDBACK_HELP_PAGE_ACCESSED")

    # Access dark_mode from session state, defaulting to False if not set
    dark_mode = st.session_state.get('dark_mode_main', False)

    st.markdown(f"""
    <style>
    .feedback-container {{
        background-color: {'#2D2D2D' if dark_mode else 'rgba(255, 255, 255, 0.96)'};
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0px 8px 20px rgba(0,0,0,{'0.2' if dark_mode else '0.1'});
        animation: fadeIn 0.8s ease-in-out;
        color: {'#E0E0E0' if dark_mode else '#333333'};
    }}
    .feedback-header {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {'#00cec9' if dark_mode else '#00cec9'};
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00cec9;
        display: inline-block;
        margin-bottom: 1.5rem;
    }}
    .feedback-caption {{
        font-size: 1.1em;
        color: {'#BBBBBB' if dark_mode else '#555555'};
        margin-bottom: 2rem;
    }}
    .stTextInput>div>div>input, .stTextArea>div>div {{
        background-color: {'#3A3A3A' if dark_mode else '#f0f2f6'};
        color: {'#E0E0E0' if dark_mode else '#333333'};
        border-radius: 8px;
        border: 1px solid {'#555555' if dark_mode else '#ccc'};
        padding: 0.75rem;
    }}
    .stTextInput>label, .stTextArea>label {{
        color: {'#E0E0E0' if dark_mode else '#333333'};
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    .stButton>button {{
        background-color: #00cec9;
        color: white;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }}
    .stButton>button:hover {{
        background-color: #00b0a8;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
    st.markdown('<div class="feedback-header">❓ Feedback & Help</div>', unsafe_allow_html=True)
    st.markdown('<p class="feedback-caption">We value your input! Please use the form below to send us your feedback, questions, or report any issues. Your insights help us improve ScreenerPro.</p>', unsafe_allow_html=True)

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            feedback_name = st.text_input("Your Name (Optional)", key="feedback_name", placeholder="e.g., John Doe")
        with col2:
            feedback_email = st.text_input("Your Email (Optional)", key="feedback_email", placeholder="e.g., your.email@example.com")
        
        feedback_subject = st.text_input("Subject", "Feedback on ScreenerPro", key="feedback_subject", placeholder="e.g., Feature Request, Bug Report, General Inquiry")
        feedback_message = st.text_area("Your Message", height=180, key="feedback_message", placeholder="Type your message here...")
        
        submit_button = st.form_submit_button("🚀 Send Feedback")

        if submit_button:
            if not feedback_message.strip():
                st.error("❌ Please enter your message before sending feedback.")
                log_user_action(user_email, "FEEDBACK_SUBMIT_FAILED", {"reason": "Empty message"})
            else:
                # ✅ Send to Formspree
                formspree_url = "https://formspree.io/f/mwpqevno"  # Your endpoint
                payload = {
                    "name": feedback_name,
                    "email": feedback_email,
                    "subject": feedback_subject,
                    "message": feedback_message
                }

                response = requests.post(formspree_url, data=payload)

                if response.status_code == 200:
                    st.success("✅ Thank you! Your feedback has been submitted successfully. We'll get back to you soon if a response is needed.")
                    log_user_action(user_email, "FEEDBACK_SUBMITTED_FORMSPREE", {"subject": feedback_subject})
                else:
                    st.error(f"⚠️ Something went wrong (Status: {response.status_code}). Please try again later. If the problem persists, please contact support directly.")
                    log_user_action(user_email, "FEEDBACK_SUBMIT_FAILED", {"status": response.status_code, "response_text": response.text})

    st.markdown("</div>", unsafe_allow_html=True)
