import os
import requests
import time
import random
import re
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

def clean_text(text: str) -> str:
    """Clean abstract text from newlines, extra spaces, and json artifacts."""
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_and_store():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials. Exiting.")
        return
        
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Expanded list of 30+ targeted keywords
    keywords = [
        "machine learning", "pendidikan", "sistem informasi", "kesehatan masyarakat",
        "artificial intelligence", "database", "data mining", "jaringan komputer",
        "software engineering", "cyber security", "internet of things", "blockchain",
        "cloud computing", "deep learning", "natural language processing", "computer vision",
        "e-commerce", "digital marketing", "fintech", "ekonomi digital",
        "psikologi sosial", "manajemen bisnis", "akuntansi", "hukum pidana",
        "hukum perdata", "pertanian modern", "teknologi pangan", "teknik sipil",
        "teknik mesin", "energi terbarukan", "perubahan iklim", "ilmu politik",
        "sosiologi", "komunikasi massa", "pendidikan anak usia dini"
    ]
    
    # Process 2 keywords per run to stay within Action limits
    random.shuffle(keywords)
    selected_keywords = keywords[:2]
    
    for keyword in selected_keywords:
        print(f"--- Starting systematic sweep for keyword: '{keyword}' ---")
        current_year, current_offset = get_state(supabase, keyword)
        
        pages_to_fetch = 5 
        page_count = 0
        
        while page_count < pages_to_fetch:
            print(f"Fetching Year: {current_year}, Offset: {current_offset}")
            
            params = {
                'query': keyword,
                'limit': 50,
                'offset': current_offset,
                'year': str(current_year),
                'fields': 'title,abstract,venue,year,authors'
            }
            
            # Retry logic for individual requests
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=20)
                    
                    if response.status_code == 200:
                        data_json = response.json()
                        papers = data_json.get('data', [])
                        total_results = data_json.get('total', 0)
                        
                        if not papers:
                            print(f"No more papers for {current_year}. Moving to {current_year - 1}.")
                            current_year -= 1
                            current_offset = 0
                            update_state(supabase, keyword, current_year, current_offset)
                            if current_year < 1990:
                                print(f"Reached 1990 for {keyword}. Resetting to 2024.")
                                current_year = 2024
                            success = True
                            break # Break retry loop, go to next page
                            
                        inserted_count = 0
                        for paper in papers:
                            abstract_text = clean_text(paper.get('abstract'))
                            if not abstract_text:
                                continue # Skip papers without abstracts
                                
                            authors_list = [a.get('name', '') for a in paper.get('authors', [])]
                            authors_str = ", ".join(authors_list)
                            
                            db_data = {
                                "paper_id": paper.get('paperId'),
                                "title": clean_text(paper.get('title')),
                                "abstract": abstract_text,
                                "venue": clean_text(paper.get('venue')),
                                "year": paper.get('year'),
                                "authors": authors_str
                            }
                            
                            try:
                                res = supabase.table('papers').upsert(db_data, on_conflict='paper_id').execute()
                                inserted_count += 1
                            except Exception as db_err:
                                if "quota" in str(db_err).lower():
                                    print("CRITICAL: Supabase Database quota exceeded (500MB).")
                                    return
                                print(f"DB Insert Error: {db_err}")
                        
                        print(f"Successfully processed {inserted_count} papers with abstracts.")
                        
                        # Increment counters
                        current_offset += 50
                        page_count += 1
                        
                        if current_offset >= 9950 or current_offset >= total_results:
                            print(f"Reached API limit or end of results for year {current_year}. Moving to previous year.")
                            current_year -= 1
                            current_offset = 0
                            if current_year < 1990:
                                current_year = 2024
                                
                        update_state(supabase, keyword, current_year, current_offset)
                        success = True
                        break # Break retry loop on success
                        
                    elif response.status_code == 429:
                        wait_time = 60 * (attempt + 1)
                        print(f"Rate limit exceeded (Attempt {attempt+1}/{max_retries}). Pausing for {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"API Error {response.status_code}: {response.text}")
                        # If severe error, don't retry, just fail this request
                        break
                        
                except Exception as e:
                    print(f"Network error on attempt {attempt+1}: {e}")
                    time.sleep(10)
            
            if not success:
                print(f"Failed to fetch page after {max_retries} retries. Skipping to next keyword.")
                break # Exit the while loop for this keyword, go to next keyword
                
            # Respect API rate limits between successful requests
            time.sleep(5)

if __name__ == "__main__":
    scrape_and_store()
