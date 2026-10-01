"""
Re-mine Reddit posts using Reddit API.
Based on the working Lobsters script pattern.
- Phase 1: Search by subreddit (like tag search in Lobsters)
- Phase 2: Search by keywords (with fallback handling)
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

# Subreddits to search (like tags in Lobsters)
SUBREDDITS = ["java", "androiddev", "programming", "learnjava", "javahelp"]

# Keywords for Reddit loaded from scientific selection
KEYWORDS = load_selected_keywords("reddit")

# Proper headers to avoid blocking (similar to Lobsters)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

# Conservative rate matching Lobsters pattern
REQUEST_DELAY = 10.0  # 10 seconds between requests
MAX_RETRIES = 3
BACKOFF_BASE = 60  # Start with 60 second backoff


def search_reddit_by_subreddit(subreddit, retry_count=0):
    """
    Search Reddit by subreddit (similar to Lobsters tag search).
    Uses: https://www.reddit.com/r/{subreddit}/search.json
    """
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": "",  # Empty query gets recent posts from subreddit
        "sort": "new",
        "limit": 100,
        "restrict_sr": "on",  # Restrict to subreddit
        "t": "all"  # All time
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)

        if resp.status_code == 200:
            data = resp.json()

            formatted = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                created_utc = post_data.get("created_utc", 0)
                if created_utc:
                    creation_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')
                else:
                    creation_date = "Unknown"

                formatted.append({
                    "title": post_data.get("title", ""),
                    "link": f"https://reddit.com{post_data.get('permalink', '')}",
                    "score": post_data.get("score", 0),
                    "snippet": (post_data.get("selftext", "") or "")[:400],
                    "creation_date": creation_date,
                    "subreddit": subreddit,
                    "num_comments": post_data.get("num_comments", 0),
                })

            return formatted

        elif resp.status_code == 429:
            # Rate limited - retry with exponential backoff
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_BASE * (2 ** retry_count)
                print(f"  ⚠️ Rate limited (429). Waiting {wait_time}s (retry {retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return search_reddit_by_subreddit(subreddit, retry_count + 1)
            else:
                print(f"  ❌ Max retries exceeded for r/{subreddit}")
                return []

        else:
            print(f"  ⚠️ Reddit API error {resp.status_code} for r/{subreddit}")
            return []

    except requests.exceptions.Timeout:
        print(f"  ⚠️ Reddit timeout for r/{subreddit}")
        if retry_count < MAX_RETRIES:
            wait_time = BACKOFF_BASE * (2 ** retry_count)
            print(f"     Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return search_reddit_by_subreddit(subreddit, retry_count + 1)
        return []

    except Exception as e:
        print(f"  ❌ Reddit Error: {e}")
        return []


def search_reddit_by_keyword(keyword, retry_count=0):
    """
    Search Reddit by keyword across all subreddits.
    Uses: https://www.reddit.com/search.json
    """
    url = f"https://www.reddit.com/search.json"
    params = {
        "q": keyword,
        "sort": "relevance",
        "limit": 100,
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)

        if resp.status_code == 200:
            data = resp.json()

            formatted = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                created_utc = post_data.get("created_utc", 0)
                if created_utc:
                    creation_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')
                else:
                    creation_date = "Unknown"

                formatted.append({
                    "title": post_data.get("title", ""),
                    "link": f"https://reddit.com{post_data.get('permalink', '')}",
                    "score": post_data.get("score", 0),
                    "snippet": (post_data.get("selftext", "") or "")[:400],
                    "creation_date": creation_date,
                    "subreddit": post_data.get("subreddit", ""),
                    "num_comments": post_data.get("num_comments", 0),
                })

            return formatted

        elif resp.status_code == 429:
            # Rate limited - retry with exponential backoff
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_BASE * (2 ** retry_count)
                print(f"  ⚠️ Rate limited (429). Waiting {wait_time}s (retry {retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return search_reddit_by_keyword(keyword, retry_count + 1)
            else:
                print(f"  ❌ Max retries exceeded for '{keyword}'")
                return []

        else:
            print(f"  ⚠️ Reddit API error {resp.status_code} for '{keyword}'")
            return []

    except requests.exceptions.Timeout:
        print(f"  ⚠️ Reddit timeout for '{keyword}'")
        if retry_count < MAX_RETRIES:
            wait_time = BACKOFF_BASE * (2 ** retry_count)
            print(f"     Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return search_reddit_by_keyword(keyword, retry_count + 1)
        return []

    except Exception as e:
        print(f"  ❌ Reddit Error: {e}")
        return []


def main():
    print("="*60)
    print("🔍 RE-MINING REDDIT (LOBSTERS-PATTERN)")
    print("="*60)
    print(f"Subreddits: {SUBREDDITS}")
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Rate limiting: {REQUEST_DELAY}s between requests")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Initial wait to avoid immediate rate limiting
    print("⏳ Initial 30-second wait to avoid rate limiting...")
    time.sleep(30)

    all_results = []

    # Phase 1: Search by subreddit (more likely to work)
    print("\n📁 Phase 1: Searching by subreddit (like Lobsters tag search)")
    for subreddit in SUBREDDITS:
        print(f"\n🔍 Searching subreddit: r/{subreddit}")
        results = search_reddit_by_subreddit(subreddit)

        if results:
            print(f"   ✅ Found {len(results)} posts")

        for res in results:
            all_results.append({
                "phase": "REDDIT_REMINING",
                "forum": "Reddit",
                "keyword": res["subreddit"],  # Using subreddit as keyword for consistency
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "subreddit": res["subreddit"],
                "num_comments": res.get("num_comments", 0),
                "collected_at": datetime.now().isoformat()
            })

        # Conservative rate limiting with jitter
        jitter = random.uniform(-2, 2)
        time.sleep(REQUEST_DELAY + jitter)

    # Phase 2: Search by keywords (use fewer keywords to avoid rate limits)
    print("\n📁 Phase 2: Searching by keywords")

    # Use only top 10 most important keywords to avoid rate limiting
    top_keywords = KEYWORDS[:10] if len(KEYWORDS) > 10 else KEYWORDS

    for keyword in top_keywords:
        print(f"\n🔍 Searching keyword: '{keyword}'")
        results = search_reddit_by_keyword(keyword)

        if results:
            print(f"   ✅ Found {len(results)} posts")

        for res in results:
            all_results.append({
                "phase": "REDDIT_REMINING",
                "forum": "Reddit",
                "keyword": keyword,
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "subreddit": res["subreddit"],
                "num_comments": res.get("num_comments", 0),
                "collected_at": datetime.now().isoformat()
            })

        # Conservative rate limiting with jitter
        jitter = random.uniform(-2, 2)
        time.sleep(REQUEST_DELAY + jitter)

    # Save results
    if all_results:
        df = pd.DataFrame(all_results)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"reddit_remined_{timestamp}.csv"
        df.to_csv(path, index=False)

        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Reddit posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")

        # Show summary
        print(f"\n📊 Summary:")
        non_unknown = df[df['creation_date'] != 'Unknown']['creation_date']
        if not non_unknown.empty:
            print(f"  Date range: {non_unknown.min()} to {non_unknown.max()}")
        print(f"  Average score: {df['score'].mean():.1f}")
        print(f"  Subreddit breakdown:")
        print(df['subreddit'].value_counts().to_string())
        print(f"  Keyword breakdown:")
        print(df['keyword'].value_counts().head(10).to_string())

        return df
    else:
        print("\n❌ No results found!")
        print("\n💡 Reddit API is restrictive. Consider:")
        print("   1. Using Reddit's official API with OAuth")
        print("   2. Using a different IP or VPN")
        print("   3. Waiting 24 hours and trying again")
        print("   4. Using pushshift.io alternative")

        # Create manual template
        template_df = pd.DataFrame(columns=[
            "phase", "forum", "keyword", "title", "link", "snippet",
            "score", "creation_date", "subreddit", "num_comments", "collected_at"
        ])
        template_path = OUTPUT_DIR / "reddit_manual_template.csv"
        template_df.to_csv(template_path, index=False)
        print(f"\n📋 Manual template created: {template_path}")

        return pd.DataFrame()


if __name__ == "__main__":
    main()