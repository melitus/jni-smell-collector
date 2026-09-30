"""
Re-mine Lobsters posts using lobste.rs API
Standalone script - only mines Lobsters
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

API_BASE = "https://lobste.rs"

# Keywords (imported from config.py)
KEYWORDS = OPTIMIZED_KEYWORDS

# Tags for Lobsters search
TAGS = ["JNI", "Java Native Interface", "Java-native-interface", "FFI", "native interop", "jni", "javawrapper"]


def search_lobsters(query):
    """Search Lobsters for a query (tag or keyword)."""
    try:
        url = f"{API_BASE}/search.json?q={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=15)

        if resp.status_code == 200:
            results = resp.json()

            formatted = []
            for r in results:
                # Extract creation date from Unix timestamp
                created_at = r.get("created_at", 0)
                if created_at:
                    creation_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d')
                else:
                    creation_date = "Unknown"

                formatted.append({
                    "title": r.get("title", ""),
                    "link": r.get("short_id_url", ""),
                    "score": r.get("score", 0),
                    "snippet": (r.get("description") or "")[:400],
                    "creation_date": creation_date,
                    "tag": query,  # Store what we searched for
                    "num_comments": r.get("comment_count", 0),
                })

            return formatted
        else:
            print(f"  ⚠️ Lobsters API error {resp.status_code} for query '{query}'")
            return []

    except requests.exceptions.Timeout:
        print(f"  ⚠️ Lobsters timeout for query '{query}'")
        return []
    except Exception as e:
        print(f"  ❌ Lobsters Error: {e}")
        return []


def main():
    print("="*60)
    print("🔍 RE-MINING LOBSTERS")
    print("="*60)
    print(f"Tags: {TAGS}")
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    all_results = []

    # Search by tags first
    for tag in TAGS:
        print(f"\n🔍 Searching tag: '{tag}'")
        results = search_lobsters(tag)

        for res in results:
            all_results.append({
                "phase": "LOBSTERS_REMINING",
                "forum": "Lobsters",
                "keyword": tag,
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "tag": res.get("tag", ""),
                "num_comments": res.get("num_comments", 0),
                "collected_at": datetime.now().isoformat()
            })

        # Rate limiting
        time.sleep(1.0)

    # Search by keywords (same as other forums)
    for keyword in KEYWORDS:
        print(f"\n🔍 Searching keyword: '{keyword}'")
        results = search_lobsters(keyword)

        for res in results:
            all_results.append({
                "phase": "LOBSTERS_REMINING",
                "forum": "Lobsters",
                "keyword": keyword,
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "tag": res.get("tag", ""),
                "num_comments": res.get("num_comments", 0),
                "collected_at": datetime.now().isoformat()
            })

        # Rate limiting
        time.sleep(1.0)

    # Save results
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"lobsters_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Lobsters posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")

        # Show summary
        print(f"\n📊 Summary:")
        print(f"  Date range: {df['creation_date'].min()} to {df['creation_date'].max()}")
        print(f"  Average score: {df['score'].mean():.1f}")
        print(f"  Tag breakdown:")
        print(df['tag'].value_counts().to_string())

        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()