import streamlit as st
import requests
import json
import os
import uuid
from datetime import datetime, timedelta, date
import random
import traceback
import time
import pandas as pd
import collections # Import collections for defaultdict
from sentence_transformers import SentenceTransformer # Added import for SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity # Added import for cosine_similarity
import numpy as np # Added import for numpy
import joblib # Added import for joblib to load ML model
import re # Added import for regex for parsing skills
import nltk # Added import for nltk

# CRITICAL: Disable Hugging Face tokenizers parallelism to avoid deadlocks with ProcessPoolExecutor
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Global NLTK download check (should run once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Define global constants (copied from resume_screen.py for consistency and self-containment)
MASTER_CITIES = set([
    "Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Chandigarh", "Kochi", "Coimbatore", "Nagpur", "Bhopal", "Indore", "Gurgaon", "Noida", "Surat", "Visakhapatnam",
    "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi",
    "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi", "Jamshedpur", "Gwalior", "Jabalpur",
    "Vijayawada", "Jodhpur", "Raipur", "Kota", "Guwahati", "Thiruvananthapuram", "Mysuru", "Hubballi-Dharwad",
    "Mangaluru", "Belagavi", "Davangere", "Ballari", "Tumakuru", "Shivamogga", "Bidar", "Hassan", "Gadag-Betageri",
    "Chitradurga", "Udupi", "Kolar", "Mandya", "Chikkamagaluru", "Koppal", "Chamarajanagar", "Yadgir", "Raichur",
    "Kalaburagi", "Bengaluru Rural", "Dakshina Kannada", "Uttara Kannada", "Kodagu", "Chikkaballapur", "Ramanagara",
    "Bagalkot", "Gadag", "Haveri", "Vijayanagara", "Krishnagiri", "Vellore", "Salem", "Erode", "Tiruppur", "Madurai",
    "Tiruchirappalli", "Thanjavur", "Dindigul", "Kanyakumari", "Thoothukudi", "Tirunelveli", "Nagercoil", "Puducherry",
    "Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda", "Bicholim", "Curchorem", "Sanquelim", "Valpoi", "Pernem",
    "Quepem", "Canacona", "Mormugao", "Sanguem", "Dharbandora", "Tiswadi", "Salcete", "Bardez",
    "London", "New York", "Paris", "Berlin", "Tokyo", "Sydney", "Toronto", "Vancouver", "Singapore", "Dubai",
    "San Francisco", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
    "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "Indianapolis",
    "Seattle", "Denver", "Washington D.C.", "Boston", "Nashville", "El Paso", "Detroit", "Oklahoma City",
    "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson",
    "Fresno", "Sacramento", "Mesa", "Atlanta", "Kansas City", "Colorado Springs", "Raleigh", "Miami", "Omaha",
    "Virginia Beach", "Long Beach", "Oakland", "Minneapolis", "Tulsa", "Wichita", "New Orleans", "Cleveland",
    "Tampa", "Honolulu", "Anaheim", "Santa Ana", "St. Louis", "Riverside", "Lexington", "Pittsburgh", "Cincinnati",
    "Anchorage", "Plano", "Newark", "Orlando", "Irvine", "Garland", "Hialeah", "Scottsdale", "North Las Vegas",
    "Chandler", "Laredo", "Chula Vista", "Madison", "Reno", "Buffalo", "Durham", "Rochester", "Winston-Salem",
    "St. Petersburg", "Jersey City", "Toledo", "Lincoln", "Greensboro", "Boise", "Richmond", "Stockton",
    "San Bernardino", "Des Moines", "Modesto", "Fayetteville", "Shreveport", "Akron", "Tacoma", "Aurora",
    "Oxnard", "Fontana", "Montgomery", "Little Rock", "Grand Rapids", "Springfield", "Yonkers", "Augusta",
    "Mobile", "Port St. Lucie", "Denton", "Spokane", "Chattanooga", "Worcester", "Providence", "Fort Lauderdale",
    "Chesapeake", "Fremont", "Baton Rouge", "Santa Clarita", "Birmingham", "Glendale", "Huntsville",
    "Salt Lake City", "Frisco", "McKinney", "Grand Prairie", "Overland Park", "Brownsville", "Killeen",
    "Pasadena", "Olathe", "Dayton", "Savannah", "Fort Collins", "Naples", "Gainesville", "Lakeland", "Sarasota",
    "Daytona Beach", "Melbourne", "Clearwater", "St. Augustine", "Key West", "Fort Myers", "Cape Coral",
    "Coral Springs", "Pompano Beach", "Miami Beach", "West Palm Beach", "Boca Raton", "Fort Pierce",
    "Port Orange", "Kissimmee", "Sanford", "Ocala", "Bradenton", "Palm Bay", "Deltona", "Largo",
    "Deerfield Beach", "Boynton Beach", "Coconut Creek", "Sunrise", "Plantation", "Davie", "Miramar",
    "Hollywood", "Pembroke Pines", "Coral Gables", "Doral", "Aventura", "Sunny Isles Beach", "North Miami",
    "Miami Gardens", "Homestead", "Cutler Bay", "Pinecrest", "Kendall", "Richmond Heights", "West Kendall",
    "East Kendall", "South Miami", "Sweetwater", "Opa-locka", "Florida City", "Golden Glades", "Leisure City",
    "Princeton", "West Perrine", "Naranja", "Goulds", "South Miami Heights", "Country Walk", "The Crossings",
    "Three Lakes", "Richmond West", "Palmetto Bay", "Palmetto Estates", "Perrine", "Cutler Ridge", "Westview",
    "Gladeview", "Brownsville", "Liberty City", "West Little River", "Pinewood", "Ojus", "Ives Estates",
    "Highland Lakes", "Sunny Isles Beach", "Golden Beach", "Bal Harbour", "Surfside", "Bay Harbor Islands",
    "Indian Creek", "North Bay Village", "Biscayne Park", "El Portal", "Miami Shores", "North Miami Beach",
    "Aventura"
])

SKILL_CATEGORIES = {
    "Programming Languages": ["Python", "Java", "JavaScript", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "TypeScript", "R", "Bash Scripting", "Shell Scripting"],
    "Web Technologies": ["HTML5", "CSS3", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", "Express.js", "WebSockets"],
    "Databases": ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Elasticsearch", "Neo4j", "Redis", "BigQuery", "Snowflake", "Redshift", "Aurora", "DynamoDB", "DocumentDB", "CosmosDB"],
    "Cloud Platforms": ["AWS", "Azure", "Google Cloud Platform", "GCP", "Serverless", "AWS Lambda", "Azure Functions", "Google Cloud Functions"],
    "DevOps & MLOps": ["Git", "GitHub", "GitLab", "Bitbucket", "CI/CD", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "CircleCI", "GitHub Actions", "Azure DevOps", "MLOps"],
    "Data Science & ML": ["Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "Data Cleaning", "Feature Engineering",
    "Model Evaluation", "Statistical Modeling", "Time Series Analysis", "Predictive Modeling", "Clustering",
    "Classification", "Regression", "Neural Networks", "Convolutional Networks", "Recurrent Networks",
    "Transformers", "LLMs", "Prompt Engineering", "Generative AI", "MLOps", "Data Munging", "A/B Testing",
    "Experiment Design", "Hypothesis Testing", "Bayesian Statistics", "Causal Inference", "Graph Neural Networks"],
    "Data Analytics & BI": ["Data Cleaning", "Feature Engineering", "Model Evaluation", "Statistical Analysis", "Time Series Analysis", "Data Munging", "A/B Testing", "Experiment Design", "Hypothesis Testing", "Bayesian Statistics", "Causal Inference", "Excel (Advanced)", "Tableau", "Power BI", "Looker", "Qlik Sense", "Google Data Studio", "Dax", "M Query", "ETL", "ELT", "Data Warehousing", "Data Lake", "Data Modeling", "Business Intelligence", "Data Visualization", "Dashboarding", "Report Generation", "Google Analytics"],
    "Soft Skills": ["Stakeholder Management", "Risk Management", "Change Management", "Communication Skills", "Public Speaking", "Presentation Skills", "Cross-functional Collaboration",
    "Problem Solving", "Critical Thinking", "Analytical Skills", "Adaptability", "Time Management",
    "Organizational Skills", "Attention to Detail", "Leadership", "Mentorship", "Team Leadership",
    "Decision Making", "Negotiation", "Client Management", "Stakeholder Communication", "Active Listening",
    "Creativity", "Innovation", "Research", "Data Analysis", "Report Writing", "Documentation"],
    "Project Management": ["Agile Methodologies", "Scrum", "Kanban", "Jira", "Trello", "Product Lifecycle", "Sprint Planning", "Project Charter", "Gantt Charts", "MVP", "Backlog Grooming",
    "Program Management", "Portfolio Management", "PMP", "CSM"],
    "Security": ["Cybersecurity", "Information Security", "Risk Assessment", "Compliance", "GDPR", "HIPAA", "ISO 27001", "Penetration Testing", "Vulnerability Management", "Incident Response", "Security Audits", "Forensics", "Threat Intelligence", "SIEM", "Firewall Management", "Endpoint Security", "IAM", "Cryptography", "Network Security", "Application Security", "Cloud Security"],
    "Other Tools & Frameworks": ["Jira", "Confluence", "Swagger", "OpenAPI", "Zendesk", "ServiceNow", "Intercom", "Live Chat", "Ticketing Systems", "HubSpot", "Salesforce Marketing Cloud",
    "QuickBooks", "SAP FICO", "Oracle Financials", "Workday", "Microsoft Dynamics", "NetSuite", "Adobe Creative Suite", "Canva", "Mailchimp", "Hootsuite", "Buffer", "SEMrush", "Ahrefs", "Moz", "Screaming Frog",
    "JMeter", "Postman", "SoapUI", "SVN", "Perforce", "Asana", "Monday.com", "Miro", "Lucidchart", "Visio", "MS Project", "Primavera", "AutoCAD", "SolidWorks", "MATLAB", "LabVIEW", "Simulink", "ANSYS",
    "CATIA", "NX", "Revit", "ArcGIS", "QGIS", "OpenCV", "NLTK", "SpaCy", "Gensim", "Hugging Face Transformers",
    "Docker Compose", "Helm", "Ansible Tower", "SaltStack", "Chef InSpec", "Terraform Cloud", "Vault",
    "Consul", "Nomad", "Prometheus", "Grafana", "Alertmanager", "Loki", "Tempo", "Jaeger", "Zipkin",
    "Fluentd", "Logstash", "Kibana", "Grafana Loki", "Datadog", "New Relic", "AppDynamics", "Dynatrace",
    "Nagios", "Zabbix", "Icinga", "PRTG", "SolarWinds", "Wireshark", "Nmap", "Metasploit", "Burp Suite",
    "OWASP ZAP", "Nessus", "Qualys", "Rapid7", "Tenable", "CrowdStrike", "SentinelOne", "Palo Alto Networks",
    "Fortinet", "Cisco Umbrella", "Okta", "Auth0", "Keycloak", "Ping Identity", "Active Directory",
    "LDAP", "OAuth", "JWT", "OpenID Connect", "SAML", "MFA", "SSO", "PKI", "TLS/SSL", "VPN", "IDS/IPS",
    "DLP", "CASB", "SOAR", "XDR", "EDR", "MDR", "GRC", "ITIL", "Lean Six Sigma", "CFA", "CPA", "SHRM-CP",
    "PHR", "CEH", "OSCP", "CCNA", "CISSP", "CISM", "CompTIA Security+"]
}

MASTER_SKILLS = set([skill for category_list in SKILL_CATEGORIES.values() for skill in category_list])

# IMPORTANT: REPLACE THESE WITH YOUR ACTUAL DEPLOYMENT URLs
APP_BASE_URL = "https://screenerpro-app.streamlit.app" # <--- **ENSURE THIS IS YOUR APP'S PUBLIC URL**
CERTIFICATE_HOSTING_URL = "https://manav-jain.github.io/screenerpro-certs"

# --- Firebase REST API Functions ---

# Helper function to convert Python data to Firestore REST API format
def _convert_to_firestore_rest_format(data):
    """
    Converts a Python dictionary to the Firestore REST API document format.
    Handles basic types (string, int, float, bool) and lists of strings.
    Nested dictionaries are converted to mapValue.
    """
    fields = {}
    for key, value in data.items():
        if value is None:
            fields[key] = {"nullValue": None}
        elif isinstance(value, bool):
            fields[key] = {"booleanValue": value}
        elif isinstance(value, int):
            fields[key] = {"integerValue": str(value)} # Firestore REST API expects integerValue as string
        elif isinstance(value, float):
            fields[key] = {"doubleValue": value}
        elif isinstance(value, str):
            fields[key] = {"stringValue": value}
        elif isinstance(value, list):
            list_values = []
            for item in value:
                # Recursively convert items in list if they are complex, otherwise stringValue
                if isinstance(item, dict):
                    list_values.append({"mapValue": {"fields": _convert_to_firestore_rest_format(item)["fields"]}})
                elif isinstance(item, list):
                    # Handle nested lists by stringifying for simplicity, or implement deeper recursion
                    list_values.append({"stringValue": json.dumps(item)})
                elif isinstance(item, (int, float)):
                    list_values.append({"doubleValue": float(item)})
                elif isinstance(item, bool):
                    list_values.append({"booleanValue": item})
                else:
                    list_values.append({"stringValue": str(item)})
            fields[key] = {"arrayValue": {"values": list_values}}
        elif isinstance(value, dict):
            fields[key] = {"mapValue": {"fields": _convert_to_firestore_rest_format(value)["fields"]}}
        else:
            fields[key] = {"stringValue": str(value)} # Fallback for other types
    return {"fields": fields}

def save_screening_result_to_firestore_rest(result_data):
    """
    Saves a single screening result to Firestore using the REST API.
    Requires FIREBASE_PROJECT_ID and FIREBASE_API_KEY in st.secrets.
    """
    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
        
        # Firestore collection path (using 'leaderboard' as before)
        # Note: For public data, your Firestore security rules must allow unauthenticated writes
        # or you need to implement user authentication and pass an ID token.
        collection_id = "leaderboard" 
        
        # Firestore REST API endpoint for creating a document with an auto-generated ID
        # To specify an ID, you'd use PATCH /v1/projects/{project_id}/databases/(default)/documents/{collection_id}/{document_id}
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}"

        # Prepare data for Firestore REST API
        # Ensure 'Matched Keywords (Categorized)' and 'Missing Skills (Categorized)' are dicts, not JSON strings
        data_to_send = result_data.copy()
        if isinstance(data_to_send.get('Matched Keywords (Categorized)'), str):
            try:
                data_to_send['Matched Keywords (Categorized)'] = json.loads(data_to_send['Matched Keywords (Categorized)'])
            except json.JSONDecodeError:
                data_to_send['Matched Keywords (Categorized)'] = {} # Fallback
        if isinstance(data_to_send.get('Missing Skills (Categorized)'), str):
            try:
                data_to_send['Missing Skills (Categorized)'] = json.loads(data_to_send['Missing Skills (Categorized)'])
            except json.JSONDecodeError:
                data_to_send['Missing Skills (Categorized)'] = {} # Fallback

        # Convert datetime.date objects to string for JSON serialization
        if isinstance(data_to_send.get('Date Screened'), (datetime, date)):
            data_to_send['Date Screened'] = data_to_send['Date Screened'].strftime("%Y-%m-%d")

        # Remove raw text if it's too large or not needed in leaderboard
        data_to_send.pop('Resume Raw Text', None)

        firestore_payload = _convert_to_firestore_rest_format(data_to_send)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(firestore_payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        st.success(f"📈 Your score has been added to the leaderboard via REST API!")
        st.info("Remember: For write access, your Firestore security rules must allow it. For production, consider secure authentication.")

    except KeyError as e:
        st.error(f"❌ Firebase REST API configuration error: Missing secret key '{e}'.")
        st.info("Please ensure 'FIREBASE_PROJECT_ID' and 'FIREBASE_API_KEY' are correctly set in your secrets.toml or Streamlit Cloud secrets.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Failed to save results to leaderboard via REST API: HTTP Error {e.response.status_code}")
        st.error(f"Response: {e.response.text}")
        st.warning("This often indicates an issue with Firestore security rules (e.g., write access denied) or incorrect API key/project ID.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while saving to leaderboard via REST API: {e}")
        st.exception(e)


# Global variable for app ID (as provided by the environment)
# This assumes __app_id is available in the Streamlit environment.
# If running locally without this, you might need to hardcode a default or set it via env var.
appId = os.environ.get('__app_id', 'default-screener-pro-app')


# Removed get_tesseract_cmd as Tesseract is no longer used.

# Load ML models once using st.cache_resource
@st.cache_resource
def load_ml_model():
    with st.spinner("Loading AI models... This may take a moment."): # Added spinner here
        try:
            # SentenceTransformer is used for generating embeddings for semantic similarity
            model = SentenceTransformer("all-MiniLM-L6-v2")
            # This is your custom ML model for score prediction
            ml_model = joblib.load("ml_screening_model.pkl")
            return model, ml_model
        except Exception as e:
            st.error(f"❌ Error loading ML models: {e}. Please ensure 'ml_screening_model.pkl' is in the same directory.")
            return None, None

# Load models globally (once per app run)
global_sentence_model, global_ml_model = load_ml_model()

# Pre-compile regex patterns for efficiency
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.\w+')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
CGPA_PATTERN = re.compile(r'(?:cgpa|gpa|grade point average)\s*[:\s]*(\d+\.\d+)(?:\s*[\/of]{1,4}\s*(\d+\.\d+|\d+))?|(\d+\.\d+)(?:\s*[\/of]{1,4}\s*(\d+\.\d+|\d+))?\s*(?:cgpa|gpa)')
EXP_DATE_PATTERNS = [
    re.compile(r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})\s*(?:to|–|-)\s*(present|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})'),
    re.compile(r'(\b\d{4})\s*(?:to|–|-)\s*(present|\b\d{4})')
]
EXP_YEARS_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(\+)?\s*(year|yrs|years)\b')
EXP_FALLBACK_PATTERN = re.compile(r'experience[^\d]{0,10}(\d+(?:\.\d+)?)')
NAME_EXCLUDE_TERMS = {
    "linkedin", "github", "portfolio", "resume", "cv", "profile", "contact", "email", "phone",
    "mobile", "number", "tel", "telephone", "address", "website", "site", "social", "media",
    "url", "link", "blog", "personal", "summary", "about", "objective", "dob", "birth", "age",
    "nationality", "gender", "location", "city", "country", "pin", "zipcode", "state", "whatsapp",
    "skype", "telegram", "handle", "id", "details", "connection", "reach", "network", "www",
    "https", "http", "contactinfo", "connect", "reference", "references","fees"
}
EDU_MATCH_PATTERN = re.compile(r'([A-Za-z0-9.,()&\-\s]+?(university|college|institute|school)[^–\n]{0,50}[–\-—]?\s*(expected\s*)?\d{4})', re.IGNORECASE)
EDU_FALLBACK_PATTERN = re.compile(r'([A-Za-z0-9.,()&\-\s]+?(b\.tech|m\.tech|b\.sc|m\.sc|bca|bba|mba|ph\.d)[^–\n]{0,50}\d{4})', re.IGNORECASE)
WORK_HISTORY_SECTION_PATTERN = re.compile(r'(?:experience|work history|employment history)\s*(\n|$)', re.IGNORECASE)
JOB_BLOCK_SPLIT_PATTERN = re.compile(r'\n(?=[A-Z][a-zA-Z\s,&\.]+(?:\s(?:at|@))?\s*[A-Z][a-zA-Z\s,&\.]*\s*(?:-|\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}))', re.IGNORECASE)
DATE_RANGE_MATCH_PATTERN = re.compile(r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4})\s*[-–]\s*(present|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4})', re.IGNORECASE)
TITLE_COMPANY_MATCH_PATTERN = re.compile(r'([A-Z][a-zA-Z\s,\-&.]+)\s+(?:at|@)\s+([A-Z][a-zA-Z\s,\-&.]+)')
COMPANY_TITLE_MATCH_PATTERN = re.compile(r'^([A-Z][a-zA-Z\s,\-&.]+),\s*([A-Z][a-zA-Z\s,\-&.]+)')
POTENTIAL_ORG_MATCH_PATTERN = re.compile(r'^[A-Z][a-zA-Z\s,\-&.]+')
PROJECT_SECTION_KEYWORDS = re.compile(r'(projects|personal projects|key projects|portfolio|selected projects|major projects|academic projects|relevant projects)\s*(\n|$)', re.IGNORECASE)
FORBIDDEN_TITLE_KEYWORDS = [
    'skills gained', 'responsibilities', 'reflection', 'summary',
    'achievements', 'capabilities', 'what i learned', 'tools used'
]
PROJECT_TITLE_START_PATTERN = re.compile(r'^[•*-]?\s*\d+[\).:-]?\s')
LANGUAGE_SECTION_PATTERN = re.compile(r'\b(languages|language skills|linguistic abilities|known languages)\s*[:\-]?\s*\n?', re.IGNORECASE)


