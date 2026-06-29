import os
import re
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
S2_API_KEY   = os.environ.get("S2_API_KEY")
S2_URL       = "https://api.semanticscholar.org/graph/v1/paper/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ScholarAI-Bot/2.0; Academic Research Tool)",
    "Accept": "application/json"
}
if S2_API_KEY:
    HEADERS["x-api-key"] = S2_API_KEY

# ── All topics (35+ disciplines) ──────────────────────────────
KEYWORDS = [
    # Technology
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "computer vision", "internet of things",
    "blockchain", "cloud computing", "cyber security", "data mining",
    "software engineering", "jaringan komputer", "sistem informasi",
    "database", "big data analytics", "edge computing", "quantum computing", "simple additive weighting", "sistem pendukung keputusan", "rancang bangun sistem",
    # Health & Science
    "kesehatan masyarakat", "epidemiologi penyakit", "farmasi klinik",
    "bioinformatics", "medical imaging", "telemedicine", "genomics",
    # Social & Humanities
    "pendidikan", "psikologi sosial", "komunikasi massa", "sosiologi",
    "ilmu politik", "hukum pidana", "hukum perdata",
    # Economics & Business
    "manajemen bisnis", "akuntansi", "ekonomi digital", "fintech",
    "digital marketing", "e-commerce", "supply chain management",
    # Engineering & Environment
    "teknik sipil", "teknik mesin", "energi terbarukan",
    "perubahan iklim", "pertanian modern", "teknologi pangan",
    "pendidikan anak usia dini"
]


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_state(supabase: Client, keyword: str):
    try:
        res = supabase.table("scrape_state").select("*").eq("keyword", keyword).execute()
        if res.data:
            return res.data[0]["current_year"], res.data[0]["current_offset"]
    except Exception as e:
        print(f"  [state] Error for '{keyword}': {e}")
    return 2024, 0


def update_state(supabase: Client, keyword: str, year: int, offset: int):
    try:
        supabase.table("scrape_state").upsert(
            {"keyword": keyword, "current_year": year, "current_offset": offset},
            on_conflict="keyword"
        ).execute()
    except Exception as e:
        print(f"  [state] Save error for '{keyword}': {e}")


def upsert_papers(supabase: Client, papers: list) -> int:
    """Batch-upsert papers into Supabase."""
    inserted = 0
    for paper in papers:
        try:
            supabase.table("papers").upsert(paper, on_conflict="paper_id").execute()
            inserted += 1
        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "storage" in err:
                print("  [DB] CRITICAL: Storage quota exceeded. Stopping.")
                raise RuntimeError("quota_exceeded")
    return inserted


def fetch_page(keyword: str, year: int, offset: int) -> dict | None:
    """Fetch one page (50 papers) from Semantic Scholar API with retry logic."""
    params = {
        "query":  keyword,
        "limit":  50,
        "offset": offset,
        "year":   str(year),
        "fields": "title,abstract,venue,year,authors"
    }
    for attempt in range(1, 4):
        try:
            res = requests.get(S2_URL, params=params, headers=HEADERS, timeout=20)
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 429:
                wait = 45 * attempt
                print(f"  [429] Rate limit on '{keyword}' (attempt {attempt}). Waiting {wait}s…")
                time.sleep(wait)
            else:
                print(f"  [API] Error {res.status_code} for '{keyword}'")
                return None
        except Exception as e:
            print(f"  [NET] Error attempt {attempt}: {e}")
            time.sleep(10)
    return None


def scrape_keyword(supabase: Client, keyword: str, pages: int = 3):
    """Scrape `pages` pages for a given keyword."""
    print(f"\n► Scraping: '{keyword}'")
    year, offset = get_state(supabase, keyword)
    scraped = 0

    for _ in range(pages):
        data = fetch_page(keyword, year, offset)
        if data is None:
            print(f"  Skip '{keyword}' — fetch failed.")
            break

        papers_raw = data.get("data", [])
        total      = data.get("total", 0)

        if not papers_raw:
            year -= 1
            offset = 0
            print(f"  No more papers for {year + 1}. Moving to {year}.")
            if year < 1990:
                year = 2024
            update_state(supabase, keyword, year, offset)
            continue

        rows = []
        for p in papers_raw:
            abstract = clean_text(p.get("abstract"))
            if not abstract:
                continue
            authors_list = [a.get("name", "") for a in p.get("authors", [])]
            rows.append({
                "paper_id": p.get("paperId"),
                "title":    clean_text(p.get("title")),
                "abstract": abstract,
                "venue":    clean_text(p.get("venue")),
                "year":     p.get("year"),
                "authors":  ", ".join(authors_list)
            })

        try:
            n = upsert_papers(supabase, rows)
            scraped += n
            print(f"  Page offset={offset}: {n}/{len(papers_raw)} saved (total DB target: {total})")
        except RuntimeError:
            return

        offset += 50
        if offset >= min(9950, total):
            year -= 1
            offset = 0
            if year < 1990:
                year = 2024

        update_state(supabase, keyword, year, offset)
        time.sleep(4)  # polite delay between pages

    print(f"  Done '{keyword}': {scraped} papers saved.")


def scrape_and_store():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials. Exiting.")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Pick 4 keywords per run, weighted toward under-scraped ones
    # Simple approach: random shuffle, take first 4
    pool = KEYWORDS.copy()
    random.shuffle(pool)
    selected = pool[:4]

    print(f"Selected keywords this run: {selected}")

    # Parallel scraping: 2 workers at a time (conservative to avoid rate limits)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(scrape_keyword, supabase, kw, 3): kw
            for kw in selected
        }
        for future in as_completed(futures):
            kw = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"  [WORKER] Exception in '{kw}': {e}")

    print("\n✓ Scraping session complete.")


if __name__ == "__main__":
    scrape_and_store()
