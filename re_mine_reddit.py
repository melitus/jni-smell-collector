"""
Re-mine Reddit posts with ultra-conservative rate limiting
"""

import requests
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
import random

# Configuration
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

from config import OPTIMIZED_KEYWORDS

# Multiple API endpoints (fallbacks)
API_ENDPOINTS = [
    "https://api.pullpush.io/reddit/search/submission",
    "https://arctic-shift.photon-reddit.com/api/posts",  # Fallback
]

SUBREDDITS = ["java", "androiddev", "programming", "learnjava", "javahelp"]

# REDUCED: Only 15 high-value JNI keywords (instead of 261)
# These are the most specific and likely to return relevant posts
KEYWORDS = [
    "JNI",
    "Java Native Interface",
    "JNA",
    "JNI memory leak",
    "DeleteLocalRef",
    "global reference",
    "local reference",
    "UnsatisfiedLinkError",
    "JNI crash",
    "native method",
    "System.loadLibrary",
    "JNI threading",
    "JNI performance",
    "native interop",
    "Project Panama",
]

# Ultra-conservative rate limiting
REQUEST_DELAY = 5.0  # 5 seconds between requests (increased from 2.5)
MAX_RETRIES = 5      # More retries
BACKOFF_BASE = 30    # Start with 30 second backoff (increased from 10)
CIRCUIT_BREAKER_THRESHOLD = 5  # Stop after 5 consecutive failures


def search_reddit_with_fallback(keyword, subreddit, retry_count=0, consecutive_failures=0):
    """
    Search with multiple API endpoints and circuit breaker.
    """
    # Circuit breaker: stop if too many consecutive failures
    if consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
        print(f"  🛑 Circuit breaker: {consecutive_failures} consecutive failures. Stopping.")
        return [], consecutive_failures
    
    # Try each API endpoint
    for api_url in API_ENDPOINTS:
        try:
            params = {
                "q": keyword,
                "size": 100,
                "sort": "desc",
                "sort_type": "score",
            }
            
            # Add subreddit filter if supported
            if "pullpush" in api_url:
                params["subreddit"] = subreddit
            
            # Add random jitter (±1 second)
            jitter = random.uniform(-1.0, 1.0)
            
            resp = requests.get(api_url, params=params, timeout=20)
            
            # Success
            if resp.status_code == 200:
                data = resp.json()
                
                # Handle different API response formats
                if "pullpush" in api_url:
                    children = data.get("data", {}).get("children", [])
                else:  # arctic-shift
                    children = [{"data": post} for post in data.get("data", [])]
                
                results = []
                for child in children:
                    post = child.get("data", {})
                    
                    created_utc = post.get("created_utc", 0)
                    if created_utc:
                        creation_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')
                    else:
                        creation_date = "Unknown"
                    
                    permalink = post.get("permalink", "")
                    link = f"https://reddit.com{permalink}" if permalink else ""
                    
                    # Filter by subreddit if using arctic-shift
                    post_subreddit = post.get("subreddit", "")
                    if "arctic-shift" in api_url and post_subreddit.lower() != subreddit.lower():
                        continue
                    
                    results.append({
                        "title": post.get("title", ""),
                        "link": link,
                        "score": post.get("score", 0),
                        "snippet": (post.get("selftext") or "")[:400],
                        "creation_date": creation_date,
                        "subreddit": subreddit,
                        "num_comments": post.get("num_comments", 0),
                        "upvote_ratio": post.get("upvote_ratio", 0),
                    })
                
                # Reset consecutive failures on success
                return results, 0
            
            # Rate limited
            elif resp.status_code == 429:
                if retry_count < MAX_RETRIES:
                    wait_time = (BACKOFF_BASE * (2 ** retry_count)) + jitter
                    print(f"  ⚠️ Rate limited. Waiting {wait_time:.1f}s (retry {retry_count + 1}/{MAX_RETRIES})...")
                    time.sleep(wait_time)
                    return search_reddit_with_fallback(
                        keyword, subreddit, retry_count + 1, consecutive_failures + 1
                    )
                else:
                    return [], consecutive_failures + 1
            
            # Other errors
            else:
                print(f"  ⚠️ API error {resp.status_code} from {api_url}")
                continue
        
        except Exception as e:
            print(f"  ❌ Error with {api_url}: {e}")
            continue
    
    return [], consecutive_failures + 1


def main():
    print("="*60)
    print("🔍 RE-MINING REDDIT (Ultra-Conservative Mode)")
    print("="*60)
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Subreddits: {SUBREDDITS}")
    print(f"Rate limiting: {REQUEST_DELAY}s delay, {MAX_RETRIES} retries")
    print(f"Circuit breaker: Stop after {CIRCUIT_BREAKER_THRESHOLD} consecutive failures")
    print()
    
    # Initial wait to avoid immediate rate limiting
    print("⏳ Initial 30-second wait to avoid rate limiting...")
    time.sleep(30)
    
    all_results = []
    consecutive_failures = 0
    total_requests = 0
    successful_requests = 0
    
    for subreddit in SUBREDDITS:
        print(f"\n📁 Subreddit: r/{subreddit}")
        
        for idx, keyword in enumerate(KEYWORDS, 1):
            print(f"  [{idx}/{len(KEYWORDS)}] 🔍 Searching: '{keyword}'")
            
            results, consecutive_failures = search_reddit_with_fallback(
                keyword, subreddit, 0, consecutive_failures
            )
            
            total_requests += 1
            if results:
                successful_requests += 1
                consecutive_failures = 0  # Reset on success
            
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
                    "upvote_ratio": res.get("upvote_ratio", 0),
                    "collected_at": datetime.now().isoformat()
                })
            
            # Rate limiting with jitter
            jitter = random.uniform(-0.5, 0.5)
            time.sleep(REQUEST_DELAY + jitter)
            
            # Progress update
            if idx % 10 == 0:
                print(f"  📊 Progress: {idx}/{len(KEYWORDS)}, {len(all_results)} posts, {successful_requests}/{total_requests} successful")
            
            # Early stop if circuit breaker triggered
            if consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
                print(f"\n🛑 Circuit breaker triggered. Stopping early.")
                break
        
        # Reset consecutive failures between subreddits
        consecutive_failures = 0
    
    # Save results
    if all_results:
        df = pd.DataFrame(all_results)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"reddit_remined_{timestamp}.csv"
        df.to_csv(path, index=False)
        
        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Reddit posts: {len(df)}")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful: {successful_requests} ({100*successful_requests/total_requests:.1f}%)")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")
        
        return df
    else:
        print("\n❌ No results found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()