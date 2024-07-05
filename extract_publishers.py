import csv
import os

# Define the path to your input CSV file
input_csv_file_path = 'findit_noformat.csv'
# Define the directory to save the text files
output_dir = 'publishers'
# Define the path to your output CSV file for unknown publishers
unknown_csv_file_path = 'unknown_publishers.csv'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize a dictionary to store unique journals by publisher
publishers = {
    'Wiley': set(),
    'ScienceDirect': set(),
    'Springer': set(),
    'Taylor & Francis': set(),
    'SAGE Publications': set(),
    'Oxford University Press': set(),
    'Cambridge University Press': set(),
    'IEEE': set(),
    'JSTOR': set(),
    'PubMed Central (PMC)': set(),
    'Nature Publishing Group': set(),
    'American Chemical Society (ACS)': set(),
    'BioMed Central (BMC)': set(),
    'Public Library of Science (PLOS)': set(),
    'Karger': set()
}

# Open the CSV file for unknown publishers
fieldnames = ['PMID', 'Journal', 'doi', 'doi_url', 'publisher_guess', 'year']
with open(unknown_csv_file_path, 'w', newline='', encoding='utf-8') as unknown_csvfile:
    unknown_writer = csv.DictWriter(unknown_csvfile, fieldnames=fieldnames)
    unknown_writer.writeheader()

    # Read the input CSV file
    with open(input_csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            journal_abbrev = row['Journal']
            publisher_guess = row['publisher_guess']

            if publisher_guess in publishers:
                publishers[publisher_guess].add(journal_abbrev)
            else:
                unknown_writer.writerow(row)

# Write each publisher's journals to a plain text file
for publisher, journals in publishers.items():
    with open(os.path.join(output_dir, f'{publisher}.txt'), 'w', encoding='utf-8') as file:
        for journal in sorted(journals):
            file.write(f'{journal}\n')

print(f"Text files created in {output_dir} directory.")
print(f"Unknown publishers CSV created at {unknown_csv_file_path}.")