def clean_text(text):
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip().lower()

def extract_relevant_keywords(text, filter_set):
    cleaned_text = clean_text(text)
    extracted_keywords = set()
    categorized_keywords = collections.defaultdict(list)

    if filter_set:
        # Create a lowercase version of the filter_set for efficient lookup
        filter_set_lower = {s.lower() for s in filter_set}
        
        # Prioritize multi-word skills/phrases first
        sorted_filter_skills = sorted([s for s in filter_set if ' ' in s], key=len, reverse=True)
        
        temp_text = cleaned_text

        for skill_phrase in sorted_filter_skills:
            pattern = r'\b' + re.escape(skill_phrase.lower()) + r'\b'
            
            if re.search(pattern, temp_text): # Use search instead of findall for simple presence check
                extracted_keywords.add(skill_phrase.lower())
                found_category = False
                for category, skills_in_category in SKILL_CATEGORIES.items():
                    if skill_phrase.lower() in {s.lower() for s in skills_in_category}:
                        categorized_keywords[category].append(skill_phrase)
                        found_category = True
                        break
                if not found_category:
                    categorized_keywords["Uncategorized"].append(skill_phrase)

                # Replace found phrase to avoid re-matching parts of it
                temp_text = re.sub(pattern, " ", temp_text)
        
        # Now process individual words from the remaining text
        individual_words_remaining = set(re.findall(r'\b\w+\b', temp_text))
        for word in individual_words_remaining:
            if word in filter_set_lower: # Efficient lookup in the lowercase set
                extracted_keywords.add(word)
                found_category = False
                for category, skills_in_category in SKILL_CATEGORIES.items():
                    if word.lower() in {s.lower() for s in skills_in_category}:
                        categorized_keywords[category].append(word)
                        found_category = True
                        break
                if not found_category:
                    categorized_keywords["Uncategorized"].append(word)

    else:
        all_words = set(re.findall(r'\b\w+\b', cleaned_text))
        extracted_keywords = {word for word in all_words if word not in STOP_WORDS}
        for word in extracted_keywords:
            categorized_keywords["General Keywords"].append(word)

    return extracted_keywords, dict(categorized_keywords)


def extract_text_from_file(file_bytes, file_name, file_type):
    full_text = ""
    
    if "pdf" in file_type:
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                full_text = ''.join(page.extract_text() or '' for page in pdf.pages)
            
            if not full_text.strip():
                return f"[ERROR] No readable text extracted from PDF. It might be a scanned PDF. Please upload a text-selectable PDF."

        except Exception as e:
            print(f"ERROR: Failed to extract text from PDF for {file_name}: {str(e)}")
            return f"[ERROR] Failed to extract text from PDF: {str(e)}. Ensure it's a text-selectable PDF, not a scanned image."

    elif "image" in file_type:
        return f"[ERROR] Image files are not supported for text extraction in this version. Please upload a PDF."
    else:
        return f"[ERROR] Unsupported file type: {file_type}. Please upload a PDF."

    if not full_text.strip():
        return "[ERROR] No readable text extracted from the file. It might be an empty document."
    
    return full_text


def extract_years_of_experience(text):
    text = text.lower()
    total_months = 0
    
    for pattern in EXP_DATE_PATTERNS: # Use pre-compiled patterns
        job_date_ranges = pattern.findall(text)
        for start_str, end_str in job_date_ranges:
            start_date = None
            end_date = None

            try:
                start_date = datetime.strptime(start_str.strip(), '%B %Y')
            except ValueError:
                try:
                    start_date = datetime.strptime(start_str.strip(), '%b %Y')
                except ValueError:
                    try:
                        start_date = datetime(int(start_str.strip()), 1, 1)
                    except ValueError:
                        pass

            if start_date is None:
                continue

            if end_str.strip() == 'present':
                end_date = datetime.now()
            else:
                try:
                    end_date = datetime.strptime(end_str.strip(), '%B %Y')
                except ValueError:
                    try:
                        end_date = datetime.strptime(end_str.strip(), '%b %Y')
                    except ValueError:
                        try:
                            end_date = datetime(int(end_str.strip()), 12, 31)
                        except ValueError:
                            pass
            
            if end_date is None:
                continue

            delta_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += max(delta_months, 0)

    if total_months > 0:
        return round(total_months / 12, 1)
    else:
        match = EXP_YEARS_PATTERN.search(text) # Use pre-compiled pattern
        if not match:
            match = EXP_FALLBACK_PATTERN.search(text) # Use pre-compiled pattern
        if match:
            return float(match.group(1))

    return 0.0

