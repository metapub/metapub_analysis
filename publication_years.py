import argparse
from metapub import PubMedFetcher
from datetime import datetime
import time

def fetch_pmids_for_date_range(journal, start_year, end_year, fetcher, retmax=9999, timeout=30):
    query = f"{journal}[Journal] AND {start_year}:{end_year}[PDAT]"
    print(f"Running query: {query}")
    try:
        start_time = time.time()
        pmids = fetcher.pmids_for_query(query, retmax=retmax)
        elapsed_time = time.time() - start_time
        print(f"Number of PMIDs found for {start_year}-{end_year}: {len(pmids)} (Time taken: {elapsed_time:.2f} seconds)")
        return pmids
    except Exception as e:
        print(f"Error during query: {e}")
        return []

def get_publication_years(journal):
    fetch = PubMedFetcher()
    current_year = datetime.now().year

    # Start querying by decade to find the oldest publication year
    oldest_pmids = []
    for year in range(1900, current_year + 1, 10):
        end_year = min(year + 9, current_year)
        decade_pmids = fetch_pmids_for_date_range(journal, year, end_year, fetch)
        if decade_pmids:
            oldest_pmids.extend(decade_pmids)
            break

    if not oldest_pmids:
        print("No PMIDs found.")
        return 1960, current_year

    # Query to get the most recent PMIDs to determine the most recent publication year
    recent_pmids = fetch_pmids_for_date_range(journal, current_year - 5, current_year, fetch, retmax=500)
    
    if not recent_pmids:
        # If no recent PMIDs are found, use the most recent PMID from the oldest PMIDs
        recent_pmids = oldest_pmids

    # Sort PMIDs to get the oldest and most recent
    oldest_pmids = sorted(oldest_pmids)
    oldest_pmid = oldest_pmids[0]

    recent_pmids = sorted(recent_pmids)
    recent_pmid = recent_pmids[-1]

    print(f"Oldest PMID: {oldest_pmid}")
    print(f"Most Recent PMID: {recent_pmid}")

    oldest_article = fetch.article_by_pmid(oldest_pmid)
    recent_article = fetch.article_by_pmid(recent_pmid)

    oldest_year = int(oldest_article.year)
    recent_year = int(recent_article.year)

    print(f"Oldest Year: {oldest_year}")
    print(f"Most Recent Year: {recent_year}")

    return max(oldest_year, 1960), recent_year

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate publication year range for a journal")
    parser.add_argument("--journal", type=str, default="J Med Chem", help="Journal name")
    args = parser.parse_args()

    journal = args.journal
    print(f"Calculating publication years for journal: {journal}")
    oldest_year, recent_year = get_publication_years(journal)
    print(f"Publication range for {journal}: {oldest_year} - {recent_year}")

