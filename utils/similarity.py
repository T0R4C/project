"""
Scholar AI — Dual-Index Field-Aware Semantic Ranking Engine v4.0

Architecture:
  1. Dual BM25 Index     → Separate BM25 for titles (k1=2.0, b=0.3) and
                           abstracts (k1=1.5, b=0.75) with independent scoring
  2. Exact Phrase Match  → Bonus for papers containing the user's exact query
                           substring in title or abstract
  3. Keyword Density     → Measures how many unique query terms appear in
                           a paper, weighted by their frequency
  4. N-gram Overlap      → Bigram + Trigram Jaccard for phrase-level context
  5. Percentile Norm     → Scores are ranked by percentile instead of min-max,
                           so the top result is NOT always 100%

Weights:
  final = 0.35 * title_bm25
        + 0.25 * abstract_bm25
        + 0.15 * exact_phrase_bonus
        + 0.12 * keyword_density
        + 0.08 * jaccard_bigram
        + 0.05 * jaccard_trigram
"""

import re
import math
from rank_bm25 import BM25Okapi


# ═══════════════════════════════════════════════════════════════
#  STOP WORDS (bilingual, kept minimal to avoid over-filtering)
# ═══════════════════════════════════════════════════════════════
STOP_WORDS = frozenset({
    # English function words only — preserve all domain terms
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "not", "no", "nor",
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "he", "she", "his", "her", "we", "our", "you", "your",
    "which", "who", "what", "how", "when", "where", "why",
    "so", "if", "then", "than", "as", "such", "also", "very",
    "each", "every", "both", "all", "any", "few", "more", "most",
    "other", "some", "only", "own", "same", "too",
    # Indonesian function words only
    "yang", "dan", "di", "ke", "dari", "dengan", "untuk", "ini", "itu",
    "pada", "adalah", "akan", "dalam", "oleh", "tidak", "juga", "telah",
    "dapat", "serta", "atau", "sebagai", "bahwa", "ada", "karena", "maka",
    "lebih", "seperti", "antara", "terhadap", "tentang", "setelah",
    "selama", "secara", "sudah", "masih", "harus", "bisa",
    "kami", "kita", "mereka", "anda", "saya",
})


# ═══════════════════════════════════════════════════════════════
#  TOKENIZER
# ═══════════════════════════════════════════════════════════════
def tokenize(text: str) -> list[str]:
    """
    Lowercase, remove punctuation (but KEEP digits for terms like 'COVID-19',
    'GPT-4', 'IoT'), filter stop words and tokens with len <= 1.
    """
    if not text:
        return []
    text = text.lower()
    # Replace punctuation with spaces but keep alphanumeric
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return [t for t in text.split() if len(t) > 1 and t not in STOP_WORDS]


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for substring matching."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


# ═══════════════════════════════════════════════════════════════
#  N-GRAM HELPERS
# ═══════════════════════════════════════════════════════════════
def get_ngrams(tokens: list[str], n: int) -> set:
    if len(tokens) < n:
        return set()
    return set(zip(*[tokens[i:] for i in range(n)]))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ═══════════════════════════════════════════════════════════════
#  NORMALIZATION (Percentile-based, NOT min-max)
# ═══════════════════════════════════════════════════════════════
def percentile_normalize(scores: list[float]) -> list[float]:
    """
    Rank-based normalization. Each score is replaced by its percentile
    rank within the list. This avoids the "always 100%" problem of min-max.
    The top result will only be 100% if it truly dominates all others.
    """
    n = len(scores)
    if n == 0:
        return []
    if n == 1:
        return [0.85 if scores[0] > 0 else 0.0]

    # Create (score, original_index) pairs and sort by score
    indexed = sorted(enumerate(scores), key=lambda x: x[1])
    ranks = [0.0] * n

    for rank_pos, (orig_idx, score) in enumerate(indexed):
        if score <= 0:
            ranks[orig_idx] = 0.0
        else:
            # Percentile = position / (n-1), scaled to [0, 0.95]
            # We cap at 0.95 so 100% is rare (only with exact_phrase bonuses)
            ranks[orig_idx] = (rank_pos / (n - 1)) * 0.95

    return ranks


