import csv
import os

INPUT_CSV_FILE_PATH = 'findit_journal_coverage.csv'
OUTPUT_DIR = 'output'
UNIQUE_FIELDS = ['oldest_PMID', 'newest_PMID', 'random_PMID']  # Fields to check for completeness
OUTPUT_UNIQUE_FIELD = 'PMID'  # Field to check in output files

def read_pmids_from_source_csv(file_path, fields):
    """Read PMIDs from the source CSV file and return a set of them."""
    pmids = set()
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for field in fields:
                if row[field] != 'N/A':
                    pmids.add(row[field])
    return pmids

def read_pmids_from_output_files(output_dir, field):
    """Read PMIDs from all CSV files in the output directory and return a set of them."""
    pmids = set()
    files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    for file in files:
        file_path = os.path.join(output_dir, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row[field] != 'N/A':
                    pmids.add(row[field])
    return pmids

def main():
    # Read PMIDs from the source CSV
    source_pmids = read_pmids_from_source_csv(INPUT_CSV_FILE_PATH, UNIQUE_FIELDS)
    
    # Read PMIDs from the output CSV files
    output_pmids = read_pmids_from_output_files(OUTPUT_DIR, OUTPUT_UNIQUE_FIELD)
    
    # Find missing PMIDs
    missing_pmids = source_pmids - output_pmids
    
    if missing_pmids:
        print(f"Number of missing PMIDs: {len(missing_pmids)}")
        for pmid in missing_pmids:
            print(pmid)
    else:
        print("All PMIDs from the source file are present in the output files.")

if __name__ == "__main__":
    main()

