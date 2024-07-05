import csv
import logging
from metapub import FindIt
from metapub.findit.dances import the_doi_2step

# Define the path to your input CSV file
input_csv_file_path = 'findit_journal_coverage.csv'
# Define the path to your output CSV file
output_csv_file_path = 'findit_noformat.csv'
# Define the path to your log file
log_file_path = 'script.log'

# Set up logging for the entire application
logger = logging.getLogger('metapub')
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Define a function to guess the publisher based on the DOI URL
def guess_publisher(doi_url):
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
    else:
        return "Unknown"

# Open the input CSV file and read its contents
with open(input_csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    # Define the fieldnames for the output CSV file
    fieldnames = ['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year']

    # Open the output CSV file for writing
    with open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Check if FindIt_coverage is False
            if row['FindIt_coverage'] == 'False':
                pmids = [row['oldest_PMID'], row['newest_PMID'], row['random_PMID']]
                for pmid in pmids:
                    # Ensure pmid is not 'N/A'
                    if pmid != 'N/A':
                        try:
                            src = FindIt(pmid, use_crossref=False)
                            logger.info(f"PMID: {src.pmid}, Year: {src.pma.year}, Journal: {src.pma.journal}")
                            logger.info(f"{src.pma.title}")
                            if src.doi:
                                doi_url = ''
                                try:
                                    doi_url = the_doi_2step(src.doi)
                                except Exception as e:
                                    logger.error(f"Error resolving DOI {src.doi} for PMID {pmid}: {e}")

                                # Guess the publisher based on the DOI URL
                                publisher_guess = guess_publisher(doi_url)

                                # Create a row dictionary
                                row_dict = {
                                    'PMID': pmid,
                                    'Journal': row['journal_abbrev'],
                                    'doi': src.doi,
                                    'doi_url': doi_url,
                                    'publisher_guess': publisher_guess,
                                    'year': src.pma.year
                                }

                                # Write the row to the output CSV file
                                writer.writerow(row_dict)
                                outfile.flush()  # Flush after writing each row
                            else:
                                logger.info("No DOI, skipping")
                        except Exception as e:
                            logger.error(f"Error processing PMID {pmid}: {e}")

