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
    "Google": ["Python", "Machine Learning", "TensorFlow", "Distributed Systems", "Algorithms", "Data Structures", "Cloud Computing", "Go", "Java", "C++"],
    "Microsoft": ["C#", "Azure", ".NET", "SQL Server", "Cloud Computing", "Power BI", "Machine Learning", "TypeScript", "React", "DevOps"],
    "Amazon": ["AWS", "Java", "Python", "Distributed Systems", "Microservices", "Cloud Computing", "SQL", "NoSQL", "Leadership", "Problem Solving"],
    "Meta (Facebook)": ["React", "Python", "JavaScript", "Deep Learning", "PyTorch", "GraphQL", "Mobile Development", "PHP", "C++", "Social Media"],
    "Apple": ["Swift", "Objective-C", "iOS Development", "macOS Development", "User Experience (UX)", "Product Design", "Hardware Integration", "Privacy", "Security"],
    "Netflix": ["Python", "AWS", "Microservices", "Data Science", "Machine Learning", "Distributed Systems", "Streaming Technologies", "Recommendation Systems", "Cloud Computing"],
    "Salesforce": ["Salesforce CRM", "Apex", "Visualforce", "Lightning Web Components", "Cloud Computing", "SaaS", "Customer Relationship Management", "JavaScript", "API Integration"],
    "IBM": ["Java", "Python", "Cloud Computing", "AI", "Machine Learning", "Data Science", "Blockchain", "Cybersecurity", "Enterprise Software", "Consulting"],
    "Oracle": ["Java", "SQL", "Oracle Database", "Cloud Computing", "Enterprise Software", "ERP", "CRM", "Data Warehousing", "Middleware"],
    "Accenture": ["Consulting", "Project Management", "Change Management", "Digital Transformation", "Cloud Computing", "Data Analytics", "Strategy", "Business Process Improvement"],
    "Infosys": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Enterprise Applications", "Consulting", "Project Management", "Data Analytics", "AI"],
    "TCS": ["Java", "Python", "Cloud Computing", "DevOps", "Agile", "Digital Transformation", "Enterprise Solutions", "Data Science", "Cybersecurity"],
    "Wipro": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Infrastructure Management", "Consulting", "Data Analytics", "AI", "Cybersecurity"],
    "HCLTech": ["Java", "Python", "Cloud Computing", "DevOps", "Digital Transformation", "Product Engineering", "Data Science", "AI", "Cybersecurity"],
    "Capgemini": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Consulting", "Data Analytics", "AI", "Cybersecurity", "ERP"],
    "Cognizant": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Data Analytics", "AI", "Cybersecurity", "IT Consulting"],
    "Tech Mahindra": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Network Services", "Data Analytics", "AI", "Cybersecurity"],
    "LTIMindtree": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Data Analytics", "AI", "Cybersecurity", "Enterprise Solutions"],
    "Persistent Systems": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Product Engineering", "Data Analytics", "AI", "Cybersecurity"],
    "Mindtree": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Data Analytics", "AI", "Cybersecurity", "Enterprise Solutions"],
    "Zensar Technologies": ["Java", "Python", "Cloud Computing", "Digital Transformation", "Data Analytics", "AI", "Cybersecurity"],
    "Cyient": ["Engineering Services", "Geospatial", "IoT", "Data Analytics", "Aerospace", "Automotive", "Medical Devices", "Manufacturing"],
    "L&T Technology Services": ["Engineering Services", "Digital Engineering", "IoT", "AI", "Machine Learning", "Embedded Systems", "Automotive", "Aerospace", "Medical Devices"],
    "Mphasis": ["Cloud Computing", "Digital Transformation", "AI", "Cognitive Computing", "Cybersecurity", "Banking & Financial Services", "Insurance"],
    "Hexaware Technologies": ["Cloud Computing", "Digital Transformation", "Automation", "AI", "Machine Learning", "Data Analytics", "Enterprise Solutions"],
    "Coforge": ["Cloud Computing", "Digital Transformation", "Automation", "AI", "Machine Learning", "Data Analytics", "Financial Services", "Travel & Tourism"],
    "Birlasoft": ["Enterprise Solutions", "Digital Transformation", "Cloud Computing", "Data Analytics", "AI", "IoT", "Manufacturing", "Life Sciences"],
    "Sonata Software": ["Digital Transformation", "Cloud Computing", "Data Analytics", "AI", "Retail", "Travel", "CPG", "Manufacturing"],
    "Firstsource Solutions": ["Customer Experience", "Business Process Management", "Digital Transformation", "Data Analytics", "Healthcare", "Financial Services", "Telecom"],
    "ExlService Holdings": ["Data Analytics", "AI", "Machine Learning", "Digital Transformation", "Operations Management", "Finance & Accounting", "Healthcare", "Insurance"],
    "Genpact": ["Digital Transformation", "AI", "Machine Learning", "Data Analytics", "Business Process Management", "Finance & Accounting", "Supply Chain", "Procurement"],
    "Concentrix": ["Customer Experience", "Digital Transformation", "Business Process Management", "Contact Center", "CX Consulting", "Sales", "Marketing"],
    "Teleperformance": ["Customer Experience", "Omnichannel Solutions", "Digital Transformation", "Contact Center", "Business Process Outsourcing"],
    "Conduent": ["Business Process Solutions", "Digital Platforms", "Healthcare", "Transportation", "Government Services", "Commercial Industries"],
    "Sutherland": ["Digital Transformation", "Customer Experience", "Business Process Transformation", "AI", "Automation", "Healthcare", "Financial Services", "Retail"],
    "Startek": ["Customer Experience", "Omnichannel Solutions", "Contact Center", "Digital Transformation", "Business Process Outsourcing"],
    "Transcom": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing"],
    "Alorica": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing"],
    "TTEC": ["Customer Experience", "Digital Transformation", "Contact Center", "AI", "Automation", "Consulting"],
    "VXI Global Solutions": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing"],
    "Sitel Group": ["Customer Experience", "Contact Center", "Digital Transformation", "Business Process Outsourcing"],
    "TaskUs": ["Digital Customer Experience", "Content Moderation", "AI Operations", "Gaming", "Fintech", "E-commerce"],
    "Arise Virtual Solutions": ["Virtual Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions"],
    "LiveOps": ["Cloud Contact Center", "Customer Service", "Sales", "Technical Support", "Work-from-Home Solutions"],
    "Concentrix + Webhelp": ["Customer Experience", "Business Process Management", "Digital Transformation", "Contact Center"],
    "Modis": ["IT Consulting", "Digital Transformation", "Talent Solutions", "Cloud", "Cybersecurity", "Data & AI"],
    "TEKsystems": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Insight Global": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Robert Half Technology": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Kforce": ["IT Staffing", "IT Consulting", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Apex Systems": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Collabera": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Hays": ["IT Staffing", "IT Recruitment", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Michael Page": ["IT Recruitment", "IT Staffing", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Randstad Technologies": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Adecco": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Kelly Services": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "ManpowerGroup": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "Aerotek": ["IT Staffing", "IT Services", "Digital Transformation", "Cloud", "Cybersecurity", "Data & AI"],
    "CDW": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services"],
    "Insight Enterprises": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services"],
    "Presidio": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services"],
    "ePlus": ["IT Solutions", "Cloud", "Cybersecurity", "Data Center", "Networking", "Managed Services"],
    "Optiv": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security"],
    "Herjavec Group": ["Cybersecurity Solutions", "Security Consulting", "Managed Security Services", "Identity & Access Management", "Cloud Security"],
    "Rapid7": ["Vulnerability Management", "Security Operations", "Application Security", "Cloud Security", "Threat Intelligence"],
    "Tenable": ["Vulnerability Management", "Cyber Exposure", "OT Security", "Cloud Security", "Web Application Security"],
    "Qualys": ["Vulnerability Management", "Cloud Security", "Web Application Security", "Compliance", "Asset Management"],
    "CrowdStrike": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "Managed Detection and Response (MDR)"],
    "SentinelOne": ["Endpoint Security", "Cloud Security", "Threat Intelligence", "Incident Response", "XDR"],
    "Palo Alto Networks": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention"],
    "Fortinet": ["Network Security", "Cloud Security", "Endpoint Security", "Security Operations", "Threat Prevention"],
    "Cisco": ["Networking", "Cybersecurity", "Collaboration", "Cloud", "Data Center", "IoT"],
    "Juniper Networks": ["Networking", "Cloud", "AI-driven Enterprise", "Security", "Automation"],
    "VMware": ["Virtualization", "Cloud Computing", "Network Virtualization", "Security", "Digital Workspace"],
    "Citrix": ["Virtualization", "Cloud Computing", "Digital Workspace", "Networking", "Security"],
    "Red Hat": ["Open Source", "Linux", "Cloud Computing", "Kubernetes", "Automation", "Middleware", "DevOps"],
    "SUSE": ["Open Source", "Linux", "Kubernetes", "Cloud Computing", "Edge Computing", "Storage"],
    "Canonical (Ubuntu)": ["Open Source", "Linux", "Cloud Computing", "IoT", "AI/ML", "Containers"],
    "MongoDB": ["NoSQL Database", "Document Database", "Cloud Database", "Atlas", "Enterprise Advanced"],
    "Databricks": ["Data Lakehouse", "Spark", "AI/ML", "Data Engineering", "Data Science", "Delta Lake", "MLflow"],
    "Snowflake": ["Cloud Data Warehouse", "Data Lake", "Data Sharing", "Data Marketplace", "Data Applications"],
    "Teradata": ["Enterprise Data Warehouse", "Cloud Data Analytics", "Hybrid Cloud", "AI/ML Integration"],
    "Cloudera": ["Data Cloud", "Data Management", "Data Analytics", "Machine Learning", "Hybrid Cloud", "Open Source"],
    "Hortonworks": ["Data Platform", "Hadoop", "Spark", "Data Management", "Data Analytics", "Open Source"],
    "Confluent": ["Kafka", "Event Streaming Platform", "Data in Motion", "Cloud-Native", "Real-Time Data"],
    "Elastic (Elasticsearch)": ["Search Engine", "Analytics Engine", "Observability", "Security", "Elastic Stack", "Kibana", "Logstash"],
    "Redis Labs": ["In-Memory Database", "NoSQL", "Caching", "Real-Time Data", "Redis Enterprise"],
    "Neo4j": ["Graph Database", "Graph Analytics", "Knowledge Graphs", "AI/ML"],
    "InfluxData (InfluxDB)": ["Time Series Database", "IoT", "Monitoring", "Analytics", "Cloud-Native"],
    "Timescale (TimescaleDB)": ["Time Series Database", "PostgreSQL Extension", "IoT", "Analytics", "Cloud-Native"],
    "Vertica": ["Columnar Database", "Analytics Database", "Data Warehousing", "Big Data Analytics"],
    "ClickHouse": ["Columnar Database", "Analytics Database", "Real-Time Analytics", "Big Data"],
    "Pinecone": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"],
    "Weaviate": ["Vector Database", "Vector Search", "AI/ML", "Knowledge Graphs", "Semantic Search"],
    "Milvus": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Similarity Search"],
    "Qdrant": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"],
    "Chroma": ["Vector Database", "Vector Search", "AI/ML", "Embeddings", "Semantic Search"],
    "Faiss": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"],
    "Annoy": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"],
    "Hnswlib": ["Similarity Search", "Vector Search", "Embeddings", "AI/ML"],
    "Scikit-learn": ["Machine Learning Library", "Python", "Classification", "Regression", "Clustering"],
    "TensorFlow": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Google"],
    "PyTorch": ["Deep Learning Framework", "AI/ML", "Neural Networks", "Facebook AI"],
    "Keras": ["Deep Learning API", "TensorFlow", "Neural Networks", "Rapid Prototyping"],
    "XGBoost": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"],
    "LightGBM": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"],
    "CatBoost": ["Gradient Boosting", "Machine Learning", "Ensemble Methods", "Classification", "Regression"],
    "Statsmodels": ["Statistical Modeling", "Econometrics", "Python", "Statistical Tests"],
    "NumPy": ["Numerical Computing", "Python", "Arrays", "Matrices"],
    "Pandas": ["Data Manipulation", "Data Analysis", "Python", "DataFrames"],
    "Matplotlib": ["Data Visualization", "Python", "Plotting"],
    "Seaborn": ["Statistical Data Visualization", "Python", "Matplotlib"],
    "Plotly": ["Interactive Data Visualization", "Web-based", "Dashboards"],
    "Bokeh": ["Interactive Data Visualization", "Web-based", "Python"],
    "Dash": ["Web Application Framework", "Python", "Plotly"],
    "Flask": ["Web Framework", "Python", "Microframework"],
    "Django": ["Web Framework", "Python", "Full-stack"],
    "FastAPI": ["Web Framework", "Python", "High Performance", "API Development"],
    "Spring Boot": ["Java Framework", "Microservices", "Web Applications"],
    ".NET Core": ["Cross-platform Framework", "C#", "Web Applications", "APIs"],
    "Node.js": ["JavaScript Runtime", "Backend Development", "Server-side"],
    "Express.js": ["Node.js Web Framework", "Backend Development", "APIs"],
    "React": ["JavaScript Library", "Frontend Development", "UI Components"],
    "Angular": ["JavaScript Framework", "Frontend Development", "Single-page Applications"],
    "Vue.js": ["JavaScript Framework", "Frontend Development", "Progressive Web Apps"],
    "Svelte": ["JavaScript Framework", "Frontend Development", "Component Compiler"],
    "jQuery": ["JavaScript Library", "DOM Manipulation", "Event Handling"],
    "Bootstrap": ["CSS Framework", "Responsive Design", "UI Components"],
    "Tailwind CSS": ["CSS Framework", "Utility-first", "Rapid UI Development"],
    "Sass": ["CSS Preprocessor", "CSS Extensions"],
    "Less": ["CSS Preprocessor", "CSS Extensions"],
    "Webpack": ["Module Bundler", "JavaScript Applications"],
    "Babel": ["JavaScript Compiler", "Transpiler"],
    "npm": ["Node Package Manager", "JavaScript Packages"],
    "Yarn": ["Package Manager", "JavaScript Packages"],
    "Ansible": ["Automation Engine", "IT Automation", "Configuration Management"],
    "Terraform": ["Infrastructure as Code", "Cloud Provisioning", "Multi-cloud"],
    "Jenkins": ["CI/CD", "Automation Server", "Build Automation"],
    "GitLab CI/CD": ["CI/CD", "GitLab Integration", "DevOps Platform"],
    "GitHub Actions": ["CI/CD", "GitHub Integration", "Workflow Automation"],
    "AWS CodeBuild": ["CI/CD", "Build Service", "AWS"],
    "AWS CodePipeline": ["CI/CD", "Release Automation", "AWS"],
    "AWS CodeDeploy": ["Deployment Service", "Automated Deployments", "AWS"],
    "AWS Lambda": ["Serverless Computing", "Function as a Service", "AWS"],
    "Azure Functions": ["Serverless Computing", "Function as a Service", "Azure"],
    "Google Cloud Functions": ["Serverless Computing", "Function as a Service", "GCP"],
    "Serverless Framework": ["Serverless Applications", "Deployment Tool"],
    "Microservices": ["Software Architecture", "Distributed Systems"],
    "API Gateway": ["API Management", "API Security", "Traffic Management"],
    "Service Mesh": ["Microservices Communication", "Traffic Management", "Observability"],
    "Istio": ["Service Mesh", "Kubernetes", "Traffic Management"],
    "Linkerd": ["Service Mesh", "Kubernetes", "Traffic Management"],
    "gRPC": ["Remote Procedure Call", "High Performance", "Microservices"],
    "RESTful APIs": ["API Design", "Web Services"],
    "SOAP": ["Web Services Protocol", "XML-based"],
    "Message Queues": ["Asynchronous Communication", "Decoupling Services"],
    "RabbitMQ": ["Message Broker", "AMQP"],
    "ActiveMQ": ["Message Broker", "JMS"],
    "Kafka": ["Distributed Streaming Platform", "Event Streaming"],
    "Amazon SQS": ["Message Queuing Service", "AWS"],
    "Amazon SNS": ["Notification Service", "AWS"],
    "Google Cloud Pub/Sub": ["Messaging Service", "GCP"],
    "Version Control": ["Source Code Management", "Collaboration"],
    "SVN": ["Version Control System", "Centralized"],
    "Perforce": ["Version Control System", "Enterprise"],
    "Trello": ["Project Management Tool", "Kanban Board"],
    "Asana": ["Project Management Tool", "Task Management"],
    "Monday.com": ["Work OS", "Project Management", "Team Collaboration"],
    "Smartsheet": ["Work Management", "Collaboration", "Project Management"],
    "MS Project": ["Project Management Software", "Gantt Charts"],
    "Primavera P6": ["Project Management Software", "Enterprise Project Portfolio Management"],
    "Zendesk": ["Customer Service Software", "Ticketing System"],
    "Freshdesk": ["Customer Service Software", "Ticketing System"],
    "ITIL": ["IT Service Management", "Framework"],
    "COBIT": ["IT Governance", "Framework"],
    "PRINCE2": ["Project Management Methodology"],
    "PMP": ["Project Management Professional", "Certification"],
    "CSM": ["Certified ScrumMaster", "Certification"],
    "Lean Six Sigma": ["Process Improvement Methodology"],
    "CFA": ["Chartered Financial Analyst", "Certification"],
    "CPA": ["Certified Public Accountant", "Certification"],
    "SHRM-CP": ["SHRM Certified Professional", "HR Certification"],
    "PHR": ["Professional in Human Resources", "HR Certification"],
    "CEH": ["Certified Ethical Hacker", "Cybersecurity Certification"],
    "OSCP": ["Offensive Security Certified Professional", "Cybersecurity Certification"],
    "CCNA": ["Cisco Certified Network Associate", "Networking Certification"],
    "CISSP": ["Certified Information Systems Security Professional", "Cybersecurity Certification"],
    "CISM": ["Certified Information Security Manager", "Cybersecurity Certification"],
    "CompTIA Security+": ["Cybersecurity Certification"],
    "CompTIA Network+": ["Networking Certification"],
    "CompTIA A+": ["IT Support Certification"],
    "CompTIA Linux+": ["Linux Certification"],
    "Certified Solutions Architect": ["AWS Certification"],
    "Certified Developer": ["AWS Certification"],
    "Certified SysOps Administrator": ["AWS Certification"],
    "Specialty Certification": ["AWS Certification"],
    "Professional Certification": ["AWS Certification"],
    "Azure AZ-900": ["Azure Fundamentals"],
    "Azure AZ-104": ["Azure Administrator Associate"],
    "Azure AZ-204": ["Azure Developer Associate"],
    "Azure AZ-303": ["Azure Architect Technologies (Retired)"],
    "Azure AZ-304": ["Azure Architect Design (Retired)"],
    "Azure AZ-400": ["Azure DevOps Engineer Expert"],
    "Azure AZ-500": ["Azure Security Engineer Associate"],
    "Azure AZ-700": ["Azure Network Engineer Associate"],
    "Azure AZ-800": ["Windows Server Hybrid Administrator Associate"],
    "Azure AZ-801": ["Windows Server Hybrid Administrator Associate"],
    "Azure DP-900": ["Azure Data Fundamentals"],
    "Azure DP-100": ["Azure Data Scientist Associate"],
    "Azure DP-203": ["Azure Data Engineer Associate"],
    "Azure AI-900": ["Azure AI Fundamentals"],
    "Azure AI-102": ["Azure AI Engineer Associate"],
    "Azure DA-100": ["Data Analyst Associate (Retired)"],
    "Azure PL-900": ["Power Platform Fundamentals"],
    "Azure PL-100": ["Power Platform App Maker Associate"],
    "Azure PL-200": ["Power Platform Functional Consultant Associate"],
    "Azure PL-300": ["Power BI Data Analyst Associate"],
    "Azure PL-400": ["Power Platform Developer Associate"],
    "Azure PL-500": ["Power Automate RPA Developer Associate"],
    "Azure MS-900": ["Microsoft 365 Fundamentals"],
    "Azure MS-100": ["Microsoft 365 Identity and Services (Retired)"],
    "Azure MS-101": ["Microsoft 365 Mobility and Security (Retired)"],
    "Azure MS-203": ["Microsoft 365 Messaging Administrator Associate"],
    "Azure MS-500": ["Microsoft 365 Security Administrator Associate"],
    "Azure MS-700": ["Microsoft Teams Administrator Associate"],
    "Azure MS-720": ["Microsoft Teams Voice Engineer Expert"],
    "Azure MS-740": ["Microsoft 365 Certified: Troubleshooting Microsoft Teams"],
    "Azure MS-600": ["Microsoft 365 Certified: Developer Associate"],
    "Azure SC-900": ["Microsoft Security, Compliance, and Identity Fundamentals"],
    "Azure SC-200": ["Microsoft Security Operations Analyst Associate"],
    "Azure SC-300": ["Microsoft Identity and Access Administrator Associate"],
    "Azure SC-400": ["Microsoft Information Protection Administrator Associate"],
    "Azure MD-100": ["Windows Client (Retired)"],
    "Azure MD-101": ["Managing Modern Desktops (Retired)"],
    "Azure MB-200": ["Microsoft Dynamics 365 Sales Functional Consultant Associate (Retired)"],
    "Azure MB-210": ["Microsoft Dynamics 365 Sales Functional Consultant Associate"],
    "Azure MB-220": ["Microsoft Dynamics 365 Marketing Functional Consultant Associate"],
    "Azure MB-230": ["Microsoft Dynamics 365 Customer Service Functional Consultant Associate"],
    "Azure MB-240": ["Microsoft Dynamics 365 Field Service Functional Consultant Associate"],
    "Azure MB-260": ["Microsoft Dynamics 365 Customer Data Platform Specialist"],
    "Azure MB-300": ["Microsoft Dynamics 365 Finance and Operations Apps Developer Associate (Retired)"],
    "Azure MB-310": ["Microsoft Dynamics 365 Finance Functional Consultant Associate"],
    "Azure MB-320": ["Microsoft Dynamics 365 Supply Chain Management, Manufacturing Functional Consultant Associate"],
    "Azure MB-330": ["Microsoft Dynamics 365 Supply Chain Management Functional Consultant Associate"],
    "Azure MB-340": ["Microsoft Dynamics 365 Commerce Functional Consultant Associate"],
    "Azure MB-400": ["Microsoft Dynamics 365 for Finance and Operations, Supply Chain Management Developer Associate (Retired)"],
    "Azure MB-500": ["Microsoft Dynamics 365: Finance and Operations Apps Developer Associate"],
    "Azure MB-600": ["Microsoft Dynamics 365 + Power Platform Solution Architect Expert"],
    "Azure MB-700": ["Microsoft Dynamics 365: Finance and Operations Apps Solution Architect Expert (Retired)"],
    "Azure MB-800": ["Microsoft Dynamics 365 Business Central Functional Consultant Associate"],
    "Azure MB-910": ["Microsoft Dynamics 365 Fundamentals (CRM)"],
    "Azure MB-920": ["Microsoft Dynamics 365 Fundamentals (ERP)"],
    "GCP ACE": ["Associate Cloud Engineer"],
    "GCP PCA": ["Professional Cloud Architect"],
    "GCP PDE": ["Professional Data Engineer"],
    "GCP PSE": ["Professional Security Engineer"],
    "GCP PML": ["Professional Machine Learning Engineer"],
    "GCP PSA": ["Professional Cloud Developer"],
    "GCP PCD": ["Professional Cloud DevOps Engineer"],
    "GCP PCN": ["Professional Cloud Network Engineer"],
    "GCP PSD": ["Professional Cloud Database Engineer"],
    "GCP PDA": ["Professional Cloud Data Architect"],
    "GCP PCI": ["Professional Cloud IoT Developer"],
    "GCP PWS": ["Professional Cloud Workload Migration Specialist"],
    "GCP PWA": ["Professional Cloud Application Developer"],
    "GCP PME": ["Professional Cloud Migration Engineer"],
    "GCP PMC": ["Professional Cloud Security Engineer"],
    "GCP PMD": ["Professional Cloud DevOps Engineer"],
    "GCP PMA": ["Professional Cloud Architect"],
    "GCP PMG": ["Professional Cloud Network Engineer"],
    "RHCSA": ["Red Hat Certified System Administrator"],
    "RHCE": ["Red Hat Certified Engineer"],
    "VCP-DCV": ["VMware Certified Professional - Data Center Virtualization"],
    "VCP-NV": ["VMware Certified Professional - Network Virtualization"],
    "VCP-DTM": ["VMware Certified Professional - Desktop and Mobility"],
    "VCP-CMA": ["VMware Certified Professional - Cloud Management and Automation"],
    "VCP-SEC": ["VMware Certified Professional - Security"],
    "VCP-DW": ["VMware Certified Professional - Digital Workspace"],
    "VCP-Cloud": ["VMware Certified Professional - Cloud"],
    "VCP-Desktop": ["VMware Certified Professional - Desktop"],
    "VCP-Mobility": ["VMware Certified Professional - Mobility"],
    "VCP-Network": ["VMware Certified Professional - Network"],
    "VCP-Security": ["VMware Certified Professional - Security"],
    "VCP-Cloud Management": ["VMware Certified Professional - Cloud Management"],
    "VCP-Automation": ["VMware Certified Professional - Automation"],
    "VCP-Digital Workspace": ["VMware Certified Professional - Digital Workspace"],
    "VCP-NSX": ["VMware Certified Professional - NSX"],
    "VCP-VMC on AWS": ["VMware Certified Professional - VMC on AWS"],
    "VCP-Tanzu": ["VMware Certified Professional - Tanzu"],
    "VCP-Carbon Black": ["VMware Certified Professional - Carbon Black"],
    "VCP-Workspace ONE": ["VMware Certified Professional - Workspace ONE"],
    "VCP-Horizon": ["VMware Certified Professional - Horizon"],
    "VCP-vSAN": ["VMware Certified Professional - vSAN"],
    "VCP-vSphere": ["VMware Certified Professional - vSphere"],
    "VCP-vCloud": ["VMware Certified Professional - vCloud"],
    "VCP-vRealize": ["VMware Certified Professional - vRealize"],
    "VCP-vRealize Automation": ["VMware Certified Professional - vRealize Automation"],
    "VCP-vRealize Operations": ["VMware Certified Professional - vRealize Operations"],
    "VCP-vRealize Log Insight": ["VMware Certified Professional - vRealize Log Insight"],
    "VCP-vRealize Network Insight": ["VMware Certified Professional - vRealize Network Insight"],
    "VCP-vRealize Suite": ["VMware Certified Professional - vRealize Suite"],
    "VCP-vRealize Cloud Management": ["VMware Certified Professional - vRealize Cloud Management"],
    "VCP-vRealize Automation Specialist": ["VMware Certified Professional - vRealize Automation Specialist"],
    "VCP-vRealize Operations Specialist": ["VMware Certified Professional - vRealize Operations Specialist"],
    "VCP-vRealize Log Insight Specialist": ["VMware Certified Professional - vRealize Log Insight Specialist"],
    "VCP-vRealize Network Insight Specialist": ["VMware Certified Professional - vRealize Network Insight Specialist"],
    "VCP-vRealize Suite Specialist": ["VMware Certified Professional - vRealize Suite Specialist"],
    "VCP-vRealize Cloud Management Specialist": ["VMware Certified Professional - vRealize Cloud Management Specialist"],
    "VCP-Cloud Native": ["VMware Certified Professional - Cloud Native"],
    "VCP-Cloud Native Application Developer": ["VMware Certified Professional - Cloud Native Application Developer"],
    "VCP-Cloud Native Platform Operator": ["VMware Certified Professional - Cloud Native Platform Operator"],
    "VCP-Cloud Native Security": ["VMware Certified Professional - Cloud Native Security"],
    "VCP-Cloud Native Storage": ["VMware Certified Professional - Cloud Native Storage"],
    "VCP-Cloud Native Networking": ["VMware Certified Professional - Cloud Native Networking"],
    "VCP-Cloud Native Operations": ["VMware Certified Professional - Cloud Native Operations"],
    "VCP-Cloud Native Automation": ["VMware Certified Professional - Cloud Native Automation"],
    "VCP-Cloud Native Observability": ["VMware Certified Professional - Cloud Native Observability"],
    "VCP-Cloud Native Data Management": ["VMware Certified Professional - Cloud Native Data Management"],
    "VCP-Cloud Native AI/ML": ["VMware Certified Professional - Cloud Native AI/ML"],
    "VCP-Cloud Native DevOps": ["VMware Certified Professional - Cloud Native DevOps"],
    "VCP-Cloud Native Microservices": ["VMware Certified Professional - Cloud Native Microservices"],
    "VCP-Cloud Native Serverless": ["VMware Certified Professional - Cloud Native Serverless"],
    "VCP-Cloud Native Edge": ["VMware Certified Professional - Cloud Native Edge"],
    "VCP-Cloud Native IoT": ["VMware Certified Professional - Cloud Native IoT"],
    "VCP-Cloud Native Blockchain": ["VMware Certified Professional - Cloud Native Blockchain"],
    "VCP-Cloud Native Quantum Computing": ["VMware Certified Professional - Cloud Native Quantum Computing"],
    "VCP-Cloud Native Robotics": ["VMware Certified Professional - Cloud Native Robotics"],
    "VCP-Cloud Native AR/VR": ["VMware Certified Professional - Cloud Native AR/VR"],
    "VCP-Cloud Native Gaming": ["VMware Certified Professional - Cloud Native Gaming"],
    "VCP-Cloud Native FinTech": ["VMware Certified Professional - Cloud Native FinTech"],
    "VCP-Cloud Native HealthTech": ["VMware Certified Professional - Cloud Native HealthTech"],
    "VCP-Cloud Native EduTech": ["VMware Certified Professional - Cloud Native EduTech"],
    "VCP-Cloud Native AgriTech": ["VMware Certified Professional - Cloud Native AgriTech"],
    "VCP-Cloud Native Smart City": ["VMware Certified Professional - Cloud Native Smart City"],
    "VCP-Cloud Native Smart Home": ["VMware Certified Professional - Cloud Native Smart Home"],
    "VCP-Cloud Native Smart Manufacturing": ["VMware Certified Professional - Cloud Native Smart Manufacturing"],
    "VCP-Cloud Native Smart Retail": ["VMware Certified Professional - Cloud Native Smart Retail"],
    "VCP-Cloud Native Smart Logistics": ["VMware Certified Professional - Cloud Native Smart Logistics"],
    "VCP-Cloud Native Smart Transportation": ["VMware Certified Professional - Cloud Native Smart Transportation"],
    "VCP-Cloud Native Smart Energy": ["VMware Certified Professional - Cloud Native Smart Energy"],
    "VCP-Cloud Native Smart Utilities": ["VMware Certified Professional - Cloud Native Smart Utilities"],
    "VCP-Cloud Native Smart Environment": ["VMware Certified Professional - Cloud Native Smart Environment"],
    "VCP-Cloud Native Smart Water": ["VMware Certified Professional - Cloud Native Smart Water"],
    "VCP-Cloud Native Smart Waste": ["VMware Certified Professional - Cloud Native Waste"],
    "VCP-Cloud Native Smart Agriculture": ["VMware Certified Professional - Cloud Native Agriculture"],
    "VCP-Cloud Native Smart Healthcare": ["VMware Certified Professional - Cloud Native Healthcare"],
    "VCP-Cloud Native Smart Education": ["VMware Certified Professional - Cloud Native Education"],
    "VCP-Cloud Native Smart Finance": ["VMware Certified Professional - Cloud Native Finance"],
    "VCP-Cloud Native Smart Government": ["VMware Certified Professional - Cloud Native Government"],
    "VCP-Cloud Native Smart City Infrastructure": ["VMware Certified Professional - Cloud Native Smart City Infrastructure"],
    "VCP-Cloud Native Smart City Services": ["VMware Certified Professional - Cloud Native Smart City Services"],
    "VCP-Cloud Native Smart City Mobility": ["VMware Certified Professional - Cloud Native Smart City Mobility"],
    "VCP-Cloud Native Smart City Environment": ["VMware Certified Professional - Cloud Native Smart City Environment"],
    "VCP-Cloud Native Smart City Governance": ["VMware Certified Professional - Cloud Native Smart City Governance"],
    "VCP-Cloud Native Smart City Security": ["VMware Certified Professional - Cloud Native Smart City Security"],
    "VCP-Cloud Native Smart City Data": ["VMware Certified Professional - Cloud Native Smart City Data"],
    "VCP-Cloud Native Smart City AI/ML": ["VMware Certified Professional - Cloud Native Smart City AI/ML"],
    "VCP-Cloud Native Smart City IoT": ["VMware Certified Professional - Cloud Native Smart City IoT"],
    "VCP-Cloud Native Smart City Blockchain": ["VMware Certified Professional - Cloud Native Smart City Blockchain"],
    "VCP-Cloud Native Smart City Quantum Computing": ["VMware Certified Professional - Cloud Native Smart City Quantum Computing"],
    "VCP-Cloud Native Smart City Robotics": ["VMware Certified Professional - Cloud Native Smart City Robotics"],
    "VCP-Cloud Native Smart City AR/VR": ["VMware Certified Professional - Cloud Native Smart City AR/VR"],
    "VCP-Cloud Native Smart City Gaming": ["VMware Certified Professional - Cloud Native Smart City Gaming"],
    "VCP-Cloud Native Smart City FinTech": ["VMware Certified Professional - Cloud Native Smart City FinTech"],
    "VCP-Cloud Native Smart City HealthTech": ["VMware Certified Professional - Cloud Native Smart City HealthTech"],
    "VCP-Cloud Native Smart City EduTech": ["VMware Certified Professional - Cloud Native Smart City EduTech"],
    "VCP-Cloud Native Smart City AgriTech": ["VMware Certified Professional - Cloud Native Smart City AgriTech"],
    "VCP-Cloud Native Smart City Smart Home": ["VMware Certified Professional - Cloud Native Smart City Smart Home"],
    "VCP-Cloud Native Smart City Smart Manufacturing": ["VMware Certified Professional - Cloud Native Smart City Smart Manufacturing"],
    "VCP-Cloud Native Smart City Smart Retail": ["VMware Certified Professional - Cloud Native Smart City Smart Retail"],
    "VCP-Cloud Native Smart City Smart Logistics": ["VMware Certified Professional - Cloud Native Smart City Smart Logistics"],
    "VCP-Cloud Native Smart City Smart Transportation": ["VMware Certified Professional - Cloud Native Smart City Smart Transportation"],
    "VCP-Cloud Native Smart City Smart Energy": ["VMware Certified Professional - Cloud Native Smart City Smart Energy"],
    "VCP-Cloud Native Smart City Smart Utilities": ["VMware Certified Professional - Cloud Native Smart City Smart Utilities"],
    "VCP-Cloud Native Smart City Smart Environment": ["VMware Certified Professional - Cloud Native Smart City Smart Environment"],
    "VCP-Cloud Native Smart City Smart Water": ["VMware Certified Professional - Cloud Native Smart City Smart Water"],
    "VCP-Cloud Native Smart City Smart Waste": ["VMware Certified Professional - Cloud Native Smart City Waste"],
    "VCP-Cloud Native Smart City Smart Agriculture": ["VMware Certified Professional - Cloud Native Smart City Agriculture"],
    "VCP-Cloud Native Smart City Smart Healthcare": ["VMware Certified Professional - Cloud Native Smart City Healthcare"],
    "VCP-Cloud Native Smart City Smart Education": ["VMware Certified Professional - Cloud Native Smart City Education"],
    "VCP-Cloud Native Smart City Smart Finance": ["VMware Certified Professional - Cloud Native Smart City Finance"],
    "VCP-Cloud Native Smart City Smart Government": ["VMware Certified Professional - Cloud Native Smart City Government"]
}
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
            return model, None # Return None for ml_model as it's not used in the new flow
        except Exception as e:
            st.error(f"❌ Error loading AI models: {e}. Please ensure 'all-MiniLM-L6-v2' model can be loaded.")
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

