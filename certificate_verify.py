import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
import requests # Import requests for REST API calls
import traceback # Import traceback for detailed error logging
import urllib.parse # For URL encoding for sharing buttons

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

# IMPORTANT: REPLACE THESE WITH YOUR ACTUAL DEPLOYMENT URLs
# This is the base URL for your Streamlit app. It should be the public URL.
# Example: "https://your-app-name.streamlit.app"
APP_BASE_URL = "https://screenerpro-app.streamlit.app" 

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

@st.cache_data
def generate_certificate_html(candidate_data):
    # This function is copied directly from resume-screen-page-py to ensure consistency
    # and avoid circular imports.
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
  min-height: 800px; /* Added min-height to ensure enough space */
  height: auto; /* Ensure height adjusts to content */
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

def certificate_verifier_page():
    st.title("✅ ScreenerPro Certificate Verification")
    st.markdown("### Verify the authenticity of a ScreenerPro Certificate.")

    # Initialize session state for certificate preview and input value
    if 'certificate_html_content_verifier' not in st.session_state:
        st.session_state['certificate_html_content_verifier'] = ""
    if 'cert_id_input_value' not in st.session_state:
        st.session_state['cert_id_input_value'] = ""

    # Check for certificate ID in URL query parameters on initial load
    query_params = st.query_params
    if "cert_id" in query_params and not st.session_state['cert_id_input_value']:
        st.session_state['cert_id_input_value'] = query_params["cert_id"]
        # Automatically trigger verification if ID found in URL
        # This will cause a rerun, and the `if st.button` block below will not execute immediately
        # but the `candidate_data` will be fetched on the next rerun.
        # We need a way to trigger the display logic without button click on initial load.
        # A simple way is to set a flag or directly call the fetch if the value is from URL.

    certificate_id_input = st.text_input(
        "Enter Certificate ID",
        value=st.session_state['cert_id_input_value'], # Use session state for value
        placeholder="e.g., a1b2c3d4-e5f6-7890-1234-567890abcdef",
        help="Paste the unique Certificate ID found on the ScreenerPro certificate.",
        key="cert_id_text_input" # Add a key for the text input
    )

    # Update session state value if user types
    if st.session_state['cert_id_text_input'] != st.session_state['cert_id_input_value']:
        st.session_state['cert_id_input_value'] = st.session_state['cert_id_text_input']
        # Clear certificate content if user starts typing a new ID
        st.session_state['certificate_html_content_verifier'] = ""
        st.rerun() # Rerun to reflect changes and clear display

    # Logic to trigger verification: either by button click or by URL parameter on initial load
    trigger_verification = False
    if st.button("🔍 Verify Certificate"):
        trigger_verification = True
    elif "cert_id" in query_params and query_params["cert_id"] == st.session_state['cert_id_input_value'] and not st.session_state['certificate_html_content_verifier']:
        # This condition checks if there's a cert_id in URL, it matches the input,
        # and the certificate hasn't been displayed yet (to avoid infinite loop).
        trigger_verification = True

    if trigger_verification and certificate_id_input:
        with st.spinner(f"Verifying certificate ID: {certificate_id_input}..."):
            candidate_data = fetch_candidate_by_certificate_id_rest(certificate_id_input)
            
            if candidate_data:
                st.success("Certificate Found and Verified!")
                st.markdown("---")
                st.markdown("#### Certificate Details:")
                
                st.write(f"**Candidate Name:** {candidate_data.get('Candidate Name', 'N/A')}")
                st.write(f"**Score (%):** {candidate_data.get('Score (%)', 0.0):.2f}%")
                st.write(f"**Years Experience:** {candidate_data.get('Years Experience', 0.0):.1f} years")
                
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

                # --- Certificate Display and Download ---
                st.subheader("View & Share Certificate")
                
                # Generate HTML content for the certificate
                certificate_html_content = generate_certificate_html(candidate_data)
                st.session_state['certificate_html_content_verifier'] = certificate_html_content # Store for preview

                # Removed the shareable link text input and copy button
                # shareable_link = f"{APP_BASE_URL}?page=certificate_verify&cert_id={urllib.parse.quote(certificate_id_input)}"
                # st.text_input("🔗 Shareable Certificate Link", value=shareable_link, disabled=True, key="share_link_display")
                # copy_js = f"""
                # <script>
                # function copyToClipboard(text) {{
                #     var dummy = document.createElement("textarea");
                #     document.body.appendChild(dummy);
                #     dummy.value = text;
                #     dummy.select();
                #     document.execCommand("copy");
                #     document.body.removeChild(dummy);
                #     alert("Link copied to clipboard!"); // Use a custom message box in production
                # }}
                # </script>
                # <button onclick="copyToClipboard('{shareable_link}')" style="background-color:#00bcd4;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;margin-top:10px;">Copy Link</button>
                # """
                # st.markdown(copy_js, unsafe_allow_html=True)


                col_cert_download, col_share_linkedin, col_share_whatsapp = st.columns(3) 
                
                with col_cert_download:
                    st.download_button(
                        label="⬇️ Download Certificate (HTML)",
                        data=certificate_html_content,
                        file_name=f"ScreenerPro_Certificate_{candidate_data['Candidate Name'].replace(' ', '_')}.html",
                        mime="text/html",
                        key="download_cert_button_verifier",
                        help="Download the certificate as an HTML file. You can open it in your browser and print to PDF."
                    )
                
                # Share message for social media
                share_message = f"""I just verified a Certificate of Screening Excellence from ScreenerPro! 🏆
This candidate was evaluated across multiple hiring parameters using AI-powered screening technology and scored above {candidate_data['Score (%)']:.1f}%.

#resume #jobsearch #ai #careergrowth #certified #ScreenerPro #LinkedIn
🌐 Verify this certificate: {APP_BASE_URL}
"""
                
                # LinkedIn Share Button
                # LinkedIn's shareArticle does not pre-fill the user's post text directly.
                # The 'summary' parameter is for the link preview description.
                linkedin_share_url = f"https://www.linkedin.com/shareArticle?mini=true&url={urllib.parse.quote(APP_BASE_URL)}&title={urllib.parse.quote('ScreenerPro Certificate Verification')}&summary={urllib.parse.quote(share_message)}"
                with col_share_linkedin:
                    st.markdown(f'<a href="{linkedin_share_url}" target="_blank"><button style="background-color:#0077B5;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">Share on LinkedIn</button></a>', unsafe_allow_html=True)

                # WhatsApp Share Button (pre-fills text)
                whatsapp_share_url = f"https://wa.me/?text={urllib.parse.quote(share_message)}"
                with col_share_whatsapp:
                    st.markdown(f'<a href="{whatsapp_share_url}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">Share on WhatsApp</button></a>', unsafe_allow_html=True)

                # --- Automatic HTML Preview Display ---
                st.markdown("---")
                st.markdown("### Generated Certificate Preview (HTML)")
                st.components.v1.html(st.session_state['certificate_html_content_verifier'], height=1200, scrolling=False) 
                st.markdown("---")

            else:
                st.error("Certificate not found or invalid. Please check the ID and try again.")
                st.info("The provided Certificate ID does not match any records in our system. It might be incorrect, or the certificate may not exist.")
                # Clear previous certificate display if not found
                st.session_state['certificate_html_content_verifier'] = ""

    # This block ensures the preview is hidden if the input is cleared or no verification is done yet
    # It also handles clearing if the user manually clears the text input
    if not certificate_id_input and st.session_state['certificate_html_content_verifier']:
        st.session_state['certificate_html_content_verifier'] = ""
        st.rerun() # Rerun to clear the display immediately

if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Certificate Verification", layout="wide")
    certificate_verifier_page()
