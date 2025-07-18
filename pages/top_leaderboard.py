import streamlit as st
import pandas as pd

def top_leaderboard_page():
    st.title("🏆 Top Leaderboard")
    st.write("See how you rank against other candidates!")
    
    leaderboard_data = {
        "Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Candidate": ["Alice Johnson", "Bob Williams", "Charlie Brown", "Diana Miller", "Eve Davis",
                      "Frank White", "Grace Lee", "Harry Kim", "Ivy Chen", "Jack Green"],
        "Score": [980, 950, 920, 890, 870, 850, 830, 810, 790, 770],
        "Company": ["Tech Solutions", "Innovate Corp", "Global Digital", "Data Dynamics", "Future Systems",
                    "Apex Innovations", "Quantum Tech", "Bright Minds", "Synergy Group", "Elite Software"]
    }
    df = pd.DataFrame(leaderboard_data)
    st.dataframe(df.set_index("Rank"), use_container_width=True)