def _process_single_resume_for_screener_page(file_name, text, jd_text, jd_embedding, 
                                             resume_embedding, jd_name_for_results,
                                             max_experience, 
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
        if target_company_name and target_company_name != "None" and target_company_name in COMPANY_SKILL_PROFILES:
            company_skills = set(s.lower() for s in COMPANY_SKILL_PROFILES[target_company_name])
            candidate_matched_company_skills = resume_skills.intersection(company_skills)
            if company_skills: # Avoid division by zero
                company_skill_match_ratio = len(candidate_matched_company_skills) / len(company_skills)
                company_boost_percentage = company_skill_match_ratio * 5 # Max 5% boost for company fit

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
            "Company Fit Assessment": llm_feedback_text, # Repurposed to show candidate feedback
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

    if target_company_name and target_company_name != "None" and target_company_name in COMPANY_SKILL_PROFILES:
        company_skills = set(s.lower() for s in COMPANY_SKILL_PROFILES[target_company_name])
        candidate_matched_company_skills = set(s.lower() for s in matched_skills).intersection(company_skills)
        if candidate_matched_company_skills:
            feedback_parts.append(f"- **Company Fit ({target_company_name}):** You demonstrate a good fit with {target_company_name}'s preferred technologies/skills, including: {', '.join(sorted(list(candidate_matched_company_skills)))}. This is a strong positive for roles within this company.")
        else:
            feedback_parts.append(f"- **Company Fit ({target_company_name}):** While your general skills are good, consider exploring more skills specific to {target_company_name} to enhance your profile for future applications with them.")


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


    # Input for Job Description
    st.subheader("1. Enter Job Description")
    
    jd_options = load_jds_from_folder()
    jd_selection_method = st.radio(
        "Choose JD Input Method:",
        ("Paste JD", "Select from Library"),
        key="jd_selection_method"
    )

    jd_text = ""
    jd_name_for_results = "User Provided JD"

    if jd_selection_method == "Paste JD":
        jd_text = st.text_area(
            "Paste the Job Description here:",
            height=300,
            key="jd_text_input",
            placeholder="E.g., 'We are looking for a Software Engineer with strong Python, AWS, and React skills...'"
        )
    else: # Select from Library
        selected_jd_file = st.selectbox(
            "Select a Job Description from your library:",
            options=list(jd_options.keys()),
            key="selected_jd_file"
        )
        if selected_jd_file != "Paste New JD":
            jd_text = jd_options[selected_jd_file]
            jd_name_for_results = selected_jd_file
            st.text_area("Selected JD Content (read-only):", value=jd_text, height=300, disabled=True)
        else:
            st.info("Please select a JD file or switch to 'Paste JD' to enter a new one.")


    # Input for Max Experience
    st.subheader("2. Set Max Experience (Years)")
    max_experience = st.number_input(
        "Maximum years of experience desired for this role:",
        min_value=0,
        max_value=30,
        value=10,
        step=1,
        help="Candidates with experience significantly above this may be considered overqualified."
    )

    # Company Selection
    st.subheader("3. Select Target Company (Optional for Score Boost)")
    company_names = ["None"] + sorted(list(COMPANY_SKILL_PROFILES.keys()))
    target_company_name = st.selectbox(
        "Select a company to apply a skill-based score boost (if applicable):",
        options=company_names,
        index=0 # Default to "None"
    )
    if target_company_name != "None":
        st.info(f"A small score boost will be applied if your resume matches skills important to {target_company_name}.")


    # File Uploader for Resume
    st.subheader("4. Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload a resume (PDF only)",
        type=["pdf"],
        help="Please upload a text-selectable PDF resume for best results."
    )

    if st.button("🚀 Screen Resume"):
        if not jd_text.strip():
            st.error("Please provide a Job Description.")
        elif not uploaded_file:
            st.error("Please upload a resume.")
        else:
            with st.spinner("Processing resume and generating insights..."):
                try:
                    # Extract text from uploaded resume
                    resume_bytes = uploaded_file.read()
                    resume_text = extract_text_from_file(resume_bytes, uploaded_file.name, uploaded_file.type)

                    if resume_text.startswith("[ERROR]"):
                        st.error(resume_text)
                        st.session_state.results = None
                        return

                    # Generate embeddings for JD and resume
                    jd_embedding = global_sentence_model.encode(clean_text(jd_text), convert_to_tensor=True)
                    resume_embedding = global_sentence_model.encode(clean_text(resume_text), convert_to_tensor=True)

                    # Process the resume
                    screening_results = _process_single_resume_for_screener_page(
                        file_name=uploaded_file.name,
                        text=resume_text,
                        jd_text=jd_text,
                        jd_embedding=jd_embedding,
                        resume_embedding=resume_embedding,
                        jd_name_for_results=jd_name_for_results,
                        max_experience=max_experience,
                        _global_ml_model=global_ml_model,
                        target_company_name=target_company_name # Pass selected company
                    )
                    st.session_state.results = screening_results
                    st.success("Analysis complete! See the results below.")

                    # --- Automatic Certificate Sending ---
                    if st.session_state.results and st.session_state.results['Email'] != 'Not Found':
                        gmail_address = st.secrets.get("GMAIL_ADDRESS")
                        gmail_app_password = st.secrets.get("GMAIL_APP_PASSWORD")

                        if gmail_address and gmail_app_password:
                            st.info("Attempting to automatically send certificate...")
                            certificate_html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>ScreenerPro Certificate</title>
                                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
                                <style>
                                    body {{ font-family: 'Inter', sans-serif; background-color: #f0f2f6; color: #333; margin: 0; padding: 20px; }}
                                    .certificate-container {{
                                        width: 100%; max-width: 800px; margin: 20px auto; padding: 40px;
                                        background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                                        text-align: center; border: 5px solid #4CAF50;
                                        box-sizing: border-box;
                                    }}
                                    .header {{ color: #4CAF50; font-size: 2.5em; font-weight: 700; margin-bottom: 20px; }}
                                    .subheader {{ font-size: 1.5em; color: #555; margin-bottom: 30px; }}
                                    .name {{ font-size: 2.2em; font-weight: 700; color: #333; margin-bottom: 10px; text-transform: capitalize; }}
                                    .award-text {{ font-size: 1.1em; margin-bottom: 20px; line-height: 1.6; }}
                                    .score {{ font-size: 3em; font-weight: 700; color: #007BFF; margin: 20px 0; }}
                                    .rank {{ font-size: 1.8em; font-weight: 700; color: #FFD700; margin-bottom: 30px; }}
                                    .details {{ font-size: 0.9em; color: #777; margin-top: 30px; line-height: 1.5; }}
                                    .signature-section {{ margin-top: 50px; display: flex; justify-content: space-around; align-items: flex-end; }}
                                    .signature-block {{ text-align: center; }}
                                    .signature-line {{ border-top: 1px solid #aaa; width: 150px; margin: 10px auto 5px auto; }}
                                    .signature-name {{ font-weight: 600; font-size: 1em; }}
                                    .footer {{ margin-top: 40px; font-size: 0.8em; color: #999; }}
                                    .qr-code {{ margin-top: 20px; }}
                                    @media (max-width: 600px) {{
                                        .certificate-container {{ padding: 20px; }}
                                        .header {{ font-size: 1.8em; }}
                                        .subheader {{ font-size: 1.2em; }}
                                        .name {{ font-size: 1.8em; }}
                                        .score {{ font-size: 2.5em; }}
                                        .rank {{ font-size: 1.4em; }}
                                        .signature-section {{ flex-direction: column; }}
                                        .signature-block {{ margin-bottom: 20px; }}
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="certificate-container">
                                    <div class="header">ScreenerPro</div>
                                    <div class="subheader">Certificate of Achievement</div>
                                    <p class="award-text">This certifies that</p>
                                    <div class="name">{st.session_state.results['Candidate Name']}</div>
                                    <p class="award-text">has successfully completed the automated resume screening process for the role of <strong>{st.session_state.results['JD Used']}</strong>, demonstrating a significant match in skills and experience.</p>
                                    <div class="score">{st.session_state.results['Skill Match']:.1f}%</div>
                                    <div class="rank">{st.session_state.results['Certificate Rank']}</div>
                                    <div class="details">
                                        <p><strong>Date Screened:</strong> {st.session_state.results['Date Screened']}</p>
                                        <p><strong>Certificate ID:</strong> {st.session_state.results['Certificate ID']}</p>
                                        <p><strong>Semantic Match:</strong> {st.session_state.results['Semantic Match']:.2f}</p>
                                        <p><strong>Years Experience:</strong> {st.session_state.results['Years Experience']:.1f}</p>
                                        <p><strong>CGPA (4.0 Scale):</strong> {st.session_state.results['CGPA (4.0 Scale)'] if st.session_state.results['CGPA (4.0 Scale)'] is not None else 'N/A'}</p>
                                    </div>
                                    <div class="signature-section">
                                        <div class="signature-block">
                                            <div class="signature-line"></div>
                                            <div class="signature-name">ScreenerPro Team</div>
                                            <div>Automated Assessment</div>
                                        </div>
                                    </div>
                                    <div class="footer">
                                        Verify this certificate at: {CERTIFICATE_HOSTING_URL}?id={st.session_state.results['Certificate ID']}
                                    </div>
                                </div>
                            </body>
                            </html>
                            """
                            send_certificate_email(
                                recipient_email=st.session_state.results['Email'],
                                candidate_name=st.session_state.results['Candidate Name'],
                                score=st.session_state.results['Skill Match'],
                                certificate_html_content=certificate_html_content,
                                certificate_public_url=f"{CERTIFICATE_HOSTING_URL}?id={st.session_state.results['Certificate ID']}",
                                gmail_address=gmail_address,
                                gmail_app_password=gmail_app_password
                            )
                        else:
                            st.warning("Email sending not configured. Certificate was not sent automatically. Please check your Streamlit secrets for GMAIL_ADDRESS and GMAIL_APP_PASSWORD.")
                    elif st.session_state.results and st.session_state.results['Email'] == 'Not Found':
                        st.warning("No email address found in the resume. Certificate could not be sent automatically.")


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

        certificate_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ScreenerPro Certificate</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Inter', sans-serif; background-color: #f0f2f6; color: #333; margin: 0; padding: 20px; }}
                .certificate-container {{
                    width: 100%; max-width: 800px; margin: 20px auto; padding: 40px;
                    background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    text-align: center; border: 5px solid #4CAF50;
                    box-sizing: border-box; /* Include padding and border in the element's total width and height */
                }}
                .header {{ color: #4CAF50; font-size: 2.5em; font-weight: 700; margin-bottom: 20px; }}
                .subheader {{ font-size: 1.5em; color: #555; margin-bottom: 30px; }}
                .name {{ font-size: 2.2em; font-weight: 700; color: #333; margin-bottom: 10px; text-transform: capitalize; }}
                .award-text {{ font-size: 1.1em; margin-bottom: 20px; line-height: 1.6; }}
                .score {{ font-size: 3em; font-weight: 700; color: #007BFF; margin: 20px 0; }}
                .rank {{ font-size: 1.8em; font-weight: 700; color: #FFD700; margin-bottom: 30px; }}
                .details {{ font-size: 0.9em; color: #777; margin-top: 30px; line-height: 1.5; }}
                .signature-section {{ margin-top: 50px; display: flex; justify-content: space-around; align-items: flex-end; }}
                .signature-block {{ text-align: center; }}
                .signature-line {{ border-top: 1px solid #aaa; width: 150px; margin: 10px auto 5px auto; }}
                .signature-name {{ font-weight: 600; font-size: 1em; }}
                .footer {{ margin-top: 40px; font-size: 0.8em; color: #999; }}
                .qr-code {{ margin-top: 20px; }}
                @media (max-width: 600px) {{
                    .certificate-container {{ padding: 20px; }}
                    .header {{ font-size: 1.8em; }}
                    .subheader {{ font-size: 1.2em; }}
                    .name {{ font-size: 1.8em; }}
                    .score {{ font-size: 2.5em; }}
                    .rank {{ font-size: 1.4em; }}
                    .signature-section {{ flex-direction: column; }}
                    .signature-block {{ margin-bottom: 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="certificate-container">
                <div class="header">ScreenerPro</div>
                <div class="subheader">Certificate of Achievement</div>
                <p class="award-text">This certifies that</p>
                <div class="name">{results['Candidate Name']}</div>
                <p class="award-text">has successfully completed the automated resume screening process for the role of <strong>{results['JD Used']}</strong>, demonstrating a significant match in skills and experience.</p>
                <div class="score">{results['Skill Match']:.1f}%</div>
                <div class="rank">{results['Certificate Rank']}</div>
                <div class="details">
                    <p><strong>Date Screened:</strong> {results['Date Screened']}</p>
                    <p><strong>Certificate ID:</strong> {results['Certificate ID']}</p>
                    <p><strong>Semantic Match:</strong> {results['Semantic Match']:.2f}</p>
                    <p><strong>Years Experience:</strong> {results['Years Experience']:.1f}</p>
                    <p><strong>CGPA (4.0 Scale):</strong> {results['CGPA (4.0 Scale)'] if results['CGPA (4.0 Scale)'] is not None else 'N/A'}</p>
                </div>
                <div class="signature-section">
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-name">ScreenerPro Team</div>
                        <div>Automated Assessment</div>
                    </div>
                </div>
                <div class="footer">
                    Verify this certificate at: {CERTIFICATE_HOSTING_URL}?id={results['Certificate ID']}
                </div>
            </div>
        </body>
        </html>
        """

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
