import streamlit as st
import pdfplumber
import re
import os
import io
import pandas as pd
from collections import Counter
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from datetime import datetime
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytesseract
from PIL import Image
import random # Added for LLM-style summary variability

# --- Global Variables and Configuration ---
# Set Tesseract path if not in PATH (adjust as needed for your system)
# pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract' # Example for macOS
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Example for Windows

# Firebase configuration (will be populated by the environment)
firebase_config = json.loads(os.environ.get('__firebase_config', '{}'))
app_id = os.environ.get('__app_id', 'default-app-id')

# Removed LLM API Configuration as it's no longer used for HR summary
# API_KEY = ""
# GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# --- Load Models and Data ---
@st.cache_resource
def load_sentence_transformer_model():
    """Loads the SentenceTransformer model for semantic similarity."""
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_sentence_transformer_model()

# Load skills library from a text file
def load_skills_library(file_path="data/skills_library.txt"):
    """Loads a list of skills from a text file."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            skills = [line.strip().lower() for line in f if line.strip()]
        return sorted(list(set(skills)))
    return []

MASTER_SKILLS = load_skills_library()

# Define skill categories and map master skills to them
SKILL_CATEGORIES = {
    "Programming Languages": ["python", "java", "c++", "javascript", "typescript", "go", "ruby", "php", "swift", "kotlin", "rust", "c#", "scala", "r", "perl", "matlab", "shell scripting", "bash", "powershell"],
    "Web Technologies": ["html", "css", "javascript", "react", "angular", "vue.js", "node.js", "express.js", "django", "flask", "spring", "asp.net", "php", "laravel", "ruby on rails", "bootstrap", "tailwind css", "sass", "less", "webpack", "babel", "npm", "yarn", "rest api", "graphql", "websocket", "ajax", "json", "xml"],
    "Cloud Platforms": ["aws", "azure", "google cloud platform", "gcp", "kubernetes", "docker", "terraform", "ansible", "jenkins", "gitlab ci/cd", "circleci", "azure devops", "aws amplify", "firebase", "heroku", "netlify", "vercel"],
    "Databases": ["sql", "mysql", "postgresql", "mongodb", "cassandra", "redis", "elasticsearch", "sqlite", "oracle", "microsoft sql server", "nosql", "dynamodb", "cosmosdb", "bigquery", "snowflake", "neo4j"],
    "Data Science/ML/AI": ["pandas", "numpy", "scikit-learn", "tensorflow", "keras", "pytorch", "r", "sagemaker", "azure ml", "google ai platform", "nlp", "computer vision", "deep learning", "machine learning", "data analysis", "data visualization", "tableau", "power bi", "apache spark", "hadoop", "kafka", "airflow"],
    "Operating Systems": ["linux", "unix", "windows", "macos"],
    "Tools & Methodologies": ["git", "jira", "confluence", "agile", "scrum", "kanban", "devops", "ci/cd", "unit testing", "integration testing", "api testing", "selenium", "postman", "swagger", "vs code", "intellij idea", "eclipse", "pycharm", "jupyter", "apache maven", "gradle"],
    "Soft Skills": ["communication", "teamwork", "problem-solving", "leadership", "adaptability", "critical thinking", "creativity", "time management", "attention to detail", "interpersonal skills", "negotiation", "presentation skills", "mentoring", "coaching"],
    "Other": [] # For skills not fitting neatly into other categories
}

# Populate SKILL_CATEGORIES with MASTER_SKILLS that are not explicitly listed
for skill in MASTER_SKILLS:
    found = False
    for category, keywords in SKILL_CATEGORIES.items():
        if skill in keywords:
            found = True
            break
    if not found:
        SKILL_CATEGORIES["Other"].append(skill)


# Load predefined company skill profiles
COMPANY_SKILL_PROFILES = {
    "Google": ["python", "java", "go", "c++", "kubernetes", "gcp", "tensorflow", "pytorch", "machine learning", "data structures", "algorithms", "distributed systems", "big data", "cloud computing", "nlp", "computer vision", "backend development", "frontend development", "android development", "site reliability engineering", "sre"],
    "Microsoft": ["c#", "azure", "asp.net", "java", "python", "power bi", "sql server", "azure devops", "machine learning", "cloud computing", "windows", "office 365", "microsoft dynamics", "data science", "ai", "full-stack development"],
    "Amazon": ["java", "python", "aws", "distributed systems", "microservices", "data structures", "algorithms", "cloud computing", "devops", "linux", "e-commerce", "logistics", "machine learning", "sagemaker", "backend development"],
    "Meta (Facebook)": ["python", "react", "php", "javascript", "graphql", "pytorch", "machine learning", "data science", "computer vision", "nlp", "social media", "distributed systems", "mobile development", "backend development", "frontend development", "ai"],
    "Apple": ["swift", "objective-c", "macos", "ios", "xcode", "c++", "javascript", "ui/ux design", "product design", "hardware engineering", "software engineering", "privacy", "security", "machine learning", "core ml"],
    "Netflix": ["java", "python", "aws", "microservices", "distributed systems", "big data", "streaming", "devops", "machine learning", "recommendation systems", "data engineering", "cloud architecture", "backend development"],
    "OpenAI": ["python", "pytorch", "tensorflow", "machine learning", "deep learning", "nlp", "large language models", "generative ai", "reinforcement learning", "ai research", "data science", "distributed systems", "cloud platforms"],
    "Salesforce": ["apex", "visualforce", "javascript", "salesforce platform", "crm", "cloud computing", "enterprise software", "integration", "api development", "ui/ux", "frontend development", "backend development"],
    "IBM": ["java", "python", "javascript", "cloud computing", "ai", "machine learning", "data science", "blockchain", "cybersecurity", "quantum computing", "enterprise solutions", "watson", "red hat", "linux"],
    "Intel": ["c++", "assembly", "python", "hardware engineering", "software engineering", "semiconductors", "microprocessors", "embedded systems", "linux", "performance optimization", "ai accelerators", "fpga"],
    "NVIDIA": ["cuda", "c++", "python", "deep learning", "machine learning", "gpu programming", "computer graphics", "ai research", "robotics", "computer vision", "gaming", "data science"],
    "Adobe": ["c++", "javascript", "python", "creative cloud", "photoshop", "illustrator", "premiere pro", "ui/ux design", "web development", "cloud services", "digital marketing", "document cloud"],
    "Cisco": ["python", "java", "c++", "networking", "cybersecurity", "cloud computing", "collaboration tools", "iot", "software defined networking", "devnet", "network automation"],
    "Oracle": ["java", "sql", "oracle database", "cloud infrastructure", "enterprise software", "fusion applications", "data management", "ai", "machine learning", "cloud engineering"],
    "SAP": ["abap", "java", "javascript", "sap erp", "s/4hana", "cloud computing", "enterprise software", "business intelligence", "data warehousing", "crm", "supply chain management"],
    "Qualcomm": ["c++", "assembly", "python", "mobile technologies", "wireless communication", "5g", "chip design", "embedded systems", "signal processing", "machine learning", "iot"],
    "Tesla": ["python", "c++", "embedded systems", "robotics", "machine learning", "ai", "automotive", "battery technology", "power electronics", "software engineering", "full self-driving", "manufacturing automation"],
    "SpaceX": ["python", "c++", "aerospace engineering", "robotics", "embedded systems", "data analysis", "machine learning", "propulsion", "avionics", "software engineering", "starlink", "reusable rockets"],
    "Palantir": ["python", "java", "scala", "big data", "data analysis", "data science", "machine learning", "distributed systems", "cloud computing", "cybersecurity", "government solutions", "enterprise software"],
    "Stripe": ["ruby", "python", "go", "java", "javascript", "payments", "fintech", "api development", "distributed systems", "cloud infrastructure", "security", "backend development", "frontend development"],
    "Coinbase": ["go", "ruby", "javascript", "blockchain", "cryptocurrency", "fintech", "security", "distributed systems", "cloud platforms", "backend development", "frontend development"],
    "Databricks": ["scala", "python", "apache spark", "big data", "data engineering", "data science", "machine learning", "cloud platforms", "data warehousing", "delta lake", "mlflow"],
    "Snowflake": ["sql", "python", "java", "data warehousing", "cloud data platform", "data engineering", "data science", "cloud computing", "etl", "data analytics"],
    "ServiceNow": ["javascript", "servicenow platform", "it service management", "itsm", "cloud computing", "enterprise software", "workflow automation", "low-code development"],
    "Workday": ["java", "scala", "cloud computing", "enterprise software", "hrms", "financial management", "data analytics", "ui/ux"],
    "Zoom": ["c++", "javascript", "python", "video conferencing", "real-time communication", "cloud infrastructure", "scalable systems", "audio/video processing"],
    "ByteDance (TikTok)": ["go", "python", "java", "machine learning", "recommendation systems", "short-form video", "distributed systems", "cloud platforms", "data science", "backend development", "frontend development"],
    "Tencent": ["java", "c++", "python", "gaming", "social media", "cloud computing", "ai", "fintech", "web development", "mobile development", "distributed systems"],
    "Alibaba": ["java", "python", "cloud computing", "e-commerce", "fintech", "logistics", "ai", "machine learning", "big data", "distributed systems"],
    "Baidu": ["python", "c++", "deep learning", "machine learning", "ai", "nlp", "computer vision", "autonomous driving", "search engine", "cloud computing"],
    "Salesforce": ["apex", "visualforce", "javascript", "salesforce platform", "crm", "cloud computing", "enterprise software", "integration", "api development", "ui/ux", "frontend development", "backend development"],
    "Accenture": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "consulting", "digital transformation", "sap", "oracle", "cybersecurity"],
    "Deloitte": ["data analytics", "cybersecurity", "cloud computing", "ai", "machine learning", "consulting", "risk management", "financial advisory", "strategy"],
    "PwC": ["data analytics", "cybersecurity", "cloud computing", "ai", "machine learning", "consulting", "audit", "tax", "advisory"],
    "EY": ["data analytics", "cybersecurity", "cloud computing", "ai", "machine learning", "consulting", "audit", "tax", "advisory"],
    "KPMG": ["data analytics", "cybersecurity", "cloud computing", "ai", "machine learning", "consulting", "audit", "tax", "advisory"],
    "Capgemini": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Wipro": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Infosys": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "TCS": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "HCLTech": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Cognizant": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "LTIMindtree": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Tech Mahindra": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Mindtree": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "consulting", "sap", "oracle"],
    "Persistent Systems": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation", "product engineering"],
    "Zensar Technologies": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation"],
    "Mphasis": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation"],
    "Coforge": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation"],
    "Happiest Minds": ["java", "python", "cloud computing", "data analytics", "ai", "machine learning", "digital transformation"],
    "Tata Communications": ["networking", "telecom", "cloud computing", "cybersecurity", "iot", "data centers"],
    "Reliance Jio": ["telecom", "digital services", "cloud computing", "ai", "machine learning", "fintech", "e-commerce"],
    "Vodafone Idea": ["telecom", "networking", "digital services"],
    "Airtel": ["telecom", "networking", "digital services", "fintech"],
    "WNS Global Services": ["bpo", "data analytics", "digital transformation", "customer experience"],
    "Genpact": ["bpo", "data analytics", "digital transformation", "ai", "machine learning", "process transformation"],
    "EXL Service": ["data analytics", "operations management", "digital transformation", "ai", "machine learning"],
    "Concentrix": ["customer experience", "bpo", "digital transformation", "ai"],
    "Teleperformance": ["customer experience", "bpo", "digital transformation"],
    "Sutherland": ["digital transformation", "customer experience", "bpo", "ai", "machine learning"],
    "Infosys BPM": ["bpo", "digital transformation", "process optimization"],
    "TCS BPS": ["bpo", "digital transformation", "process optimization"],
    "Wipro BPS": ["bpo", "digital transformation", "process optimization"],
    "HCLTech BPS": ["bpo", "digital transformation", "process optimization"],
    "Cognizant BPS": ["bpo", "digital transformation", "process optimization"],
    "LTIMindtree BPS": ["bpo", "digital transformation", "process optimization"],
    "Tech Mahindra BPS": ["bpo", "digital transformation", "process optimization"],
    "Mindtree BPS": ["bpo", "digital transformation", "process optimization"],
    "Persistent Systems BPS": ["bpo", "digital transformation", "process optimization"],
    "Zensar Technologies BPS": ["bpo", "digital transformation", "process optimization"],
    "Mphasis BPS": ["bpo", "digital transformation", "process optimization"],
    "Coforge BPS": ["bpo", "digital transformation", "process optimization"],
    "Happiest Minds BPS": ["bpo", "digital transformation", "process optimization"],
    "Tata Communications BPS": ["bpo", "digital transformation", "process optimization"],
    "Reliance Jio BPS": ["bpo", "digital transformation", "process optimization"],
    "Vodafone Idea BPS": ["bpo", "digital transformation", "process optimization"],
    "Airtel BPS": ["bpo", "digital transformation", "process optimization"],
    "WNS Global Services BPS": ["bpo", "digital transformation", "process optimization"],
    "Genpact BPS": ["bpo", "digital transformation", "process optimization"],
    "EXL Service BPS": ["bpo", "digital transformation", "process optimization"],
    "Concentrix BPS": ["bpo", "digital transformation", "process optimization"],
    "Teleperformance BPS": ["bpo", "digital transformation", "process optimization"],
    "Sutherland BPS": ["bpo", "digital transformation", "process optimization"],
}


# Load course database
COURSE_DATABASE = [
    {"skill": "Python", "course": "Python for Everybody", "platform": "Coursera", "link": "https://www.coursera.org/specializations/python"},
    {"skill": "Data Science", "course": "IBM Data Science Professional Certificate", "platform": "Coursera", "link": "https://www.coursera.org/professional-certificates/ibm-data-science"},
    {"skill": "Machine Learning", "course": "Machine Learning by Andrew Ng", "platform": "Coursera", "link": "https://www.coursera.org/learn/machine-learning"},
    {"skill": "Deep Learning", "course": "Deep Learning Specialization", "platform": "Coursera", "link": "https://www.coursera.org/specializations/deep-learning"},
    {"skill": "SQL", "course": "SQL for Data Science", "platform": "Coursera", "link": "https://www.coursera.org/learn/sql-for-data-science"},
    {"skill": "React", "course": "React - The Complete Guide (incl Hooks, React Router, Redux)", "platform": "Udemy", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-hooks-react-router-redux/"},
    {"skill": "AWS", "course": "AWS Certified Solutions Architect - Associate", "platform": "Udemy", "link": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/"},
    {"skill": "Azure", "course": "AZ-900: Microsoft Azure Fundamentals", "platform": "Udemy", "link": "https://www.udemy.com/course/az-900-microsoft-azure-fundamentals-prep-new-2023/"},
    {"skill": "Docker", "course": "Docker & Kubernetes: The Complete Guide", "platform": "Udemy", "link": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/"},
    {"skill": "Kubernetes", "course": "Kubernetes for the Absolute Beginners - Hands-on", "platform": "Udemy", "link": "https://www.udemy.com/course/kubernetes-for-the-absolute-beginners-hands-on/"},
    {"skill": "Git", "course": "Git Complete: The definitive, step-by-step guide to Git", "platform": "Udemy", "link": "https://www.udemy.com/course/git-complete/"},
    {"skill": "JavaScript", "course": "The Complete JavaScript Course 2024: From Zero to Expert!", "platform": "Udemy", "link": "https://www.udemy.com/course/the-complete-javascript-course/"},
    {"skill": "Java", "course": "Java Programming Masterclass for Software Developers", "platform": "Udemy", "link": "https://www.udemy.com/course/java-the-complete-java-developer-course/"},
    {"skill": "Data Structures & Algorithms", "course": "Mastering Data Structures & Algorithms using C and C++", "platform": "Udemy", "link": "https://www.udemy.com/course/datastructuresalgorithms/"},
    {"skill": "NLP", "course": "Natural Language Processing Specialization", "platform": "Coursera", "link": "https://www.coursera.org/specializations/natural-language-processing"},
    {"skill": "Computer Vision", "course": "Deep Learning for Computer Vision with Python", "platform": "Udemy", "link": "https://www.udemy.com/course/deep-learning-computer-vision-python-opencv/"},
    {"skill": "Cloud Computing", "course": "Introduction to Cloud Computing", "platform": "Coursera", "link": "https://www.coursera.org/learn/introduction-to-cloud-computing"},
    {"skill": "DevOps", "course": "DevOps Fundamentals: CI/CD, Jenkins, Docker, Ansible, Kubernetes", "platform": "Udemy", "link": "https://www.udemy.com/course/devops-fundamentals/"},
    {"skill": "Agile", "course": "Agile with Atlassian Jira", "platform": "Coursera", "link": "https://www.coursera.org/learn/agile-atlassian-jira"},
    {"skill": "Cybersecurity", "course": "Google Cybersecurity Professional Certificate", "platform": "Coursera", "link": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
]


# --- Utility Functions ---

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file using pdfplumber.
    If pdfplumber fails (e.g., scanned PDF), it attempts OCR with pytesseract.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if not text.strip(): # If pdfplumber extracts no text, it might be a scanned PDF
            st.warning("No text extracted by pdfplumber. Attempting OCR (Optical Character Recognition). This may take a moment and accuracy can vary.")
            pdf_file.seek(0) # Reset file pointer for image processing
            images = convert_pdf_to_images(pdf_file)
            for img in images:
                text += pytesseract.image_to_string(img)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}. Attempting OCR as fallback.")
        pdf_file.seek(0) # Reset file pointer for image processing
        images = convert_pdf_to_images(pdf_file)
        for img in images:
            text += pytesseract.image_to_string(img)
    return text

def convert_pdf_to_images(pdf_file):
    """Converts PDF pages to PIL Image objects for OCR."""
    # This requires 'poppler' to be installed and in your system's PATH
    # On macOS: brew install poppler
    # On Windows: Download from poppler.freedesktop.org and add to PATH
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_file.read())
        return images
    except ImportError:
        st.error("pdf2image library not found. Please install it (`pip install pdf2image`) and ensure Poppler is installed and in your system's PATH for OCR functionality.")
        return []
    except Exception as e:
        st.error(f"Error converting PDF to images for OCR: {e}. Ensure Poppler is installed and in your system's PATH.")
        return []

# Name extraction helper (copied from HR portal app)
NAME_EXCLUDE_TERMS = {
    "linkedin", "github", "portfolio", "resume", "cv", "profile", "contact", "email", "phone",
    "mobile", "number", "tel", "telephone", "address", "website", "site", "social", "media",
    "url", "link", "blog", "personal", "summary", "about", "objective", "dob", "birth", "age",
    "nationality", "gender", "location", "city", "country", "pin", "zipcode", "state", "whatsapp",
    "skype", "telegram", "handle", "id", "details", "connection", "reach", "network", "www",
    "https", "http", "contactinfo", "connect", "reference", "references","fees","Bangalore, Karnataka",
    "resume", "cv", "curriculum vitae", "resume of", "cv of", "summary", "about",
    "objective", "declaration", "personal profile", "profile", "career objective",
    "introduction", "bio", "statement", "overview",

    # Education & academic
    "education", "qualifications", "academic", "certification", "certifications", "degree",
    "school", "college", "university", "diploma", "graduate", "graduation", "passed", "gpa",
    "cgpa", "marks", "percentage", "year", "pass", "exam", "results", "board",

    # Skills and tools
    "skills", "technical", "technologies", "tools", "software", "programming",
    "languages", "frameworks", "libraries", "databases", "methodologies", "platforms",
    "proficient", "knowledge", "experience", "exposure", "tools used", "framework",

    # Software/product/tool names (block spaCy NER mistakes)
    "zoom", "slack", "google", "microsoft", "excel", "word", "docs", "teams", "powerpoint",
    "notion", "jupyter", "linux", "windows", "android", "firebase", "oracle", "git", "github",
    "bitbucket", "jira", "confluence", "sheets", "trello", "figma", "canva", "sql", "mysql",
    "postgres", "mongodb", "hadoop", "spark", "kubernetes", "docker", "aws", "azure", "gcp",

    # Job/work section
    "experience", "internship", "work", "professional", "employment", "company",
    "role", "designation", "job", "project", "responsibilities", "position",
    "organization", "industry", "client", "team", "department",

    # Hobbies/extra
    "interests", "hobbies", "achievements", "awards", "activities", "extra curricular",
    "certified", "certificates", "participation", "strengths", "weaknesses", "languages known",

    # Location examples
    "bangalore", "delhi", "mumbai", "chennai", "hyderabad", "pune", "kolkata", "india",
    "remote", "new york", "california", "london", "tokyo", "berlin", "canada", "germany",

    # Misc
    "fees", "salary", "expected", "compensation", "passport", "visa", "availability",
    "notice period", "relocate", "relocation", "travel", "timing", "schedule", "full-time", "part-time",

    # Filler/common false-positive content
    "available", "required", "requested", "relevant", "coursework", "summary", "hello",
    "introduction", "dear", "regards", "thanks", "thank you", "please", "objective", "kindly"
}

def extract_name(text):
    lines = text.strip().splitlines()
    if not lines:
        return None

    PREFIX_CLEANER = re.compile(r"^(name[\s:\-]*|mr\.?|ms\.?|mrs\.?)", re.IGNORECASE)

    potential_names = []

    for line in lines[:10]:
        original_line = line.strip()
        if not original_line:
            continue

        cleaned_line = PREFIX_CLEANER.sub('', original_line).strip()
        cleaned_line = re.sub(r'[^A-Za-z\s]', '', cleaned_line)

        if any(term in cleaned_line.lower() for term in NAME_EXCLUDE_TERMS):
            continue

        words = cleaned_line.split()

        if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
            if all(w.istitle() or w.isupper() for w in words):
                potential_names.append(cleaned_line)

    if potential_names:
        return max(potential_names, key=len).title()

    return None

# Job domain classifier (copied from HR portal app)
def detect_job_domain(jd_title, jd_text):
    text = (jd_title + " " + jd_text).lower()
    if any(k in text for k in ["accountant", "finance", "ca", "cpa", "audit", "tax", "financial"]):
        return "finance"
    elif any(k in text for k in ["data scientist", "analytics", "ml", "ai", "machine learning", "deep learning", "nlp", "computer vision"]):
        return "data_science"
    elif any(k in text for k in ["developer", "engineer", "react", "python", "java", "software", "web", "frontend", "backend", "fullstack"]):
        return "software"
    elif any(k in text for k in ["recruiter", "talent acquisition", "hr", "human resources", "people operations", "onboarding"]):
        return "hr"
    elif any(k in text for k in ["designer", "photoshop", "figma", "ux", "ui", "illustrator", "graphic"]):
        return "design"
    else:
        return "general"


def extract_info(text):
    """
    Extracts various pieces of information from the resume text.
    """
    info = {
        "Name": "N/A", # Added Name field
        "Years of Experience": 0,
        "Email": "N/A",
        "Phone Number": "N/A",
        "Location": "N/A",
        "Languages": [],
        "Education": [],
        "Work History": [],
        "Project Details": [],
        "Certifications": [],
        "CGPA": "N/A"
    }

    # Extract Name
    name = extract_name(text)
    if name:
        info["Name"] = name

    # Years of Experience (simple regex, can be improved)
    exp_match = re.search(r'(\d+)\s*years?\s*of\s*experience', text, re.IGNORECASE)
    if exp_match:
        info["Years of Experience"] = int(exp_match.group(1))
    else:
        # Try to infer from dates in work history (more complex)
        work_history_text = re.search(r'(work experience|professional experience|employment history)(.*?)(education|skills|projects|$)', text, re.IGNORECASE | re.DOTALL)
        if work_history_text:
            dates = re.findall(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})[.\s-]?(\d{4})\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})?[.\s-]?(\d{4}|present|current)', work_history_text.group(2), re.IGNORECASE)
            if dates:
                total_months = 0
                for start_month_str, start_year_str, end_month_str, end_year_str in dates:
                    try:
                        start_year = int(start_year_str)
                        # Handle month conversion
                        start_month = datetime.strptime(start_month_str[:3], '%b').month if not start_month_str.isdigit() else int(start_month_str)

                        if end_year_str.lower() in ['present', 'current']:
                            end_year = datetime.now().year
                            end_month = datetime.now().month
                        else:
                            end_year = int(end_year_str)
                            end_month = datetime.strptime(end_month_str[:3], '%b').month if end_month_str and not end_month_str.isdigit() else (int(end_month_str) if end_month_str else start_month) # Default to start_month if end_month is missing

                        months_diff = (end_year - start_year) * 12 + (end_month - start_month)
                        if months_diff > 0:
                            total_months += months_diff
                    except ValueError:
                        continue
                info["Years of Experience"] = round(total_months / 12, 1)


    # Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        info["Email"] = email_match.group(0)

    # Phone Number (supports various formats)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        info["Phone Number"] = phone_match.group(0)

    # Location (simple keywords, can be expanded with a gazetteer)
    location_keywords = ["london", "new york", "san francisco", "seattle", "dublin", "berlin", "paris", "tokyo", "sydney", "toronto", "mumbai", "bangalore", "delhi", "chennai", "hyderabad", "pune", "kolkata", "ahmedabad", "gurgaon", "noida", "singapore", "dubai", "amsterdam", "zurich", "stockholm", "oslo", "helsinki", "copenhagen", "warsaw", "prague", "budapest", "vienna", "rome", "madrid", "barcelona", "lisbon", "brussels", "auckland", "wellington", "melbourne", "brisbane", "perth", "adelaide", "gold coast", "canberra", "hobart", "darwin", "cairns", "townsville", "geelong", "ballarat", "bendigo", "launceston", "rockhampton", "mackay", "bundaberg", "gladstone", "hervey bay", "maryborough", "toowoomba", "warwick", "dalby", "chinchilla", "roma", "emerald", "biloela", "montreal", "vancouver", "calgary", "edmonton", "ottawa", "winnipeg", "quebec city", "halifax", "victoria", "saskatoon", "regina", "st. john's", "fredericton", "charlottetown", "whitehorse", "yellowknife", "iqaluit", "mexico city", "rio de janeiro", "sao paulo", "buenos aires", "santiago", "bogota", "lima", "quito", "caracas", "montevideo", "asuncion", "la paz", "santa cruz", "guayaquil", "medellin", "cali", "barranquilla", "cartagena", "cucuta", "bucaramanga", "pereira", "manizales", "armenia", "ibague", "pasto", "neiva", "villavicencio", "tunja", "florencia", "yopal", "sincelejo", "monteria", "valledupar", "riohacha", "santa marta", "popayan", "palmira", "tulua", "envigado", "itagui", "sabaneta", "caldas", "la estrella", "rionegro", "apartado", "turbo", "caucasia", "montelibano", "san andres", "providencia", "leticia", "puerto carreño", "puerto inirida", "mitu", "san jose del guaviare", "arauca", "yopal", "quibdo", "mocoa", "puerto asis", "san vicente del caguan", "san agustin", "tierradentro", "villa de leyva", "barichara", "guatavita", "zipaquira", "salt mine", "cancun", "guadalajara", "monterrey", "puebla", "tijuana", "leon", "ciudad juarez", "san luis potosi", "aguascalientes", "merida", "queretaro", "hermosillo", "saltillo", "mexicali", "culiacan", "chihuahua", "torreon", "acapulco", "oaxaca", "veracruz", "toluca", "cuernavaca", "pachuca", "xalapa", "chetumal", "durango", "zacatecas", "ciudad victoria", "tampico", "matamoros", "nuevo laredo", "piedras negras", "reynosa", "san miguel de allende", "guanajuato", "patzcuaro", "uruapan", "morelia", "colima", "manzanillo", "tepic", "mazatlan", "los cabos", "la paz", "ensenada", "rosarito", "tecate", "san quintin", "guerrero negro", "santa rosalia", "loreto", "ciudad constitución", "cabo san lucas", "san jose del cabo", "todos santos", "el rosario", "cataviña", "san ignacio", "san javier", "san francisco javier", "san borja", "san fernando", "san vicente", "san felipe", "san quintin", "san pedro martir", "san pedro", "san pablo", "san miguel", "san marcos", "san juan", "san ignacio", "san gregorio", "san gabriel", "san esteban", "san diego", "san cristobal", "san carlos", "san benito", "san bartolo", "san antonio", "san andres", "san alberto", "san agustin", "san adrian", "san abel", "san aaron", "san abdon", "san abelardo", "san abilio", "san abra", "san abraham", "san abram", "san absalon", "san acacio", "san acisclo", "san adela", "san adelaida", "san adolfo", "san adonai", "san adriano", "san agapito", "san agata", "san agueda", "san agustin", "san alberto", "san albin", "san alcides", "san aldo", "san alejo", "san alejandro", "san alfonso", "san alfredo", "san alipio", "san alvaro", "san amadeo", "san amador", "san ambrosio", "san amelia", "san anastasio", "san anastasia", "san ancelmo", "san andres", "san angela", "san angel", "san anibal", "san aniceto", "san anna", "san anselmo", "san antolin", "san anton", "san antonia", "san antonio", "san apolinar", "san apolonia", "san aquilino", "san arcadio", "san arecio", "san areta", "san argeo", "san ariana", "san arias", "san aristides", "san arnaldo", "san arturo", "san asuncion", "san atanasio", "san atilio", "san augusto", "san aurelia", "san aureliano", "san aurelio", "san aurora", "san baldomero", "san balduino", "san baltasar", "san barbara", "san bartolome", "san basilio", "san beatriz", "san benedicto", "san benito", "san bernabe", "san bernarda", "san bernardino", "san bernardo", "san blas", "san bonifacio", "san borja", "san bruno", "san buenaventura", "san candida", "san candido", "san carla", "san carlo", "san carlos", "san carmen", "san casimiro", "san catalina", "san cayetano", "san cecilia", "san celestino", "san celia", "san cesar", "san charo", "san chus", "san clara", "san claudio", "san clemente", "san concepcion", "san conrado", "san constanza", "san cornelio", "san cosme", "san crisanto", "san crispin", "san cristina", "san cristobal", "san cruz", "san daciano", "san damian", "san daniel", "san david", "san demetrio", "san diego", "san dionisio", "san dolores", "san domingo", "san donato", "san dorotea", "san edgar", "san edmundo", "san eduardo", "san elena", "san eleuterio", "san elias", "san elisa", "san eloy", "san emeterio", "san emilio", "san enrique", "san eusebio", "san eustaquio", "san eva", "san ezequiel", "san fabian", "san faustino", "san fausto", "san federico", "san felicia", "san feliciano", "san felipe", "san felix", "san fermin", "san fernanda", "san fernando", "san fidel", "san filomena", "san fina", "san florencia", "san florencio", "san florian", "san francisco", "san fulgencio", "san gabriel", "san gema", "san genaro", "san genoveva", "san gerardo", "san germán", "san gervasio", "san gines", "san gloria", "san gonzalo", "san gregorio", "san guadalupe", "san gumer", "san helena", "san heriberto", "san hermenegildo", "san hilario", "san hipolito", "san honorio", "san horacio", "san humberto", "san ignacia", "san ignacio", "san ildefonso", "san ines", "san inocencio", "san irene", "san isabel", "san isidro", "san ismael", "san jacinto", "san jacobo", "san jaime", "san javier", "san jeremias", "san jeronimo", "san jesus", "san joaquin", "san joaquina", "san jon", "san jorge", "san jose", "san josefa", "san josefina", "san josue", "san juan", "san julian", "san juliana", "san julio", "san justa", "san justo", "san laura", "san lazaro", "san leandro", "san leon", "san leonor", "san leopoldo", "san lino", "san lorenzo", "san lourdes", "san lucas", "san lucia", "san luciano", "san luisa", "san luis", "san luz", "san macario", "san magdalena", "san manuel", "san manuela", "san marcelino", "san marcelo", "san marcos", "san margarita", "san maria", "san mariano", "san marina", "san mario", "san marta", "san martin", "san mateo", "san matilde", "san mauricio", "san maximiliano", "san maximino", "san mercedes", "san miguel", "san milagros", "san monica", "san narciso", "san natalia", "san nazario", "san nicanor", "san nicolas", "san nieves", "san noelia", "san norberto", "san obdulia", "san octavio", "san odon", "san olga", "san omar", "san onofre", "san orencio", "san oscar", "san osvaldo", "san pablo", "san paloma", "san pascual", "san patricia", "san patricio", "san paula", "san pedro", "san pilar", "san pio", "san policarpo", "san ponciano", "san prudencio", "san purificacion", "san rafael", "san ramon", "san ramona", "san raquel", "san rebeca", "san remigio", "san renata", "san renato", "san reyes", "san ricardo", "san rita", "san roberto", "san rocio", "san roque", "san rosa", "san rosario", "san ruben", "san rufino", "san ruperto", "san sabina", "san salvador", "san samuel", "san sandra", "san santiago", "san sara", "san sebastian", "san serafin", "san sergio", "san severino", "san silvestre", "san simon", "san sixto", "san sofia", "san sonia", "san susana", "san teresa", "san teodoro", "san teresa", "san tomas", "san toribio", "san trinidad", "san urbano", "san ursula", "san valentin", "san valeriano", "san vanesa", "san venancio", "san veronica", "san vicenta", "san vicente", "san victor", "san victoria", "san victoriano", "san victorino", "san vida", "san vilma", "san vicente", "san yolanda", "san zacarias", "san zoe", "san zulema"]
    for loc in location_keywords:
        if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
            info["Location"] = loc.title()
            break

    # Languages (common languages)
    language_keywords = ["english", "spanish", "french", "german", "chinese", "mandarin", "japanese", "korean", "hindi", "arabic", "portuguese", "russian", "italian", "dutch", "swedish", "norwegian", "danish", "finnish", "greek", "turkish", "polish", "czech", "slovak", "hungarian", "romanian", "bulgarian", "serbian", "croatian", "bosnian", "slovenian", "albanian", "macedonian", "ukrainian", "lithuanian", "latvian", "estonian", "bengali", "tamil", "telugu", "kannada", "malayalam", "gujarati", "punjabi", "marathi", "nepali", "sinhala", "thai", "vietnamese", "indonesian", "malay", "filipino", "urdu", "persian", "hebrew", "swahili", "amharic", "yoruba", "igbo", "zulu", "xhosa", "afrikaans"]
    found_languages = []
    for lang in language_keywords:
        if re.search(r'\b' + re.escape(lang) + r'\b', text, re.IGNORECASE):
            found_languages.append(lang.title())
    info["Languages"] = list(set(found_languages)) # Remove duplicates

    # Education (simple extraction, looks for degree and university names)
    education_matches = re.findall(r'(Bachelor\'s|Master\'s|Ph\.D\.|B\.S\.|M.S\.|B.Tech|M.Tech|BCA|MCA|MBA|BBA|B.E\.|M.E\.)\s+in\s+([\w\s.&,-]+?)\s+from\s+([\w\s.,-]+?)(?:\s+-\s+(\d{4}))?', text, re.IGNORECASE)
    for match in education_matches:
        degree, field, university, year = match
        info["Education"].append({"degree": degree.strip(), "field": field.strip(), "university": university.strip(), "year": year if year else "N/A"})

    # Work History (looks for job titles and companies, dates)
    work_history_matches = re.findall(r'(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})[.\s-]?\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})?[.\s-]?(\d{4}|present|current))\s*\n\s*(.*?)\s+at\s+([^\n]+)', text, re.IGNORECASE | re.DOTALL)
    for match in work_history_matches:
        dates_str, title, company = match
        info["Work History"].append({"title": title.strip(), "company": company.strip(), "dates": dates_str.strip()})

    # Project Details (simple extraction, looks for "Project" keyword)
    project_matches = re.findall(r'(?:Project|Projects)[:\s-]?\s*([^\n]+(?:\n[^\n]+)*?)(?=(?:Education|Skills|Work History|Certifications|$))', text, re.IGNORECASE | re.DOTALL)
    for match in project_matches:
        # Split by common project delimiters like "Project Name:" or bullet points
        sub_projects = re.split(r'\n\s*(?:-|\*|\d+\.)\s*', match.strip())
        info["Project Details"].extend([p.strip() for p in sub_projects if p.strip()])


    # Certifications
    certification_keywords = ["certified", "certification", "certificate", "aws certified", "azure certified", "google cloud certified", "pmp", "csm", "cisa", "cism", "cissp", "scrum master", "itil", "comptia", "ccna", "ccnp", "red hat certified"]
    found_certifications = []
    for cert_keyword in certification_keywords:
        cert_matches = re.findall(r'\b' + re.escape(cert_keyword) + r'[\w\s-]*?(?:\d{3,4})?\b', text, re.IGNORECASE)
        found_certifications.extend(cert_matches)
    info["Certifications"] = list(set([cert.strip() for cert in found_certifications]))

    # CGPA extraction and normalization
    cgpa_match = re.search(r'(?:CGPA|GPA|Score):\s*(\d(?:\.\d{1,2})?)\s*(?:/\s*(\d(?:\.\d{1,2})?))?', text, re.IGNORECASE)
    if cgpa_match:
        cgpa_value = float(cgpa_match.group(1))
        max_scale = float(cgpa_match.group(2)) if cgpa_match.group(2) else 4.0 # Default to 4.0 if max scale not provided
        normalized_cgpa = (cgpa_value / max_scale) * 4.0
        info["CGPA"] = round(normalized_cgpa, 2)
    else:
        # Try to find percentages and convert to 4.0 scale (approximate)
        percentage_match = re.search(r'(\d{1,3}(?:\.\d{1,2})?)\s*%', text)
        if percentage_match:
            percentage = float(percentage_match.group(1))
            # Rough conversion: 60% -> 2.0, 80% -> 3.0, 100% -> 4.0
            # Linear interpolation: CGPA = (Percentage / 100) * 4.0
            normalized_cgpa = (percentage / 100.0) * 4.0
            info["CGPA"] = round(normalized_cgpa, 2)

    return info

def extract_skills(text, master_skills):
    """
    Extracts skills from text based on a master list of skills.
    Returns a list of found skills.
    """
    found_skills = []
    text_lower = text.lower()
    for skill in master_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
    return list(set(found_skills))

def get_jd_files():
    """Returns a list of predefined JD files in the 'data' directory."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.pdf'))]

