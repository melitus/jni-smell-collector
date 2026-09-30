"""
Re-mine Stack Overflow posts using the same approach as scraper.py
Standalone script - only mines Stack Overflow

FIXED v2: Removed server-side tag filter that was causing 0 results for JNI keywords.
Now uses client-side post-filtering to ensure JNI relevance without restricting API results.
"""

import requests
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

# Configuration
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import keywords from categories.py (261 categorized keywords)
from categories import get_all_keywords

API_BASE = "https://api.stackexchange.com/2.3"
SITE = "stackoverflow"
API_KEY = "rl_6tCCJohCUSHcN8kVcghTNeoRd"

# Tags used for CLIENT-SIDE filtering (not sent to API)
JNI_RELATED_TAGS = {
    "java-native-interface",
    "jni",
    "jniwrapper",
    "jna",
    "java",
    "android",
    "android-ndk",
    "c++",
    "c",
    "jvm",
    "native-methods",
    "javacpp",
    "project-panama",
    "swig",
}
KEYWORDS = get_all_keywords()

MAX_PAGES = 6  # Max pages per keyword (100 results/page = 600 max per keyword)
PAGE_SIZE = 100
REQUEST_TIMEOUT = 15


# ============================================================
# Helpers
# ============================================================
def clean_html(html_content: str) -> str:
    """Clean HTML content to plain text."""
    if not html_content:
        return ""
    import html2text

    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(html_content).strip()


def _item_to_record(item: dict) -> dict | None:
    """
    Convert a raw SO item into a clean record dict.

    NEW: Client-side tag filtering to ensure JNI relevance.
    Returns None if post has no JNI-related tags.
    """
    link = item.get("link", "")
    if "/questions/" not in link:
        return None

    # ✅ NEW: Client-side tag filter
    post_tags = set(item.get("tags", []))
    if not post_tags.intersection(JNI_RELATED_TAGS):
        return None  # Skip posts without JNI-related tags

    raw_ts = item.get("creation_date")
    creation_date = (
        datetime.fromtimestamp(raw_ts).strftime("%Y-%m-%d") if raw_ts else "Unknown"
    )

    return {
        "title": item.get("title", ""),
        "link": link,
        "score": item.get("score", 0),
        "snippet": (item.get("body") or "")[:400],
        "creation_date": creation_date,
        "tags": ",".join(item.get("tags", [])),
        "answer_count": item.get("answer_count", 0),
        "view_count": item.get("view_count", 0),
    }


def _do_request(params: dict, keyword: str, page: int) -> requests.Response | None:
    """Do a single GET with timeout handling. Returns Response or None."""
    url = f"{API_BASE}/search/advanced"
    try:
        return requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        print(f"  ⚠️ StackOverflow timeout for '{keyword}' (page {page})")
        return None
    except Exception as e:
        print(f"  ❌ StackOverflow error on page {page}: {e}")
        return None


# ============================================================
# Core search function
# ============================================================
def search_stackoverflow(keyword: str) -> list[dict]:
    """
    Search Stack Overflow for a keyword (paginated).

    ✅ FIXED: No server-side tag filter. Filtering happens in _item_to_record().
    This prevents the API from returning 0 results for JNI-specific keywords.
    """
    all_items: list[dict] = []
    seen_links: set[str] = set()
    clean_keyword = keyword.strip()
    if not clean_keyword:
        return []

    for page in range(1, MAX_PAGES + 1):
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": clean_keyword,
            "site": SITE,
            "pagesize": PAGE_SIZE,
            "page": page,
            "filter": "withbody",
            "key": API_KEY,
            # ✅ REMOVED: "tagged" parameter - filtering is now client-side
        }

        resp = _do_request(params, keyword, page)
        if resp is None:
            break

        # ---- 200 OK ----
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if not items:
                break  # no more pages

            added = 0
            filtered_out = 0
            for it in items:
                rec = _item_to_record(it)
                if rec is None:
                    filtered_out += 1  # Filtered by client-side tag check
                    continue
                if rec["link"] not in seen_links:
                    seen_links.add(rec["link"])
                    all_items.append(rec)
                    added += 1

            # If nothing new was added this page, stop paging
            # (but continue if we only filtered by tags - there might be more)
            if added == 0 and filtered_out == 0:
                break

            time.sleep(0.5)
            continue

        # ---- 400 Bad Request ----
        elif resp.status_code == 400:
            err = resp.json().get("error_message", "Unknown error")
            print(f"  ⚠️ StackOverflow bad request for '{keyword}': {err}")
            break

        # ---- 403 Rate limit ----
        elif resp.status_code == 403:
            print(f"  ⚠️ StackOverflow rate limit. Waiting 60s...")
            time.sleep(60)
            continue

        # ---- Backoff / quota ----
        elif resp.status_code == 429 or "backoff" in resp.json():
            backoff = resp.json().get("backoff", 10)
            print(f"  ⚠️ Backoff required for {backoff}s")
            time.sleep(backoff)
            continue

        else:
            print(f"  ⚠️ StackOverflow error {resp.status_code} for '{keyword}'")
            break

    if not all_items:
        print(f"  (StackOverflow: 0 results for '{keyword}')")
    else:
        print(f"  ✅ StackOverflow: {len(all_items)} results for '{keyword}'")

    return all_items


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("🔍 RE-MINING STACK OVERFLOW")
    print("=" * 60)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Output:   {OUTPUT_DIR}")
    print(f"Client-side tag filter: {len(JNI_RELATED_TAGS)} JNI-related tags")
    print()

    all_results: list[dict] = []
    seen_global: set[str] = set()  # global dedupe across keywords

    for idx, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{idx}/{len(KEYWORDS)}] 🔍 Searching: '{keyword}'")
        results = search_stackoverflow(keyword)

        for res in results:
            if res["link"] in seen_global:
                continue
            seen_global.add(res["link"])

            all_results.append(
                {
                    "phase": "STACKOVERFLOW_REMINING",
                    "forum": "Stack Overflow",
                    "keyword": keyword,
                    "title": res["title"],
                    "link": res["link"],
                    "snippet": res["snippet"],
                    "score": res["score"],
                    "creation_date": res["creation_date"],
                    "tags": res.get("tags", ""),
                    "answer_count": res.get("answer_count", 0),
                    "view_count": res.get("view_count", 0),
                    "collected_at": datetime.now().isoformat(),
                }
            )

        # Rate limiting between keywords
        time.sleep(1.5)

    # ---- Save results ----
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        path = OUTPUT_DIR / f"stackoverflow_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'=' * 60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total unique Stack Overflow posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'=' * 60}")

        # Summary
        non_unknown = df[df["creation_date"] != "Unknown"]["creation_date"]
        print(f"\n📊 Summary:")
        if not non_unknown.empty:
            print(f"  Date range: {non_unknown.min()} to {non_unknown.max()}")
        print(f"  Average score: {df['score'].mean():.1f}")
        print(f"  Posts with answers: {(df['answer_count'] > 0).sum()}")
        print(f"  Posts with tags: {(df['tags'] != '').sum()}")

        # Per-keyword breakdown
        print(f"\n📋 Per-keyword counts:")
        for kw, count in df["keyword"].value_counts().items():
            print(f"  • {kw}: {count}")

        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()
