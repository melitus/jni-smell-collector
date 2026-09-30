"""
Re-mine Hacker News posts using Algolia API
Standalone script - only mines Hacker News
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

# Import centralized keywords
from config import OPTIMIZED_KEYWORDS

API_BASE = "https://hn.algolia.com/api/v1"

# Keywords (imported from config.py)
KEYWORDS = OPTIMIZED_KEYWORDS

# Tags for HN search (structural tags)
TAGS = ["story", "comment"]


def search_hackernews(keyword, tag):
    """Search Hacker News for a keyword using Algolia API."""
    all_hits = []

    try:
        url = f"{API_BASE}/search"
        params = {
            "query": keyword,
            "tags": tag,
            "hitsPerPage": 100,
        }

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", [])

        for hit in hits:
            # Extract creation date
            created_at = hit.get("created_at", "")
            if created_at:
                creation_date = created_at[:10]
            else:
                creation_date = "Unknown"

            # Determine post type
            if tag == "story":
                post_type = "story"
                title = hit.get("title", "")
                text = hit.get("story_text") or ""
                external_url = hit.get("url")
            else:
                post_type = "comment"
                title = hit.get("story_title", "")
                text = hit.get("comment_text") or ""
                external_url = None

            all_hits.append({
                "title": title,
                "link": external_url or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "score": hit.get("points") or 0,
                "snippet": text[:400],
                "creation_date": creation_date,
                "type": post_type,
                "author": hit.get("author", "Unknown"),
                "num_comments": hit.get("num_comments") or 0,
                "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            })

        return all_hits

    except requests.exceptions.Timeout:
        print(f"  ⚠️ HN timeout for '{keyword}' in tag '{tag}'")
        return []
    except Exception as e:
        print(f"  ❌ HN Error: {e}")
        return []


def main():
    print("="*60)
    print("🔍 RE-MINING HACKER NEWS")
    print("="*60)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Tags: {TAGS}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    all_results = []

    # Search by tags first (story, comment)
    for tag in TAGS:
        print(f"\n📁 Tag: {tag}")

        for keyword in KEYWORDS:
            print(f"  🔍 Searching: '{keyword}'")
            results = search_hackernews(keyword, tag)

            for res in results:
                all_results.append({
                    "phase": "HACKERNEWS_REMINING",
                    "forum": "Hacker News",
                    "keyword": keyword,
                    "title": res["title"],
                    "link": res["link"],
                    "snippet": res["snippet"],
                    "score": res["score"],
                    "creation_date": res["creation_date"],
                    "type": res.get("type", ""),
                    "author": res.get("author", ""),
                    "num_comments": res.get("num_comments", 0),
                    "collected_at": datetime.now().isoformat()
                })

            # Rate limiting
            time.sleep(0.5)

    # Save results
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"hackernews_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Hacker News posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")

        # Show summary
        print(f"\n📊 Summary:")
        print(f"  Date range: {df['creation_date'].min()} to {df['creation_date'].max()}")
        print(f"  Average score: {df['score'].mean():.1f}")
        print(f"  Type breakdown:")
        print(df['type'].value_counts().to_string())

        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()