def generate_keyword_cloud(text):
    """Generates a simple keyword cloud from text."""
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(
        "a an the is are was were be been being has have had do does did will would shall should can could may might must ought to in on at by for with against between into through during before after above below to from up down in out over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now d ll m o re ve y ain aren couldn didn doesn hadn hasn haven isn mightn mustn needn shan shouldn wasn weren won wouldn".split()
    )
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(20) # Get top 20 words

    if common_words:
        st.subheader("JD Keyword Cloud (Top 20)")
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        for i, (word, count) in enumerate(common_words):
            with cols[i % 5]:
                st.markdown(f"<span style='background-color:#e0f7fa; padding: 5px 10px; border-radius: 5px; margin: 3px; display: inline-block; font-size: {14 + count/2}px;'>{word}</span>", unsafe_allow_html=True)
    else:
        st.info("No significant keywords found to generate a cloud.")

# Removed get_llm_response as it's no longer used for HR summary

def normalize_score(score, min_val, max_val, new_min=0, new_max=100):
    """Normalizes a score from an old range to a new range."""
    if max_val == min_val:
        return new_min if score <= min_val else new_max
    return new_min + (score - min_val) * (new_max - new_min) / (max_val - min_val)

def calculate_exact_match_score(jd_skills, resume_skills):
    """Calculates an exact keyword match score."""
    matched_keywords = set(jd_skills).intersection(set(resume_skills))
    if not jd_skills:
        return 0
    score = (len(matched_keywords) / len(jd_skills)) * 100
    return score

