import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
import requests # Import requests for REST API calls

# Removed firebase_admin imports as we are now using the REST API for fetching.

# Global variable for app ID (as provided by the environment)
# This assumes __app_id is available in the Streamlit environment.
# If running locally without this, you might need to hardcode a default or set it via env var.
appId = os.environ.get('__app_id', 'default-screener-pro-app')

# Helper function to convert Firestore REST API format back to Python data
def _convert_from_firestore_rest_format(field_value):
    """
    Converts a Firestore REST API field value (e.g., {"stringValue": "abc"})
    back to a standard Python value.
    """
    if "stringValue" in field_value:
        return field_value["stringValue"]
    elif "integerValue" in field_value:
        return int(field_value["integerValue"])
    elif "doubleValue" in field_value:
        return float(field_value["doubleValue"])
    elif "booleanValue" in field_value:
        return field_value["booleanValue"]
    elif "nullValue" in field_value:
        return None
    elif "arrayValue" in field_value:
        return [_convert_from_firestore_rest_format(item) for item in field_value["arrayValue"].get("values", [])]
    elif "mapValue" in field_value:
        return {k: _convert_from_firestore_rest_format(v) for k, v in field_value["mapValue"].get("fields", {}).items()}
    return None # Fallback for unknown types

@st.cache_data(ttl=60) # Cache data for 60 seconds to reduce Firestore reads
def fetch_leaderboard_data():
    """
    Fetches candidate screening results from Firestore using the REST API.
    Data is fetched from a public collection path.
    """
    leaderboard_data = []
    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
        
        # Firestore collection path (using 'leaderboard' as before)
        collection_id = "leaderboard" 
        
        # Firestore REST API endpoint for listing documents in a collection
        # This path adheres to the public data storage convention: /artifacts/{appId}/public/data/{your_collection_name}
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/{appId}/public/data/{collection_id}?key={api_key}"

        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        response_json = response.json()
        
        # The REST API response for listing documents is a list of documents,
        # where each document has a 'fields' key containing the actual data.
        for doc_entry in response_json.get("documents", []):
            data = {}
            # Convert each field from Firestore REST format to Python native types
            for key, value_obj in doc_entry.get("fields", {}).items():
                data[key] = _convert_from_firestore_rest_format(value_obj)
            
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
    except KeyError as e:
        st.error(f"❌ Firebase REST API configuration error: Missing secret key '{e}'.")
        st.info("Please ensure 'FIREBASE_PROJECT_ID' and 'FIREBASE_API_KEY' are correctly set in your secrets.toml or Streamlit Cloud secrets.")
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Failed to fetch leaderboard data via REST API: HTTP Error {e.response.status_code}")
        st.error(f"Response: {e.response.text}")
        st.warning("This often indicates an issue with Firestore security rules (e.g., read access denied) or incorrect API key/project ID.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while fetching leaderboard data via REST API: {e}")
        st.exception(e)
        return pd.DataFrame()

def leaderboard_page():
    """
    Displays the ScreenerPro Leaderboard page in Streamlit.
    Fetches and filters candidate data from Firestore.
    """
    st.title("🏆 ScreenerPro Leaderboard")
    st.markdown("### Top Candidates by Screening Score")
    st.caption("View the highest-scoring candidates across various job descriptions.")

    st.info("💡 Data is being loaded using the Firebase REST API.") # Added this line for clarity

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
