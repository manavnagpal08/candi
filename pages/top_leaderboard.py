import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

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
            cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]))
            firebase_admin.initialize_app(cred, firebase_config)
        
        db = firestore.client()
        return db
    except Exception as e:
        st.error(f"❌ Error initializing Firebase: {e}. Please ensure your Firebase secrets are correctly configured.")
        return None

# Get Firestore DB client
db = initialize_firebase()

# Global variable for app ID (as provided by the environment)
# This assumes __app_id is available in the Streamlit environment.
# If running locally without this, you might need to hardcode a default or set it via env var.
appId = os.environ.get('__app_id', 'default-screener-pro-app')

@st.cache_data(ttl=60) # Cache data for 60 seconds, then re-fetch
def fetch_leaderboard_data():
    """Fetches candidate screening results from Firestore."""
    if db is None:
        st.error("Firestore is not initialized. Cannot fetch data.")
        return pd.DataFrame()

    leaderboard_data = []
    try:
        # Path for public data (accessible by all authenticated users)
        collection_ref = db.collection(f'artifacts/{appId}/public/data/leaderboard')
        
        # Fetch documents
        # IMPORTANT: Firestore queries cannot order by multiple fields or on non-indexed fields
        # without explicit index creation. For simplicity and to avoid index issues,
        # we will fetch all and sort in Python.
        docs = collection_ref.stream()
        
        for doc in docs:
            data = doc.to_dict()
            # Ensure all expected fields are present, provide defaults if missing
            leaderboard_data.append({
                "Candidate Name": data.get("Candidate Name", "N/A"),
                "Score (%)": data.get("Score (%)", 0.0),
                "Years Experience": data.get("Years Experience", 0.0),
                "CGPA (4.0 Scale)": data.get("CGPA (4.0 Scale)", None),
                "JD Used": data.get("JD Used", "N/A"),
                "Date Screened": data.get("Date Screened", datetime.now().strftime("%Y-%m-%d")),
                "Certificate Rank": data.get("Certificate Rank", "N/A"),
                "Tag": data.get("Tag", "N/A"),
                "Certificate ID": data.get("Certificate ID", "N/A") # Include Certificate ID for potential future use
            })
        
        df = pd.DataFrame(leaderboard_data)
        # Convert 'Date Screened' to datetime objects for proper sorting
        df['Date Screened'] = pd.to_datetime(df['Date Screened'])
        # Sort by score in descending order by default
        df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching leaderboard data: {e}")
        return pd.DataFrame()

def leaderboard_page():
    st.title("🏆 ScreenerPro Leaderboard")
    st.markdown("### Top Candidates by Screening Score")
    st.caption("View the highest-scoring candidates across various job descriptions.")

    if db is None:
        st.warning("Firebase is not configured. Leaderboard data cannot be displayed.")
        return

    # Add a refresh button
    if st.button("🔄 Refresh Leaderboard Data"):
        st.cache_data.clear() # Clear cache to force refetch immediately
        st.rerun()

    leaderboard_df = fetch_leaderboard_data()

    if leaderboard_df.empty:
        st.info("No candidate data available yet. Upload resumes on the main Screener page to populate the leaderboard.")
        return

    # Filters
    st.sidebar.header("📊 Filter Leaderboard")
    
    # Filter by Job Description
    unique_jds = ["All"] + sorted(leaderboard_df["JD Used"].unique())
    selected_jd = st.sidebar.selectbox("Filter by Job Description", unique_jds)

    # Filter by Minimum Score
    min_score_filter = st.sidebar.slider("Minimum Score (%)", 0, 100, 0)

    # Filter by Minimum Experience
    min_exp_filter = st.sidebar.slider("Minimum Experience (Years)", 0, 15, 0)

    # Apply filters
    filtered_df = leaderboard_df.copy()
    if selected_jd != "All":
        filtered_df = filtered_df[filtered_df["JD Used"] == selected_jd]
    
    filtered_df = filtered_df[filtered_df["Score (%)"] >= min_score_filter]
    filtered_df = filtered_df[filtered_df["Years Experience"] >= min_exp_filter]

    if filtered_df.empty:
        st.info("No candidates match the selected filters.")
    else:
        st.dataframe(
            filtered_df[[
                "Candidate Name", 
                "Score (%)", 
                "Years Experience", 
                "CGPA (4.0 Scale)", 
                "JD Used", 
                "Date Screened", 
                "Certificate Rank", 
                "Tag"
            ]].style.format({
                "Score (%)": "{:.2f}",
                "Years Experience": "{:.1f}",
                "CGPA (4.0 Scale)": lambda x: f"{x:.2f}" if pd.notna(x) else "N/A",
                "Date Screened": lambda x: x.strftime("%Y-%m-%d")
            }),
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    leaderboard_page()
