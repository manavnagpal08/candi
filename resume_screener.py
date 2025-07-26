import streamlit as st
import pdfplumber
import re
import os
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sentence_transformers import SentenceTransformer, util
import nltk
import collections
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import traceback
import json
import requests

from company_profiles import COMPANY_SKILL_PROFILES
from weasyprint import HTML

os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

MASTER_CITIES = set([
    "Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Chandigarh", "Kochi", "Coimbatore", "Nagpur", "Bhopal", "Indore", "Gurgaon", "Noida", "Surat", "Visakhapatnam",
    "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi",
    "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi", "Jabalpur", "Gwalior", "Vijayawada",
    "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Bareilly", "Moradabad", "Mysore", "Tiruchirappalli",
    "Thiruvananthapuram", "Bhubaneswar", "Salem", "Tiruppur", "Jalandhar", "Bhiwandi", "Saharanpur", "Gorakhpur",
    "Guntur", "Bikaner", "Amravati", "Noida", "Jamshedpur", "Bhilai", "Cuttack", "Firozabad", "Kochi", "Nellore",
    "Bhavnagar", "Dehradun", "Durgapur", "Asansol", "Nanded", "Kolhapur", "Ajmer", "Gulbarga", "Jamnagar", "Ujjain",
    "Loni", "Siliguri", "Jhansi", "Ulhasnagar", "Jammu", "Sangli-Miraj & Kupwad", "Mangaluru", "Belagavi",
    "Ambattur", "Tirunelveli", "Malegaon", "Gaya", "Jalgaon", "Udaipur", "Maheshtala", "Davanagere", "Kozhikode",
    "Kurnool", "Akola", "Rajahmundry", "Bokaro Steel City", "South Dumdum", "Bellary", "Patiala", "Gopalpur",
    "Bhagalpur", "Muzaffarnagar", "Bhatpara", "Panihati", "Latur", "Dhule", "Rohtak", "Korba", "Bhilwara",
    "Berhampur", "Ahmednagar", "Kakinada", "Ichalkaranji", "Thane", "Puducherry", "Tumakuru", "Aligarh", "Rampur",
    "Shivamogga", "Chandrapur", "Junagadh", "Thrissur", "Alwar", "Bardhaman", "Katihar", "Hisar", "Ozhukarai",
    "Bihar Sharif", "Panipat", "Darbhanga", "Bally", "Satna", "Munger", "Kirari Suleman Nagar", "Secunderabad",
    "Karawal Nagar", "Nadiad", "Yamunanagar", "Panchkula", "Karnal", "Erode", "Anantapur", "Arrah", "Thanjavur",
    "Murwara", "Orai", "Bahraich", "Vellore", "Proddatur", "Chittoor", "Ballia", "Warangal", "Guntur", "Kakinada",
    "Nizamabad", "Khammam", "Karimnagar", "Ramagundam", "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet",
    "Miryalaguda", "Jagtial", "Wanaparthy", "Palwancha", "Siddipet", "Nagarkurnool", "Kothagudem", "Amalapuram",
    "Ongole", "Eluru", "Machilipatnam", "Tenali", "Chirala", "Tadepalligudem", "Gudivada", "Srikakulam",
    "Vizianagaram", "Anakapalle", "Kavali", "Tirupati", "Kadapa", "Kuppam", "Nellore", "Hindupur", "Dharmavaram",
    "Guntakal", "Adoni", "Madanapalle", "Rayachoti", "Chittoor", "Pileru", "Srikalahasti", "Punganur", "Renigunta",
    "Kovur", "Gudur", "Venkatagiri", "Sullurpeta", "Naidupeta", "Podili", "Kandukur", "Darsi", "Markapur",
    "Giddalur", "Bellampalli", "Mancherial", "Mandamarri", "Chennur", "Kyathampalle", "Ramagundam", "Peddapalli",
    "Godavarikhani", "Sultanabad", "Jammikunta", "Huzurabad", "Bhongir", "Jangaon", "Yadagirigutta", "Kagaznagar",
    "Sirpur Kagaznagar", "Manuguru", "Yellandu", "Kothagudem", "Palwancha", "Tekulapally", "Sathupally",
    "Madhira", "Wyra", "Karempudi", "Vemulawada", "Sircilla", "Koratla", "Metpally", "Armoor", "Bodhan",
    "Kamareddy", "Nirmal", "Bhainsa", "Adilabad", "Bellampalli", "Mancherial", "Mandamarri", "Chennur",
    "Kyathampalle", "Kagaznagar", "Sirpur Kagaznagar", "Manuguru", "Yellandu", "Kothagudem", "Palwancha",
    "Tekulapally", "Sathupally", "Madhira", "Wyra", "Karempudi", "Vemulawada", "Sircilla", "Koratla",
    "Metpally", "Armoor", "Bodhan", "Kamareddy", "Nirmal", "Bhainsa"
])

FIRESTORE_PROJECT_ID = "your-gcp-project-id"
FIRESTORE_COLLECTION_PATH = "screenerpro_results"

def _to_firestore_value(value):
    if isinstance(value, str):
        return {"stringValue": value}
    elif isinstance(value, (int, float)):
        if isinstance(value, int):
            return {"integerValue": str(value)}
        else:
            return {"doubleValue": value}
    elif isinstance(value, bool):
        return {"booleanValue": value}
    elif isinstance(value, list):
        return {"arrayValue": {"values": [_to_firestore_value(item) for item in value]}}
    elif isinstance(value, dict):
        fields = {k: _to_firestore_value(v) for k, v in value.items()}
        return {"mapValue": {"fields": fields}}
    elif value is None:
        return {"nullValue": None}
    else:
        st.warning(f"Unsupported data type for Firestore: {type(value)}. Converting to string.")
        return {"stringValue": str(value)}

def save_screening_result_to_firestore_rest(candidate_data):
    if FIRESTORE_PROJECT_ID == "your-gcp-project-id":
        st.error("Please replace 'your-gcp-project-id' with your actual Google Cloud Project ID in the code to enable Firestore saving.")
        return

    url = f"https://firestore.googleapis.com/v1/projects/{FIRESTORE_PROJECT_ID}/databases/(default)/documents/{FIRESTORE_COLLECTION_PATH}"
    headers = {
        "Content-Type": "application/json"
    }

    firestore_fields = {}
    for key, value in candidate_data.items():
        firestore_fields[key] = _to_firestore_value(value)

    payload = {
        "fields": firestore_fields
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        st.success("Screening result saved to Firestore!")
        st.json(response.json())
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err} - {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Connection error occurred: {conn_err}. Check your internet connection or Firestore project ID/rules.")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Timeout error occurred: {timeout_err}. The request took too long.")
    except requests.exceptions.RequestException as req_err:
        st.error(f"An unexpected error occurred: {req_err}")
    except Exception as e:
        st.error(f"An error occurred while saving to Firestore: {e}")
        st.error(traceback.format_exc())

@st.cache_resource
def load_models():
    with st.spinner("Loading AI models... This may take a moment."):
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            ml_model = None
            return model, ml_model
        except Exception as e:
            st.error(f"❌ Error loading AI models: {e}. Please ensure 'all-MiniLM-L6-v2' model can be loaded.")
            return None, None

