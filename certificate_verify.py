import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os
import traceback # Import traceback for detailed error logging

# Initialize Firebase (only once)
@st.cache_resource
def initialize_firebase():
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # Use Streamlit secrets for Firebase configuration
            firebase_config = {
                "apiKey": st.secrets["FIREBASE_API_KEY"],
                "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
                "projectId": st.secrets["FIREBASE_PROJECT_ID"],
                "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
                "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
                "appId": st.secrets["FIREBASE_APP_ID"],
                "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"]
            }
            # Load service account key from secrets
            service_account_key_json = st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]
            cred = credentials.Certificate(json.loads(service_account_key_json))
            firebase_admin.initialize_app(cred, firebase_config)
        
        db = firestore.client()
        return db
    except Exception as e:
        st.error(f"❌ Error initializing Firebase: {e}")
        st.error(f"Traceback: {traceback.format_exc()}") # Print full traceback for debugging
        st.info("Please ensure ALL Firebase secrets (API Key, Auth Domain, Project ID, etc., and the Service Account Key JSON) are correctly configured in your secrets.toml or Streamlit Cloud secrets.")
        return None

# Get Firestore DB client
db = initialize_firebase()

# Global variable for app ID (as provided by the environment)
# Note: appId is not directly used in the collection path here, as per the new rules
# and user's Firestore structure which places 'leaderboard' at the root.
appId = os.environ.get('__app_id', 'default-screener-pro-app')

def certificate_verifier_page():
    st.title("✅ ScreenerPro Certificate Verification")
    st.markdown("### Verify the authenticity of a ScreenerPro Certificate.")

    if db is None:
        st.warning("Firebase is not configured. Certificate verification is unavailable.")
        return

    certificate_id_input = st.text_input(
        "Enter Certificate ID",
        placeholder="e.g., a1b2c3d4-e5f6-7890-1234-567890abcdef",
        help="Paste the unique Certificate ID found on the ScreenerPro certificate."
    )

    if st.button("🔍 Verify Certificate"):
        if not certificate_id_input:
            st.warning("Please enter a Certificate ID to verify.")
            return

        with st.spinner(f"Verifying certificate ID: {certificate_id_input}..."):
            try:
                # Corrected: Access 'leaderboard' collection directly at the root
                doc_ref = db.collection('leaderboard').document(certificate_id_input)
                doc = doc_ref.get()

                if doc.exists:
                    certificate_data = doc.to_dict()
                    st.success("Certificate Found and Verified!")
                    st.markdown("---")
                    st.markdown("#### Certificate Details:")
                    
                    st.write(f"**Candidate Name:** {certificate_data.get('Candidate Name', 'N/A')}")
                    st.write(f"**Score (%):** {certificate_data.get('Score (%)', 0.0):.2f}%")
                    st.write(f"**Years Experience:** {certificate_data.get('Years Experience', 0.0):.1f} years")
                    
                    cgpa_display = f"{certificate_data.get('CGPA (4.0 Scale)', None):.2f}" if pd.notna(certificate_data.get('CGPA (4.0 Scale)', None)) else "N/A"
                    st.write(f"**CGPA (4.0 Scale):** {cgpa_display}")
                    
                    st.write(f"**Job Description Used:** {certificate_data.get('JD Used', 'N/A')}")
                    st.write(f"**Date Screened:** {certificate_data.get('Date Screened', 'N/A')}")
                    st.write(f"**Certificate Rank:** {certificate_data.get('Certificate Rank', 'N/A')}")
                    st.write(f"**Tag:** {certificate_data.get('Tag', 'N/A')}")
                    st.write(f"**Certificate ID:** `{certificate_data.get('Certificate ID', 'N/A')}`")

                    st.markdown("---")
                    st.info("This certificate is authentic and was issued by ScreenerPro.")
                else:
                    st.error("Certificate not found. Please check the ID and try again.")
                    st.info("The provided Certificate ID does not match any records in our system. It might be incorrect, or the certificate may not exist.")

            except Exception as e:
                st.error(f"❌ An error occurred during verification: {e}")
                st.error(f"Traceback: {traceback.format_exc()}") # Print full traceback for debugging
                st.info("Please ensure your Firebase configuration is correct and the Certificate ID is valid.")

if __name__ == "__main__":
    certificate_verifier_page()
