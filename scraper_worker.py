import os
import requests
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def get_state(supabase: Client, keyword: str):
    """Fetch the current scraping state for a keyword."""
    try:
        res = supabase.table('scrape_state').select('*').eq('keyword', keyword).execute()
        if res.data:
            return res.data[0]['current_year'], res.data[0]['current_offset']
    except Exception as e:
        print(f"Error fetching state for {keyword}: {e}")
    # Default starting point: year 2024, offset 0
    return 2024, 0

def update_state(supabase: Client, keyword: str, year: int, offset: int):
    """Save the current scraping state."""
    data = {
        "keyword": keyword,
        "current_year": year,
        "current_offset": offset
    }
    try:
        supabase.table('scrape_state').upsert(data, on_conflict='keyword').execute()
    except Exception as e:
        print(f"Error saving state for {keyword}: {e}")

def scrape_and_store():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials. Exiting.")
        return
        
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # List of targeted keywords to sweep systematically
    keywords = [
        "machine learning", "pendidikan", "sistem informasi", 
        "kesehatan masyarakat", "artificial intelligence", 
        "database", "data mining", "jaringan komputer"
    ]
    
    # We will process 2 keywords per run to stay within 30 min action limits
    import random
    random.shuffle(keywords)
    selected_keywords = keywords[:2]
    
    for keyword in selected_keywords:
        print(f"--- Starting systematic sweep for keyword: '{keyword}' ---")
        current_year, current_offset = get_state(supabase, keyword)
        
        # We will do 5 pagination requests (5 * 50 = 250 papers) per keyword per run
        pages_to_fetch = 5 
        
        for _ in range(pages_to_fetch):
            print(f"Fetching Year: {current_year}, Offset: {current_offset}")
            
            params = {
                'query': keyword,
                'limit': 50,
                'offset': current_offset,
                'year': str(current_year),
                'fields': 'title,abstract,venue,year,authors'
            }
            
            try:
                response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=15)
                if response.status_code == 200:
                    data_json = response.json()
                    papers = data_json.get('data', [])
                    total_results = data_json.get('total', 0)
                    
                    if not papers:
                        # No more papers for this year, move to previous year
                        print(f"No more papers for {current_year}. Moving to {current_year - 1}.")
                        current_year -= 1
                        current_offset = 0
                        update_state(supabase, keyword, current_year, current_offset)
                        
                        # Stop if we went too far back (e.g. before 1990)
                        if current_year < 1990:
                            print(f"Reached 1990 for {keyword}. Resetting to 2024.")
                            current_year = 2024
                        continue
                        
                    inserted_count = 0
                    for paper in papers:
                        if not paper.get('abstract'):
                            continue # Skip papers without abstracts
                            
                        authors_list = [a.get('name', '') for a in paper.get('authors', [])]
                        authors_str = ", ".join(authors_list)
                        
                        db_data = {
                            "paper_id": paper.get('paperId'),
                            "title": paper.get('title'),
                            "abstract": paper.get('abstract'),
                            "venue": paper.get('venue'),
                            "year": paper.get('year'),
                            "authors": authors_str
                        }
                        
                        try:
                            # Upsert prevents duplicates
                            res = supabase.table('papers').upsert(db_data, on_conflict='paper_id').execute()
                            inserted_count += 1
                        except Exception as db_err:
                            if "quota" in str(db_err).lower():
                                print("CRITICAL: Supabase Database quota exceeded (500MB).")
                                return # Stop the whole worker
                            print(f"DB Insert Error: {db_err}")
                    
                    print(f"Successfully processed {inserted_count} papers with abstracts.")
                    
                    # Update offset for next page
                    current_offset += 50
                    
                    # If we reached Semantic Scholar's hard limit (9999) or processed all results for this year
                    if current_offset >= 9950 or current_offset >= total_results:
                        print(f"Reached API limit or end of results for year {current_year}. Moving to previous year.")
                        current_year -= 1
                        current_offset = 0
                        if current_year < 1990:
                            current_year = 2024
                            
                    update_state(supabase, keyword, current_year, current_offset)
                    
                elif response.status_code == 429:
                    print("Rate limit exceeded. Pausing for 60 seconds...")
                    time.sleep(60)
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    break # Skip to next keyword on severe error
                    
            except Exception as e:
                print(f"Network error: {e}")
                
            # Respect API rate limits (100/5mins)
            time.sleep(5)

if __name__ == "__main__":
    scrape_and_store()
