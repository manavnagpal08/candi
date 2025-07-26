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

# --- Removed: Company Skill Pr
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

        # Generate candidate feedback (no LLM)
        candidate_ai_feedback = generate_candidate_feedback(
            candidate_name=candidate_name,
            score=match_score,
            years_exp=exp,
            semantic_similarity=semantic_score_from_feedback,
            cgpa=cgpa,
            matched_skills=matched_skills_list,
            missing_skills=missing_skills_list
        )

        # Assign to variables used by downstream functions
        score = match_score 
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
def generate_candidate_feedback(candidate_name, score, years_exp, semantic_similarity, cgpa, matched_skills, missing_skills):
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

def resume_screener_page():
    st.title("📄 AI-Powered Resume Screener")
    st.markdown("Upload a resume and paste a Job Description to get an instant match score and personalized feedback!")

    # Initialize session state for results if not already present
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'jd_text_input' not in st.session_state:
        st.session_state.jd_text_input = ""

    # Input for Job Description
    st.subheader("1. Enter Job Description")
    jd_text = st.text_area(
        "Paste the Job Description here:",
        height=300,
        key="jd_text_input",
        placeholder="E.g., 'We are looking for a Software Engineer with strong Python, AWS, and React skills...'"
    )

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

    # File Uploader for Resume
    st.subheader("3. Upload Resume")
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
                        jd_name_for_results="User Provided JD", # Or a name you define
                        max_experience=max_experience,
                        _global_ml_model=global_ml_model # Pass the loaded model
                    )
                    st.session_state.results = screening_results
                    st.success("Analysis complete! See the results below.")

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

        # Email certificate section
        with st.expander("Email Certificate"):
            recipient_email = st.text_input("Enter recipient email address:", value=results['Email'] if results['Email'] != 'Not Found' else '')
            if st.button("Send Certificate via Email"):
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