global_sentence_model, global_ml_model = load_models()

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.\w+')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
CGPA_PATTERN = re.compile(r'(?:cgpa|gpa|grade point average)\s*[:\s]*(\d+\.\d+)(?:\s*[\/of]{1,4}\s*(\d+\.\d+|\d+))?|(\d+\.\d+)(?:\s*[\/of]{1,4}\s*(\d+\.\d+|\d+))?\s*(?:cgpa|gpa)')
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
SKILL_LIST = MASTER_SKILLS

CERTIFICATE_HOSTING_URL = "https://candidate-screeneerpro.streamlit.app/"

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
        filter_set_lower = {s.lower() for s in filter_set}
        sorted_filter_skills = sorted([s for s in filter_set if ' ' in s], key=len, reverse=True)
        
        temp_text = cleaned_text

        for skill_phrase in sorted_filter_skills:
            pattern = r'\b' + re.escape(skill_phrase.lower()) + r'\b'
            
            if re.search(pattern, temp_text):
                extracted_keywords.add(skill_phrase.lower())
                found_category = False
                for category, skills_in_category in SKILL_CATEGORIES.items():
                    if skill_phrase.lower() in {s.lower() for s in skills_in_category}:
                        categorized_keywords[category].append(skill_phrase)
                        found_category = True
                        break
                if not found_category:
                    categorized_keywords["Uncategorized"].append(skill_phrase)
                temp_text = re.sub(pattern, " ", temp_text)
        
        individual_words_remaining = set(re.findall(r'\b\w+\b', temp_text))
        for word in individual_words_remaining:
            if word in filter_set_lower:
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
            return f"[ERROR] Failed to extract text from PDF: {str(e)}. Ensure it's a text-selectable PDF, not a scanned image."

    elif "image" in file_type:
        return f"[ERROR] Image files are not supported for text extraction in this version. Please upload a PDF."
    else:
        return f"[ERROR] Unsupported file type: {file_type}. Please upload a PDF."

    if not full_text.strip():
        return "[ERROR] No readable text extracted from the file. It might be an empty document."
    
    return full_text

def extract_years_of_experience(resume_text):
    def remove_education_section(text):
        lines = text.lower().splitlines()
        filtered = []
        inside_education = False
        for line in lines:
            if any(keyword in line for keyword in [
                "education", "b.tech", "btech", "class x", "class xii", "school",
                "higher secondary", "cgpa", "percentage"
            ]):
                inside_education = True
            elif inside_education and line.strip() == "":
                inside_education = False
            if not inside_education:
                filtered.append(line)
        return "\n".join(filtered)

    def normalize_date_str(date_str):
        return re.sub(r'[,\.\s]+', ' ', date_str.strip().lower()).title()

    text = remove_education_section(resume_text)
    text = re.sub(r'[\:\,\–—]+', ' - ', text)

    total_months = 0
    now = datetime.now()

    date_patterns = [
        r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4})\s*[-to]+\s*(present|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4})',
        r'(\b\d{4})\s*[-to]+\s*(present|\b\d{4})'
    ]

    for pattern in date_patterns:
        job_date_ranges = re.findall(pattern, text)
        for start_str, end_str in job_date_ranges:
            start_str = normalize_date_str(start_str)
            end_str = normalize_date_str(end_str)

            try:
                start_date = datetime.strptime(start_str, '%B %Y')
            except:
                try:
                    start_date = datetime.strptime(start_str, '%b %Y')
                except:
                    try:
                        start_date = datetime(int(start_str.strip()), 1, 1)
                    except:
                        continue

            if not start_date or start_date > now:
                continue

            if 'present' in end_str.lower():
                end_date = now
            else:
                try:
                    end_date = datetime.strptime(end_str, '%B %Y')
                except:
                    try:
                        end_date = datetime.strptime(end_str, '%b %Y')
                    except:
                        try:
                            end_date = datetime(int(end_str.strip()), 12, 31)
                        except:
                            continue

                if end_date > now:
                    end_date = now

            if not end_date:
                continue

            delta_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += max(delta_months, 0)

    if total_months > 0:
        return round(total_months / 12, 1)

    match = re.search(r'(\d+(?:\.\d+)?)\s*(\+)?\s*(year|yrs|years)\b', text)
    if not match:
        match = re.search(r'experience[^\d]{0,10}(\d+(?:\.\d+)?)', text)
    if match:
        return float(match.group(1))

    return 0.0

def extract_email(text):
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None

def extract_phone_number(text):
    match = PHONE_PATTERN.search(text)
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
    lines = text.strip().splitlines()
    if not lines:
        return None

    EXCLUDE_TERMS = {
        "email", "e-mail", "phone", "mobile", "contact", "linkedin", "github",
        "portfolio", "website", "profile", "summary", "objective", "education",
        "skills", "projects", "certifications", "achievements", "experience",
        "dob", "date of birth", "address", "resume", "cv", "career", "gender",
        "marital", "nationality", "languages", "language"
    }

    PREFIX_CLEANER = re.compile(r"^(name[\s:\-]*|mr\.?|ms\.?|mrs\.?)", re.IGNORECASE)

    potential_names = []

    for line in lines[:10]:
        original_line = line.strip()
        if not original_line:
            continue

        cleaned_line = PREFIX_CLEANER.sub('', original_line).strip()
        cleaned_line = re.sub(r'[^A-Za-z\s]', '', cleaned_line)

        if any(term in cleaned_line.lower() for term in EXCLUDE_TERMS):
            continue

        words = cleaned_line.split()

        if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
            if all(w.istitle() or w.isupper() for w in words):
                potential_names.append(cleaned_line)

    if potential_names:
        return max(potential_names, key=len).title()

    return None

def extract_cgpa(text):
    text = text.lower()
    
    matches = CGPA_PATTERN.findall(text)

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

EDU_MATCH_PATTERN = re.compile(
    r"(b\.?tech|bachelor|be|b\.e\.|m\.?tech|master|mca|mba)[^\n]{0,100}?(university|college|institute)[^\n]{0,100}?(20\d{2})(?!\d)",
    re.IGNORECASE
)

EDU_FALLBACK_PATTERN = re.compile(
    r"(b\.?tech|bachelor|be|b\.e\.|m\.?tech|master|mca|mba)[^\n]{0,100}?(20\d{2})(?!\d)",
    re.IGNORECASE
)

def extract_education_text(text):
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

    edu_match = EDU_MATCH_PATTERN.search(education_section)
    if edu_match:
        return ' '.join(edu_match.groups()).strip()

    fallback_match = EDU_FALLBACK_PATTERN.search(education_section)
    if fallback_match:
        return ' '.join(fallback_match.groups()).strip()

    fallback_line = education_section.split('.')[0].strip()
    return fallback_line if fallback_line else None

