"""
Scaled-up Reddit Scraper (based on working approach)
- Keeps the simple, fast pattern
- Processes keywords in batches to avoid rate limits
"""

import requests
import pandas as pd
import html2text
import time
from datetime import datetime
from pathlib import Path

# Import centralized keywords
from keyword_selection import load_selected_keywords

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Use the working configuration
SUBREDDITS = ["java", "androiddev", "programming", "learnjava", "javahelp"]

# Keywords for Reddit loaded from scientific selection
KEYWORDS = load_selected_keywords("reddit")



API_BASE = "https://api.pullpush.io/reddit/search/submission"


def search_archive(keyword, subreddit, limit=100):
    """Simple search - NO User-Agent, NO retries, just works."""
    params = {
        "q": keyword,
        "size": limit,
        "sort": "desc",
        "sort_type": "score",
    }
    if subreddit:
        params["subreddit"] = subreddit
    
    try:
        response = requests.get(API_BASE, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            for post in data.get("data", []):
                created_utc = post.get("created_utc", 0)
                creation_date = (
                    datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d")
                    if isinstance(created_utc, (int, float)) and created_utc
                    else "Unknown"
                )
                posts.append({
                    "id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "selftext": post.get("selftext", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "subreddit": post.get("subreddit", ""),
                    "creation_date": creation_date,
                    "permalink": post.get("permalink", ""),
                    "url": post.get("url", ""),
                })
            return posts
        else:
            print(f"    ⚠️  Status {response.status_code} - skipping")
            return []
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return []


def main():
    print("="*70)
    print("🔍 SCALED REDDIT SCRAPER (Simple Approach)")
    print("="*70)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Subreddits: {len(SUBREDDITS)}")
    print(f"Total planned requests: {len(KEYWORDS) * len(SUBREDDITS)}")
    print()
    
    all_results = []
    seen_ids = set()
    request_count = 0
    
    # Process in batches of 5 keywords to avoid rate limits
    BATCH_SIZE = 5
    keyword_batches = [KEYWORDS[i:i+BATCH_SIZE] for i in range(0, len(KEYWORDS), BATCH_SIZE)]
    
    for batch_num, batch in enumerate(keyword_batches, 1):
        print(f"\n📦 Batch {batch_num}/{len(keyword_batches)}: {batch}")
        
        for keyword in batch:
            for subreddit in SUBREDDITS:
                request_count += 1
                print(f"  [{request_count}] r/{subreddit} + '{keyword}'", end=" ")
                
                posts = search_archive(keyword, subreddit, limit=100)
                print(f"→ {len(posts)} posts")
                
                # Add new posts
                for post in posts:
                    if post["id"] not in seen_ids:
                        seen_ids.add(post["id"])
                        all_results.append({
                            "phase": "REDDIT_REMINING",
                            "forum": "Reddit",
                            "keyword": keyword,
                            "title": post["title"],
                            "link": f"https://reddit.com{post['permalink']}" if post['permalink'] else post['url'],
                            "snippet": (post["selftext"] or "")[:400],
                            "score": post["score"],
                            "creation_date": post["creation_date"],
                            "subreddit": post["subreddit"],
                            "num_comments": post["num_comments"],
                            "collected_at": datetime.now().isoformat(),
                        })
                
                # Simple 1-second delay (matches working script)
                time.sleep(1)
        
        # Longer pause between batches (10 seconds)
        if batch_num < len(keyword_batches):
            print(f"\n  ⏸️  Batch pause: 10 seconds...")
            time.sleep(10)
    
    # Save results
    if all_results:
        df = pd.DataFrame(all_results)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"reddit_scaled_{timestamp}.csv"
        df.to_csv(path, index=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPING COMPLETE!")
        print(f"   Total requests: {request_count}")
        print(f"   Unique posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*70}")
        
        print(f"\n📊 Summary:")
        print(f"  Subreddit breakdown:")
        print(df['subreddit'].value_counts().to_string())
        print(f"\n  Top keywords:")
        for kw, count in df['keyword'].value_counts().head(10).items():
            print(f"    • {kw}: {count}")
        
        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()