def calculate_semantic_similarity(jd_text, resume_text):
    """Calculates semantic similarity between JD and resume using SentenceTransformer."""
    if not jd_text or not resume_text:
        return 0.0
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.cos_sim(jd_embedding, resume_embedding).item()
    return similarity * 100 # Convert to percentage

def calculate_scores(jd_text, resume_text, resume_info, jd_skills, resume_skills): # Removed high_priority_skills, medium_priority_skills
    """
    Calculates various scores for resume screening,
    using logic aligned with the HR portal for main scoring.
    """
    scores = {}

    # 1. Exact Match Score (from HR Portal logic)
    scores["Exact Match Score"] = calculate_exact_match_score(jd_skills, resume_skills)

    # 2. Semantic Similarity Score (from HR Portal logic)
    scores["Semantic Similarity Score"] = calculate_semantic_similarity(jd_text, resume_text)

    # 3. Final Match Score (60% Semantic, 40% Exact - from HR Portal logic)
    # Ensure scores are normalized to 0-100 before weighted average
    semantic_normalized = scores["Semantic Similarity Score"]
    exact_normalized = scores["Exact Match Score"]

    scores["Final Match Score"] = (0.60 * semantic_normalized) + (0.40 * exact_normalized)
    scores["Final Match Score"] = round(scores["Final Match Score"], 2)

    # 4. Experience Score (simple, can be enhanced)
    # Give higher score if experience is closer to JD's implied experience
    # For now, a simple binary: if experience > 0, give some points.
    # A more advanced logic would be to compare to a target range from JD.
    scores["Experience Score"] = 0
    if resume_info["Years of Experience"] > 0:
        scores["Experience Score"] = min(100, resume_info["Years of Experience"] * 10) # Max 100 for 10+ years

    # 5. CGPA Score (if available, normalized to 4.0 scale)
    scores["CGPA Score"] = 0
    if isinstance(resume_info["CGPA"], (int, float)) and resume_info["CGPA"] != "N/A":
        scores["CGPA Score"] = (resume_info["CGPA"] / 4.0) * 100 # Scale to 100

    # 6. Company Fit Score (unique to Candidate Portal, based on selected company profile)
    scores["Company Fit Score"] = 0
    if st.session_state.get('selected_company_profile') and st.session_state.selected_company_profile != "None":
        company_skills = COMPANY_SKILL_PROFILES.get(st.session_state.selected_company_profile, [])
        if company_skills:
            # Semantic similarity with company profile
            company_profile_text = " ".join(company_skills)
            company_embedding = model.encode(company_profile_text, convert_to_tensor=True)
            resume_embedding = model.encode(resume_text, convert_to_tensor=True)
            company_semantic_similarity = util.cos_sim(company_embedding, resume_embedding).item() * 100

            # Exact match with company profile
            company_exact_match = calculate_exact_match_score(company_skills, resume_skills)

            # Combine for company fit (e.g., 70% semantic, 30% exact for company fit)
            scores["Company Fit Score"] = (0.70 * company_semantic_similarity) + (0.30 * company_exact_match)
            scores["Company Fit Score"] = round(scores["Company Fit Score"], 2)


    # Determine AI Tag based on Final Match Score (HR Portal logic)
    if scores["Final Match Score"] >= 80:
        scores["AI Tag"] = "Exceptional Match"
    elif scores["Final Match Score"] >= 60:
        scores["AI Tag"] = "Strong Candidate"
    elif scores["Final Match Score"] >= 40:
        scores["AI Tag"] = "Good Fit"
    elif scores["Final Match Score"] >= 20:
        scores["AI Tag"] = "Potential Match"
    else:
        scores["AI Tag"] = "Low Match"

    return scores

