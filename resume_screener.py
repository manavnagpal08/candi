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
from sentence_transformers import SentenceTransformer, util
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

# Define SKILL_LIST for the new functions
SKILL_LIST = MASTER_SKILLS

# Re-added: Company Skill Profiles (placeholder structure)
# IMPORTANT: You will need to populate this dictionary with actual skills relevant to each company.
# Example: "Google": ["Python", "Machine Learning", "TensorFlow", "Distributed Systems"]
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
        "keywords": ["AWS", "Java", "Python", "Distributed Systems", "Microservices", "Cloud Computing", "SQL", "NoSQL", "Leadership", "Problem Solving", "Serverless", "DynamoDB", "S3", "Lambda", "EC2", "E-commerce", "Logistics", "Machine Learning", "Alexa", "Data Engineering", "Supply Chain", "Retail Tech", "Fulfillment", "Prime Video", "Kindle", "Robotics (Warehouse)", "Natural Language Processing (NLP)", "Computer Vision"]
    },
    "Meta (Facebook)": {
        "description": "A technology conglomerate focusing on social media, virtual reality, and artificial intelligence.",
        "keywords": ["React", "PyTorch", "GraphQL", "AI", "Machine Learning", "Virtual Reality (VR)", "Augmented Reality (AR)", "Social Media", "Data Science", "Python", "PHP", "Distributed Systems", "Mobile Development", "Computer Vision", "Privacy", "Content Moderation", "Recommendation Engines", "AdTech", "Horizon Worlds", "Ray-Ban Meta Smart Glasses"]
    },
    "Apple": {
        "description": "A multinational technology company focusing on consumer electronics, software, and online services.",
        "keywords": ["Swift", "Objective-C", "iOS Development", "macOS Development", "User Experience (UX)", "Product Design", "Hardware Integration", "Privacy", "Security", "iOS", "Xcode", "Mobile Development", "Hardware Engineering", "Design Thinking", "AI (Siri)", "Cloud (iCloud)", "WatchOS", "iPadOS", "tvOS", "Apple Silicon", "HealthKit", "ARKit", "Apple Pay", "App Store", "Services Revenue"]
    },
    "Netflix": {
        "description": "A streaming service and production company.",
        "keywords": ["Python", "AWS", "Microservices", "Data Science", "Machine Learning", "Distributed Systems", "Streaming Technologies", "Recommendation Systems", "Cloud Computing", "Cloud Native", "DevOps", "Big Data", "User Experience (UX)", "Content Delivery Networks (CDN)", "Video Encoding", "Personalization", "A/B Testing", "Chaos Engineering"]
    },
    "Salesforce": {
        "description": "A cloud-based software company providing customer relationship management (CRM) service.",
        "keywords": ["Salesforce CRM", "Apex", "Visualforce", "Lightning Web Components", "Cloud Computing", "SaaS", "Customer Relationship Management", "JavaScript", "API Integration", "CRM", "Integration (MuleSoft)", "Platform Development", "Marketing Cloud", "Service Cloud", "Einstein AI", "Tableau", "Slack"]
    },
    "IBM": {
        "description": "An American multinational technology and consulting company, specializing in computer hardware, middleware, and software.",
        "keywords": ["Java", "Python", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Blockchain", "Cybersecurity", "Enterprise Software", "Consulting", "Cloud Computing (IBM Cloud)", "AI (Watson)", "Enterprise Solutions", "Quantum Computing", "Hybrid Cloud", "Data Analytics", "Linux", "Mainframe", "Red Hat", "OpenShift", "Automation (RPA)", "IT Services", "Storage Solutions", "Server Technologies"]
    },
    "Oracle": {
        "description": "A multinational computer technology corporation best known for its database software and cloud engineered systems.",
        "keywords": ["Java", "SQL", "Oracle Database", "Cloud Computing", "Enterprise Software", "ERP", "CRM", "Data Warehousing", "Middleware", "Cloud Infrastructure (OCI)", "Fusion Applications", "NetSuite", "Peoplesoft", "Supply Chain Management"]
    },
    "Accenture": {
        "description": "A leading global professional services company, providing a broad range of services and solutions in strategy, consulting, digital, technology and operations.",
        "keywords": ["Consulting", "Project Management", "Change Management", "Digital Transformation", "Cloud Computing", "Data Analytics", "Strategy", "Business Process Improvement", "IT Strategy", "System Integration", "Enterprise Architecture", "Cybersecurity Consulting", "AI Consulting", "Blockchain Consulting"]
    },
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
    "Capgemini": {
        "description": "A global leader in consulting, technology services, and digital transformation.",
        "keywords": ["Consulting", "IT Services", "Digital Transformation", "Cloud Computing", "AI", "Data Analytics", "Cybersecurity", "Application Services", "DevOps", "Agile", "SAP", "Oracle", "Industry Expertise", "Intelligent Automation", "Customer Experience"]
    },
    "Cognizant": {
        "description": "A global information technology services and consulting company.",
        "keywords": ["IT Consulting", "Digital Strategy", "Cloud Solutions", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Application Development", "Business Process Services", "Industry Solutions", "DevOps", "Agile", "Digital Engineering", "Enterprise Transformation"]
    },
    "Tech Mahindra": {
        "description": "An Indian multinational information technology services and consulting company.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Cybersecurity", "Network Services", "Business Process Services", "Enterprise Applications", "Engineering Services", "Blockchain", "5G", "IoT", "Robotics", "Telecommunications", "CRM Services", "Data Analytics"]
    },
    "LTIMindtree": {
        "description": "An Indian multinational information technology services and consulting company, formed by the merger of L&T Infotech and Mindtree.",
        "keywords": ["IT Services", "Digital Transformation", "Cloud Computing", "Data & Analytics", "Generative AI", "Application Development", "Cybersecurity", "Enterprise Solutions", "IoT", "DevOps", "Agile", "Consulting", "Product Engineering", "Customer Experience (CX)", "SAP", "Oracle"]
    },
    "Persistent Systems": {
        "description": "A global services company that provides software product development and technology services.",
        "keywords": ["Product Engineering", "Digital Engineering", "Cloud Native", "Data & AI", "Enterprise Modernization", "Software Development", "Agile", "DevOps", "Banking & Financial Services (BFS)", "Healthcare Tech", "Life Sciences", "IoT Solutions"]
    },
    "Mphasis": {
        "description": "A global information technology solutions provider specializing in cloud and cognitive services.",
        "keywords": ["Cloud Transformation", "AI", "Cognitive Technologies", "Digital Transformation", "DevOps", "Automation", "Cybersecurity", "Data Analytics", "IT Services", "Blockchain", "Application Modernization", "Financial Services Tech"]
    },
    "Coforge": {
        "description": "A global IT solutions organization enabling businesses to transform with digital technologies.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions", "Automation", "Cybersecurity", "Application Development", "Microservices", "API Management", "Travel Tech", "Financial Services"]
    },
    "Zensar Technologies": {
        "description": "A global technology services company, providing digital solutions and technology consulting.",
        "keywords": ["Digital Transformation", "Cloud Services", "AI", "Machine Learning", "Data Analytics", "Cybersecurity", "Enterprise Applications", "DevOps", "Agile", "Robotics Process Automation (RPA)"]
    },
    "Cyient": {
        "description": "A global engineering and technology solutions company.",
        "keywords": ["Engineering Services", "Geospatial", "IoT", "Data Analytics", "Aerospace", "Automotive", "Medical Devices", "Manufacturing", "Digital Engineering", "Product Design"]
    },
    "L&T Technology Services": {
        "description": "A global pure-play engineering research and development services company.",
        "keywords": ["Engineering Services", "Digital Engineering", "IoT", "AI", "Machine Learning", "Embedded Systems", "Automotive", "Aerospace", "Medical Devices", "Manufacturing Automation", "Product Development"]
    },
    "Firstsource Solutions": {
        "description": "A global provider of business process management (BPM) services.",
        "keywords": ["Customer Experience", "Business Process Management", "Digital Transformation", "Data Analytics", "Healthcare BPO", "Financial Services BPO", "Telecom BPO", "Robotics Process Automation (RPA)", "AI in CX"]
    },
    "ExlService Holdings": {
        "description": "A global analytics and digital operations and solutions company.",
        "keywords": ["Data Analytics", "AI", "Machine Learning", "Digital Transformation", "Operations Management", "Finance & Accounting BPO", "Healthcare Analytics", "Insurance Analytics", "Business Process Optimization"]
    },
    "Genpact": {
        "description": "A global professional services firm focused on delivering digital transformation and business process management.",
        "keywords": ["Digital Transformation", "Business Process Management (BPM)", "AI & Automation", "Data Analytics", "Financial Services Operations", "Supply Chain Management", "Risk & Compliance", "Robotics Process Automation (RPA)", "Consulting"]
    },
    "Concentrix": {
        "description": "A global provider of customer experience (CX) solutions and technology.",
        "keywords": ["Customer Experience", "Business Process Management", "Digital Transformation", "Contact Center", "CX Consulting", "Sales", "Marketing", "AI in CX", "Automation"]
    },
    "Teleperformance": {
        "description": "A global leader in omnichannel customer experience management.",
        "keywords": ["Customer Experience", "Omnichannel Solutions", "Digital Transformation", "Contact Center", "Business Process Outsourcing", "AI in CX", "Customer Support"]
    },
    "Conduent": {
        "description": "A global business process services company.",
        "keywords": ["Business Process Solutions", "Digital Platforms", "Healthcare BPS", "Transportation Solutions", "Government Services", "Commercial Industries", "Payment Solutions", "HR Services"]
    },
    "Sutherland": {
        "description": "A global process transformation company.",
        "keywords": ["Digital Transformation", "Customer Experience", "Business Process Transformation", "AI", "Automation", "Healthcare BPS", "Financial Services BPS", "Retail BPS", "Robotics Process Automation (RPA)"]
    },
    "Startek": {
        "description": "A global provider of customer experience management solutions.",
        "keywords": ["Customer Experience", "Omnichannel Solutions", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Transcom": {
        "description": "A global customer experience specialist.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Alorica": {
        "description": "A global leader in customer experience solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "TTEC": {
        "description": "A global customer experience technology and services company.",
        "keywords": ["Customer Experience", "Digital Transformation", "Contact Center", "AI", "Automation", "Consulting", "Customer Engagement"]
    },
    "VXI Global Solutions": {
        "description": "A global leader in customer care and customer experience (CX) solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "Sitel Group": {
        "description": "A global leader in customer experience products and solutions.",
        "keywords": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing", "Customer Support"]
    },
    "TaskUs": {
        "description": "A leading provider of digital customer experience, content security, and AI operations.",
        "keywords": ["Digital Customer Experience", "Content Moderation", "AI Operations", "Gaming Support", "Fintech Support", "E-commerce Support", "Trust & Safety"]
    },
    "Arise Virtual Solutions": {
        "description": "A leading platform for crowdsourced customer service.",
        "keywords": ["Virtual Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions", "Gig Economy"]
    },
    "LiveOps": {
        "description": "A cloud contact center platform for remote agents.",
        "keywords": ["Cloud Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions", "Remote Operations"]
    },
    "Modis": {
        "description": "A global leader in professional solutions, specializing in IT and engineering.",
        "keywords": ["IT Consulting", "Digital Transformation", "Talent Solutions", "Cloud", "Cybersecurity", "Data & AI", "Engineering Services"]
    },
    "TEKsystems": {
        "description": "A leading provider of IT staffing solutions, IT services and talent management expertise.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Management"]
    },
    "Insight Global": {
        "description": "A national staffing and services company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Robert Half Technology": {
        "description": "A leading provider of IT professionals on a contract, contract-to-hire and permanent basis.",
        "keywords": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Kforce": {
        "description": "A professional staffing and solutions firm specializing in Technology and Finance & Accounting.",
        "keywords": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Finance & Accounting Staffing"]
    },
    "Apex Systems": {
        "description": "A leading IT staffing and services firm.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Collabera": {
        "description": "A global IT staffing and services company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Hays": {
        "description": "A leading global professional recruiting group.",
        "keywords": ["IT Staffing", "IT Recruitment", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Michael Page": {
        "description": "A leading professional recruitment consultancy specializing in IT.",
        "keywords": ["IT Recruitment", "IT Staffing", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Acquisition"]
    },
    "Randstad Technologies": {
        "description": "A leading provider of IT talent and solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Talent Solutions"]
    },
    "Adecco": {
        "description": "A global leader in human resource solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "HR Solutions"]
    },
    "Kelly Services": {
        "description": "A global leader in providing workforce solutions.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Workforce Solutions"]
    },
    "ManpowerGroup": {
        "description": "A global workforce solutions company.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Workforce Solutions"]
    },
    "Aerotek": {
        "description": "A leading recruiting and staffing agency.",
        "keywords": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI", "Staffing Solutions"]
    },
    "CDW": {
        "description": "A leading provider of technology solutions to business, government, education and healthcare.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Hardware", "Software"]
    },
    "Insight Enterprises": {
        "description": "A Fortune 500 global technology provider of hardware, software, cloud, and service solutions.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "Presidio": {
        "description": "A global digital services and solutions provider.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "ePlus": {
        "description": "A leading provider of technology solutions.",
        "keywords": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services", "Digital Transformation"]
    },
    "Optiv": {
        "description": "A leading cybersecurity solutions and services company.",
        "keywords": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security", "Security Operations"]
    },
    "Herjavec Group": {
        "description": "A global cybersecurity advisory firm and managed security services provider.",
        "keywords": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security", "Incident Response"]
    },
    "Rapid7": {
        "description": "A leading provider of security analytics and automation.",
        "keywords": ["Vulnerability Management", "Security Operations", "Application Security", "Cloud Security", "Threat Intelligence", "Incident Response"]
    },
    "Tenable": {
        "description": "A leading provider of Cyber Exposure solutions.",
        "keywords": ["Vulnerability Management", "Cyber Exposure", "OT Security", "Cloud Security", "Web Application Security", "Attack Surface Management"]
    },
    "Qualys": {
        "description": "A pioneer and leading provider of cloud-based security and compliance solutions.",
        "keywords": ["Vulnerability Management", "Cloud Security", "Web Application Security", "Compliance", "Asset Management", "Security Audits"]
    },
    "CrowdStrike": {
        "description": "A leader in cloud-native endpoint protection.",
        "keywords": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "Managed Detection and Response (MDR)", "XDR"]
    },
    "SentinelOne": {
        "description": "A leading provider of AI-powered endpoint security.",
        "keywords": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "XDR", "AI in Security"]
    },
    "Palo Alto Networks": {
        "description": "A global cybersecurity leader.",
        "keywords": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention", "Firewalls", "AI in Security"]
    },
    "Fortinet": {
        "description": "A global leader in broad, integrated, and automated cybersecurity solutions.",
        "keywords": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention", "Firewalls", "SD-WAN"]
    },
    "Cisco": {
        "description": "An American multinational digital communications technology conglomerate corporation.",
        "keywords": ["Networking", "Cybersecurity", "Collaboration", "Cloud", "Data Center", "IoT", "Routers", "Switches", "Webex", "Meraki"]
    },
    "Juniper Networks": {
        "description": "A global leader in networking innovations.",
        "keywords": ["Networking", "Cloud", "AI-driven Enterprise", "Security", "Automation", "Routers", "Switches", "SD-WAN"]
    },
    "VMware": {
        "description": "A cloud computing and virtualization technology company, now part of Broadcom.",
        "keywords": ["Virtualization", "Cloud Computing", "Network Virtualization", "Security", "Digital Workspace", "SDDC", "NSX", "vSAN", "Tanzu", "Kubernetes"]
    },
    "Citrix": {
        "description": "A company providing digital workspace, networking, and analytics solutions.",
        "keywords": ["Virtualization", "Cloud Computing", "Digital Workspace", "Networking", "Security", "VDI", "Application Delivery"]
    },
    "Red Hat": {
        "description": "A leading provider of open source software solutions.",
        "keywords": ["Open Source", "Linux", "Cloud Computing", "Kubernetes", "Automation", "Middleware", "DevOps", "OpenShift", "Ansible"]
    },
    "SUSE": {
        "description": "A global leader in open source software, specializing in Linux, Kubernetes, and Edge solutions.",
        "keywords": ["Open Source", "Linux", "Kubernetes", "Cloud Computing", "Edge Computing", "Storage", "Rancher"]
    },
    "Canonical (Ubuntu)": {
        "description": "The company behind Ubuntu, a popular open-source operating system.",
        "keywords": ["Open Source", "Linux", "Cloud Computing", "IoT", "AI/ML", "Containers", "Ubuntu", "Kubernetes"]
    },
    "MongoDB": {
        "description": "A leading NoSQL database provider.",
        "keywords": ["NoSQL Database", "Document Database", "Cloud Database", "Atlas", "Enterprise Advanced", "Data Modeling (NoSQL)"]
    },
    "Databricks": {
        "description": "A company providing a cloud-based data lakehouse platform for data science and AI.",
        "keywords": ["Data Lakehouse", "Spark", "AI/ML", "Data Engineering", "Data Science", "Delta Lake", "MLflow", "Lakehouse Architecture", "Python", "Scala", "SQL"]
    },
    "Snowflake": {
        "description": "A cloud-based data warehousing company offering a data cloud platform.",
        "keywords": ["Cloud Data Warehouse", "Data Lake", "Data Sharing", "Data Marketplace", "Data Applications", "SQL", "Data Governance"]
    },
    "Teradata": {
        "description": "A leading provider of pervasive data intelligence.",
        "keywords": ["Enterprise Data Warehouse", "Cloud Data Analytics", "Hybrid Cloud", "AI/ML Integration", "Data Management"]
    },
    "Cloudera": {
        "description": "A hybrid data cloud company.",
        "keywords": ["Data Cloud", "Data Management", "Data Analytics", "Machine Learning", "Hybrid Cloud", "Open Source", "Hadoop", "Spark"]
    },
    "Confluent": {
        "description": "A company providing an event streaming platform based on Apache Kafka.",
        "keywords": ["Kafka", "Event Streaming Platform", "Data in Motion", "Cloud-Native", "Real-Time Data", "Apache Kafka"]
    },
    "Elastic (Elasticsearch)": {
        "description": "A company behind the Elastic Stack (Elasticsearch, Kibana, Logstash, Beats).",
        "keywords": ["Search Engine", "Analytics Engine", "Observability", "Security", "Elastic Stack", "Kibana", "Logstash", "Elasticsearch"]
    },
    "Redis Labs": {
        "description": "A company providing Redis Enterprise, an in-memory database platform.",
        "keywords": ["In-Memory Database", "NoSQL", "Caching", "Real-Time Data", "Redis Enterprise", "Redis"]
    },
    "Neo4j": {
        "description": "A leading graph database platform.",
        "keywords": ["Graph Database", "Graph Analytics", "Knowledge Graphs", "AI/ML", "Cypher"]
    },
    "InfluxData (InfluxDB)": {
        "description": "A company providing InfluxDB, a time series database.",
        "keywords": ["Time Series Database", "IoT", "Monitoring", "Analytics", "Cloud-Native", "InfluxDB"]
    },
    "Timescale (TimescaleDB)": {
        "description": "A company providing TimescaleDB, a PostgreSQL extension for time series data.",
        "keywords": ["Time Series Database", "PostgreSQL Extension", "IoT", "Analytics", "Cloud-Native", "TimescaleDB"]
    },
    "Vertica": {
        "description": "A columnar database for analytics.",
        "keywords": ["Columnar Database", "Analytics Database", "Data Warehousing", "Big Data Analytics"]
    },
    "ClickHouse": {
        "description": "An open-source columnar database for analytical queries.",
        "keywords": ["Columnar Database", "Analytics Database", "Real-Time Analytics", "Big Data"]
    },
    "Pinecone": {
        "description": "A vector database for AI applications.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Weaviate": {
        "description": "An open-source vector database.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Knowledge Graphs", "Semantic Search"]
    },
    "Milvus": {
        "description": "An open-source vector database for AI applications.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Similarity Search"]
    },
    "Qdrant": {
        "description": "A vector similarity search engine.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Chroma": {
        "description": "An open-source AI-native embedding database.",
        "keywords": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"]
    },
    "Faiss": {
        "description": "A library for efficient similarity search and clustering of dense vectors.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Annoy": {
        "description": "A C++ library with Python bindings for approximate nearest neighbors.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Hnswlib": {
        "description": "A C++ library for approximate nearest neighbor search.",
        "keywords": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"]
    },
    "Scikit-learn": {
        "description": "A free software machine learning library for the Python programming language.",
        "keywords": ["Machine Learning Library", "Python", "Classification", "Regression", "Clustering"]
    },
    "TensorFlow": {
        "description": "An open-source machine learning framework developed by Google.",
        "keywords": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Google"]
    },
    "PyTorch": {
        "description": "An open-source machine learning library developed by Facebook AI Research.",
        "keywords": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Facebook AI"]
    },
    "Keras": {
        "description": "An open-source software library that provides a Python interface for artificial neural networks.",
        "keywords": ["Deep Learning API", "TensorFlow", "Neural Networks", "Rapid Prototyping"]
    },
    "XGBoost": {
        "description": "An optimized distributed gradient boosting library.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "LightGBM": {
        "description": "A gradient boosting framework that uses tree-based learning algorithms.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "CatBoost": {
        "description": "An open-source gradient boosting library developed by Yandex.",
        "keywords": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"]
    },
    "Statsmodels": {
        "description": "A Python module that provides classes and functions for the estimation of many different statistical models.",
        "keywords": ["Statistical Modeling", "Econometrics", "Python", "Statistical Tests"]
    },
    "NumPy": {
        "description": "A fundamental package for scientific computing with Python.",
        "keywords": ["Numerical Computing", "Python", "Arrays", "Matrices"]
    },
    "Pandas": {
        "description": "A software library written for the Python programming language for data manipulation and analysis.",
        "keywords": ["Data Manipulation", "Data Analysis", "Python", "DataFrames"]
    },
    "Matplotlib": {
        "description": "A plotting library for the Python programming language.",
        "keywords": ["Data Visualization", "Python", "Plotting"]
    },
    "Seaborn": {
        "description": "A Python data visualization library based on matplotlib.",
        "keywords": ["Statistical Data Visualization", "Python", "Matplotlib"]
    },
    "Plotly": {
        "description": "A graphing library for Python, R, and JavaScript.",
        "keywords": ["Interactive Data Visualization", "Web-based", "Dashboards"]
    },
    "Bokeh": {
        "description": "An interactive visualization library for modern web browsers.",
        "keywords": ["Interactive Data Visualization", "Web-based", "Python"]
    },
    "Dash": {
        "description": "A Python framework for building analytical web applications.",
        "keywords": ["Web Application Framework", "Python", "Plotly"]
    },
    "Flask": {
        "description": "A micro web framework for Python.",
        "keywords": ["Web Framework", "Python", "Microframework"]
    },
    "Django": {
        "description": "A high-level Python Web framework that encourages rapid development and clean, pragmatic design.",
        "keywords": ["Web Framework", "Python", "Full-stack"]
    },
    "FastAPI": {
        "description": "A modern, fast (high-performance) web framework for building APIs with Python.",
        "keywords": ["Web Framework", "Python", "High Performance", "API Development"]
    },
    "Spring Boot": {
        "description": "An open-source, microservice-based Java web framework.",
        "keywords": ["Java Framework", "Microservices", "Web Applications"]
    },
    ".NET Core": {
        "description": "A free, cross-platform, open-source managed computer software framework.",
        "keywords": ["Cross-platform Framework", "C#", "Web Applications", "APIs"]
    },
    "Node.js": {
        "description": "A JavaScript runtime built on Chrome's V8 JavaScript engine.",
        "keywords": ["JavaScript Runtime", "Backend Development", "Server-side"]
    },
    "Express.js": {
        "description": "A minimal and flexible Node.js web application framework.",
        "keywords": ["Node.js Web Framework", "Backend Development", "APIs"]
    },
    "React": {
        "description": "A JavaScript library for building user interfaces.",
        "keywords": ["JavaScript Library", "Frontend Development", "UI Components"]
    },
    "Angular": {
        "description": "A TypeScript-based open-source web application framework.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Single-page Applications"]
    },
    "Vue.js": {
        "description": "An open-source Model-View-ViewModel JavaScript framework for building user interfaces and single-page applications.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Progressive Web Apps"]
    },
    "Svelte": {
        "description": "A free, open-source JavaScript framework.",
        "keywords": ["JavaScript Framework", "Frontend Development", "Component Compiler"]
    },
    "jQuery": {
        "description": "A fast, small, and feature-rich JavaScript library.",
        "keywords": ["JavaScript Library", "DOM Manipulation", "Event Handling"]
    },
    "Bootstrap": {
        "description": "A free and open-source CSS framework directed at responsive, mobile-first front-end web development.",
        "keywords": ["CSS Framework", "Responsive Design", "UI Components"]
    },
    "Tailwind CSS": {
        "description": "A utility-first CSS framework for rapidly building custom user interfaces.",
        "keywords": ["CSS Framework", "Utility-first", "Rapid UI Development"]
    },
    "Sass": {
        "description": "A preprocessor scripting language that is interpreted or compiled into CSS.",
        "keywords": ["CSS Preprocessor", "CSS Extensions"]
    },
    "Less": {
        "description": "A dynamic stylesheet language that extends CSS.",
        "keywords": ["CSS Preprocessor", "CSS Extensions"]
    },
    "Webpack": {
        "description": "A static module bundler for modern JavaScript applications.",
        "keywords": ["Module Bundler", "JavaScript Applications"]
    },
    "Babel": {
        "description": "A free and open-source JavaScript transpiler.",
        "keywords": ["JavaScript Compiler", "Transpiler"]
    },
    "npm": {
        "description": "The default package manager for the JavaScript runtime environment Node.js.",
        "keywords": ["Node Package Manager", "JavaScript Packages"]
    },
    "Yarn": {
        "description": "A fast, reliable, and secure dependency management tool.",
        "keywords": ["Package Manager", "JavaScript Packages"]
    },
    "Ansible": {
        "description": "An open-source software provisioning, configuration management, and application-deployment tool.",
        "keywords": ["Automation Engine", "IT Automation", "Configuration Management"]
    },
    "Terraform": {
        "description": "An open-source infrastructure as code software tool.",
        "keywords": ["Infrastructure as Code", "Cloud Provisioning", "Multi-cloud"]
    },
    "Jenkins": {
        "description": "An open-source automation server.",
        "keywords": ["CI/CD", "Automation Server", "Build Automation"]
    },
    "GitLab CI/CD": {
        "description": "A part of GitLab that allows for continuous integration, delivery, and deployment.",
        "keywords": ["CI/CD", "GitLab Integration", "DevOps Platform"]
    },
    "GitHub Actions": {
        "description": "A CI/CD platform that allows you to automate your build, test, and deployment pipeline.",
        "keywords": ["CI/CD", "GitHub Integration", "Workflow Automation"]
    },
    "AWS CodeBuild": {
        "description": "A fully managed continuous integration service that compiles source code, runs tests, and produces software packages that are ready to deploy.",
        "keywords": ["CI/CD", "Build Service", "AWS"]
    },
    "AWS CodePipeline": {
        "description": "A fully managed continuous delivery service that helps you automate your release pipelines.",
        "keywords": ["CI/CD", "Release Automation", "AWS"]
    },
    "AWS CodeDeploy": {
        "description": "A service that automates code deployments to any instance, including Amazon EC2 instances and on-premises servers.",
        "keywords": ["Deployment Service", "Automated Deployments", "AWS"]
    },
    "AWS Lambda": {
        "description": "A serverless, event-driven compute service.",
        "keywords": ["Serverless Computing", "Function as a Service", "AWS"]
    },
    "Azure Functions": {
        "description": "A serverless compute service that enables you to run small pieces of code.",
        "keywords": ["Serverless Computing", "Function as a Service", "Azure"]
    },
    "Google Cloud Functions": {
        "description": "A serverless execution environment for building and connecting cloud services.",
        "keywords": ["Serverless Computing", "Function as a Service", "GCP"]
    },
    "Serverless Framework": {
        "description": "An open-source web framework written in Node.js.",
        "keywords": ["Serverless Applications", "Deployment Tool"]
    },
    "Microservices": {
        "description": "A software architecture style in which complex applications are composed of small, independent processes communicating with each other using language-agnostic APIs.",
        "keywords": ["Software Architecture", "Distributed Systems"]
    },
    "API Gateway": {
        "description": "A management service for APIs.",
        "keywords": ["API Management", "API Security", "Traffic Management"]
    },
    "Service Mesh": {
        "description": "A configurable infrastructure layer for microservices applications.",
        "keywords": ["Microservices Communication", "Traffic Management", "Observability"]
    },
    "Istio": {
        "description": "An open-source service mesh that layers transparently on existing distributed applications.",
        "keywords": ["Service Mesh", "Kubernetes", "Traffic Management"]
    },
    "Linkerd": {
        "description": "An ultralight, security-first service mesh for Kubernetes.",
        "keywords": ["Service Mesh", "Kubernetes", "Traffic Management"]
    },
    "gRPC": {
        "description": "A modern open-source high-performance RPC framework.",
        "keywords": ["Remote Procedure Call", "High Performance", "Microservices"]
    },
    "RESTful APIs": {
        "description": "An architectural style for an application program interface (API) that uses HTTP requests to access and use data.",
        "keywords": ["API Design", "Web Services"]
    },
    "SOAP": {
        "description": "A messaging protocol specification for exchanging structured information in the implementation of web services.",
        "keywords": ["Web Services Protocol", "XML-based"]
    },
    "Message Queues": {
        "description": "A form of asynchronous service-to-service communication used in serverless and microservices architectures.",
        "keywords": ["Asynchronous Communication", "Decoupling Services"]
    },
    "RabbitMQ": {
        "description": "The most widely deployed open source message broker.",
        "keywords": ["Message Broker", "AMQP"]
    },
    "ActiveMQ": {
        "description": "A popular open-source, multi-protocol message broker.",
        "keywords": ["Message Broker", "JMS"]
    },
    "Kafka": {
        "description": "A distributed streaming platform.",
        "keywords": ["Distributed Streaming Platform", "Event Streaming"]
    },
    "Amazon SQS": {
        "description": "A fully managed message queuing service.",
        "keywords": ["Message Queuing Service", "AWS"]
    },
    "Amazon SNS": {
        "description": "A fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.",
        "keywords": ["Notification Service", "AWS"]
    },
    "Google Cloud Pub/Sub": {
        "description": "An asynchronous messaging service that decouples senders and receivers.",
        "keywords": ["Messaging Service", "GCP"]
    },
    "Version Control": {
        "description": "A system that records changes to a file or set of files over time so that you can recall specific versions later.",
        "keywords": ["Source Code Management", "Collaboration"]
    },
    "SVN": {
        "description": "A software versioning and revision control system.",
        "keywords": ["Version Control System", "Centralized"]
    },
    "Perforce": {
        "description": "A software company that provides enterprise-scale development tools.",
        "keywords": ["Version Control System", "Enterprise"]
    },
    "Trello": {
        "description": "A web-based Kanban-style list-making application.",
        "keywords": ["Project Management Tool", "Kanban Board"]
    },
    "Asana": {
        "description": "A web and mobile application designed to help teams organize, track, and manage their work.",
        "keywords": ["Project Management Tool", "Task Management"]
    },
    "Monday.com": {
        "description": "A work operating system (Work OS) that powers teams to run projects and workflows with confidence.",
        "keywords": ["Work OS", "Project Management", "Team Collaboration"]
    },
    "Smartsheet": {
        "description": "A software as a service (SaaS) offering for collaboration and work management.",
        "keywords": ["Work Management", "Collaboration", "Project Management"]
    },
    "MS Project": {
        "description": "A project management software program developed and sold by Microsoft.",
        "keywords": ["Project Management Software", "Gantt Charts"]
    },
    "Primavera P6": {
        "description": "A project portfolio management (PPM) software.",
        "keywords": ["Project Management Software", "Enterprise Project Portfolio Management"]
    },
    "Zendesk": {
        "description": "A customer service software company.",
        "keywords": ["Customer Service Software", "Ticketing System"]
    },
    "Freshdesk": {
        "description": "A cloud-based customer service software.",
        "keywords": ["Customer Service Software", "Ticketing System"]
    },
    "ITIL": {
        "description": "A framework for IT service management.",
        "keywords": ["IT Service Management", "Framework"]
    },
    "COBIT": {
        "description": "A framework for IT governance and management.",
        "keywords": ["IT Governance", "Framework"]
    },
    "PRINCE2": {
        "description": "A structured project management methodology.",
        "keywords": ["Project Management Methodology"]
    },
    "PMP": {
        "description": "Project Management Professional certification.",
        "keywords": ["Project Management Professional", "Certification"]
    },
    "CSM": {
        "description": "Certified ScrumMaster certification.",
        "keywords": ["Certified ScrumMaster", "Certification"]
    },
    "Lean Six Sigma": {
        "description": "A methodology that relies on a collaborative team effort to improve performance by systematically removing waste and reducing variation.",
        "keywords": ["Process Improvement Methodology"]
    },
    "CFA": {
        "description": "Chartered Financial Analyst designation.",
        "keywords": ["Chartered Financial Analyst", "Certification"]
    },
    "CPA": {
        "description": "Certified Public Accountant license.",
        "keywords": ["Certified Public Accountant", "Certification"]
    },
    "SHRM-CP": {
        "description": "SHRM Certified Professional certification.",
        "keywords": ["SHRM Certified Professional", "HR Certification"]
    },
    "PHR": {
        "description": "Professional in Human Resources certification.",
        "keywords": ["Professional in Human Resources", "HR Certification"]
    },
    "CEH": {
        "description": "Certified Ethical Hacker certification.",
        "keywords": ["Certified Ethical Hacker", "Cybersecurity Certification"]
    },
    "OSCP": {
        "description": "Offensive Security Certified Professional certification.",
        "keywords": ["Offensive Security Certified Professional", "Cybersecurity Certification"]
    },
    "CCNA": {
        "description": "Cisco Certified Network Associate certification.",
        "keywords": ["Cisco Certified Network Associate", "Networking Certification"]
    },
    "CISSP": {
        "description": "Certified Information Systems Security Professional certification.",
        "keywords": ["Certified Information Systems Security Professional", "Cybersecurity Certification"]
    },
    "CISM": {
        "description": "Certified Information Security Manager certification.",
        "keywords": ["Certified Information Security Manager", "Cybersecurity Certification"]
    },
    "CompTIA Security+": {
        "description": "CompTIA Security+ certification.",
        "keywords": ["Cybersecurity Certification"]
    }
}
# Convert all company keywords to lowercase for consistent matching
for company_data in COMPANY_SKILL_PROFILES.values():
    company_data["keywords"] = [kw.lower() for kw in company_data["keywords"]]


