import os
import hashlib
from flask import Flask, request, jsonify, render_template
from flask_caching import Cache

from utils.pdf_extractor import extract_text_from_pdf
from utils.preprocessor import remove_bibliography, clean_text
from utils.chunker import sentence_tokenize, create_chunks
from utils.api_client import search_academic_sources
from utils.similarity import find_best_match
from utils.report_generator import aggregate_similarities

app = Flask(__name__)
# Configure cache (SimpleCache for MVP)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

@cache.memoize(timeout=300)
def cached_search(query):
    return search_academic_sources(query)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_plagiarism():
    if 'pdfFile' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['pdfFile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.lower().endswith('.pdf'):
         return jsonify({'error': 'Invalid file format. Please upload a PDF file.'}), 400
         
    exclude_refs = request.form.get('excludeRefs') == 'true'
    
    try:
        # 1. Extract text from PDF
        file_bytes = file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        
        if not raw_text.strip():
            return jsonify({'error': 'Could not extract text from PDF. Ensure the PDF is not an image.'}), 400
            
        # 2. Preprocess text (Remove bibliography if requested)
        text_no_refs = remove_bibliography(raw_text, exclude_refs)
        cleaned_text = clean_text(text_no_refs)
        
        # 3. Tokenization & Chunking
        sentences = sentence_tokenize(cleaned_text)
        chunks = create_chunks(sentences, chunk_size=3) # Size 3 sentences
        
        if not chunks:
            return jsonify({'error': 'Not enough text content to analyze.'}), 400
            
        # Limit chunks to avoid too many API calls for MVP
        MAX_CHUNKS = 50
        if len(chunks) > MAX_CHUNKS:
            chunks = chunks[:MAX_CHUNKS]
            
        # 4 & 5. API Search & Similarity Match per chunk
        chunk_results = []
        high_similarity_chunks_count = 0
        
        for chunk in chunks:
            if len(chunk.strip()) < 10:
                continue # Skip very short chunks
                
            sources = cached_search(chunk)
            score, best_source = find_best_match(chunk, sources)
            
            res = {
                'chunk': chunk,
                'score': float(score),
                'source': best_source
            }
            chunk_results.append(res)
            
            if score > 0.5:
                high_similarity_chunks_count += 1
                
        # 6. Aggregate Scores
        overall_score, matched_sources = aggregate_similarities(chunk_results)
        
        # Format response
        return jsonify({
            'similarity_percentage': overall_score,
            'matched_sources': matched_sources,
            'processed_chunks': len(chunk_results),
            'high_similarity_chunks': high_similarity_chunks_count,
            'excluded_bibliography': exclude_refs
        })
        
    except Exception as e:
        print(f"Error processing: {e}")
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