# New LLM-style HR summary generation function (copied from HR portal app)
def generate_hr_summary(name, score, experience, matched_skills, missing_skills, cgpa, job_domain, tone="Professional"):
    summary_parts = []

    # Map job_domain to a more descriptive role_tag
    role_tag_map = {
        "finance": "finance-focused",
        "data_science": "data science-oriented",
        "software": "software development-centric",
        "hr": "human resources-aligned",
        "design": "design-specialized",
        "general": "well-rounded"
    }
    role_tag = role_tag_map.get(job_domain, "general")

    cgpa_str = f"a CGPA of {cgpa:.2f} on a 4.0 scale" if pd.notna(cgpa) and cgpa != "N/A" else "no specific CGPA mentioned"

    # 1. Opening Statement
    if tone == "Professional":
        summary_parts.append(
            f"{name} presents as a {role_tag} candidate with approximately {experience} years of experience and {cgpa_str}."
        )
    elif tone == "Friendly":
        summary_parts.append(
            f"Meet {name}, a {role_tag} professional with about {experience} years under their belt, and they've achieved {cgpa_str}."
        )
    elif tone == "Critical":
        summary_parts.append(
            f"Analysis of {name}'s profile reveals {experience} years of experience and {cgpa_str}, with a {role_tag} focus."
        )

    # 2. Highlighted Strengths
    if matched_skills:
        focus_skills = ', '.join(matched_skills[:5])
        if tone == "Professional":
            strength_openers = [
                f"The candidate demonstrates strong alignment in key technical areas such as: {focus_skills}.",
                f"Core proficiencies identified include: {focus_skills}.",
                f"Notable strengths encompass: {focus_skills}."
            ]
        elif tone == "Friendly":
            strength_openers = [
                f"They're really strong in areas like: {focus_skills}.",
                f"Their top skills are definitely: {focus_skills}.",
                f"You'll find them excelling in: {focus_skills}."
            ]
        elif tone == "Critical":
            strength_openers = [
                f"Some relevant proficiencies include: {focus_skills}.",
                f"Skills present are: {focus_skills}.",
                f"Identified capabilities: {focus_skills}."
            ]
        summary_parts.append(random.choice(strength_openers))

    # 3. Score Interpretation
    if score >= 85:
        if tone == "Professional":
            summary_parts.append("This is an exceptional profile with clear alignment to the role requirements. The candidate is highly likely to thrive with minimal onboarding.")
        elif tone == "Friendly":
            summary_parts.append("Wow, this candidate is a fantastic match! They're super aligned with what we're looking for and should hit the ground running.")
        elif tone == "Critical":
            summary_parts.append("The profile shows strong alignment, indicating a high probability of successful integration into the role.")
    elif score >= 70:
        if tone == "Professional":
            summary_parts.append("This is a strong match with most key requirements met. The candidate is suitable for a technical interview.")
        elif tone == "Friendly":
            summary_parts.append("A solid match! They've got most of what we need and are definitely worth a chat.")
        elif tone == "Critical":
            summary_parts.append("The candidate meets a majority of the core competencies, warranting further evaluation.")
    elif score >= 50:
        if tone == "Professional":
            summary_parts.append("This profile shows potential but lacks alignment in some critical areas. Further assessment is recommended.")
        elif tone == "Friendly":
            summary_parts.append("They've got some good stuff, but there are a few gaps. Might need a closer look or some development.")
        elif tone == "Critical":
            summary_parts.append("Identified gaps in key areas suggest a need for more rigorous screening or consideration for alternative roles.")
    else:
        if tone == "Professional":
            summary_parts.append("This candidate may not currently align with the role’s expectations. Consider for future openings or roles with a different skill set.")
        elif tone == "Friendly":
            summary_parts.append("Not quite the right fit for this one, but keep them in mind for other opportunities!")
        elif tone == "Critical":
            summary_parts.append("The candidate's profile presents significant deviations from the required competencies, rendering them unsuitable for the current vacancy.")

    # 4. Areas to Improve
    if missing_skills:
        if tone == "Professional":
            summary_parts.append(
                f"To increase alignment with this role, the candidate could focus on gaining expertise in: {', '.join(missing_skills[:4])}."
            )
        elif tone == "Friendly":
            summary_parts.append(
                f"If they brush up on {', '.join(missing_skills[:4])}, they'd be even stronger!"
            )
        elif tone == "Critical":
            summary_parts.append(
                f"Deficiencies were noted in: {', '.join(missing_skills[:4])}."
            )

    # 5. Career Fit Tag (Additional Insight)
    if experience > 10:
        if tone == "Professional":
            summary_parts.append("Additional insight: Given their extensive experience, the candidate may be suitable for senior or lead roles beyond the scope of the current opening.")
        elif tone == "Friendly":
            summary_parts.append("Just a thought: With all that experience, they might be a great fit for a more senior or leadership position!")
        elif tone == "Critical":
            summary_parts.append("Observation: The candidate's experience level suggests potential overqualification for this specific role; consider higher-tier positions.")
    elif experience < 1 and score >= 60: # Only suggest entry-level if they still scored reasonably well
        if tone == "Professional":
            summary_parts.append("Additional insight: This appears to be an early-career candidate, ideal for internships or entry-level roles where foundational skills are valued.")
        elif tone == "Friendly":
            summary_parts.append("Heads up: This looks like a fresh face, perfect for an internship or a junior role!")
        elif tone == "Critical":
            summary_parts.append("Observation: The candidate's limited experience suggests suitability for entry-level positions only.")

    return " ".join(summary_parts)


