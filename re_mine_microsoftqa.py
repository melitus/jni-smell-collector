"""
Re-mine Microsoft Q&A posts using the learn.microsoft.com search API.
Standalone script - only mines Microsoft Q&A.
"""

import requests
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
import random

# Import centralized keywords
from keyword_selection import load_selected_keywords

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Keywords for Microsoft Q&A loaded from scientific selection
# Using Microsoft Q&A platform-specific selection (Q&A forum vocabulary)
KEYWORDS = load_selected_keywords("microsoftqa")
if not KEYWORDS:  # Fallback to reddit keywords
    print("⚠️ No Microsoft Q&A keywords found, using Reddit keywords...")
    KEYWORDS = load_selected_keywords("reddit")

# Proper headers to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://learn.microsoft.com/en-us/search/",
}

# Conservative rate limiting
REQUEST_DELAY = 3.0  # 3 seconds between requests
MAX_RETRIES = 3


def search_microsoft_qa(keyword, retry_count=0):
    """
    Search Microsoft Q&A using the learn.microsoft.com search API.

    API format:
    https://learn.microsoft.com/api/search?search=QUERY&locale=en-us&top=20&category=answers
    """

    url = "https://learn.microsoft.com/api/search"
    params = {
        "search": keyword,
        "locale": "en-us",
        "top": 20,
        "category": "answers",
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)

        if resp.status_code == 200:
            data = resp.json()

            results = data.get("results", []) or data.get("value", []) or data.get("items", [])

            if not results:
                return []

            formatted = []
            for r in results:
                # Extract date from lastUpdatedDate (only date field available)
                creation_date = r.get("lastUpdatedDate", "")
                if creation_date:
                    creation_date = creation_date[:10]  # YYYY-MM-DD
                else:
                    creation_date = "Unknown"

                formatted.append({
                    "title": r.get("title", "") or r.get("name", ""),
                    "link": r.get("url", "") or r.get("link", "") or r.get("uri", ""),
                    "score": 0,
                    "snippet": (r.get("summary", "") or r.get("description", "") or r.get("content", ""))[:400],
                    "creation_date": creation_date,
                })

            return formatted

        elif resp.status_code == 403:
            # Rate limited - retry with exponential backoff
            if retry_count < MAX_RETRIES:
                wait_time = 30 * (2 ** retry_count)
                print(f"  ⚠️ Rate limited (403). Waiting {wait_time}s (retry {retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return search_microsoft_qa(keyword, retry_count + 1)
            else:
                print(f"  ❌ Max retries exceeded for '{keyword}'")
                return []

        elif resp.status_code == 400:
            print(f"  ❌ Bad request (400) for '{keyword}'")
            print(f"     URL: {resp.url}")
            print(f"     Response: {resp.text[:200]}")
            return []

        else:
            print(f"  ⚠️ Microsoft Q&A error {resp.status_code} for query '{keyword}'")
            return []

    except requests.exceptions.Timeout:
        print(f"  ⚠️ Microsoft Q&A timeout for query '{keyword}'")
        if retry_count < MAX_RETRIES:
            wait_time = 30 * (2 ** retry_count)
            print(f"     Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return search_microsoft_qa(keyword, retry_count + 1)
        return []

    except Exception as e:
        print(f"  ❌ Microsoft Q&A Error: {e}")
        return []


def main():
    print("=" * 60)
    print("🔍 RE-MINING MICROSOFT Q&A")
    print("=" * 60)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Rate limiting: {REQUEST_DELAY}s between requests")
    print(f"Output: {OUTPUT_DIR}")
    print()

    all_results = []

    for keyword in KEYWORDS:
        print(f"\n🔍 Searching keyword: '{keyword}'")
        results = search_microsoft_qa(keyword)

        if results:
            print(f"   ✅ Found {len(results)} results")

        for res in results:
            all_results.append({
                "phase": "MICROSOFTQA_REMINING",
                "forum": "Microsoft Q&A",
                "keyword": keyword,
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "collected_at": datetime.now().isoformat()
            })

        # Conservative rate limiting with jitter
        jitter = random.uniform(-1, 1)
        time.sleep(REQUEST_DELAY + jitter)

    # Save results
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"microsoftqa_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'=' * 60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Microsoft Q&A posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'=' * 60}")

        # Show summary
        print(f"\n📊 Summary:")
        non_unknown = df[df['creation_date'] != 'Unknown']['creation_date']
        if not non_unknown.empty:
            print(f"  Date range: {non_unknown.min()} to {non_unknown.max()}")
        print(f"  Average score: {df['score'].mean():.1f}")
        print(f"  Keyword breakdown:")
        print(df['keyword'].value_counts().head(10).to_string())

        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()