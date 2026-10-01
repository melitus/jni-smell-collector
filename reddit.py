"""
Reddit Scraper using Pullpush.io Archive API
NO AUTHENTICATION REQUIRED - Works immediately
"""

import requests
import pandas as pd
import html2text
import time
from datetime import datetime
from urllib.parse import quote_plus

# Configuration
SUBREDDITS = ["java", "androiddev", "programming", "learnjava", "javahelp"]
KEYWORDS = ["JNI", "Java Native Interface", "Java-native-interface", "JNA", "native interop"]
NUM_POSTS = 5

# Pullpush API (working Pushshift mirror)
API_BASE = "https://api.pullpush.io/reddit/search/submission"
COMMENTS_API = "https://api.pullpush.io/reddit/search/comment"

# Criteria
INCLUSION_KEYWORDS = [
    "JNI", "Java Native Interface", "JNA", "native method", "native interop",
    "FFM", "Foreign Function and Memory", "Project Panama", "JNR-FFI", "jextract",
    "UnsatisfiedLinkError", "System.loadLibrary", "jni.h", "JNIEXPORT", "NDK"
]
EXCLUSION_KEYWORDS = ["meme", "funny", "joke", "hiring", "job opening"]


def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(html_content).strip()


def search_archive(keyword: str, subreddit: str = None, limit: int = 100) -> list[dict]:
    """Search Reddit archive - NO AUTH REQUIRED."""
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
                
                if isinstance(created_utc, str):
                    creation_date = created_utc[:10]
                elif created_utc:
                    creation_date = datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d")
                else:
                    creation_date = ""
                
                posts.append({
                    "id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "selftext": post.get("selftext", ""),
                    "score": post.get("score", 0) or 0,
                    "num_comments": post.get("num_comments", 0) or 0,
                    "subreddit": post.get("subreddit", "unknown"),
                    "created_utc": created_utc,
                    "creation_date": creation_date,
                    "permalink": post.get("permalink", ""),
                    "url": post.get("url", ""),
                    "author": post.get("author", "[deleted]"),
                })
            
            return posts
        
        return []
    
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return []


def fetch_comments(post_id: str, limit: int = 15) -> list[str]:
    """Fetch comments - NO AUTH REQUIRED."""
    try:
        params = {
            "link_id": f"t3_{post_id}",
            "size": limit,
            "sort": "desc",
            "sort_type": "score",
        }
        
        response = requests.get(COMMENTS_API, params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            comments = []
            
            for comment in data.get("data", []):
                author = comment.get("author", "[deleted]")
                body = comment.get("body", "")
                score = comment.get("score", 0)
                
                if body and body not in ["[deleted]", "[removed]"]:
                    comments.append(f"[{author}] (Score: {score})\n{body}")
            
            return comments
        
        return []
    
    except Exception:
        return []


def passes_criteria(post: dict) -> tuple[bool, bool, str, str]:
    """Check inclusion and exclusion criteria."""
    title = post.get("title", "").lower()
    body = post.get("selftext", "").lower()
    text = f"{title} {body}"
    
    # Inclusion
    inc_pass = any(kw.lower() in text for kw in INCLUSION_KEYWORDS)
    inc_reason = "Passes inclusion" if inc_pass else "No relevant keywords"
    
    # Exclusion
    exc_pass = not any(kw.lower() in text for kw in EXCLUSION_KEYWORDS)
    exc_reason = "Passes exclusion" if exc_pass else f"Contains excluded keyword"
    
    return inc_pass, exc_pass, inc_reason, exc_reason


def main():
    print("="*70)
    print("🚀 Reddit Archive Scraper (Pullpush.io)")
    print("="*70)
    print("NO AUTHENTICATION REQUIRED")
    print(f"Target: {NUM_POSTS} posts\n")
    
    # Collect posts
    all_posts = []
    
    print("📡 Phase 1: Searching Reddit archive...")
    for subreddit in SUBREDDITS:
        for keyword in KEYWORDS:
            print(f"  🔍 r/{subreddit} + '{keyword}'")
            posts = search_archive(keyword, subreddit, limit=50)
            all_posts.extend(posts)
            time.sleep(1)
            
            if len(all_posts) >= NUM_POSTS * 10:
                break
        
        if len(all_posts) >= NUM_POSTS * 10:
            break
    
    # Global search if needed
    if len(all_posts) < NUM_POSTS * 5:
        print("\n📡 Phase 2: Global search...")
        for keyword in KEYWORDS:
            print(f"  🔍 Global: '{keyword}'")
            posts = search_archive(keyword, limit=100)
            all_posts.extend(posts)
            time.sleep(1)
            
            if len(all_posts) >= NUM_POSTS * 10:
                break
    
    print(f"\n📊 Found {len(all_posts)} raw posts")
    
    if not all_posts:
        print("❌ Archive API not responding")
        print("   Try again in a few minutes")
        return
    
    # Deduplicate
    unique = {}
    for post in all_posts:
        post_id = post.get("id")
        if post_id and post_id not in unique:
            unique[post_id] = post
    all_posts = list(unique.values())
    print(f"   {len(all_posts)} unique posts\n")
    
    # Apply criteria and build records
    print("🔍 Phase 3: Filtering and enriching...")
    filtered = []
    
    for post in all_posts:
        inc_pass, exc_pass, inc_reason, exc_reason = passes_criteria(post)
        
        if not (inc_pass and exc_pass):
            continue
        
        # Fetch comments
        comments = fetch_comments(post["id"])
        time.sleep(0.5)
        
        record = {
            "post_id": post["id"],
            "subreddit": f"r/{post['subreddit']}",
            "title": post["title"],
            "post_body": post["selftext"][:3000] if post["selftext"] else f"[Link: {post['url']}]",
            "score": post["score"],
            "num_comments": post["num_comments"],
            "creation_date": post["creation_date"],
            "author": post["author"],
            "comments": "\n\n---\n\n".join(comments) if comments else "No comments",
            "url": f"https://reddit.com{post['permalink']}" if post["permalink"] else post["url"],
            "inclusion_criteria": inc_reason,
            "exclusion_criteria": exc_reason,
        }
        
        filtered.append(record)
        print(f"  ✅ [{len(filtered)}/{NUM_POSTS}] {post['title'][:60]}")
        
        if len(filtered) >= NUM_POSTS:
            break
    
    if not filtered:
        print("\n❌ No posts passed criteria!")
        return
    
    # Save
    df = pd.DataFrame(filtered)
    
    output_xlsx = "reddit_posts_filtered.xlsx"
    output_csv = "reddit_posts_filtered.csv"
    
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Posts")
        
        worksheet = writer.sheets["Posts"]
        for column in worksheet.columns:
            max_length = min(max(len(str(cell.value or "")) for cell in column) + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = max_length
    
    df.to_csv(output_csv, index=False)
    
    print(f"\n✅ Saved {len(filtered)} posts to:")
    print(f"   - {output_xlsx}")
    print(f"   - {output_csv}")
    
    print(f"\n📋 Summary:")
    for r in filtered:
        print(f"   [{r['score']}↑] {r['subreddit']} - {r['title'][:50]}")


if __name__ == "__main__":
    main()