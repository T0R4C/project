from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def semantic_search(user_text, papers_pool, top_k=10):
    """
    Rank papers_pool based on cosine similarity of their (Title + Abstract) 
    against the user's input text (Semantic Search).
    """
    if not user_text or not papers_pool:
        return []
        
    # Prepare documents
    documents = [user_text]
    for paper in papers_pool:
        title = paper.get('title') or ''
        abstract = paper.get('abstract') or ''
        documents.append(f"{title} {abstract}")
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity between the user_text (index 0) and all papers
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Sort indices by score descending
        related_indices = cosine_similarities.argsort()[::-1]
        
        results = []
        for idx in related_indices:
            score = cosine_similarities[idx]
            if score > 0.05: # Threshold to filter out complete noise
                paper = papers_pool[idx]
                results.append({
                    'paperId': paper.get('paper_id'),
                    'title': paper.get('title'),
                    'abstract': paper.get('abstract'),
                    'venue': paper.get('venue'),
                    'year': paper.get('year'),
                    'authors': paper.get('authors'),
                    'relevance_score': round(float(score) * 100, 1) # Convert to percentage
                })
                
                if len(results) >= top_k:
                    break
                    
        return results
        
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []
