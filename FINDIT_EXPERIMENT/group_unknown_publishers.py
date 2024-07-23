import csv
import re
from collections import defaultdict

# Define the path to your input CSV file
input_csv_file_path = 'unknown_publishers.csv'
# Define the path to your output CSV file
output_csv_file_path = 'unknown_publishers_grouped.csv'

# A function to extract the base URL from the doi_url and drop the "www" prefix if it exists
def extract_base_url(doi_url):
    match = re.search(r'https?://(?:www\.)?([^/]+)', doi_url)
    if match:
        return match.group(1)
    return 'no_pattern'

# Read the input CSV file and group by base URL
url_groups = defaultdict(list)
with open(input_csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        base_url = extract_base_url(row['doi_url'])
        url_groups[base_url].append(row)

# Write the grouped data to separate CSV files
fieldnames = ['PMID', 'Journal', 'publisher_guess', 'year', 'doi', 'doi_url']

for base_url, rows in url_groups.items():
    with open(base_url+".csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print(f"Grouped CSV file created at {base_url}.csv.")

