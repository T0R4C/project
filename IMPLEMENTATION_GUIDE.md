# Plagiarism Checker Web App - Implementation Guide
*Agent-friendly documentation for building from scratch to completion*

## Project Overview
Build a web-based plagiarism detection tool for individual student use (~15 users) that checks PDF documents against academic sources (Semantic Scholar, Sinta, Garuda) using TF-IDF cosine similarity. Features include optional bibliography exclusion, similarity reporting, source listing, and text highlighting.

## Technology Stack
- **Backend**: Python 3.9+ with Flask (or FastAPI)
- **PDF Extraction**: PyMuPDF (fitz)
- **NLP/Similarity**: NLTK, scikit-learn (TF-IDF, cosine_similarity)
- **HTTP Client**: requests
- **Frontend**: HTML5, CSS3 (Bootstrap 5), Vanilla JS
- **Deployment**: Render/Railway/Fly.io (free tier)
- **Optional**: Docker, flask-caching

## File Structure
```
plagiarism-checker/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── templates/
│   └── index.html          # Main upload/results page
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # Frontend logic
│
└── utils/
    ├── pdf_extractor.py    # PDF text extraction
    ├── preprocessor.py     # Text cleaning & bibliography removal
    ├── chunker.py          # Sentence tokenization & chunking
    ├── api_client.py       # Semantic Scholar/Garuda/Sinta API wrapper
    ├── similarity.py       # TF-IDF & cosine similarity computation
    └── report_generator.py # Similarity aggregation & result formatting
```

