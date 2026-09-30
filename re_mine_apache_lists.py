"""
Re-mine Apache Mailing Lists posts using lists.apache.org API
Standalone script - only mines Apache Lists
"""

import requests
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from urllib.parse import quote_plus

# Configuration
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import centralized keywords
from config import OPTIMIZED_KEYWORDS

API_BASE = "https://lists.apache.org/api/lucene.lua"

# Keywords (imported from config.py)
KEYWORDS = OPTIMIZED_KEYWORDS

# Apache projects to search (from search_criteria.yaml)
PROJECTS = ["hadoop", "spark", "kafka", "flink"]


def search_apache_lists(keyword, project=None):
    """Search Apache Mailing Lists for a keyword, optionally filtered by project."""
    try:
        # Build query - can add project filter
        if project:
            query = f"{keyword} list:{project}.apache.org"
        else:
            query = keyword

        url = f"{API_BASE}?q={quote_plus(query)}&size=100"
        resp = requests.get(url, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            docs = data.get("response", {}).get("docs", [])

            results = []
            for doc in docs:
                # Extract creation date
                date_str = doc.get("date", "Unknown")
                if date_str and date_str != "Unknown":
                    creation_date = date_str[:10]
                else:
                    creation_date = "Unknown"

                # Get link
                msg_id = doc.get("id", "")
                link = f"https://lists.apache.org/thread/{msg_id}" if msg_id else ""

                results.append({
                    "title": doc.get("subject", ""),
                    "link": link,
                    "score": 0,
                    "snippet": (doc.get("body") or "")[:400],
                    "creation_date": creation_date,
                    "project": project or "all",
                    "list": doc.get("list", ""),
                    "thread_id": msg_id,
                })

            return results
        else:
            print(f"  ⚠️ Apache Lists API error {resp.status_code} for query '{query}'")
            return []

    except requests.exceptions.Timeout:
        print(f"  ⚠️ Apache Lists timeout for query '{query}'")
        return []
    except Exception as e:
        print(f"  ❌ Apache Lists Error: {e}")
        return []


def main():
    print("="*60)
    print("🔍 RE-MINING APACHE MAILING LISTS")
    print("="*60)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Projects: {PROJECTS}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    all_results = []

    # Search across all projects (no project filter first)
    print(f"\n📁 Searching all projects (no project filter)")
    for keyword in KEYWORDS:
        print(f"  🔍 Searching: '{keyword}'")
        results = search_apache_lists(keyword, project=None)

        for res in results:
            all_results.append({
                "phase": "APACHE_LISTS_REMINING",
                "forum": "Apache Lists",
                "keyword": keyword,
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "project": res.get("project", ""),
                "list": res.get("list", ""),
                "thread_id": res.get("thread_id", ""),
                "collected_at": datetime.now().isoformat()
            })

        # Rate limiting
        time.sleep(1.0)

    # Search each project specifically
    for project in PROJECTS:
        print(f"\n📁 Project: {project}")

        for keyword in KEYWORDS:
            print(f"  🔍 Searching: '{keyword}'")
            results = search_apache_lists(keyword, project=project)

            for res in results:
                all_results.append({
                    "phase": "APACHE_LISTS_REMINING",
                    "forum": "Apache Lists",
                    "keyword": keyword,
                    "title": res["title"],
                    "link": res["link"],
                    "snippet": res["snippet"],
                    "score": res["score"],
                    "creation_date": res["creation_date"],
                    "project": res.get("project", ""),
                    "list": res.get("list", ""),
                    "thread_id": res.get("thread_id", ""),
                    "collected_at": datetime.now().isoformat()
                })

            # Rate limiting
            time.sleep(1.0)

    # Save results
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"apache_lists_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Apache Lists posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")

        # Show summary
        print(f"\n📊 Summary:")
        print(f"  Date range: {df['creation_date'].min()} to {df['creation_date'].max()}")
        print(f"  Project breakdown:")
        print(df['project'].value_counts().to_string())

        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()