"""
Scholar AI — Hybrid Semantic Similarity Engine
Combines BM25Okapi + Bi-gram Jaccard for high-precision academic search.
"""

import re
from rank_bm25 import BM25Okapi

# ── Stop words (Bahasa Indonesia + English) ───────────────────
STOP_WORDS = {
    # English
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","has","have","had",
    "do","does","did","will","would","could","should","may","might","can",
    "this","that","these","those","it","its","they","them","their",
    "which","who","what","how","when","where","why",
    # Indonesian
    "yang","dan","di","ke","dari","dengan","untuk","ini","itu","pada",
    "adalah","akan","dalam","oleh","tidak","juga","telah","dapat",
    "serta","atau","sebagai","bahwa","ada","karena","maka","dengan",
    "lebih","seperti","antara","terhadap","tentang","setelah","selama",
    "hasil","penelitian","metode","data","sistem","penggunaan","pengembangan"
}


def tokenize(text: str) -> list[str]:
    """Lowercase, remove punctuation, filter stop words and very short tokens."""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", " ", text)
    tokens = [t for t in text.split() if len(t) > 2 and t not in STOP_WORDS]
    return tokens


def get_ngrams(tokens: list[str], n: int = 2) -> set:
    """Generate n-grams from token list."""
    return set(zip(*[tokens[i:] for i in range(n)]))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union > 0 else 0.0


def normalize(scores: list[float]) -> list[float]:
    """Min-Max normalize a list of scores to [0, 1]."""
    mn, mx = min(scores), max(scores)
    if mx == mn:
        return [1.0 if s > 0 else 0.0 for s in scores]
    return [(s - mn) / (mx - mn) for s in scores]


def semantic_search(user_text: str, papers_pool: list, top_k: int = 10) -> list:
    """
    Hybrid BM25 + Bi-gram Jaccard search.

    Scoring formula:
      composite = 0.65 * BM25_norm + 0.25 * Jaccard_bigram + 0.10 * Jaccard_trigram

    All scores are normalized to [0,1] before blending.
    Only results above 15% composite are returned.
    Results are capped at top_k.
    """
    if not user_text or not papers_pool:
        return []

    # Tokenize query
    q_tokens  = tokenize(user_text)
    q_bigrams  = get_ngrams(q_tokens, 2)
    q_trigrams = get_ngrams(q_tokens, 3)

    if not q_tokens:
        return []

    # Build corpus
    corpus_tokens = []
    corpus_bigrams  = []
    corpus_trigrams = []

    for paper in papers_pool:
        title    = paper.get("title") or ""
        abstract = paper.get("abstract") or ""
        # Weight title slightly more by repeating it
        combined = f"{title} {title} {abstract}"
        toks = tokenize(combined)
        corpus_tokens.append(toks)
        corpus_bigrams.append(get_ngrams(toks, 2))
        corpus_trigrams.append(get_ngrams(toks, 3))

    try:
        # BM25 scores
        bm25 = BM25Okapi(corpus_tokens)
        raw_bm25 = list(bm25.get_scores(q_tokens))

        # Normalize BM25
        norm_bm25 = normalize(raw_bm25) if max(raw_bm25) > 0 else [0.0] * len(raw_bm25)

        results = []
        for idx, paper in enumerate(papers_pool):
            jac2 = jaccard(q_bigrams, corpus_bigrams[idx])
            jac3 = jaccard(q_trigrams, corpus_trigrams[idx])

            composite = (
                0.65 * norm_bm25[idx] +
                0.25 * jac2 +
                0.10 * jac3
            )

            if composite > 0.15:
                results.append({
                    "paperId":         paper.get("paper_id"),
                    "title":           paper.get("title"),
                    "abstract":        paper.get("abstract"),
                    "venue":           paper.get("venue"),
                    "year":            paper.get("year"),
                    "authors":         paper.get("authors"),
                    "relevance_score": round(composite * 100, 1),
                    "_bm25":           round(norm_bm25[idx] * 100, 1),
                    "_jaccard2":       round(jac2 * 100, 1),
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    except Exception as e:
        print(f"[similarity] Hybrid search error: {e}")
        return []
