import csv
import os

OUTPUT_DIR = 'output'
COMBINED_FILE_PATH = 'COMBINED.csv'
FIELDNAMES = ['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year']  # Fields to write in the combined CSV

def read_and_combine_csv_files(output_dir, fieldnames):
    """Read all CSV files in the output directory and combine them, removing duplicates."""
    combined_rows = []
    seen = set()
    files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    for file in files:
        file_path = os.path.join(output_dir, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                identifier = row['PMID']
                if identifier not in seen:
                    seen.add(identifier)
                    combined_rows.append(row)
    return combined_rows

def write_combined_csv(file_path, rows, fieldnames):
    """Write the combined rows to a new CSV file."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    # Read and combine rows from the output CSV files
    combined_rows = read_and_combine_csv_files(OUTPUT_DIR, FIELDNAMES)
    
    # Write the combined rows to the new CSV file
    write_combined_csv(COMBINED_FILE_PATH, combined_rows, FIELDNAMES)
    
    print(f"Combined CSV file created at {COMBINED_FILE_PATH} with {len(combined_rows)} unique entries.")

if __name__ == "__main__":
    main()

