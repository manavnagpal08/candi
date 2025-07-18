import streamlit as st
import requests
import json
import os
import uuid
from datetime import datetime, timedelta, date # Added 'date' to the import
import random
import traceback
import time # Added import for the 'time' module

# --- Helper functions copied from resume_screen.py for self-containment ---

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
                if isinstance(item, dict):
                    list_values.append({"mapValue": {"fields": _convert_to_firestore_rest_format(item)["fields"]}})
                elif isinstance(item, list):
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
        
        collection_id = "leaderboard" 
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_id}?key={api_key}"

        data_to_send = result_data.copy()
        # Ensure categorized skills are dicts, not JSON strings, before converting to Firestore format
        if isinstance(data_to_send.get('Matched Keywords (Categorized)'), str):
            try:
                data_to_send['Matched Keywords (Categorized)'] = json.loads(data_to_send['Matched Keywords (Categorized)'])
            except json.JSONDecodeError:
                data_to_send['Matched Keywords (Categorized)'] = {}
        if isinstance(data_to_send.get('Missing Skills (Categorized)'), str):
            try:
                data_to_send['Missing Skills (Categorized)'] = json.loads(data_to_send['Missing Skills (Categorized)'])
            except json.JSONDecodeError:
                data_to_send['Missing Skills (Categorized)'] = {}

        if isinstance(data_to_send.get('Date Screened'), (datetime, date)):
            data_to_send['Date Screened'] = data_to_send['Date Screened'].strftime("%Y-%m-%d")

        data_to_send.pop('Resume Raw Text', None) # Remove raw text if present

        firestore_payload = _convert_to_firestore_rest_format(data_to_send)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(firestore_payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        return True, response.json().get('name') # Return success and document name/ID
    except KeyError as e:
        return False, f"Firebase REST API configuration error: Missing secret key '{e}'."
    except requests.exceptions.HTTPError as e:
        return False, f"Failed to save results to Firestore: HTTP Error {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return False, f"An unexpected error occurred while saving to Firestore: {e}\n{traceback.format_exc()}"

# --- Dummy Data Generation Logic ---

def generate_dummy_candidate_data(index):
    """Generates a single dictionary of dummy candidate data."""
    # Updated names list to include Indian names
    names = [
    "Priya Sharma", "Rahul Singh", "Ananya Gupta", "Aryan Kumar", "Diya Patel",
    "Rohan Mehta", "Ishita Verma", "Kabir Khan", "Sanya Reddy", "Vivaan Joshi",
    "Aisha Rahman", "Arjun Nair", "Meera Devi", "Siddharth Rao", "Zara Ali",
    "Dev Sharma", "Kavya Singh", "Neil Gupta", "Riya Patel", "Samar Mehta",
    "Shreya Verma", "Veer Khan", "Aditi Reddy", "Dhruv Joshi", "Naina Rahman",
    "Om Nair", "Tara Devi", "Vihaan Rao", "Zoya Ali", "Amit Kumar",
    "Bhavna Singh", "Chetan Gupta", "Deepa Patel", "Eshan Mehta", "Falguni Verma",
    "Gaurav Khan", "Hina Reddy", "Inder Joshi", "Jaya Rahman", "Karan Nair",
    "Lata Devi", "Manoj Rao", "Nisha Ali", "Omkar Sharma", "Pooja Singh",
    "Qasim Gupta", "Renu Patel", "Sanjay Mehta", "Tina Verma", "Uday Khan",
    "Vani Reddy", "Waseem Joshi", "Xena Rahman", "Yash Nair", "Zainab Devi",
    
    # Newly added (50 more)
    "Aarav Kapoor", "Sneha Desai", "Harsh Vardhan", "Nikita Iyer", "Tanmay Dubey",
    "Lavanya Pillai", "Raghav Bansal", "Chitra Nair", "Ibrahim Shaikh", "Pranavi Sharma",
    "Aniket Choudhary", "Simran Lamba", "Yuvraj Sethi", "Reetika Das", "Abhinav Malhotra",
    "Myra Menon", "Rajeev Tripathi", "Shruti Kaul", "Tejas Chopra", "Gayatri Sen",
    "Ritvik Bhattacharya", "Nandita Joshi", "Krishna Yadav", "Pallavi Mishra", "Atharv Jain",
    "Niharika Mohanty", "Farhan Syed", "Avantika Kulkarni", "Sahil Arora", "Tanvi Rawat",
    "Varun Agrawal", "Ila Dey", "Parthiv Shetty", "Mahira Noor", "Shivam Tiwari",
    "Divya Chauhan", "Aditya Ghosh", "Roshni Kalra", "Arnav Deshmukh", "Trisha George",
    "Rehan Qureshi", "Mehul Dutta", "Srishti Anand", "Vivaan Bhatt", "Nausheen Fatima",
    "Darshan Vora", "Juhi Jain", "Kunal Sengupta", "Anaya Kaur", "Zuber Lakhani"
]

    jds = ["Software Engineer JD", "Data Scientist JD", "HR Manager JD", "Product Manager JD", "Marketing Specialist JD"]
    locations = ["Bengaluru", "New York", "London", "Hyderabad", "San Francisco", "Mumbai", "Toronto", "Chennai", "Delhi", "Pune", "Kolkata", "Ahmedabad"]
    languages = ["English", "English, Hindi", "English, Spanish", "English, French", "English, Marathi", "English, Bengali", "English, Tamil"]
    tags = ["👑 Exceptional Match", "🔥 Strong Candidate", "✨ Promising Fit", "⚠️ Needs Review", "❌ Limited Match"]
    
    candidate_name = random.choice(names) + f" {index}"
    score = round(random.uniform(30, 100), 2)
    years_exp = round(random.uniform(0, 15), 1)
    cgpa = round(random.uniform(2.0, 4.0), 2) if random.random() > 0.2 else None # 80% chance of having CGPA
    email = f"{candidate_name.lower().replace(' ', '.')}{random.randint(1,100)}@example.com"
    phone = f"+91-{random.randint(70000,99999)}-{random.randint(10000,99999)}" # Indian phone number format
    location = random.choice(locations)
    langs = random.choice(languages)

    # Simplified categorized skills for dummy data
    dummy_matched_cat = {
        "Programming Languages": ["Python", "Java"] if score > 70 else [],
        "Cloud Platforms": ["AWS"] if score > 80 else [],
        "Soft Skills": ["Communication"]
    }
    dummy_missing_cat = {
        "DevOps & MLOps": ["Docker", "Kubernetes"] if score < 60 else [],
        "Security": ["Cybersecurity"] if score < 50 else []
    }

    certificate_rank = "Not Applicable"
    if score >= 90:
        certificate_rank = "🏅 Elite Match"
    elif score >= 80:
        certificate_rank = "⭐ Strong Match"
    elif score >= 75:
        certificate_rank = "✅ Good Fit"

    tag = "❌ Limited Match"
    if score >= 90 and years_exp >= 5 and score > 85: # Simplified logic for tag
        tag = "👑 Exceptional Match"
    elif score >= 80 and years_exp >= 3:
        tag = "🔥 Strong Candidate"
    elif score >= 60 and years_exp >= 1:
        tag = "✨ Promising Fit"
    elif score >= 40:
        tag = "⚠️ Needs Review"

    # Random date within the last year
    today = datetime.now().date()
    random_days_ago = random.randint(0, 365)
    date_screened = today - timedelta(days=random_days_ago)

    return {
        "File Name": f"resume_{candidate_name.replace(' ', '_')}.pdf",
        "Candidate Name": candidate_name,
        "Score (%)": score,
        "Years Experience": years_exp,
        "CGPA (4.0 Scale)": cgpa,
        "Email": email,
        "Phone Number": phone,
        "Location": location,
        "Languages": langs,
        "Education Details": "Dummy University, 2023",
        "Work History": "Dummy Corp (2020-Present); Another Co (2018-2020)",
        "Project Details": "Project X (Python, ML); Project Y (Web, React)",
        "AI Suggestion": "This is a dummy AI suggestion for demonstration.",
        "Detailed HR Assessment": "This is a dummy detailed HR assessment for demonstration purposes. It indicates a good fit for general roles.",
        "Matched Keywords": "python, java, aws, communication",
        "Missing Skills": "docker, kubernetes",
        "Matched Keywords (Categorized)": json.dumps(dummy_matched_cat),
        "Missing Skills (Categorized)": json.dumps(dummy_missing_cat),
        "Semantic Similarity": round(random.uniform(0.3, 0.9), 2),
        "Resume Raw Text": "This is a dummy resume text. It contains some keywords like python, java, and aws.",
        "JD Used": random.choice(jds),
        "Date Screened": date_screened,
        "Certificate ID": str(uuid.uuid4()),
        "Certificate Rank": certificate_rank,
        "Tag": tag
    }

def generate_fake_data_page():
    st.set_page_config(page_title="Generate Fake Data", layout="centered")
    st.title("🧪 Generate Fake ScreenerPro Data")
    st.warning("⚠️ **Caution:** This tool will add dummy entries to your live Firestore database. Use it for testing and demonstration purposes only.")
    st.markdown("---")

    # Increased max_value to 500 and default value to 50
    num_entries = st.number_input("Number of fake entries to generate:", min_value=1, max_value=500, value=50, step=1)

    if st.button("🚀 Generate and Upload Fake Data"):
        st.info(f"Generating and uploading {num_entries} fake entries to Firestore...")
        progress_bar = st.progress(0)
        success_count = 0
        fail_count = 0
        failed_entries = []

        for i in range(num_entries):
            dummy_data = generate_dummy_candidate_data(i + 1)
            success, message = save_screening_result_to_firestore_rest(dummy_data)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                failed_entries.append(f"Entry {i+1} ({dummy_data.get('Candidate Name', 'N/A')}): {message}")
            
            progress_bar.progress((i + 1) / num_entries)
            time.sleep(0.1) # Small delay to show progress

        st.markdown("---")
        if success_count > 0:
            st.success(f"🎉 Successfully uploaded {success_count} fake entries!")
        if fail_count > 0:
            st.error(f"❌ Failed to upload {fail_count} entries.")
            with st.expander("View Failed Entries Details"):
                for entry in failed_entries:
                    st.write(entry)
        st.markdown("---")
        st.info("You can now check your 'Leaderboard' and 'Total Resumes Screened' pages to see the new data.")

if __name__ == "__main__":
    generate_fake_data_page()
