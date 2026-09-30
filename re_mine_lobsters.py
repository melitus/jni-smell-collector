"""
Re-mine Lobsters posts using lobste.rs API
FIXED: Correct API parameters, better rate limiting, proper headers
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

API_BASE = "https://lobste.rs"

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Keywords for Lobsters loaded from scientific selection
KEYWORDS = load_selected_keywords("lobsters")

# Tags for Lobsters search (only use actual Lobsters tags)
TAGS = ["java", "programming", "compilers", "security", "android"]

# Proper headers to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

# Conservative rate limiting
REQUEST_DELAY = 10.0  # 10 seconds between requests (very conservative)
MAX_RETRIES = 3
BACKOFF_BASE = 60  # Start with 60 second backoff


def search_lobsters(query, retry_count=0):
    """
    Search Lobsters with correct API parameters.
    
    Lobsters API format:
    /search.json?q=QUERY&what=stories&order=newest
    """
    
    url = f"{API_BASE}/search.json"
    params = {
        "q": query,
        "what": "stories",  # ✅ Required parameter
        "order": "newest",  # ✅ Required parameter
    }
    
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
        
        if resp.status_code == 200:
            results = resp.json()
            
            formatted = []
            for r in results:
                # Extract creation date
                created_at = r.get("created_at", 0)
                if created_at:
                    if isinstance(created_at, str):
                        creation_date = created_at[:10]
                    else:
                        creation_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d')
                else:
                    creation_date = "Unknown"
                
                formatted.append({
                    "title": r.get("title", ""),
                    "link": r.get("short_id_url", "") or r.get("url", ""),
                    "score": r.get("score", 0),
                    "snippet": (r.get("description") or "")[:400],
                    "creation_date": creation_date,
                    "query": query,
                    "num_comments": r.get("comment_count", 0),
                    "tags": ", ".join(r.get("tags", [])),
                })
            
            return formatted
        
        elif resp.status_code == 429:
            # Rate limited - retry with exponential backoff
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_BASE * (2 ** retry_count)
                print(f"  ⚠️ Rate limited (429). Waiting {wait_time}s (retry {retry_count + 1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return search_lobsters(query, retry_count + 1)
            else:
                print(f"  ❌ Max retries exceeded for '{query}'")
                return []
        
        elif resp.status_code == 400:
            # Bad request - log the error
            print(f"  ❌ Bad request (400) for '{query}'")
            print(f"     URL: {resp.url}")
            print(f"     Response: {resp.text[:200]}")
            return []
        
        else:
            print(f"  ⚠️ Lobsters API error {resp.status_code} for query '{query}'")
            return []
    
    except requests.exceptions.Timeout:
        print(f"  ⚠️ Lobsters timeout for query '{query}'")
        if retry_count < MAX_RETRIES:
            wait_time = BACKOFF_BASE * (2 ** retry_count)
            print(f"     Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return search_lobsters(query, retry_count + 1)
        return []
    
    except Exception as e:
        print(f"  ❌ Lobsters Error: {e}")
        return []


def search_by_tag(tag_name):
    """
    Search Lobsters by tag using the tag endpoint.
    Format: /t/TAG.json
    """
    url = f"{API_BASE}/t/{tag_name}.json"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        
        if resp.status_code == 200:
            results = resp.json()
            
            formatted = []
            for r in results:
                created_at = r.get("created_at", 0)
                if created_at:
                    if isinstance(created_at, str):
                        creation_date = created_at[:10]
                    else:
                        creation_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d')
                else:
                    creation_date = "Unknown"
                
                formatted.append({
                    "title": r.get("title", ""),
                    "link": r.get("short_id_url", "") or r.get("url", ""),
                    "score": r.get("score", 0),
                    "snippet": (r.get("description") or "")[:400],
                    "creation_date": creation_date,
                    "query": f"tag:{tag_name}",
                    "num_comments": r.get("comment_count", 0),
                    "tags": ", ".join(r.get("tags", [])),
                })
            
            return formatted
        else:
            print(f"  ⚠️ Tag search error {resp.status_code} for '{tag_name}'")
            return []
    
    except Exception as e:
        print(f"  ❌ Tag search error: {e}")
        return []


def main():
    print("="*60)
    print("🔍 RE-MINING LOBSTERS (FIXED)")
    print("="*60)
    print(f"Tags: {TAGS}")
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Rate limiting: {REQUEST_DELAY}s between requests")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Initial wait to avoid immediate rate limiting
    print("⏳ Initial 30-second wait to avoid rate limiting...")
    time.sleep(30)
    
    all_results = []
    
    # Phase 1: Search by tags (more likely to work)
    print("\n📁 Phase 1: Searching by tags")
    for tag in TAGS:
        print(f"\n🔍 Searching tag: '{tag}'")
        results = search_by_tag(tag)
        
        if results:
            print(f"   ✅ Found {len(results)} stories")
        
        for res in results:
            all_results.append({
                "phase": "LOBSTERS_REMINING",
                "forum": "Lobsters",
                "keyword": res["query"],
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "tags": res.get("tags", ""),
                "num_comments": res.get("num_comments", 0),
                "collected_at": datetime.now().isoformat()
            })
        
        # Conservative rate limiting with jitter
        jitter = random.uniform(-2, 2)
        time.sleep(REQUEST_DELAY + jitter)
    
    # Phase 2: Search by keywords (fewer keywords to avoid rate limits)
    print("\n📁 Phase 2: Searching by keywords")
    
    # Use only top 10 most important keywords to avoid rate limiting
    top_keywords = KEYWORDS[:10] if len(KEYWORDS) > 10 else KEYWORDS
    
    for keyword in top_keywords:
        print(f"\n🔍 Searching keyword: '{keyword}'")
        results = search_lobsters(keyword)
        
        if results:
            print(f"   ✅ Found {len(results)} stories")
        
        for res in results:
            all_results.append({
                "phase": "LOBSTERS_REMINING",
                "forum": "Lobsters",
                "keyword": res["query"],
                "title": res["title"],
                "link": res["link"],
                "snippet": res["snippet"],
                "score": res["score"],
                "creation_date": res["creation_date"],
                "tags": res.get("tags", ""),
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
        path = OUTPUT_DIR / f"lobsters_remined_{timestamp}.csv"
        df.to_csv(path, index=False)
        
        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total Lobsters posts: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")
        
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
        print("\n💡 Lobsters API is very restrictive. Consider:")
        print("   1. Manual collection from https://lobste.rs")
        print("   2. Using a VPN or different network")
        print("   3. Waiting 24 hours and trying again")
        
        # Create manual template
        template_df = pd.DataFrame(columns=[
            "phase", "forum", "keyword", "title", "link", "snippet",
            "score", "creation_date", "tags", "num_comments", "collected_at"
        ])
        template_path = OUTPUT_DIR / "lobsters_manual_template.csv"
        template_df.to_csv(template_path, index=False)
        print(f"\n📋 Manual template created: {template_path}")
        
        return pd.DataFrame()


if __name__ == "__main__":
    main()