# IMPORTANT: REPLACE THESE WITH YOUR ACTUAL DEPLOYMENT URLs
APP_BASE_URL = "https://candidate-screenerpro.streamlit.app/" # <--- UPDATED URL
# This URL should be where your generated HTML certificates are publicly accessible.
# For this implementation, the PDF is generated on-the-fly for download/email, so this URL is less critical for email attachment.
CERTIFICATE_HOSTING_URL = "https://candidate-screenerpro.streamlit.app/certificate_verify" # <--- UPDATED URL

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
            # Assuming 'ml_screening_model.pkl' is a pre-trained scikit-learn model
            # You would need to ensure this file is present in your deployment environment
            # ml_model = joblib.load("ml_screening_model.pkl") # Uncomment and provide your model path
            ml_model = None # Placeholder if no specific ML model is used beyond SentenceTransformer
            return model, ml_model
        except Exception as e:
            st.error(f"❌ Error loading AI models: {e}. Please ensure 'all-MiniLM-L6-v2' model can be loaded and 'ml_screening_model.pkl' (if used) is in the same directory.")
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
    text = re.sub(r'[\:\,\–—]+', ' - ', text)  # Normalize all symbols to hyphen

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

            # Parse start date
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

            # Parse end date
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

    # Fallback: textual pattern like "3 years of experience"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(\+)?\s*(year|yrs|years)\b', text)
    if not match:
        match = re.search(r'experience[^\d]{0,10}(\d+(?:\.\d+)?)', text)
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
    lines = text.strip().splitlines()
    if not lines:
        return None

    # 🚫 Terms that should NOT be considered part of a name line
    EXCLUDE_TERMS = {
        "email", "e-mail", "phone", "mobile", "contact", "linkedin", "github",
        "portfolio", "website", "profile", "summary", "objective", "education",
        "skills", "projects", "certifications", "achievements", "experience",
        "dob", "date of birth", "address", "resume", "cv", "career", "gender",
        "marital", "nationality", "languages", "language"
    }

    # 🔠 Common prefixes before names to remove
    PREFIX_CLEANER = re.compile(r"^(name[\s:\-]*|mr\.?|ms\.?|mrs\.?)", re.IGNORECASE)

    potential_names = []

    for line in lines[:10]:  # 🔍 Only scan top 10 lines
        original_line = line.strip()
        if not original_line:
            continue

        # Remove known prefixes (e.g., "Name: John Doe")
        cleaned_line = PREFIX_CLEANER.sub('', original_line).strip()

        # Remove special characters, digits, commas, etc.
        cleaned_line = re.sub(r'[^A-Za-z\s]', '', cleaned_line)

        # Skip if contains any noise terms
        if any(term in cleaned_line.lower() for term in EXCLUDE_TERMS):
            continue

        words = cleaned_line.split()

        # Must be 2–4 words, all alphabetic, and properly cased
        if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
            if all(w.istitle() or w.isupper() for w in words):
                potential_names.append(cleaned_line)

    # Return longest valid name found
    if potential_names:
        return max(potential_names, key=len).title()

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

