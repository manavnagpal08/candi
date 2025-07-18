import streamlit as st

def resume_screen_page():
    st.title("📄 Resume Screen")
    st.write(f"Welcome, {st.session_state.username}! This is your personal resume management area.")
    st.write("Here you can upload, view, and edit your resume.")
    
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.info("Note: In a real application, this file would be saved to a database or cloud storage.")

    st.subheader("Your Stored Resumes")
    st.write("No resumes uploaded yet. Upload one above!")
