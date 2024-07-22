import streamlit as st
import os
import sqlite3
from publication_years import get_publication_years
from metapub import PubMedFetcher, FindIt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                 (pmid INTEGER PRIMARY KEY, journal TEXT, year INTEGER, url TEXT, reason TEXT, downloadable INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS publication_years
                 (journal TEXT PRIMARY KEY, oldest_year INTEGER, recent_year INTEGER)''')
    conn.commit()
    conn.close()

# Save result to database
def save_result(pmid, journal, year, url, reason, downloadable):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO results (pmid, journal, year, url, reason, downloadable) VALUES (?, ?, ?, ?, ?, ?)",
              (pmid, journal, year, url, reason, downloadable))
    conn.commit()
    conn.close()

# Save publication years to database
def save_publication_years(journal, oldest_year, recent_year):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO publication_years (journal, oldest_year, recent_year) VALUES (?, ?, ?)",
              (journal, oldest_year, recent_year))
    conn.commit()
    conn.close()

# Fetch results for the current journal and year from the database
def fetch_results(journal, year):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT pmid, url, reason, downloadable FROM results WHERE journal=? AND year=?", (journal, year))
    rows = c.fetchall()
    conn.close()
    return rows

# Fetch publication years for a journal from the database
def fetch_publication_years(journal):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT oldest_year, recent_year FROM publication_years WHERE journal=?", (journal,))
    row = c.fetchone()
    conn.close()
    return row

# Fetch result for a specific PMID
def fetch_result_for_pmid(pmid):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT url, reason, downloadable FROM results WHERE pmid=?", (pmid,))
    row = c.fetchone()
    conn.close()
    return row

# Check if a URL is downloadable and is a PDF using Selenium
def check_downloadable(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        if "application/pdf" in driver.execute_script("return document.contentType"):
            response_code = 200
        else:
            response_code = 402  # Not a PDF
    except Exception as e:
        response_code = 400  # Use a different code if an error occurs
    finally:
        driver.quit()
    
    return response_code

# Initialize the database at the start
init_db()

# Step 1: Select Publisher and Journal
st.sidebar.header("Step 1: Select Publisher and Journal")
publishers_display = get_publishers()
selected_publisher = st.sidebar.selectbox("Publisher", publishers_display)

if selected_publisher:
    journals = get_journal_list(selected_publisher)
    selected_journal = st.sidebar.selectbox("Journal", journals)

    if selected_journal:
        st.sidebar.write(f"Selected Journal: {selected_journal}")

        # Step 2: Calculate and Display Publication Year Range
        if st.sidebar.button("Calculate Publication Years"):
            with st.spinner("Calculating publication years..."):
                try:
                    # Check cache for publication years
                    cached_years = fetch_publication_years(selected_journal)
                    if cached_years:
                        oldest_year, recent_year = cached_years
                        st.session_state["oldest_year"] = oldest_year
                        st.session_state["recent_year"] = recent_year
                    else:
                        oldest_year, recent_year = get_publication_years(selected_journal)
                        st.session_state["oldest_year"] = oldest_year
                        st.session_state["recent_year"] = recent_year
                        # Save publication years to cache
                        save_publication_years(selected_journal, oldest_year, recent_year)
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")

        if "oldest_year" in st.session_state and "recent_year" in st.session_state:
            oldest_year = st.session_state["oldest_year"]
            recent_year = st.session_state["recent_year"]
            st.write(f"Publication range for {selected_journal}: {oldest_year} - {recent_year}")

            # Step 3: Select Year and Run the Test
            selected_year = st.slider("Select Year", min_value=oldest_year, max_value=recent_year, value=recent_year)
            
            if st.button("Run Test"):
                fetch = PubMedFetcher()
                try:
                    query = f"{selected_journal}[Journal] AND {selected_year}[PDAT]"
                    pmids = fetch.pmids_for_query(query)
                    st.write(f"Found {len(pmids)} articles for {selected_journal} in {selected_year}.")
                    
                    # Initialize progress bar
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    result_display = st.empty()
                    
                    free_count = 0
                    publisher_count = 0
                    downloadable_count = 0
                    non_downloadable_count = 0
                    cached_count = 0

                    # Process each PMID
                    for i, pmid in enumerate(pmids):
                        cached_result = fetch_result_for_pmid(pmid)
                        if cached_result:
                            cached_count += 1
                            url, reason, downloadable = cached_result
                            if url:
                                if "europepmc" in url:
                                    result_display.markdown(f"PMID {pmid}: [URL]({url}) [Free] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                                    free_count += 1
                                    downloadable_count += 1
                                else:
                                    if downloadable == 200:
                                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                                        downloadable_count += 1
                                    elif downloadable == 402:
                                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[402]</span>", unsafe_allow_html=True)
                                    else:
                                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[{downloadable}]</span>", unsafe_allow_html=True)
                                        non_downloadable_count += 1
                            else:
                                result_display.write(f"PMID {pmid}: No URL ({reason}).")
                        else:
                            src = FindIt(pmid, verify=False)
                            if src.url:
                                if "europepmc" in src.url:
                                    result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Free] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                                    free_count += 1
                                    downloadable_count += 1
                                    save_result(pmid, selected_journal, selected_year, src.url, None, 200)
                                else:
                                    result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher]", unsafe_allow_html=True)
                                    publisher_count += 1
                                    response_code = check_downloadable(src.url)
                                    if response_code == 200:
                                        result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                                        downloadable_count += 1
                                    else:
                                        result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher] <span style='color: red;'>[{response_code}]</span>", unsafe_allow_html=True)
                                        non_downloadable_count += 1
                                    save_result(pmid, selected_journal, selected_year, src.url, None, response_code)
                            else:
                                reason = src.reason
                                if not src.doi:
                                    reason = "No DOI found."
                                save_result(pmid, selected_journal, selected_year, None, reason, None)
                                result_display.write(f"PMID {pmid}: No URL ({reason}).")
                        
                        # Update progress bar
                        progress_bar.progress((i + 1) / len(pmids))
                        progress_text.text(f"Processing {i + 1}/{len(pmids)} articles")

                    # Display statistics
                    st.write(f"Total articles processed: {len(pmids)}")
                    st.write(f"Articles loaded from cache: {cached_count}")
                    st.write(f"Free articles: {free_count}")
                    st.write(f"Publisher articles: {publisher_count}")
                    st.write(f"Downloadable articles: {downloadable_count}")
                    st.write(f"Non-downloadable articles: {non_downloadable_count}")

                except Exception as e:
                    st.write(f"Error: {e}")

                # Step 4: Display Results for the Current Journal and Year
                results = fetch_results(selected_journal, selected_year)
                if results:
                    st.header(f"Results for {selected_journal} in {selected_year}")
                    for row in results:
                        pmid, url, reason, downloadable = row
                        if url:
                            if "europepmc" in url:
                                st.markdown(f"PMID {pmid}: [URL]({url}) [Free] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                            else:
                                if downloadable == 200:
                                    st.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                                elif downloadable == 402:
                                    st.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[402]</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[{downloadable}]</span>", unsafe_allow_html=True)
                        else:
                            st.write(f"PMID {pmid}: No URL found, reason: {reason}")

# Optionally clear the session state if needed
if st.button("Clear Session State"):
    st.session_state.clear()

