import requests
import time
import logging
import os
from datetime import datetime

# Set up logging
logging.basicConfig(filename='ncbi_api_test.log', level=logging.INFO, format='%(asctime)s %(message)s')

def test_ncbi_eutils():
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    params = {
        'db': 'pubmed',
        'id': '12345678',  # Example PMID, replace with a valid one if needed
        'retmode': 'xml'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logging.info('NCBI E-utilities API is working fine.')
            return True
        else:
            logging.error(f'Error: Received status code {response.status_code}')
            logging.error(f'Response content: {response.text}')
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f'Error making request to NCBI E-utilities API: {e}')
        return False

if __name__ == '__main__':
    while True:
        logging.info('Testing NCBI E-utilities API...')
        if test_ncbi_eutils():
            # Play sound when the API stops returning 500 errors
            os.system('echo -e "\a"')
            break
        time.sleep(15)  # Wait for 15 seconds before trying again

