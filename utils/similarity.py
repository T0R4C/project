from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(text1, text2):
    """Compute cosine similarity between two texts"""
    if not text1 or not text2:
        return 0.0
    try:
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    except Exception:
        # In case of empty vocabulary or other tfidf errors
        return 0.0

def find_best_match(chunk, source_texts):
    """Find highest similarity score against list of source texts"""
    if not source_texts:
        return 0.0, None
    
    scores = []
    for source in source_texts:
        # Combine title and abstract if available to form the source text
        title = source.get('title', '')
        abstract = source.get('abstract', '') or ''
        combined_text = f"{title} {abstract}"
        
        score = compute_similarity(chunk, combined_text)
        scores.append((score, source))
    
    if not scores:
        return 0.0, None
        
    best_score, best_source = max(scores, key=lambda x: x[0])
    return best_score, best_source
