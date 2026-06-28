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
    
    # Collect unique sources
    sources_seen = set()
    matched_sources = []
    for res in chunk_results:
        source = res.get('source')
        if source and source.get('paperId') not in sources_seen:
            sources_seen.add(source.get('paperId'))
            authors = [a.get('name', '') for a in source.get('authors', [])]
            author_str = ", ".join(authors) if authors else "Unknown Authors"
            
            matched_sources.append({
                'title': source.get('title', 'Unknown'),
                'authors': author_str,
                'venue': source.get('venue', ''),
                'year': source.get('year', ''),
                'similarity': res['score']
            })
    
    # Sort by similarity descending
    matched_sources.sort(key=lambda x: x['similarity'], reverse=True)
    return min(overall_score * 100, 100.0), matched_sources  # Cap at 100%
