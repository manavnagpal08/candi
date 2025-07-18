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

# Global variable for app ID (as provided by the environment)
appId = os.environ.get('__app_id', 'default-screener-pro-app')

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
        
        # Corrected: Parent path is part of the URL for runQuery when querying a subcollection
        # The URL should point to the parent document of the collection you want to query.
        parent_path = f"projects/{project_id}/databases/(default)/documents/artifacts/{appId}/public/data"
        url = f"https://firestore.googleapis.com/v1/{parent_path}:runQuery?key={api_key}"

        # Structured query to find a document where 'Certificate ID' field matches the input
        # 'collectionId' is now just the immediate collection name relative to the parent_path
        query_payload = {
            "structuredQuery": {
                "from": [{"collectionId": "leaderboard"}], # Only the immediate collection name here
                "where": {
                    "fieldFilter": {
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

@st.cache_data
def generate_certificate_html(candidate_data):
    html_template = """

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ScreenerPro Certificate</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

    body {
      margin: 0;
      padding: 0;
      background: #f4f6f8;
      font-family: 'Inter', sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .certificate {
  background-color: #ffffff;
  width: 960px;
  max-width: 960px;
  padding: 60px 50px;
  border: 10px solid #00bcd4;
  box-shadow: 0 0 20px rgba(0,0,0,0.1);
  box-sizing: border-box;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.certificate img.logo {
  width: 260px;         /* Large logo */
  max-height: 100px;    /* Limit height */
  object-fit: contain;  /* Keep it proportional */
  margin-bottom: 15px;
}


    h1 {
      font-family: 'Playfair Display', serif;
      font-size: 36px;
      margin-bottom: 10px;
      color: #003049;
    }

    h2 {
      font-family: 'Playfair Display', serif;
      font-size: 22px;
      margin: 5px 0 30px;
      color: #007c91;
      font-weight: normal;
    }

    .candidate-name {
      font-family: 'Playfair Display', serif;
      font-size: 32px;
      color: #00bcd4;
      margin: 20px 0 10px;
      font-weight: bold;
      text-decoration: underline;
    }

    .subtext {
      font-size: 18px;
      color: #333;
      margin-bottom: 20px;
    }

    .score-rank {
      display: inline-block;
      margin: 15px 0;
      font-size: 18px;
      font-weight: 600;
      background: #e0f7fa;
      color: #2e7d32;
      padding: 8px 20px;
      border-radius: 8px;
    }

    .description {
      font-size: 16px;
      color: #555;
      margin: 25px auto;
      line-height: 1.6;
      max-width: 750px;
    }

    .footer-details {
      font-size: 14px;
      color: #666;
      margin-top: 40px;
    }

    .signature-block {
      text-align: left;
      margin-top: 60px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .signature {
      text-align: left;
    }

    .signature .name {
      font-weight: 600;
      font-size: 15px;
      margin-top: 8px;
    }

    .signature .title {
      font-size: 13px;
      color: #777;
    }

    .signature img {
      width: 160px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5px;
    }

    .stamp {
      font-size: 42px;
      color: #4caf50;
    }

    @media print {
      body {
        background: #ffffff;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }

      .certificate {
        box-shadow: none;
      }
    }
  </style>
</head>
<body>
  <div class="certificate">
    <!-- Local logo image -->
    <img class="logo" src="https://raw.githubusercontent.com/manavnagpal08/yg/main/logo.png" alt="ScreenerPro Logo" />


    <h1>CERTIFICATE OF EXCELLENCE</h1>
    <h2>Presented by ScreenerPro</h2>

    <div class="subtext">This is to certify that</div>
    <div class="candidate-name">{{CANDIDATE_NAME}}</div>

    <div class="subtext">has successfully completed the AI-powered resume screening process</div>

    <div class="score-rank">Score: {{SCORE}}% | Rank: {{CERTIFICATE_RANK}}</div>

    <div class="description">
      This certificate acknowledges the candidate’s exceptional qualifications, industry-aligned skills, and readiness to contribute effectively in challenging roles. Evaluated and validated by ScreenerPro’s advanced screening engine.
    </div>

    <div class="footer-details">
      Awarded on: {{DATE_SCREENED}}<br>
      Certificate ID: {{CERTIFICATE_ID}}
    </div>

    <div class="signature-block">
  <div class="signature">
    <img src="https://see.fontimg.com/api/rf5/DOLnW/ZTAyODAyZDM3MWUyNDVjNjg0ZWRmYTRjMjNlOTE3ODUub3Rm/U2NyZWVuZXJQcm8/autography.png?r=fs&h=81&w=1250&fg=000000&bg=FFFFFF&tb=1&s=65" alt="Signature" />
    <div class="title">Founder & Product Head, ScreenerPro</div>
  </div>
  <div class="stamp">✔️</div>
</div>


    
  </div>
</body>
</html>


    """

    candidate_name = candidate_data.get('Candidate Name', 'Candidate Name')
    score = candidate_data.get('Score (%)', 0.0)
    certificate_rank = candidate_data.get('Certificate Rank', 'Not Applicable')
    
    # Ensure Date Screened is a datetime object before formatting
    date_screened_raw = candidate_data.get('Date Screened', datetime.now().strftime("%Y-%m-%d"))
    if isinstance(date_screened_raw, str):
        try:
            date_screened = pd.to_datetime(date_screened_raw).strftime("%B %d, %Y")
        except:
            date_screened = date_screened_raw # Fallback if parsing fails
    elif isinstance(date_screened_raw, datetime):
        date_screened = date_screened_raw.strftime("%B %d, %Y")
    else:
        date_screened = str(date_screened_raw) # Last resort

    certificate_id = candidate_data.get('Certificate ID', 'N/A')
    
    html_content = html_template.replace("{{CANDIDATE_NAME}}", candidate_name)
    html_content = html_content.replace("{{SCORE}}", f"{score:.1f}")
    html_content = html_content.replace("{{CERTIFICATE_RANK}}", certificate_rank)
    html_content = html_content.replace("{{DATE_SCREENED}}", date_screened)
    html_content = html_content.replace("{{CERTIFICATE_ID}}", certificate_id)

    return html_content

def certificate_verification_page():
    """
    Displays the Certificate Verification page in Streamlit.
    Allows users to input a Certificate ID and view candidate details.
    """
    # Personalized greeting for the logged-in user
    if st.session_state.get('authenticated', False) and st.session_state.get('username'):
        st.markdown(f"## Hello, {st.session_state.username}!")

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

                st.markdown("---")
                st.subheader("View Certificate")
                
                certificate_html_content = generate_certificate_html(candidate_details)
                
                col_cert_view, col_cert_download = st.columns(2)
                
                with col_cert_view:
                    if st.button("👁️ View Certificate (HTML Preview)", key="view_cert_button_verify"):
                        st.session_state['show_certificate_preview_verify'] = True
                    else:
                        st.session_state['show_certificate_preview_verify'] = False
                        
                with col_cert_download:
                    st.download_button(
                        label="⬇️ Download Certificate (HTML)",
                        data=certificate_html_content,
                        file_name=f"ScreenerPro_Certificate_{candidate_details['Candidate Name'].replace(' ', '_')}.html",
                        mime="text/html",
                        key="download_cert_button_verify",
                        help="Download the certificate as an HTML file. You can open it in your browser and print to PDF."
                    )
                
                # Only show the HTML preview if the button was clicked
                if st.session_state.get('show_certificate_preview_verify', False):
                    st.markdown("---")
                    st.markdown("### Generated Certificate Preview (HTML)")
                    st.components.v1.html(certificate_html_content, height=600, scrolling=True)
                    st.markdown("---")

            else:
                st.warning("Certificate ID not found or invalid. Please check the ID and try again.")
        else:
            st.error("Please enter a Certificate ID to verify.")

# This block ensures the certificate_verification_page function is called when the script is run directly
if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Certificate Verification", layout="wide")
    certificate_verification_page()
