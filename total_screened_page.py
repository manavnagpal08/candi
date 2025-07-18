import streamlit as st
import requests
import json
import os
import time

def total_screened_page():
    st.title("📊 Total Resumes Screened")
    st.markdown("This page displays the cumulative count of resumes that have been screened through ScreenerPro.")

    # Fetch Firebase secrets
    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
    except KeyError as e:
        st.error(f"❌ Firebase configuration error: Missing secret key '{e}'.")
        st.info("Please ensure 'FIREBASE_PROJECT_ID' and 'FIREBASE_API_KEY' are correctly set in your secrets.toml or Streamlit Cloud secrets.")
        return

    # Firestore collection path where screening results are stored
    # This should match the collection used in resume_screen.py for saving results
    collection_id = "leaderboard" # Assuming results are saved to 'leaderboard' collection

    # Firestore REST API endpoint for listing documents in a collection
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}"

    st.markdown("---")

    # Button to refresh the count
    if st.button("🔄 Refresh Count"):
        st.session_state['refresh_count'] = True

    if 'total_resumes_screened' not in st.session_state or st.session_state.get('refresh_count', False):
        st.session_state['refresh_count'] = False # Reset refresh flag

        with st.spinner("Fetching total screened resumes from Firestore..."):
            try:
                start_time = time.time()
                response = requests.get(url)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                
                data = response.json()
                
                # Firestore REST API returns documents in a 'documents' array
                # If no documents, 'documents' key might be missing or empty
                total_count = len(data.get('documents', []))
                st.session_state['total_resumes_screened'] = total_count
                
                end_time = time.time()
                st.success(f"Data fetched successfully in {end_time - start_time:.2f} seconds.")

            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Failed to fetch data from Firestore: HTTP Error {e.response.status_code}")
                st.error(f"Response: {e.response.text}")
                st.warning("This often indicates an issue with Firestore security rules (e.g., read access denied) or incorrect API key/project ID.")
                st.session_state['total_resumes_screened'] = "Error"
            except Exception as e:
                st.error(f"❌ An unexpected error occurred while fetching data: {e}")
                st.exception(e)
                st.session_state['total_resumes_screened'] = "Error"
    
    if isinstance(st.session_state['total_resumes_screened'], int):
        st.markdown(f"""
        <div style="
            background-color: #e0f7fa;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <h2 style="color: #007c91; font-size: 2.5em; margin-bottom: 10px;">
                Total Resumes Screened:
            </h2>
            <p style="color: #003049; font-size: 4em; font-weight: bold; margin: 0;">
                {st.session_state['total_resumes_screened']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state['total_resumes_screened'] == "Error":
        st.warning("Could not retrieve the total count. Please check the error messages above.")
    else:
        st.info("Click 'Refresh Count' to load the total number of resumes screened.")

# This allows the page to be run directly for testing, but typically it's imported by app.py
if __name__ == "__main__":
    st.set_page_config(page_title="Total Resumes Screened", layout="centered")
    total_screened_page()