import re

# Patterns to match degrees and institutions
EDU_MATCH_PATTERN = re.compile(
    r"(b\.?tech|bachelor|be|b\.e\.|m\.?tech|master|mca|mba)[^\n]{0,100}?(university|college|institute)[^\n]{0,100}?(20\d{2})(?!\d)",
    re.IGNORECASE
)

# Fallback pattern: year + degree without university
EDU_FALLBACK_PATTERN = re.compile(
    r"(b\.?tech|bachelor|be|b\.e\.|m\.?tech|master|mca|mba)[^\n]{0,100}?(20\d{2})(?!\d)",
    re.IGNORECASE
)

def extract_education_text(text):
    """
    Extract a clean single-line education summary from resume.
    E.g., "B.Tech in CSE, Alliance University, Bangalore – 2028"
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

    # Try matching full pattern: degree + college + year
    edu_match = EDU_MATCH_PATTERN.search(education_section)
    if edu_match:
        return ' '.join(edu_match.groups()).strip()

    # Try fallback: degree + year
    fallback_match = EDU_FALLBACK_PATTERN.search(education_section)
    if fallback_match:
        return ' '.join(fallback_match.groups()).strip()

    # Fallback to first line in section
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

# --- NEW: Function to get dynamic learning links ---
def get_learning_links(skill):
    """
    Generates dynamic search links for a given skill on various platforms.
    """
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

def generate_company_fit_assessment(candidate_name, company_name, resume_embedding, company_profile_embedding, resume_skills_set, company_keywords):
    """
    Generates a company-specific fit assessment.
    """
    assessment_parts = []
    assessment_parts.append(f"### Company Fit Assessment for {candidate_name} with {company_name}\n")

    # Semantic similarity to company profile
    semantic_fit = cosine_similarity(resume_embedding.reshape(1, -1), company_profile_embedding.reshape(1, -1))[0][0]
    semantic_fit = float(np.clip(semantic_fit, 0, 1))

    if semantic_fit >= 0.75:
        assessment_parts.append(f"Your profile shows a **very strong semantic alignment ({semantic_fit:.2f})** with {company_name}'s core values, technologies, and industry focus. This indicates a high potential for cultural and technical fit.")
    elif semantic_fit >= 0.5:
        assessment_parts.append(f"There is a **good semantic alignment ({semantic_fit:.2f})** between your profile and {company_name}. You share common themes and areas of interest, suggesting a solid potential fit.")
    else:
        assessment_parts.append(f"The semantic alignment ({semantic_fit:.2f}) with {company_name} is moderate. While you may have relevant skills, consider highlighting experiences that directly relate to {company_name}'s specific industry, products, or mission.")

    # Keyword overlap with company's preferred skills
    company_keywords_set = set(company_keywords)
    matched_company_skills = resume_skills_set.intersection(company_keywords_set)
    missing_company_skills = company_keywords_set.difference(resume_keywords_set) # Corrected to use resume_keywords_set

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
                                             min_score_threshold, min_experience_threshold, 
                                             min_cgpa_threshold, max_experience, 
                                             _global_ml_model, target_company_name=None):
    """
    Processes a single resume (pre-extracted text and pre-computed embeddings)
    for the main screener page and returns a dictionary of results.
    """
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

        # --- FULL SCORING LOGIC INTEGRATION ---
        match_score, matched_skills_list, missing_skills_list = calculate_match_score(text, jd_text, global_sentence_model)
        semantic_score_from_feedback = cosine_similarity(resume_embedding.reshape(1, -1), jd_embedding.reshape(1, -1))[0][0]
        semantic_score_from_feedback = float(np.clip(semantic_score_from_feedback, 0, 1)) # Ensure between 0 and 1

        # Apply company-specific skill boost
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
                company_skills = set(s.lower() for s in company_profile["keywords"]) # Access keywords from the nested dict
                
                # Extract skills from resume for company boost calculation
                resume_skills_for_company_boost, _ = extract_relevant_keywords(text, MASTER_SKILLS)
                candidate_matched_company_skills = resume_skills_for_company_boost.intersection(company_skills)
                
                if company_skills: # Avoid division by zero
                    company_skill_match_ratio = len(candidate_matched_company_skills) / len(company_skills)
                    company_boost_percentage = company_skill_match_ratio * 5 # Max 5% boost for company fit

                # Generate company fit assessment text
                company_keywords_for_embedding = " ".join(company_profile["keywords"])
                company_description_for_embedding = company_profile["description"]
                company_text_for_embedding = f"{company_description_for_embedding} {company_keywords_for_embedding}"
                company_embedding = global_sentence_model.encode([clean_text(company_text_for_embedding)])[0]

                company_fit_assessment_text = generate_company_fit_assessment(
                    candidate_name=candidate_name,
                    company_name=normalized_company_name,
                    resume_embedding=resume_embedding,
                    company_profile_embedding=company_embedding,
                    resume_skills_set=set(matched_skills_list), # Pass as set
                    company_keywords=company_profile["keywords"]
                )
            else:
                company_fit_assessment_text = f"Company '{target_company_name}' not found in our predefined profiles. Please try one of the examples (e.g., Google, Microsoft, Amazon, Generic Tech Startup, IBM, Oracle, SAP, Cisco, Adobe, NVIDIA)."
        # --- END Company-specific logic ---

        overall_score = (match_score * 0.95) + (company_boost_percentage) # Adjust weights to accommodate boost
        overall_score = np.clip(overall_score, 0, 100) # Ensure score is between 0 and 100

        # Generate candidate feedback (no LLM)
        candidate_ai_feedback = generate_candidate_feedback(
            candidate_name=candidate_name,
            score=overall_score, # Use the boosted score for feedback
            years_exp=exp,
            semantic_similarity=semantic_score_from_feedback,
            cgpa=cgpa,
            matched_skills=matched_skills_list,
            missing_skills=missing_skills_list,
            target_company_name=target_company_name # Pass company name to feedback
        )

        # Assign to variables used by downstream functions
        score = overall_score
        semantic_similarity = semantic_score_from_feedback 
        matched_keywords = matched_skills_list 
        missing_skills = missing_skills_list 
        
        # All assessment fields will now contain the candidate-facing feedback
        llm_feedback_text = candidate_ai_feedback # Renamed for clarity in output structure

        certificate_id = str(uuid.uuid4())
        certificate_rank = "Not Applicable"

        # Determine Certificate Rank based on score
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
        
        # Determine Tag based on all criteria (including user-set thresholds)
        tag = "❌ Limited Match"
        if score >= min_score_threshold and exp >= min_experience_threshold and exp <= max_experience and (cgpa is None or cgpa >= min_cgpa_threshold):
            if score >= 90 and semantic_similarity >= 0.85:
                tag = "👑 Exceptional Match"
            elif score >= 80 and semantic_similarity >= 0.7:
                tag = "🔥 Strong Candidate"
            elif score >= 60:
                tag = "✨ Promising Fit"
            else:
                tag = "✅ Qualified (Meets Thresholds)"
        else:
            tag = "⚠️ Does Not Meet Thresholds"


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
            "AI Suggestion": llm_feedback_text, # Now directly uses generated candidate feedback
            "Detailed HR Assessment": llm_feedback_text, # Repurposed to show candidate feedback
            "Company Fit Assessment": company_fit_assessment_text, # New field added here
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
            "LLM Feedback": llm_feedback_text # This field also holds the candidate feedback
        }
    except Exception as e:
        print(f"CRITICAL ERROR: Unhandled exception processing {file_name}: {e}")
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
            "Company Fit Assessment": f"Critical Error: {e}", # New field
            "Matched Skills": [], "Missing Skills": [],
            "Matched Keywords (Categorized)": "{}", 
            "Missing Skills (Categorized)": "{}", 
            "Resume Raw Text": "",
            "JD Used": jd_name_for_results, "Date Screened": datetime.now().date(),
            "Certificate ID": str(uuid.uuid4()), "Certificate Rank": "Not Applicable",
            "Tag": "❌ Critical Processing Error",
            "LLM Feedback": f"Critical Error: {e}" 
        }

# --- Function to extract skills from text ---
def extract_skills(text):
    """
    Extracts relevant skills from a given text using MASTER_SKILLS.
    Returns a set of extracted skills (lowercase).
    """
    extracted_keywords, _ = extract_relevant_keywords(text, MASTER_SKILLS)
    return extracted_keywords

# --- Function to calculate match score ---
def calculate_match_score(resume_text, jd_text, sentence_model):
    """
    Calculates a match score between resume and JD based on keyword overlap
    and semantic similarity.
    Returns: score, matched_skills_list, missing_skills_list
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # Keyword-based match
    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills.difference(resume_skills)

    keyword_match_percentage = 0
    if len(jd_skills) > 0:
        keyword_match_percentage = (len(matched_skills) / len(jd_skills)) * 100

    # Semantic similarity
    resume_embedding = sentence_model.encode(clean_text(resume_text), convert_to_tensor=True)
    jd_embedding = sentence_model.encode(clean_text(jd_text), convert_to_tensor=True)
    
    semantic_similarity = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()
    semantic_similarity = float(np.clip(semantic_similarity, 0, 1)) # Ensure between 0 and 1

    # Combine scores (you can adjust weights)
    # Give more weight to keyword match for direct skill alignment, and some to semantic for overall context
    overall_score = (keyword_match_percentage * 0.6) + (semantic_similarity * 40) # Max 60 + 40 = 100
    overall_score = np.clip(overall_score, 0, 100) # Ensure score is between 0 and 100

    return overall_score, list(matched_skills), list(missing_skills)

