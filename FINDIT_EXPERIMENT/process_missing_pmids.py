import csv
import logging
import os
from logging.handlers import RotatingFileHandler
from metapub import FindIt
from metapub.findit.dances import the_doi_2step

# Define constants
INPUT_FILE = "missing_pmids.txt"
OUTPUT_DIR = 'output'
LOG_DIR = 'logs'
LOG_FILE_PATH = os.path.join(LOG_DIR, 'improve_findit_coverage.log')
MAX_ENTRIES_PER_FILE = 2000

def setup_logging():
    """Set up logging for the entire application."""
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def guess_publisher(doi_url):
    """Guess the publisher based on the DOI URL."""
    if "wiley" in doi_url:
        return "Wiley"
    elif "sciencedirect" in doi_url or "elsevier" in doi_url:
        return "ScienceDirect"
    elif "springer" in doi_url or "link.springer" in doi_url:
        return "Springer"
    elif "tandfonline" in doi_url:
        return "Taylor & Francis"
    elif "sagepub" in doi_url:
        return "SAGE Publications"
    elif "oup" in doi_url or "academic.oup" in doi_url:
        return "Oxford University Press"
    elif "cambridge.org" in doi_url:
        return "Cambridge University Press"
    elif "ieee" in doi_url:
        return "IEEE"
    elif "jstor" in doi_url:
        return "JSTOR"
    elif "ncbi.nlm.nih.gov/pmc" in doi_url or "pubmedcentral" in doi_url:
        return "PubMed Central (PMC)"
    elif "nature.com" in doi_url:
        return "Nature Publishing Group"
    elif "acs.org" in doi_url or "pubs.acs" in doi_url:
        return "American Chemical Society (ACS)"
    elif "biomedcentral" in doi_url:
        return "BioMed Central (BMC)"
    elif "plos" in doi_url:
        return "Public Library of Science (PLOS)"
    elif "karger" in doi_url:
        return "Karger"
    elif "scielo.org" in doi_url:
        return "SciELO"
    elif "doiserbia" in doi_url:
        return "DOISerbia"
    else:
        return "Unknown"

def get_processed_pmids():
    """Get a list of all PMIDs that have already been processed."""
    processed_pmids = set()
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith('findit_noformat_') and filename.endswith('.csv'):
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, mode='r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    processed_pmids.add(row['PMID'])
    return processed_pmids

def process_pmid(pmid, writer):
    """Process a single PMID and write the result to the CSV writer."""
    try:
        src = FindIt(pmid, verify=False, use_crossref=False)
        logging.info(f"PMID: {src.pmid}, Year: {src.pma.year}, Journal: {src.pma.journal}")
        if src.doi:
            doi_url = ''
            try:
                doi_url = the_doi_2step(src.doi)
            except Exception as e:
                logging.error(f"Error resolving DOI {src.doi} for PMID {pmid}: {e}")

            publisher_guess = guess_publisher(doi_url)
            row_dict = {
                'PMID': pmid,
                'Journal': src.pma.journal,
                'doi': src.doi,
                'doi_url': doi_url,
                'publisher_guess': publisher_guess,
                'year': src.pma.year
            }
        else:
            row_dict = {
                'PMID': pmid,
                'Journal': src.pma.journal,
                'doi': '',
                'doi_url': '',
                'publisher_guess': '',
                'year': src.pma.year
            }
            logging.info(f"PMID: {src.pmid} No DOI, skipping.")

        writer.writerow(row_dict)
        return True
    except Exception as e:
        logging.error(f"Error processing PMID {pmid}: {e}")
        return False

def main():
    # Setup
    setup_logging()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_index = 0

    # Determine the next available file index
    while os.path.exists(os.path.join(OUTPUT_DIR, f'findit_noformat_{file_index}.csv')):
        file_index += 1

    # Get the list of already processed PMIDs
    processed_pmids = get_processed_pmids()

    # Open the input text file and read its contents
    with open(INPUT_FILE, mode='r', encoding='utf-8') as infile:
        missing_pmids = infile.read().splitlines()

    # Skip PMIDs that have already been processed
    missing_pmids = [pmid for pmid in missing_pmids if pmid not in processed_pmids]

    rows_written = 0
    output_file_path = os.path.join(OUTPUT_DIR, f'findit_noformat_{file_index}.csv')
    outfile = open(output_file_path, mode='w', newline='', encoding='utf-8')
    writer = csv.DictWriter(outfile, fieldnames=['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year'])
    writer.writeheader()

    for pmid in missing_pmids:
        process_pmid(pmid, writer)
        rows_written += 1

        # Split to a new file if the current file has reached the max entries
        if rows_written >= MAX_ENTRIES_PER_FILE:
            outfile.close()
            file_index += 1
            rows_written = 0
            output_file_path = os.path.join(OUTPUT_DIR, f'findit_noformat_{file_index}.csv')
            outfile = open(output_file_path, mode='w', newline='', encoding='utf-8')
            writer = csv.DictWriter(outfile, fieldnames=['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year'])
            writer.writeheader()

        outfile.flush()

    # Close the final output file
    outfile.close()

    print(f"Processed entries written to {OUTPUT_DIR} directory.")

if __name__ == "__main__":
    main()

