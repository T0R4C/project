import os
import requests
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def scrape_and_store():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials. Exiting.")
        return
        
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # List of keywords to loop through (can be expanded)
    keywords = ["machine learning", "pendidikan", "sistem informasi", "kesehatan masyarakat", "artificial intelligence", "database"]
    
    for keyword in keywords:
        print(f"Scraping for keyword: {keyword}")
        params = {
            'query': keyword,
            'limit': 50,  # Fetch 50 at a time
            'fields': 'title,abstract,venue,year,authors'
        }
        
        try:
            response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=15)
            if response.status_code == 200:
                papers = response.json().get('data', [])
                
                for paper in papers:
                    if not paper.get('abstract'):
                        continue # Skip papers without abstracts
                        
                    authors_list = [a.get('name', '') for a in paper.get('authors', [])]
                    authors_str = ", ".join(authors_list)
                    
                    data = {
                        "paper_id": paper.get('paperId'),
                        "title": paper.get('title'),
                        "abstract": paper.get('abstract'),
                        "venue": paper.get('venue'),
                        "year": paper.get('year'),
                        "authors": authors_str
                    }
                    
                    # Upsert to prevent duplicates
                    try:
                        supabase.table('papers').upsert(data, on_conflict='paper_id').execute()
                    except Exception as db_err:
                        print(f"DB Insert Error: {db_err}")
                
                print(f"Successfully processed {len(papers)} papers for '{keyword}'")
            else:
                print(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Network error: {e}")
            
        # Respect API rate limits (100/5mins)
        # We wait 5 seconds between each keyword batch
        time.sleep(5)

if __name__ == "__main__":
    scrape_and_store()
