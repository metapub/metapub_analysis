import csv
import logging
import random
from metapub import PubMedFetcher
from metapub.findit import SUPPORTED_JOURNALS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
file_handler = logging.FileHandler('/tmp/script_progress.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

MEDLINE_JOURNAL_LIST = "/tmp/journals.csv"
OUTPUT_CSV = "/tmp/findit_journal_coverage.csv"

def fetch_pmids_for_journal(journal_abbrev):
    fetcher = PubMedFetcher()
    pmids = {'oldest': None, 'newest': None, 'random': None}

    try:
        # Fetch the oldest PMID
        oldest_pmids = fetcher.pmids_for_query(f'{journal_abbrev}[TA]', mindate='1800', maxdate='2009', retmax=1)
        if oldest_pmids:
            pmids['oldest'] = oldest_pmids[0]

        # Fetch the newest PMID
        newest_pmids = fetcher.pmids_for_query(f'{journal_abbrev}[TA]', mindate='2010', maxdate='2024', retmax=1)
        if newest_pmids:
            pmids['newest'] = newest_pmids[0]

        # Fetch random PMIDs and select one
        all_pmids = fetcher.pmids_for_query(f'{journal_abbrev}[TA]', retmax=100)
        if all_pmids:
            pmids['random'] = random.choice(all_pmids)

    except Exception as e:
        logger.error(f"Error fetching PMIDs for {journal_abbrev}: {e}")

    return pmids

def create_output_csv(input_file_path, output_file_path):
    total_entries = 0
    processed_entries = 0
    pmids_collected = 0

    # First count the total number of entries
    with open(input_file_path, newline='') as infile:
        reader = csv.DictReader(infile)
        total_entries = sum(1 for row in reader)
    logger.info(f"Total entries to process: {total_entries}")

    with open(input_file_path, newline='') as infile, open(output_file_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['journal_abbrev', 'oldest_PMID', 'newest_PMID', 'random_PMID', 'FindIt_coverage']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            journal_abbrev = row['MedAbbr']
            if journal_abbrev in SUPPORTED_JOURNALS:
                writer.writerow({
                    'journal_abbrev': journal_abbrev,
                    'oldest_PMID': 'N/A',
                    'newest_PMID': 'N/A',
                    'random_PMID': 'N/A',
                    'FindIt_coverage': True,
                })
            else:
                pmids = fetch_pmids_for_journal(journal_abbrev)
                pmids_collected += sum(1 for pmid in pmids.values() if pmid is not None)
                writer.writerow({
                    'journal_abbrev': journal_abbrev,
                    'oldest_PMID': pmids['oldest'] if pmids['oldest'] else 'None',
                    'newest_PMID': pmids['newest'] if pmids['newest'] else 'None',
                    'random_PMID': pmids['random'] if pmids['random'] else 'None',
                    'FindIt_coverage': False
                })

            processed_entries += 1
            if processed_entries % 10 == 0:
                logger.info(f"Entries left to process: {total_entries - processed_entries} out of {total_entries}")
                logger.info(f"PMIDs collected: {pmids_collected}")
                outfile.flush()  # Flush the buffer to the file

        logger.info(f"Processing completed. Total processed entries: {processed_entries}")

create_output_csv(MEDLINE_JOURNAL_LIST, OUTPUT_CSV)

