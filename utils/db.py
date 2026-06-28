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

def get_all_papers(supabase, page=1, limit=20, search_query=""):
    """
    Fetch papers with pagination and optional search.
    """
    if not supabase:
        return {"data": [], "total": 0}
        
    try:
        offset = (page - 1) * limit
        
        query = supabase.table('papers').select('*', count='exact')
        
        if search_query:
            query = query.ilike('title', f'%{search_query}%')
            
        # Order by year descending, then title
        response = query.order('year', desc=True).range(offset, offset + limit - 1).execute()
        
        results = []
        for row in response.data:
            results.append({
                'paperId': row.get('paper_id'),
                'title': row.get('title'),
                'abstract': row.get('abstract'),
                'venue': row.get('venue'),
                'year': row.get('year'),
                'authors': row.get('authors')
            })
            
        return {
            "data": results,
            "total": response.count if response.count is not None else 0
        }
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return {"data": [], "total": 0}
