import requests
from metapub import PubMedFetcher

fetch = PubMedFetcher()

def get_article(pmid):
    art = fetch.article_by_pmid(pmid)
    print(art)

def check_embargo(article_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": article_id,
        "retmode": "json"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "result" in data and article_id in data["result"]:
            article = data["result"][article_id]
            embargo_date = article.get("embargo_date")
            if embargo_date:
                print(f"Article ID: {article_id}, Embargo Date: {embargo_date}")
                return embargo_date
            else:
                print(f"Article ID: {article_id} has no embargo date.")
                return None
        else:
            print(f"Article ID: {article_id} not found in response.")
            return None
    else:
        print(f"Failed to retrieve data for Article ID: {article_id}. Status code: {response.status_code}")
        return None

article_ids = ["30726183", "31537512", "29466254"] 
for article_id in article_ids:
    get_article(article_id)