# --- Function to generate candidate feedback (no LLM API calls) ---
def generate_candidate_feedback(candidate_name, score, years_exp, semantic_similarity, cgpa, matched_skills, missing_skills, target_company_name=None):
    """
    Generates detailed, diverse feedback for the candidate based on their screening results.
    This function does NOT use an external LLM API.
    """
    feedback_parts = []
    
    feedback_parts.append(f"### Personalized Feedback for {candidate_name}\n")
    feedback_parts.append(f"Thank you for submitting your resume! Here's a detailed assessment of your profile for this role, based on our automated screening.\n")

    # Overall Fit Summary
    if score >= 85:
        feedback_parts.append("**Overall Fit: Excellent!** Your profile demonstrates a very strong alignment with the requirements of this position. You possess a robust skill set and relevant experience that closely matches what we're looking for.")
    elif score >= 70:
        feedback_parts.append("**Overall Fit: Good.** Your resume shows a solid match for this role. You have many of the key skills and experiences needed, indicating strong potential for success.")
    elif score >= 50:
        feedback_parts.append("**Overall Fit: Moderate.** Your profile indicates some alignment with the role, but there are areas where further development or clearer demonstration of skills could significantly strengthen your candidacy.")
    else:
        feedback_parts.append("**Overall Fit: Limited.** While we appreciate your application, your current profile shows limited direct alignment with the specific requirements of this position.")

    # Strengths
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


    # Areas for Improvement
    feedback_parts.append("\n#### Areas for Growth:")
    if missing_skills:
        feedback_parts.append(f"To further strengthen your profile for future opportunities, consider developing skills in these areas that were highlighted in the job description but less prominent in your resume: {', '.join(sorted(missing_skills))}.")
        feedback_parts.append("Focusing on these could significantly enhance your alignment with similar roles.")
    else:
        feedback_parts.append("Your profile is quite comprehensive! Continue to deepen your expertise in your core areas and explore emerging technologies relevant to your field.")

    # Actionable Advice
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