def extract_email(text):
    text = text.lower()

    text = text.replace("gmaill.com", "gmail.com").replace("gmai.com", "gmail.com")
    text = text.replace("yah00", "yahoo").replace("outiook", "outlook")
    text = text.replace("coim", "com").replace("hotmai", "hotmail")

    text = re.sub(r'[^\w\s@._+-]', ' ', text)

    possible_emails = EMAIL_PATTERN.findall(text) # Use pre-compiled pattern

    if possible_emails:
        for email in possible_emails:
            if "gmail" in email or "manav" in email: # Specific filter, consider removing or making configurable
                return email
        return possible_emails[0]
    
    return None

def extract_phone_number(text):
    match = PHONE_PATTERN.search(text) # Use pre-compiled pattern
    return match.group(0) if match else None

def extract_location(text):
    found_locations = set()
    text_lower = text.lower()

    sorted_cities = sorted(list(MASTER_CITIES), key=len, reverse=True)

    for city in sorted_cities:
        pattern = r'\b' + re.escape(city.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_locations.add(city)

    if found_locations:
        return ", ".join(sorted(list(found_locations)))
    return "Not Found"

def extract_name(text):
    lines = text.strip().split('\n')
    if not lines:
        return None

    potential_name_lines = []
    for line in lines[:5]:
        line = line.strip()
        line_lower = line.lower()

        if not re.search(r'[@\d\.\-]', line) and \
           len(line.split()) <= 4 and \
           not any(term in line_lower for term in NAME_EXCLUDE_TERMS): # Use pre-defined set
            if line.isupper() or (line and line[0].isupper() and all(word[0].isupper() or not word.isalpha() for word in line.split())):
                potential_name_lines.append(line)

    if potential_name_lines:
        name = max(potential_name_lines, key=len)
        name = re.sub(r'summary|education|experience|skills|projects|certifications|profile|contact', '', name, flags=re.IGNORECASE).strip()
        name = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', name).strip()
        if name:
            return name.title()
    return None

def extract_cgpa(text):
    text = text.lower()
    
    matches = CGPA_PATTERN.findall(text) # Use pre-compiled pattern

    for match in matches:
        if match[0] and match[0].strip():
            raw_cgpa = float(match[0])
            scale = float(match[1]) if match[1] else None
        elif match[2] and match[2].strip():
            raw_cgpa = float(match[2])
            scale = float(match[3]) if match[3] else None
        else:
            continue

        if scale and scale not in [0, 1]:
            normalized_cgpa = (raw_cgpa / scale) * 4.0
            return round(normalized_cgpa, 2)
        elif raw_cgpa <= 4.0:
            return round(raw_cgpa, 2)
        elif raw_cgpa <= 10.0:
            return round((raw_cgpa / 10.0) * 4.0, 2)
        
    return None

def extract_education_text(text):
    """
    Extracts a single-line education entry from resume text.
    Returns a clean string like: "B.Tech in CSE, Alliance University, Bangalore – 2028"
    Works with or without 'Expected' in the year.
    """

    text = text.replace('\r', '').replace('\t', ' ')
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    education_section = ''
    capture = False

    for line in lines:
        line_lower = line.lower()
        if any(h in line_lower for h in ['education', 'academic background', 'qualifications']):
            capture = True
            continue
        if capture and any(h in line_lower for h in ['experience', 'skills', 'certifications', 'projects', 'languages']):
            break
        if capture:
            education_section += line + ' '

    education_section = education_section.strip()

    edu_match = EDU_MATCH_PATTERN.search(education_section) # Use pre-compiled pattern

    if edu_match:
        return edu_match.group(1).strip()

    fallback_match = EDU_FALLBACK_PATTERN.search(education_section) # Use pre-compiled pattern
    if fallback_match:
        return fallback_match.group(1).strip()

    fallback_line = education_section.split('.')[0].strip()
    return fallback_line if fallback_line else None

def extract_work_history(text):
    work_history_section_matches = WORK_HISTORY_SECTION_PATTERN.finditer(text) # Use pre-compiled pattern
    work_details = []
    
    start_index = -1
    for match in work_history_section_matches:
        start_index = match.end()
        break

    if start_index != -1:
        sections = ['education', 'skills', 'projects', 'certifications', 'awards', 'publications']
        end_index = len(text)
        for section in sections:
            section_match = re.search(r'\b' + re.escape(section) + r'\b', text[start_index:], re.IGNORECASE)
            if section_match:
                end_index = start_index + section_match.start()
                break
        
        work_text = text[start_index:end_index].strip()
        
        job_blocks = JOB_BLOCK_SPLIT_PATTERN.split(work_text) # Use pre-compiled pattern
        
        for block in job_blocks:
            block = block.strip()
            if not block:
                continue
            
            company = None
            title = None
            start_date = None
            end_date = None

            date_range_match = DATE_RANGE_MATCH_PATTERN.search(block) # Use pre-compiled pattern
            if date_range_match:
                start_date = date_range_match.group(1)
                end_date = date_range_match.group(2)
                block = block.replace(date_range_match.group(0), '').strip()

            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue

                title_company_match = TITLE_COMPANY_MATCH_PATTERN.search(line) # Use pre-compiled pattern
                if title_company_match:
                    title = title_company_match.group(1).strip()
                    company = title_company_match.group(2).strip()
                    break
                
                company_title_match = COMPANY_TITLE_MATCH_PATTERN.search(line) # Use pre-compiled pattern
                if company_title_match:
                    company = company_title_match.group(1).strip()
                    title = company_title_match.group(2).strip()
                    break
                
                if not company and not title:
                    potential_org_match = POTENTIAL_ORG_MATCH_PATTERN.search(line) # Use pre-compiled pattern
                    if potential_org_match and len(potential_org_match.group(0).split()) > 1:
                        if not company: company = potential_org_match.group(0).strip()
                        elif not title: title = potential_org_match.group(0).strip()
                        break

            if company or title or start_date or end_date:
                work_details.append({
                    "Company": company,
                    "Title": title,
                    "Start Date": start_date,
                    "End Date": end_date
                })
    return work_details

def extract_project_details(text, MASTER_SKILLS):
    """
    Extracts real project entries from resume text.
    Returns a list of dicts: Title, Description, Technologies Used
    """

    project_details = []

    text = text.replace('\r', '').replace('\t', ' ')
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    # Step 1: Isolate project section
    project_section_match = PROJECT_SECTION_KEYWORDS.search(text) # Use pre-compiled pattern

    if not project_section_match:
        project_text = text[:1000]  # fallback to first 1000 chars
        start_index = 0
    else:
        start_index = project_section_match.end()
        sections = ['education', 'skills', 'certifications', 'awards', 'publications', 'interests', 'hobbies']
        end_index = len(text)
        for section in sections:
            match = re.search(r'\b' + re.escape(section) + r'\b', text[start_index:], re.IGNORECASE)
            if match:
                end_index = start_index + match.start()
                break
        project_text = text[start_index:end_index].strip()

    if not project_text:
        return []

    lines = [line.strip() for line in project_text.split('\n') if line.strip()]
    current_project = {"Project Title": None, "Description": [], "Technologies Used": set()}

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Skip all-uppercase names or headers
        if re.match(r'^[A-Z\s]{5,}$', line) and len(line.split()) <= 4:
            continue

        # Previous line was a bullet?
        prev_line_is_bullet = False
        if i > 0 and re.match(r'^[•*-]', lines[i - 1]):
            prev_line_is_bullet = True

        # Strong new project title if:
        # - starts with number or bullet
        # - not just a soft skill block
        # - contains 3–15 words
        # - not all caps
        is_title = (
            (PROJECT_TITLE_START_PATTERN.match(line) or line.lower().startswith("project")) and # Use pre-compiled pattern
            3 <= len(line.split()) <= 15 and
            not any(kw in line_lower for kw in FORBIDDEN_TITLE_KEYWORDS) and
            not prev_line_is_bullet and
            not line.isupper()
        )

        is_url = re.match(r'https?://', line_lower)

        # New Project Begins
        if is_title or is_url:
            if current_project["Project Title"] or current_project["Description"]:
                full_desc = "\n".join(current_project["Description"])
                techs, _ = extract_relevant_keywords(full_desc, MASTER_SKILLS)
                current_project["Technologies Used"].update(techs)

                project_details.append({
                    "Project Title": current_project["Project Title"],
                    "Description": full_desc.strip(),
                    "Technologies Used": ", ".join(sorted(current_project["Technologies Used"]))
                })

            current_project = {"Project Title": line, "Description": [], "Technologies Used": set()}
        else:
            current_project["Description"].append(line)

    # Add last project
    if current_project["Project Title"] or current_project["Description"]:
        full_desc = "\n".join(current_project["Description"])
        techs, _ = extract_relevant_keywords(full_desc, MASTER_SKILLS)
        current_project["Technologies Used"].update(techs)

        project_details.append({
            "Project Title": current_project["Project Title"],
            "Description": full_desc.strip(),
            "Technologies Used": ", ".join(sorted(current_project["Technologies Used"]))
        })

    return project_details


def extract_languages(text):
    """
    Extracts known languages from resume text.
    Returns a comma-separated string of detected languages or 'Not Found'.
    """
    languages_list = set()
    cleaned_full_text = clean_text(text)

    # De-duplicated, lowercase language set
    all_languages = list(set([
        "english", "hindi", "spanish", "french", "german", "mandarin", "japanese", "arabic",
        "russian", "portuguese", "italian", "korean", "bengali", "marathi", "telugu", "tamil",
        "gujarati", "urdu", "kannada", "odia", "malayalam", "punjabi", "assamese", "kashmiri",
        "sindhi", "sanskrit", "dutch", "swedish", "norwegian", "danish", "finnish", "greek",
        "turkish", "hebrew", "thai", "vietnamese", "indonesian", "malay", "filipino", "swahili",
        "farsi", "persian", "polish", "ukrainian", "romanian", "czech", "slovak", "hungarian",
        "chinese", "tagalog", "nepali", "sinhala", "burmese", "khmer", "lao", "pashto", "dari",
        "uzbek", "kazakh", "azerbaijani", "georgian", "armenian", "albanian", "serbian",
        "croatian", "bosnian", "bulgarian", "macedonian", "slovenian", "estonian", "latvian",
        "lithuanian", "icelandic", "irish", "welsh", "gaelic", "maltese", "esperanto", "latin",
        "ancient greek", "modern greek", "yiddish", "romani", "catalan", "galician", "basque",
        "breton", "cornish", "manx", "frisian", "luxembourgish", "sami", "romansh", "sardinian",
        "corsican", "occitan", "provencal", "walloon", "flemish", "afrikaans", "zulu", "xhosa",
        "sesotho", "setswana", "shona", "ndebele", "venda", "tsonga", "swati", "kikuyu",
        "luganda", "kinyarwanda", "kirundi", "lingala", "kongo", "yoruba", "igbo", "hausa",
        "fulani", "twi", "ewe", "ga", "dagbani", "gur", "mossi", "bambara", "senufo", "wolof",
        "mandinka", "susu", "krio", "temne", "limba", "mende", "gola", "vai", "kpelle", "loma",
        "bandi", "bassa", "grebo", "krahn", "dan", "mano", "guerze", "kono", "kisi"
    ]))

    sorted_all_languages = sorted(all_languages, key=len, reverse=True)

    # Step 1: Try to locate a language-specific section
    section_match = LANGUAGE_SECTION_PATTERN.search(cleaned_full_text) # Use pre-compiled pattern

    if section_match:
        start_index = section_match.end()
        # Optional: stop at next known section
        end_index = len(cleaned_full_text)
        stop_words = ['education', 'experience', 'skills', 'certifications', 'awards', 'publications', 'interests', 'hobbies']
        for stop in stop_words:
            m = re.search(r'\b' + stop + r'\b', cleaned_full_text[start_index:], re.IGNORECASE)
            if m:
                end_index = start_index + m.start()
                break

        language_chunk = cleaned_full_text[start_index:end_index]
    else:
        language_chunk = cleaned_full_text

    # Step 2: Match known languages
    for lang in sorted_all_languages:
        # Use word boundaries for exact matches and allow for common suffixes like " (fluent)"
        pattern = r'\b' + re.escape(lang) + r'(?:\s*\(?[a-z\s,-]+\)?)?\b'
        if re.search(pattern, language_chunk, re.IGNORECASE):
            if lang == "de":
                languages_list.add("German")
            else:
                languages_list.add(lang.title())

    return ", ".join(sorted(languages_list)) if languages_list else "Not Found"


def format_work_history(work_list):
    if not work_list:
        return "Not Found"
    formatted_entries = []
    for entry in work_list:
        parts = []
        if entry.get("Title"):
            parts.append(entry["Title"])
        if entry.get("Company"):
            parts.append(f"at {entry['Company']}")
        if entry.get("Start Date") and entry.get("End Date"):
            parts.append(f"({entry['Start Date']} - {entry['End Date']})")
        elif entry.get("Start Date"):
            parts.append(f"(Since {entry['Start Date']})")
        formatted_entries.append(" ".join(parts).strip())
    return "; ".join(formatted_entries) if formatted_entries else "Not Found"

def format_project_details(proj_list):
    if not proj_list:
        return "Not Found"
    formatted_entries = []
    for entry in proj_list:
        parts = []
        if entry.get("Project Title"):
            parts.append(f"**{entry['Project Title']}**")
        if entry.get("Technologies Used"):
            parts.append(f"({entry['Technologies Used']})")
        if entry.get("Description") and entry["Description"].strip():
            desc_snippet = entry["Description"].split('\n')[0][:50] + "..." if len(entry["Description"]) > 50 else entry["Description"]
            parts.append(f'"{desc_snippet}"')
        formatted_entries.append(" ".join(parts).strip())
    return "; ".join(formatted_entries) if formatted_entries else "Not Found"

@st.cache_data(show_spinner="Generating concise AI Suggestion...")
def generate_concise_ai_suggestion(candidate_name, score, years_exp, semantic_similarity, cgpa):
    overall_fit_description = ""
    review_focus_text = ""
    key_strength_hint = ""

    high_score = 85
    moderate_score = 65
    high_exp = 4
    moderate_exp = 2
    high_sem_sim = 0.75
    moderate_sem_sim = 0.4
    high_cgpa = 3.5
    moderate_cgpa = 3.0

    if score >= high_score and years_exp >= high_exp and semantic_similarity >= high_sem_sim:
        overall_fit_description = "High alignment."
        key_strength_hint = "Strong technical and experience match, quick integration expected."
        review_focus_text = "Cultural fit, project contributions."
    elif score >= moderate_score and years_exp >= moderate_exp and semantic_similarity >= moderate_sem_sim:
        overall_fit_description = "Moderate fit."
        key_strength_hint = "Good foundational skills, potential for growth."
        review_focus_text = "Depth of experience, skill application, learning agility."
    else:
        overall_fit_description = "Limited alignment."
        key_strength_hint = "May require significant development or a different role."
        review_focus_text = "Foundational skills, transferable experience, long-term potential."

    cgpa_note = ""
    if cgpa is not None:
        if cgpa >= high_cgpa:
            cgpa_note = "Excellent academic record. "
        elif cgpa >= moderate_cgpa:
            cgpa_note = "Solid academic background. "
        else:
            cgpa_note = "Academic record may need review. "
    else:
        cgpa_note = "CGPA not found. "

    summary_text = f"**Fit:** {overall_fit_description} **Strengths:** {cgpa_note}{key_strength_hint} **Focus:** {review_focus_text}"
    return summary_text

@st.cache_data(show_spinner="Generating detailed HR Assessment...")
def generate_detailed_hr_assessment(candidate_name, score, years_exp, semantic_similarity, cgpa, jd_text, resume_text, matched_keywords, missing_skills, max_exp_cutoff):
    assessment_parts = []
    overall_assessment_title = ""
    next_steps_focus = ""

    matched_kws_str = ", ".join(matched_keywords) if isinstance(matched_keywords, list) else matched_keywords
    missing_skills_str = ", ".join(missing_skills) if isinstance(missing_skills, list) else missing_skills

    high_score = 90
    strong_score = 80
    promising_score = 60
    high_exp = 5
    strong_exp = 3
    promising_exp = 1
    high_sem_sim = 0.85
    strong_sem_sim = 0.7
    promising_sem_sim = 0.35
    high_cgpa = 3.5
    strong_cgpa = 3.0
    promising_cgpa = 2.5

    if score >= high_score and years_exp >= high_exp and years_exp <= max_exp_cutoff and semantic_similarity >= high_sem_sim and (cgpa is None or cgpa >= high_cgpa):
        overall_assessment_title = "Exceptional Candidate: Highly Aligned with Strategic Needs"
        assessment_parts.append(f"**{candidate_name}** presents an **exceptional profile** with a high score of {score:.2f}% and {years_exp:.1f} years of experience. This demonstrates a profound alignment with the job description's core requirements, further evidenced by a strong semantic similarity of {semantic_similarity:.2f}.")
        if cgpa is not None:
            assessment_parts.append(f"Their academic record, with a CGPA of {cgpa:.2f} (normalized to 4.0 scale), further solidifies their strong foundational knowledge.")
        assessment_parts.append(f"**Key Strengths:** This candidate possesses a robust skill set directly matching critical keywords in the JD, including: *{matched_kws_str if matched_kws_str else 'No specific keywords listed, but overall strong match'}*. Their extensive experience indicates a capacity for leadership and handling complex challenges, suggesting immediate productivity and minimal ramp-up time. They are poised to make significant contributions from day one.")
        assessment_parts.append("The resume highlights a clear career progression and a history of successful project delivery, often exceeding expectations. Their qualifications exceed expectations, making them a top-tier applicant for this role.")
        assessment_parts.append("This individual's profile suggests they are not only capable of fulfilling the role's duties but also have the potential to mentor others, drive innovation, and take on strategic initiatives within the team. Their background indicates a strong fit for a high-impact position.")
        next_steps_focus = "The next steps should focus on assessing cultural integration, exploring leadership potential, and delving into strategic contributions during the interview. Prepare for a deep dive into their most challenging projects, how they navigated complex scenarios, and their long-term vision. Consider fast-tracking this candidate through the interview process and potentially involving senior leadership early on."
        assessment_parts.append(f"**Action:** Strongly recommend for immediate interview. Prioritize for hiring and consider for advanced roles if applicable.")

    elif score >= strong_score and years_exp >= strong_exp and years_exp <= max_exp_cutoff and semantic_similarity >= strong_sem_sim and (cgpa is None or cgpa >= strong_cgpa):
        overall_assessment_title = "Strong Candidate: Excellent Potential for Key Contributions"
        assessment_parts.append(f"**{candidate_name}** is a **strong candidate** with a score of {score:.2f}% and {years_exp:.1f} years of experience. They show excellent alignment with the job description, supported by a solid semantic similarity of {semantic_similarity:.2f}.")
        if cgpa is not None:
            assessment_parts.append(f"Their academic performance, with a CGPA of {cgpa:.2f}, indicates a solid theoretical grounding.")
        assessment_parts.append(f"**Key Strengths:** Significant overlap in required skills and practical experience that directly addresses the job's demands. Matched keywords include: *{matched_kws_str if matched_kws_str else 'No specific keywords listed, but overall strong match'}*. This individual is likely to integrate well and contribute effectively from an early stage, bringing valuable expertise to the team.")
        assessment_parts.append("Their resume indicates a consistent track record of achieving results and adapting to new challenges. They demonstrate a solid understanding of the domain and could quickly become a valuable asset, requiring moderate onboarding.")
        assessment_parts.append("This candidate is well-suited for the role and demonstrates the core competencies required. Their experience suggests they can handle typical challenges and contribute positively to team dynamics.")
        next_steps_focus = "During the interview, explore specific project methodologies, problem-solving approaches, and long-term career aspirations to confirm alignment with team dynamics and growth opportunities within the company. Focus on behavioral questions to understand their collaboration style, initiative, and how they handle feedback. A technical assessment might be beneficial to confirm depth of skills."
        assessment_parts.append(f"**Action:** Recommend for interview. Good fit for the role, with potential for growth.")

    elif score >= promising_score and years_exp >= promising_exp and years_exp <= max_exp_cutoff and semantic_similarity >= promising_sem_sim and (cgpa is None or cgpa >= promising_cgpa):
        overall_assessment_title = "Promising Candidate: Requires Focused Review on Specific Gaps"
        assessment_parts.append(f"**{candidate_name}** is a **promising candidate** with a score of {score:.2f}% and {years_exp:.1f} years of experience. While demonstrating a foundational understanding (semantic similarity: {semantic_similarity:.2f}), there are areas that warrant deeper investigation to ensure a complete fit.")
        
        gaps_identified = []
        if score < 70:
            gaps_identified.append("The overall score suggests some core skill areas may need development or further clarification.")
        if years_exp < promising_exp:
            gaps_identified.append(f"Experience ({years_exp:.1f} yrs) is on the lower side; assess their ability to scale up quickly and take on more responsibility.")
        if semantic_similarity < 0.5:
            gaps_identified.append("Semantic understanding of the JD's nuances might be limited; probe their theoretical knowledge versus practical application in real-world scenarios.")
        if cgpa is not None and cgpa < promising_cgpa:
            gaps_identified.append(f"Academic record (CGPA: {cgpa:.2f}) is below preferred, consider its relevance to role demands.")
        if missing_skills_str:
            gaps_identified.append(f"**Potential Missing Skills:** *{missing_skills_str}*. Focus interview questions on these areas to assess their current proficiency or learning agility.")
        
        if years_exp > max_exp_cutoff:
            gaps_identified.append(f"Experience ({years_exp:.1f} yrs) exceeds the maximum desired ({max_exp_cutoff} yrs). Evaluate if this indicates overqualification or a potential mismatch in role expectations.")

        if gaps_identified:
            assessment_parts.append("Areas for further exploration include: " + " ".join(gaps_identified))
        
        assessment_parts.append("The candidate shows potential, especially if they can demonstrate quick learning or relevant transferable skills. Their resume indicates a willingness to grow and take on new challenges, which is a positive sign for development opportunities.")
        next_steps_focus = "The interview should focus on validating foundational skills, understanding their learning agility, and assessing their potential for growth within the role. Be prepared to discuss specific examples of how they've applied relevant skills and how they handle challenges, particularly in areas where skills are missing. Consider a skills assessment or a structured case study to gauge problem-solving abilities. Discuss their motivation for this role and long-term career goals."
        assessment_parts.append(f"**Action:** Consider for initial phone screen or junior role. Requires careful evaluation and potentially a development plan.")

    else:
        overall_assessment_title = "Limited Match: Consider Only for Niche Needs or Pipeline Building"
        assessment_parts.append(f"**{candidate_name}** shows a **limited match** with a score = {score:.2f}% and {years_exp:.1f} years of experience (semantic similarity: {semantic_similarity:.2f}). This profile indicates a significant deviation from the core requirements of the job description.")
        if cgpa is not None:
            assessment_parts.append(f"Their academic record (CGPA: {cgpa:.2f}) also indicates a potential mismatch.")
        assessment_parts.append(f"**Key Concerns:** A low overlap in essential skills and potentially insufficient experience for the role's demands. Many key skills appear to be missing: *{missing_skills_str if missing_skills_str else 'No specific missing skills listed, but overall low match'}*. While some transferable skills may exist, a substantial investment in training or a re-evaluation of role fit would likely be required for this candidate to succeed.")
        
        if years_exp > max_exp_cutoff:
            assessment_parts.append(f"Additionally, their experience ({years_exp:.1f} yrs) significantly exceeds the maximum desired ({max_exp_cutoff} yrs), which might indicate overqualification or a mismatch in career trajectory for this specific opening.")

        assessment_parts.append("The resume does not strongly align with the technical or experience demands of this specific position. Their background may be more suited for a different type of role or industry, or an entry-level position if their core skills are strong but experience is lacking.")
        assessment_parts.append("This candidate might not be able to meet immediate role requirements without extensive support. Their current profile suggests a mismatch with the current opening.")
        next_steps_focus = "This candidate is generally not recommended for the current role unless there are specific, unforeseen niche requirements or a strategic need to broaden the candidate pool significantly. If proceeding, focus on understanding their fundamental capabilities, their motivation for this specific role despite the mismatch, and long-term career aspirations. It might be more beneficial to suggest other roles within the organization or provide feedback for future applications."
        assessment_parts.append(f"**Action:** Not recommended for this role. Consider for other open positions or future pipeline, or politely decline.")

    final_assessment = f"**Overall HR Assessment: {overall_assessment_title}**\n\n"
    final_assessment += "\n".join(assessment_parts)

    return final_assessment

def semantic_score_calculation(jd_embedding, resume_embedding, years_exp, cgpa, weighted_keyword_overlap_score, _ml_model):
    score = 0.0
    semantic_similarity = cosine_similarity(jd_embedding.reshape(1, -1), resume_embedding.reshape(1, -1))[0][0]
    semantic_similarity = float(np.clip(semantic_similarity, 0, 1))

    if _ml_model is None:
        print("DEBUG: ML model not loaded in semantic_score_calculation. Providing basic score and generic feedback.")
        basic_score = (weighted_keyword_overlap_score * 0.7)
        basic_score += min(years_exp * 5, 30)
        
        if cgpa is not None:
            if cgpa >= 3.5:
                basic_score += 5
            elif cgpa < 2.5:
                basic_score -= 5
        
        score = round(min(basic_score, 100), 2)
        
        return score, round(semantic_similarity, 2)

    try:
        years_exp_for_model = float(years_exp) if years_exp is not None else 0.0
        features = np.concatenate([jd_embedding, resume_embedding, [years_exp_for_model], [weighted_keyword_overlap_score]])
        predicted_score = _ml_model.predict([features])[0]

        blended_score = (predicted_score * 0.6) + \
                        (weighted_keyword_overlap_score * 0.1) + \
                        (semantic_similarity * 100 * 0.3)

        if semantic_similarity > 0.7 and years_exp >= 3:
            blended_score += 5
        
        if cgpa is not None:
            if cgpa >= 3.5:
                blended_score += 3
            elif cgpa >= 3.0:
                blended_score += 1
            elif cgpa < 2.5:
                blended_score -= 2

        score = float(np.clip(blended_score, 0, 100))
        
        return round(score, 2), round(semantic_similarity, 2)

    except Exception as e:
        print(f"ERROR: Error during semantic score calculation: {e}")
        traceback.print_exc()
        basic_score = (weighted_keyword_overlap_score * 0.7)
        basic_score += min(years_exp * 5, 30)
        
        if cgpa is not None:
            basic_score += 5 if cgpa >= 3.5 else (-5 if cgpa < 2.5 else 0)

        score = round(min(basic_score, 100), 2)

        return score, 0.0

def create_mailto_link(recipient_email, candidate_name, job_title="Job Opportunity", sender_name="Recruiting Team"):
    subject = urllib.parse.quote(f"Invitation for Interview - {job_title} - {candidate_name}")
    body = urllib.parse.quote(f"""Dear {candidate_name},

We were very impressed with your profile and would like to invite you for an interview for the {job_title} position.

Best regards,

The {sender_name}""")
    return f"mailto:{recipient_email}?subject={subject}&body={body}"

def send_certificate_email(recipient_email, candidate_name, score, certificate_html_content, gmail_address, gmail_app_password):
    """
    Sends an email with the certificate embedded as HTML content.
    """
    if not gmail_address or not gmail_app_password:
        st.error("❌ Email sending is not configured. Please ensure your Gmail address and App Password secrets are set in Streamlit.")
        return False

    msg = MIMEMultipart('alternative') # Use 'alternative' for plain text and HTML versions
    msg['Subject'] = f"🎉 Congratulations, {candidate_name}! Your ScreenerPro Certificate is Here!"
    msg['From'] = gmail_address
    msg['To'] = recipient_email

    plain_text_body = f"""Hi {candidate_name},

Congratulations on successfully clearing the ScreenerPro resume screening process with a score of {score:.1f}%!

We’re proud to award you an official certificate recognizing your skills and employability.

You can save this HTML file, add it to your resume, LinkedIn, or share it with employers to stand out.

To view your certificate online, visit: {APP_BASE_URL}

Have questions? Contact us at support@screenerpro.in

🚀 Keep striving. Keep growing.

– Team ScreenerPro
"""

    # Embed the certificate HTML directly into the email's HTML part
    html_body = f"""
    <html>
        <body>
            <p>Hi {candidate_name},</p>
            <p>Congratulations on successfully clearing the ScreenerPro resume screening process with a score of <strong>{score:.1f}%</strong>!</p>
            <p>We’re proud to award you an official certificate recognizing your skills and employability.</p>
            <p>You can save this certificate (attached below or viewable online) to your resume, LinkedIn, or share it with employers to stand out.</p>
            
            <p>To view your certificate online, please visit: <a href="{APP_BASE_URL}">{APP_BASE_URL}</a></p>
            
            <p>Here is your certificate:</p>
            <hr/>
            {certificate_html_content}
            <hr/>
            
            <p>Have questions? Contact us at support@screenerpro.in</p>
            <p>🚀 Keep striving. Keep growing.</p>
            <p>– Team ScreenerPro</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(plain_text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            smtp.send_message(msg)
        st.success(f"✅ Certificate email sent to {recipient_email}!")
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Failed to send email: Authentication error. Please check your Gmail address and App Password.")
        st.info("Ensure you have generated an App Password for your Gmail account and used it instead of your regular password.")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
    return False

def _process_single_resume_for_screener_page(file_name, text, jd_text, jd_embedding, 
                                             resume_embedding, jd_name_for_results,
                                             high_priority_skills, medium_priority_skills, max_experience,
                                             _global_ml_model):
    """
    Processes a single resume (pre-extracted text and pre-computed embeddings)
    for the main screener page and returns a dictionary of results.
    """
    try:
        if text.startswith("[ERROR]"):
            return {
                "File Name": file_name,
                "Candidate Name": file_name.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('_', ' ').title(),
                "Score (%)": 0, "Years Experience": 0, "CGPA (4.0 Scale)": None,
                "Email": "Not Found", "Phone Number": "Not Found", "Location": "Not Found",
                "Languages": "Not Found", "Education Details": "Not Found",
                "Work History": "Not Found", "Project Details": "Not Found",
                "AI Suggestion": f"Error: {text.replace('[ERROR] ', '')}",
                "Detailed HR Assessment": f"Error processing resume: {text.replace('[ERROR] ', '')}",
                "Matched Keywords": "", "Missing Skills": "",
                "Matched Keywords (Categorized)": "{}", # Store as empty JSON string
                "Missing Skills (Categorized)": "{}", # Store as empty JSON string
                "Semantic Similarity": 0.0, "Resume Raw Text": "",
                "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
                "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
                "Tag": "❌ Text Extraction Error"
            }

        exp = extract_years_of_experience(text)
        email = extract_email(text)
        phone = extract_phone_number(text)
        location = extract_location(text)
        languages = extract_languages(text) 
        
        education_details_text = extract_education_text(text)
        work_history_raw = extract_work_history(text)
        project_details_raw = extract_project_details(text, MASTER_SKILLS)
        
        education_details_formatted = education_details_text
        work_history_formatted = format_work_history(work_history_raw)
        project_details_formatted = format_project_details(project_details_raw)

        candidate_name = extract_name(text) or file_name.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('_', ' ').title()
        cgpa = extract_cgpa(text)

        resume_raw_skills_set, resume_categorized_skills = extract_relevant_keywords(text, MASTER_SKILLS)
        jd_raw_skills_set, jd_categorized_skills = extract_relevant_keywords(jd_text, MASTER_SKILLS)

        matched_keywords = list(resume_raw_skills_set.intersection(jd_raw_skills_set))
        
        # Corrected: Missing skills should be JD skills NOT found in resume
        missing_skills = list(jd_raw_skills_set.difference(resume_raw_skills_set))


        # Calculate weighted keyword overlap score
        weighted_keyword_overlap_score = 0
        total_jd_skill_weight = 0
        WEIGHT_HIGH = 3
        WEIGHT_MEDIUM = 2
        WEIGHT_BASE = 1

        for jd_skill in jd_raw_skills_set:
            current_weight = WEIGHT_BASE
            if jd_skill in [s.lower() for s in high_priority_skills]:
                current_weight = WEIGHT_HIGH
            elif jd_skill in [s.lower() for s in medium_priority_skills]:
                current_weight = WEIGHT_MEDIUM
            
            total_jd_skill_weight += current_weight
            
            if jd_skill in resume_raw_skills_set:
                weighted_keyword_overlap_score += current_weight

        # Call the semantic score calculation with pre-computed embeddings
        score, semantic_similarity = semantic_score_calculation(
            jd_embedding, resume_embedding, exp, cgpa, weighted_keyword_overlap_score, _global_ml_model
        )
        
        concise_ai_suggestion = generate_concise_ai_suggestion(
            candidate_name=candidate_name,
            score=score,
            years_exp=exp,
            semantic_similarity=semantic_similarity,
            cgpa=cgpa
        )

        detailed_hr_assessment = generate_detailed_hr_assessment(
            candidate_name=candidate_name,
            score=score,
            years_exp=exp,
            semantic_similarity=semantic_similarity,
            cgpa=cgpa,
            jd_text=jd_text,
            resume_text=text,
            matched_keywords=matched_keywords,
            missing_skills=missing_skills,
            max_exp_cutoff=max_experience
        )

        certificate_id = str(uuid.uuid4())
        certificate_rank = "Not Applicable"

        if score >= 90:
            certificate_rank = "🏅 Elite Match"
        elif score >= 80:
            certificate_rank = "⭐ Strong Match"
        elif score >= 75:
            certificate_rank = "✅ Good Fit"
        
        # Determine Tag
        tag = "❌ Limited Match"
        if score >= 90 and exp >= 5 and exp <= max_experience and semantic_similarity >= 0.85 and (cgpa is None or cgpa >= 3.5):
            tag = "👑 Exceptional Match"
        elif score >= 80 and exp >= 3 and exp <= max_experience and semantic_similarity >= 0.7 and (cgpa is None or cgpa >= 3.0):
            tag = "🔥 Strong Candidate"
        elif score >= 60 and exp >= 1 and exp <= max_experience and (cgpa is None or cgpa >= 2.5):
            tag = "✨ Promising Fit"
        elif score >= 40:
            tag = "⚠️ Needs Review"

        return {
            "File Name": file_name,
            "Candidate Name": candidate_name,
            "Score (%)": score,
            "Years Experience": exp,
            "CGPA (4.0 Scale)": cgpa,
            "Email": email or "Not Found",
            "Phone Number": phone or "Not Found",
            "Location": location or "Not Found",
            "Languages": languages,
            "Education Details": education_details_formatted,
            "Work History": work_history_formatted,
            "Project Details": project_details_formatted,
            "AI Suggestion": concise_ai_suggestion,
            "Detailed HR Assessment": detailed_hr_assessment,
            "Matched Keywords": ", ".join(matched_keywords),
            "Missing Skills": ", ".join(missing_skills),
            "Matched Keywords (Categorized)": json.dumps(dict(resume_categorized_skills)), # Convert to JSON string
            "Missing Skills (Categorized)": json.dumps(dict(jd_categorized_skills)),     # Convert to JSON string
            "Semantic Similarity": semantic_similarity,
            "Resume Raw Text": text,
            "JD Used": jd_name_for_results,
            "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()),
            "Certificate Rank": certificate_rank,
            "Tag": tag
        }
    except Exception as e:
        print(f"CRITICAL ERROR: Unhandled exception processing {file_name}: {e}")
        traceback.print_exc()
        return {
            "File Name": file_name,
            "Candidate Name": file_name.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('_', ' ').title(),
            "Score (%)": 0, "Years Experience": 0, "CGPA (4.0 Scale)": None,
            "Email": "Not Found", "Phone Number": "Not Found", "Location": "Not Found",
            "Languages": "Not Found", "Education Details": "Not Found",
            "Work History": "Not Found", "Project Details": "Not Found",
            "AI Suggestion": f"Critical Error: {e}",
            "Detailed HR Assessment": f"Critical Error processing resume: {e}",
            "Matched Keywords": "", "Missing Skills": "",
            "Matched Keywords (Categorized)": "{}", # Store as empty JSON string
            "Missing Skills (Categorized)": "{}", # Store as empty JSON string
            "Semantic Similarity": 0.0, "Resume Raw Text": "",
            "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
            "Tag": "❌ Critical Processing Error"
        }

def suggest_courses_for_skills(missing_skills_list):
    """
    Suggests courses or learning platforms for given missing skills.
    This is a simplified example; a real-world solution might use a more extensive
    database or an LLM call.
    """
    course_suggestions = {
        "Python": "Python for Everybody (Coursera), Automate the Boring Stuff with Python (Udemy)",
        "Java": "Java Programming Masterclass (Udemy), Object-Oriented Programming in Java (Coursera)",
        "JavaScript": "The Complete JavaScript Course (Udemy), JavaScript Basics (freeCodeCamp)",
        "React": "React - The Complete Guide (Udemy), React Basics (egghead.io)",
        "SQL": "SQL for Data Science (Coursera), Learn SQL (Codecademy)",
        "AWS": "AWS Certified Cloud Practitioner (Udemy), AWS Fundamentals (Coursera)",
        "Docker": "Docker & Kubernetes: The Practical Guide (Udemy), Docker Essentials (Pluralsight)",
        "Machine Learning": "Machine Learning (Coursera by Andrew Ng), Applied Machine Learning (edX)",
        "Data Analysis": "Google Data Analytics Professional Certificate (Coursera), Data Analyst with Python (DataCamp)",
        "Cybersecurity": "CompTIA Security+ (Udemy), Introduction to Cybersecurity (Coursera)",
        "Project Management": "Project Management Professional (PMP) Certification (various providers), Agile with Atlassian Jira (Coursera)",
        "Communication Skills": "Effective Communication (Coursera), Public Speaking (edX)",
        # Add more mappings as needed
    }

    st.subheader("📚 Suggested Courses for Missing Skills")
    if not missing_skills_list:
        st.info("Great! You have no significant missing skills based on the Job Description.")
        return

    st.write("Based on the skills missing from your resume compared to the Job Description, here are some suggested courses or learning resources:")
    
    found_suggestions = False
    for skill in missing_skills_list: # Corrected variable name from 'missing_skills' to 'missing_skills_list'
        # Normalize skill name for lookup (e.g., "python" -> "Python")
        normalized_skill = skill.title() 
        if normalized_skill in course_suggestions:
            st.markdown(f"- **{normalized_skill}:** {course_suggestions[normalized_skill]}")
            found_suggestions = True
        else:
            st.markdown(f"- **{normalized_skill}:** Consider exploring courses on Coursera, Udemy, or edX to develop this skill.")
            found_suggestions = True # Mark as found suggestion even if generic

    if not found_suggestions:
        st.info("We couldn't find specific course suggestions for all missing skills, but continuous learning is key!")
        st.markdown("Consider exploring platforms like Coursera, Udemy, or edX for relevant courses.")

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
    date_screened = candidate_data.get('Date Screened', datetime.now().date()).strftime("%B %d, %Y")
    certificate_id = candidate_data.get('Certificate ID', 'N/A')
    
    html_content = html_template.replace("{{CANDIDATE_NAME}}", candidate_name)
    html_content = html_content.replace("{{SCORE}}", f"{score:.1f}")
    html_content = html_content.replace("{{CERTIFICATE_RANK}}", certificate_rank)
    html_content = html_content.replace("{{DATE_SCREENED}}", date_screened)
    html_content = html_content.replace("{{CERTIFICATE_ID}}", certificate_id)

    return html_content

def generate_fake_data_page():
    # Personalized greeting for the logged-in user
    if st.session_state.get('authenticated', False) and st.session_state.get('username'):
        st.markdown(f"## Hello, {st.session_state.username}!")

    st.title("🧪 Generate Fake Candidate Data")
    st.markdown("This page allows you to generate realistic fake candidate data and push it to your Firestore database for testing and demonstration purposes.")

    # Fetch Firebase secrets
    try:
        project_id = st.secrets["FIREBASE_PROJECT_ID"]
        api_key = st.secrets["FIREBASE_API_KEY"]
    except KeyError as e:
        st.error(f"❌ Firebase configuration error: Missing secret key '{e}'.")
        st.info("Please ensure 'FIREBASE_PROJECT_ID' and 'FIREBASE_API_KEY' are correctly set in your secrets.toml or Streamlit Cloud secrets.")
        return

    # Firestore collection path where screening results are stored
    collection_id = "leaderboard" # Assuming results are saved to 'leaderboard' collection

    st.markdown("---")

    num_candidates = st.slider("🔢 Number of Fake Candidates to Generate", 1, 100, 10)
    
    # Text area for a sample JD to influence skill generation and AI assessments
    st.markdown("### Provide a Sample Job Description")
    st.info("This JD will influence the 'Matched' and 'Missing' skills, and the AI assessments, making the fake data more contextually relevant.")
    sample_jd_text = st.text_area(
        "Sample Job Description for Fake Data Generation",
        value="""
        We are seeking a highly motivated and skilled Software Engineer with expertise in Python, Java, and cloud platforms like AWS.
        Experience with React, SQL databases (PostgreSQL, MongoDB), and DevOps tools (Docker, Kubernetes, Git) is essential.
        Candidates should have strong problem-solving abilities, excellent communication skills, and a proven track record in developing scalable applications.
        Knowledge of Machine Learning or Data Science concepts is a plus. Minimum 3 years of experience required.
        """,
        height=200
    )

    if st.button("🚀 Generate & Push Fake Data to Firestore"):
        if not sample_jd_text.strip():
            st.error("Please provide a sample Job Description to generate more realistic data.")
            return

        with st.spinner(f"Generating and pushing {num_candidates} fake candidates..."):
            generated_count = 0
            errors = 0
            
            # Pre-compute JD embedding once
            jd_clean = clean_text(sample_jd_text)
            jd_embedding = global_sentence_model.encode([jd_clean])[0]

            # Extract JD skills for realistic matched/missing skills
            jd_raw_skills_set, _ = extract_relevant_keywords(sample_jd_text, MASTER_SKILLS)

            for i in range(num_candidates):
                try:
                    candidate_data = generate_dummy_candidate_data(
                        jd_text=sample_jd_text,
                        jd_embedding=jd_embedding,
                        jd_raw_skills_set=jd_raw_skills_set,
                        max_experience_cutoff=15 # A reasonable max for fake data generation
                    )
                    
                    # Firestore REST API endpoint for creating a document with an auto-generated ID
                    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}"

                    # Prepare data for Firestore REST API
                    data_to_send = candidate_data.copy()
                    
                    # Ensure 'Matched Keywords (Categorized)' and 'Missing Skills (Categorized)' are dicts
                    if isinstance(data_to_send.get('Matched Keywords (Categorized)'), str):
                        try:
                            data_to_send['Matched Keywords (Categorized)'] = json.loads(data_to_send['Matched Keywords (Categorized)'])
                        except json.JSONDecodeError:
                            data_to_send['Matched Keywords (Categorized)'] = {} # Fallback
                    if isinstance(data_to_send.get('Missing Skills (Categorized)'), str):
                        try:
                            data_to_send['Missing Skills (Categorized)'] = json.loads(data_to_send['Missing Skills (Categorized)'])
                        except json.JSONDecodeError:
                            data_to_send['Missing Skills (Categorized)'] = {} # Fallback

                    # Convert datetime.date objects to string for JSON serialization
                    if isinstance(data_to_send.get('Date Screened'), (datetime, date)):
                        data_to_send['Date Screened'] = data_to_send['Date Screened'].strftime("%Y-%m-%d")

                    # Remove raw text if it's too large or not needed in leaderboard
                    data_to_send.pop('Resume Raw Text', None)

                    firestore_payload = _convert_to_firestore_rest_format(data_to_send)

                    headers = {
                        "Content-Type": "application/json"
                    }

                    response = requests.post(url, headers=headers, data=json.dumps(firestore_payload))
                    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                    generated_count += 1
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ Error pushing candidate {i+1} to Firestore: HTTP Error {e.response.status_code} - {e.response.text}")
                    errors += 1
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred for candidate {i+1}: {e}")
                    errors += 1
            
            st.success(f"✅ Successfully generated and pushed {generated_count} candidates to Firestore!")
            if errors > 0:
                st.warning(f"⚠️ {errors} candidates failed to push due to errors. Check logs for details.")
            
            # Optionally, refresh the total screened count in session state
            st.session_state['refresh_count'] = True # Trigger refresh on total screened page

def generate_dummy_candidate_data(jd_text, jd_embedding, jd_raw_skills_set, max_experience_cutoff):
    """
    Generates a single fake candidate profile with realistic data,
    influenced by a provided Job Description.
    """
    first_names = [
        "Abhinav", "Bhargav", "Chirantan", "Deepesh", "Eshanpreet", "Feroz", "Gokul", "Harshvardhan", "Indrajit", "Jatin",
    "Karthik", "Lokesh", "Mihir", "Nikhilesh", "Onir", "Pradyumna", "Qasim", "Ritvik", "Sharvil", "Tarak",
    "Udayveer", "Vikrant", "Waman", "Yagnesh", "Zayan", "Aaryan", "Brahma", "Chiranjeevi", "Divyansh", "Ekagra",
    "Faiyaz", "Gurdeep", "Hemendra", "Irfan", "Jaskaran", "Kush", "Luv", "Mahesh", "Namish", "Omveer",
    "Prithviraj", "Ravikant", "Sankalp", "Tanraj", "Upendra", "Vibhor", "Wasimuddin", "Yogin", "Zubairuddin", "Ajinkya",

    # Indian Female (50)
    "Ankita", "Bhoomi", "Chanchal", "Damini", "Elina", "Farzana", "Gauri", "Haripriya", "Iraja", "Jinal",
    "Kavitha", "Lajja", "Mallika", "Nirmala", "Ojaswini", "Pankhuri", "Qamra", "Rashmi", "Sharvani", "Triveni",
    "Urmila", "Vidya", "Winnie", "Yamika", "Zaina", "Ambika", "Bharati", "Chandrika", "Devika", "Eshaana",
    "Falguni", "Geetika", "Hemlata", "Ishwari", "Jayanti", "Krupali", "Lakshmi", "Mahima", "Neelam", "Oorja",
    "Padma", "Rajshree", "Shambhavi", "Tara", "Urvashi", "Vaishali", "Warishta", "Yukti", "Zeba", "Anvitha"
      ]


    last_names = [
    # Common Indian Last Names (75)
        "Abrol", "Bansod", "Chitale", "Dani", "Ekambaram", "Fattehpuria", "Ganwani", "Hasija", "Ingle", "Jadhav",
    "Karnik", "Londhekar", "Madhwani", "Nagori", "Ojari", "Pansare", "Qazi", "Rajput", "Sawlani", "Tiwade",
    "Ubhaykar", "Valmiki", "Wadhera", "Yellamraju", "Zende", "Ashar", "Baghel", "Chauke", "Dangar", "Eknath",
    "Funkar", "Gharat", "Hatkar", "Iqubal", "Jakhotia", "Khetan", "Lokre", "Malkani", "Nanda", "Ojariwala",
    "Pipara", "Rachh", "Sambrekar", "Tapkir", "Upasani", "Virk", "Warke", "Yelagond", "Zore", "Attal",
    "Bapat", "Chavan", "Dalvi", "Edla", "Fatnani", "Gavaskar", "Hussain", "Idnani", "Jhala", "Kalra",
    "Lele", "Mendiratta", "Nerurkar", "Patankar", "Qutbuddin", "Rajani", "Sampat", "Tandel", "Uchil", "Vaghani",
    "Wadhwani", "Yennam", "Zutshi", "Adani", "Bhoir", "Chougle", "Dubal", "Ekka", "Fouzdar", "Ganatra",
    "Hingorani", "Ismaili", "Jagtap", "Kansara", "Lunkad", "Mahadik", "Nehra", "Odekar", "Pacharne", "Ravoori",
    "Sahani", "Talwar", "Ujwal", "Varghese", "Wable", "Yarlagadda", "Zulfi", "Agrawal", "Bhutani", "Chokhani"
        ]

    email_domains = ["example.com", "mail.com", "techcorp.org", "devs.net"]

    # Education details with realistic institutions and degrees
    education_details_options = [
        "B.Tech in Computer Science, Indian Institute of Technology, Delhi - 2024",
        "M.Sc. in Data Science, University of California, Berkeley - 2023",
        "B.E. in Software Engineering, Anna University, Chennai - 2025",
        "Ph.D. in Artificial Intelligence, Stanford University - 2022",
        "Bachelor of Technology in Information Technology, Vellore Institute of Technology - 2023",
        "Master of Computer Applications, National Institute of Technology, Warangal - 2024",
        "B.Sc. in Computer Science, University of Mumbai - 2022",
        "M.Tech. in Machine Learning, Carnegie Mellon University - 2023",
        "Bachelor of Engineering in Electronics, Birla Institute of Technology & Science, Pilani - 2024",
        "MBA in Business Analytics, Indian Institute of Management, Bangalore - 2025"
    ]

    # Work history options with realistic companies and titles
    work_history_options = [
        {"Company": "Tech Solutions Inc.", "Title": "Software Developer", "Start Date": "Jan 2022", "End Date": "Present"},
        {"Company": "Global Innovations Ltd.", "Title": "Data Scientist", "Start Date": "Aug 2021", "End Date": "Dec 2023"},
        {"Company": "Digital Dynamics", "Title": "DevOps Engineer", "Start Date": "Mar 2023", "End Date": "Present"},
        {"Company": "FinTech Corp.", "Title": "AI/ML Engineer", "Start Date": "Oct 2020", "End Date": "Nov 2022"},
        {"Company": "NextGen Systems", "Title": "Senior Software Engineer", "Start Date": "Jul 2019", "End Date": "Feb 2023"},
        {"Company": "Innovate Labs", "Title": "Cloud Architect", "Start Date": "Apr 2020", "End Date": "Present"},
        {"Company": "CyberSecure Solutions", "Title": "Cybersecurity Analyst", "Start Date": "Sep 2022", "End Date": "Present"},
        {"Company": "Data Insights Co.", "Title": "Business Intelligence Analyst", "Start Date": "Jan 2021", "End Date": "Jul 2023"},
        {"Company": "Quantum Leap Tech", "Title": "Associate Developer", "Start Date": "Feb 2024", "End Date": "Present"},
        {"Company": "Enterprise Software", "Title": "Project Manager", "Start Date": "Nov 2018", "End Date": "Dec 2021"}
    ]

    # Project details with realistic titles and descriptions
    project_details_options = [
        {"Project Title": "E-commerce Recommendation System", "Description": "Developed a personalized product recommendation engine using collaborative filtering and machine learning. Achieved a 15% increase in user engagement.", "Technologies Used": "Python, TensorFlow, Scikit-learn, MongoDB"},
        {"Project Title": "Real-time Chat Application", "Description": "Built a scalable real-time chat application with WebSocket integration and robust backend services. Supported millions of concurrent users.", "Technologies Used": "Node.js, Express.js, WebSockets, PostgreSQL"},
        {"Project Title": "Automated Deployment Pipeline", "Description": "Designed and implemented a CI/CD pipeline for microservices using Docker and Kubernetes, reducing deployment time by 50%.", "Technologies Used": "Docker, Kubernetes, Jenkins, Git, AWS"},
        {"Project Title": "Fraud Detection System", "Description": "Created an AI-powered fraud detection system that identified suspicious transactions with 98% accuracy, preventing significant financial losses.", "Technologies Used": "Python, PyTorch, Pandas, SQL"},
        {"Project Title": "Customer Relationship Management (CRM) Tool", "Description": "Developed a custom CRM solution to manage client interactions, sales pipelines, and support tickets, improving customer satisfaction by 20%.", "Technologies Used": "React, Django, MySQL, AWS S3"},
        {"Project Title": "Predictive Maintenance Platform", "Description": "Engineered a predictive maintenance platform for industrial machinery, reducing downtime by analyzing sensor data with machine learning models.", "Technologies Used": "Python, Azure ML, IoT Hub, Power BI"},
        {"Project Title": "Secure Authentication Module", "Description": "Implemented a multi-factor authentication (MFA) module for a web application, enhancing security and compliance with industry standards.", "Technologies Used": "Java, Spring Boot, OAuth2, JWT"},
        {"Project Title": "Natural Language Processing (NLP) Chatbot", "Description": "Built an NLP-driven chatbot for customer support, capable of understanding user queries and providing automated responses, reducing support load by 30%.", "Technologies Used": "Python, NLTK, SpaCy, Flask"},
        {"Project Title": "Inventory Management System", "Description": "Developed a web-based inventory management system for a retail chain, optimizing stock levels and reducing waste.", "Technologies Used": "Vue.js, Node.js, MongoDB, Google Cloud Functions"},
        {"Project Title": "Financial Data Visualization Dashboard", "Description": "Created an interactive dashboard to visualize complex financial data, enabling stakeholders to make informed decisions faster.", "Technologies Used": "Python, Tableau, SQL, Pandas"}
    ]

    name = random.choice(first_names) + " " + random.choice(last_names)
    email = f"{name.replace(' ', '.').lower()}@{random.choice(email_domains)}"
    phone = f"+91-{random.randint(7000000000, 9999999999)}"
    location = random.choice(list(MASTER_CITIES))
    languages = ", ".join(random.sample(["English", "Hindi", "Spanish", "French", "German"], random.randint(1, 3)))
    
    education_details = random.choice(education_details_options)
    work_history_raw = [random.choice(work_history_options) for _ in range(random.randint(1, 3))]
    project_details_raw = [random.choice(project_details_options) for _ in range(random.randint(1, 3))]

    years_exp = round(random.uniform(1, min(max_experience_cutoff, 15)), 1) # Ensure experience is within limits
    cgpa = round(random.uniform(2.8, 4.0), 2) # Higher CGPA for realistic good candidates

    # Generate skills based on the JD and a "score"
    # Higher score means more matched skills, fewer missing
    simulated_score = random.uniform(75, 100) # Target average 80%
    
    matched_skills_count = int(len(jd_raw_skills_set) * (simulated_score / 100.0) * random.uniform(0.7, 1.0))
    missing_skills_count = int(len(jd_raw_skills_set) * ((100 - simulated_score) / 100.0) * random.uniform(0.5, 0.8))

    matched_skills = random.sample(list(jd_raw_skills_set), min(matched_skills_count, len(jd_raw_skills_set)))
    
    # Ensure missing skills are actually missing from the matched set
    potential_missing = list(jd_raw_skills_set.difference(set(matched_skills)))
    missing_skills = random.sample(potential_missing, min(missing_skills_count, len(potential_missing)))

    # Categorize skills
    matched_categorized = collections.defaultdict(list)
    for skill in matched_skills:
        found = False
        for category, skills_in_category in SKILL_CATEGORIES.items():
            if skill.lower() in {s.lower() for s in skills_in_category}:
                matched_categorized[category].append(skill)
                found = True
                break
        if not found:
            matched_categorized["Other"].append(skill)
    
    missing_categorized = collections.defaultdict(list)
    for skill in missing_skills:
        found = False
        for category, skills_in_category in SKILL_CATEGORIES.items():
            if skill.lower() in {s.lower() for s in skills_in_category}:
                missing_categorized[category].append(skill)
                found = True
                break
        if not found:
            missing_categorized["Other"].append(skill)

    # Simulate resume raw text for AI assessment functions
    simulated_resume_text = f"Candidate Name: {name}\n"
    simulated_resume_text += f"Email: {email}\nPhone: {phone}\nLocation: {location}\n"
    simulated_resume_text += f"Education: {education_details}\n"
    simulated_resume_text += "Work Experience:\n"
    for job in work_history_raw:
        simulated_resume_text += f"- {job.get('Title', 'Engineer')} at {job.get('Company', 'Company')} ({job.get('Start Date', 'Date')} - {job.get('End Date', 'Present')})\n"
    simulated_resume_text += "Projects:\n"
    for proj in project_details_raw:
        simulated_resume_text += f"- {proj.get('Project Title', 'Project')}: {proj.get('Description', 'Description')}\n"
        simulated_resume_text += f"  Technologies: {proj.get('Technologies Used', 'None')}\n"
    simulated_resume_text += f"Skills: {', '.join(matched_skills + missing_skills)}\n" # Combine for raw text
    simulated_resume_text += f"Languages: {languages}\n"
    simulated_resume_text += f"CGPA: {cgpa}/4.0\n"
    simulated_resume_text += f"Years of Experience: {years_exp}\n"

    # Generate resume embedding for semantic similarity
    resume_embedding = global_sentence_model.encode([clean_text(simulated_resume_text)])[0]
    
    # Calculate semantic similarity (dummy for now, or use pre-trained model if available)
    semantic_similarity = cosine_similarity(jd_embedding.reshape(1, -1), resume_embedding.reshape(1, -1))[0][0]
    semantic_similarity = float(np.clip(semantic_similarity, 0.4, 0.95)) # Keep it in a reasonable range

    # Calculate weighted keyword overlap score (simplified for dummy data)
    weighted_keyword_overlap_score = (len(matched_skills) / len(jd_raw_skills_set)) if jd_raw_skills_set else 0
    weighted_keyword_overlap_score = float(np.clip(weighted_keyword_overlap_score, 0.0, 1.0))

    # Call AI assessment functions with the generated data
    concise_ai_suggestion = generate_concise_ai_suggestion(
        candidate_name=name,
        score=simulated_score,
        years_exp=years_exp,
        semantic_similarity=semantic_similarity,
        cgpa=cgpa
    )

    detailed_hr_assessment = generate_detailed_hr_assessment(
        candidate_name=name,
        score=simulated_score,
        years_exp=years_exp,
        semantic_similarity=semantic_similarity,
        cgpa=cgpa,
        jd_text=jd_text, # Pass the sample JD
        resume_text=simulated_resume_text,
        matched_keywords=matched_skills,
        missing_skills=missing_skills,
        max_exp_cutoff=max_experience_cutoff
    )

    certificate_rank = "Not Applicable"
    if simulated_score >= 90:
        certificate_rank = "🏅 Elite Match"
    elif simulated_score >= 80:
        certificate_rank = "⭐ Strong Match"
    elif simulated_score >= 75:
        certificate_rank = "✅ Good Fit"

    tag = "❌ Limited Match"
    if simulated_score >= 90 and years_exp >= 5 and years_exp <= max_experience_cutoff and semantic_similarity >= 0.85 and (cgpa is None or cgpa >= 3.5):
        tag = "👑 Exceptional Match"
    elif simulated_score >= 80 and years_exp >= 3 and years_exp <= max_experience_cutoff and semantic_similarity >= 0.7 and (cgpa is None or cgpa >= 3.0):
        tag = "🔥 Strong Candidate"
    elif simulated_score >= 60 and years_exp >= 1 and years_exp <= max_experience_cutoff and (cgpa is None or cgpa >= 2.5):
        tag = "✨ Promising Fit"
    elif simulated_score >= 40:
        tag = "⚠️ Needs Review"

    return {
        "File Name": f"{name.replace(' ', '_').lower()}.pdf",
        "Candidate Name": name,
        "Score (%)": simulated_score,
        "Years Experience": years_exp,
        "CGPA (4.0 Scale)": cgpa,
        "Email": email,
        "Phone Number": phone,
        "Location": location,
        "Languages": languages,
        "Education Details": education_details,
        "Work History": format_work_history(work_history_raw),
        "Project Details": format_project_details(project_details_raw),
        "AI Suggestion": concise_ai_suggestion,
        "Detailed HR Assessment": detailed_hr_assessment,
        "Matched Keywords": ", ".join(matched_skills),
        "Missing Skills": ", ".join(missing_skills),
        "Matched Keywords (Categorized)": json.dumps(dict(matched_categorized)),
        "Missing Skills (Categorized)": json.dumps(dict(missing_categorized)),
        "Semantic Similarity": semantic_similarity,
        "Resume Raw Text": simulated_resume_text, # Keep raw text for potential future use
        "JD Used": "Simulated JD",
        "Date Screened": datetime.now().date(),
        "Certificate ID": str(uuid.uuid4()),
        "Certificate Rank": certificate_rank,
        "Tag": tag
    }

# Functions below are copied from resume_screen.py to ensure generate_fake_data_page is self-contained
# and can call these for realistic AI assessment generation.
# --- Start of copied functions from resume_screen.py ---

NLTK_STOP_WORDS = set(nltk.corpus.stopwords.words('english'))
CUSTOM_STOP_WORDS = set([
    "work", "experience", "years", "year", "months", "month", "day", "days", "project", "projects",
    "team", "teams", "developed", "managed", "led", "created", "implemented", "designed",
    "responsible", "proficient", "knowledge", "ability", "strong", "proven", "demonstrated",
    "solution", "solutions", "system", "systems", "platform", "platforms", "framework", "frameworks",
    "database", "databases", "server", "servers", "cloud", "computing", "machine", "learning",
    "artificial", "intelligence", "api", "apis", "rest", "graphql", "agile", "scrum", "kanban",
    "devops", "ci", "cd", "testing", "qa",
    "security", "network", "networking", "virtualization",
    "containerization", "docker", "kubernetes", "terraform", "ansible", "jenkins", "circleci", "github actions", "azure devops", "mlops",
    "containerization", "docker", "kubernetes", "git", "github", "gitlab", "bitbucket", "jira",
    "confluence", "slack", "microsoft", "google", "amazon", "azure", "oracle", "sap", "crm", "erp",
    "salesforce", "servicenow", "tableau", "powerbi", "qlikview", "excel", "word", "powerpoint",
    "outlook", "visio", "html", "css", "js", "web", "data", "science", "analytics", "engineer",
    "software", "developer", "analyst", "business", "management", "reporting", "analysis", "tools",
    "python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "swift", "kotlin", "r",
    "sql", "nosql", "linux", "unix", "windows", "macos", "ios", "android", "mobile", "desktop",
    "application", "applications", "frontend", "backend", "fullstack", "ui", "ux", "design",
    "architecture", "architect", "engineering", "scientist", "specialist", "consultant",
    "associate", "senior", "junior", "lead", "principal", "director", "manager", "head", "chief",
    "officer", "president", "vice", "executive", "ceo", "cto", "cfo", "coo", "hr", "human",
    "resources", "recruitment", "talent", "acquisition", "onboarding", "training", "development",
    "performance", "compensation", "benefits", "payroll", "compliance", "legal", "finance",
    "accounting", "auditing", "tax", "budgeting", "forecasting", "investments", "marketing",
    "sales", "customer", "service", "support", "operations", "supply", "chain", "logistics",
    "procurement", "manufacturing", "production", "quality", "assurance", "control", "research",
    "innovation", "product", "program", "portfolio", "governance", "risk", "communication",
    "presentation", "negotiation", "problem", "solving", "critical", "thinking", "analytical",
    "creativity", "adaptability", "flexibility", "teamwork", "collaboration", "interpersonal",
    "organizational", "time", "multitasking", "detail", "oriented", "independent", "proactive",
    "self", "starter", "results", "driven", "client", "facing", "stakeholder", "engagement",
    "vendor", "budget", "cost", "reduction", "process", "improvement", "standardization",
    "optimization", "automation", "digital", "transformation", "change", "methodologies",
    "industry", "regulations", "regulatory", "documentation", "technical", "writing",
    "dashboards", "visualizations", "workshops", "feedback", "reviews", "appraisals",
    "offboarding", "employee", "relations", "diversity", "inclusion", "equity", "belonging",
    "corporate", "social", "responsibility", "csr", "sustainability", "environmental", "esg",
    "ethics", "integrity", "professionalism", "confidentiality", "discretion", "accuracy",
    "precision", "efficiency", "effectiveness", "scalability", "robustness", "reliability",
    "vulnerability", "assessment", "penetration", "incident", "response", "disaster",
    "recovery", "continuity", "bcp", "drp", "gdpr", "hipaa", "soc2", "iso", "nist", "pci",
    "dss", "ccpa", "privacy", "protection", "grc", "cybersecurity", "information", "infosec",
    "threat", "intelligence", "soc", "event", "siem", "identity", "access", "iam", "privileged",
    "pam", "multi", "factor", "authentication", "mfa", "single", "sign", "on", "sso",
    "encryption", "decryption", "firewall", "ids", "ips", "vpn", "endpoint", "antivirus",
    "malware", "detection", "forensics", "handling", "assessments", "policies", "procedures",
    "guidelines", "mitre", "att&ck", "modeling", "secure", "lifecycle", "sdlc", "awareness",
    "phishing", "vishing", "smishing", "ransomware", "spyware", "adware", "rootkits",
    "botnets", "trojans", "viruses", "worms", "zero", "day", "exploits", "patches", "patching",
    "updates", "upgrades", "configuration", "ticketing", "crm", "erp", "scm", "hcm", "financial",
    "accounting", "bi", "warehousing", "etl", "extract", "transform", "load", "lineage",
    "master", "mdm", "lakes", "marts", "big", "hadoop", "spark", "kafka", "flink", "mongodb",
    "cassandra", "redis", "elasticsearch", "relational", "mysql", "postgresql", "db2",
    "teradata", "snowflake", "redshift", "synapse", "bigquery", "aurora", "dynamodb",
    "documentdb", "cosmosdb", "graph", "neo4j", "graphdb", "timeseries", "influxdb",
    "timescaledb", "columnar", "vertica", "clickhouse", "vector", "pinecone", "weaviate",
    "milvus", "qdrant", "chroma", "faiss", "annoy", "hnswlib", "scikit", "learn", "tensorflow",
    "pytorch", "keras", "xgboost", "lightgbm", "catboost", "statsmodels", "numpy", "pandas",
    "matplotlib", "seaborn", "plotly", "bokeh", "dash", "flask", "django", "fastapi", "spring",
    "boot", ".net", "core", "node.js", "express.js", "react", "angular", "vue.js", "svelte",
    "jquery", "bootstrap", "tailwind", "sass", "less", "webpack", "babel", "npm", "yarn",
    "ansible", "terraform", "jenkins", "gitlab", "github", "actions", "codebuild", "codepipeline",
    "codedeploy", "build", "deploy", "run", "lambda", "functions", "serverless", "microservices",
    "gateway", "mesh", "istio", "linkerd", "grpc", "restful", "soap", "message", "queues",
    "rabbitmq", "activemq", "bus", "sqs", "sns", "pubsub", "version", "control", "svn",
    "mercurial", "trello", "asana", "monday.com", "smartsheet", "project", "primavera",
    "zendesk", "freshdesk", "itil", "cobit", "prince2", "pmp", "master", "owner", "lean",
    "six", "sigma", "black", "belt", "green", "yellow", "qms", "9001", "27001", "14001",
    "ohsas", "18001", "sa", "8000", "cmii", "cmi", "cism", "cissp", "ceh", "comptia",
    "security+", "network+", "a+", "linux+", "ccna", "ccnp", "ccie", "certified", "solutions",
    "architect", "developer", "sysops", "administrator", "specialty", "professional", "azure",
    "az-900", "az-104", "az-204", "az-303", "az-304", "az-400", "az-500", "az-700", "az-800",
    "az-801", "dp-900", "dp-100", "dp-203", "ai-900", "ai-102", "da-100", "pl-900", "pl-100",
    "pl-200", "pl-300", "pl-400", "pl-500", "ms-900", "ms-100", "ms-101", "ms-203", "ms-500",
    "ms-700", "ms-720", "ms-740", "ms-600", "sc-900", "sc-200", "sc-300", "sc-400", "md-100",
    "md-101", "mb-200", "mb-210", "mb-220", "mb-230", "mb-240", "mb-260", "mb-300", "mb-310",
    "mb-320", "mb-330", "mb-340", "mb-400", "mb-500", "mb-600", "mb-700", "mb-800", "mb-910",
    "mb-920", "gcp-ace", "gcp-pca", "gcp-pde", "gcp-pse", "gcp-pml", "gcp-psa", "gcp-pcd",
    "gcp-pcn", "gcp-psd", "gcp-pda", "gcp-pci", "gcp-pws", "gcp-pwa", "gcp-pme", "gcp-pmc",
    "gcp-pmd", "gcp-pma", "gcp-pmc", "gcp-pmg", "cisco", "juniper", "red", "hat", "rhcsa",
    "rhce", "vmware", "vcpa", "vcpd", "vcpi", "vcpe", "vcpx", "citrix", "cc-v", "cc-p",
    "cc-e", "cc-m", "cc-s", "cc-x", "palo", "alto", "pcnsa", "pcnse", "fortinet", "fcsa",
    "fcsp", "fcc", "fcnsp", "fct", "fcp", "fcs", "fce", "fcn", "fcnp", "fcnse"
])
STOP_WORDS = NLTK_STOP_WORDS.union(CUSTOM_STOP_WORDS)

SKILL_CATEGORIES = {
    "Programming Languages": ["Python", "Java", "JavaScript", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "TypeScript", "R", "Bash Scripting", "Shell Scripting"],
    "Web Technologies": ["HTML5", "CSS3", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", "Express.js", "WebSockets"],
    "Databases": ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Elasticsearch", "Neo4j", "Redis", "BigQuery", "Snowflake", "Redshift", "Aurora", "DynamoDB", "DocumentDB", "CosmosDB"],
    "Cloud Platforms": ["AWS", "Azure", "Google Cloud Platform", "GCP", "Serverless", "AWS Lambda", "Azure Functions", "Google Cloud Functions"],
    "DevOps & MLOps": ["Git", "GitHub", "GitLab", "Bitbucket", "CI/CD", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "CircleCI", "GitHub Actions", "Azure DevOps", "MLOps"],
    "Data Science & ML": ["Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "Data Cleaning", "Feature Engineering",
    "Model Evaluation", "Statistical Modeling", "Time Series Analysis", "Predictive Modeling", "Clustering",
    "Classification", "Regression", "Neural Networks", "Convolutional Networks", "Recurrent Networks",
    "Transformers", "LLMs", "Prompt Engineering", "Generative AI", "MLOps", "Data Munging", "A/B Testing",
    "Experiment Design", "Hypothesis Testing", "Bayesian Statistics", "Causal Inference", "Graph Neural Networks"],
    "Data Analytics & BI": ["Data Cleaning", "Feature Engineering", "Model Evaluation", "Statistical Analysis", "Time Series Analysis", "Data Munging", "A/B Testing", "Experiment Design", "Hypothesis Testing", "Bayesian Statistics", "Causal Inference", "Excel (Advanced)", "Tableau", "Power BI", "Looker", "Qlik Sense", "Google Data Studio", "Dax", "M Query", "ETL", "ELT", "Data Warehousing", "Data Lake", "Data Modeling", "Business Intelligence", "Data Visualization", "Dashboarding", "Report Generation", "Google Analytics"],
    "Soft Skills": ["Stakeholder Management", "Risk Management", "Change Management", "Communication Skills", "Public Speaking", "Presentation Skills", "Cross-functional Collaboration",
    "Problem Solving", "Critical Thinking", "Analytical Skills", "Adaptability", "Time Management",
    "Organizational Skills", "Attention to Detail", "Leadership", "Mentorship", "Team Leadership",
    "Decision Making", "Negotiation", "Client Management", "Stakeholder Communication", "Active Listening",
    "Creativity", "Innovation", "Research", "Data Analysis", "Report Writing", "Documentation"],
    "Project Management": ["Agile Methodologies", "Scrum", "Kanban", "Jira", "Trello", "Product Lifecycle", "Sprint Planning", "Project Charter", "Gantt Charts", "MVP", "Backlog Grooming",
    "Program Management", "Portfolio Management", "PMP", "CSM"],
    "Security": ["Cybersecurity", "Information Security", "Risk Assessment", "Compliance", "GDPR", "HIPAA", "ISO 27001", "Penetration Testing", "Vulnerability Management", "Incident Response", "Security Audits", "Forensics", "Threat Intelligence", "SIEM", "Firewall Management", "Endpoint Security", "IAM", "Cryptography", "Network Security", "Application Security", "Cloud Security"],
    "Other Tools & Frameworks": ["Jira", "Confluence", "Swagger", "OpenAPI", "Zendesk", "ServiceNow", "Intercom", "Live Chat", "Ticketing Systems", "HubSpot", "Salesforce Marketing Cloud",
    "QuickBooks", "SAP FICO", "Oracle Financials", "Workday", "Microsoft Dynamics", "NetSuite", "Adobe Creative Suite", "Canva", "Mailchimp", "Hootsuite", "Buffer", "SEMrush", "Ahrefs", "Moz", "Screaming Frog",
    "JMeter", "Postman", "SoapUI", "SVN", "Perforce", "Asana", "Monday.com", "Miro", "Lucidchart", "Visio", "MS Project", "Primavera", "AutoCAD", "SolidWorks", "MATLAB", "LabVIEW", "Simulink", "ANSYS",
    "CATIA", "NX", "Revit", "ArcGIS", "QGIS", "OpenCV", "NLTK", "SpaCy", "Gensim", "Hugging Face Transformers",
    "Docker Compose", "Helm", "Ansible Tower", "SaltStack", "Chef InSpec", "Terraform Cloud", "Vault",
    "Consul", "Nomad", "Prometheus", "Grafana", "Alertmanager", "Loki", "Tempo", "Jaeger", "Zipkin",
    "Fluentd", "Logstash", "Kibana", "Grafana Loki", "Datadog", "New Relic", "AppDynamics", "Dynatrace",
    "Nagios", "Zabbix", "Icinga", "PRTG", "SolarWinds", "Wireshark", "Nmap", "Metasploit", "Burp Suite",
    "OWASP ZAP", "Nessus", "Qualys", "Rapid7", "Tenable", "CrowdStrike", "SentinelOne", "Palo Alto Networks",
    "Fortinet", "Cisco Umbrella", "Okta", "Auth0", "Keycloak", "Ping Identity", "Active Directory",
    "LDAP", "OAuth", "JWT", "OpenID Connect", "SAML", "MFA", "SSO", "PKI", "TLS/SSL", "VPN", "IDS/IPS",
    "DLP", "CASB", "SOAR", "XDR", "EDR", "MDR", "GRC", "ITIL", "Lean Six Sigma", "CFA", "CPA", "SHRM-CP",
    "PHR", "CEH", "OSCP", "CCNA", "CISSP", "CISM", "CompTIA Security+"]
}

MASTER_SKILLS = set([skill for category_list in SKILL_CATEGORIES.values() for skill in category_list])
STOP_WORDS = NLTK_STOP_WORDS.union(CUSTOM_STOP_WORDS)

# --- End of copied functions from resume_screen.py ---

# This allows the page to be run directly for testing, but typically it's imported by app.py
if __name__ == "__main__":
    st.set_page_config(page_title="Generate Fake Data", layout="wide")
    generate_fake_data_page()