def soft_normalize(scores: list[float]) -> list[float]:
    """
    Sigmoid-based soft normalization for BM25 scores.
    Maps raw scores to [0, 1] using sigmoid around the median.
    Much better than min-max for skewed distributions.
    """
    n = len(scores)
    if n == 0:
        return []

    # Filter out zeros to find meaningful median
    nonzero = [s for s in scores if s > 0]
    if not nonzero:
        return [0.0] * n

    median = sorted(nonzero)[len(nonzero) // 2]
    # Steepness factor
    k = 4.0 / (median + 1e-9)

    result = []
    for s in scores:
        if s <= 0:
            result.append(0.0)
        else:
            # Sigmoid centered at median
            sig = 1.0 / (1.0 + math.exp(-k * (s - median)))
            result.append(sig)
    return result


# ═══════════════════════════════════════════════════════════════
#  EXACT PHRASE MATCH
# ═══════════════════════════════════════════════════════════════
def exact_phrase_score(query_norm: str, title_norm: str, abstract_norm: str) -> float:
    """
    Check if the user's query (or significant substrings of it) appear
    as exact substrings in the title or abstract.

    Returns 0.0 to 1.0:
      - 1.0 if full query found in title
      - 0.8 if full query found in abstract
      - 0.3-0.6 for partial matches (3+ word windows)
    """
    if not query_norm:
        return 0.0

    score = 0.0

    # Full query match
    if query_norm in title_norm:
        score = max(score, 1.0)
    elif query_norm in abstract_norm:
        score = max(score, 0.8)

    # Sliding window: check 3-word and 4-word windows of the query
    words = query_norm.split()
    if len(words) >= 3:
        for window_size in [4, 3]:
            if len(words) < window_size:
                continue
            matches = 0
            total_windows = len(words) - window_size + 1
            for i in range(total_windows):
                phrase = " ".join(words[i:i + window_size])
                if phrase in title_norm:
                    matches += 2  # Title match worth double
                elif phrase in abstract_norm:
                    matches += 1
            if total_windows > 0:
                window_score = min(1.0, matches / total_windows) * (0.6 if window_size == 4 else 0.4)
                score = max(score, window_score)

    return score


# ═══════════════════════════════════════════════════════════════
#  KEYWORD DENSITY
# ═══════════════════════════════════════════════════════════════
def keyword_density(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """
    Measures what fraction of unique query terms actually appear in
    the document, weighted by how often they appear.

    Coverage + Density combined metric.
    """
    if not query_tokens or not doc_tokens:
        return 0.0

    unique_query = set(query_tokens)
    doc_set = set(doc_tokens)

    # Coverage: how many query terms are present
    present = unique_query & doc_set
    coverage = len(present) / len(unique_query)

    # Frequency: average count of present query terms in doc
    if not present:
        return 0.0

    doc_freq = {}
    for t in doc_tokens:
        doc_freq[t] = doc_freq.get(t, 0) + 1

    total_freq = sum(doc_freq.get(t, 0) for t in present)
    avg_freq = total_freq / len(present)

    # Logarithmic density (diminishing returns for high frequency)
    density = math.log(1 + avg_freq) / math.log(1 + len(doc_tokens))

    # Combine: coverage is more important
    return 0.7 * coverage + 0.3 * min(1.0, density * 5)


# ═══════════════════════════════════════════════════════════════
#  MAIN SEARCH FUNCTION
# ═══════════════════════════════════════════════════════════════
def semantic_search(user_text: str, papers_pool: list, top_k: int = 10) -> list:
    """
    Dual-Index Field-Aware Semantic Search.

    Builds separate BM25 indices for titles and abstracts with different
    tuning parameters, then combines 6 signals into a final score.

    Returns top_k results above the relevance threshold.
    """
    if not user_text or not papers_pool:
        return []

    q_tokens   = tokenize(user_text)
    q_norm     = normalize_text(user_text)
    q_bigrams  = get_ngrams(q_tokens, 2)
    q_trigrams = get_ngrams(q_tokens, 3)

    if not q_tokens:
        return []

    # ── Build dual corpus ─────────────────────────────────────
    title_corpus    = []
    abstract_corpus = []
    full_corpus     = []
    title_norms     = []
    abstract_norms  = []

    for paper in papers_pool:
        raw_title    = paper.get("title") or ""
        raw_abstract = paper.get("abstract") or ""

        t_tokens = tokenize(raw_title)
        a_tokens = tokenize(raw_abstract)
        f_tokens = t_tokens + a_tokens

        title_corpus.append(t_tokens if t_tokens else ["_empty_"])
        abstract_corpus.append(a_tokens if a_tokens else ["_empty_"])
        full_corpus.append(f_tokens if f_tokens else ["_empty_"])
        title_norms.append(normalize_text(raw_title))
        abstract_norms.append(normalize_text(raw_abstract))

    try:
        # ── BM25 Title Index (high k1, low b → favor exact keyword matches) ──
        bm25_title = BM25Okapi(title_corpus, k1=2.0, b=0.3)
        raw_title_scores = list(bm25_title.get_scores(q_tokens))

        # ── BM25 Abstract Index (standard tuning) ──
        bm25_abstract = BM25Okapi(abstract_corpus, k1=1.5, b=0.75)
        raw_abstract_scores = list(bm25_abstract.get_scores(q_tokens))

        # ── Normalize with sigmoid (not min-max!) ──
        norm_title    = soft_normalize(raw_title_scores)
        norm_abstract = soft_normalize(raw_abstract_scores)

        # ── Score each paper ─────────────────────────────────
        scored = []
        for idx in range(len(papers_pool)):
            # Signal 1: Title BM25
            s_title = norm_title[idx]

            # Signal 2: Abstract BM25
            s_abstract = norm_abstract[idx]

            # Signal 3: Exact phrase match
            s_exact = exact_phrase_score(q_norm, title_norms[idx], abstract_norms[idx])

            # Signal 4: Keyword density
            s_density = keyword_density(q_tokens, full_corpus[idx])

            # Signal 5: Bigram Jaccard
            doc_bigrams = get_ngrams(full_corpus[idx], 2)
            s_jac2 = jaccard(q_bigrams, doc_bigrams)

            # Signal 6: Trigram Jaccard
            doc_trigrams = get_ngrams(full_corpus[idx], 3)
            s_jac3 = jaccard(q_trigrams, doc_trigrams)

            # ── Weighted composite ────────────────────────────
            composite = (
                0.35 * s_title +
                0.25 * s_abstract +
                0.15 * s_exact +
                0.12 * s_density +
                0.08 * s_jac2 +
                0.05 * s_jac3
            )

            scored.append((idx, composite, s_title, s_abstract, s_exact, s_density))

        # ── Rank and filter ──────────────────────────────────
        scored.sort(key=lambda x: x[1], reverse=True)

        # Dynamic threshold: at least 10% of the top score, but minimum 0.08
        top_composite = scored[0][1] if scored else 0
        threshold = max(0.08, top_composite * 0.10)

        results = []
        for idx, composite, s_title, s_abstract, s_exact, s_density in scored:
            if composite < threshold:
                break

            paper = papers_pool[idx]

            # Convert composite to a display percentage (0-100)
            # Use calibrated scale: sigmoid maps composite to percentage
            display_score = min(99.0, round(composite * 130, 1))

            results.append({
                "paperId":         paper.get("paper_id"),
                "title":           paper.get("title"),
                "abstract":        paper.get("abstract"),
                "venue":           paper.get("venue"),
                "year":            paper.get("year"),
                "authors":         paper.get("authors"),
                "relevance_score": display_score,
                "_signals": {
                    "title_bm25":     round(s_title * 100, 1),
                    "abstract_bm25":  round(s_abstract * 100, 1),
                    "exact_phrase":   round(s_exact * 100, 1),
                    "keyword_density": round(s_density * 100, 1),
                }
            })

            if len(results) >= top_k:
                break

        return results

    except Exception as e:
        print(f"[similarity] Search engine error: {e}")
        return []
