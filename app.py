import os
import hashlib
from flask import Flask, request, jsonify, render_template
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.db import get_db_client, get_all_papers, fetch_pool_for_semantic_search, get_db_stats, get_paper_by_id
from utils.similarity import semantic_search

app = Flask(__name__)

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Cache
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

# Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://"
)

# Initialize Supabase globally
supabase = get_db_client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database')
def database_explorer():
    return render_template('database.html')

@app.route('/paper/<paper_id>')
def paper_detail(paper_id):
    return render_template('paper_detail.html', paper_id=paper_id)

# ─── API: Stats ─────────────────────────────────────────────────────────────
@app.route('/api/stats')
@cache.cached(timeout=120, key_prefix='db_stats')
def api_stats():
    stats = get_db_stats(supabase)
    return jsonify({'success': True, **stats})

# ─── API: All Papers (Database Explorer) ────────────────────────────────────
@app.route('/api/papers')
def api_get_papers():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search_query = request.args.get('search', '', type=str)
    year_from = request.args.get('year_from', None, type=int)
    year_to = request.args.get('year_to', None, type=int)

    result = get_all_papers(supabase, page, limit, search_query, year_from, year_to)
    return jsonify({
        'success': True,
        'page': page,
        'limit': limit,
        'total': result['total'],
        'data': result['data']
    })

# ─── API: Single Paper ───────────────────────────────────────────────────────
@app.route('/api/paper/<paper_id>')
@cache.cached(timeout=600, key_prefix=lambda: f'paper_{request.view_args["paper_id"]}')
def api_get_paper(paper_id):
    paper = get_paper_by_id(supabase, paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    return jsonify({'success': True, 'data': paper})

# ─── API: Semantic Recommend ─────────────────────────────────────────────────
@app.route('/recommend', methods=['POST'])
@limiter.limit("10 per minute")
def recommend_papers():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided. Please input your research topic or abstract.'}), 400

    user_text = data['text'].strip()
    year_from = data.get('year_from', None)
    year_to = data.get('year_to', None)

    if len(user_text) < 10:
        return jsonify({'error': 'Text is too short. Please provide more details about your research.'}), 400

    # Use cache based on query hash + year filters
    cache_key = hashlib.md5(f"{user_text}_{year_from}_{year_to}".encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        return jsonify({'success': True, 'cached': True, **cached})

    try:
        papers_pool = fetch_pool_for_semantic_search(supabase, limit=2000, year_from=year_from, year_to=year_to)

        if not papers_pool:
            return jsonify({'error': 'Database is empty. Please wait for the scraper to gather data.'}), 500

        top_matches = semantic_search(user_text, papers_pool, top_k=10)

        result_data = {
            'query_length': len(user_text),
            'pool_size': len(papers_pool),
            'results': top_matches
        }
        cache.set(cache_key, result_data, timeout=300)

        return jsonify({'success': True, 'cached': False, **result_data})

    except Exception as e:
        print(f"Error processing recommendation: {e}")
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
