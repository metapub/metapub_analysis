import re
from metapub import FindIt
from metapub.findit.dances import the_doi_2step

def extract_pmids(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to find PMIDs
    pmid_pattern = r'PMID:\s*(\d+)'
    pmids = re.findall(pmid_pattern, content)
    
    return pmids

# Replace 'your_file.txt' with the path to your text file
file_path = 'problem_pmids.txt'
pmid_list = extract_pmids(file_path)

pmids = set(pmid_list)

for pmid in pmids:
    url = None
    src = FindIt(pmid)
    if src.doi:
        url = the_doi_2step(src.doi)

    print(pmid, src.doi, url)
