import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
import requests # Import requests for REST API calls
import matplotlib.pyplot as plt # For visualizations
import seaborn as sns # For better looking plots

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
        # Recursively convert items in list
        return [_convert_from_firestore_rest_format(item) for item in field_value["arrayValue"].get("values", [])]
    elif "mapValue" in field_value:
        # Recursively convert items in map
        return {k: _convert_from_firestore_rest_format(v) for k, v in field_value["mapValue"].get("fields", {}).items()}
    return None # Fallback for unknown types

@st.cache_data(ttl=60) # Cache data for 60 seconds to reduce Firestore reads
def fetch_leaderboard_data():
    """
    Fetches candidate screening results from Firestore using the REST API,
    implementing pagination to retrieve all documents.
    Data is fetched from the 'leaderboard' collection at the root.
    Includes the Firestore document ID for detailed view fetching.
    """
    leaderboard_data = []
    page_token = None
    
    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
        
        collection_id = "leaderboard"
        base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}"

        while True:
            url = base_url
            if page_token:
                url += f"&pageToken={page_token}"
            
            response = requests.get(url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
            response_json = response.json()
            
            for doc_entry in response_json.get("documents", []):
                data = {}
                doc_id = doc_entry.get("name", "").split('/')[-1]
                data["Firestore Doc ID"] = doc_id # Store the document ID

                for key, value_obj in doc_entry.get("fields", {}).items():
                    data[key] = _convert_from_firestore_rest_format(value_obj)
                
                leaderboard_data.append({
                    "Firestore Doc ID": data.get("Firestore Doc ID", "N/A"), # Ensure ID is present
                    "Candidate Name": data.get("Candidate Name", "N/A"),
                    "Score (%)": data.get("Score (%)", 0.0), 
                    "Years Experience": data.get("Years Experience", 0.0),
                    "CGPA (4.0 Scale)": data.get("CGPA (4.0 Scale)", None),
                    "JD Used": data.get("JD Used", "N/A"),
                    "Date Screened": pd.to_datetime(data.get("Date Screened", datetime.now().strftime("%Y-%m-%d"))),
                    "Certificate Rank": data.get("Certificate Rank", "N/A"),
                    "Tag": data.get("Tag", "N/A"),
                    "AI Suggestion": data.get("AI Suggestion", "N/A"), # Fetch for detailed view
                    "Detailed HR Assessment": data.get("Detailed HR Assessment", "N/A"), # Fetch for detailed view
                    "Matched Keywords (Categorized)": data.get("Matched Keywords (Categorized)", "{}"), # Fetch for detailed view
                    "Missing Skills (Categorized)": data.get("Missing Skills (Categorized)", "{}"), # Fetch for detailed view
                    "Semantic Similarity": data.get("Semantic Similarity", 0.0) # Fetch for detailed view
                })
            
            # Check for next page token
            page_token = response_json.get("nextPageToken")
            if not page_token:
                break # No more pages, exit loop
        
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
    Fetches and filters candidate data from Firestore, and provides detailed view.
    """
    # Personalized greeting for the logged-in user
    if st.session_state.get('authenticated', False) and st.session_state.get('username'):
        st.markdown(f"## Hello, {st.session_state.username}!")

    st.title("🏆 ScreenerPro Leaderboard")
    st.markdown("### Top Candidates by Screening Score")
    st.caption("This page is publicly accessible and displays all candidates who have used the ScreenerPro app.")

    st.info("💡 Data is being loaded using the Firebase REST API.")

    col_buttons_1, col_buttons_2 = st.columns([1, 1])
    with col_buttons_1:
        # Add a refresh button to allow users to get the latest data
        if st.button("🔄 Refresh Leaderboard Data"):
            st.cache_data.clear() # Clear the cache to force a fresh data fetch
            st.rerun() # Rerun the app to apply changes
    with col_buttons_2:
        # Search by Candidate Name
        search_query = st.text_input("🔍 Search by Candidate Name", "")

    # Fetch the leaderboard data
    leaderboard_df = fetch_leaderboard_data()

    if leaderboard_df.empty:
        st.info("No candidate data available yet. Upload resumes on the main Screener page to populate the leaderboard.")
        return

    # --- Filters moved to main content area ---
    st.markdown("---")
    st.subheader("📊 Filter Leaderboard")
    
    filter_cols = st.columns(3)
    with filter_cols[0]:
        # Filter by Job Description
        unique_jds = ["All"] + sorted(leaderboard_df["JD Used"].unique())
        selected_jd = st.selectbox("Filter by Job Description", unique_jds)

    with filter_cols[1]:
        # Filter by Tag
        unique_tags = ["All"] + sorted(leaderboard_df["Tag"].unique())
        selected_tag = st.selectbox("Filter by Tag", unique_tags)

    with filter_cols[2]:
        # Filter by Certificate Rank
        unique_cert_ranks = ["All"] + sorted(leaderboard_df["Certificate Rank"].unique())
        selected_cert_rank = st.selectbox("Filter by Certificate Rank", unique_cert_ranks)

    filter_cols_2 = st.columns(2)
    with filter_cols_2[0]:
        # Filter by Minimum Score
        min_score_filter = st.slider("Minimum Score (%)", 0, 100, 0)
    with filter_cols_2[1]:
        # Filter by Minimum Experience
        min_exp_filter = st.slider("Minimum Experience (Years)", 0, 15, 0)

    # Apply filters to the DataFrame
    filtered_df = leaderboard_df.copy()

    # Apply search filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Candidate Name"].str.contains(search_query, case=False, na=False)
        ]

    if selected_jd != "All":
        filtered_df = filtered_df[filtered_df["JD Used"] == selected_jd]
    
    if selected_tag != "All":
        filtered_df = filtered_df[filtered_df["Tag"] == selected_tag]

    if selected_cert_rank != "All":
        filtered_df = filtered_df[filtered_df["Certificate Rank"] == selected_cert_rank]

    filtered_df = filtered_df[filtered_df["Score (%)"] >= min_score_filter]
    filtered_df = filtered_df[filtered_df["Years Experience"] >= min_exp_filter]

    # Add Rank column to the filtered DataFrame
    if not filtered_df.empty:
        filtered_df['Rank'] = filtered_df['Score (%)'].rank(ascending=False, method='min').astype(int)
        filtered_df = filtered_df.sort_values(by="Rank").reset_index(drop=True)

    # Display Average Score
    if not filtered_df.empty:
        avg_score = filtered_df["Score (%)"].mean()
        st.metric(label="Average Score (Filtered Candidates)", value=f"{avg_score:.2f}%")

    # Display the filtered data
    if filtered_df.empty:
        st.info("No candidates match the selected filters.")
    else:
        st.markdown("---")
        st.subheader("Leaderboard Results")
        st.caption("Click on a row to view detailed candidate assessment.")

        # Download Button for Filtered Data
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Filtered Data as CSV",
            data=csv_data,
            file_name="screenerpro_leaderboard_filtered.csv",
            mime="text/csv",
            key="download_filtered_csv"
        )
        
        # Display the dataframe with selection enabled
        st.dataframe(
            filtered_df[[
                "Rank", # Include Rank column
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
            hide_index=True,
            on_select='rerun', # Rerun app when a row is selected
            selection_mode='single-row', # Allow only single row selection
            key="leaderboard_table" # Unique key for the dataframe
        )

        # Check for selected rows and display details
        selected_rows = st.session_state.leaderboard_table.get("selection", {}).get("rows", [])
        if selected_rows:
            selected_index = selected_rows[0] # Get the index of the first selected row
            selected_candidate_data = filtered_df.iloc[selected_index] # Get the full row data from filtered_df

            st.markdown("---")
            st.subheader(f"Detailed Assessment for {selected_candidate_data['Candidate Name']}")
            
            # All detailed data is now available in selected_candidate_data
            if selected_candidate_data is not None:
                st.markdown(f"**Score:** {selected_candidate_data.get('Score (%)', 0.0):.2f}% | **Experience:** {selected_candidate_data.get('Years Experience', 0.0):.1f} years | **CGPA:** {selected_candidate_data.get('CGPA (4.0 Scale)', 'N/A')} (4.0 Scale) | **Semantic Similarity:** {selected_candidate_data.get('Semantic Similarity', 0.0):.2f}")
                st.markdown(f"**AI Suggestion:** {selected_candidate_data.get('AI Suggestion', 'N/A')}")
                st.markdown(f"**Detailed HR Assessment:**")
                st.markdown(selected_candidate_data.get('Detailed HR Assessment', 'N/A'))

                st.markdown("#### Matched Skills Breakdown:")
                matched_kws_categorized_str = selected_candidate_data['Matched Keywords (Categorized)']
                if matched_kws_categorized_str and isinstance(matched_kws_categorized_str, str):
                    try:
                        matched_kws_categorized_dict = json.loads(matched_kws_categorized_str)
                        if matched_kws_categorized_dict:
                            for category, skills in matched_kws_categorized_dict.items():
                                st.write(f"**{category}:** {', '.join(skills)}")
                        else:
                            st.write("No categorized matched skills found.")
                    except json.JSONDecodeError:
                        st.write(f"Error parsing matched skills data.")
                else:
                    st.write("No categorized matched skills found.")

                st.markdown("#### Missing Skills Breakdown (from JD):")
                missing_kws_categorized_str = selected_candidate_data['Missing Skills (Categorized)']
                if missing_kws_categorized_str and isinstance(missing_kws_categorized_str, str):
                    try:
                        missing_kws_categorized_dict = json.loads(missing_kws_categorized_str)
                        if missing_kws_categorized_dict:
                            for category, skills in missing_kws_categorized_dict.items():
                                st.write(f"**{category}:** {', '.join(skills)}")
                        else:
                            st.write("No categorized missing skills found.")
                    except json.JSONDecodeError:
                        st.write(f"Error parsing missing skills data.")
                else:
                    st.write("No categorized missing skills found.")
            else:
                st.warning("Could not load detailed information for the selected candidate.")
            
        st.markdown("---")
        st.subheader("Score Distribution")
        st.caption("Histogram showing the distribution of screening scores.")
        
        # Plotting the score distribution
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(filtered_df["Score (%)"], bins=10, kde=True, ax=ax, color='#00bcd4')
            ax.set_title("Distribution of Candidate Scores")
            ax.set_xlabel("Score (%)")
            ax.set_ylabel("Number of Candidates")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data to display score distribution.")


# This block ensures the leaderboard_page function is called when the script is run directly
if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Leaderboard", layout="wide")
    leaderboard_page()