## Setup Instructions
1. Clone repository and navigate to project directory
2. Create virtual environment: `python -m venv venv`
3. Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Run locally: `python app.py` (access at http://localhost:5000)

## Core Dependencies (requirements.txt)
```
Flask==2.3.3
PyMuPDF==1.23.8
nltk==3.8.1
scikit-learn==1.3.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
# Optional for caching:
Flask-Caching==2.0.2
# Optional for production:
gunicorn==21.2.0
```

## Implementation Sequence (Follow Todo Order)
Refer to the SQL `todos` table for exact task tracking. Implement in this order:

1. **Project Setup** (`proj-setup`)
   - Create folder structure above
   - Initialize git repo (optional)
   - Create basic `app.py` with Flask skeleton

2. **PDF Text Extraction** (`pdf-extract`)
   - Implement `utils/pdf_extractor.py`:
     ```python
     import fitz  # PyMuPDF
     
     def extract_text_from_pdf(file_stream):
         """Extract text from PDF file stream"""
         doc = fitz.open(stream=file_stream, filetype="pdf")
         text = ""
         for page in doc:
             text += page.get_text()
         doc.close()
         return text
     ```

3. **Text Preprocessing** (`preprocess`)
   - Implement `utils/preprocessor.py`:
     - Remove headers/footers (repeating text patterns)
     - Remove page numbers
     - Detect and optionally remove bibliography section:
       ```python
       import re
       
       def remove_bibliography(text, exclude_refs=False):
           if not exclude_refs:
               return text
           
           # Patterns for bibliography section (case-insensitive)
           biblio_patterns = [
               r'\n\s*DAFTAR PUSTAKA\s*\n',
               r'\n\s*REFERENCES\s*\n',
               r'\n\s*BIBLIOGRAFI\s*\n',
               r'\n\s*\d+\.\s*[A-Z].*'  # Simple numbered ref pattern
           ]
           
           # Find first occurrence and truncate
           for pattern in biblio_patterns:
               match = re.search(pattern, text, re.IGNORECASE)
               if match:
                   return text[:match.start()]
           return text
       
       def clean_text(text):
           # Remove extra whitespace, normalize
           text = re.sub(r'\s+', ' ', text)
           return text.strip()
     ```

4. **Sentence Tokenization & Chunking** (`chunking`)
   - Implement `utils/chunker.py`:
     ```python
     import nltk
     nltk.download('punkt', quiet=True)
     
     def sentence_tokenize(text):
         return nltk.sent_tokenize(text)
     
     def create_chunks(sentences, chunk_size=4):
         """Group sentences into chunks of chunk_size sentences"""
         chunks = []
         for i in range(0, len(sentences), chunk_size):
             chunk = " ".join(sentences[i:i+chunk_size])
             chunks.append(chunk)
         return chunks
     ```

5. **Academic API Integration** (`api-integr`)
   - Implement `utils/api_client.py`:
     - Semantic Scholar API (free, no key needed for basic usage)
       ```
       GET https://api.semanticscholar.org/graph/v1/paper/search
       Query: ?query=<text_chunk>&limit=3&fields=title,abstract,venue,year
       ```
     - Handle rate limits (100 req/5min for free tier) - implement caching
     - Fallback to other APIs if available (Sinta/Garuda - check their docs)
     - Example function:
       ```python
       import requests
       import time
       
       SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
       
       def search_academic_sources(query, limit=3):
           params = {
               'query': query,
               'limit': limit,
               'fields': 'title,abstract,venue,year,citationCount'
           }
           response = requests.get(SEMANTIC_SCHOLAR_URL, params=params)
           if response.status_code == 200:
               return response.json().get('data', [])
           return []
       ```

6. **Similarity Computation** (`similarity`)
   - Implement `utils/similarity.py`:
     ```python
     from sklearn.feature_extraction.text import TfidfVectorizer
     from sklearn.metrics.pairwise import cosine_similarity
     
     def compute_similarity(text1, text2):
         """Compute cosine similarity between two texts"""
         vectorizer = TfidfVectorizer().fit_transform([text1, text2])
         vectors = vectorizer.toarray()
         return cosine_similarity([vectors[0]], [vectors[1]])[0][0]
     
     def find_best_match(chunk, source_texts):
         """Find highest similarity score against list of source texts"""
         if not source_texts:
             return 0.0, None
         
         scores = []
         for source in source_texts:
             score = compute_similarity(chunk, source['text'])
             scores.append((score, source))
         
         best_score, best_source = max(scores, key=lambda x: x[0])
         return best_score, best_source
     ```

7. **Score Aggregation & Reporting** (`aggregate`)
   - Implement `utils/report_generator.py`:
     ```python
     def aggregate_similarities(chunk_results):
         """
         chunk_results: list of dicts {'chunk': text, 'score': float, 'source': dict}
         Returns: overall_score, matched_sources
         """
         if not chunk_results:
             return 0.0, []
         
         # Method 1: Average of max scores per chunk
         scores = [res['score'] for res in chunk_results]
         overall_score = sum(scores) / len(scores)
         
         # Method 2: Percentage of chunks above threshold (0.7)
         # threshold = 0.7
         # above_threshold = sum(1 for s in scores if s > threshold)
         # overall_score = above_threshold / len(scores)
         
         # Collect unique sources
         sources_seen = set()
         matched_sources = []
         for res in chunk_results:
             source = res['source']
             if source and source.get('paperId') not in sources_seen:
                 sources_seen.add(source.get('paperId'))
                 matched_sources.append({
                     'title': source.get('title', 'Unknown'),
                     'venue': source.get('venue', ''),
                     'year': source.get('year', ''),
                     'similarity': res['score']
                 })
         
         # Sort by similarity descending
         matched_sources.sort(key=lambda x: x['similarity'], reverse=True)
         return min(overall_score * 100, 100.0), matched_sources  # Cap at 100%
     ```

8. **Basic Frontend UI** (`frontend-basic`)
   - Create `templates/index.html` with Bootstrap 5:
     ```html
     <!DOCTYPE html>
     <html lang="id">
     <head>
         <meta charset="UTF-8">
         <meta name="viewport" content="width=device-width, initial-scale=1.0">
         <title>Plagiarism Checker</title>
         <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
         <link href="/static/css/style.css" rel="stylesheet">
     </head>
     <body>
         <div class="container mt-5">
             <h1 class="mb-4">Plagiarism Checker untuk Mahasiswa</h1>
             
             <form id="uploadForm" enctype="multipart/form-data">
                 <div class="mb-3">
                     <label for="pdfFile" class="form-label">Upload Dokumen PDF</label>
                     <input class="form-control" type="file" id="pdfFile" name="pdfFile" accept=".pdf" required>
                 </div>
                 
                 <div class="mb-3 form-check">
                     <input type="checkbox" class="form-check-input" id="excludeRefs">
                     <label class="form-check-label" for="excludeRefs">
                         Eksklisikan kutipan/bibliografi
                     </label>
                 </div>
                 
                 <button type="submit" class="btn btn-primary">Periksa Plagiarisme</button>
             </form>
             
             <div id="results" class="mt-4"></div>
         </div>
         
         <script src="/static/js/main.js"></script>
     </body>
     </html>
     ```

9. **Frontend-Backend Connection** (`frontend-connect`)
   - Create `static/js/main.js`:
     ```javascript
     document.getElementById('uploadForm').addEventListener('submit', async (e) => {
         e.preventDefault();
         
         const formData = new FormData();
         const fileInput = document.getElementById('pdfFile');
         const excludeRefs = document.getElementById('excludeRefs').checked;
         
         if (!fileInput.files[0]) {
             showError('Silakan pilih file PDF');
             return;
         }
         
         formData.append('pdfFile', fileInput.files[0]);
         formData.append('excludeRefs', excludeRefs);
         
         try {
             const response = await fetch('/check', {
                 method: 'POST',
                 body: formData
             });
             
             if (!response.ok) throw new Error('Server error');
             
             const result = await response.json();
             displayResults(result);
         } catch (error) {
             showError('Gagal memproses: ' + error.message);
         }
     });
     
     function displayResults(result) {
         const resultsDiv = document.getElementById('results');
         resultsDiv.innerHTML = '';
         
         if (result.error) {
             showError(result.error);
             return;
         }
         
         // Similarity percentage
         const similarityEl = document.createElement('div');
         similarityEl.className = 'alert alert-info mb-3';
         similarityEl.innerHTML = `<strong>Tingkat Similarity:</strong> ${result.similarity_percentage.toFixed(2)}%`;
         resultsDiv.appendChild(similarityEl);
         
         // Matched sources
         if result.matched_sources.length > 0 {
             const sourcesEl = document.createElement('div');
             sourcesEl.className = 'card mb-3';
             sourcesEl.innerHTML = `
                 <div class="card-header bg-light">
                     <h5>Sumber yang Cocok</h5>
                 </div>
                 <div class="card-body">
                     <ul class="list-group">
                         ${result.matched_sources.map(src => `
                             <li class="list-group-item">
                                 <strong>${src.title}</strong><br>
                                 <small>${src.venue} ${src.year}</small><br>
                                 <small>Similarity: ${(src.similarity*100).toFixed(1)}%</small>
                             </li>
                         `).join('')}
                     </ul>
                 </div>
             `;
             resultsDiv.appendChild(sourcesEl);
         } else {
             resultsDiv.innerHTML += '<div class="alert alert-success">Tidak ditemukan sumber yang cocok signifikan.</div>';
         }
     }
     
     function showError(message) {
         const resultsDiv = document.getElementById('results');
         resultsDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
     }
     ```

10. **Reference Exclusion Option** (`exclude-ref`)
    - Already handled in preprocessing step; frontend sends `excludeRefs` flag via form data
    - In `app.py` route:
      ```python
      @app.route('/check', methods=['POST'])
      def check_plagiarism():
          if 'pdfFile' not in request.files:
              return jsonify({'error': 'No file uploaded'}), 400
          
          file = request.files['pdfFile']
          exclude_refs = request.form.get('excludeRefs') == 'on'
          
          # Process file...
      ```

11. **Text Highlighting** (`highlight`)
    - Enhance `displayResults()` in `main.js` to show original text with highlights
    - Requires backend to return highlighted chunks or positions
    - Alternative: return similarity scores per chunk and highlight in frontend
    - Example approach:
      ```javascript
      // In displayResults, after getting result:
      if result.highlighted_text {
          const highlightedEl = document.createElement('div');
          highlightedEl.className = 'mb-3 p-3 bg-light rounded';
          highlightedEl.innerHTML = `<h6>Teks dengan Penyorotan:</h6><p>${result.highlighted_text}</p>`;
          resultsDiv.appendChild(highlightedEl);
      }
      ```
    - Backend needs to generate HTML with `<mark>` tags for chunks above threshold (e.g., 0.5)

12. **Error Handling & Loading States** (`error-handling`)
    - Add loading spinner during API calls
    - Handle specific errors: API timeouts, rate limits, invalid PDF
    - Example in `main.js`:
      ```javascript
      // Before fetch
      document.getElementById('uploadForm').innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
      
      // In catch/finally
      // Restore form
      ```

13. **Simple Caching** (`caching`)
    - Use `Flask-Caching` or simple dictionary with TTL
    - Cache API responses by query hash:
      ```python
      from flask_caching import Cache
      
      cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
      
      @cache.memoize(timeout=300)  # 5 minutes
      def cached_search(query):
          return search_academic_sources(query)
      ```

14. **Testing** (`testing`)
    - Create test PDFs:
      - Original text (low similarity expected)
      - Plagiarized text from known academic source (high similarity)
      - Text with bibliography (test exclusion option)
    - Verify similarity percentages and source detection

15. **Deployment** (`deploy`)
    - Create `Procfile` for Render/Railway:
      ```
      web: gunicorn app:app
      ```
    - Or Dockerfile:
      ```dockerfile
      FROM python:3.9-slim
      WORKDIR /app
      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt
      COPY . .
      EXPOSE 5000
      CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
      ```
    - Deploy to free tier of Render, Railway, or Fly.io
    - Set environment variables if needed (e.g., API keys for other services)

## API Notes
- **Semantic Scholar**: Free tier allows ~100 requests/5 minutes. Implement caching and consider batching.
- **Sinta/Garuda**: Check if they offer free APIs; if not, focus on Semantic Scholar as primary source.
- **Rate Limit Handling**: 
  - Cache responses for 5-10 minutes
  - Show user-friendly message if limit exceeded
  - Consider implementing exponential backoff

## Preprocessing Details
- **Header/Footer Removal**: Identify repeating text patterns across pages (simple approach: find lines that appear in >50% of pages)
- **Page Number Removal**: Regex for common patterns like `^\s*\d+\s*$`, `^\s*Halaman\s+\d+\s*$`
- **Bibliography Detection**: 
  - Look for section headers: "DAFTAR PUSTAKA", "REFERENCES", "BIBLIOGRAFI"
  - Look for numbered reference patterns: `^\[\d+\]`, `^\d+\.`, etc.
  - Truncate text at first detected bibliography section when exclusion is enabled

## Chunking Strategy
- Use NLTK for sentence tokenization (more accurate than simple split)
- Chunk size: 3-5 sentences (balance context vs. specificity)
- Overlap chunks optionally for better coverage (advanced)

## Similarity Thresholds
- **Chunk level**: Consider chunk as plagiarized if similarity > 0.5-0.6
- **Overall report**: 
  - 0-20%: Likely original
  - 20-40%: Moderate similarity (check sources)
  - 40-60%: High similarity (review needed)
  - >60%: Very high similarity (likely plagiarism)
- These are guidelines; adjust based on testing

## Security & Privacy
- Process PDFs in memory; do not store uploaded files permanently
- Delete extracted text after processing
- Consider adding file size limit (e.g., 10MB)
- Validate file type (check magic bytes, not just extension)

## Extensibility Ideas (Future)
- Support DOCX/TXT uploads
- Allow URL input for online article checking
- User history/login system
- Batch processing for instructors
- Custom corpus upload (for checking against specific references)
- Multi-language support (Indonesian/English)
- Detailed side-by-side comparison view

## Troubleshooting
- **Empty PDF text**: Some PDFs are image-based; MVP assumes text-based PDFs
- **API timeouts**: Increase timeout or implement retry logic
- **Low similarity scores**: May indicate need for better preprocessing or different similarity metric
- **Deployment issues**: Check logs for missing dependencies or port conflicts

---
*This guide provides a complete roadmap for building the plagiarism checker. Follow the todo items in sequence, referring to the relevant sections above for implementation details.*