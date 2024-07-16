import streamlit as st
import os
import sqlite3
from metapub import PubMedFetcher, FindIt
from datetime import datetime

# Set the directory where publisher files are stored
publisher_dir = "FINDIT_EXPERIMENT/publishers"
db_path = "findit_results.db"

# Function to get list of publisher files and strip the ".txt"
def get_publishers():
    files = os.listdir(publisher_dir)
    publishers = sorted([file.replace(".txt", "") for file in files if file.endswith(".txt")])
    return publishers

# Function to read journal list from the selected publisher file
def get_journal_list(publisher):
    file_path = os.path.join(publisher_dir, f"{publisher}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            journals = file.read().splitlines()
        return journals
    else:
        return ["File not found."]

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (pmid INTEGER PRIMARY KEY, journal TEXT, year INTEGER, url TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

# Save result to database
def save_result(pmid, journal, year, url, reason):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO results (pmid, journal, year, url, reason) VALUES (?, ?, ?, ?, ?)",
              (pmid, journal, year, url, reason))
    conn.commit()
    conn.close()

# Function to get the oldest and most recent publication years for a journal
def get_publication_years(journal):
    fetch = PubMedFetcher()
    query = f"{journal}[Journal]"
    pmids = fetch.pmids_for_query(query, retmax=1, mindate="1900", maxdate=str(datetime.now().year))
    if not pmids:
        return 1960, datetime.now().year
    
    oldest_pmid = pmids[-1]
    recent_pmid = pmids[0]
    
    oldest_article = fetch.article_by_pmid(oldest_pmid)
    recent_article = fetch.article_by_pmid(recent_pmid)
    
    oldest_year = oldest_article.year
    recent_year = recent_article.year
    
    return max(oldest_year, 1960), recent_year

# Initialize the database at the start
init_db()

# Get the list of publishers dynamically
publishers_display = get_publishers()

# Sidebar for publisher selection
st.sidebar.header("Select Publisher")
selected_publisher = st.sidebar.selectbox("Publisher", publishers_display)

# Get the list of journals for the selected publisher
journals = get_journal_list(selected_publisher)
selected_journal = st.sidebar.selectbox("Journal", journals)

# Sidebar for year selection
st.sidebar.header("Select Year")

# Get the publication years for the selected journal
oldest_year, recent_year = get_publication_years(selected_journal)

selected_year = st.sidebar.slider("Year", min_value=oldest_year, max_value=recent_year, value=recent_year)

# Button to start the test
if st.sidebar.button("Run Test"):
    try:
        query = f"{selected_journal}[Journal] AND {selected_year}[PDAT]"
        pmids = fetch.pmids_for_query(query)
        st.write(f"Found {len(pmids)} articles for {selected_journal} in {selected_year}.")
        
        # Process each PMID
        for pmid in pmids:
            src = FindIt(pmid, verify=False)
            if src.url:
                save_result(pmid, selected_journal, selected_year, src.url, None)
                st.write(f"PMID {pmid}: Found URL {src.url}")
            else:
                save_result(pmid, selected_journal, selected_year, None, "No URL found")
                st.write(f"PMID {pmid}: No URL found")
    except Exception as e:
        st.write(f"Error: {e}")

# Display results
st.header("Results")
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT * FROM results")
rows = c.fetchall()
for row in rows:
    st.write(row)
conn.close()

