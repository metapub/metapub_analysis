import os
import streamlit as st
from metapub import PubMedFetcher
from database import fetch_publication_years, save_publication_years
from fetch_utils import get_publication_years

# Function to get list of publisher files and strip the ".txt"
def get_publishers(publisher_dir):
    files = os.listdir(publisher_dir)
    publishers = sorted([file.replace(".txt", "") for file in files if file.endswith(".txt")])
    return publishers

# Function to read journal list from the selected publisher file
def get_journal_list(publisher_dir, publisher):
    file_path = os.path.join(publisher_dir, f"{publisher}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            journals = file.read().splitlines()
        return journals
    else:
        return ["File not found."]

# Function to calculate and display publication years
def calculate_publication_years(selected_journal):
    try:
        # Check cache for publication years
        cached_years = fetch_publication_years(selected_journal)
        if cached_years:
            oldest_year, recent_year, valid_years = cached_years
            st.session_state["oldest_year"] = oldest_year
            st.session_state["recent_year"] = recent_year
            st.session_state["valid_years"] = valid_years
        else:
            oldest_year, recent_year, valid_years = get_publication_years(selected_journal)
            st.session_state["oldest_year"] = oldest_year
            st.session_state["recent_year"] = recent_year
            st.session_state["valid_years"] = valid_years
            # Save publication years to cache
            save_publication_years(selected_journal, oldest_year, recent_year, valid_years)
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