def extract_work_history(text):
    work_history_section_matches = WORK_HISTORY_SECTION_PATTERN.finditer(text)
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
        
        job_blocks = JOB_BLOCK_SPLIT_PATTERN.split(work_text)
        
        for block in job_blocks:
            block = block.strip()
            if not block:
                continue
            
            company = None
            title = None
            start_date = None
            end_date = None

            date_range_match = DATE_RANGE_MATCH_PATTERN.search(block)
            if date_range_match:
                start_date = date_range_match.group(1)
                end_date = date_range_match.group(2)
                block = block.replace(date_range_match.group(0), '').strip()

            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue

                title_company_match = TITLE_COMPANY_MATCH_PATTERN.search(line)
                if title_company_match:
                    title = title_company_match.group(1).strip()
                    company = title_company_match.group(2).strip()
                    break
                
                company_title_match = COMPANY_TITLE_MATCH_PATTERN.search(line)
                if company_title_match:
                    company = company_title_match.group(1).strip()
                    title = company_title_match.group(2).strip()
                    break
                
                if not company and not title:
                    potential_org_match = POTENTIAL_ORG_MATCH_PATTERN.search(line)
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
    project_details = []

    text = text.replace('\r', '').replace('\t', ' ')
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    project_section_match = PROJECT_SECTION_KEYWORDS.search(text)

    if not project_section_match:
        project_text = text[:1000]
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

        if re.match(r'^[A-Z\s]{5,}$', line) and len(line.split()) <= 4:
            continue

        prev_line_is_bullet = False
        if i > 0 and re.match(r'^[•*-]', lines[i - 1]):
            prev_line_is_bullet = True

        is_title = (
            (PROJECT_TITLE_START_PATTERN.match(line) or line.lower().startswith("project")) and
            3 <= len(line.split()) <= 15 and
            not any(kw in line_lower for kw in FORBIDDEN_TITLE_KEYWORDS) and
            not prev_line_is_bullet and
            not line.isupper()
        )

        is_url = re.match(r'https?://', line_lower)

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
    languages_list = set()
    cleaned_full_text = clean_text(text)

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

    section_match = LANGUAGE_SECTION_PATTERN.search(cleaned_full_text)

    if section_match:
        start_index = section_match.end()
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

    for lang in sorted_all_languages:
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

def get_learning_links(skill):
    return {
        "Coursera": f"https://www.coursera.org/search?query={urllib.parse.quote(skill)}",
        "Udemy": f"https://www.udemy.com/courses/search/?q={urllib.parse.quote(skill)}",
        "YouTube": f"https://www.youtube.com/results?search_query={urllib.parse.quote(skill)}+course",
        "Google": f"https://www.google.com/search?q={urllib.parse.quote(skill)}+tutorial"
    }

def create_mailto_link(recipient_email, candidate_name, job_title="Job Opportunity", sender_name="Recruiting Team"):
    subject = urllib.parse.quote(f"Invitation for Interview - {job_title} - {candidate_name}")
    body = urllib.parse.quote(f"""Dear {candidate_name},

We were very impressed with your profile and would like to invite you for an interview for the {job_title} position.

Best regards,

The {sender_name}""")
    return f"mailto:{recipient_email}?subject={subject}&body={body}"

def send_certificate_email(recipient_email, candidate_name, score, certificate_html_content, certificate_public_url, gmail_address, gmail_app_password):
    if not gmail_address or not gmail_app_password:
        st.error("❌ Email sending is not configured. Please ensure your Gmail address and App Password secrets are set in Streamlit.")
        return False

    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"🎉 Congratulations, {candidate_name}! Your ScreenerPro Certificate is Here!"
    msg['From'] = gmail_address
    msg['To'] = recipient_email

    plain_text_body = f"""Hi {candidate_name},

Congratulations on successfully clearing the ScreenerPro resume screening process with a score of {score:.1f}%!

We’re proud to award you an official certificate recognizing your skills and employability.

You can view your certificate online here: {certificate_public_url}
A PDF version of your certificate is also attached to this email.

Have questions? Contact us at screenerpro.ai@gmail.com

🚀 Keep striving. Keep growing.

– Team ScreenerPro
"""

    html_body = f"""
    <html>
        <body>
            <p>Hi {candidate_name},</p>
            <p>Congratulations on successfully clearing the ScreenerPro resume screening process with a score of <strong>{score:.1f}%</strong>!</p>
            <p>We’re proud to award you an official certificate recognizing your skills and employability.</p>
            
            <p>You can view your certificate online here: <a href="{certificate_public_url}">{certificate_public_url}</a></p>
            <p>A PDF version of your certificate is also attached to this email.</p>
            
            <p>Have questions? Contact us at screenerpro.ai@gmail.com</p>
            <p>🚀 Keep striving. Keep growing.</p>
            <p>– Team ScreenerPro</p>
        </body>
    </html>
    """
    
    alternative_part = MIMEMultipart('alternative')
    alternative_part.attach(MIMEText(plain_text_body, 'plain'))
    alternative_part.attach(MIMEText(html_body, 'html'))
    msg.attach(alternative_part)

    try:
        pdf_bytes = HTML(string=certificate_html_content).write_pdf()
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="ScreenerPro_Certificate_{candidate_name.replace(" ", "_")}.pdf"')
        msg.attach(part)
    except Exception as e:
        st.error(f"❌ Failed to generate or attach PDF to email: {e}")
        st.warning("The email will be sent without the PDF attachment.")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎉 Congratulations, {candidate_name}! Your ScreenerPro Certificate is Here!"
        msg['From'] = gmail_address
        msg['To'] = recipient_email
        msg.attach(MIMEText(plain_text_body.replace("A PDF version of your certificate is also attached to this email.", ""), 'plain'))
        msg.attach(MIMEText(html_body.replace("A PDF version of your certificate is also attached to this email.", ""), 'html'))

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

def generate_company_fit_assessment(candidate_name, company_name, resume_embedding, company_profile_embedding, resume_skills_set, company_keywords):
    assessment_parts = []
    assessment_parts.append(f"### Company Fit Assessment for {candidate_name} with {company_name}\n")

    semantic_fit = cosine_similarity(resume_embedding.reshape(1, -1), company_profile_embedding.reshape(1, -1))[0][0]
    semantic_fit = float(np.clip(semantic_fit, 0, 1))

    if semantic_fit >= 0.75:
        assessment_parts.append(f"Your profile shows a **very strong semantic alignment ({semantic_fit:.2f})** with {company_name}'s core values, technologies, and industry focus. This indicates a high potential for cultural and technical fit.")
    elif semantic_fit >= 0.5:
        assessment_parts.append(f"There is a **good semantic alignment ({semantic_fit:.2f})** between your profile and {company_name}. You share common themes and areas of interest, suggesting a solid potential fit.")
    else:
        assessment_parts.append(f"The semantic alignment ({semantic_fit:.2f}) with {company_name} is moderate. While you may have relevant skills, consider highlighting experiences that directly relate to {company_name}'s specific industry, products, or mission.")

    company_keywords_set = set(company_keywords)
    matched_company_skills = resume_skills_set.intersection(company_keywords_set)
    missing_company_skills = company_keywords_set.difference(resume_skills_set)

    if matched_company_skills:
        assessment_parts.append(f"\n**Key Skills for {company_name}:** You possess several skills highly valued by {company_name}, including: {', '.join(sorted(list(matched_company_skills)))}. This direct skill match is a significant advantage.")
    else:
        assessment_parts.append(f"\n**Key Skills for {company_name}:** We did not find direct matches for some of {company_name}'s highly preferred skills in your resume. This could be an area for improvement.")

    if missing_company_skills:
        assessment_parts.append(f"\n**Areas to Enhance for {company_name}:** To further boost your fit for {company_name}, consider developing or highlighting experience in: {', '.join(sorted(list(missing_company_skills)))}. These are areas {company_name} frequently looks for.")
        assessment_parts.append(f"Researching {company_name}'s recent projects, tech blogs, and job postings can provide more specific insights.")
    else:
        assessment_parts.append(f"\n**Excellent Skill Alignment with {company_name}:** Your resume covers many of the key skills that {company_name} typically seeks. Continue to deepen your expertise in these areas.")

    return "\n".join(assessment_parts)

