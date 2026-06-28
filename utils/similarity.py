import re
from rank_bm25 import BM25Okapi

def get_bigrams(text):
    """Generate bi-grams from text for phrase matching."""
    words = text.split()
    return set(zip(words, words[1:]))

def jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return float(intersection) / union if union > 0 else 0.0

def tokenize(text):
    """Simple tokenizer that lowercases and removes punctuation."""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()

def semantic_search(user_text, papers_pool, top_k=10):
    """
    Rank papers_pool using a Hybrid Approach: BM25 + Bi-gram Jaccard.
    BM25 handles robust keyword/context matching.
    Bi-gram Jaccard handles exact phrase overlaps.
    """
    if not user_text or not papers_pool:
        return []
        
    user_tokens = tokenize(user_text)
    user_bigrams = get_bigrams(" ".join(user_tokens))
    
    # Prepare documents for BM25
    corpus_tokens = []
    corpus_texts = []
    
    for paper in papers_pool:
        title = paper.get('title') or ''
        abstract = paper.get('abstract') or ''
        combined = f"{title} {abstract}"
        
        corpus_texts.append(combined)
        corpus_tokens.append(tokenize(combined))
        
    try:
        # 1. Calculate BM25 Scores
        bm25 = BM25Okapi(corpus_tokens)
        bm25_scores = bm25.get_scores(user_tokens)
        
        # Normalize BM25 scores (Min-Max scaling to 0-1 range roughly)
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 and max(bm25_scores) > 0 else 1.0
        normalized_bm25 = [score / max_bm25 for score in bm25_scores]
        
        results = []
        for idx, paper in enumerate(papers_pool):
            # 2. Calculate Bi-gram Jaccard Score
            paper_bigrams = get_bigrams(" ".join(corpus_tokens[idx]))
            jaccard_score = jaccard_similarity(user_bigrams, paper_bigrams)
            
            # 3. Composite Score: 70% BM25 + 30% Jaccard
            composite_score = (0.7 * normalized_bm25[idx]) + (0.3 * jaccard_score)
            
            # Filter out very low relevance (Threshold: 15% composite)
            if composite_score > 0.15:
                results.append({
                    'paperId': paper.get('paper_id'),
                    'title': paper.get('title'),
                    'abstract': paper.get('abstract'),
                    'venue': paper.get('venue'),
                    'year': paper.get('year'),
                    'authors': paper.get('authors'),
                    'relevance_score': round(composite_score * 100, 1) # Convert to percentage
                })
        
        # Sort by relevance descending
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        print(f"Hybrid search error: {e}")
        return []
