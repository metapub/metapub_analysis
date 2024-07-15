import os
import csv

OUTPUT_DIR = 'output'
FIELDNAMES = ['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year']
UNIQUE_FIELD = 'PMID'  # Field to check for duplicates

def check_input_duplicates(input_csv_file_path, unique_field):
    """Check for duplicates in the input CSV file."""
    seen = set()
    duplicates = 0
    with open(input_csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            identifier = row[unique_field]
            if identifier in seen:
                duplicates += 1
            else:
                seen.add(identifier)
    return duplicates

input_csv_file_path = 'findit_journal_coverage.csv'
duplicates_in_input = check_input_duplicates(input_csv_file_path, 'random_PMID')
print(f"Number of duplicate entries in input file: {duplicates_in_input}")


def read_csv_files(output_dir):
    """Read all CSV files in the output directory and return a list of rows."""
    rows = []
    files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    for file in files:
        file_path = os.path.join(output_dir, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
    return rows

def find_duplicates(rows, unique_field):
    """Find duplicates in the list of rows based on the unique field."""
    seen = set()
    duplicates_count = 0
    for row in rows:
        identifier = row[unique_field]
        if identifier in seen:
            duplicates_count += 1
        else:
            seen.add(identifier)
    return duplicates_count

def main():
    # Read all rows from the CSV files
    rows = read_csv_files(OUTPUT_DIR)
    
    # Find duplicates
    duplicates_count = find_duplicates(rows, UNIQUE_FIELD)
    
    print(f"Number of duplicate entries: {duplicates_count}")

if __name__ == "__main__":
    main()

