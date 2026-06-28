import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env variables if running locally
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_db_client():
    """Return Supabase client if configured, else None"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None

def search_paper_in_db(supabase, query_text):
    """
    Search for similar text in Supabase using textSearch (Full Text Search).
    Assumes a table 'papers' with columns: title, abstract, venue, year, authors, paper_id.
    """
    if not supabase:
        return []
        
    try:
        # We process query to remove very short words and keep meaningful tokens
        words = [w for w in query_text.replace("'", "").split() if len(w) > 3]
        if not words:
            return []
            
        search_query = " | ".join(words[:5]) # Take top 5 words to form a tsquery
        
        # Searching against 'abstract' or 'title'
        # Note: Supabase Postgres requires a full-text search index for optimal performance
        response = supabase.table('papers').select('*').text_search('abstract', search_query).limit(3).execute()
        
        # Format to match our app's internal structure
        results = []
        for row in response.data:
            # Reconstruct the authors format
            authors_str = row.get('authors', '')
            authors_list = [{'name': name.strip()} for name in authors_str.split(',') if name.strip()] if authors_str else []
            
            results.append({
                'paperId': row.get('paper_id'),
                'title': row.get('title'),
                'abstract': row.get('abstract'),
                'venue': row.get('venue'),
                'year': row.get('year'),
                'authors': authors_list
            })
            
        return results
    except Exception as e:
        print(f"Error searching Supabase: {e}")
        return []