def _process_single_resume_for_screener_page(file_name, text, jd_text, jd_embedding, 
                                             resume_embedding, jd_name_for_results,
                                             _global_ml_model, target_company_name=None):
    try:
        if text.startswith("[ERROR]"):
            return {
                "File Name": file_name,
                "Candidate Name": file_name.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('_', ' ').title(),
                "Skill Match": 0, "Semantic Match": 0.0, "Years Experience": 0, "CGPA (4.0 Scale)": None,
                "Email": "Not Found", "Phone Number": "Not Found", "Location": "Not Found",
                "Languages": "Not Found", "Education Details": "Not Found",
                "Work History": "Not Found", "Project Details": "Not Found",
                "AI Suggestion": f"Error: {text.replace('[ERROR] ', '')}",
                "Detailed HR Assessment": f"Error processing resume: {text.replace('[ERROR] ', '')}", 
                "Company Fit Assessment": f"Error: Resume text extraction failed.", 
                "Matched Skills": [], "Missing Skills": [],
                "Matched Keywords (Categorized)": "{}", 
                "Missing Skills (Categorized)": "{}", 
                "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
                "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
                "Tag": "❌ Text Extraction Error",
                "LLM Feedback": f"Error: {text.replace('[ERROR] ', '')}"
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

        match_score, matched_skills_list, missing_skills_list = calculate_match_score(text, jd_text, global_sentence_model)
        semantic_score_from_feedback = cosine_similarity(resume_embedding.reshape(1, -1), jd_embedding.reshape(1, -1))[0][0]
        semantic_score_from_feedback = float(np.clip(semantic_score_from_feedback, 0, 1))

        company_boost_percentage = 0
        company_fit_assessment_text = "No target company specified or found."
        if target_company_name and target_company_name != "None":
            normalized_company_name = None
            for company_key, profile_data in COMPANY_SKILL_PROFILES.items():
                if company_key.lower() == target_company_name.lower():
                    normalized_company_name = company_key
                    break

            if normalized_company_name:
                company_profile = COMPANY_SKILL_PROFILES[normalized_company_name]
                company_skills = set(s.lower() for s in company_profile["keywords"])
                
                resume_skills_for_company_boost, _ = extract_relevant_keywords(text, MASTER_SKILLS)
                candidate_matched_company_skills = resume_skills_for_company_boost.intersection(company_skills)
                
                if company_skills:
                    company_skill_match_ratio = len(candidate_matched_company_skills) / len(company_skills)
                    company_boost_percentage = company_skill_match_ratio * 5

                company_keywords_for_embedding = " ".join(company_profile["keywords"])
                company_description_for_embedding = company_profile["description"]
                company_text_for_embedding = f"{company_description_for_embedding} {company_keywords_for_embedding}"
                company_embedding = global_sentence_model.encode([clean_text(company_text_for_embedding)])[0]

                company_fit_assessment_text = generate_company_fit_assessment(
                    candidate_name=candidate_name,
                    company_name=normalized_company_name,
                    resume_embedding=resume_embedding,
                    company_profile_embedding=company_embedding,
                    resume_skills_set=set(matched_skills_list),
                    company_keywords=company_profile["keywords"]
                )
            else:
                company_fit_assessment_text = f"Company '{target_company_name}' not found in our predefined profiles. Please try one of the examples (e.g., Google, Microsoft, Amazon, Generic Tech Startup, IBM, Oracle, SAP, Cisco, Adobe, NVIDIA)."

        overall_score = (match_score * 0.95) + (company_boost_percentage)
        overall_score = np.clip(overall_score, 0, 100)

        candidate_ai_feedback = generate_candidate_feedback(
            candidate_name=candidate_name,
            score=overall_score,
            years_exp=exp,
            semantic_similarity=semantic_score_from_feedback,
            cgpa=cgpa,
            matched_skills=matched_skills_list,
            missing_skills=missing_skills_list,
            target_company_name=target_company_name
        )

        score = overall_score
        semantic_similarity = semantic_score_from_feedback 
        matched_keywords = matched_skills_list 
        missing_skills = missing_skills_list 
        
        llm_feedback_text = candidate_ai_feedback

        certificate_id = str(uuid.uuid4())
        certificate_rank = "Not Applicable"

        if score >= 90:
            certificate_rank = "🏅 Elite Match"
        elif score >= 80:
            certificate_rank = "⭐ Strong Match"
        elif score >= 75:
            certificate_rank = "✅ Good Fit"
        elif score >= 65: 
            certificate_rank = "⚪ Low Fit"
        elif score >= 50:
            certificate_rank = "🟡 Basic Fit"
        
        tag = "❌ Limited Match"
        if score >= 90 and semantic_similarity >= 0.85:
            tag = "👑 Exceptional Match"
        elif score >= 80 and semantic_similarity >= 0.7:
            tag = "🔥 Strong Candidate"
        elif score >= 60:
            tag = "✨ Promising Fit"
        else:
            tag = "⚪ General Match"

        return {
            "File Name": file_name,
            "Candidate Name": candidate_name,
            "Skill Match": score, 
            "Semantic Match": semantic_similarity, 
            "Years Experience": exp,
            "CGPA (4.0 Scale)": cgpa,
            "Email": email or "Not Found",
            "Phone Number": phone or "Not Found",
            "Location": location or "Not Found",
            "Languages": languages,
            "Education Details": education_details_formatted,
            "Work History": work_history_formatted,
            "Project Details": project_details_formatted,
            "AI Suggestion": llm_feedback_text,
            "Detailed HR Assessment": llm_feedback_text,
            "Company Fit Assessment": company_fit_assessment_text,
            "Matched Skills": matched_keywords, 
            "Missing Skills": missing_skills, 
            "Matched Keywords (Categorized)": json.dumps(dict(extract_relevant_keywords(text, MASTER_SKILLS)[1])), 
            "Missing Skills (Categorized)": json.dumps(dict(extract_relevant_keywords(jd_text, MASTER_SKILLS)[1])), 
            "Resume Raw Text": text,
            "JD Used": jd_name_for_results,
            "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()),
            "Certificate Rank": certificate_rank,
            "Tag": tag,
            "LLM Feedback": llm_feedback_text
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "File Name": file_name,
            "Candidate Name": file_name.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('_', ' ').title(),
            "Skill Match": 0, "Semantic Match": 0.0, "Years Experience": 0, "CGPA (4.0 Scale)": None,
            "Email": "Not Found", "Phone Number": "Not Found", "Location": "Not Found",
            "Languages": "Not Found", "Education Details": "Not Found",
            "Work History": "Not Found", "Project Details": "Not Found",
            "AI Suggestion": f"Critical Error: {e}",
            "Detailed HR Assessment": f"Critical Error processing resume: {e}",
            "Company Fit Assessment": f"Critical Error: {e}",
            "Matched Skills": [], "Missing Skills": [],
            "Matched Keywords (Categorized)": "{}", 
            "Missing Skills (Categorized)": "{}", 
            "Resume Raw Text": "",
            "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
            "Tag": "❌ Critical Processing Error",
            "LLM Feedback": f"Critical Error: {e}" 
        }

def extract_skills(text):
    extracted_keywords, _ = extract_relevant_keywords(text, MASTER_SKILLS)
    return extracted_keywords

def calculate_match_score(resume_text, jd_text, sentence_model):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills.difference(resume_skills)

    keyword_match_percentage = 0
    if len(jd_skills) > 0:
        keyword_match_percentage = (len(matched_skills) / len(jd_skills)) * 100

    resume_embedding = sentence_model.encode(clean_text(resume_text), convert_to_tensor=True)
    jd_embedding = sentence_model.encode(clean_text(jd_text), convert_to_tensor=True)
    
    semantic_similarity = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()
    semantic_similarity = float(np.clip(semantic_similarity, 0, 1))

    overall_score = (keyword_match_percentage * 0.6) + (semantic_similarity * 40)
    overall_score = np.clip(overall_score, 0, 100)

    return overall_score, list(matched_skills), list(missing_skills)

def generate_candidate_feedback(candidate_name, score, years_exp, semantic_similarity, cgpa, matched_skills, missing_skills, target_company_name=None):
    feedback_parts = []
    
    feedback_parts.append(f"### Personalized Feedback for {candidate_name}\n")
    feedback_parts.append(f"Thank you for submitting your resume! Here's a detailed assessment of your profile for this role, based on our automated screening.\n")

    if score >= 85:
        feedback_parts.append("**Overall Fit: Excellent!** Your profile demonstrates a very strong alignment with the requirements of this position. You possess a robust skill set and relevant experience that closely matches what we're looking for.")
    elif score >= 70:
        feedback_parts.append("**Overall Fit: Good.** Your resume shows a solid match for this role. You have many of the key skills and experiences needed, indicating strong potential for success.")
    elif score >= 50:
        feedback_parts.append("**Overall Fit: Moderate.** Your profile indicates some alignment with the role, but there are areas where further development or clearer demonstration of skills could significantly strengthen your candidacy.")
    else:
        feedback_parts.append("**Overall Fit: Limited.** While we appreciate your application, your current profile shows limited direct alignment with the specific requirements of this position.")

    feedback_parts.append("\n#### Your Strengths:")
    if matched_skills:
        feedback_parts.append(f"- **Key Skills:** We identified strong matches in skills such as: {', '.join(sorted(matched_skills))}. These are highly relevant to the role and demonstrate your capabilities.")
    else:
        feedback_parts.append("- **Skills:** While specific keyword matches were limited, your resume shows a foundational understanding of relevant concepts.")
    
    if years_exp > 0:
        feedback_parts.append(f"- **Experience:** With {years_exp:.1f} years of experience, you bring practical knowledge that is valuable for this role.")
        if years_exp >= 5:
            feedback_parts.append(" Your extensive experience suggests you are well-prepared for complex challenges and leadership opportunities.")
        elif years_exp >= 2:
            feedback_parts.append(" Your experience provides a solid foundation for contributing effectively to our team.")
    else:
        feedback_parts.append("- **Experience:** While direct professional experience might be limited, your academic projects and other activities demonstrate a proactive approach to learning and applying skills.")

    if cgpa is not None:
        if cgpa >= 3.5:
            feedback_parts.append(f"- **Academic Excellence:** Your CGPA of {cgpa:.2f} (normalized to 4.0 scale) highlights a strong academic background and a commitment to learning.")
        elif cgpa >= 3.0:
            feedback_parts.append(f"- **Solid Academics:** Your CGPA of {cgpa:.2f} (normalized to 4.0 scale) indicates a good academic foundation.")
    
    feedback_parts.append(f"- **Semantic Alignment:** Your resume's content has a semantic similarity of {semantic_similarity:.2f} with the job description, meaning the overall themes and concepts in your profile resonate well with the role's requirements.")

    if target_company_name and target_company_name != "None":
        normalized_company_name = None
        for company_key, profile_data in COMPANY_SKILL_PROFILES.items():
            if company_key.lower() == target_company_name.lower():
                normalized_company_name = company_key
                break

        if normalized_company_name:
            company_skills = set(s.lower() for s in COMPANY_SKILL_PROFILES[normalized_company_name]["keywords"])
            candidate_matched_company_skills = set(s.lower() for s in matched_skills).intersection(company_skills)
            if candidate_matched_company_skills:
                feedback_parts.append(f"- **Company Fit ({normalized_company_name}):** You demonstrate a good fit with {normalized_company_name}'s preferred technologies/skills, including: {', '.join(sorted(list(candidate_matched_company_skills)))}. This is a strong positive for roles within this company.")
            else:
                feedback_parts.append(f"- **Company Fit ({normalized_company_name}):** While your general skills are good, consider exploring more skills specific to {normalized_company_name} to enhance your profile for future applications with them.")

    feedback_parts.append("\n#### Areas for Growth:")
    if missing_skills:
        feedback_parts.append(f"To further strengthen your profile for future opportunities, consider developing skills in these areas that were highlighted in the job description but less prominent in your resume: {', '.join(sorted(missing_skills))}.")
        feedback_parts.append("Focusing on these could significantly enhance your alignment with similar roles.")
    else:
        feedback_parts.append("Your profile is quite comprehensive! Continue to deepen your expertise in your core areas and explore emerging technologies relevant to your field.")

    feedback_parts.append("\n#### Next Steps & Advice:")
    if score >= 70:
        feedback_parts.append("We encourage you to continue refining your skills and showcasing your projects. For roles like this, demonstrating practical application of your skills through detailed project descriptions and quantifiable achievements is key.")
        if missing_skills:
            feedback_parts.append("Explore online courses, certifications, or personal projects related to your missing skills to bridge those gaps.")
    elif score >= 50:
        feedback_parts.append("Consider gaining more hands-on experience through internships, volunteer work, or personal projects. Actively seek opportunities to apply and deepen the skills you already possess, and strategically acquire new ones.")
        if missing_skills:
            feedback_parts.append("We highly recommend pursuing learning resources for: " + ", ".join(sorted(missing_skills)) + ". This will make your profile even more competitive.")
    else:
        feedback_parts.append("We recommend focusing on building a stronger foundation in the core skills required for your target roles. Consider entry-level positions or intensive training programs to gain practical experience.")
        if missing_skills:
            feedback_parts.append("Prioritize learning and gaining practical experience in: " + ", ".join(sorted(missing_skills)) + ".")

    feedback_parts.append("\nWe wish you the best in your career journey!")
    
    return "\n".join(feedback_parts)

def generate_certificate_html(results):
    candidate_name = results.get('Candidate Name', 'Candidate')
    score = results.get('Skill Match', 0)
    date_screened = results.get('Date Screened', datetime.now().date()).strftime("%B %d, %Y")
    certificate_id = results.get('Certificate ID', 'N/A')
    rank = results.get('Certificate Rank', 'Not Applicable')

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>ScreenerPro Certificate (Landscape)</title>
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
            width: 1120px;
            height: 790px;
            padding: 50px 70px;
            border: 10px solid #00bcd4;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            box-sizing: border-box;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .certificate img.logo {
            width: 200px;
            margin-bottom: 20px;
        }

        h1 {
            font-family: 'Playfair Display', serif;
            font-size: 36px;
            color: #003049;
            margin: 10px 0;
        }

        h2 {
            font-size: 20px;
            margin-bottom: 25px;
            color: #007c91;
        }

        .subtext {
            font-size: 18px;
            color: #333;
            margin-bottom: 10px;
        }

        .candidate-name {
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            color: #00bcd4;
            font-weight: bold;
            margin: 10px 0;
            text-decoration: underline;
        }

        .score-rank {
            display: inline-block;
            font-size: 18px;
            font-weight: 600;
            background: #e0f7fa;
            color: #2e7d32;
            padding: 8px 24px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .description {
            font-size: 16px;
            color: #555;
            margin: 20px auto;
            line-height: 1.5;
            max-width: 900px;
        }

        .footer-details {
            font-size: 13px;
            color: #666;
            margin-top: 20px;
        }

        .signature-block {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .signature img {
            width: 150px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }

        .signature .title {
            font-size: 13px;
            color: #777;
            margin-top: 5px;
            text-align: left;
        }

        .stamp {
            font-size: 42px;
            color: #4caf50;
            margin-right: 10px;
        }

        @media print {
            @page {
                size: landscape;
                margin: 0;
            }

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
        <img class="logo" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhhq_OCSv-QmuBjXeRQXr60EfsvVA4chRPCNslo3NhjVQkoKjUtiRfTPpGoQjyQXS7sMsJifQC6Yq34cAhNbq9lMwBXZqIIbCij1adyXSuNoyxuzOTDfrPU2dnna0baimldd7Y1KCkvaAfrWC1yLGxp25SJ9s4exJ-JAc8kNcTyUSgkLWbW2DdvhpWH4GlO/s320/logo.png" alt="ScreenerPro Logo" />

        <h1>CERTIFICATE OF EXCELLENCE</h1>
        <h2>Presented by ScreenerPro</h2>

        <div class="subtext">This is to certify that</div>
        <div class="candidate-name">{candidate_name}</div>

        <div class="subtext">has successfully completed the AI-powered resume screening process</div>

        <div class="score-rank">Score: {score:.2f}% | Rank: {rank}</div>

        <div class="description">
            This certificate acknowledges the candidate’s exceptional qualifications, industry-aligned skills, and readiness to contribute effectively in challenging roles. Evaluated and validated by ScreenerPro’s advanced screening engine.
        </div>

        <div class="footer-details">
            Awarded on: {date_screened}<br>
            Certificate ID: {certificate_id}
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
    return html_template

def load_jds_from_folder(folder_path="data"):
    jds_paths = {}
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith((".txt", ".md")):
                filepath = os.path.join(folder_path, filename)
                display_name = filename.replace(".txt", "").replace(".md", "").replace("_", " ").title()
                jds_paths[display_name] = filepath
    return jds_paths

def resume_screener_page():
    st.set_page_config(page_title="ScreenerPro Resume Screener", layout="wide", initial_sidebar_state="expanded")

    st.markdown("""
        <style>
            .stApp {
                background-color: #f0f2f6;
                color: #333333;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #45a049;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            }
            .stButton>button:active {
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 1.1rem;
                font-weight: 600;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 20px;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-bottom: -3px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #ffffff;
                border-bottom: 3px solid #2196F3;
                color: #2196F3;
            }
            .stExpander {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;
                background-color: #ffffff;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .stExpander > div > div > p {
                font-weight: bold;
                color: #3F51B5;
            }
            .stMarkdown h3 {
                color: #3F51B5;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 5px;
                margin-top: 25px;
            }
            .stMarkdown h2 {
                color: #2196F3;
                margin-top: 30px;
                padding-bottom: 8px;
                border-bottom: 2px solid #2196F3;
            }
            .stAlert > div {
                border-radius: 10px;
            }
            .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
                border-radius: 8px;
                border: 1px solid #ccc;
                padding: 8px;
            }
            .stFileUploader>div>div>button {
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .stFileUploader>div>div>button:hover {
                background-color: #1976D2;
                transform: translateY(-2px);
            }
            .score-metric .stMetric {
                background-color: #e8f5e9;
                border-left: 5px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            }
            .score-metric .stMetric > div > div:first-child {
                font-size: 1.1em;
                color: #4CAF50;
                font-weight: 600;
            }
            .score-metric .stMetric > div > div:last-child {
                font-size: 2.2em;
                font-weight: 700;
                color: #333;
            }
            /* New/Enhanced UI styles */
            .stContainer {
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 25px;
                background-color: #ffffff;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
            .stMarkdown h1 {
                text-align: center;
                color: #003049;
                font-family: 'Playfair Display', serif;
                font-size: 3.5em;
                margin-bottom: 0.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .stMarkdown h3 {
                color: #2196F3;
                font-size: 1.8em;
                text-align: center;
                margin-top: -10px;
                margin-bottom: 30px;
            }
            .stAlert.st-emotion-cache-1f0646s.e1f1d6z03 { /* Targeting specific alert types for better visuals */
                background-color: #e3f2fd; /* Light blue for info */
                border-left: 5px solid #2196F3;
            }
            .stAlert.st-emotion-cache-1f0646s.e1f1d6z04 { /* Light green for success */
                background-color: #e8f5e9;
                border-left: 5px solid #4CAF50;
            }
            .stAlert.st-emotion-cache-1f0646s.e1f1d6z05 { /* Light red for error */
                background-color: #ffebee;
                border-left: 5px solid #f44336;
            }
            .stAlert.st-emotion-cache-1f0646s.e1f1d6z06 { /* Light yellow for warning */
                background-color: #fffde7;
                border-left: 5px solid #ffc107;
            }
            .stSelectbox label, .stFileUploader label, .stTextInput label, .stTextArea label {
                font-weight: 600;
                color: #333;
                font-size: 1.05em;
            }
            .stDownloadButton button {
                background-color: #00bcd4; /* Teal for download */
            }
            .stDownloadButton button:hover {
                background-color: #0097a7;
            }
            .stExpander > div:first-child { /* Style for expander header */
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px 15px;
                font-weight: bold;
                color: #3F51B5;
            }
            .stExpander > div:first-child:hover {
                background-color: #e0e0e0;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("📄 AI-Powered Resume Screener")
    st.markdown("### Instantly assess candidate fit with advanced AI matching and personalized feedback.")

    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'jd_text_input' not in st.session_state:
        st.session_state.jd_text_input = ""
    if 'jd_selection_method' not in st.session_state:
        st.session_state.jd_selection_method = "Paste JD"
    if 'selected_jd_file' not in st.session_state:
        st.session_state.selected_jd_file = "Paste New JD"
    if 'certificate_html_content' not in st.session_state:
        st.session_state['certificate_html_content'] = ""

    jd_text = ""
    jd_name_for_results = "User Provided JD"

    with st.container(border=True):
        st.markdown("## ⚙️ Define Job Requirements & Screening Criteria")
        st.markdown("Choose how you want to provide the Job Description (JD).")
        col1_jd, col2_jd = st.columns([2, 1])

        with col1_jd:
            pre_loaded_jd_paths = load_jds_from_folder("data")
            jd_options_display = ["Paste New JD", "Upload my own"] + sorted(list(pre_loaded_jd_paths.keys()))
            
            jd_option_selected = st.selectbox(
                "📌 **Select a Pre-Loaded Job Role or Upload Your Own Job Description**",
                jd_options_display,
                key="jd_option_selector",
                help="You can either paste a new job description, upload a file, or select from our pre-loaded examples."
            )

            uploaded_jd_file = None

            if jd_option_selected == "Paste New JD":
                jd_text = st.text_area(
                    "Paste the Job Description here:",
                    height=300,
                    key="jd_text_input_paste",
                    placeholder="E.g., 'We are looking for a Software Engineer with strong Python, AWS, and React skills...'"
                )
                jd_name_for_results = "User Provided JD (Pasted)"
            elif jd_option_selected == "Upload my own":
                uploaded_jd_file = st.file_uploader(
                    "Upload Job Description (TXT, PDF)",
                    type=["txt", "pdf"],
                    help="Upload a .txt or .pdf file containing the job description. Ensure it's text-selectable.",
                    key="jd_file_uploader"
                )
                if uploaded_jd_file:
                    jd_text = extract_text_from_file(uploaded_jd_file.read(), uploaded_jd_file.name, uploaded_jd_file.type)
                    jd_name_for_results = uploaded_jd_file.name.replace('.pdf', '').replace('.txt', '')
                else:
                    jd_name_for_results = "Uploaded JD (No file selected)"
            else:
                jd_path = pre_loaded_jd_paths.get(jd_option_selected)
                if jd_path and os.path.exists(jd_path):
                    try:
                        with open(jd_path, "r", encoding="utf-8") as f:
                            jd_text = f.read()
                        jd_name_for_results = jd_option_selected
                    except Exception as e:
                        st.error(f"❌ Error loading selected JD from file '{jd_path}': {e}")
                        jd_text = ""
                        jd_name_for_results = "Error Loading JD"
                else:
                    st.error(f"❌ Selected JD file not found: {jd_path}")
                    jd_text = ""
                    jd_name_for_results = "Error Loading JD"

        with col2_jd:
            if jd_text:
                with st.expander("📝 View Loaded Job Description"):
                    st.text_area("Job Description Content", jd_text, height=200, disabled=True, label_visibility="collapsed")
                
                st.markdown("---")
                st.markdown("### ☁️ Job Description Keyword Cloud")
                st.caption("Visualizing the most frequent and important keywords from the Job Description.")
                
                jd_words_for_cloud_set, _ = extract_relevant_keywords(jd_text, MASTER_SKILLS) 
                jd_words_for_cloud = " ".join(list(jd_words_for_cloud_set))

                if jd_words_for_cloud:
                    wordcloud = WordCloud(width=800, height=400, background_color='white', collocations=False).generate(jd_words_for_cloud)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("ℹ️ No significant keywords to display for the Job Description. Please ensure your JD has sufficient content or adjust your SKILL_CATEGORIES list.")
            else:
                st.info("👆 Please select or upload a Job Description to view its keyword cloud.")

    with st.container(border=True):
        st.markdown("## 🏢 Target Company Fit (Optional)")
        st.caption("Assess how well your resume aligns with a specific company's profile.")
        target_company_name = st.selectbox(
            "**Select a Target Company**",
            options=["None"] + sorted(list(COMPANY_SKILL_PROFILES.keys())),
            index=0,
            help="Choose a company from the list to see how well your resume aligns with its typical profile. This is based on a simplified, predefined list of company keywords.",
            key="target_company_selector"
        )
        if target_company_name != "None":
            st.info(f"💡 A small score boost will be applied if your resume matches skills important to **{target_company_name}**. A detailed company fit assessment will also be provided.")
        
        with st.expander("📚 View All Company Profiles"):
            st.code(json.dumps(COMPANY_SKILL_PROFILES, indent=2), language='json')
            st.markdown("You can modify the `company_profiles.py` file directly to add or update company profiles.")

    with st.container(border=True):
        st.markdown("## 📥 Upload Resume")
        uploaded_resume_file = st.file_uploader(
            "Upload a resume (PDF only)",
            type=["pdf"],
            help="Please upload a text-selectable PDF resume for best results.",
            key="resume_uploader"
        )

    st.markdown("---")
    screen_button_col, _ = st.columns([0.3, 0.7])
    with screen_button_col:
        if st.button("🚀 Screen Resume", use_container_width=True):
            if not jd_text.strip():
                st.error("⚠️ Please provide a Job Description to proceed with screening.")
            elif not uploaded_resume_file:
                st.error("⚠️ Please upload a resume to proceed with screening.")
            else:
                with st.spinner("Processing resume and generating insights... This may take a few moments."):
                    try:
                        resume_bytes = uploaded_resume_file.read()
                        resume_text = extract_text_from_file(resume_bytes, uploaded_resume_file.name, uploaded_resume_file.type)

                        if resume_text.startswith("[ERROR]"):
                            st.error(resume_text)
                            st.session_state.results = None
                            return

                        jd_embedding = global_sentence_model.encode(clean_text(jd_text), convert_to_tensor=True)
                        resume_embedding = global_sentence_model.encode(clean_text(resume_text), convert_to_tensor=True)

                        screening_results = _process_single_resume_for_screener_page(
                            file_name=uploaded_resume_file.name,
                            text=resume_text,
                            jd_text=jd_text,
                            jd_embedding=jd_embedding,
                            resume_embedding=resume_embedding,
                            jd_name_for_results=jd_name_for_results,
                            _global_ml_model=global_ml_model,
                            target_company_name=target_company_name
                        )
                        st.session_state.results = screening_results
                        st.success("✅ Analysis complete! See the results below.")

                        if st.session_state.results and st.session_state.results['Email'] != 'Not Found' and st.session_state.results['Skill Match'] >= 50:
                            gmail_address = st.secrets.get("GMAIL_ADDRESS")
                            gmail_app_password = st.secrets.get("GMAIL_APP_PASSWORD")

                            if gmail_address and gmail_app_password:
                                st.info("📧 Attempting to automatically send certificate...")
                                try:
                                    certificate_html_content = generate_certificate_html(st.session_state.results)
                                except NameError:
                                    st.warning("`generate_certificate_html` function not found. Certificate HTML preview and PDF generation will not work.")
                                    certificate_html_content = "Certificate HTML content placeholder."
                                
                                certificate_public_url = f"{CERTIFICATE_HOSTING_URL}?id={st.session_state.results['Certificate ID']}"
                                
                                send_certificate_email(
                                    recipient_email=st.session_state.results['Email'],
                                    candidate_name=st.session_state.results['Candidate Name'],
                                    score=st.session_state.results['Skill Match'],
                                    certificate_html_content=certificate_html_content,
                                    certificate_public_url=certificate_public_url,
                                    gmail_address=gmail_address,
                                    gmail_app_password=gmail_app_password
                                )
                            else:
                                st.warning("⚠️ Email sending not configured. Certificate was not sent automatically. Please check your Streamlit secrets for GMAIL_ADDRESS and GMAIL_APP_PASSWORD.")
                        elif st.session_state.results and st.session_state.results['Email'] == 'Not Found':
                            st.warning("⚠️ No email address found in the resume. Certificate could not be sent automatically.")
                        elif st.session_state.results and st.session_state.results['Skill Match'] < 50:
                            st.info(f"ℹ️ Candidate score ({st.session_state.results['Skill Match']:.2f}%) is below the 50% threshold for automatic certificate issuance.")

                    except Exception as e:
                        st.error(f"❌ An unexpected error occurred during processing: {e}")
                        traceback.print_exc()
                        st.session_state.results = None

    if st.session_state.results:
        results = st.session_state.results
        st.markdown("---")
        st.markdown("## 📊 Screening Results")

        st.markdown(f"### Candidate: **{results['Candidate Name']}**")
        
        col_score, col_tag = st.columns(2)
        with col_score:
            st.metric(label="Overall Match Score", value=f"{results['Skill Match']:.2f}%", delta_color="off", help="This score reflects the overall alignment of the resume with the job description, including semantic understanding and keyword match.")
        with col_tag:
            st.metric(label="Candidate Tag", value=results['Tag'], delta_color="off", help="A quick tag indicating the candidate's fit category based on their score and semantic match.")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["AI Feedback", "Company Fit", "Extracted Information", "Skill Alignment", "Certificate"])

        with tab1:
            st.markdown(results['LLM Feedback'])
        
        with tab2:
            st.markdown(results['Company Fit Assessment'])

        with tab3:
            st.markdown("### 👤 Personal Details")
            st.write(f"**Email:** {results['Email']}")
            st.write(f"**Phone Number:** {results['Phone Number']}")
            st.write(f"**Location:** {results['Location']}")
            st.write(f"**Languages:** {results['Languages']}")
            st.write(f"**Years of Experience:** {results['Years Experience']:.1f}")
            st.write(f"**CGPA (4.0 Scale):** {results['CGPA (4.0 Scale)'] if results['CGPA (4.0 Scale)'] is not None else 'Not Found'}")

            st.markdown("### 🎓 Education")
            st.write(f"**Education Details:** {results['Education Details']}")

            st.markdown("### 💼 Work History")
            if results['Work History'] != "Not Found":
                for entry in results['Work History'].split('; '):
                    st.markdown(f"- {entry}")
            else:
                st.write("Not Found")

            st.markdown("### 💡 Projects")
            if results['Project Details'] != "Not Found":
                for entry in results['Project Details'].split('; '):
                    st.markdown(f"- {entry}")
            else:
                st.write("Not Found")

        with tab4:
            col_matched, col_missing = st.columns(2)
            with col_matched:
                st.markdown("✅ **Matched Skills:**")
                if results['Matched Skills']:
                    for skill in sorted(results['Matched Skills']):
                        st.markdown(f"- {skill.title()}")
                else:
                    st.markdown("- No direct skill matches found.")

            with col_missing:
                st.markdown("❌ **Missing Skills & Learning Links:**")
                if results['Missing Skills']:
                    for skill in sorted(results['Missing Skills']):
                        st.markdown(f"**{skill.title()}**:")
                        links = get_learning_links(skill)
                        for platform, url in links.items():
                            st.markdown(f"  - 🔗 [{platform}]({url})", unsafe_allow_html=True)
                else:
                    st.markdown("- No missing skills identified based on JD.")
                    st.markdown("Great job! Your skills align well with the job description.")

        with tab5:
            st.markdown("### 🏆 Your ScreenerPro Certificate")
            st.markdown(f"Your unique Certificate ID: `{results['Certificate ID']}`")
            st.markdown(f"**Rank Achieved:** {results['Certificate Rank']}")

            certificate_html_content = generate_certificate_html(results)

            download_col, email_col_manual = st.columns(2) # Renamed email_col to email_col_manual to avoid conflict with manual email expander
            with download_col:
                st.download_button(
                    label="Download Certificate (PDF)",
                    data=HTML(string=certificate_html_content).write_pdf(),
                    file_name=f"ScreenerPro_Certificate_{results['Candidate Name'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with email_col_manual:
                with st.expander("Manually Email Certificate"):
                    recipient_email = st.text_input("Enter recipient email address:", value=results['Email'] if results['Email'] != 'Not Found' else '', key="manual_email_input")
                    if st.button("Send Certificate via Email (Manual)", key="send_manual_email_button"):
                        if recipient_email and re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
                            gmail_address = st.secrets.get("GMAIL_ADDRESS")
                            gmail_app_password = st.secrets.get("GMAIL_APP_PASSWORD")
                            
                            if gmail_address and gmail_app_password:
                                with st.spinner("Sending email..."):
                                    send_certificate_email(
                                        recipient_email=recipient_email,
                                        candidate_name=results['Candidate Name'],
                                        score=results['Skill Match'],
                                        certificate_html_content=certificate_html_content,
                                        certificate_public_url=f"{CERTIFICATE_HOSTING_URL}?id={results['Certificate ID']}",
                                        gmail_address=gmail_address,
                                        gmail_app_password=gmail_app_password
                                    )
                            else:
                                st.error("❌ Email sending is not configured. Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your Streamlit secrets.")
                        else:
                            st.error("❌ Please enter a valid recipient email address.")

        st.markdown("---")
        st.markdown("### 📈 Contribute to Leaderboard")
        st.caption("Help us build a public leaderboard of top screening results!")
        leaderboard_col, _ = st.columns([0.3, 0.7])
        with leaderboard_col:
            if st.button("Add My Score to Leaderboard", use_container_width=True):
                with st.spinner("Saving to leaderboard..."):
                    save_screening_result_to_firestore_rest(results)

if __name__ == "__main__":
    resume_screener_page()
