from metapub import PubMedFetcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_publication_years(journal):
    fetch = PubMedFetcher()
    query = f"{journal}[Journal]"
    pmids = fetch.pmids_for_query(query, retmax=9999)

    if not pmids:
        return None, None

    oldest_year = None
    recent_year = None

    if len(pmids) == 9999:
        # Perform decade-wise search to find the oldest year
        for decade_start in range(1900, 2020, 10):
            query = f"{journal}[Journal] AND {decade_start}:{decade_start + 9}[PDAT]"
            decade_pmids = fetch.pmids_for_query(query, retmax=9999)
            if decade_pmids:
                oldest_pmid = min(decade_pmids)
                oldest_year = fetch.article_by_pmid(oldest_pmid).year
                break
    else:
        oldest_pmid = min(pmids)
        oldest_year = fetch.article_by_pmid(oldest_pmid).year

    # Find the most recent year
    recent_pmid = max(pmids)
    recent_year = fetch.article_by_pmid(recent_pmid).year

    return oldest_year, recent_year

def check_downloadable(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        if "application/pdf" in driver.execute_script("return document.contentType"):
            response_code = 200
        else:
            response_code = 402  # Not a PDF
    except Exception as e:
        response_code = 400  # Use a different code if an error occurs
    finally:
        driver.quit()
    
    return response_code

