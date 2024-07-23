import streamlit as st
from metapub import FindIt
from database import fetch_result_for_pmid, save_result
from fetch_utils import check_downloadable

# Function to process each PMID
def process_pmids(pmids, selected_journal, selected_year, result_display, progress_bar, progress_text):
    free_count = 0
    publisher_count = 0
    downloadable_count = 0
    non_downloadable_count = 0
    cached_count = 0

    for i, pmid in enumerate(pmids):
        cached_result = fetch_result_for_pmid(pmid)
        if cached_result:
            cached_count += 1
            url, reason, downloadable = cached_result
            if url:
                if "europepmc" in url:
                    free_count += 1
                    downloadable_count += 1
                    result_display.markdown(f"PMID {pmid}: [URL]({url}) [Free] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                else:
                    publisher_count += 1
                    if downloadable == 200:
                        downloadable_count += 1
                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                    elif downloadable == 402:
                        non_downloadable_count += 1
                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[402]</span>", unsafe_allow_html=True)
                    else:
                        non_downloadable_count += 1
                        result_display.markdown(f"PMID {pmid}: [URL]({url}) [Publisher] <span style='color: red;'>[{downloadable}]</span>", unsafe_allow_html=True)
            else:
                result_display.write(f"PMID {pmid}: No URL ({reason}).")
        else:
            src = FindIt(pmid, verify=False)
            if src.url:
                if "europepmc" in src.url:
                    free_count += 1
                    downloadable_count += 1
                    result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Free] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                    save_result(pmid, selected_journal, selected_year, src.url, None, 200)
                else:
                    publisher_count += 1
                    result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher]", unsafe_allow_html=True)
                    response_code = check_downloadable(src.url)
                    if response_code == 200:
                        downloadable_count += 1
                        result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                    else:
                        non_downloadable_count += 1
                        result_display.markdown(f"PMID {pmid}: [URL]({src.url}) [Publisher] <span style='color: red;'>[{response_code}]</span>", unsafe_allow_html=True)
                    save_result(pmid, selected_journal, selected_year, src.url, None, response_code)
            else:
                reason = src.reason
                if "DENIED" in reason and src.doi:
                    doi_url = f"https://dx.doi.org/{src.doi}"
                    response_code = check_downloadable(doi_url)
                    if response_code == 200:
                        result_display.markdown(f"PMID {pmid}: [URL]({doi_url}) [Publisher] <span style='color: green;'>[200]</span>", unsafe_allow_html=True)
                        save_result(pmid, selected_journal, selected_year, doi_url, None, 200)
                    else:
                        result_display.markdown(f"PMID {pmid}: [URL]({doi_url}) [Publisher] <span style='color: red;'>[{response_code}]</span>", unsafe_allow_html=True)
                        save_result(pmid, selected_journal, selected_year, doi_url, reason, response_code)
                else:
                    if not src.doi:
                        reason = "No DOI found."
                    save_result(pmid, selected_journal, selected_year, None, reason, 402)
                    result_display.write(f"PMID {pmid}: No URL ({reason}).")

        # Update progress bar
        progress_bar.progress((i + 1) / len(pmids))
        progress_text.text(f"Processing {i + 1}/{len(pmids)} articles")

    return free_count, publisher_count, downloadable_count, non_downloadable_count, cached_count

# Function to display statistics
def display_statistics(pmids, cached_count, free_count, publisher_count, downloadable_count, non_downloadable_count):
    st.write(f"Total articles processed: {len(pmids)}")
    st.write(f"Articles loaded from cache: {cached_count}")
    st.write(f"Free articles: {free_count}")
    st.write(f"Publisher articles: {publisher_count}")
    st.write(f"Downloadable articles: {downloadable_count}")
    st.write(f"Non-downloadable articles: {non_downloadable_count}")

