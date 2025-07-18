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
    """
    Initializes the Firebase Admin SDK.
    This function is cached to ensure Firebase is initialized only once per app run.
    """
    try:
        # Check if Firebase app is already initialized to prevent re-initialization errors
        if not firebase_admin._apps:
            # Load Firebase configuration from Streamlit secrets
            firebase_config = {
                "apiKey": st.secrets["FIREBASE_API_KEY"],
                "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
                "projectId": st.secrets["FIREBASE_PROJECT_ID"],
                "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
                "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
                "appId": st.secrets["FIREBASE_APP_ID"],
                "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"]
            }
            # Load service account key from secrets. It must be a JSON string.
            cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]))
            firebase_admin.initialize_app(cred, firebase_config)
        
        # Return the Firestore client instance
        db = firestore.client()
        return db
    except KeyError as e:
        st.error(f"❌ Firebase initialization error: Missing secret key '{e}'.")
        st.info("Please ensure all Firebase configuration keys (apiKey, authDomain, projectId, etc., and FIREBASE_SERVICE_ACCOUNT_KEY) are correctly set in your secrets.toml or Streamlit Cloud secrets.")
        return None
    except json.JSONDecodeError:
        st.error("❌ Firebase initialization error: 'FIREBASE_SERVICE_ACCOUNT_KEY' is not a valid JSON string.")
        st.info("Ensure the service account key in your secrets is a single-line JSON string.")
        return None
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during Firebase initialization: {e}")
        st.info("Check your Firebase project settings and Streamlit secrets for any misconfigurations.")
        return None

# Get Firestore DB client globally (initialized once)
db = initialize_firebase()

# Global variable for app ID (as provided by the environment)
# This assumes __app_id is available in the Streamlit environment.
# If running locally without this, you might need to hardcode a default or set it via env var.
appId = os.environ.get('__app_id', 'default-screener-pro-app')

@st.cache_data(ttl=60) # Cache data for 60 seconds to reduce Firestore reads
def fetch_leaderboard_data():
    """
    Fetches candidate screening results from Firestore.
    Data is fetched from a public collection path.
    """
    if db is None:
        st.error("Firestore is not initialized. Cannot fetch data.")
        return pd.DataFrame()

    leaderboard_data = []
    try:
        # Define the collection reference for public data
        # This path adheres to the public data storage convention: /artifacts/{appId}/public/data/{your_collection_name}
        collection_ref = db.collection(f'artifacts/{appId}/public/data/leaderboard')
        
        # Stream documents from the collection.
        # Note: Firestore queries do not support ordering by multiple fields or on non-indexed fields
        # without explicit index creation. For simplicity, we fetch all and sort in Python.
        docs = collection_ref.stream()
        
        for doc in docs:
            data = doc.to_dict()
            # Append data to the list, providing default values for robustness
            leaderboard_data.append({
                "Candidate Name": data.get("Candidate Name", "N/A"),
                "Score (%)": data.get("Score (%)", 0.0),
                "Years Experience": data.get("Years Experience", 0.0),
                "CGPA (4.0 Scale)": data.get("CGPA (4.0 Scale)", None),
                "JD Used": data.get("JD Used", "N/A"),
                # Convert date string back to datetime object for proper sorting/display
                "Date Screened": pd.to_datetime(data.get("Date Screened", datetime.now().strftime("%Y-%m-%d"))),
                "Certificate Rank": data.get("Certificate Rank", "N/A"),
                "Tag": data.get("Tag", "N/A"),
                "Certificate ID": data.get("Certificate ID", "N/A") # Include Certificate ID
            })
        
        df = pd.DataFrame(leaderboard_data)
        # Sort the DataFrame by "Score (%)" in descending order
        df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching leaderboard data: {e}")
        st.info("Ensure your Firestore security rules allow read access to 'artifacts/{appId}/public/data/leaderboard'.")
        return pd.DataFrame()

def leaderboard_page():
    """
    Displays the ScreenerPro Leaderboard page in Streamlit.
    Fetches and filters candidate data from Firestore.
    """
    st.title("🏆 ScreenerPro Leaderboard")
    st.markdown("### Top Candidates by Screening Score")
    st.caption("View the highest-scoring candidates across various job descriptions.")

    # Check if Firebase is initialized before proceeding
    if db is None:
        st.warning("Firebase is not configured. Leaderboard data cannot be displayed.")
        return

    # Add a refresh button to allow users to get the latest data
    if st.button("🔄 Refresh Leaderboard Data"):
        st.cache_data.clear() # Clear the cache to force a fresh data fetch
        st.rerun() # Rerun the app to apply changes

    # Fetch the leaderboard data
    leaderboard_df = fetch_leaderboard_data()

    if leaderboard_df.empty:
        st.info("No candidate data available yet. Upload resumes on the main Screener page to populate the leaderboard.")
        return

    # Sidebar filters for the leaderboard
    st.sidebar.header("📊 Filter Leaderboard")
    
    # Filter by Job Description
    unique_jds = ["All"] + sorted(leaderboard_df["JD Used"].unique())
    selected_jd = st.sidebar.selectbox("Filter by Job Description", unique_jds)

    # Filter by Minimum Score
    min_score_filter = st.sidebar.slider("Minimum Score (%)", 0, 100, 0)

    # Filter by Minimum Experience
    min_exp_filter = st.sidebar.slider("Minimum Experience (Years)", 0, 15, 0)

    # Apply filters to the DataFrame
    filtered_df = leaderboard_df.copy()
    if selected_jd != "All":
        filtered_df = filtered_df[filtered_df["JD Used"] == selected_jd]
    
    filtered_df = filtered_df[filtered_df["Score (%)"] >= min_score_filter]
    filtered_df = filtered_df[filtered_df["Years Experience"] >= min_exp_filter]

    # Display the filtered data
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
                # Format CGPA only if it's not None/NaN
                "CGPA (4.0 Scale)": lambda x: f"{x:.2f}" if pd.notna(x) else "N/A",
                "Date Screened": lambda x: x.strftime("%Y-%m-%d") # Format date for display
            }),
            use_container_width=True,
            hide_index=True
        )

# This block ensures the leaderboard_page function is called when the script is run directly
if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Leaderboard", layout="wide")
    leaderboard_page()
