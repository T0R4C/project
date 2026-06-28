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

def get_db_stats(supabase):
    """Return aggregate statistics about the papers database."""
    if not supabase:
        return {"total_papers": 0, "latest_year": None, "oldest_year": None}
    try:
        # Total count
        count_res = supabase.table('papers').select('*', count='exact').limit(1).execute()
        total = count_res.count or 0

        # Latest and oldest year
        latest_res = supabase.table('papers').select('year').order('year', desc=True).limit(1).execute()
        oldest_res = supabase.table('papers').select('year').order('year', desc=False).limit(1).execute()

        latest_year = latest_res.data[0]['year'] if latest_res.data else None
        oldest_year = oldest_res.data[0]['year'] if oldest_res.data else None

        return {
            "total_papers": total,
            "latest_year": latest_year,
            "oldest_year": oldest_year
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {"total_papers": 0, "latest_year": None, "oldest_year": None}

def get_paper_by_id(supabase, paper_id):
    """Fetch a single paper by its paper_id."""
    if not supabase:
        return None
    try:
        res = supabase.table('papers').select('*').eq('paper_id', paper_id).limit(1).execute()
        if res.data:
            row = res.data[0]
            return {
                'paperId': row.get('paper_id'),
                'title': row.get('title'),
                'abstract': row.get('abstract'),
                'venue': row.get('venue'),
                'year': row.get('year'),
                'authors': row.get('authors'),
            }
        return None
    except Exception as e:
        print(f"Error fetching paper {paper_id}: {e}")
        return None

def search_paper_in_db(supabase, query_text):
    """
    Search for similar text in Supabase using textSearch (Full Text Search).
    """
    if not supabase:
        return []

    try:
        words = [w for w in query_text.replace("'", "").split() if len(w) > 3]
        if not words:
            return []

        search_query = " | ".join(words[:5])
        response = supabase.table('papers').select('*').limit(3).text_search('abstract', search_query).execute()

        results = []
        for row in response.data:
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

def get_all_papers(supabase, page=1, limit=20, search_query="", year_from=None, year_to=None):
    """
    Fetch papers with pagination, optional search and year filtering.
    """
    if not supabase:
        return {"data": [], "total": 0}

    try:
        offset = (page - 1) * limit
        query = supabase.table('papers').select('*', count='exact')

        if search_query:
            query = query.ilike('title', f'%{search_query}%')
        if year_from:
            query = query.gte('year', year_from)
        if year_to:
            query = query.lte('year', year_to)

        response = query.order('year', desc=True).range(offset, offset + limit - 1).execute()

        results = []
        for row in response.data:
            results.append({
                'paper_id': row.get('paper_id'),
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

def fetch_pool_for_semantic_search(supabase, limit=2000, year_from=None, year_to=None):
    """
    Fetch a pool of papers from Supabase for semantic ranking.
    Supports optional year range filtering.
    """
    if not supabase:
        return []
    try:
        query = supabase.table('papers').select('paper_id, title, abstract, venue, year, authors')
        if year_from:
            query = query.gte('year', year_from)
        if year_to:
            query = query.lte('year', year_to)
        response = query.order('year', desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching pool: {e}")
        return []
