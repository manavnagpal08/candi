import streamlit as st
import requests
import json
import os
import pandas as pd # For displaying data
from datetime import datetime # Import datetime for pd.to_datetime

# Helper function to convert Firestore REST API format back to Python data
# (Copied from top_leaderboard.py to ensure consistency)
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

@st.cache_data(ttl=60) # Cache data for a short period
def fetch_candidate_by_certificate_id(certificate_id):
    """
    Fetches candidate details from Firestore by Certificate ID using the REST API.
    """
    if not certificate_id:
        return None

    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
        collection_id = "leaderboard"

        # Firestore REST API endpoint for running a structured query
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:runQuery?key={api_key}"

        # Structured query to find a document where 'Certificate ID' field matches the input
        query_payload = {
            "structuredQuery": {
                "from": [{"collectionId": collection_id}],
                "where": {
                    "fieldFilter": {
                        # FIX: Enclose "Certificate ID" in backticks for the fieldPath
                        "field": {"fieldPath": "`Certificate ID`"},
                        "op": "EQUAL",
                        "value": {"stringValue": certificate_id}
                    }
                },
                "limit": 1 # We only expect one result for a unique certificate ID
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(query_payload))
        response.raise_for_status() # Raise an HTTPError for bad responses

        response_json = response.json()

        # The response for runQuery is an array of results, each containing a 'document' field
        # Note: If no document matches, response_json might be empty or not contain 'document'
        if response_json and len(response_json) > 0 and "document" in response_json[0]:
            doc_entry = response_json[0]["document"]
            details = {}
            for key, value_obj in doc_entry.get("fields", {}).items():
                details[key] = _convert_from_firestore_rest_format(value_obj)
            
            # Ensure categorized skills are parsed from JSON strings if they come as such
            if isinstance(details.get('Matched Keywords (Categorized)'), str):
                try:
                    details['Matched Keywords (Categorized)'] = json.loads(details['Matched Keywords (Categorized)'])
                except json.JSONDecodeError:
                    details['Matched Keywords (Categorized)'] = {}
            if isinstance(details.get('Missing Skills (Categorized)'), str):
                try:
                    details['Missing Skills (Categorized)'] = json.loads(details['Missing Skills (Categorized)'])
                except json.JSONDecodeError:
                    details['Missing Skills (Categorized)'] = {}
            
            return details
        else:
            return None # No document found
    except KeyError as e:
        st.error(f"❌ Firebase REST API configuration error for certificate verification: Missing secret key '{e}'.")
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

def certificate_verification_page():
    """
    Displays the Certificate Verification page in Streamlit.
    Allows users to input a Certificate ID and view candidate details.
    """
    st.title("✅ Certificate Verification")
    st.markdown("### Verify the authenticity of ScreenerPro Certificates.")
    st.caption("Enter a Certificate ID below to view the associated candidate's details and screening assessment.")

    st.info("💡 Certificate IDs are unique identifiers generated during the resume screening process.")

    certificate_id_input = st.text_input("Enter Certificate ID", key="cert_id_input", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")

    if st.button("🔍 Verify Certificate"):
        if certificate_id_input:
            with st.spinner("Verifying certificate..."):
                candidate_details = fetch_candidate_by_certificate_id(certificate_id_input)
            
            if candidate_details:
                st.markdown("---")
                st.subheader(f"Certificate Details for {candidate_details.get('Candidate Name', 'N/A')}")
                
                # Display key details in a structured way
                col_info_1, col_info_2 = st.columns(2)
                with col_info_1:
                    st.write(f"**Candidate Name:** {candidate_details.get('Candidate Name', 'N/A')}")
                    st.write(f"**Score (%):** {candidate_details.get('Score (%)', 0.0):.2f}%")
                    st.write(f"**Years Experience:** {candidate_details.get('Years Experience', 0.0):.1f} years")
                    st.write(f"**CGPA (4.0 Scale):** {candidate_details.get('CGPA (4.0 Scale)', 'N/A')}")
                with col_info_2:
                    st.write(f"**JD Used:** {candidate_details.get('JD Used', 'N/A')}")
                    # Ensure Date Screened is formatted correctly for display
                    date_screened_str = candidate_details.get('Date Screened', datetime.now().strftime('%Y-%m-%d'))
                    if isinstance(date_screened_str, str):
                        st.write(f"**Date Screened:** {pd.to_datetime(date_screened_str).strftime('%Y-%m-%d')}")
                    else:
                        st.write(f"**Date Screened:** {date_screened_str}") # Fallback if not string
                    st.write(f"**Certificate Rank:** {candidate_details.get('Certificate Rank', 'N/A')}")
                    st.write(f"**Tag:** {candidate_details.get('Tag', 'N/A')}")
                
                st.markdown("---")
                st.subheader("AI Assessment Summary:")
                st.markdown(f"**AI Suggestion:** {candidate_details.get('AI Suggestion', 'N/A')}")
                st.markdown(f"**Detailed HR Assessment:**")
                st.markdown(candidate_details.get('Detailed HR Assessment', 'N/A'))

                st.markdown("#### Matched Skills Breakdown:")
                matched_kws_categorized_dict = candidate_details.get('Matched Keywords (Categorized)', {})
                if matched_kws_categorized_dict:
                    for category, skills in matched_kws_categorized_dict.items():
                        st.write(f"**{category}:** {', '.join(skills)}")
                else:
                    st.write("No categorized matched skills found.")

                st.markdown("#### Missing Skills Breakdown (from JD):")
                missing_kws_categorized_dict = candidate_details.get('Missing Skills (Categorized)', {})
                if missing_kws_categorized_dict:
                    for category, skills in missing_kws_categorized_dict.items():
                        st.write(f"**{category}:** {', '.join(skills)}")
                else:
                    st.write("No categorized missing skills found.")
            else:
                st.warning("Certificate ID not found or invalid. Please check the ID and try again.")
        else:
            st.error("Please enter a Certificate ID to verify.")

# This block ensures the certificate_verification_page function is called when the script is run directly
if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Certificate Verification", layout="wide")
    certificate_verification_page()