def generate_certificate(candidate_name, final_score, ai_tag, email, phone, experience, cgpa, matched_skills):
    """Generates a ScreenerPro Certificate as HTML and PDF."""
    current_date = datetime.now().strftime("%B %d, %Y")
    certificate_id = f"SP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{np.random.randint(1000, 9999)}"
    
    # HTML Certificate Content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ScreenerPro Certificate</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
            .certificate-container {{ width: 100%; max-width: 800px; background-color: #ffffff; border: 10px solid #007bff; border-image: linear-gradient(45deg, #007bff, #00c6ff) 1; padding: 40px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); text-align: center; position: relative; overflow: hidden; border-radius: 15px; }}
            .certificate-container::before {{ content: ''; position: absolute; top: -50px; left: -50px; right: -50px; bottom: -50px; background: radial-gradient(circle at top left, rgba(0, 123, 255, 0.1), transparent 50%), radial-gradient(circle at bottom right, rgba(0, 198, 255, 0.1), transparent 50%); z-index: 0; }}
            .content {{ position: relative; z-index: 1; }}
            h1 {{ color: #007bff; font-size: 2.8em; margin-bottom: 10px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; font-size: 1.8em; margin-top: 5px; margin-bottom: 20px; }}
            p {{ font-size: 1.1em; color: #555; line-height: 1.6; margin-bottom: 10px; }}
            .name {{ font-size: 2.2em; color: #0056b3; margin: 25px 0; font-weight: bold; text-transform: uppercase; }}
            .score {{ font-size: 2.5em; color: #28a745; font-weight: bold; margin: 20px 0; }}
            .ai-tag {{ font-size: 1.5em; color: #6c757d; margin-bottom: 30px; font-style: italic; }}
            .details {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .detail-item {{ flex: 1 1 45%; min-width: 250px; background-color: #e9f7fe; padding: 15px; border-radius: 10px; text-align: left; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); }}
            .detail-item strong {{ color: #007bff; }}
            .footer {{ margin-top: 40px; font-size: 0.9em; color: #888; }}
            .logo {{ margin-bottom: 20px; }}
            .logo img {{ height: 60px; }}
            .signature {{ margin-top: 50px; display: flex; justify-content: space-around; align-items: flex-end; }}
            .signature div {{ text-align: center; border-top: 1px solid #ccc; padding-top: 10px; width: 45%; }}
            .signature p {{ margin: 0; font-size: 0.9em; color: #666; }}
            .certificate-id {{ font-size: 0.8em; color: #aaa; margin-top: 20px; }}
            .skills-list {{ text-align: left; margin-top: 15px; }}
            .skills-list span {{ display: inline-block; background-color: #d1ecf1; color: #0c5460; padding: 5px 10px; border-radius: 5px; margin: 4px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="certificate-container">
            <div class="content">
                <div class="logo">
                    <img src="https://placehold.co/200x60/007bff/ffffff?text=ScreenerPro" alt="ScreenerPro Logo">
                </div>
                <h1>CERTIFICATE OF ASSESSMENT</h1>
                <h2>This certifies that</h2>
                <p class="name">{candidate_name}</p>
                <p>has successfully undergone a comprehensive AI-powered resume screening and achieved an assessment score of</p>
                <p class="score">{final_score:.2f}%</p>
                <p class="ai-tag">AI Tag: {ai_tag}</p>
                <p>This assessment reflects the candidate's alignment with industry standards and job requirements based on their provided resume.</p>

                <div class="details">
                    <div class="detail-item">
                        <strong>Experience:</strong> {experience} Years
                    </div>
                    <div class="detail-item">
                        <strong>CGPA (Normalized):</strong> {cgpa} / 4.0
                    </div>
                    <div class="detail-item">
                        <strong>Email:</strong> {email}
                    </div>
                    <div class="detail-item">
                        <strong>Phone:</strong> {phone}
                    </div>
                    <div class="detail-item">
                        <strong>Matched Skills:</strong>
                        <div class="skills-list">
                            {''.join([f"<span>{skill}</span>" for skill in matched_skills]) if matched_skills else '<span>No key skills matched</span>'}
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>Issued on: {current_date}</p>
                    <p class="certificate-id">Certificate ID: {certificate_id}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # PDF Certificate Content (using ReportLab)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(name='Title', alignment=TA_CENTER, fontSize=28,
                              textColor=HexColor('#007bff'), spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Subtitle', alignment=TA_CENTER, fontSize=18,
                              textColor=HexColor('#333333'), spaceAfter=20))
    styles.add(ParagraphStyle(name='Name', alignment=TA_CENTER, fontSize=26,
                              textColor=HexColor('#0056b3'), spaceAfter=25, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalCenter', alignment=TA_CENTER, fontSize=11,
                              textColor=HexColor('#555555'), spaceAfter=10))
    styles.add(ParagraphStyle(name='Score', alignment=TA_CENTER, fontSize=30,
                              textColor=HexColor('#28a745'), spaceAfter=20, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='AITag', alignment=TA_CENTER, fontSize=14,
                              textColor=HexColor('#6c757d'), spaceAfter=30, fontName='Helvetica-Oblique'))
    styles.add(ParagraphStyle(name='DetailHeader', fontSize=12, textColor=HexColor('#007bff'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5))
    styles.add(ParagraphStyle(name='DetailText', fontSize=11, textColor=HexColor('#555555'), spaceAfter=5))
    styles.add(ParagraphStyle(name='Footer', alignment=TA_CENTER, fontSize=9, textColor=HexColor('#888888'), spaceBefore=40))
    styles.add(ParagraphStyle(name='CertID', alignment=TA_CENTER, fontSize=8, textColor=HexColor('#aaaaaa'), spaceAfter=10))
    styles.add(ParagraphStyle(name='SkillTag', fontSize=9, textColor=HexColor('#0c5460'), backColor=HexColor('#d1ecf1'), borderRadius=5,
                              leftIndent=5, rightIndent=5, spaceBefore=2, spaceAfter=2, leading=12,
                              alignment=TA_CENTER))


    elements = []

    # Logo (placeholder)
    elements.append(RLImage("https://placehold.co/200x60/007bff/ffffff?text=ScreenerPro", width=2*inch, height=0.6*inch))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("CERTIFICATE OF ASSESSMENT", styles['Title']))
    elements.append(Paragraph("This certifies that", styles['Subtitle']))
    elements.append(Paragraph(candidate_name.upper(), styles['Name']))
    elements.append(Paragraph("has successfully undergone a comprehensive AI-powered resume screening and achieved an assessment score of", styles['NormalCenter']))
    elements.append(Paragraph(f"{final_score:.2f}%", styles['Score']))
    elements.append(Paragraph(f"AI Tag: {ai_tag}", styles['AITag']))
    elements.append(Paragraph("This assessment reflects the candidate's alignment with industry standards and job requirements based on their provided resume.", styles['NormalCenter']))
    elements.append(Spacer(1, 0.3*inch))

    # Details Section
    elements.append(Paragraph("<b><u>Candidate Details</u></b>", styles['DetailHeader']))
    elements.append(Paragraph(f"<b>Experience:</b> {experience} Years", styles['DetailText']))
    elements.append(Paragraph(f"<b>CGPA (Normalized):</b> {cgpa} / 4.0", styles['DetailText']))
    elements.append(Paragraph(f"<b>Email:</b> {email}", styles['DetailText']))
    elements.append(Paragraph(f"<b>Phone:</b> {phone}", styles['DetailText']))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("<b><u>Matched Skills</u></b>", styles['DetailHeader']))
    if matched_skills:
        skill_text = ""
        for skill in matched_skills:
            skill_text += f'<font color="#0c5460"><u>{skill}</u></font>  ' # Underline for emphasis in PDF
        elements.append(Paragraph(skill_text, styles['DetailText']))
    else:
        elements.append(Paragraph("No key skills matched", styles['DetailText']))

    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph(f"Issued on: {current_date}", styles['Footer']))
    elements.append(Paragraph(f"Certificate ID: {certificate_id}", styles['CertID']))

    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()

    return html_content, pdf_content, certificate_id

def send_email(receiver_email, subject, body, html_body, attachment_name, attachment_content):
    """Sends an email with an HTML body and a PDF attachment."""
    sender_email = st.secrets["EMAIL_SENDER"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach plain text and HTML versions
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Attach PDF
    pdf_part = MIMEText(attachment_content, "base64")
    pdf_part.add_header("Content-Disposition", f"attachment; filename={attachment_name}")
    pdf_part.add_header("Content-Type", "application/pdf")
    msg.attach(pdf_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def save_certificate_data_to_firestore(certificate_data):
    """
    Saves certificate data to Firestore using a REST API call.
    Uses the public collection path: /artifacts/{appId}/public/data/certificates/{documentId}
    """
    firestore_api_url = f"https://firestore.googleapis.com/v1/projects/{firebase_config['projectId']}/databases/(default)/documents/artifacts/{app_id}/public/data/certificates"
    
    # Construct Firestore document structure
    document_data = {
        "fields": {
            "certificateId": {"stringValue": certificate_data.get("certificate_id", "")},
            "candidateName": {"stringValue": certificate_data.get("candidate_name", "")},
            "finalScore": {"doubleValue": certificate_data.get("final_score", 0.0)},
            "aiTag": {"stringValue": certificate_data.get("ai_tag", "")},
            "email": {"stringValue": certificate_data.get("email", "")},
            "experience": {"doubleValue": certificate_data.get("experience", 0.0)},
            "cgpa": {"doubleValue": certificate_data.get("cgpa", 0.0)},
            "matchedSkills": {"arrayValue": {"values": [{"stringValue": s} for s in certificate_data.get("matched_skills", [])]}},
            "timestamp": {"timestampValue": datetime.now().isoformat() + "Z"}
        }
    }

    try:
        response = requests.post(firestore_api_url, json=document_data)
        response.raise_for_status()
        st.success("Certificate data saved to Firestore for verification!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to save certificate data to Firestore: {e}")
        return False


# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="ScreenerPro - Candidate Portal", page_icon="📄")

st.title("🚀 ScreenerPro - Candidate Portal")
st.markdown("### Get an AI-Powered Assessment of Your Resume Against a Job Description")

# Initialize session state for company profile
if 'selected_company_profile' not in st.session_state:
    st.session_state.selected_company_profile = "None"

# Sidebar for JD Upload/Selection
st.sidebar.header("Job Description (JD)")
jd_option = st.sidebar.radio("Choose JD Source:", ("Upload New JD", "Select Pre-loaded JD"))

jd_text = ""
jd_name_for_results = "" # Added to pass to detect_job_domain
if jd_option == "Upload New JD":
    uploaded_jd_file = st.sidebar.file_uploader("Upload Job Description (TXT or PDF)", type=["txt", "pdf"])
    if uploaded_jd_file:
        if uploaded_jd_file.type == "text/plain":
            jd_text = uploaded_jd_file.read().decode("utf-8")
        elif uploaded_jd_file.type == "application/pdf":
            jd_text = extract_text_from_pdf(uploaded_jd_file)
        jd_name_for_results = uploaded_jd_file.name
        st.sidebar.success("JD uploaded successfully!")
elif jd_option == "Select Pre-loaded JD":
    jd_files = get_jd_files()
    if jd_files:
        selected_jd_file = st.sidebar.selectbox("Select a JD:", ["-- Select --"] + jd_files)
        if selected_jd_file != "-- Select --":
            file_path = os.path.join("data", selected_jd_file)
            if selected_jd_file.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    jd_text = f.read()
            elif selected_jd_file.endswith(".pdf"):
                with open(file_path, 'rb') as f:
                    jd_text = extract_text_from_pdf(io.BytesIO(f.read()))
            jd_name_for_results = selected_jd_file
            st.sidebar.success(f"JD '{selected_jd_file}' loaded.")
    else:
        st.sidebar.warning("No pre-loaded JDs found in the 'data' directory.")

st.sidebar.markdown("---")
st.sidebar.header("Your Resume")
uploaded_resume_file = st.sidebar.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

st.sidebar.markdown("---")
st.sidebar.header("Company Fit Assessment")
st.sidebar.selectbox(
    "Select a Target Company Profile:",
    ["None"] + sorted(list(COMPANY_SKILL_PROFILES.keys())),
    key='selected_company_profile',
    help="Assess how well your resume aligns with the typical skill sets of a specific company."
)

# Removed Skill Prioritization section
# st.sidebar.markdown("---")
# st.sidebar.header("Skill Prioritization")
# st.sidebar.info("Select skills you consider highly or medium priority for your assessment. This will influence the keyword matching.")

# col_high, col_medium = st.sidebar.columns(2)
# with col_high:
#     high_priority_skills = st.multiselect(
#         "High Priority Skills (3x weight):",
#         options=MASTER_SKILLS,
#         help="Skills that are crucial for the role and should have higher impact on your score."
#     )
# with col_medium:
#     medium_priority_skills = st.multiselect(
#         "Medium Priority Skills (2x weight):",
#         options=MASTER_SKILLS,
#         help="Important skills that should have a moderate impact on your score."
#     )

st.sidebar.markdown("---")
st.sidebar.header("AI Summary Tone")
summary_tone = st.sidebar.radio(
    "Choose the tone for your AI HR Assessment:",
    ("Professional", "Friendly", "Critical"),
    help="Select how you want the AI to present the HR assessment of your resume."
)


# Main content area
if jd_text and uploaded_resume_file:
    st.subheader("📄 Job Description Content")
    st.expander("View JD").markdown(jd_text)
    generate_keyword_cloud(jd_text)

    st.subheader("⚙️ Processing Your Resume...")
    with st.spinner("Extracting information and analyzing skills..."):
        resume_text = extract_text_from_pdf(uploaded_resume_file)
        if not resume_text.strip():
            st.error("Could not extract text from your resume. Please ensure it's a selectable PDF (not a scanned image) or try OCR if configured.")
            st.stop()

        resume_info = extract_info(resume_text)
        jd_skills = extract_skills(jd_text, MASTER_SKILLS)
        resume_skills = extract_skills(resume_text, MASTER_SKILLS)

        # Updated call to calculate_scores (removed priority skills)
        scores = calculate_scores(jd_text, resume_text, resume_info, jd_skills, resume_skills)

        matched_skills = list(set(jd_skills).intersection(set(resume_skills)))
        missing_skills = list(set(jd_skills) - set(resume_skills))
        
        # Sort skills for consistent display
        matched_skills.sort()
        missing_skills.sort()

    st.subheader("✅ Analysis Complete!")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Your Score")
        st.metric("Final Match Score", f"{scores['Final Match Score']:.2f}%")
        st.write(f"**AI Tag:** {scores['AI Tag']}")

        st.subheader("Summary of Extracted Info")
        # Display Name explicitly
        st.write(f"**Name:** {resume_info.get('Name', 'N/A')}")
        st.json({k: v for k, v in resume_info.items() if k not in ["Name", "Education", "Work History", "Project Details", "Certifications"]})

        st.subheader("Detailed Scores")
        st.info(f"**Exact Match Score:** {scores['Exact Match Score']:.2f}% (Keyword overlap)")
        st.info(f"**Semantic Similarity Score:** {scores['Semantic Similarity Score']:.2f}% (Meaningful relevance)")
        if st.session_state.selected_company_profile != "None":
            st.info(f"**Company Fit Score ({st.session_state.selected_company_profile}):** {scores['Company Fit Score']:.2f}%")
        st.info(f"**Experience Score:** {scores['Experience Score']:.2f}%")
        st.info(f"**CGPA Score:** {scores['CGPA Score']:.2f}%")


    with col2:
        st.subheader("🎯 Skill Alignment")
        st.markdown("**Matched Skills:**")
        if matched_skills:
            # Corrected f-string syntax here
            st.markdown(f"<div style='display: flex; flex-wrap: wrap; gap: 8px;'>{''.join([f\"<span style='background-color:#d4edda; color:#155724; padding: 5px 10px; border-radius: 5px;'>{s}</span>\" for s in matched_skills])}</div>", unsafe_allow_html=True)
        else:
            st.info("No direct skill matches found with the JD.")

        st.markdown("---")
        st.markdown("**Missing Skills (from JD):**")
        if missing_skills:
            # Corrected f-string syntax here
            st.markdown(f"<div style='display: flex; flex-wrap: wrap; gap: 8px;'>{''.join([f\"<span style='background-color:#f8d7da; color:#721c24; padding: 5px 10px; border-radius: 5px;'>{s}</span>\" for s in missing_skills])}</div>", unsafe_allow_html=True)
        else:
            st.success("You have all the key skills mentioned in the JD!")

        st.subheader("Detailed HR Assessment (AI-Powered)")
        # Updated call to generate_hr_summary (using the new local function)
        job_domain = detect_job_domain(jd_name_for_results, jd_text)
        hr_summary = generate_hr_summary(
            name=resume_info.get('Name', 'Candidate'),
            score=scores['Final Match Score'],
            experience=resume_info.get('Years of Experience', 0),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            cgpa=resume_info.get('CGPA', 'N/A'),
            job_domain=job_domain,
            tone=summary_tone
        )
        st.markdown(hr_summary)

    st.markdown("---")
    st.subheader("📚 Course Suggestions for Missing Skills")
    if missing_skills:
        suggested_courses = []
        for skill in missing_skills:
            for course_rec in COURSE_DATABASE:
                if skill.lower() in course_rec["skill"].lower():
                    suggested_courses.append(course_rec)
        
        if suggested_courses:
            st.write("Here are some courses that can help you bridge the skill gaps:")
            for course in suggested_courses:
                st.markdown(f"- **{course['course']}** on {course['platform']} ([Link]({course['link']})) (Skill: {course['skill']})")
        else:
            st.info("No specific course suggestions found for your missing skills in our database.")
    else:
        st.info("You have no missing skills from the JD! Keep up the great work.")


    st.markdown("---")
    st.subheader("🏅 ScreenerPro Certificate")
    if scores['Final Match Score'] >= 50:
        st.success("Congratulations! You qualify for a ScreenerPro Assessment Certificate.")
        candidate_name_for_cert = st.text_input("Enter your full name for the certificate:", value=resume_info.get("Name", "Candidate Name"))
        
        if st.button("Generate Certificate"):
            if candidate_name_for_cert:
                html_cert, pdf_cert, cert_id = generate_certificate(
                    candidate_name_for_cert,
                    scores['Final Match Score'],
                    scores['AI Tag'],
                    resume_info.get("Email", "N/A"),
                    resume_info.get("Phone Number", "N/A"),
                    resume_info.get("Years of Experience", 0),
                    resume_info.get("CGPA", "N/A"),
                    matched_skills
                )
                st.session_state['html_cert'] = html_cert
                st.session_state['pdf_cert'] = pdf_cert
                st.session_state['cert_id'] = cert_id
                st.session_state['candidate_name_for_cert'] = candidate_name_for_cert

                st.download_button(
                    label="Download Certificate (PDF)",
                    data=pdf_cert,
                    file_name=f"ScreenerPro_Certificate_{candidate_name_for_cert.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.markdown("You can also view the HTML certificate directly:")
                st.download_button(
                    label="Download Certificate (HTML)",
                    data=html_cert,
                    file_name=f"ScreenerPro_Certificate_{candidate_name_for_cert.replace(' ', '_')}.html",
                    mime="text/html"
                )
                st.markdown("---")
                st.write("Share your achievement!")
                linkedin_share_url = f"https://www.linkedin.com/shareArticle?mini=true&url=https://screenerpro.com/certificates/{cert_id}&title=ScreenerPro%20Assessment%20Certificate&summary=I%20just%20received%20a%20ScreenerPro%20AI-powered%20resume%20assessment%20certificate%20with%20a%20score%20of%20{scores['Final Match Score']:.2f}%21%20Check%20it%20out%3A&source=ScreenerPro"
                whatsapp_share_url = f"https://wa.me/?text=Check%20out%20my%20ScreenerPro%20AI-powered%20resume%20assessment%20certificate%20with%20a%20score%20of%20{scores['Final Match Score']:.2f}%25%21%20Verify%20it%20here%3A%20https://screenerpro.com/certificates/{cert_id}"
                
                st.markdown(f"[Share on LinkedIn]({linkedin_share_url}) | [Share on WhatsApp]({whatsapp_share_url})")

                # Save to Firestore
                certificate_data = {
                    "certificate_id": cert_id,
                    "candidate_name": candidate_name_for_cert,
                    "final_score": scores['Final Match Score'],
                    "ai_tag": scores['AI Tag'],
                    "email": resume_info.get("Email", "N/A"),
                    "experience": resume_info.get("Years of Experience", 0),
                    "cgpa": resume_info.get("CGPA", "N/A"),
                    "matched_skills": matched_skills
                }
                save_certificate_data_to_firestore(certificate_data)

                # Email sending functionality (requires secrets)
                st.markdown("---")
                st.subheader("Email Your Certificate")
                receiver_email = st.text_input("Enter recipient email address (e.g., your email):", value=resume_info.get("Email", ""))
                if st.button("Send Certificate via Email"):
                    if receiver_email and st.session_state.get('pdf_cert'):
                        email_subject = f"ScreenerPro Assessment Certificate for {candidate_name_for_cert}"
                        email_body_plain = f"Dear {candidate_name_for_cert},\n\nCongratulations on receiving your ScreenerPro Assessment Certificate!\n\nYour Final Match Score is: {scores['Final Match Score']:.2f}%\nAI Tag: {scores['AI Tag']}\n\nPlease find your certificate attached.\n\nBest regards,\nScreenerPro Team\n\nVerify your certificate here: https://screenerpro.com/certificates/{cert_id}"
                        email_html_body = f"""
                        <p>Dear {candidate_name_for_cert},</p>
                        <p>Congratulations on receiving your <b>ScreenerPro Assessment Certificate!</b></p>
                        <p>Your <b>Final Match Score</b> is: <b>{scores['Final Match Score']:.2f}%</b></p>
                        <p><b>AI Tag:</b> {scores['AI Tag']}</p>
                        <p>Please find your certificate attached.</p>
                        <p>Best regards,<br><b>ScreenerPro Team</b></p>
                        <p>Verify your certificate here: <a href="https://screenerpro.com/certificates/{cert_id}">ScreenerPro Certificate Verification</a></p>
                        """
                        if send_email(receiver_email, email_subject, email_body_plain, email_html_body, f"ScreenerPro_Certificate_{candidate_name_for_cert.replace(' ', '_')}.pdf", st.session_state['pdf_cert']):
                            st.success(f"Certificate sent successfully to {receiver_email}!")
                        else:
                            st.error("Failed to send email. Please check your email configuration (secrets) and try again.")
                    else:
                        st.warning("Please generate the certificate and provide a recipient email address.")

            else:
                st.warning("Please enter your name to generate the certificate.")
    else:
        st.info(f"Your Final Match Score of {scores['Final Match Score']:.2f}% is below the 50% threshold for certificate generation. Keep improving!")

elif uploaded_resume_file and not jd_text:
    st.warning("Please upload or select a Job Description to proceed with the assessment.")
elif jd_text and not uploaded_resume_file:
    st.warning("Please upload your Resume to proceed with the assessment.")
else:
    st.info("Upload a Job Description and your Resume to get started with your AI-powered assessment!")

st.markdown("---")
st.markdown("Developed with ❤️ by ScreenerPro AI")
