import streamlit as st
from fetch_helpers import get_publishers, get_journal_list, calculate_publication_years
from process_helpers import process_pmids, display_statistics
from database import init_db, fetch_results
from metapub import PubMedFetcher

# Set the directory where publisher files are stored
publisher_dir = "FINDIT_EXPERIMENT/publishers"

# Initialize the database at the start
init_db()

# Step 1: Select Publisher and Journal
st.sidebar.header("Step 1: Select Publisher and Journal")
publishers_display = get_publishers(publisher_dir)
selected_publisher = st.sidebar.selectbox("Publisher", publishers_display)

if selected_publisher:
    journals = get_journal_list(publisher_dir, selected_publisher)
    selected_journal = st.sidebar.selectbox("Journal", journals)

    if selected_journal:
        st.sidebar.write(f"Selected Journal: {selected_journal}")

        # Step 2: Calculate and Display Publication Year Range
        if st.sidebar.button("Calculate Publication Years"):
            with st.spinner("Calculating publication years..."):
                calculate_publication_years(selected_journal)

        if "oldest_year" in st.session_state and "recent_year" in st.session_state and "valid_years" in st.session_state:
            oldest_year = st.session_state["oldest_year"]
            recent_year = st.session_state["recent_year"]
            valid_years = st.session_state["valid_years"]

            if oldest_year is None or recent_year is None or oldest_year > recent_year:
                st.write("Could not determine the publication range for this journal.")
            else:
                st.write(f"Publication range for {selected_journal}: {oldest_year} - {recent_year}")

                # Step 3: Select Year and Run the Test
                selected_year = st.selectbox("Select Year", valid_years)

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
                        
                        free_count, publisher_count, downloadable_count, non_downloadable_count, cached_count = process_pmids(pmids, selected_journal, selected_year, result_display, progress_bar, progress_text)

                        # Display statistics
                        display_statistics(pmids, cached_count, free_count, publisher_count, downloadable_count, non_downloadable_count)

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

