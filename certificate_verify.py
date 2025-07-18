import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
import requests # Import requests for REST API calls
import traceback # Import traceback for detailed error logging

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

# Global variable for app ID (not directly used in this query path as 'leaderboard' is root)
appId = os.environ.get('__app_id', 'default-screener-pro-app')

@st.cache_data(ttl=60) # Cache data for a short period
def fetch_candidate_by_certificate_id_rest(certificate_id):
    """
    Fetches candidate details from Firestore by Certificate ID using the REST API.
    Queries the top-level 'leaderboard' collection.
    """
    if not certificate_id:
        return None

    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
        
        # Correct URL for runQuery on a top-level collection
        # The URL points to the database root, and the collection is specified in 'from'
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:runQuery?key={api_key}"

        # Structured query to find a document where 'Certificate ID' field matches the input
        query_payload = {
            "structuredQuery": {
                "from": [{"collectionId": "leaderboard"}], # Top-level collection name only
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "`Certificate ID`"}, # Field name with backticks for special characters
                        "op": "EQUAL",
                        "value": {"stringValue": certificate_id}
                    }
                },
                "limit": 1 # We only expect one result for a unique certificate ID
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(query_payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()

        # The response for runQuery is an array of results, each containing a 'document' field
        # Note: If no document matches, response_json might be empty or not contain 'document'
        if response_json and len(response_json) > 0 and "document" in response_json[0]:
            doc_entry = response_json[0]["document"]
            details = {}
            for key, value_obj in doc_entry.get("fields", {}).items():
                details[key] = _convert_from_firestore_rest_format(value_obj)
            
            # Ensure categorized skills are parsed from JSON strings if they come as such
            # This is important if they were stored as JSON strings in Firestore
            if isinstance(details.get('Matched Keywords (Categorized)'), str):
                try:
                    details['Matched Keywords (Categorized)'] = json.loads(details['Matched Keywords (Categorized)'])
                except json.JSONDecodeError:
                    details['Matched Keywords (Categorized)'] = {} # Fallback
            if isinstance(details.get('Missing Skills (Categorized)'), str):
                try:
                    details['Missing Skills (Categorized)'] = json.loads(details['Missing Skills (Categorized)'])
                except json.JSONDecodeError:
                    details['Missing Skills (Categorized)'] = {} # Fallback
            
            return details
        else:
            return None # No document found
    except KeyError as e:
        st.error(f"❌ Firebase REST API configuration error for certificate verification: Missing secret key '{e}'.")
        st.info("Please ensure 'FIREBASE_PROJECT_ID' and 'FIREBASE_API_KEY' are correctly set in your secrets.toml or Streamlit Cloud secrets.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Failed to fetch certificate details via REST API: HTTP Error {e.response.status_code}")
        st.error(f"Response: {e.response.text}")
        st.warning("Ensure Firestore security rules allow read access to the 'leaderboard' collection.")
        return None
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while verifying certificate: {e}")
        st.exception(e)
        return None

def certificate_verifier_page():
    st.title("✅ ScreenerPro Certificate Verification")
    st.markdown("### Verify the authenticity of a ScreenerPro Certificate.")

    # No longer need to check for 'db' as firebase_admin is removed.
    # The REST API functions will handle their own error messages if secrets are missing.

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
            # Call the REST API function to fetch data
            candidate_data = fetch_candidate_by_certificate_id_rest(certificate_id_input)
            
            if candidate_data:
                st.success("Certificate Found and Verified!")
                st.markdown("---")
                st.markdown("#### Certificate Details:")
                
                st.write(f"**Candidate Name:** {candidate_data.get('Candidate Name', 'N/A')}")
                st.write(f"**Score (%):** {candidate_data.get('Score (%)', 0.0):.2f}%")
                st.write(f"**Years Experience:** {candidate_data.get('Years Experience', 0.0):.1f} years")
                
                # Handle CGPA display, ensuring it's formatted only if a valid number
                cgpa_value = candidate_data.get('CGPA (4.0 Scale)', None)
                cgpa_display = f"{cgpa_value:.2f}" if pd.notna(cgpa_value) and isinstance(cgpa_value, (int, float)) else "N/A"
                st.write(f"**CGPA (4.0 Scale):** {cgpa_display}")
                
                st.write(f"**Job Description Used:** {candidate_data.get('JD Used', 'N/A')}")
                st.write(f"**Date Screened:** {candidate_data.get('Date Screened', 'N/A')}")
                st.write(f"**Certificate Rank:** {candidate_data.get('Certificate Rank', 'N/A')}")
                st.write(f"**Tag:** {candidate_data.get('Tag', 'N/A')}")
                st.write(f"**Certificate ID:** `{candidate_data.get('Certificate ID', 'N/A')}`")

                st.markdown("---")
                st.info("This certificate is authentic and was issued by ScreenerPro.")
            else:
                st.error("Certificate not found. Please check the ID and try again.")
                st.info("The provided Certificate ID does not match any records in our system. It might be incorrect, or the certificate may not exist.")

if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Certificate Verification", layout="wide")
    certificate_verifier_page()
