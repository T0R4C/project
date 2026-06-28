import requests
import time
from utils.db import get_db_client, search_paper_in_db

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# Initialize Supabase client globally
supabase = get_db_client()

def search_academic_sources(query, limit=3):
    # 1. First, check our own Supabase Database
    if supabase:
        db_results = search_paper_in_db(supabase, query)
        if db_results and len(db_results) > 0:
            print("Found match in local Supabase DB!")
            return db_results

    # 2. If not found in DB or DB not configured, fallback to API
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,abstract,venue,year,citationCount,authors'
    }
    
    # Jeda dasar 3 detik antar permintaan untuk menjaga rate limit aman (100 req / 5 menit)
    time.sleep(3)
    
    max_retries = 3
    base_wait = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get('data', [])
                
                # We could potentially insert this new data back into Supabase here to grow the cache dynamically
                # (Omitted for brevity, handled by scraper worker)
                
                return data
            elif response.status_code == 429:
                print(f"Rate limit exceeded (Attempt {attempt+1}/{max_retries}). Waiting {base_wait} seconds...")
                time.sleep(base_wait)
                base_wait *= 2  # Exponential backoff
            else:
                print(f"API returned status: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error querying Semantic Scholar: {e}")
            if attempt == max_retries - 1:
                return []
            time.sleep(base_wait)
            base_wait *= 2
            
    return []
