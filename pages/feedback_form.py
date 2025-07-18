import streamlit as st
import pandas as pd # For pd.Timestamp.now()

def feedback_form_page():
    st.title("💬 Feedback Form")
    st.write("We value your input! Please share your thoughts, suggestions, or report any issues you've encountered.")
    
    with st.form("feedback_form", clear_on_submit=True):
        feedback_type = st.radio("Type of Feedback:", ("Suggestion", "Bug Report", "General Comment", "Feature Request"))
        subject = st.text_input("Subject")
        message = st.text_area("Your Feedback", height=150)
        email_contact = st.text_input("Your Email (Optional, for follow-up)", value=st.session_state.username if st.session_state.authenticated else "")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if not subject or not message:
                st.error("Please fill in the Subject and Your Feedback fields.")
            else:
                st.success("Thank you for your feedback! We appreciate your contribution.")
                st.json({
                    "feedback_type": feedback_type,
                    "subject": subject,
                    "message": message,
                    "email_contact": email_contact,
                    "user": st.session_state.username,
                    "timestamp": pd.Timestamp.now().isoformat()
                })
                st.info("This feedback has been logged (simulated).")