# --- NEW: Function to get dynamic learning links (re-implemented) ---
def get_learning_links(skill):
    """
    Generates dynamic search links for a given skill on various trusted platforms.
    """
    return {
        "Coursera": f"https://www.coursera.org/search?query={urllib.parse.quote(skill)}",
        "Udemy": f"https://www.udemy.com/courses/search/?q={urllib.parse.quote(skill)}",
        "YouTube": f"https://www.youtube.com/results?search_query={urllib.parse.quote(skill)}+course",
        "Google": f"https://www.google.com/search?q={urllib.parse.quote(skill)}+tutorial"
    }

# Function to load JDs from a local folder
def load_jds_from_folder(folder_path="data/jds"):
    jds = {"Paste New JD": ""}
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith((".txt", ".md")):
                filepath = os.path.join(folder_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        jds[filename] = f.read()
                except Exception as e:
                    st.warning(f"Could not load JD from {filename}: {e}")
    return jds

def resume_screener_page():
    st.title("📄 AI-Powered Resume Screener")
    st.markdown("Upload a resume and paste a Job Description to get an instant match score and personalized feedback!")

    # Initialize session state for results if not already present
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'jd_text_input' not in st.session_state:
        st.session_state.jd_text_input = ""
    if 'jd_selection_method' not in st.session_state:
        st.session_state.jd_selection_method = "Paste JD"
    if 'selected_jd_file' not in st.session_state:
        st.session_state.selected_jd_file = "Paste New JD"
    
    # Initialize certificate display state
    if 'certificate_html_content' not in st.session_state:
        st.session_state['certificate_html_content'] = ""

    # Initialize jd_text and jd_name_for_results outside the column scope
    jd_text = ""
    jd_name_for_results = "User Provided JD"

    st.markdown("## ⚙️ Define Job Requirements & Screening Criteria")
    col1_jd, col2_jd = st.columns([2, 1]) # Renamed columns to avoid conflict

    with col1_jd:
        job_roles = {"Upload my own": None}
        # Load JDs from the 'data/jds' folder
        jd_files_from_folder = load_jds_from_folder("data/")
        job_roles.update(jd_files_from_folder) # Add loaded JDs to options

        jd_option = st.selectbox("📌 **Select a Pre-Loaded Job Role or Upload Your Own Job Description**", list(job_roles.keys()))
        
        if jd_option == "Upload my own":
            jd_file = st.file_uploader("Upload Job Description (TXT, PDF)", type=["txt", "pdf"], help="Upload a .txt or .pdf file containing the job description.")
            if jd_file:
                jd_text = extract_text_from_file(jd_file.read(), jd_file.name, jd_file.type)
                jd_name_for_results = jd_file.name.replace('.pdf', '').replace('.txt', '')
            else:
                jd_name_for_results = "Uploaded JD (No file selected)"
        else:
            # If a pre-loaded JD is selected
            if jd_option in job_roles and job_roles[jd_option] is not None:
                jd_path = job_roles[jd_option]
                try:
                    with open(jd_path, "r", encoding="utf-8") as f:
                        jd_text = f.read()
                    jd_name_for_results = jd_option
                except Exception as e:
                    st.error(f"Error loading selected JD: {e}")
                    jd_text = ""
                    jd_name_for_results = "Error Loading JD"
            else: # This case handles "Paste New JD" if it was added to job_roles, or if the path is None
                jd_text = st.text_area(
                    "Paste the Job Description here:",
                    height=300,
                    key="jd_text_input_paste", # Changed key to avoid conflict
                    placeholder="E.g., 'We are looking for a Software Engineer with strong Python, AWS, and React skills...'"
                )
                jd_name_for_results = "User Provided JD"


    with col2_jd:
        if jd_text:
            with st.expander("📝 View Loaded Job Description"):
                st.text_area("Job Description Content", jd_text, height=200, disabled=True, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("## ☁️ Job Description Keyword Cloud")
            st.caption("Visualizing the most frequent and important keywords from the Job Description.")
            st.info("💡 To filter candidates by these skills, use the 'Filter Candidates by Skill' section below the main results table.")
            
            jd_words_for_cloud_set, _ = extract_relevant_keywords(jd_text, MASTER_SKILLS) # Corrected to MASTER_SKILLS
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
        else:
            st.info("Please select or upload a Job Description to view its keyword cloud.")


   


    # Company Selection
    st.markdown("## 🏢 Target Company Fit (Optional)")
    st.caption("Assess how well your resume aligns with a specific company's profile.")
    target_company_name = st.selectbox(
        "**Select a Target Company**",
        options=["None"] + sorted(list(COMPANY_SKILL_PROFILES.keys())), # Added "None" as first option
        index=0, # Default to "None"
        help="Choose a company from the list to see how well your resume aligns with its typical profile. This is based on a simplified, predefined list of company keywords."
    )
    if target_company_name != "None":
        st.info(f"A small score boost will be applied if your resume matches skills important to {target_company_name}. A detailed company fit assessment will also be provided.")


    # File Uploader for Resume
    st.subheader("4. Upload Resume")
    uploaded_resume_file = st.file_uploader(
        "Upload a resume (PDF only)",
        type=["pdf"],
        help="Please upload a text-selectable PDF resume for best results."
    )

    if st.button("🚀 Screen Resume"):
        if not jd_text.strip():
            st.error("Please provide a Job Description.")
        elif not uploaded_resume_file:
            st.error("Please upload a resume.")
        else:
            with st.spinner("Processing resume and generating insights..."):
                try:
                    # Extract text from uploaded resume
                    resume_bytes = uploaded_resume_file.read() # Corrected variable name
                    resume_text = extract_text_from_file(resume_bytes, uploaded_resume_file.name, uploaded_resume_file.type) # Corrected variable name

                    if resume_text.startswith("[ERROR]"):
                        st.error(resume_text)
                        st.session_state.results = None
                        return

                    # Generate embeddings for JD and resume
                    jd_embedding = global_sentence_model.encode(clean_text(jd_text), convert_to_tensor=True)
                    resume_embedding = global_sentence_model.encode(clean_text(resume_text), convert_to_tensor=True)

                    # Process the resume
                    screening_results = _process_single_resume_for_screener_page(
                        file_name=uploaded_resume_file.name, # Corrected variable name
                        text=resume_text,
                        jd_text=jd_text,
                        jd_embedding=jd_embedding,
                        resume_embedding=resume_embedding,
                        jd_name_for_results=jd_name_for_results,
                        min_score_threshold=min_score_threshold, # Pass thresholds
                        min_experience_threshold=min_experience_threshold,
                        min_cgpa_threshold=min_cgpa_threshold,
                        max_experience=max_experience,
                        _global_ml_model=global_ml_model,
                        target_company_name=target_company_name # Pass selected company
                    )
                    st.session_state.results = screening_results
                    st.success("Analysis complete! See the results below.")

                    # --- Automatic Certificate Sending ---
                    if st.session_state.results and st.session_state.results['Email'] != 'Not Found' and st.session_state.results['Skill Match'] >= 50: # Only send if score >= 50
                        gmail_address = st.secrets.get("GMAIL_ADDRESS")
                        gmail_app_password = st.secrets.get("GMAIL_APP_PASSWORD")

                        if gmail_address and gmail_app_password:
                            st.info("Attempting to automatically send certificate...")
                            certificate_html_content = generate_certificate_html(st.session_state.results) # Use the dedicated function
                            
                            # Construct the public URL for the certificate (if you plan to host them)
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
                            st.warning("Email sending not configured. Certificate was not sent automatically. Please check your Streamlit secrets for GMAIL_ADDRESS and GMAIL_APP_PASSWORD.")
                    elif st.session_state.results and st.session_state.results['Email'] == 'Not Found':
                        st.warning("No email address found in the resume. Certificate could not be sent automatically.")
                    elif st.session_state.results and st.session_state.results['Skill Match'] < 50:
                        st.info(f"Candidate score ({st.session_state.results['Skill Match']:.2f}%) is below the 50% threshold for automatic certificate issuance.")


                except Exception as e:
                    st.error(f"An unexpected error occurred during processing: {e}")
                    traceback.print_exc()
                    st.session_state.results = None

    if st.session_state.results:
        results = st.session_state.results
        st.subheader("📊 Screening Results")

        st.markdown(f"### Candidate: {results['Candidate Name']}")
        st.info(f"**Overall Match Score:** {results['Skill Match']:.2f}% {results['Tag']}")

        # Display AI Suggestion/Feedback
        st.markdown("---")
        st.markdown("### AI Feedback")
        st.markdown(results['LLM Feedback']) # This now holds the detailed candidate feedback
        
        # --- Display Company Fit Assessment ---
        st.markdown("---")
        st.markdown("## 🏢 Company Fit Assessment")
        st.markdown(results['Company Fit Assessment'])
        # --- END Display Company Fit Assessment ---

        # Display Key Information
        st.markdown("---")
        st.markdown("### Key Information Extracted")
        with st.expander("Personal Details"):
            st.write(f"**Email:** {results['Email']}")
            st.write(f"**Phone Number:** {results['Phone Number']}")
            st.write(f"**Location:** {results['Location']}")
            st.write(f"**Languages:** {results['Languages']}")
            st.write(f"**Years of Experience:** {results['Years Experience']:.1f}")
            st.write(f"**CGPA (4.0 Scale):** {results['CGPA (4.0 Scale)'] if results['CGPA (4.0 Scale)'] is not None else 'Not Found'}")

        with st.expander("Education"):
            st.write(f"**Education Details:** {results['Education Details']}")

        with st.expander("Work History"):
            if results['Work History'] != "Not Found":
                st.markdown(f"**Work History:**")
                for entry in results['Work History'].split('; '):
                    st.markdown(f"- {entry}")
            else:
                st.write("**Work History:** Not Found")

        with st.expander("Projects"):
            if results['Project Details'] != "Not Found":
                st.markdown(f"**Project Details:**")
                for entry in results['Project Details'].split('; '):
                    st.markdown(f"- {entry}")
            else:
                st.write("**Project Details:** Not Found")

        # Display Matched and Missing Skills
        st.markdown("---")
        st.markdown("### Skill Alignment")
        
        matched_skills_list = results['Matched Skills']
        missing_skills_list = results['Missing Skills']

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("✅ **Matched Skills:**")
            if matched_skills_list:
                for skill in sorted(matched_skills_list):
                    st.markdown(f"- {skill.title()}")
            else:
                st.markdown("- No direct skill matches found.")

        with col2:
            st.markdown("❌ **Missing Skills & Learning Links:**")
            if missing_skills_list:
                for skill in sorted(missing_skills_list):
                    st.markdown(f"**{skill.title()}**:")
                    links = get_learning_links(skill)
                    for platform, url in links.items():
                        st.markdown(f"  - 🔗 [{platform}]({url})", unsafe_allow_html=True)
            else:
                st.markdown("- No missing skills identified based on JD.")
                st.markdown("Great job! Your skills align well with the job description.")

        # Certificate Generation
        st.markdown("---")
        st.markdown("### Your ScreenerPro Certificate")
        st.markdown(f"Your unique Certificate ID: `{results['Certificate ID']}`")
        st.markdown(f"**Rank Achieved:** {results['Certificate Rank']}")

        certificate_html_content = generate_certificate_html(results) # Use the dedicated function

        # Download button
        st.download_button(
            label="Download Certificate (PDF)",
            data=HTML(string=certificate_html_content).write_pdf(),
            file_name=f"ScreenerPro_Certificate_{results['Candidate Name'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

        # Email certificate section (manual trigger still available)
        with st.expander("Manually Email Certificate"):
            recipient_email = st.text_input("Enter recipient email address:", value=results['Email'] if results['Email'] != 'Not Found' else '')
            if st.button("Send Certificate via Email (Manual)"):
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
                        st.error("Email sending is not configured. Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your Streamlit secrets.")
                else:
                    st.error("Please enter a valid recipient email address.")

        # Save to Leaderboard button
        st.markdown("---")
        st.markdown("### Contribute to Leaderboard")
        if st.button("Add My Score to Leaderboard"):
            with st.spinner("Saving to leaderboard..."):
                save_screening_result_to_firestore_rest(results)

# This is the entry point for your Streamlit app.
# If you have an `app.py` file, it should look something like this:
#
# # app.py
# import streamlit as st
# from resume_screener import resume_screener_page
#
# def main():
#     st.set_page_config(layout="wide", page_title="ScreenerPro")
#     resume_screener_page()
#
# if __name__ == "__main__":
#     main()
