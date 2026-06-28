import os
from flask import Flask, request, jsonify, render_template
from flask_caching import Cache

from utils.db import get_db_client, get_all_papers, fetch_pool_for_semantic_search
from utils.similarity import semantic_search

app = Flask(__name__)
# Configure cache (SimpleCache for MVP)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

# Initialize Supabase globally
supabase = get_db_client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database')
def database_explorer():
    return render_template('database.html')

@app.route('/api/papers')
def api_get_papers():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search_query = request.args.get('search', '', type=str)
    
    result = get_all_papers(supabase, page, limit, search_query)
    return jsonify({
        'success': True,
        'page': page,
        'limit': limit,
        'total': result['total'],
        'data': result['data']
    })

@app.route('/recommend', methods=['POST'])
def recommend_papers():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided. Please input your research topic or abstract.'}), 400
        
    user_text = data['text'].strip()
    if len(user_text) < 10:
        return jsonify({'error': 'Text is too short. Please provide more details about your research.'}), 400
        
    try:
        # 1. Fetch a pool of candidates from Supabase (e.g., top 1000 latest papers)
        papers_pool = fetch_pool_for_semantic_search(supabase, limit=1000)
        
        if not papers_pool:
            return jsonify({'error': 'Database is empty. Please wait for the scraper to gather data.'}), 500
            
        # 2. Perform Semantic Search using TF-IDF & Cosine Similarity
        # This will rank the papers pool based on relevance to the user's text
        top_matches = semantic_search(user_text, papers_pool, top_k=10)
        
        return jsonify({
            'success': True,
            'query_length': len(user_text),
            'pool_size': len(papers_pool),
            'results': top_matches
        })
        
    except Exception as e:
        print(f"Error processing recommendation: {e}")
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
