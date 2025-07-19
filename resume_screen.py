import streamlit as st
import pdfplumber
import re
import os
import sklearn
import joblib
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sentence_transformers import SentenceTransformer
import nltk
import collections
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase # Import MIMEBase for file attachment
from email import encoders
from io import BytesIO
import traceback
import time
import pandas as pd
import json
import requests # Import requests for REST API calls
from weasyprint import HTML # Re-added: WeasyPrint for PDF generation

# CRITICAL: Disable Hugging Face tokenizers parallelism to avoid deadlocks with ProcessPoolExecutor
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Global NLTK download check (should run once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Define global constants
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

# --- NEW: Company Skill Profiles (Expanded for Demonstration) ---
# This dictionary maps company names to a list of keywords/phrases
# that represent their typical tech stack, industry focus, or values.
# In a real-world scenario, this would be a much larger, dynamically updated database.
COMPANY_SKILL_PROFILES = {
        "Google": {
        "description": "A global technology company focusing on search, cloud computing, artificial intelligence, and hardware.",
        "keywords": ["Google Cloud Platform", "GCP", "Kubernetes", "TensorFlow", "Python", "Go", "Machine Learning", "BigQuery", "Data Science", "AI", "Distributed Systems", "Algorithms", "Scale", "Innovation", "Android", "Chrome", "Deep Learning", "Search Engine Optimization", "AdTech", "Material Design", "Wearables", "Autonomous Vehicles (Waymo)", "Robotics"]
    },
    "Microsoft": {
        "description": "A multinational technology corporation producing computer software, consumer electronics, personal computers, and related services.",
        "keywords": ["Azure", "C#", ".NET", "SQL Server", "Microsoft 365", "Dynamics 365", "Power BI", "Cloud Computing", "Enterprise Software", "Windows", "AI", "DevOps", "Cybersecurity", "TypeScript", "Gaming (Xbox)", "Active Directory", "SharePoint", "Visual Studio", "Low-Code (Power Apps)", "Mixed Reality (HoloLens)", "Quantum Computing"]
    },
    "Amazon": {
        "description": "An American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.",
        "keywords": ["AWS", "Cloud Computing", "Serverless", "DynamoDB", "S3", "Lambda", "EC2", "Microservices", "Scale", "E-commerce", "Logistics", "Machine Learning", "Alexa", "Data Engineering", "Supply Chain", "Retail Tech", "Fulfillment", "Prime Video", "Kindle", "Robotics (Warehouse)", "Natural Language Processing (NLP)", "Computer Vision"]
    },
    "Meta (Facebook)": {
        "description": "A technology conglomerate focusing on social media, virtual reality, and artificial intelligence.",
        "keywords": ["React", "PyTorch", "GraphQL", "AI", "Machine Learning", "Virtual Reality (VR)", "Augmented Reality (AR)", "Social Media", "Data Science", "Python", "PHP", "Distributed Systems", "Mobile Development", "Computer Vision", "Privacy", "Content Moderation", "Recommendation Engines", "AdTech", "Horizon Worlds", "Ray-Ban Meta Smart Glasses"]
    },
    "Apple": {
        "description": "A multinational technology company focusing on consumer electronics, software, and online services.",
        "keywords": ["iOS", "Swift", "Objective-C", "macOS", "Xcode", "Mobile Development", "Hardware Engineering", "User Experience (UX)", "Design Thinking", "Privacy", "Security", "AI (Siri)", "Cloud (iCloud)", "WatchOS", "iPadOS", "tvOS", "Apple Silicon", "HealthKit", "ARKit", "Apple Pay", "App Store", "Services Revenue"]
    },
    "Netflix": {
        "description": "A streaming service and production company.",
        "keywords": ["AWS", "Microservices", "Distributed Systems", "Java", "Python", "Data Science", "Machine Learning", "Recommendation Systems", "Streaming", "Cloud Native", "DevOps", "Big Data", "User Experience (UX)", "Content Delivery Networks (CDN)", "Video Encoding", "Personalization", "A/B Testing", "Chaos Engineering"]
    },
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce", "CRM", "Apex", "Lightning Web Components", "Cloud Computing", "SaaS", "Enterprise Software", "Customer Success", "Data Analytics", "Integration (MuleSoft)", "Platform Development", "Marketing Cloud", "Service Cloud", "Einstein AI", "Tableau", "Slack"]
    },
    "Generic Tech Startup": {
        "description": "A fast-paced, innovative technology company, often focused on new technologies and agile development.",
        "keywords": ["Agile", "Scrum", "Fast-paced", "Innovation", "MVP", "Growth Hacking", "Fullstack Development", "React", "Node.js", "Python", "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Problem Solving", "Adaptability", "Entrepreneurship", "Cross-functional Teams", "Product-led Growth", "Seed Funding", "Series A/B"]
    },
    "IBM": {
        "description": "An American multinational technology and consulting company, specializing in computer hardware, middleware, and software.",
        "keywords": ["Cloud Computing (IBM Cloud)", "AI (Watson)", "Enterprise Solutions", "Blockchain", "Quantum Computing", "Consulting", "Hybrid Cloud", "Data Analytics", "Java", "Linux", "Mainframe", "Cybersecurity", "Red Hat", "OpenShift", "Automation (RPA)", "IT Services", "Storage Solutions", "Server Technologies"]
    },
    "Oracle": {
        "description": "A multinational computer technology corporation best known for its database software and cloud engineered systems.",
        "keywords": ["Oracle Database", "SQL", "Cloud Infrastructure (OCI)", "ERP (Fusion Applications)", "CRM", "Java", "Enterprise Software", "SaaS", "Data Warehousing", "Middleware", "Cloud Applications", "NetSuite", "Peoplesoft", "Supply Chain Management"]
    },
    "Cisco": {
        "description": "An American multinational digital communications technology conglomerate corporation that develops, manufactures, and sells networking hardware, software, telecommunications equipment, and other high-technology services and products.",
        "keywords": ["Networking", "Cybersecurity (Talos, Duo, Meraki)", "Routers", "Switches", "Collaboration Tools (Webex)", "Cloud Networking", "IoT", "Enterprise Security", "SD-WAN", "Python (for automation)", "Network Automation", "Data Center Networking", "Voice over IP (VoIP)", "Firewalls"]
    },
    "Adobe": {
        "description": "An American multinational computer software company that has historically focused upon the creation of multimedia and creativity software products.",
        "keywords": ["Creative Cloud", "Photoshop", "Illustrator", "Premiere Pro", "Experience Cloud", "Digital Marketing", "SaaS", "Cloud Computing", "User Interface (UI)", "User Experience (UX)", "Web Development", "Content Management", "Analytics (Adobe Analytics)", "Targeting", "Audience Management", "AI (Sensei)", "Video Editing", "Graphic Design"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP (SAP S/4HANA)", "CRM", "Cloud Computing", "Business Intelligence (SAP BW/4HANA)", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS", "SAP Fiori", "Data Warehousing", "SAP Concur", "Ariba"]
    },
    "Intel": {
        "description": "An American multinational corporation and technology company that is the world's largest semiconductor chip manufacturer by revenue.",
        "keywords": ["Semiconductors", "Processors (CPUs)", "Microarchitecture", "Hardware Engineering", "Chip Design", "Manufacturing", "IoT", "AI Accelerators", "Cloud Computing Infrastructure", "Embedded Systems", "Security (McAfee)", "FPGA", "Xeon", "Core", "Ecosystem Development"]
    },
    "NVIDIA": {
        "description": "A global technology company that designs graphics processing units (GPUs) for the gaming, professional visualization, data center, and automotive markets.",
        "keywords": ["GPU", "AI", "Deep Learning", "Machine Learning", "CUDA", "Computer Graphics", "High-Performance Computing (HPC)", "Gaming", "Autonomous Vehicles", "Data Center", "TensorFlow", "PyTorch", "Robotics (Isaac)", "Virtual Reality", "Ray Tracing", "Simulation (Omniverse)"]
    },
    "Tesla": {
        "description": "An American multinational automotive and clean energy company.",
        "keywords": ["Electric Vehicles (EV)", "Battery Technology", "AI", "Autonomous Driving", "Robotics", "Software Engineering (Automotive)", "Manufacturing", "Energy Storage", "Machine Learning (Computer Vision)", "Embedded Systems", "Gigafactory", "Powerwall", "Supercharger Network"]
    },
    "SpaceX": {
        "description": "An American spacecraft manufacturer, launch service provider, and satellite communications company.",
        "keywords": ["Aerospace Engineering", "Rocketry", "Satellite Communications (Starlink)", "Propulsion", "Manufacturing", "Software Engineering (Aerospace)", "Embedded Systems", "Guidance, Navigation, and Control (GNC)", "Reusable Rockets", "Space Exploration", "Avionics", "Ground Systems"]
    },
    "Zoom": {
        "description": "A communications technology company providing video telephony and online chat services.",
        "keywords": ["Video Conferencing", "Real-time Communication", "Cloud Infrastructure", "Scalability", "Audio/Video Processing", "Network Protocols", "Security", "SaaS", "Collaboration Tools", "Web Development (WebRTC)", "API Integration", "User Interface (UI)"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development (Now Platform)", "Service Management", "Operations Management", "Security Operations"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM (Human Capital Management)", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting", "Adaptive Planning", "Recruiting", "Benefits Administration"]
    },
    "T-Mobile (US)": {
        "description": "A major American wireless network operator.",
        "keywords": ["Telecommunications", "5G", "Wireless Networks", "Mobile Technology", "Network Engineering", "Customer Experience", "IoT Connectivity", "VoIP", "Fiber Optics", "Cloud Native (Telecom)", "Billing Systems"]
    },
    "Verizon": {
        "description": "An American multinational telecommunications conglomerate and a wireless network operator.",
        "keywords": ["Telecommunications", "5G", "Wireless Networks", "Fiber Optic Networks", "IoT", "Enterprise Solutions", "Network Security", "Cloud Services", "Edge Computing", "Media & Entertainment (Verizon Media)", "Digital Marketing"]
    },
    "AT&T": {
        "description": "An American multinational telecommunications holding company.",
        "keywords": ["Telecommunications", "5G", "Fiber Optics", "Wireless Services", "Broadband", "Network Infrastructure", "Cybersecurity", "Entertainment (Warner Bros. Discovery)", "IoT Solutions", "Enterprise Connectivity"]
    },
    "Qualcomm": {
        "description": "A global semiconductor company that designs and markets wireless telecommunications products and services.",
        "keywords": ["Semiconductors", "Mobile Processors (Snapdragon)", "5G Technology", "Wireless Communication", "IoT", "Automotive (ADAS)", "Chip Design", "Embedded Systems", "AI Processors", "RF Front End", "Modems"]
    },
    "Broadcom": {
        "description": "A global infrastructure technology company designing, developing, and supplying a broad range of semiconductor and infrastructure software solutions.",
        "keywords": ["Semiconductors", "Networking Hardware", "Storage Solutions", "Broadband Communication", "Enterprise Software", "Cybersecurity (Symantec)", "Mainframe Software (CA Technologies)", "Fiber Optics", "Wireless Connectivity"]
    },
    "VMware (now Broadcom subsidiary)": {
        "description": "A cloud computing and virtualization technology company, now part of Broadcom.",
        "keywords": ["Virtualization", "Cloud Computing", "Data Center", "SDDC (Software-Defined Data Center)", "Network Virtualization (NSX)", "Storage Virtualization (vSAN)", "Hybrid Cloud", "Multi-Cloud", "Containerization (Tanzu)", "Kubernetes", "VMs (Virtual Machines)", "VDI (Virtual Desktop Infrastructure)"]
    },
    "Palo Alto Networks": {
        "description": "A global cybersecurity leader providing enterprise security solutions.",
        "keywords": ["Cybersecurity", "Network Security", "Cloud Security", "Endpoint Security", "Firewalls", "Threat Detection", "Incident Response", "AI in Security", "Machine Learning in Security", "Zero Trust", "Security Operations (SecOps)", "SaaS Security"]
    },
    "CrowdStrike": {
        "description": "A cybersecurity technology company focused on endpoint protection.",
        "keywords": ["Cybersecurity", "Endpoint Detection and Response (EDR)", "Cloud Security", "Threat Intelligence", "Incident Response", "AI in Security", "Machine Learning", "XDR (Extended Detection and Response)", "Security Analytics", "Cloud Native Security"]
    },
    "Snowflake": {
        "description": "A cloud-based data warehousing company offering a data cloud platform.",
        "keywords": ["Data Warehousing", "Cloud Data Platform", "SQL", "Big Data", "Data Lakes", "Data Sharing", "Data Governance", "Analytics", "Machine Learning (Data)", "Snowflake Native Apps", "Data Engineering", "Performance Optimization"]
    },
    "Databricks": {
        "description": "A company providing a cloud-based data lakehouse platform for data science and AI.",
        "keywords": ["Data Lakehouse", "Spark", "Data Science", "Machine Learning", "AI", "Big Data", "Data Engineering", "Delta Lake", "MLflow", "Lakehouse Architecture", "Python", "Scala", "SQL", "Data Bricks Runtime"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development (Now Platform)", "Service Management", "Operations Management", "Security Operations"]
    },
    "Okta": {
        "description": "A leading independent provider of identity for the enterprise.",
        "keywords": ["Identity and Access Management (IAM)", "Single Sign-On (SSO)", "Multi-Factor Authentication (MFA)", "Cloud Security", "API Security", "Enterprise Security", "Zero Trust", "AuthN/AuthZ"]
    },
    "Zscaler": {
        "description": "A cloud security company offering a cloud-native security platform.",
        "keywords": ["Cloud Security", "Zero Trust Network Access (ZTNA)", "SASE (Secure Access Service Edge)", "Network Security", "Cybersecurity", "Secure Web Gateway (SWG)", "Cloud Firewall", "Proxy Services"]
    },
    "Twilio": {
        "description": "A cloud communications platform as a service (CPaaS) company.",
        "keywords": ["CPaaS", "APIs", "Cloud Communications", "SMS", "Voice", "Video", "Email", "Customer Engagement", "Programmable Communications", "Twilio Segment (CDP)", "Twilio Flex (Contact Center)"]
    },
    "Shopify": {
        "description": "A leading e-commerce platform for online stores and retail point-of-sale systems.",
        "keywords": ["E-commerce", "SaaS", "Online Retail", "Shopify Plus", "Payment Gateways", "Logistics", "Inventory Management", "Marketing Automation", "Web Development", "Ruby on Rails", "React", "Store Management"]
    },
    "Square (Block, Inc.)": {
        "description": "A financial services and mobile payment company.",
        "keywords": ["FinTech", "Mobile Payments", "Payment Processing", "Point-of-Sale (POS)", "SME Solutions", "Cash App", "Bitcoin (Square Crypto)", "Business Banking", "Hardware (Readers)", "Blockchain"]
    },
    "Stripe": {
        "description": "A financial technology company offering payment processing software and APIs.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "SaaS", "Billing", "Fraud Prevention", "Global Payments", "Developer Tools", "Financial Infrastructure", "Stripe Connect"]
    },
    "DocuSign": {
        "description": "A company providing electronic signature technology and digital transaction management services.",
        "keywords": ["Electronic Signature", "Digital Transformation", "SaaS", "Workflow Automation", "Document Management", "Legal Tech", "Compliance", "Cloud Security", "API Integration"]
    },
    "Coupa Software": {
        "description": "A business spend management (BSM) software company.",
        "keywords": ["Procurement Software", "Spend Management", "SaaS", "Cloud Computing", "Supply Chain Management", "Financial Software", "Contract Management", "Expense Management"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting"]
    },
    "Zendesk": {
        "description": "A customer service software company building products designed to improve customer relationships.",
        "keywords": ["Customer Service", "CRM", "SaaS", "Help Desk Software", "Ticketing System", "Customer Support", "Chatbot", "Knowledge Base", "Customer Experience (CX)", "Analytics"]
    },
    "Splunk": {
        "description": "A software company that produces software for searching, monitoring, and analyzing machine-generated big data.",
        "keywords": ["Big Data", "Data Analytics", "Machine Data", "SIEM (Security Information and Event Management)", "IT Operations", "Cybersecurity", "Observability", "Monitoring", "Log Management", "Search Technology", "Dashboards"]
    },
    "Datadog": {
        "description": "A monitoring and analytics platform for developers, IT operations teams and business users.",
        "keywords": ["Monitoring", "Observability", "Cloud Monitoring", "Application Performance Monitoring (APM)", "Log Management", "Infrastructure Monitoring", "Security Monitoring", "DevOps", "Kubernetes Monitoring", "Cloud Native"]
    },
    "PwC": {
        "description": "A multinational professional services network, providing audit, assurance, consulting, and tax services.",
        "keywords": ["Consulting", "Digital Transformation", "Cybersecurity Consulting", "Cloud Strategy", "Data Analytics Consulting", "Enterprise Architecture", "Technology Advisory", "ERP Implementation", "Financial Consulting", "Management Consulting"]
    },
    "Deloitte": {
        "description": "One of the 'Big Four' accounting organizations and the largest professional services network by revenue and number of professionals.",
        "keywords": ["Consulting", "IT Consulting", "Digital Transformation", "Cybersecurity Consulting", "Cloud Strategy", "Data Science Consulting", "AI Strategy", "Enterprise Solutions", "Risk Advisory", "Strategy Consulting"]
    },
    "EY (Ernst & Young)": {
        "description": "A multinational professional services firm, one of the 'Big Four' accounting firms.",
        "keywords": ["Consulting", "Technology Consulting", "Digital Transformation", "Cybersecurity", "Data Analytics", "Cloud Services", "AI & Automation", "Strategy & Transactions", "Advisory Services"]
    },
    "KPMG": {
        "description": "A multinational professional services network, and one of the 'Big Four' accounting organizations.",
        "keywords": ["Consulting", "Digital Transformation", "Cybersecurity", "Cloud Advisory", "Data & Analytics", "Emerging Technologies", "Risk Consulting", "Financial Services Consulting", "Technology Implementation"]
    },
    # Indian Companies - IT Services & Consulting
    "Tata Consultancy Services (TCS)": {
        "description": "A leading global IT services, consulting, and business solutions organization and part of the Tata Group.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Cybersecurity", "IoT", "Agile", "DevOps", "Java", "Python", "SAP", "Oracle", "Automation", "Blockchain", "Financial Services", "Manufacturing", "Cognitive Business Operations", "Assurance Services", "Engineering & Industrial Services"]
    },
    "Infosys": {
        "description": "A global leader in next-generation digital services and consulting.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "IoT", "Automation", "Enterprise Applications", "SAP", "Oracle", "Java", "Python", "Big Data", "DevOps", "Blockchain", "Consulting", "Digital Experience", "Legacy Modernization", "Finacle (Banking Software)"]
    },
    "Wipro": {
        "description": "A global information technology, consulting, and business process services company.",
        "keywords": ["IT Services", "Consulting", "Digital Transformation", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Cybersecurity", "IoT", "Automation", "DevOps", "SAP", "Oracle", "Java", "Python", "Analytics", "Blockchain", "Industry Solutions", "Application Development & Management", "Infrastructure Services"]
    },
    "HCLTech": {
        "description": "A global technology company that helps enterprises reimagine their businesses for the digital age.",
        "keywords": ["Digital Engineering", "Cloud Adoption", "IoT Solutions", "Automation", "Security", "Analytics", "Digital Transformation", "AI", "Machine Learning", "Cybersecurity", "Fullstack Development", "Cloud Native", "DevOps", "Enterprise Applications", "Product Engineering", "Infrastructure Modernization"]
    },
    "Tech Mahindra": {
        "description": "An Indian multinational information technology services and consulting company.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Cybersecurity", "Network Services", "Business Process Services", "Enterprise Applications", "Engineering Services", "Blockchain", "5G", "IoT", "Robotics", "Telecommunications", "CRM Services", "Data Analytics"]
    },
    "LTIMindtree": {
        "description": "An Indian multinational information technology services and consulting company, formed by the merger of L&T Infotech and Mindtree.",
        "keywords": ["IT Services", "Digital Transformation", "Cloud Computing", "Data & Analytics", "Generative AI", "Application Development", "Cybersecurity", "Enterprise Solutions", "IoT", "DevOps", "Agile", "Consulting", "Product Engineering", "Customer Experience (CX)", "SAP", "Oracle"]
    },
    "Cognizant": {
        "description": "A global information technology services and consulting company with a significant presence in India.",
        "keywords": ["IT Consulting", "Digital Strategy", "Cloud Solutions", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Application Development", "Business Process Services", "Industry Solutions", "DevOps", "Agile", "Digital Engineering", "Enterprise Transformation"]
    },
    "Capgemini (India Operations)": {
        "description": "A global leader in consulting, technology services, and digital transformation, with strong operations in India.",
        "keywords": ["Consulting", "IT Services", "Digital Transformation", "Cloud Computing", "AI", "Data Analytics", "Cybersecurity", "Application Services", "DevOps", "Agile", "SAP", "Oracle", "Industry Expertise", "Intelligent Automation", "Customer Experience"]
    },
    "Persistent Systems": {
        "description": "A global services company that provides software product development and technology services.",
        "keywords": ["Product Engineering", "Digital Engineering", "Cloud Native", "Data & AI", "Enterprise Modernization", "Software Development", "Agile", "DevOps", "Banking & Financial Services (BFS)", "Healthcare Tech", "Life Sciences", "IoT Solutions"]
    },
    "Mphasis": {
        "description": "A global information technology solutions provider specializing in cloud and cognitive services.",
        "keywords": ["Cloud Transformation", "AI", "Cognitive Technologies", "Digital Transformation", "DevOps", "Automation", "Cybersecurity", "Data Analytics", "IT Services", "Blockchain", "Application Modernization", "Financial Services Tech"]
    },
    "Coforge (formerly NIIT Technologies)": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    # Indian Companies - Startups & Product Companies
    "Reliance Jio Platforms": {
        "description": "A technology company providing digital services, including mobile connectivity, broadband, and various digital platforms.",
        "keywords": ["5G", "Telecommunications", "Digital Services", "Cloud Platforms", "AI", "IoT", "Big Data", "Mobile Technology", "Fixed Wireless Access (FWA)", "E-commerce (JioMart)", "FinTech (JioMoney)", "Content Streaming (JioCinema)", "Fiber Optics", "Digital Payments", "Edge Computing"]
    },
    "Flipkart": {
        "description": "An Indian e-commerce company, a subsidiary of Walmart, offering a wide range of products.",
        "keywords": ["E-commerce", "Supply Chain", "Logistics", "Retail Technology", "Mobile Development", "Android", "iOS", "Data Science", "Machine Learning (Recommendations)", "Cloud Infrastructure (AWS, GCP)", "Microservices", "Payments", "Fraud Detection", "Personalization", "Big Data", "Customer Experience"]
    },
    "Zomato": {
        "description": "An Indian multinational restaurant aggregator and food delivery company.",
        "keywords": ["Food Delivery", "Restaurant Technology", "Logistics", "Mobile Development", "Data Analytics", "Machine Learning (Recommendation Systems)", "Cloud Infrastructure (AWS)", "Geolocation", "Payment Gateways", "User Experience (UX)", "Growth Hacking", "Hyperlocal", "Mapping", "Real-time Systems"]
    },
    "Swiggy": {
        "description": "An Indian online food ordering and delivery platform.",
        "keywords": ["Food Delivery", "Quick Commerce (Instamart)", "Logistics Optimization", "Mobile Development", "Data Science", "Machine Learning", "Real-time Systems", "Cloud Platforms (AWS)", "Geolocation", "Payments", "User Experience (UX)", "Route Optimization", "Demand Forecasting"]
    },
    "Paytm": {
        "description": "An Indian multinational financial technology company specializing in digital payment systems, e-commerce, and financial services.",
        "keywords": ["FinTech", "Digital Payments", "Mobile Wallets", "UPI", "E-commerce", "Financial Services", "Blockchain", "Cybersecurity", "Data Analytics", "Fraud Detection", "Cloud Computing", "Microservices", "Scalability", "Security", "Investment Tech", "Lending", "Insurance Tech"]
    },
    "Ola": {
        "description": "An Indian multinational ridesharing company offering transportation, food delivery, and financial services.",
        "keywords": ["Ridesharing", "Mobility Solutions", "Electric Vehicles (EV)", "Logistics", "Geolocation", "Mobile Development", "Data Science", "Machine Learning (Pricing, Routing)", "Cloud Platforms (AWS)", "Payment Systems", "User Experience", "Fleet Management", "Mapping", "Autonomous Driving (early stages)"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation (Video, Animation)", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics (Student Progress)", "Curriculum Development", "User Experience", "Subscription Models", "Gamification", "Adaptive Learning", "K-12 Education"]
    },
    "CRED": {
        "description": "A members-only credit card bill payment platform that rewards its members for clearing their credit card bills on time.",
        "keywords": ["FinTech", "Credit Scoring", "Payments", "Data Analytics", "User Experience (UX)", "Mobile App Development", "Security", "Wealth Management (early stages)", "Loyalty Programs", "Personal Finance"]
    },
    "Razorpay": {
        "description": "A leading Indian fintech company that provides payment solutions for businesses of all sizes.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "UPI", "Payment Processing", "SME Solutions", "Banking Tech", "Neo-banking", "Payroll Management", "Fraud Detection", "Data Analytics", "Scalability"]
    },
    "PhonePe": {
        "description": "An Indian digital payments and financial services company, a subsidiary of Flipkart.",
        "keywords": ["FinTech", "Digital Payments", "UPI", "Mobile Wallets", "Financial Services", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Geolocation", "Security", "Data Analytics", "Scalability"]
    },
    "Meesho": {
        "description": "An Indian social commerce platform enabling small businesses and individuals to start online businesses without investment.",
        "keywords": ["E-commerce", "Social Commerce", "Reselling", "Logistics", "Supply Chain", "Mobile Development", "Data Science", "Machine Learning (Recommendations)", "Payments", "User Acquisition", "Growth Hacking", "Tier 2/3 Markets"]
    },
    "Dream11": {
        "description": "An Indian fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics", "Curriculum Development", "User Experience", "Subscription Models"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "PolicyBazaar": {
        "description": "An Indian online insurance aggregator and financial services company.",
        "keywords": ["FinTech", "Insurance Tech (InsurTech)", "Online Aggregator", "Digital Marketing", "Lead Generation", "Data Analytics", "AI (Recommendations)", "Customer Service Tech", "Web Development", "Mobile App Development"]
    },
    "Nykaa": {
        "description": "An Indian e-commerce company for beauty, wellness, and fashion products.",
        "keywords": ["E-commerce", "Retail Tech", "Beauty & Fashion Tech", "Online Shopping", "Logistics", "Inventory Management", "Digital Marketing", "Personalization", "Mobile App Development", "Customer Experience (CX)"]
    },
    "Udaan": {
        "description": "An Indian B2B e-commerce platform for small and medium businesses.",
        "keywords": ["B2B E-commerce", "Supply Chain", "Logistics", "FinTech (Lending)", "Wholesale Trade", "Marketplace", "Data Analytics", "Mobile Platform", "Small Business Solutions", "Procurement"]
    },
    "BrowserStack": {
        "description": "A cloud web and mobile testing platform.",
        "keywords": ["Testing Automation", "Cloud Testing", "Browser Compatibility", "Mobile Testing", "SaaS", "DevOps Tools", "Continuous Integration/Continuous Delivery (CI/CD)", "Quality Assurance (QA)", "Selenium", "Appium"]
    },
    "Freshworks": {
        "description": "A global software company providing SaaS customer engagement solutions.",
        "keywords": ["SaaS", "CRM", "Help Desk Software", "Customer Service", "ITSM", "Sales Automation", "Marketing Automation", "AI Chatbots", "Customer Engagement", "Cloud Computing"]
    },
    "Druva": {
        "description": "A cloud data protection and management company.",
        "keywords": ["Cloud Data Protection", "Data Backup", "Disaster Recovery", "Data Governance", "Cybersecurity", "SaaS", "Cloud Computing", "Data Resilience", "Compliance", "Security Automation"]
    },
    "Postman": {
        "description": "A leading API development and testing platform.",
        "keywords": ["API Development", "API Testing", "Developer Tools", "Collaboration Tools", "API Management", "RESTful APIs", "GraphQL", "Microservices", "DevOps", "Software Development Lifecycle (SDLC)"]
    },
    "Amagi": {
        "description": "A global leader in cloud-based SaaS technology for broadcast and streaming TV.",
        "keywords": ["Cloud TV", "Broadcast Technology", "Streaming Media", "SaaS", "Video On Demand (VOD)", "Live Streaming", "Content Delivery Networks (CDN)", "Ad Insertion", "Media Technology", "AWS", "GCP"]
    },
    "Chargebee": {
        "description": "A subscription billing and revenue management platform for SaaS and subscription businesses.",
        "keywords": ["SaaS", "Subscription Management", "Billing Software", "Revenue Operations", "Payment Gateways", "FinTech", "Recurring Revenue", "Stripe", "Zuora", "Financial Analytics"]
    },
    "CleverTap": {
        "description": "A leading customer engagement and retention platform for mobile apps.",
        "keywords": ["Mobile Marketing", "Customer Engagement", "Retention Marketing", "Personalization", "Data Analytics", "AI (Marketing)", "Machine Learning", "Push Notifications", "In-App Messaging", "Customer Data Platform (CDP)"]
    },
    "Unacademy": {
        "description": "An Indian online education technology company.",
        "keywords": ["EdTech", "Online Learning", "Live Classes", "Test Preparation", "Content Creation", "Mobile App Development", "Data Analytics (Learning)", "Personalized Learning"]
    },
    "Vedantu": {
        "description": "An Indian online tutoring platform providing live interactive classes.",
        "keywords": ["EdTech", "Online Tutoring", "Live Classes", "Personalized Learning", "Mobile App Development", "Learning Management Systems (LMS)", "AI (Learning Analytics)", "Gamification"]
    },
    "Urban Company": {
        "description": "An Indian at-home services platform.",
        "keywords": ["On-demand Services", "Hyperlocal", "Mobile App Development", "Logistics", "Geolocation", "Service Marketplace", "User Experience (UX)", "Payment Systems"]
    },
    "MakeMyTrip": {
        "description": "An Indian online travel company providing travel services and products.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Holiday Packages", "Mobile App Development", "E-commerce", "Payment Gateways", "Recommendation Systems"]
    },
    "Bykea": { # Pakistani but similar market dynamics
        "description": "A Pakistani on-demand ride-hailing, logistics, and payments company.",
        "keywords": ["Ridesharing", "Logistics", "FinTech (Payments)", "On-demand Services", "Hyperlocal", "Mobile App Development", "Geolocation", "Last-Mile Delivery"]
    },
    # Global Companies - Other sectors
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce", "CRM", "Apex", "Lightning Web Components", "Cloud Computing", "SaaS", "Enterprise Software", "Customer Success", "Data Analytics", "Integration", "Platform Development"]
    },
    "Intuit": {
        "description": "A global technology platform that helps consumers and small businesses prosper with financial management solutions.",
        "keywords": ["FinTech", "Accounting Software (QuickBooks)", "Tax Software (TurboTax)", "Personal Finance (Mint)", "Small Business Solutions", "SaaS", "Data Analytics", "AI in Finance", "Cloud Accounting", "Payroll", "Payment Processing"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP", "CRM", "S/4HANA", "Cloud Computing", "Business Intelligence", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS"]
    },
    "Siemens AG": {
        "description": "A global technology powerhouse focusing on industry, infrastructure, transport, and healthcare.",
        "keywords": ["Industrial IoT", "Automation", "Digital Twin", "Smart Infrastructure", "Mobility Solutions", "Healthcare Technology", "Software Engineering (Industrial)", "AI in Manufacturing", "Edge Computing", "Cybersecurity (Industrial)"]
    },
    "GE Digital": {
        "description": "A subsidiary of General Electric, focusing on industrial IoT software and services.",
        "keywords": ["Industrial IoT", "Asset Performance Management (APM)", "Digital Twin", "Data Analytics (Industrial)", "Cloud Platforms", "Cybersecurity (OT/IT)", "Predictive Maintenance", "Operational Technology (OT)"]
    },
    "ABB": {
        "description": "A leading global technology company that energizes the transformation of society and industry to achieve a more productive, sustainable future.",
        "keywords": ["Industrial Automation", "Robotics", "Power Grids", "Electrification", "Motion Control", "IoT", "Digital Transformation (Industry)", "Control Systems", "Sustainable Technologies"]
    },
    "Honeywell": {
        "description": "A diversified technology and manufacturing company with segments in aerospace, building technologies, performance materials, and safety and productivity solutions.",
        "keywords": ["Industrial IoT", "Automation", "Aerospace Systems", "Building Management Systems", "Supply Chain Software", "Cybersecurity (Industrial)", "Control Systems", "Sensing Technologies", "Connected Solutions"]
    },
    "Schneider Electric": {
        "description": "A global specialist in energy management and automation.",
        "keywords": ["Energy Management", "Industrial Automation", "IoT", "Smart Buildings", "Data Center Solutions", "Renewable Energy", "Digital Transformation (Energy)", "Edge Computing", "Power Management", "Sustainability Tech"]
    },
    "Qualtrics": {
        "description": "An experience management company, helping organizations manage customer, employee, product, and brand experiences.",
        "keywords": ["Experience Management (XM)", "Customer Experience (CX)", "Employee Experience (EX)", "Survey Software", "Data Analytics", "Sentiment Analysis", "AI in CX", "Feedback Management", "SaaS"]
    },
    "ServiceNow": {
        "description": "An American software company that develops a cloud computing platform to help companies manage digital workflows for enterprise operations.",
        "keywords": ["ITSM", "HRSD", "CSM", "Workflow Automation", "Cloud Platform", "Enterprise Software", "SaaS", "Low-code/No-code", "Integration", "Digital Transformation", "Platform Development"]
    },
    "Workday": {
        "description": "An American on-demand (cloud-based) financial management and human capital management software vendor.",
        "keywords": ["HCM", "Financial Management", "SaaS", "Cloud Computing", "Enterprise Software", "Data Analytics", "HRIS", "Payroll", "Talent Management", "Reporting"]
    },
    "ZoomInfo": {
        "description": "A leading go-to-market intelligence platform for sales and marketing teams.",
        "keywords": ["Go-to-Market (GTM)", "Sales Intelligence", "Marketing Intelligence", "Lead Generation", "Data Analytics", "CRM Integration", "SaaS", "B2B Data", "Predictive Analytics"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management", "Work Management", "Collaboration Tools", "SaaS", "Agile Project Management", "Workflow Automation", "Task Management", "Team Productivity"]
    },
    "Atlassian": {
        "description": "A software company that develops products for software developers, project managers, and other software development teams.",
        "keywords": ["Jira", "Confluence", "Trello", "Bitbucket", "DevOps Tools", "Project Management", "Team Collaboration", "Agile Software Development", "SaaS", "Cloud Tools", "Enterprise Software"]
    },
    "HubSpot": {
        "description": "A developer and marketer of software products for inbound marketing, sales, and customer service.",
        "keywords": ["CRM", "Marketing Automation", "Sales Software", "Customer Service Software", "SaaS", "Inbound Marketing", "Content Management System (CMS)", "Website Builder", "Email Marketing", "Analytics"]
    },
    "Stripe": {
        "description": "A financial technology company offering payment processing software and APIs.",
        "keywords": ["FinTech", "Payment Gateway", "API", "Online Payments", "SaaS", "Billing", "Fraud Prevention", "Global Payments", "Developer Tools", "Financial Infrastructure"]
    },
    "Adyen": {
        "description": "A global payment company providing payment solutions for businesses.",
        "keywords": ["FinTech", "Payment Processing", "Online Payments", "Point-of-Sale (POS)", "Global Payments", "Fraud Prevention", "Payment Gateway", "API", "Merchant Services"]
    },
    "Fiserv": {
        "description": "A global provider of financial services technology solutions.",
        "keywords": ["FinTech", "Payment Processing", "Core Banking", "Digital Banking", "Financial Technology", "Enterprise Software", "Risk Management (Financial)", "Data Analytics (Financial)"]
    },
    "Fidelity National Information Services (FIS)": {
        "description": "A global leader in financial services technology, specializing in payment processing and banking solutions.",
        "keywords": ["FinTech", "Payment Processing", "Banking Technology", "Capital Markets Solutions", "Enterprise Payments", "Fraud & Risk Management", "Wealth Management Tech", "Blockchain (Financial)"]
    },
    "Illumina": {
        "description": "A company that develops, manufactures, and markets integrated systems for large-scale analysis of genetic variation and function.",
        "keywords": ["Bioinformatics", "Genomics", "Life Sciences", "Data Analysis (Genomics)", "Sequencing Technology", "Biotech", "Research & Development", "Machine Learning (Genetics)"]
    },
    "Moderna": {
        "description": "A biotechnology company focused on drug discovery, drug development, and vaccine technologies based on messenger RNA (mRNA).",
        "keywords": ["Biotechnology", "mRNA Technology", "Drug Discovery", "Vaccine Development", "Genomics", "Bioinformatics", "Clinical Trials", "Research & Development", "Life Sciences"]
    },
    "Guardant Health": {
        "description": "A precision oncology company focused on developing and commercializing proprietary blood tests for cancer.",
        "keywords": ["Biotech", "Healthcare Tech", "Precision Oncology", "Liquid Biopsy", "Genomics", "Data Analytics (Healthcare)", "Machine Learning (Diagnostics)", "Medical Devices", "Molecular Diagnostics"]
    },
    "Intuitive Surgical": {
        "description": "A company that develops, manufactures, and markets robotic products designed to improve clinical outcomes of patients through minimally invasive surgery.",
        "keywords": ["Robotics (Surgical)", "Medical Devices", "Healthcare Tech", "Minimally Invasive Surgery", "Computer Vision (Medical)", "Haptics", "AI in Healthcare", "Embedded Systems", "Hardware Engineering (Medical)"]
    },
    "GE Healthcare": {
        "description": "A leading global medical technology, pharmaceutical diagnostics, and digital solutions innovator.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "AI in Healthcare", "Data Analytics (Healthcare)", "Digital Health", "Precision Health", "Healthcare IT", "Patient Monitoring", "Diagnostic Equipment"]
    },
    "Siemens Healthineers": {
        "description": "A leading medical technology company and independent listed company of Siemens AG, offering products and services for diagnostic and therapeutic purposes.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "Laboratory Diagnostics", "AI in Healthcare", "Digital Health", "Precision Medicine", "Healthcare IT Solutions", "Therapeutic Devices", "Cybersecurity (Healthcare)"]
    },
    "Philips Healthcare": {
        "description": "A diversified technology company focused on improving people's health and well-being through meaningful innovation.",
        "keywords": ["Healthcare Technology", "Medical Devices", "Diagnostic Imaging", "Patient Monitoring", "Connected Care", "Personal Health", "AI in Healthcare", "Digital Health", "Software as a Medical Device (SaMD)"]
    },
    "TSMC (Taiwan Semiconductor Manufacturing Company)": {
        "description": "The world's largest dedicated independent (pure-play) semiconductor foundry.",
        "keywords": ["Semiconductors", "Chip Manufacturing", "Foundry Services", "Process Technology", "Microelectronics", "Wafer Fabrication", "Advanced Packaging", "R&D (Semiconductor)", "Supply Chain (Semiconductor)"]
    },
    "ASML Holding": {
        "description": "A Dutch multinational corporation specializing in the development and manufacturing of photolithography systems for the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Photolithography", "EUV Lithography", "Advanced Manufacturing", "Optics", "Precision Engineering", "Vacuum Technology", "Cleanroom Technology", "High-Tech Manufacturing"]
    },
    "Micron Technology": {
        "description": "An American producer of computer memory and computer data storage including DRAM, NAND flash, and NOR flash.",
        "keywords": ["Semiconductors", "Memory (DRAM, NAND)", "Flash Storage", "Solid State Drives (SSDs)", "Memory Controllers", "Chip Design", "Manufacturing (Memory)", "Data Storage Solutions"]
    },
    "Applied Materials": {
        "description": "A global leader in materials engineering solutions for the semiconductor, flat panel display, and solar photovoltaic industries.",
        "keywords": ["Semiconductor Equipment", "Materials Science", "Process Engineering", "Thin Film Deposition", "Etch Technology", "Ion Implantation", "Metrology", "Yield Management", "Manufacturing (Semiconductor)"]
    },
    "Lam Research": {
        "description": "A global supplier of wafer fabrication equipment and services to the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Wafer Fabrication", "Etch", "Deposition", "Process Control", "Materials Engineering", "Advanced Manufacturing", "R&D (Semiconductor)"]
    },
    "Amdocs": {
        "description": "A multinational corporation that specializes in software and services for communications, media, and financial services providers.",
        "keywords": ["Telecommunications Software", "BSS/OSS", "Digital Transformation (Telecom)", "CRM (Telecom)", "Billing Systems", "Customer Experience (Telecom)", "Cloud Native (Telecom)", "5G Solutions", "Network Management"]
    },
    "Ericsson": {
        "description": "A Swedish multinational networking and telecommunications company.",
        "keywords": ["Telecommunications", "5G Networks", "Mobile Networks", "Radio Access Networks (RAN)", "Network Infrastructure", "IoT Connectivity", "Managed Services", "Network Orchestration", "Cloud Native (Telecom)"]
    },
    "Nokia": {
        "description": "A Finnish multinational telecommunications, information technology, and consumer electronics company.",
        "keywords": ["Telecommunications", "5G Networks", "Network Infrastructure", "Fixed Networks", "Cloud & Network Services", "Optical Networks", "Cybersecurity (Telecom)", "IoT", "Private Wireless Networks"]
    },
    "ZTE Corporation": {
        "description": "A Chinese multinational telecommunications equipment and systems company.",
        "keywords": ["Telecommunications Equipment", "5G Networks", "Wireless Communication", "Optical Communication", "Core Network", "IoT Solutions", "Smart City Solutions", "Network Infrastructure"]
    },
    "SoftBank Group": {
        "description": "A Japanese multinational conglomerate holding company primarily focused on investment in technology, energy, and financial companies.",
        "keywords": ["Investment (Tech)", "Venture Capital", "Vision Fund", "AI Investment", "Telecommunications (SoftBank Corp.)", "ARM Holdings", "Robotics (Boston Dynamics)", "Disruptive Technologies"]
    },
    "Tencent": {
        "description": "A Chinese multinational technology and entertainment conglomerate holding company.",
        "keywords": ["Gaming (Tencent Games)", "Social Media (WeChat)", "FinTech (WeChat Pay)", "Cloud Computing (Tencent Cloud)", "AI", "Content Platforms", "Digital Entertainment", "E-commerce", "Online Advertising"]
    },
    "Alibaba Group": {
        "description": "A Chinese multinational technology company specializing in e-commerce, retail, Internet, and technology.",
        "keywords": ["E-commerce (Taobao, Tmall)", "FinTech (Ant Group, Alipay)", "Cloud Computing (Alibaba Cloud)", "Logistics (Cainiao)", "Digital Media & Entertainment", "AI", "Big Data", "Supply Chain", "Retail Tech"]
    },
    "ByteDance": {
        "description": "A Chinese internet technology company, best known for its video-sharing platform TikTok.",
        "keywords": ["Social Media", "Short-form Video (TikTok)", "Content Recommendation", "AI (Recommendation Algorithms)", "Machine Learning", "Natural Language Processing (NLP)", "Computer Vision", "Content Creation Tools", "AdTech", "Global Scale"]
    },
    "Baidu": {
        "description": "A Chinese multinational technology company specializing in internet-related services and products, and artificial intelligence.",
        "keywords": ["Search Engine", "AI", "Autonomous Driving (Apollo)", "Cloud Computing (Baidu AI Cloud)", "Natural Language Processing (NLP)", "Computer Vision", "Smart Devices", "Digital Assistant (DuerOS)", "Machine Learning", "Big Data"]
    },
    "SAP": {
        "description": "A German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
        "keywords": ["ERP", "CRM", "S/4HANA", "Cloud Computing", "Business Intelligence", "Supply Chain Management", "Procurement", "Financial Software", "ABAP", "Enterprise Solutions", "SaaS"]
    },
    "Siemens AG": {
        "description": "A global technology powerhouse focusing on industry, infrastructure, transport, and healthcare.",
        "keywords": ["Industrial IoT", "Automation", "Digital Twin", "Smart Infrastructure", "Mobility Solutions", "Healthcare Technology", "Software Engineering (Industrial)", "AI in Manufacturing", "Edge Computing", "Cybersecurity (Industrial)"]
    },
    "GE Digital": {
        "description": "A subsidiary of General Electric, focusing on industrial IoT software and services.",
        "keywords": ["Industrial IoT", "Asset Performance Management (APM)", "Digital Twin", "Data Analytics (Industrial)", "Cloud Platforms", "Cybersecurity (OT/IT)", "Predictive Maintenance", "Operational Technology (OT)"]
    },
    "ABB": {
        "description": "A leading global technology company that energizes the transformation of society and industry to achieve a more productive, sustainable future.",
        "keywords": ["Industrial Automation", "Robotics", "Power Grids", "Electrification", "Motion Control", "IoT", "Digital Transformation (Industry)", "Control Systems", "Sustainable Technologies"]
    },
    "Honeywell": {
        "description": "A diversified technology and manufacturing company with segments in aerospace, building technologies, performance materials, and safety and productivity solutions.",
        "keywords": ["Industrial IoT", "Automation", "Aerospace Systems", "Building Management Systems", "Supply Chain Software", "Cybersecurity (Industrial)", "Control Systems", "Sensing Technologies", "Connected Solutions"]
    },
    "Schneider Electric": {
        "description": "A global specialist in energy management and automation.",
        "keywords": ["Energy Management", "Industrial Automation", "IoT", "Smart Buildings", "Data Center Solutions", "Renewable Energy", "Digital Transformation (Energy)", "Edge Computing", "Power Management", "Sustainability Tech"]
    },
    "Qualtrics": {
        "description": "An experience management company, helping organizations manage customer, employee, product, and brand experiences.",
        "keywords": ["Experience Management (XM)", "Customer Experience (CX)", "Employee Experience (EX)", "Survey Software", "Data Analytics", "Sentiment Analysis", "AI in CX", "Feedback Management", "SaaS"]
    },
    "ZoomInfo": {
        "description": "A leading go-to-market intelligence platform for sales and marketing teams.",
        "keywords": ["Go-to-Market (GTM)", "Sales Intelligence", "Marketing Intelligence", "Lead Generation", "Data Analytics", "CRM Integration", "SaaS", "B2B Data", "Predictive Analytics"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management", "Work Management", "Collaboration Tools", "SaaS", "Agile Project Management", "Workflow Automation", "Task Management", "Team Productivity"]
    },
    "Atlassian": {
        "description": "A software company that develops products for software developers, project managers, and other software development teams.",
        "keywords": ["Jira", "Confluence", "Trello", "Bitbucket", "DevOps Tools", "Project Management", "Team Collaboration", "Agile Software Development", "SaaS", "Cloud Tools", "Enterprise Software"]
    },
    "HubSpot": {
        "description": "A developer and marketer of software products for inbound marketing, sales, and customer service.",
        "keywords": ["CRM", "Marketing Automation", "Sales Software", "Customer Service Software", "SaaS", "Inbound Marketing", "Content Management System (CMS)", "Website Builder", "Email Marketing", "Analytics"]
    },
    "Adyen": {
        "description": "A global payment company providing payment solutions for businesses.",
        "keywords": ["FinTech", "Payment Processing", "Online Payments", "Point-of-Sale (POS)", "Global Payments", "Fraud Prevention", "Payment Gateway", "API", "Merchant Services"]
    },
    "Fiserv": {
        "description": "A global provider of financial services technology solutions.",
        "keywords": ["FinTech", "Payment Processing", "Core Banking", "Digital Banking", "Financial Technology", "Enterprise Software", "Risk Management (Financial)", "Data Analytics (Financial)"]
    },
    "Fidelity National Information Services (FIS)": {
        "description": "A global leader in financial services technology, specializing in payment processing and banking solutions.",
        "keywords": ["FinTech", "Payment Processing", "Banking Technology", "Capital Markets Solutions", "Enterprise Payments", "Fraud & Risk Management", "Wealth Management Tech", "Blockchain (Financial)"]
    },
    "Illumina": {
        "description": "A company that develops, manufactures, and markets integrated systems for large-scale analysis of genetic variation and function.",
        "keywords": ["Bioinformatics", "Genomics", "Life Sciences", "Data Analysis (Genomics)", "Sequencing Technology", "Biotech", "Research & Development", "Machine Learning (Genetics)"]
    },
    "Moderna": {
        "description": "A biotechnology company focused on drug discovery, drug development, and vaccine technologies based on messenger RNA (mRNA).",
        "keywords": ["Biotechnology", "mRNA Technology", "Drug Discovery", "Vaccine Development", "Genomics", "Bioinformatics", "Clinical Trials", "Research & Development", "Life Sciences"]
    },
    "Guardant Health": {
        "description": "A precision oncology company focused on developing and commercializing proprietary blood tests for cancer.",
        "keywords": ["Biotech", "Healthcare Tech", "Precision Oncology", "Liquid Biopsy", "Genomics", "Data Analytics (Healthcare)", "Machine Learning (Diagnostics)", "Medical Devices", "Molecular Diagnostics"]
    },
    "Intuitive Surgical": {
        "description": "A company that develops, manufactures, and markets robotic products designed to improve clinical outcomes of patients through minimally invasive surgery.",
        "keywords": ["Robotics (Surgical)", "Medical Devices", "Healthcare Tech", "Minimally Invasive Surgery", "Computer Vision (Medical)", "Haptics", "AI in Healthcare", "Embedded Systems", "Hardware Engineering (Medical)"]
    },
    "GE Healthcare": {
        "description": "A leading global medical technology, pharmaceutical diagnostics, and digital solutions innovator.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "AI in Healthcare", "Data Analytics (Healthcare)", "Digital Health", "Precision Health", "Healthcare IT", "Patient Monitoring", "Diagnostic Equipment"]
    },
    "Siemens Healthineers": {
        "description": "A leading medical technology company and independent listed company of Siemens AG, offering products and services for diagnostic and therapeutic purposes.",
        "keywords": ["Healthcare Technology", "Medical Imaging", "Laboratory Diagnostics", "AI in Healthcare", "Digital Health", "Precision Medicine", "Healthcare IT Solutions", "Therapeutic Devices", "Cybersecurity (Healthcare)"]
    },
    "Philips Healthcare": {
        "description": "A diversified technology company focused on improving people's health and well-being through meaningful innovation.",
        "keywords": ["Healthcare Technology", "Medical Devices", "Diagnostic Imaging", "Patient Monitoring", "Connected Care", "Personal Health", "AI in Healthcare", "Digital Health", "Software as a Medical Device (SaMD)"]
    },
    "TSMC (Taiwan Semiconductor Manufacturing Company)": {
        "description": "The world's largest dedicated independent (pure-play) semiconductor foundry.",
        "keywords": ["Semiconductors", "Chip Manufacturing", "Foundry Services", "Process Technology", "Microelectronics", "Wafer Fabrication", "Advanced Packaging", "R&D (Semiconductor)", "Supply Chain (Semiconductor)"]
    },
    "ASML Holding": {
        "description": "A Dutch multinational corporation specializing in the development and manufacturing of photolithography systems for the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Photolithography", "EUV Lithography", "Advanced Manufacturing", "Optics", "Precision Engineering", "Vacuum Technology", "Cleanroom Technology", "High-Tech Manufacturing"]
    },
    "Micron Technology": {
        "description": "An American producer of computer memory and computer data storage including DRAM, NAND flash, and NOR flash.",
        "keywords": ["Semiconductors", "Memory (DRAM, NAND)", "Flash Storage", "Solid State Drives (SSDs)", "Memory Controllers", "Chip Design", "Manufacturing (Memory)", "Data Storage Solutions"]
    },
    "Applied Materials": {
        "description": "A global leader in materials engineering solutions for the semiconductor, flat panel display, and solar photovoltaic industries.",
        "keywords": ["Semiconductor Equipment", "Materials Science", "Process Engineering", "Thin Film Deposition", "Etch Technology", "Ion Implantation", "Metrology", "Yield Management", "Manufacturing (Semiconductor)"]
    },
    "Lam Research": {
        "description": "A global supplier of wafer fabrication equipment and services to the semiconductor industry.",
        "keywords": ["Semiconductor Equipment", "Wafer Fabrication", "Etch", "Deposition", "Process Control", "Materials Engineering", "Advanced Manufacturing", "R&D (Semiconductor)"]
    },
    "Amdocs": {
        "description": "A multinational corporation that specializes in software and services for communications, media, and financial services providers.",
        "keywords": ["Telecommunications Software", "BSS/OSS", "Digital Transformation (Telecom)", "CRM (Telecom)", "Billing Systems", "Customer Experience (Telecom)", "Cloud Native (Telecom)", "5G Solutions", "Network Management"]
    },
    "Ericsson": {
        "description": "A Swedish multinational networking and telecommunications company.",
        "keywords": ["Telecommunications", "5G Networks", "Mobile Networks", "Radio Access Networks (RAN)", "Network Infrastructure", "IoT Connectivity", "Managed Services", "Network Orchestration", "Cloud Native (Telecom)"]
    },
    "Nokia": {
        "description": "A Finnish multinational telecommunications, information technology, and consumer electronics company.",
        "keywords": ["Telecommunications", "5G Networks", "Network Infrastructure", "Fixed Networks", "Cloud & Network Services", "Optical Networks", "Cybersecurity (Telecom)", "IoT", "Private Wireless Networks"]
    },
    "ZTE Corporation": {
        "description": "A Chinese multinational telecommunications equipment and systems company.",
        "keywords": ["Telecommunications Equipment", "5G Networks", "Wireless Communication", "Optical Communication", "Core Network", "IoT Solutions", "Smart City Solutions", "Network Infrastructure"]
    },
    "SoftBank Group": {
        "description": "A Japanese multinational conglomerate holding company primarily focused on investment in technology, energy, and financial companies.",
        "keywords": ["Investment (Tech)", "Venture Capital", "Vision Fund", "AI Investment", "Telecommunications (SoftBank Corp.)", "ARM Holdings", "Robotics (Boston Dynamics)", "Disruptive Technologies"]
    },
    "Tencent": {
        "description": "A Chinese multinational technology and entertainment conglomerate holding company.",
        "keywords": ["Gaming (Tencent Games)", "Social Media (WeChat)", "FinTech (WeChat Pay)", "Cloud Computing (Tencent Cloud)", "AI", "Content Platforms", "Digital Entertainment", "E-commerce", "Online Advertising"]
    },
    "Alibaba Group": {
        "description": "A Chinese multinational technology company specializing in e-commerce, retail, Internet, and technology.",
        "keywords": ["E-commerce (Taobao, Tmall)", "FinTech (Ant Group, Alipay)", "Cloud Computing (Alibaba Cloud)", "Logistics (Cainiao)", "Digital Media & Entertainment", "AI", "Big Data", "Supply Chain", "Retail Tech"]
    },
    "ByteDance": {
        "description": "A Chinese internet technology company, best known for its video-sharing platform TikTok.",
        "keywords": ["Social Media", "Short-form Video (TikTok)", "Content Recommendation", "AI (Recommendation Algorithms)", "Machine Learning", "Natural Language Processing (NLP)", "Computer Vision", "Content Creation Tools", "AdTech", "Global Scale"]
    },
    "Baidu": {
        "description": "A Chinese multinational technology company specializing in internet-related services and products, and artificial intelligence.",
        "keywords": ["Search Engine", "AI", "Autonomous Driving (Apollo)", "Cloud Computing (Baidu AI Cloud)", "Natural Language Processing (NLP)", "Computer Vision", "Smart Devices", "Digital Assistant (DuerOS)", "Machine Learning", "Big Data"]
    },
    # More Indian Tech Companies (Established & Emerging)
    "Zerodha": {
        "description": "India's largest retail stockbroker, offering a flat-fee brokerage model.",
        "keywords": ["FinTech", "Stock Trading", "Investment Platform", "Brokerage", "Mobile App Development", "Data Analytics (Finance)", "Algorithmic Trading", "Frontend Development", "Backend Development", "Scalability", "Security (Financial)"]
    },
    "Groww": {
        "description": "An Indian online investment platform for mutual funds and stocks.",
        "keywords": ["FinTech", "Investment Platform", "Mutual Funds", "Stock Trading", "User Experience (UX)", "Mobile App Development", "Data Analytics", "Personal Finance", "Wealth Management"]
    },
    "ShareChat": {
        "description": "An Indian social media and short video platform available in multiple Indian languages.",
        "keywords": ["Social Media", "Short-form Video", "Content Recommendation", "AI (Content)", "Machine Learning", "Natural Language Processing (NLP)", "Mobile App Development", "Vernacular Content", "User Engagement", "AdTech"]
    },
    "Dailyhunt": {
        "description": "An Indian content and news aggregator platform, providing local language content.",
        "keywords": ["Content Aggregation", "News Platform", "Local Language Content", "AI (Content Recommendation)", "Natural Language Processing (NLP)", "Mobile App Development", "AdTech", "User Engagement", "Big Data"]
    },
    "Dreamplug (formerly CRED's parent company)": {
        "description": "Parent company of CRED, focusing on financial technology and consumer products.",
        "keywords": ["FinTech", "Consumer Tech", "Financial Products", "Digital Payments", "Data Analytics", "Product Management", "Mobile Development", "Strategy", "User Experience (UX)"]
    },
    "Pine Labs": {
        "description": "An Indian merchant commerce platform providing payment solutions and financial services.",
        "keywords": ["FinTech", "Payment Solutions", "POS Systems", "Merchant Services", "Digital Payments", "Installment Payments", "Credit", "SME Solutions", "API Integration", "Cloud Payments"]
    },
    "IndusInd Bank": {
        "description": "A leading private sector bank in India, focusing on digital banking initiatives.",
        "keywords": ["FinTech", "Digital Banking", "Core Banking Systems", "Mobile Banking", "Cybersecurity (Banking)", "Data Analytics (Financial)", "Risk Management", "Blockchain (Financial Services)", "Retail Banking", "Corporate Banking"]
    },
    "HDFC Bank": {
        "description": "India's largest private sector bank, rapidly adopting digital technologies.",
        "keywords": ["FinTech", "Digital Banking", "Mobile Banking", "Core Banking", "Payments", "Cybersecurity (Banking)", "Data Analytics (Financial)", "AI in Banking", "Fraud Detection", "Risk Management"]
    },
    "ICICI Bank": {
        "description": "A major Indian multinational banking and financial services company, leveraging technology for customer experience.",
        "keywords": ["FinTech", "Digital Banking", "Mobile Banking", "Payments", "AI in Banking", "Blockchain (Financial)", "Cybersecurity (Banking)", "Data Analytics", "Customer Experience", "Retail Banking", "Corporate Banking"]
    },
    "Airtel Digital": {
        "description": "The digital arm of Bharti Airtel, focusing on digital services and products.",
        "keywords": ["Digital Services", "Telecommunications", "Mobile Payments (Airtel Payments Bank)", "Content Streaming (Airtel Xstream)", "AdTech", "Gaming", "Cybersecurity", "Cloud Services", "Data Analytics", "5G applications"]
    },
    "Nazara Technologies": {
        "description": "An Indian gaming and sports media company.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "OYO Rooms": {
        "description": "An Indian multinational hospitality chain of leased and franchised hotels, homes, and living spaces.",
        "keywords": ["Hospitality Tech", "Travel Tech", "Platform Development", "Supply Chain (Hospitality)", "Revenue Management", "Mobile App Development", "User Experience (UX)", "Data Analytics", "Hyperlocal"]
    },
    "MakeMyTrip": {
        "description": "An Indian online travel company providing travel services and products.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Holiday Packages", "Mobile App Development", "E-commerce", "Payment Gateways", "Recommendation Systems"]
    },
    "EaseMyTrip": {
        "description": "An Indian online travel company offering flight, hotel, and holiday bookings.",
        "keywords": ["Travel Tech", "Online Travel Agency (OTA)", "Flight Booking", "Hotel Booking", "Bus Booking", "Rail Booking", "E-commerce", "Payment Gateways", "User Experience (UX)"]
    },
    "CarDekho": {
        "description": "An Indian automotive platform providing information and services related to new and used cars.",
        "keywords": ["Automotive Tech", "Online Marketplace (Cars)", "Digital Marketing", "Lead Generation", "Data Analytics (Automotive)", "AI (Pricing)", "Customer Experience", "Mobile App Development"]
    },
    "Spinny": {
        "description": "An Indian used car retailing platform focusing on transparency and quality.",
        "keywords": ["Automotive Tech", "Used Car Market", "E-commerce", "Logistics (Automotive)", "Quality Assurance", "Data Analytics", "Customer Experience", "Blockchain (Supply Chain)"]
    },
    "PharmEasy": {
        "description": "An Indian online pharmacy and healthcare aggregator.",
        "keywords": ["HealthTech", "E-pharmacy", "Online Diagnostics", "Telemedicine", "Supply Chain (Pharma)", "Logistics", "Mobile App Development", "Data Analytics (Healthcare)", "Personalized Healthcare"]
    },
    "Apollo Hospitals": {
        "description": "One of India's largest healthcare groups, also venturing into digital health.",
        "keywords": ["HealthTech", "Hospital Management Systems (HMS)", "Telemedicine", "Digital Health Records (EHR)", "AI in Healthcare", "Medical Imaging", "Data Analytics (Clinical)", "Patient Engagement Platforms", "IoT (Medical Devices)"]
    },
    "Max Healthcare": {
        "description": "A leading chain of hospitals in India, adopting digital transformation in healthcare delivery.",
        "keywords": ["HealthTech", "Hospital Information Systems (HIS)", "Digital Health", "Teleconsultation", "AI in Diagnostics", "Data Analytics (Healthcare Operations)", "Patient Portals", "Medical IoT"]
    },
    "Innovaccer": {
        "description": "A healthcare technology company unifying patient data and providing actionable insights.",
        "keywords": ["HealthTech", "Data Platform (Healthcare)", "Population Health Management", "AI in Healthcare", "Machine Learning (Clinical)", "Interoperability", "Data Governance (Healthcare)", "Value-Based Care", "Cloud Computing"]
    },
    "Practo": {
        "description": "An Indian healthcare technology company connecting patients with doctors and clinics online.",
        "keywords": ["HealthTech", "Telemedicine", "Online Doctor Consultation", "Appointment Booking", "EHR (Electronic Health Records)", "Practice Management Software", "Mobile App Development", "Data Analytics (Healthcare)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "BharatPe": {
        "description": "An Indian FinTech company offering QR code-based payment solutions and financial services to merchants.",
        "keywords": ["FinTech", "Digital Payments", "QR Code Payments", "Merchant Solutions", "SME Lending", "UPI", "Data Analytics (Merchant)", "Fraud Detection", "Mobile App Development"]
    },
    "Open Financial Technologies": {
        "description": "Asia's first neo-banking platform for SMEs and startups.",
        "keywords": ["FinTech", "Neo-banking", "SME Banking", "Payments API", "Expense Management", "Payroll Automation", "Cloud Banking", "API Integrations", "Cybersecurity (FinTech)", "Financial Automation"]
    },
    "Jupiter Money": {
        "description": "An Indian neo-banking platform providing a digital-first banking experience.",
        "keywords": ["FinTech", "Neo-banking", "Digital Banking", "Mobile Banking", "Personal Finance", "Wealth Management", "Payments", "User Experience (UX)", "Data Analytics"]
    },
    "CoinDCX": {
        "description": "An Indian cryptocurrency exchange and crypto investment platform.",
        "keywords": ["FinTech", "Cryptocurrency", "Blockchain", "Crypto Exchange", "Decentralized Finance (DeFi)", "Trading Platforms", "Cybersecurity (Crypto)", "Risk Management", "Backend Development", "Scalability"]
    },
    "CoinSwitch Kuber": {
        "description": "An Indian cryptocurrency exchange platform for simplified crypto investments.",
        "keywords": ["FinTech", "Cryptocurrency", "Blockchain", "Crypto Investment", "Mobile App Development", "User Experience (UX)", "Security (Crypto)", "Data Analytics", "Trading Algorithms"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Infibeam Avenues": {
        "description": "An Indian e-commerce and payment solutions company.",
        "keywords": ["E-commerce Platform", "Payment Gateway (CCAvenue)", "FinTech", "Online Retail Solutions", "Digital Payments", "White-label Solutions", "Cloud Computing"]
    },
    "MapmyIndia (CE Info Systems)": {
        "description": "An Indian company specializing in digital maps, geospatial software, and location-based IoT technologies.",
        "keywords": ["Mapping Technology", "GIS (Geographic Information Systems)", "Location-based Services", "IoT", "Navigation Systems", "GPS", "Data Analytics (Geospatial)", "Autonomous Vehicles (Mapping)", "Smart Cities"]
    },
    "Happiest Minds Technologies": {
        "description": "An Indian IT services company focusing on digital transformation, cloud, and cybersecurity.",
        "keywords": ["Digital Transformation", "Cloud Services", "Cybersecurity", "IoT", "AI & Analytics", "Product Engineering", "Infrastructure Management", "Automation", "DevOps", "Agile", "Enterprise Solutions"]
    },
    "Coforge": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    "Mindtree (now LTIMindtree)": {
        "description": "A global technology consulting and services company, now part of LTIMindtree.",
        "keywords": ["Digital Transformation", "Cloud Solutions", "Data & AI", "Enterprise Applications", "Product Engineering", "Customer Experience (CX)", "Agile Development", "DevOps", "IoT", "Managed Services"]
    },
    "Genpact": {
        "description": "A global professional services firm focused on delivering digital transformation and business process management.",
        "keywords": ["Digital Transformation", "Business Process Management (BPM)", "AI & Automation", "Data Analytics", "Financial Services Operations", "Supply Chain Management", "Risk & Compliance", "Robotics Process Automation (RPA)", "Consulting"]
    },
    "EXL Service": {
        "description": "A global analytics and digital operations and solutions company.",
        "keywords": ["Data Analytics", "AI", "Machine Learning", "Digital Operations", "Business Process Outsourcing (BPO)", "Risk Management", "Customer Experience (CX)", "Healthcare Analytics", "Insurance Analytics", "Financial Services Analytics"]
    },
    "WNS (Holdings)": {
        "description": "A global business process management (BPM) company.",
        "keywords": ["Business Process Management (BPM)", "Digital Transformation", "Automation", "Analytics", "Customer Experience (CX)", "Travel BPM", "Healthcare BPM", "Finance & Accounting BPM", "Robotics Process Automation (RPA)"]
    },
    "KPIT Technologies": {
        "description": "An Indian multinational corporation that provides software to the automotive industry.",
        "keywords": ["Automotive Software", "Autonomous Driving", "Electric Vehicles (EV)", "Connected Cars", "Infotainment Systems", "Embedded Systems", "Software-Defined Vehicles (SDV)", "AI (Automotive)", "ADAS (Advanced Driver-Assistance Systems)", "Vehicle Diagnostics"]
    },
    "Tata Motors": {
        "description": "An Indian multinational automotive manufacturing company, increasingly focused on electric vehicles and connected car technologies.",
        "keywords": ["Automotive Manufacturing", "Electric Vehicles (EV)", "Connected Car Technology", "ADAS", "Software Engineering (Automotive)", "Battery Management Systems (BMS)", "Infotainment", "IoT (Automotive)", "Supply Chain (Automotive)"]
    },
    "Mahindra & Mahindra": {
        "description": "An Indian multinational automotive manufacturing corporation, with a focus on SUVs, commercial vehicles, and electric mobility.",
        "keywords": ["Automotive Manufacturing", "Electric Vehicles (EV)", "Farm Equipment (Tech)", "Connected Vehicles", "ADAS", "Software Engineering (Automotive)", "IoT (Automotive)", "Sustainable Mobility"]
    },
    "Bajaj Auto": {
        "description": "An Indian multinational two-wheeler and three-wheeler manufacturing company, exploring electric and smart mobility solutions.",
        "keywords": ["Automotive Manufacturing", "Electric Two/Three Wheelers", "Connected Mobility", "IoT (Vehicles)", "Powertrain Technology", "Software Engineering (Embedded)"]
    },
    "Ather Energy": {
        "description": "An Indian electric scooter manufacturer and charging infrastructure provider.",
        "keywords": ["Electric Vehicles (EV)", "Electric Scooters", "Battery Technology", "IoT (Connected Vehicles)", "Charging Infrastructure", "Mobile App Development (EV)", "Embedded Systems", "Hardware Engineering (EV)"]
    },
    "Rebel Foods": {
        "description": "An Indian online restaurant company, operating multiple cloud kitchen brands.",
        "keywords": ["Cloud Kitchen", "Food Tech", "Restaurant Tech", "Logistics", "Supply Chain (Food)", "Data Analytics (Food Delivery)", "AI (Demand Forecasting)", "Brand Management", "Ghost Kitchens"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Zomato": {
        "description": "An Indian multinational restaurant aggregator and food delivery company.",
        "keywords": ["Food Delivery", "Restaurant Technology", "Logistics", "Mobile Development", "Data Analytics", "Machine Learning (Recommendation Systems)", "Cloud Infrastructure", "Geolocation", "Payment Gateways", "User Experience (UX)", "Growth Hacking"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Urban Company": {
        "description": "An Indian at-home services platform.",
        "keywords": ["On-demand Services", "Hyperlocal", "Mobile App Development", "Logistics", "Geolocation", "Service Marketplace", "User Experience (UX)", "Payment Systems"]
    },
    "Vedantu": {
        "description": "An Indian online tutoring platform providing live interactive classes.",
        "keywords": ["EdTech", "Online Tutoring", "Live Classes", "Personalized Learning", "Mobile App Development", "Learning Management Systems (LMS)", "AI (Learning Analytics)", "Gamification"]
    },
    "Unacademy": {
        "description": "An Indian online education technology company.",
        "keywords": ["EdTech", "Online Learning", "Live Classes", "Test Preparation", "Content Creation", "Mobile App Development", "Data Analytics (Learning)", "Personalized Learning"]
    },
    "Toppr (Byju's Group)": {
        "description": "An Indian online learning platform for K-12 and competitive exams.",
        "keywords": ["EdTech", "Online Learning", "Test Preparation", "Content Creation", "Adaptive Learning", "AI (Personalized Study)", "Mobile App Development", "Gamification"]
    },
    "BYJU'S": {
        "description": "An Indian multinational educational technology company, providing online tutoring and learning programs.",
        "keywords": ["EdTech", "Online Learning", "Content Creation (Video, Animation)", "Mobile App Development", "AI (Personalized Learning)", "Machine Learning", "Data Analytics (Student Progress)", "Curriculum Development", "User Experience", "Subscription Models"]
    },
    "UpGrad": {
        "description": "An Indian online higher education company providing online programs.",
        "keywords": ["EdTech", "Online Higher Education", "Skill Development", "Career Services", "Content Curation", "Learning Management Systems (LMS)", "Data Analytics (Career Outcomes)", "Industry Partnerships"]
    },
    "Great Learning": {
        "description": "An Indian ed-tech company providing online professional and higher education programs.",
        "keywords": ["EdTech", "Professional Education", "Upskilling", "Data Science Courses", "AI Courses", "Cloud Computing Courses", "Career Development", "Online Learning Platform"]
    },
    "Druva": {
        "description": "A cloud data protection and management company.",
        "keywords": ["Cloud Data Protection", "Data Backup", "Disaster Recovery", "Data Governance", "Cybersecurity", "SaaS", "Cloud Computing", "Data Resilience", "Compliance", "Security Automation"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "Mobikwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": { # Duplicate with slightly different description for clarity if needed
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Zetwerk": {
        "description": "An Indian B2B marketplace for manufacturing goods.",
        "keywords": ["B2B Marketplace", "Manufacturing Tech", "Supply Chain", "Procurement", "Digital Manufacturing", "IoT (Manufacturing)", "Quality Control", "Logistics", "Cloud Platform"]
    },
    "Infra.Market": {
        "description": "An Indian B2B marketplace for construction materials.",
        "keywords": ["B2B Marketplace", "Construction Tech", "Supply Chain", "Logistics", "Procurement", "FinTech (Construction Finance)", "Digital Platform"]
    },
    "OfBusiness": {
        "description": "An Indian B2B e-commerce and FinTech platform providing raw materials and credit to SMEs.",
        "keywords": ["B2B E-commerce", "FinTech (SME Lending)", "Supply Chain", "Procurement", "Data Analytics (B2B)", "Credit Risk Assessment", "Logistics", "Marketplace", "Enterprise Software"]
    },
    "Capillary Technologies": {
        "description": "A leading provider of AI-powered loyalty and customer engagement solutions for retailers.",
        "keywords": ["Retail Tech", "Customer Engagement", "Loyalty Programs", "Personalization", "AI (Retail)", "Machine Learning (Retail)", "Data Analytics (Retail)", "CRM", "Omnichannel Marketing"]
    },
    "RateGain": {
        "description": "A global provider of SaaS solutions for the travel and hospitality industry.",
        "keywords": ["Travel Tech", "Hospitality Tech", "SaaS", "Revenue Management", "Pricing Optimization", "Data Analytics (Travel)", "AI (Pricing)", "Distribution Channels", "API Integration"]
    },
    "Sigmoid": {
        "description": "A leading data engineering and AI consulting company.",
        "keywords": ["Data Engineering", "Big Data", "Data Analytics", "Cloud Data Platforms", "AI Consulting", "Machine Learning Engineering", "Data Warehousing", "Data Lakes", "ETL", "AWS", "GCP", "Azure"]
    },
    "Analytics Vidhya": {
        "description": "A leading global community and knowledge portal for analytics and data science professionals.",
        "keywords": ["Data Science", "Machine Learning", "Deep Learning", "AI", "Python", "R", "SQL", "Big Data Technologies", "Data Visualization", "Natural Language Processing (NLP)", "Computer Vision", "Statistical Modeling", "Data Analytics Training"]
    },
    "Indegene": {
        "description": "A global healthcare solutions company providing commercialization and marketing services for life sciences.",
        "keywords": ["HealthTech", "Life Sciences", "Digital Marketing (Pharma)", "Medical Communications", "Data Analytics (Healthcare)", "AI (Commercialization)", "CRM (Pharma)", "Omnichannel Engagement"]
    },
    "Netcore Cloud": {
        "description": "A full-stack marketing technology company providing AI-powered solutions for customer engagement.",
        "keywords": ["Marketing Automation", "Customer Engagement", "Personalization", "AI (Marketing)", "Machine Learning", "Email Marketing", "Push Notifications", "Customer Data Platform (CDP)", "Analytics"]
    },
    "Manthan": {
        "description": "A global leader in AI-powered analytics solutions for retail and consumer businesses.",
        "keywords": ["Retail Analytics", "Consumer Analytics", "AI (Retail)", "Machine Learning (Retail)", "Big Data", "Personalization", "Merchandising Analytics", "Customer Analytics", "Supply Chain Analytics"]
    },
    "Happay": {
        "description": "An Indian FinTech company offering expense management and corporate card solutions.",
        "keywords": ["FinTech", "Expense Management", "Corporate Cards", "Payment Solutions", "SaaS", "Financial Automation", "Mobile App Development", "Data Analytics (Expenses)"]
    },
    "Juspay": {
        "description": "An Indian payments technology company providing full-stack payment solutions.",
        "keywords": ["FinTech", "Payment Gateway", "UPI", "Payment Orchestration", "Mobile Payments", "Fraud Prevention", "Security (Payments)", "API Development", "Scalability"]
    },
    "BillDesk (now part of Prosus' PayU)": {
        "description": "An Indian online payment gateway company.",
        "keywords": ["FinTech", "Payment Gateway", "Online Payments", "Billing Solutions", "Payment Processing", "Digital Payments", "Security (Payments)"]
    },
    "MobiKwik": {
        "description": "An Indian FinTech company offering mobile wallet, payments, and financial services, with a focus on lending and insurance.",
        "keywords": ["FinTech", "Mobile Wallet", "Digital Payments", "UPI", "Lending", "Insurance Tech", "Investment Tech", "E-commerce Payments", "Cybersecurity"]
    },
    "Nazara Technologies": {
        "description": "An Indian diversified gaming and sports media platform.",
        "keywords": ["Gaming Tech", "Mobile Gaming", "Esports", "Advergaming", "Subscription Gaming", "Game Development", "User Engagement", "Data Analytics (Gaming)", "Fantasy Sports"]
    },
    "Games24x7": {
        "description": "An Indian online skill gaming company operating platforms like RummyCircle and My11Circle.",
        "keywords": ["Gaming Tech", "Skill Gaming", "Fantasy Sports", "Rummy", "Poker", "Real-time Systems", "Fraud Detection", "Data Analytics (Gaming)", "Mobile Gaming", "User Acquisition"]
    },
    "Dream11": {
        "description": "India's largest fantasy sports platform.",
        "keywords": ["Gaming Tech", "Fantasy Sports", "Mobile Gaming", "Data Analytics", "User Engagement", "Real-time Systems", "Scalability", "Backend Development", "Payments Integration", "Sports Analytics"]
    },
    "Myntra": {
        "description": "An Indian fashion e-commerce company, a subsidiary of Flipkart.",
        "keywords": ["E-commerce (Fashion)", "Online Retail", "Supply Chain (Fashion)", "Logistics", "Digital Marketing", "Personalization", "AI (Fashion Recommendations)", "Mobile App Development", "User Experience (UX)"]
    },
    "Lenskart": {
        "description": "An Indian optical prescription eyewear retail chain, integrating online and offline experiences.",
        "keywords": ["Retail Tech", "E-commerce", "Omnichannel Retail", "Computer Vision (Eyewear Try-on)", "Supply Chain (Retail)", "Manufacturing (Eyewear)", "Customer Experience (CX)", "Mobile App Development"]
    },
    "Pepperfry": {
        "description": "An Indian online furniture and home goods marketplace.",
        "keywords": ["E-commerce (Furniture)", "Home Decor Tech", "Supply Chain", "Logistics", "Online Marketplace", "Digital Marketing", "3D Visualization", "Augmented Reality (AR) in Retail"]
    },
    "BigBasket": {
        "description": "An Indian online grocery delivery service, part of the Tata Group.",
        "keywords": ["E-grocery", "E-commerce", "Logistics (Grocery)", "Supply Chain Optimization", "Last-Mile Delivery", "Data Analytics (Retail)", "Inventory Management", "Mobile App Development", "Hyperlocal"]
    },
    "Dunzo": {
        "description": "An Indian hyperlocal delivery service that delivers anything locally.",
        "keywords": ["Hyperlocal Delivery", "Quick Commerce", "Logistics", "On-demand Services", "Mobile App Development", "Geolocation", "Route Optimization", "User Experience (UX)"]
    },
    "Delhivery": {
        "description": "An Indian logistics and supply chain services company.",
        "keywords": ["Logistics", "Supply Chain Management", "Warehousing", "Last-Mile Delivery", "E-commerce Logistics", "Route Optimization", "Fleet Management", "Data Analytics", "Automation (Warehouse)", "IoT (Tracking)", "GIS", "Machine Learning (Forecasting)"]
    },
    "Blue Dart Express": {
        "description": "India's premier express air and integrated transportation and distribution company.",
        "keywords": ["Logistics", "Express Delivery", "Supply Chain", "Warehousing", "Air Cargo", "Tracking Systems", "Route Optimization", "Customs Clearance", "Automation (Logistics)"]
    },
    "Shiprocket": {
        "description": "An Indian logistics software solution for e-commerce businesses.",
        "keywords": ["Logistics Tech", "E-commerce Logistics", "Shipping Software", "Order Fulfillment", "Carrier Integration", "Tracking & Analytics", "SME Solutions", "API (Logistics)"]
    },
    "Vistara": {
        "description": "An Indian airline, a joint venture between Tata Sons and Singapore Airlines, focusing on premium air travel.",
        "keywords": ["Airline Technology", "Travel Tech", "Flight Operations", "Customer Experience (Airline)", "Reservations Systems", "Loyalty Programs", "Digital Transformation (Airline)", "Mobile App Development"]
    },
    "IndiGo": {
        "description": "India's largest airline by passengers carried and fleet size, known for its low-cost model.",
        "keywords": ["Airline Technology", "Flight Operations", "Revenue Management", "Fleet Management", "Digital Transformation (Airline)", "Mobile App Development", "E-ticketing", "Customer Experience"]
    },
    "IRCTC": {
        "description": "Indian Railway Catering and Tourism Corporation, managing catering, tourism, and online ticketing operations for Indian Railways.",
        "keywords": ["E-ticketing", "Railway Systems", "Online Reservations", "Payment Gateways", "Logistics (Catering)", "Tourism Tech", "Mobile App Development", "Scalability (High Traffic)"]
    },
    "Tata Digital": {
        "description": "The digital arm of Tata Group, building a super app and digital ecosystem.",
        "keywords": ["Super App", "Digital Ecosystem", "E-commerce (Tata Neu)", "FinTech", "HealthTech", "EdTech", "Loyalty Programs", "Data Analytics", "AI (Cross-platform)", "User Experience (UX)"]
    },
    "JioMart": {
        "description": "Reliance Retail's online grocery and e-commerce platform.",
        "keywords": ["E-commerce (Grocery)", "Omnichannel Retail", "Logistics", "Supply Chain", "Hyperlocal", "Digital Payments", "Customer Experience", "Mobile App Development"]
    },
    "FreshToHome": {
        "description": "An Indian e-commerce platform for fresh fish and meat.",
        "keywords": ["E-commerce (Perishables)", "Supply Chain (Fresh Food)", "Logistics", "Cold Chain Management", "Mobile App Development", "Data Analytics (Supply/Demand)", "Quality Control"]
    }
}
# Convert all company keywords to lowercase for consistent matching
for company_data in COMPANY_SKILL_PROFILES.values():
    company_data["keywords"] = [kw.lower() for kw in company_data["keywords"]]

# IMPORTANT: REPLACE THESE WITH YOUR ACTUAL DEPLOYMENT URLs
APP_BASE_URL = "https://candidate-screeneerpro.streamlit.app/" # <--- UPDATED URL
# This URL should be where your generated HTML certificates are publicly accessible.
# For this implementation, the PDF is generated on-the-fly for download/email, so this URL is less critical for email attachment.
CERTIFICATE_HOSTING_URL = "https://candidate-screeneerpro.streamlit.app/certificate_verify" # <--- UPDATED URL

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
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}" # Corrected API key interpolation

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
            model = SentenceTransformer("all-MiniLM-L6-v2")
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
    "https", "http", "contactinfo", "connect", "reference", "references","fees","Gurgaon, Haryana"
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
    match = EMAIL_PATTERN.search(text) # Use pre-compiled pattern
    return match.group(0) if match else None

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

# --- NEW: Function to generate Company Fit Assessment ---
@st.cache_data(show_spinner="Generating Company Fit Assessment...")
def generate_company_fit_assessment(candidate_name, company_name, resume_embedding, company_profile_embedding, resume_skills_set, company_keywords):
    """
    Generates an assessment of how well the resume fits a target company.
    """
    if not company_name or company_name.strip() == "":
        return "Please enter a target company name to get a company fit assessment."
    
    company_name_lower = company_name.lower()
    if company_name_lower not in [k.lower() for k in COMPANY_SKILL_PROFILES.keys()]:
        return f"Company '{company_name}' not found in our predefined profiles. Please try one of the examples (e.g., Google, Microsoft, Amazon, Generic Tech Startup, IBM, Oracle, SAP, Cisco, Adobe, NVIDIA)."

    # Calculate semantic similarity
    semantic_similarity = cosine_similarity(resume_embedding.reshape(1, -1), company_profile_embedding.reshape(1, -1))[0][0]
    semantic_similarity = float(np.clip(semantic_similarity, 0, 1))

    # Calculate keyword overlap score
    matched_company_keywords = resume_skills_set.intersection(set(company_keywords))
    
    company_fit_score = 0
    if len(company_keywords) > 0:
        keyword_overlap_percentage = (len(matched_company_keywords) / len(company_keywords)) * 100
        # Blend semantic similarity with keyword overlap
        company_fit_score = (semantic_similarity * 60) + (keyword_overlap_percentage * 0.4)
        company_fit_score = np.clip(company_fit_score, 0, 100) # Ensure score is between 0 and 100
    else:
        # If no keywords for company, rely more on semantic similarity
        company_fit_score = semantic_similarity * 100

    assessment = []
    assessment.append(f"### Company Fit Assessment for {company_name}")
    assessment.append(f"**Company Fit Score:** {company_fit_score:.2f}%")
    assessment.append(f"**Semantic Alignment with Company Profile:** {semantic_similarity:.2f}")

    if company_fit_score >= 80:
        assessment.append(f"**Overall Fit:** **Excellent!** {candidate_name}'s profile shows a very strong alignment with {company_name}'s typical technical and cultural landscape.")
        assessment.append(f"**Strengths:** Your resume semantically resonates well with {company_name}'s focus areas. You possess a significant number of skills highly relevant to {company_name}'s operations.")
        if matched_company_keywords:
            assessment.append(f"**Key Matching Keywords:** {', '.join(sorted(list(matched_company_keywords)))}")
        assessment.append("This indicates you are likely to be a highly valuable asset and integrate quickly into their environment.")
    elif company_fit_score >= 60:
        assessment.append(f"**Overall Fit:** **Good.** {candidate_name}'s resume shows a good general alignment with {company_name}.")
        assessment.append(f"**Strengths:** There's a solid semantic connection and a fair number of relevant skills identified.")
        if matched_company_keywords:
            assessment.append(f"**Key Matching Keywords:** {', '.join(sorted(list(matched_company_keywords)))}")
        assessment.append("You possess many skills relevant to the company, but some areas might require further development or emphasis during interviews.")
    elif company_fit_score >= 40:
        assessment.append(f"**Overall Fit:** **Moderate.** {candidate_name}'s profile has some alignment with {company_name}, but there are noticeable gaps.")
        assessment.append(f"**Areas for Improvement:** The semantic alignment is moderate, and while some relevant skills were found, a deeper dive into {company_name}'s specific needs and a focus on acquiring more of their core technologies would be beneficial.")
        if matched_company_keywords:
            assessment.append(f"**Key Matching Keywords:** {', '.join(sorted(list(matched_company_keywords)))}")
        assessment.append("Consider tailoring your resume more specifically to the company's known tech stack and industry challenges.")
    else:
        assessment.append(f"**Overall Fit:** **Limited.** {candidate_name}'s resume shows limited alignment with {company_name}'s typical profile.")
        assessment.append(f"**Areas for Improvement:** There is a low semantic match and few direct skill overlaps. It might be challenging to meet {company_name}'s expectations without significant upskilling or targeting different roles within the company.")
        if matched_company_keywords:
            assessment.append(f"**Key Matching Keywords:** {', '.join(sorted(list(matched_company_keywords)))}")
        else:
            assessment.append("No direct skill overlaps with the company's profile were found.")
        assessment.append("It's recommended to research {company_name}'s specific requirements thoroughly and consider how your experience can be reframed or augmented to better fit their needs.")
    
    return "\n".join(assessment)


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
        # Corrected variable name here: years_exp_for_overlap_score -> years_exp_for_model
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

def send_certificate_email(recipient_email, candidate_name, score, certificate_html_content, certificate_public_url, gmail_address, gmail_app_password):
    """
    Sends an email with the certificate HTML content AND a PDF attachment.
    """
    if not gmail_address or not gmail_app_password:
        st.error("❌ Email sending is not configured. Please ensure your Gmail address and App Password secrets are set in Streamlit.")
        return False

    msg = MIMEMultipart('mixed') # Changed to 'mixed' for attachments
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
    
    # Create a container for both plain and HTML parts
    alternative_part = MIMEMultipart('alternative')
    alternative_part.attach(MIMEText(plain_text_body, 'plain'))
    alternative_part.attach(MIMEText(html_body, 'html'))
    msg.attach(alternative_part)

    # Attach PDF
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
        # If PDF generation fails, send email without attachment
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

def _process_single_resume_for_screener_page(file_name, text, jd_text, jd_embedding, 
                                             resume_embedding, jd_name_for_results,
                                             high_priority_skills, medium_priority_skills, max_experience,
                                             _global_ml_model, target_company_name=None): # Added target_company_name
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
                "Company Fit Assessment": "Error: Resume text extraction failed.", # New field
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

        # Defensive checks for sets
        if not isinstance(resume_raw_skills_set, set):
            print(f"DEBUG: resume_raw_skills_set is not a set. Type: {type(resume_raw_skills_set)}. Defaulting to empty set.")
            resume_raw_skills_set = set()
        if not isinstance(jd_raw_skills_set, set):
            print(f"DEBUG: jd_raw_skills_set is not a set. Type: {type(jd_raw_skills_set)}. Defaulting to empty set.")
            jd_raw_skills_set = set()

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

        # --- NEW: Company Fit Assessment Logic ---
        company_fit_assessment_text = "No target company specified or found."
        if target_company_name:
            # Normalize company name for lookup
            normalized_company_name = None
            for company_key, profile_data in COMPANY_SKILL_PROFILES.items():
                if company_key.lower() == target_company_name.lower():
                    normalized_company_name = company_key
                    break

            if normalized_company_name:
                company_profile = COMPANY_SKILL_PROFILES[normalized_company_name]
                company_keywords_for_embedding = " ".join(company_profile["keywords"])
                company_description_for_embedding = company_profile["description"]

                # Combine keywords and description for a richer company embedding
                company_text_for_embedding = f"{company_description_for_embedding} {company_keywords_for_embedding}"
                company_embedding = global_sentence_model.encode([clean_text(company_text_for_embedding)])[0]

                company_fit_assessment_text = generate_company_fit_assessment(
                    candidate_name=candidate_name,
                    company_name=normalized_company_name,
                    resume_embedding=resume_embedding,
                    company_profile_embedding=company_embedding,
                    resume_skills_set=resume_raw_skills_set,
                    company_keywords=company_profile["keywords"]
                )
            else:
                company_fit_assessment_text = f"Company '{target_company_name}' not found in our predefined profiles. Please try one of the examples (e.g., Google, Microsoft, Amazon, Generic Tech Startup, IBM, Oracle, SAP, Cisco, Adobe, NVIDIA)."
        # --- END NEW: Company Fit Assessment Logic ---


        certificate_id = str(uuid.uuid4())
        certificate_rank = "Not Applicable"

        if score >= 90:
            certificate_rank = "🏅 Elite Match"
        elif score >= 80:
            certificate_rank = "⭐ Strong Match"
        elif score >= 75:
            certificate_rank = "✅ Good Fit"
        elif score >= 65: # Added new elif block for "Low Fit"
            certificate_rank = "⚪ Low Fit"
        elif score >= 50:
            certificate_rank = "🟡 Basic Fit"
        
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
            "Company Fit Assessment": company_fit_assessment_text, # New field added here
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
            "Company Fit Assessment": f"Critical Error: {e}", # New field
            "Matched Keywords": "", "Missing Skills": "",
            "Matched Keywords (Categorized)": "{}", # Store as empty JSON string
            "Missing Skills (Categorized)": "{}", # Store as empty JSON string
            "Semantic Similarity": 0.0, "Resume Raw Text": "",
            "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
            "Tag": "❌ Critical Processing Error"
        }
# --- NEW: Centralized Course Database ---
course_database = {
    "python": {"title": "Python for Everybody (Coursera)", "link": "https://www.coursera.org/learn/python"},
    "java": {"title": "Java Programming Masterclass (Udemy)", "link": "https://www.udemy.com/course/java-the-complete-java-developer-course/"},
    "javascript": {"title": "The Complete JavaScript Course (Udemy)", "link": "https://www.udemy.com/course/the-complete-javascript-course/"},
    "react": {"title": "React - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
    "sql": {"title": "SQL for Data Science (Coursera)", "link": "https://www.coursera.org/learn/sql-for-data-science"},
    "aws": {"title": "AWS Certified Cloud Practitioner (Udemy)", "link": "https://www.udemy.com/course/aws-certified-cloud-practitioner-clf-c01/"},
    "docker": {"title": "Docker & Kubernetes: The Practical Guide (Udemy)", "link": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/"},
    "machine learning": {"title": "Machine Learning (Coursera by Andrew Ng)", "link": "https://www.coursera.org/learn/machine-learning"},
    "data analysis": {"title": "Google Data Analytics Professional Certificate (Coursera)", "link": "https://www.coursera.org/professional-certificates/google-data-analytics"},
    "cybersecurity": {"title": "CompTIA Security+ (Udemy)", "link": "https://www.udemy.com/course/comptia-security-sy0-601-cert-prep-course/"},
    "project management": {"title": "Project Management Professional (PMP) Certification (various providers)", "link": "https://www.pmi.org/certifications/project-management-pmp"},
    "communication skills": {"title": "Effective Communication (Coursera)", "link": "https://www.coursera.org/learn/uva-darden-effective-communication"},
    "power bi": {"title": "Microsoft Power BI Desktop for Business Intelligence (Udemy)", "link": "https://www.udemy.com/course/microsoft-power-bi-desktop-for-business-intelligence/"},
    "data warehousing": {"title": "Data Warehousing for Business Intelligence (Coursera)", "link": "https://www.coursera.org/learn/data-warehousing-business-intelligence"},
    "etl": {"title": "ETL Testing & Data Warehouse Concepts (Udemy)", "link": "https://www.udemy.com/course/etl-testing-data-warehouse-concepts/"},
    "statistical analysis": {"title": "Statistics for Data Science and Business Analysis (Udemy)", "link": "https://www.udemy.com/course/statistics-for-data-science-and-business-analysis/"},
    "r": {"title": "R Programming (Coursera)", "link": "https://www.coursera.org/learn/r-programming"},
    "angular": {"title": "Angular - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/the-complete-guide-to-angular-2/"},
    "vue.js": {"title": "Vue JS - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/vuejs-2-the-complete-guide/"},
    "node.js": {"title": "Node.js, Express, MongoDB & More (Udemy)", "link": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/"},
    "django": {"title": "Python and Django Full Stack Web Developer Bootcamp (Udemy)", "link": "https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/"},
    "flask": {"title": "Flask: Develop Web Applications in Python (Udemy)", "link": "https://www.udemy.com/course/flask-develop-web-applications-in-python/"},
    "spring boot": {"title": "Spring & Hibernate for Beginners (Udemy)", "link": "https://www.udemy.com/course/spring-hibernate-tutorial/"},
    "mongodb": {"title": "MongoDB - The Complete Developer's Guide (Udemy)", "link": "https://www.udemy.com/course/mongodb-the-complete-developers-guide/"},
    "postgresql": {"title": "The Complete SQL Bootcamp (Udemy) - includes PostgreSQL", "link": "https://www.udemy.com/course/the-complete-sql-bootcamp/"},
    "mysql": {"title": "MySQL for Data Analysis (Udemy)", "link": "https://www.udemy.com/course/mysql-for-data-analysis/"},
    "azure": {"title": "AZ-900 Microsoft Azure Fundamentals (Udemy)", "link": "https://www.udemy.com/course/az-900-azure-fundamentals-practice-tests/"},
    "gcp": {"title": "Google Cloud Associate Cloud Engineer (Coursera)", "link": "https://www.coursera.org/professional-certificates/google-cloud-associate-cloud-engineer"},
    "kubernetes": {"title": "Kubernetes for the Absolute Beginners (Udemy)", "link": "https://www.udemy.com/course/learn-kubernetes/"},
    "terraform": {"title": "HashiCorp Certified: Terraform Associate (Udemy)", "link": "https://www.udemy.com/course/terraform-associate-practice-exam/"},
    "ansible": {"title": "Ansible for the Absolute Beginner (Udemy)", "link": "https://www.udemy.com/course/ansible-for-the-absolute-beginner-hands-on-devops/"},
    "jenkins": {"title": "Jenkins, From Zero To Hero (Udemy)", "link": "https://www.udemy.com/course/jenkins-from-zero-to-hero/"},
    "git": {"title": "Git Complete: The definitive, step-by-step guide (Udemy)", "link": "https://www.udemy.com/course/git-complete/"},
    "tableau": {"title": "Tableau 2020 A-Z: Hands-On Tableau Training For Data Science! (Udemy)", "link": "https://www.udemy.com/course/tableau10/"},
    "looker": {"title": "Looker for Data Analysts (Coursera)", "link": "https://www.coursera.org/learn/looker-for-data-analysts"},
    "qlik sense": {"title": "Qlik Sense Masterclass (Udemy)", "link": "https://www.udemy.com/course/qlik-sense-masterclass/"},
    "google data studio": {"title": "Google Data Studio A-Z (Udemy)", "link": "https://www.udemy.com/course/google-data-studio-a-z-hands-on-data-visualization-course/"},
    "dax": {"title": "DAX for Power BI (Udemy)", "link": "https://www.udemy.com/course/dax-for-power-bi-mastering-data-analysis-expressions/"},
    "m query": {"title": "Power Query, Power Pivot & DAX in Excel & Power BI (Udemy)", "link": "https://www.udemy.com/course/power-query-power-pivot-dax-excel-power-bi/"},
    "elt": {"title": "Modern Data Engineering with AWS (Udemy) - includes ELT concepts", "link": "https://www.udemy.com/course/modern-data-engineering-with-aws/"},
    "data lake": {"title": "Building a Data Lake on AWS (Coursera)", "link": "https://www.coursera.org/learn/building-data-lake-aws"},
    "data modeling": {"title": "Data Modeling Fundamentals (Pluralsight)", "link": "https://www.pluralsight.com/courses/data-modeling-fundamentals"},
    "business intelligence": {"title": "Business Intelligence Analyst Master's Program (Simplilearn)", "link": "https://www.simplilearn.com/business-intelligence-analyst-masters-program-training"},
    "data visualization": {"title": "Data Visualization with Python (Coursera)", "link": "https://www.coursera.org/learn/data-visualization-python"},
    "dashboarding": {"title": "Dashboarding with Excel (Coursera)", "link": "https://www.coursera.org/learn/dashboarding-excel"},
    "report generation": {"title": "Automating Reports with Python (Udemy)", "link": "https://www.udemy.com/course/automate-reports-with-python/"},
    "google analytics": {"title": "Google Analytics for Beginners (Google Analytics Academy)", "link": "https://analytics.google.com/analytics/academy/courses/1"},
    "deep learning": {"title": "Deep Learning Specialization (Coursera by Andrew Ng)", "link": "https://www.coursera.org/specializations/deep-learning"},
    "natural language processing": {"title": "Natural Language Processing Specialization (Coursera)", "link": "https://www.coursera.org/specializations/natural-language-processing"},
    "computer vision": {"title": "Computer Vision Basics (Coursera)", "link": "https://www.coursera.org/learn/computer-vision-basics"},
    "reinforcement learning": {"title": "Reinforcement Learning Specialization (Coursera)", "link": "https://www.coursera.org/specializations/reinforcement-learning"},
    "scikit-learn": {"title": "Machine Learning A-Z™: Hands-On Python & R In Data Science (Udemy)", "link": "https://www.udemy.com/course/machine-learning-a-z/"},
    "tensorflow": {"title": "TensorFlow in Practice Specialization (Coursera)", "link": "https://www.coursera.org/specializations/tensorflow-in-practice"},
    "pytorch": {"title": "Deep Learning with PyTorch (Udemy)", "link": "https://www.udemy.com/course/deep-learning-with-pytorch/"},
    "keras": {"title": "Deep Learning with Keras (Coursera)", "link": "https://www.coursera.org/learn/deep-learning-keras"},
    "xgboost": {"title": "XGBoost & LightGBM in Python (Udemy)", "link": "https://www.udemy.com/course/xgboost-lightgbm-in-python/"},
    "lightgbm": {"title": "XGBoost & LightGBM in Python (Udemy)", "link": "https://www.udemy.com/course/xgboost-lightgbm-in-python/"},
    "data cleaning": {"title": "Data Cleaning and Preparation in Python (DataCamp)", "link": "https://www.datacamp.com/courses/data-cleaning-and-preparation-in-python"},
    "feature engineering": {"title": "Feature Engineering for Machine Learning (Coursera)", "link": "https://www.coursera.org/learn/feature-engineering-machine-learning"},
    "model evaluation": {"title": "Machine Learning: Model Evaluation & Validation (Coursera)", "link": "https://www.coursera.org/learn/machine-learning-model-evaluation"},
    "statistical modeling": {"title": "Statistical Modeling for Data Science (Coursera)", "link": "https://www.coursera.org/learn/statistical-modeling-data-science"},
    "time series analysis": {"title": "Time Series Analysis in Python (DataCamp)", "link": "https://www.datacamp.com/courses/time-series-analysis-in-python"},
    "predictive modeling": {"title": "Predictive Modeling and Analytics (edX)", "link": "https://www.edx.org/course/predictive-modeling-and-analytics"},
    "clustering": {"title": "Unsupervised Learning in Python (DataCamp)", "link": "https://www.datacamp.com/courses/unsupervised-learning-in-python"},
    "classification": {"title": "Supervised Learning in Python (DataCamp)", "link": "https://www.datacamp.com/courses/supervised-learning-in-python"},
    "regression": {"title": "Linear Regression in Python (DataCamp)", "link": "https://www.datacamp.com/courses/linear-regression-in-python"},
    "neural networks": {"title": "Neural Networks and Deep Learning (Coursera by Andrew Ng)", "link": "https://www.coursera.org/learn/neural-networks-deep-learning"},
    "convolutional networks": {"title": "Convolutional Neural Networks (Coursera by Andrew Ng)", "link": "https://www.coursera.org/learn/convolutional-neural-networks"},
    "recurrent networks": {"title": "Sequence Models (Coursera by Andrew Ng) - includes RNNs", "link": "https://www.coursera.org/learn/sequence-models"},
    "transformers": {"title": "Transformers United (Coursera)", "link": "https://www.coursera.org/learn/transformers-united"},
    "llms": {"title": "Generative AI with Large Language Models (Coursera)", "link": "https://www.coursera.org/learn/generative-ai-with-llms"},
    "prompt engineering": {"title": "Prompt Engineering for Developers (DeepLearning.AI)", "link": "https://www.deeplearning.ai/short-courses/prompt-engineering-for-developers/"},
    "generative ai": {"title": "Generative AI for Everyone (Coursera)", "link": "https://www.coursera.org/learn/generative-ai-for-everyone"},
    "mlops": {"title": "Machine Learning Engineering for Production (MLOps) Specialization (Coursera)", "link": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"},
    "data munging": {"title": "Data Munging with Python (Udemy)", "link": "https://www.udemy.com/course/data-munging-with-python/"},
    "a/b testing": {"title": "A/B Testing for Data Science (Udemy)", "link": "https://www.udemy.com/course/ab-testing-for-data-science/"},
    "experiment design": {"title": "Experimentation and A/B Testing (Coursera)", "link": "https://www.coursera.org/learn/experimentation-ab-testing"},
    "hypothesis testing": {"title": "Hypothesis Testing in Python (DataCamp)", "link": "https://www.datacamp.com/courses/hypothesis-testing-in-python"},
    "bayesian statistics": {"title": "Bayesian Statistics (Coursera)", "link": "https://www.coursera.org/learn/bayesian-statistics"},
    "causal inference": {"title": "Causal Inference (edX)", "link": "https://www.edx.org/course/causal-inference"},
    "graph neural networks": {"title": "Graph Neural Networks (Coursera)", "link": "https://www.coursera.org/learn/graph-neural-networks"},
    "stakeholder management": {"title": "Stakeholder Management (Udemy)", "link": "https://www.udemy.com/course/stakeholder-management-course/"},
    "risk management": {"title": "Project Risk Management (Coursera)", "link": "https://www.coursera.org/learn/project-risk-management"},
    "change management": {"title": "Change Management Specialist Certification (Udemy)", "link": "https://www.udemy.com/course/change-management-specialist-certification/"},
    "public speaking": {"title": "Dynamic Public Speaking (Coursera)", "link": "https://www.coursera.org/learn/public-speaking"},
    "presentation skills": {"title": "Successful Presentation (Coursera)", "link": "https://www.coursera.org/learn/successful-presentation"},
    "cross-functional collaboration": {"title": "Collaborative Leadership (Coursera)", "link": "https://www.coursera.org/learn/collaborative-leadership"},
    "problem solving": {"title": "Creative Problem Solving (Coursera)", "link": "https://www.coursera.org/learn/creative-problem-solving"},
    "critical thinking": {"title": "Critical Thinking Skills for University Success (Coursera)", "link": "https://www.coursera.org/learn/critical-thinking-university-success"},
    "analytical skills": {"title": "Analytical Skills for Business (Coursera)", "link": "https://www.coursera.org/learn/analytical-skills-business"},
    "adaptability": {"title": "Developing Your Adaptability as a Leader (Coursera)", "link": "https://www.coursera.org/learn/developing-adaptability-as-leader"},
    "time management": {"title": "Learning How to Learn (Coursera) - includes time management", "link": "https://www.coursera.org/learn/learning-how-to-learn"},
    "organizational skills": {"title": "Organizational Design and Management (Coursera)", "link": "https://www.coursera.org/learn/organizational-design"},
    "attention to detail": {"title": "Attention to Detail: The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/attention-to-detail/"},
    "leadership": {"title": "Introduction to Leadership (Coursera)", "link": "https://www.coursera.org/learn/introduction-to-leadership"},
    "mentorship": {"title": "Mentoring and Coaching (Coursera)", "link": "https://www.coursera.org/learn/mentoring-coaching"},
    "team leadership": {"title": "Leading Teams (Coursera)", "link": "https://www.coursera.org/learn/leading-teams"},
    "decision making": {"title": "Effective Decision-Making (Coursera)", "link": "https://www.coursera.org/learn/effective-decision-making"},
    "negotiation": {"title": "Successful Negotiation: Essential Strategies and Skills (Coursera)", "link": "https://www.coursera.org/learn/negotiation-skills"},
    "client management": {"title": "Client Management (Udemy)", "link": "https://www.udemy.com/course/client-management/"},
    "active listening": {"title": "Effective Communication: Listening Skills (Udemy)", "link": "https://www.udemy.com/course/effective-communication-listening-skills/"},
    "creativity": {"title": "Creative Thinking: Techniques and Tools for Success (Coursera)", "link": "https://www.coursera.org/learn/creative-thinking"},
    "innovation": {"title": "Innovation Management (Coursera)", "link": "https://www.coursera.org/learn/innovation-management"},
    "research": {"title": "Research Methods for Business (Coursera)", "link": "https://www.coursera.org/learn/research-methods-business"},
    "report writing": {"title": "Business English Communication Skills (Coursera) - includes report writing", "link": "https://www.coursera.org/learn/business-english-communication"},
    "documentation": {"title": "Technical Writing: Documentation (Coursera)", "link": "https://www.coursera.org/learn/technical-writing-documentation"},
    "agile methodologies": {"title": "Agile with Atlassian Jira (Coursera)", "link": "https://www.coursera.org/learn/agile-atlassian-jira"},
    "scrum": {"title": "Scrum Master Certification Prep (Udemy)", "link": "https://www.udemy.com/course/scrum-master-certification-prep-training/"},
    "kanban": {"title": "Kanban for Software Development (Udemy)", "link": "https://www.udemy.com/course/kanban-for-software-development/"},
    "jira": {"title": "Jira Fundamentals (Coursera)", "link": "https://www.coursera.org/learn/jira-fundamentals"},
    "trello": {"title": "Trello for Project Management (Udemy)", "link": "https://www.udemy.com/course/trello-for-project-management/"},
    "product lifecycle": {"title": "Product Management: Product Lifecycle (Coursera)", "link": "https://www.coursera.org/learn/product-management-lifecycle"},
    "sprint planning": {"title": "Agile Project Management with Google: Sprint Planning (Coursera)", "link": "https://www.coursera.org/learn/agile-project-management-google-sprint-planning"},
    "project charter": {"title": "Project Management: Project Planning (Coursera) - includes project charter", "link": "https://www.coursera.org/learn/project-planning"},
    "gantt charts": {"title": "Microsoft Project 2019/365: The Complete Course (Udemy) - includes Gantt charts", "link": "https://www.udemy.com/course/microsoft-project-2019-365-the-complete-course/"},
    "mvp": {"title": "Product Management: Building a Product Strategy (Coursera) - includes MVP", "link": "https://www.coursera.org/learn/product-management-strategy"},
    "backlog grooming": {"title": "Agile Project Management with Google: Backlog Grooming (Coursera)", "link": "https://www.coursera.org/learn/agile-project-management-google-backlog-grooming"},
    "program management": {"title": "Program Management Professional (PgMP) Certification (various providers)", "link": "https://www.pmi.org/certifications/program-management-pgmp"},
    "portfolio management": {"title": "Portfolio Management Professional (PfMP) Certification (various providers)", "link": "https://www.pmi.org/certifications/portfolio-management-pfmp"},
    "pmp": {"title": "PMP Certification Exam Prep (Udemy)", "link": "https://www.udemy.com/course/pmp-certification-exam-prep-course-pmbok-6th-edition/"},
    "csm": {"title": "Certified ScrumMaster (CSM) Training (various providers)", "link": "https://www.scrumalliance.org/certifications/practitioners/csm-certification"},
    "information security": {"title": "Introduction to Information Security (Coursera)", "link": "https://www.coursera.org/learn/introduction-to-information-security"},
    "risk assessment": {"title": "Cybersecurity Risk Management (Coursera)", "link": "https://www.coursera.org/learn/cybersecurity-risk-management"},
    "compliance": {"title": "Cybersecurity Compliance Framework & System Administration (Coursera)", "link": "https://www.coursera.org/learn/cybersecurity-compliance-framework-system-administration"},
    "gdpr": {"title": "GDPR Compliance: The Ultimate Guide (Udemy)", "link": "https://www.udemy.com/course/gdpr-compliance-the-ultimate-guide/"},
    "hipaa": {"title": "HIPAA Compliance: The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/hipaa-compliance/"},
    "iso 27001": {"title": "ISO 27001 Lead Implementer (Udemy)", "link": "https://www.udemy.com/course/iso-27001-lead-implementer-training/"},
    "penetration testing": {"title": "Penetration Testing and Ethical Hacking (Coursera)", "link": "https://www.coursera.org/learn/penetration-testing-ethical-hacking"},
    "vulnerability management": {"title": "Vulnerability Management (Coursera)", "link": "https://www.coursera.org/learn/vulnerability-management"},
    "incident response": {"title": "Cybersecurity Incident Response (Coursera)", "link": "https://www.coursera.org/learn/cybersecurity-incident-response"},
    "security audits": {"title": "IT Audit Fundamentals (Udemy)", "link": "https://www.udemy.com/course/it-audit-fundamentals/"},
    "forensics": {"title": "Introduction to Digital Forensics (Coursera)", "link": "https://www.coursera.org/learn/introduction-to-digital-forensics"},
    "threat intelligence": {"title": "Cyber Threat Intelligence (Coursera)", "link": "https://www.coursera.org/learn/cyber-threat-intelligence"},
    "siem": {"title": "Splunk Fundamentals 1 (Splunk Education)", "link": "https://www.splunk.com/en_us/training/courses/splunk-fundamentals-1.html"},
    "firewall management": {"title": "Network Security with Firewalls (Udemy)", "link": "https://www.udemy.com/course/network-security-with-firewalls/"},
    "endpoint security": {"title": "Endpoint Security (Coursera)", "link": "https://www.coursera.org/learn/endpoint-security"},
    "iam": {"title": "Identity and Access Management (IAM) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/identity-and-access-management-iam-fundamentals/"},
    "cryptography": {"title": "Cryptography I (Coursera)", "link": "https://www.coursera.org/learn/cryptography"},
    "network security": {"title": "Network Security (Coursera)", "link": "https://www.coursera.org/learn/network-security"},
    "application security": {"title": "Application Security (Coursera)", "link": "https://www.coursera.org/learn/application-security"},
    "cloud security": {"title": "Cloud Security Fundamentals (Coursera)", "link": "https://www.coursera.org/learn/cloud-security-fundamentals"},
    "confluence": {"title": "Confluence Fundamentals (Atlassian University)", "link": "https://university.atlassian.com/student/path/780283-confluence-fundamentals"},
    "swagger": {"title": "Mastering OpenAPI & Swagger (Udemy)", "link": "https://www.udemy.com/course/mastering-openapi-swagger/"},
    "openapi": {"title": "Mastering OpenAPI & Swagger (Udemy)", "link": "https://www.udemy.com/course/mastering-openapi-swagger/"},
    "zendesk": {"title": "Zendesk Support for Agents (Zendesk)", "link": "https://training.zendesk.com/learning-paths/zendesk-support-for-agents"},
    "servicenow": {"title": "ServiceNow Fundamentals (ServiceNow)", "link": "https://www.servicenow.com/services/training-and-certification/servicenow-fundamentals.html"},
    "intercom": {"title": "Intercom Academy (Intercom)", "link": "https://www.intercom.com/academy"},
    "live chat": {"title": "Customer Service: Live Chat Skills (Udemy)", "link": "https://www.udemy.com/course/customer-service-live-chat-skills/"},
    "ticketing systems": {"title": "IT Help Desk Professional Certificate (Google/Coursera) - covers ticketing", "link": "https://www.coursera.org/professional-certificates/google-it-support"},
    "hubspot": {"title": "HubSpot Marketing Software (HubSpot Academy)", "link": "https://academy.hubspot.com/courses/hubspot-marketing-software"},
    "salesforce marketing cloud": {"title": "Salesforce Marketing Cloud Administrator (Trailhead)", "link": "https://trailhead.salesforce.com/content/learn/trails/sfmc_admin_essentials"},
    "quickbooks": {"title": "QuickBooks Online Masterclass (Udemy)", "link": "https://www.udemy.com/course/quickbooks-online-masterclass/"},
    "sap fico": {"title": "SAP FICO Training (Udemy)", "link": "https://www.udemy.com/course/sap-fico-training/"},
    "oracle financials": {"title": "Oracle Financials Cloud: General Ledger (Oracle University)", "link": "https://education.oracle.com/oracle-financials-cloud-general-ledger-2020-implementation-essentials/pexam_1Z0-1054-20"},
    "workday": {"title": "Workday HCM Fundamentals (Workday)", "link": "https://www.workday.com/en-us/training/workday-hcm-fundamentals.html"},
    "microsoft dynamics": {"title": "Microsoft Dynamics 365 Fundamentals (MB-901) (Udemy)", "link": "https://www.udemy.com/course/microsoft-dynamics-365-fundamentals-mb-901/"},
    "netsuite": {"title": "NetSuite Fundamentals (Oracle NetSuite)", "link": "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N330219.html"},
    "adobe creative suite": {"title": "Adobe Creative Cloud Masterclass (Udemy)", "link": "https://www.udemy.com/course/adobe-creative-cloud-masterclass/"},
    "canva": {"title": "Canva Master Course (Udemy)", "link": "https://www.udemy.com/course/canva-master-course/"},
    "mailchimp": {"title": "Mailchimp Basics (Mailchimp)", "link": "https://mailchimp.com/help/mailchimp-basics/"},
    "hootsuite": {"title": "Hootsuite Platform Certification (Hootsuite Academy)", "link": "https://hootsuite.com/education/certifications/hootsuite-platform-certification"},
    "buffer": {"title": "Buffer Academy (Buffer)", "link": "https://buffer.com/library/"},
    "semrush": {"title": "SEMrush SEO Toolkit Course (SEMrush Academy)", "link": "https://www.semrush.com/academy/courses/semrush-seo-toolkit-course"},
    "ahrefs": {"title": "Blogging for Business (Ahrefs Academy) - includes Ahrefs usage", "link": "https://ahrefs.com/academy/blogging-for-business"},
    "moz": {"title": "SEO Essentials Certificate (Moz Academy)", "link": "https://moz.com/academy/seo-essentials"},
    "screaming frog": {"title": "Screaming Frog SEO Spider Guide (Screaming Frog)", "link": "https://www.screamingfrog.co.uk/seo-spider/user-guide/"},
    "jmeter": {"title": "Apache JMeter Basics (Udemy)", "link": "https://www.udemy.com/course/apache-jmeter-basics/"},
    "postman": {"title": "Postman API Testing (Udemy)", "link": "https://www.udemy.com/course/postman-api-testing-from-scratch/"},
    "soapui": {"title": "SoapUI Pro for Beginners (Udemy)", "link": "https://www.udemy.com/course/soapui-pro-for-beginners/"},
    "svn": {"title": "SVN for Developers (Udemy)", "link": "https://www.udemy.com/course/svn-for-developers/"},
    "perforce": {"title": "Perforce Helix Core Fundamentals (Perforce)", "link": "https://www.perforce.com/support/training/helix-core-fundamentals"},
    "asana": {"title": "Asana for Project Management (Udemy)", "link": "https://www.udemy.com/course/asana-for-project-management/"},
    "monday.com": {"title": "monday.com Masterclass (Udemy)", "link": "https://www.udemy.com/course/mondaycom-masterclass/"},
    "miro": {"title": "Miro Basics (Miro Academy)", "link": "https://academy.miro.com/courses/miro-basics"},
    "lucidchart": {"title": "Lucidchart Training (Lucidchart)", "link": "https://www.lucidchart.com/pages/training"},
    "visio": {"title": "Microsoft Visio 2019/365: The Complete Course (Udemy)", "link": "https://www.udemy.com/course/microsoft-visio-2019-365-the-complete-course/"},
    "ms project": {"title": "Microsoft Project 2019/365: The Complete Course (Udemy)", "link": "https://www.udemy.com/course/microsoft-project-2019-365-the-complete-course/"},
    "primavera": {"title": "Primavera P6 Professional Fundamentals (Udemy)", "link": "https://www.udemy.com/course/primavera-p6-professional-fundamentals/"},
    "autocad": {"title": "AutoCAD 2023 Essential Training (LinkedIn Learning)", "link": "https://www.linkedin.com/learning/autocad-2023-essential-training"},
    "solidworks": {"title": "SolidWorks 2023 Essential Training (LinkedIn Learning)", "link": "https://www.linkedin.com/learning/solidworks-2023-essential-training"},
    "matlab": {"title": "MATLAB Programming for Engineers and Scientists (Coursera)", "link": "https://www.coursera.org/learn/matlab-programming"},
    "labview": {"title": "LabVIEW Core 1 (National Instruments)", "link": "https://www.ni.com/en-us/support/training/labview-core-1.html"},
    "simulink": {"title": "Simulink Onramp (MathWorks)", "link": "https://www.mathworks.com/learn/tutorials/simulink-onramp.html"},
    "ansys": {"title": "ANSYS Workbench Tutorial (Udemy)", "link": "https://www.udemy.com/course/ansys-workbench-tutorial/"},
    "catia": {"title": "CATIA V5-6R2018: Introduction to Modeling (Udemy)", "link": "https://www.udemy.com/course/catia-v5-6r2018-introduction-to-modeling/"},
    "nx": {"title": "Siemens NX CAD Fundamentals (Udemy)", "link": "https://www.udemy.com/course/siemens-nx-cad-fundamentals/"},
    "revit": {"title": "Revit 2023 Essential Training (LinkedIn Learning)", "link": "https://www.linkedin.com/learning/revit-2023-essential-training"},
    "arcgis": {"title": "ArcGIS Pro Basics (Esri Academy)", "link": "https://www.esri.com/training/catalog/576304348519f6a2d98762d6/arcgis-pro-basics/"},
    "qgis": {"title": "QGIS for Beginners (Udemy)", "link": "https://www.udemy.com/course/qgis-for-beginners/"},
    "opencv": {"title": "OpenCV Python for Beginners (Udemy)", "link": "https://www.udemy.com/course/opencv-python-for-beginners/"},
    "nltk": {"title": "Python for Text Mining and NLP (Udemy) - includes NLTK", "link": "https://www.udemy.com/course/python-for-text-mining-and-nlp/"},
    "spacy": {"title": "Natural Language Processing with SpaCy (DataCamp)", "link": "https://www.datacamp.com/courses/natural-language-processing-with-spacy"},
    "gensim": {"title": "Topic Modeling in Python (DataCamp) - includes Gensim", "link": "https://www.datacamp.com/courses/topic-modeling-in-python"},
    "hugging face transformers": {"title": "Natural Language Processing with Transformers (Coursera)", "link": "https://www.coursera.org/learn/natural-language-processing-transformers"},
    "docker compose": {"title": "Docker Compose in Depth (Udemy)", "link": "https://www.udemy.com/course/docker-compose-in-depth/"},
    "helm": {"title": "Helm - The Kubernetes Package Manager (Udemy)", "link": "https://www.udemy.com/course/helm-the-kubernetes-package-manager/"},
    "ansible tower": {"title": "Ansible Tower Fundamentals (Red Hat)", "link": "https://www.redhat.com/en/services/training/do409-ansible-automation-platform-administration"},
    "saltstack": {"title": "SaltStack Fundamentals (SaltStack)", "link": "https://docs.saltproject.io/salt/training/index.html"},
    "chef inspec": {"title": "Chef InSpec Fundamentals (Chef)", "link": "https://learn.chef.io/courses/chef-inspec-fundamentals"},
    "terraform cloud": {"title": "Terraform Cloud and Enterprise (HashiCorp)", "link": "https://learn.hashicorp.com/collections/terraform/cloud-enterprise"},
    "vault": {"title": "HashiCorp Certified: Vault Associate (Udemy)", "link": "https://www.udemy.com/course/hashicorp-certified-vault-associate-practice-exam/"},
    "consul": {"title": "HashiCorp Certified: Consul Associate (Udemy)", "link": "https://www.udemy.com/course/hashicorp-certified-consul-associate-practice-exam/"},
    "nomad": {"title": "HashiCorp Certified: Nomad Associate (HashiCorp)", "link": "https://learn.hashicorp.com/collections/nomad/associate-certification"},
    "prometheus": {"title": "Prometheus Monitoring Fundamentals (Udemy)", "link": "https://www.udemy.com/course/prometheus-monitoring-fundamentals/"},
    "grafana": {"title": "Grafana - A Complete Guide (Udemy)", "link": "https://www.udemy.com/course/grafana-complete-guide/"},
    "alertmanager": {"title": "Prometheus & Alertmanager (Udemy)", "link": "https://www.udemy.com/course/prometheus-alertmanager/"},
    "loki": {"title": "Grafana Loki Fundamentals (Grafana Labs)", "link": "https://grafana.com/training/loki-fundamentals/"},
    "tempo": {"title": "Grafana Tempo Fundamentals (Grafana Labs)", "link": "https://grafana.com/training/tempo-fundamentals/"},
    "jaeger": {"title": "Distributed Tracing with Jaeger (Udemy)", "link": "https://www.udemy.com/course/distributed-tracing-with-jaeger/"},
    "zipkin": {"title": "Distributed Tracing with Spring Cloud Sleuth and Zipkin (Udemy)", "link": "https://www.udemy.com/course/distributed-tracing-with-spring-cloud-sleuth-and-zipkin/"},
    "fluentd": {"title": "Fluentd Fundamentals (Fluentd)", "link": "https://www.fluentd.org/training"},
    "logstash": {"title": "Elastic Stack: Logstash (Udemy)", "link": "https://www.udemy.com/course/elastic-stack-logstash/"},
    "kibana": {"title": "Elastic Stack: Kibana (Udemy)", "link": "https://www.udemy.com/course/elastic-stack-kibana/"},
    "datadog": {"title": "Datadog Fundamentals (Datadog)", "link": "https://learn.datadoghq.com/course/datadog-fundamentals"},
    "new relic": {"title": "New Relic Fundamentals (New Relic University)", "link": "https://learn.newrelic.com/courses/new-relic-fundamentals"},
    "appdynamics": {"title": "AppDynamics Fundamentals (AppDynamics)", "link": "https://docs.appdynamics.com/appd/21.x/21.9/en/getting-started/appdynamics-university"},
    "dynatrace": {"title": "Dynatrace Associate Certification (Dynatrace)", "link": "https://www.dynatrace.com/support/help/learning/certification"},
    "nagios": {"title": "Nagios Core Monitoring (Udemy)", "link": "https://www.udemy.com/course/nagios-core-monitoring/"},
    "zabbix": {"title": "Zabbix Certified Specialist (Zabbix)", "link": "https://www.zabbix.com/training"},
    "icinga": {"title": "Icinga 2 Fundamentals (Icinga)", "link": "https://www.icinga.com/docs/icinga-2/latest/doc/10-getting-started/01-installation/"},
    "prtg": {"title": "PRTG Network Monitor Training (Paessler)", "link": "https://www.paessler.com/prtg/training"},
    "solarwinds": {"title": "SolarWinds Orion Platform Fundamentals (SolarWinds)", "link": "https://www.solarwinds.com/success-center/training"},
    "wireshark": {"title": "Wireshark for Beginners (Udemy)", "link": "https://www.udemy.com/course/wireshark-for-beginners/"},
    "nmap": {"title": "Nmap: The Ultimate Guide (Udemy)", "link": "https://www.udemy.com/course/nmap-the-ultimate-guide/"},
    "metasploit": {"title": "Metasploit Framework: The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/metasploit-framework-the-complete-guide/"},
    "burp suite": {"title": "Burp Suite for Web Penetration Testing (Udemy)", "link": "https://www.udemy.com/course/burp-suite-for-web-penetration-testing/"},
    "owasp zap": {"title": "OWASP ZAP - Web Application Penetration Testing (Udemy)", "link": "https://www.udemy.com/course/owasp-zap-web-application-penetration-testing/"},
    "nessus": {"title": "Nessus Vulnerability Scanner (Udemy)", "link": "https://www.udemy.com/course/nessus-vulnerability-scanner/"},
    "qualys": {"title": "Qualys Vulnerability Management (Qualys)", "link": "https://www.qualys.com/training/"},
    "rapid7": {"title": "Rapid7 InsightVM Fundamentals (Rapid7)", "link": "https://www.rapid7.com/training/insightvm-fundamentals/"},
    "tenable": {"title": "Tenable Nessus Fundamentals (Tenable)", "link": "https://www.tenable.com/training/courses/nessus-fundamentals"},
    "crowdstrike": {"title": "CrowdStrike Falcon Platform Fundamentals (CrowdStrike)", "link": "https://www.crowdstrike.com/resources/training/"},
    "sentinelone": {"title": "SentinelOne Endpoint Protection Platform (SentinelOne)", "link": "https://support.sentinelone.com/hc/en-us/categories/360002127274-Training-and-Certification)"},
    "palo alto networks": {"title": "Palo Alto Networks PCNSA Certification (Udemy)", "link": "https://www.udemy.com/course/palo-alto-networks-pcnsa-certification/"},
    "fortinet": {"title": "Fortinet NSE 4 - FortiGate Security (Fortinet)", "link": "https://training.fortinet.com/course/nse-4-fortigate-security/"},
    "cisco umbrella": {"title": "Cisco Umbrella Fundamentals (Cisco)", "link": "https://www.cisco.com/c/en/us/training-events/training-certifications/training/cisco-umbrella.html"},
    "okta": {"title": "Okta Administrator (Okta)", "link": "https://www.okta.com/training/courses/okta-administrator/"},
    "auth0": {"title": "Auth0 Fundamentals (Auth0)", "link": "https://auth0.com/docs/get-started/auth0-fundamentals"},
    "keycloak": {"title": "Keycloak Fundamentals (Udemy)", "link": "https://www.udemy.com/course/keycloak-fundamentals/"},
    "ping identity": {"title": "Ping Identity Administrator (Ping Identity)", "link": "https://www.pingidentity.com/en/training.html"},
    "active directory": {"title": "Active Directory Administration for Beginners (Udemy)", "link": "https://www.udemy.com/course/active-directory-administration-for-beginners/"},
    "ldap": {"title": "LDAP for Beginners (Udemy)", "link": "https://www.udemy.com/course/ldap-for-beginners/"},
    "oauth": {"title": "OAuth 2.0 and OpenID Connect (Udemy)", "link": "https://www.udemy.com/course/oauth2-openid-connect-masterclass/"},
    "jwt": {"title": "JWT Authentication in Practice (Udemy)", "link": "https://www.udemy.com/course/jwt-authentication-in-practice/"},
    "openid connect": {"title": "OAuth 2.0 and OpenID Connect (Udemy)", "link": "https://www.udemy.com/course/oauth2-openid-connect-masterclass/"},
    "saml": {"title": "SAML 2.0 For Beginners (Udemy)", "link": "https://www.udemy.com/course/saml-20-for-beginners/"},
    "mfa": {"title": "Multi-Factor Authentication (MFA) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/multi-factor-authentication-mfa-fundamentals/"},
    "sso": {"title": "Single Sign-On (SSO) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/single-sign-on-sso-fundamentals/"},
    "pki": {"title": "Public Key Infrastructure (PKI) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/public-key-infrastructure-pki-fundamentals/"},
    "tls/ssl": {"title": "TLS/SSL Certificates Explained (Udemy)", "link": "https://www.udemy.com/course/tls-ssl-certificates-explained/"},
    "vpn": {"title": "VPN Fundamentals (Udemy)", "link": "https://www.udemy.com/course/vpn-fundamentals/"},
    "ids/ips": {"title": "Intrusion Detection/Prevention Systems (IDS/IPS) (Udemy)", "link": "https://www.udemy.com/course/intrusion-detection-prevention-systems-ids-ips/"},
    "dlp": {"title": "Data Loss Prevention (DLP) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/data-loss-prevention-dlp-fundamentals/"},
    "casb": {"title": "Cloud Access Security Broker (CASB) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/cloud-access-security-broker-casb-fundamentals/"},
    "soar": {"title": "Security Orchestration, Automation and Response (SOAR) (Udemy)", "link": "https://www.udemy.com/course/security-orchestration-automation-and-response-soar/"},
    "xdr": {"title": "Extended Detection and Response (XDR) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/extended-detection-and-response-xdr-fundamentals/"},
    "edr": {"title": "Endpoint Detection and Response (EDR) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/endpoint-detection-and-response-edr-fundamentals/"},
    "mdr": {"title": "Managed Detection and Response (MDR) Fundamentals (Udemy)", "link": "https://www.udemy.com/course/managed-detection-and-response-mdr-fundamentals/"},
    "grc": {"title": "GRC Fundamentals (Udemy)", "link": "https://www.udemy.com/course/grc-fundamentals/"},
    "itil": {"title": "ITIL 4 Foundation (Udemy)", "link": "https://www.udemy.com/course/itil-4-foundation-certification-training/"},
    "lean six sigma": {"title": "Lean Six Sigma Green Belt (Udemy)", "link": "https://www.udemy.com/course/lean-six-sigma-green-belt-certification-course/"},
    "cfa": {"title": "CFA Level 1 Exam Prep (Kaplan Schweser)", "link": "https://www.schweser.com/cfa/level-1/study-packages"},
    "cpa": {"title": "CPA Exam Review (Becker)", "link": "https://www.becker.com/cpa-review"},
    "shrm-cp": {"title": "SHRM-CP Exam Prep (SHRM)", "link": "https://www.shrm.org/certification/getting-certified/prep/pages/default.aspx"},
    "phr": {"title": "PHR Certification Prep (HRCI)", "link": "https://www.hrci.org/our-certifications/phr/phr-preparation"},
    "ceh": {"title": "Certified Ethical Hacker (CEH) (EC-Council)", "link": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/"},
    "oscp": {"title": "Offensive Security Certified Professional (OSCP) (Offensive Security)", "link": "https://www.offensive-security.com/pwk-oscp/"},
    "ccna": {"title": "Cisco CCNA 200-301 (Udemy)", "link": "https://www.udemy.com/course/ccna-200-301-complete-course-and-simulator/)"},
    "cissp": {"title": "CISSP Certification Exam Prep (Udemy)", "link": "https://www.udemy.com/course/cissp-certification-training-course/"},
    "cism": {"title": "CISM Certification Exam Prep (Udemy)", "link": "https://www.udemy.com/course/cism-certification-training-course/"},
    "comptia security+": {"title": "CompTIA Security+ (Udemy)", "link": "https://www.udemy.com/course/comptia-security-sy0-601-cert-prep-course/"},
    "typescript": {"title": "TypeScript: The Complete Developer's Guide (Udemy)", "link": "https://www.udemy.com/course/typescript-the-complete-developers-guide/"},
    "go": {"title": "Go: The Complete Developer's Guide (Udemy)", "link": "https://www.udemy.com/course/go-the-complete-developers-guide/"},
    "swift": {"title": "iOS & Swift - The Complete iOS App Development Bootcamp (Udemy)", "link": "https://www.udemy.com/course/ios-13-app-development-bootcamp/"},
    "kotlin": {"title": "Android App Development Masterclass with Kotlin (Udemy)", "link": "https://www.udemy.com/course/android-oreo-kotlin-developer-masterclass/"},
    "php": {"title": "PHP for Beginners - Become a PHP Master - CMS Project (Udemy)", "link": "https://www.udemy.com/course/php-for-absolute-beginners-php-crash-course/"},
    "ruby": {"title": "The Complete Ruby on Rails Developer Course (Udemy)", "link": "https://www.udemy.com/course/the-complete-ruby-on-rails-developer-course/"},
    "bash scripting": {"title": "Linux Command Line and Shell Scripting Masterclass (Udemy)", "link": "https://www.udemy.com/course/linux-command-line-shell-scripting-masterclass/"},
    "shell scripting": {"title": "Linux Command Line and Shell Scripting Masterclass (Udemy)", "link": "https://www.udemy.com/course/linux-command-line-shell-scripting-masterclass/"},
    "html5": {"title": "The Complete 2023 Web Development Bootcamp (Udemy) - includes HTML5", "link": "https://www.udemy.com/course/the-complete-web-development-bootcamp/"},
    "css3": {"title": "The Complete 2023 Web Development Bootcamp (Udemy) - includes CSS3", "link": "https://www.udemy.com/course/the-complete-web-development-bootcamp/"},
    "express.js": {"title": "Node.js, Express, MongoDB & More (Udemy)", "link": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/"},
    "websockets": {"title": "Realtime Web with Node.js and WebSockets (Udemy)", "link": "https://www.udemy.com/course/realtime-web-with-nodejs-and-websockets/"},
    "dynamodb": {"title": "AWS DynamoDB - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/aws-dynamodb-the-complete-guide/"},
    "cassandra": {"title": "Apache Cassandra Fundamentals (DataStax Academy)", "link": "https://academy.datastax.com/courses/ds201-datastax-apache-cassandra-fundamentals"},
    "elasticsearch": {"title": "Elasticsearch 7 and the Elastic Stack (Udemy)", "link": "https://www.udemy.com/course/elasticsearch-7-and-the-elastic-stack/"},
    "neo4j": {"title": "Neo4j Graph Database Fundamentals (Udemy)", "link": "https://www.udemy.com/course/neo4j-graph-database-fundamentals/"},
    "redis": {"title": "Redis Crash Course (Udemy)", "link": "https://www.udemy.com/course/redis-crash-course/"},
    "snowflake": {"title": "Snowflake Data Warehouse Masterclass (Udemy)", "link": "https://www.udemy.com/course/snowflake-data-warehouse-masterclass/"},
    "redshift": {"title": "AWS Certified Data Analytics - Specialty (Udemy) - includes Redshift", "link": "https://www.udemy.com/course/aws-certified-data-analytics-specialty-das-c01/"},
    "aurora": {"title": "AWS Certified Database - Specialty (Udemy) - includes Aurora", "link": "https://www.udemy.com/course/aws-certified-database-specialty/"},
    "documentdb": {"title": "AWS Certified Database - Specialty (Udemy) - includes DocumentDB", "link": "https://www.udemy.com/course/aws-certified-database-specialty/"},
    "cosmosdb": {"title": "Azure Cosmos DB (Microsoft Learn)", "link": "https://learn.microsoft.com/en-us/training/paths/azure-cosmos-db-develop/"},
    "serverless": {"title": "Serverless Framework with AWS Lambda & API Gateway (Udemy)", "link": "https://www.udemy.com/course/serverless-framework-aws-lambda-api-gateway/"},
    "aws lambda": {"title": "AWS Lambda and the Serverless Framework - Hands-On! (Udemy)", "link": "https://www.udemy.com/course/aws-lambda-serverless-framework-a-complete-guide/"},
    "azure functions": {"title": "Azure Functions: The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/azure-functions-the-complete-guide/"},
    "google cloud functions": {"title": "Google Cloud Functions for Developers (Google Cloud)", "link": "https://cloud.google.com/functions/docs/tutorials"},
    "github": {"title": "The Git & GitHub Bootcamp (Udemy)", "link": "https://www.udemy.com/course/git-and-github-bootcamp/"},
    "gitlab": {"title": "GitLab CI/CD: Learn GitLab CI for DevOps & Developers (Udemy)", "link": "https://www.udemy.com/course/gitlab-ci-cd-pipelines/"},
    "bitbucket": {"title": "Bitbucket Fundamentals (Atlassian University)", "link": "https://university.atlassian.com/student/path/780284-bitbucket-fundamentals"},
    "ci/cd": {"title": "Ultimate AWS Certified DevOps Engineer Professional 2023 (Udemy) - includes CI/CD", "link": "https://www.udemy.com/course/aws-certified-devops-engineer-professional-hands-on/"},
    "github actions": {"title": "GitHub Actions - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/github-actions-the-complete-guide/"},
    "azure devops": {"title": "Azure DevOps - The Complete Guide (Udemy)", "link": "https://www.udemy.com/course/azure-devops-complete-guide/"},
    "excel (advanced)": {"title": "Microsoft Excel - Excel from Beginner to Advanced (Udemy)", "link": "https://www.udemy.com/course/microsoft-excel-2013-from-beginner-to-advanced-and-beyond/"},
}

# --- NEW: Function to suggest courses based on the database ---
def suggest_courses(missing_skills):
    course_suggestions_list = []
    for skill in missing_skills:
        # Normalize skill name to lowercase for database lookup
        normalized_skill = skill.lower()
        course = course_database.get(normalized_skill, None)
        if course:
            course_suggestions_list.append({
                "skill": skill,
                "title": course["title"],
                "link": course["link"]
            })
        else:
            # Default Udemy fallback if not found in specific database
            udemy_search = f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}&src=sac"
            course_suggestions_list.append({
                "skill": skill,
                "title": f"Learn {skill} on Udemy",
                "link": udemy_search
            })
    return course_suggestions_list

def suggest_courses_for_skills(missing_skills_list):
    """
    Suggests courses or learning platforms for given missing skills using the new suggest_courses function.
    """
    st.subheader("📚 Suggested Courses for Missing Skills")
    if not missing_skills_list:
        st.info("Great! You have no significant missing skills based on the Job Description.")
        return

    st.write("Based on the skills missing from your resume compared to the Job Description, here are some suggested courses or learning resources:")
    
    # Use the new suggest_courses function to get the formatted list
    suggestions = suggest_courses(missing_skills_list)
    
    found_suggestions = False
    suggested_count = 0
    for suggestion in suggestions:
        if suggested_count >= 5: # Limit to 5 courses
            break
        st.markdown(f"- **{suggestion['skill']}:** [{suggestion['title']}]({suggestion['link']})")
        found_suggestions = True
        suggested_count += 1

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

def resume_screener_page():
    st.title("🧠 ScreenerPro – AI-Powered Resume Screener")

    all_master_skills = sorted(list(MASTER_SKILLS)) 

    # Removed st.session_state initializations for filters
    # if 'screening_cutoff_score' not in st.session_state:
    #     st.session_state['screening_cutoff_score'] = 75
    # if 'screening_min_experience' not in st.session_state:
    #     st.session_state['screening_min_experience'] = 2
    # if 'screening_max_experience' not in st.session_state:
    #     st.session_state['screening_max_experience'] = 10
    # if 'screening_min_cgpa' not in st.session_state:
    #     st.session_state['screening_min_cgpa'] = 2.5
    
    if 'certificate_html_content' not in st.session_state:
        st.session_state['certificate_html_content'] = ""
    if 'show_certificate_preview' not in st.session_state:
        st.session_state['show_certificate_preview'] = False


    st.markdown("## ⚙️ Define Job Requirements & Screening Criteria")
    col1, col2 = st.columns([2, 1])

    with col1:
        jd_text = ""
        job_roles = {"Upload my own": None}
        if os.path.exists("data"): # Assuming 'data' directory for pre-loaded JDs
            for fname in os.listdir("data"):
                if fname.endswith(".txt"):
                    job_roles[fname.replace(".txt", "").replace("_", " ").title()] = os.path.join("data", fname)

        jd_option = st.selectbox("📌 **Select a Pre-Loaded Job Role or Upload Your Own Job Description**", list(job_roles.keys()))
        
        jd_name_for_results = ""
        if jd_option == "Upload my own":
            jd_file = st.file_uploader("Upload Job Description (TXT, PDF)", type=["txt", "pdf"], help="Upload a .txt or .pdf file containing the job description.")
            if jd_file:
                jd_text = extract_text_from_file(jd_file.read(), jd_file.name, jd_file.type)
                jd_name_for_results = jd_file.name.replace('.pdf', '').replace('.txt', '')
            else:
                jd_name_for_results = "Uploaded JD (No file selected)"
        else:
            jd_path = job_roles[jd_option]
            if jd_path and os.path.exists(jd_path):
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            jd_name_for_results = jd_option

        if jd_text:
            with st.expander("📝 View Loaded Job Description"):
                st.text_area("Job Description Content", jd_text, height=200, disabled=True, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("## ☁️ Job Description Keyword Cloud")
            st.caption("Visualizing the most frequent and important keywords from the Job Description.")
            st.info("💡 To filter candidates by these skills, use the 'Filter Candidates by Skill' section below the main results table.")
            
            jd_words_for_cloud_set, _ = extract_relevant_keywords(jd_text, all_master_skills)
            jd_words_for_cloud = " ".join(list(jd_words_for_cloud_set))

            if jd_words_for_cloud:
                wordcloud = WordCloud(width=800, height=400, background_color='white', collocations=False).generate(jd_words_for_cloud)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No significant keywords to display for the Job Description. Please ensure your JD has sufficient content or adjust your SKILL_CATEGORIES list.")
            st.markdown("---")


    # Removed the entire col2 block, as it contained all the filters
    # with col2:
    #     cutoff = st.slider("📈 **Minimum Score Cutoff (%)**", 0, 100, 75, key="min_score_cutoff_slider", help="Candidates scoring below this percentage will be flagged for closer review or considered less suitable.")
    #     st.session_state['screening_cutoff_score'] = cutoff

    #     min_experience = st.slider("💼 **Minimum Experience Required (Years)**", 0, 15, 2, key="min_exp_slider", help="Candidates with less than this experience will be noted.")
    #     st.session_state['screening_min_experience'] = min_experience

    #     max_experience = st.slider("⬆️ **Maximum Experience Allowed (Years)**", 0, 20, 10, key="max_exp_slider", help="Candidates with more than this experience might be considered overqualified or outside the target range.")
    #     st.session_state['screening_max_experience'] = max_experience

    #     min_cgpa = st.slider("🎓 **Minimum CGPA Required (4.0 Scale)**", 0.0, 4.0, 2.5, 0.1, key="min_cgpa_slider", help="Candidates with CGPA below this value (normalized to 4.0) will be noted.")
    #     st.session_state['screening_min_cgpa'] = min_cgpa

    #     st.markdown("---")
    #     st.info("Once criteria are set, upload your resume below to begin screening.")

    st.markdown("## 🎯 Skill Prioritization (Optional)")
    st.caption("Assign higher importance to specific skills in the Job Description.")
    
    all_master_skills = sorted(list(MASTER_SKILLS)) 
    col_weights_1, col_weights_2 = st.columns(2)
    with col_weights_1:
        high_priority_skills = st.multiselect(
            "🌟 **High Priority Skills (Weight x3)**",
            options=all_master_skills,
            help="Select skills that are absolutely critical for this role. These will significantly boost the score if found."
        )
    with col_weights_2:
        medium_priority_skills = st.multiselect(
            "✨ **Medium Priority Skills (Weight x2)**",
            options=[s for s in all_master_skills if s not in high_priority_skills],
            help="Select skills that are very important, but not as critical as high priority ones."
        )

    # --- NEW: Target Company Input ---
    st.markdown("## 🏢 Target Company Fit (Optional)")
    st.caption("Assess how well your resume aligns with a specific company's profile.")
    target_company_name = st.selectbox(
        "**Select a Target Company**",
        options=[""] + sorted(list(COMPANY_SKILL_PROFILES.keys())),
        help="Choose a company from the list to see how well your resume aligns with its typical profile. This is based on a simplified, predefined list of company keywords."
    )
    # --- END NEW: Target Company Input ---

    uploaded_resume_file = st.file_uploader("📄 **Upload Your Resume (PDF)**", type=["pdf"], help="Upload your resume (text-selectable PDF only). File must be less than 1MB.")
    
    if jd_text and uploaded_resume_file:
        total_screening_start_time = time.time()

        file_data_bytes = uploaded_resume_file.read()
        file_name = uploaded_resume_file.name
        file_type = uploaded_resume_file.type

        if uploaded_resume_file.size > 1 * 1024 * 1024: # 1MB limit
            st.error(f"❌ File '{file_name}' is too large ({uploaded_resume_file.size / (1024*1024):.2f} MB). Please upload files smaller than 1MB.")
            return

        with st.spinner(f"Extracting text from {file_name}..."):
            resume_text = extract_text_from_file(file_data_bytes, file_name, file_type)
        
        if resume_text.startswith("[ERROR]"):
            st.error(resume_text)
            return
        
        st.success("Text extraction complete.")

        with st.spinner(f"Generating embeddings for resume and JD..."):
            jd_clean = clean_text(jd_text)
            jd_embedding = global_sentence_model.encode([jd_clean])[0]
            
            resume_embedding = global_sentence_model.encode([resume_text])[0]
        
        st.success("Embedding generation complete.")

        with st.spinner(f"Analyzing your resume with AI models..."):
            # Fixed max_experience to a default value since the slider is removed
            default_max_experience = 15 
            result = _process_single_resume_for_screener_page(
                file_name, resume_text, jd_text, jd_embedding, resume_embedding,
                jd_name_for_results, high_priority_skills, medium_priority_skills, default_max_experience,
                global_ml_model, target_company_name # Pass target_company_name
            )
            
        st.success("Resume analysis complete. Displaying your results.")
        
        total_screening_end_time = time.time()
        st.info(f"Total screening time: {total_screening_end_time - total_screening_start_time:.2f} seconds.")

        st.markdown("---")
        st.markdown("## 👑 Your AI Assessment")
        st.caption("A detailed, AI-powered assessment of your resume against the job requirements.")
        
        if result:
            candidate_data = result
            
            cgpa_display = f"{candidate_data['CGPA (4.0 Scale)']:.2f}" if pd.notna(candidate_data['CGPA (4.0 Scale)']) else "N/A"
            semantic_sim_display = f"{candidate_data['Semantic Similarity']:.2f}" if pd.notna(candidate_data['Semantic Similarity']) else "N/A"

            st.markdown(f"### **{candidate_data['Candidate Name']}**")
            st.markdown(f"**Score:** {candidate_data['Score (%)']:.2f}% | **Experience:** {candidate_data['Years Experience']:.1f} years | **CGPA:** {cgpa_display} (4.0 Scale) | **Semantic Similarity:** {semantic_sim_display}")
            
            if candidate_data.get('Certificate Rank') != "Not Applicable" and candidate_data['Score (%)'] >= 50:
                st.markdown(f"**ScreenerPro Certification:** {candidate_data['Certificate Rank']}")

            st.markdown(f"**Overall AI Assessment:**")
            st.markdown(candidate_data['Detailed HR Assessment'])
            
            # --- NEW: Display Company Fit Assessment ---
            st.markdown("---")
            st.markdown("## 🏢 Company Fit Assessment")
            st.markdown(candidate_data['Company Fit Assessment'])
            # --- END NEW: Display Company Fit Assessment ---

            st.markdown("#### Matched Skills Breakdown:")
            matched_kws_categorized_str = candidate_data['Matched Keywords (Categorized)']
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
            # Defensive checks for sets before performing set operations
            jd_raw_skills_set_for_display, jd_categorized_skills_for_top = extract_relevant_keywords(jd_text, all_master_skills)
            resume_raw_skills_set_for_top, _ = extract_relevant_keywords(candidate_data['Resume Raw Text'], all_master_skills)

            if not isinstance(jd_raw_skills_set_for_display, set):
                print(f"DEBUG: jd_raw_skills_set_for_display is not a set. Type: {type(jd_raw_skills_set_for_display)}. Defaulting to empty set.")
                jd_raw_skills_set_for_display = set()
            if not isinstance(resume_raw_skills_set_for_top, set):
                print(f"DEBUG: resume_raw_skills_set_for_top is not a set. Type: {type(resume_raw_skills_set_for_top)}. Defaulting to empty set.")
                resume_raw_skills_set_for_top = set()
            
            missing_skills_for_current = list(jd_raw_skills_set_for_display.difference(resume_raw_skills_set_for_top))
            
            if missing_skills_for_current:
                missing_categorized = collections.defaultdict(list)
                for skill in missing_skills_for_current:
                    found_category = False
                    for category, skills_in_category in SKILL_CATEGORIES.items():
                        if skill.lower() in [s.lower() for s in skills_in_category]:
                            missing_categorized[category].append(skill)
                            found_category = True
                            break
                    if not found_category:
                        missing_categorized["Uncategorized"].append(skill)
                
                if missing_categorized:
                    for category, skills in missing_categorized.items():
                        st.write(f"**{category}:** {', '.join(skills)}")
                else:
                    st.write("No categorized missing skills found for this candidate relative to the JD.")
            else:
                st.write("No missing skills found for this candidate relative to the JD.") 
            
            st.markdown("---")
            # Course Suggestions based on missing skills
            suggest_courses_for_skills(missing_skills_for_current)
            st.markdown("---")

            # --- Certificate Display and Email Logic (Conditional on Score >= 50) ---
            if candidate_data.get('Certificate Rank') != "Not Applicable" and candidate_data['Score (%)'] >= 50:
                st.markdown("## 🏆 Your ScreenerPro Certificate")
                st.caption("Congratulations! Here is your certificate. It has also been sent to your email.")

                # Generate HTML content for the certificate
                certificate_html_content = generate_certificate_html(candidate_data)
                st.session_state['certificate_html_content'] = certificate_html_content # Store for display

                # Construct the public URL for the certificate (if you plan to host them)
                # For this implementation, the PDF is generated on-the-fly for download/email.
                # If you need to host PDFs, you'd need a separate storage mechanism (e.g., AWS S3, GitHub Pages for PDFs).
                certificate_public_url = f"{CERTIFICATE_HOSTING_URL}certificates/{candidate_data['Certificate ID']}.html" # Changed to .html extension, added /certificates/ path

                # --- Automatic Email Sending ---
                candidate_email = candidate_data.get('Email')
                if candidate_email and candidate_email != "Not Found":
                    # Check if email has already been sent for this session and candidate
                    email_sent_key = f"email_sent_{candidate_data['Certificate ID']}"
                    if not st.session_state.get(email_sent_key, False):
                        with st.spinner(f"Sending certificate to {candidate_email}..."):
                            gmail_address = st.secrets.get("GMAIL_ADDRESS")
                            gmail_app_password = st.secrets.get("GMAIL_APP_PASSWORD")
                            
                            if send_certificate_email(
                                candidate_email, 
                                candidate_data['Candidate Name'], 
                                candidate_data['Score (%)'], 
                                certificate_html_content, # Pass HTML content for email body
                                certificate_public_url, # Pass public URL
                                gmail_address, 
                                gmail_app_password
                            ):
                                st.session_state[email_sent_key] = True # Mark as sent
                            else:
                                st.warning(f"Could not send email to {candidate_email}. Please check email configuration.")
                else:
                    st.warning("Candidate email not found in resume. Cannot send certificate via email.")


                col_cert_download, col_share_linkedin, col_share_whatsapp = st.columns(3)
                
                with col_cert_download:
                    # Download button for HTML file
                    st.download_button(
                        label="⬇️ Download Certificate (HTML)",
                        data=certificate_html_content.encode('utf-8'), # Encode HTML string to bytes
                        file_name=f"ScreenerPro_Certificate_{candidate_data['Candidate Name'].replace(' ', '_')}.html",
                        mime="text/html",
                        key="download_cert_button",
                        help="Download the certificate as an HTML file. You can open it in your browser and use 'Print to PDF' to save it as a PDF."
                    )
                
                # Share message for social media
                share_message = f"""I just received a Certificate of Screening Excellence from ScreenerPro! 🏆
After uploading my resume, I was evaluated across multiple hiring parameters using AI-powered screening technology.

I'm happy to share that I scored above {candidate_data['Score (%)']:.1f}%, which reflects the strength of my profile in today's job market.
View my certificate online: {certificate_public_url}

Thanks to the team at ScreenerPro for building such a transparent and insightful platform for job seekers!

#resume #jobsearch #ai #caregrowth #certified #ScreenerPro #LinkedIn
🌐 Learn more about the tool: For candidate login: {urllib.parse.quote(APP_BASE_URL)} and for HR login: {urllib.parse.quote(APP_BASE_URL)}
"""
                
                # LinkedIn Share Button (now shares the public certificate URL)
                linkedin_share_url = f"https://www.linkedin.com/shareArticle?mini=true&url={urllib.parse.quote(certificate_public_url)}&title={urllib.parse.quote('ScreenerPro Certificate of Excellence')}&summary={urllib.parse.quote(share_message)}"
                with col_share_linkedin:
                    st.markdown(f'<a href="{linkedin_share_url}" target="_blank"><button style="background-color:#0077B5;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">Share on LinkedIn</button></a>', unsafe_allow_html=True)

                # WhatsApp Share Button (now shares the public certificate URL)
                whatsapp_share_url = f"https://wa.me/?text={urllib.parse.quote(share_message)}"
                with col_share_whatsapp:
                    st.markdown(f'<a href="{whatsapp_share_url}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">Share on WhatsApp</button></a>', unsafe_allow_html=True)

                # --- Firestore Save for Leaderboard (using REST API) ---
                # This will attempt to save the data via REST API
                save_screening_result_to_firestore_rest(candidate_data)
                # --- End of Firestore save section ---

                # --- Automatic HTML Preview Display ---
                st.markdown("---")
                st.markdown("### Generated Certificate Preview (HTML)")
                st.components.v1.html(st.session_state['certificate_html_content'], height=1200, scrolling=False) 
                st.markdown("---")

            else:
                if candidate_data['Score (%)'] < 50:
                    st.info(f"Your score of {candidate_data['Score (%)']:.2f}% is below the 50% threshold for certificate issuance. Keep improving!")
                else:
                    st.info(f"{candidate_data['Candidate Name']} does not qualify for a ScreenerPro Certificate at this time.")
        else:
            st.info("No results to display for the candidate.")

    # This block ensures the preview is hidden if the input is cleared or no resume is uploaded
    if not uploaded_resume_file and st.session_state['certificate_html_content']:
        st.session_state['certificate_html_content'] = ""
        st.rerun() # Rerun to clear the display immediately

if __name__ == "__main__":
    st.set_page_config(page_title="ScreenerPro Resume Screener", layout="wide")
    resume_screener_page()
