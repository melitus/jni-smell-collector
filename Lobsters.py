"""
Fetch Lobsters posts using working API endpoints + HTML fallback.
Lobsters search JSON is broken, but tag feeds work perfectly.
"""

import requests
import pandas as pd
import html2text
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
API_BASE = "https://lobste.rs"
NUM_POSTS = 5

# Use tags instead of search (these endpoints WORK)
TAGS = ["java", "programming", "compilers"]  # Lobsters tags
SEARCH_TERMS = ["JNI", "Java Native Interface", "FFI", "native interop"]

# Inclusion criteria
INCLUSION_RULES = {
    "keywords": ["JNI", "Java Native Interface", "FFI", "Java", "native", "interop", "JNA", "Panama"],
    "min_score": 0,
    "min_comments": 0,
}

# Exclusion criteria
EXCLUSION_RULES = {
    "exclude_tags": ["job", "hiring", "career"],
    "exclude_title_keywords": ["hiring", "job opening", "position available"],
}


def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(html_content).strip()


def fetch_by_tag(tag: str) -> list[dict]:
    """Fetch stories from a Lobsters tag feed (THIS WORKS)."""
    url = f"{API_BASE}/t/{tag}.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # This endpoint returns JSON reliably
        results = response.json()
        
        if not results:
            print(f"  ⚠️  No results for tag '{tag}'")
            return []
        
        formatted = []
        for r in results:
            created_at = r.get("created_at", 0)
            if isinstance(created_at, str):
                creation_date = created_at[:10]
            else:
                creation_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d')
            
            formatted.append({
                "title": r.get("title", ""),
                "short_id": r.get("short_id", ""),
                "url": r.get("short_id_url", "") or r.get("url", ""),
                "description": r.get("description", "") or "",
                "score": r.get("score", 0),
                "comment_count": r.get("comment_count", 0),
                "submitter": r.get("submitter_user", "Unknown"),
                "tags": r.get("tags", []),
                "creation_date": creation_date,
                "keyword": f"tag:{tag}",
            })
        
        print(f"  ✅ Found {len(formatted)} stories from tag '{tag}'")
        return formatted
        
    except Exception as e:
        print(f"  ❌ Error fetching tag '{tag}': {e}")
        return []


def scrape_search_html(term: str) -> list[dict]:
    """Fallback: scrape search results from HTML page."""
    url = f"{API_BASE}/search?q={term}&what=stories&order=newest"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Lobsters story structure
        stories = soup.find_all('div', class_='story') or soup.find_all('li', class_='story')
        
        for story in stories[:20]:
            try:
                # Extract title and link
                title_link = story.find('a', class_='u-url') or story.find('a', class_='link')
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                story_url = title_link.get('href', '')
                
                # Extract description
                desc_elem = story.find('span', class_='description') or story.find('div', class_='description')
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract score
                score_elem = story.find('div', class_='score') or story.find('span', class_='score')
                score = int(score_elem.get_text(strip=True)) if score_elem and score_elem.get_text(strip=True).isdigit() else 0
                
                # Extract tags
                tag_elems = story.find_all('a', class_='tag')
                tags = [t.get_text(strip=True) for t in tag_elems]
                
                # Extract comments count
                comments_link = story.find('a', string=lambda s: s and 'comment' in s.lower() if s else False)
                comment_count = 0
                if comments_link:
                    import re
                    match = re.search(r'(\d+)', comments_link.get_text())
                    if match:
                        comment_count = int(match.group(1))
                
                results.append({
                    "title": title,
                    "short_id": "",
                    "url": story_url if story_url.startswith('http') else f"{API_BASE}{story_url}",
                    "description": description,
                    "score": score,
                    "comment_count": comment_count,
                    "submitter": "Unknown",
                    "tags": tags,
                    "creation_date": "",
                    "keyword": term,
                })
            except Exception as e:
                continue
        
        print(f"  ✅ Scraped {len(results)} stories for '{term}'")
        return results
        
    except Exception as e:
        print(f"  ❌ HTML scraping failed for '{term}': {e}")
        return []


def fetch_story_details(short_id: str) -> dict:
    """Fetch full story details from Lobsters page."""
    if not short_id:
        return {"description": "", "comments": []}
    
    # Try JSON first
    url = f"{API_BASE}/s/{short_id}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        comments = []
        for comment in data.get("comments", [])[:20]:
            author = comment.get("commenting_user", {}).get("username", "Unknown")
            text = clean_html(comment.get("comment", ""))
            score = comment.get("score", 0)
            comments.append(f"[{author}] (Score: {score})\n{text}")
        
        return {
            "description": data.get("description", ""),
            "comments": comments,
        }
    except Exception:
        return {"description": "", "comments": []}


def passes_inclusion(story: dict) -> tuple[bool, str]:
    title = story.get("title", "").lower()
    description = story.get("description", "").lower()
    text = f"{title} {description}"
    
    has_keyword = any(kw.lower() in text for kw in INCLUSION_RULES["keywords"])
    if not has_keyword:
        return False, "No relevant keywords"
    
    return True, "Passes inclusion"


def passes_exclusion(story: dict) -> tuple[bool, str]:
    title = story.get("title", "").lower()
    tags = story.get("tags", [])
    
    if isinstance(tags, str):
        tags = [tags]
    
    excluded_tags = [t for t in tags if t in EXCLUSION_RULES["exclude_tags"]]
    if excluded_tags:
        return False, f"Excluded tags: {excluded_tags}"
    
    return True, "Passes exclusion"


def build_story_record(story: dict) -> dict:
    details = fetch_story_details(story.get("short_id", ""))
    
    description = details.get("description") or story.get("description", "") or "No description (link post)"
    comments = details.get("comments", [])
    
    inc_passes, inc_reason = passes_inclusion(story)
    exc_passes, exc_reason = passes_exclusion(story)
    
    short_id = story.get("short_id", "")
    tags = story.get("tags", [])
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    
    time.sleep(1)
    
    return {
        "short_id": short_id,
        "title": story.get("title", ""),
        "description": description,
        "url": story.get("url", ""),
        "tags": tags_str,
        "score": story.get("score", 0),
        "comment_count": story.get("comment_count", 0),
        "submitter": story.get("submitter", "Unknown"),
        "creation_date": story.get("creation_date", ""),
        "search_keyword": story.get("keyword", ""),
        "comments": "\n\n---\n\n".join(comments) if comments else "No comments",
        "lobsters_url": f"{API_BASE}/s/{short_id}" if short_id else story.get("url", ""),
        "inclusion_criteria": inc_reason,
        "exclusion_criteria": exc_reason,
    }


def main():
    print(f"Fetching {NUM_POSTS} Lobsters stories")
    print(f"Strategy: Tag feeds (working) + HTML scraping (fallback)\n")
    
    all_stories = []
    
    # Strategy 1: Fetch from working tag feeds
    print("📡 Strategy 1: Fetching from tag feeds (reliable)")
    for tag in TAGS:
        stories = fetch_by_tag(tag)
        all_stories.extend(stories)
        time.sleep(1)
    
    # Strategy 2: HTML scraping for specific search terms
    print("\n🔍 Strategy 2: Scraping search HTML (fallback)")
    for term in SEARCH_TERMS:
        stories = scrape_search_html(term)
        all_stories.extend(stories)
        time.sleep(2)
    
    print(f"\nTotal raw results: {len(all_stories)}")
    
    # Deduplicate
    unique = {}
    for s in all_stories:
        key = s.get("short_id") or s.get("url", "")
        if key and key not in unique:
            unique[key] = s
    all_stories = list(unique.values())
    print(f"Unique stories: {len(all_stories)}\n")
    
    if not all_stories:
        print("❌ No stories found through any method!")
        print("\n📋 MANUAL COLLECTION GUIDE:")
        print("1. Visit: https://lobste.rs/t/java")
        print("2. Visit: https://lobste.rs/search?q=JNI")
        print("3. Manually copy 5 relevant posts to lobsters_template.xlsx")
        
        template_df = pd.DataFrame(columns=[
            "short_id", "title", "description", "url", "tags", "score",
            "comment_count", "submitter", "creation_date", "search_keyword",
            "comments", "lobsters_url", "inclusion_criteria", "exclusion_criteria"
        ])
        template_df.to_excel("lobsters_template.xlsx", index=False)
        print("✅ Created: lobsters_template.xlsx")
        return
    
    # Filter stories
    filtered = []
    excluded_log = []
    
    for i, story in enumerate(all_stories, 1):
        print(f"Processing {i}/{len(all_stories)}: {story.get('title', '')[:60]}...")
        
        inc_passes, inc_reason = passes_inclusion(story)
        if not inc_passes:
            excluded_log.append({"title": story.get("title", "")[:50], "reason": f"INCLUSION: {inc_reason}"})
            continue
        
        exc_passes, exc_reason = passes_exclusion(story)
        if not exc_passes:
            excluded_log.append({"title": story.get("title", "")[:50], "reason": f"EXCLUSION: {exc_reason}"})
            continue
        
        record = build_story_record(story)
        filtered.append(record)
        
        if len(filtered) >= NUM_POSTS:
            break
    
    print(f"\n📊 Filtering Summary:")
    print(f"  Total stories: {len(all_stories)}")
    print(f"  Excluded: {len(excluded_log)}")
    print(f"  Passed: {len(filtered)}")
    
    if excluded_log:
        print(f"\n❌ Excluded (first 3):")
        for item in excluded_log[:3]:
            print(f"  - {item['title']}: {item['reason']}")
    
    if not filtered:
        print("\n❌ No stories passed criteria!")
        print("   The tag feeds work, but none contained JNI-related content.")
        print("   This is expected - Lobsters is a small community.")
        return
    
    # Save
    df = pd.DataFrame(filtered)
    
    output_file = "lobsters_posts_filtered.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Stories")
        
        worksheet = writer.sheets["Stories"]
        for column in worksheet.columns:
            max_length = min(max(len(str(cell.value or "")) for cell in column) + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = max_length
    
    csv_file = "lobsters_posts_filtered.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"\n✅ Saved to {output_file} and {csv_file}")
    print(f"Total stories: {len(filtered)}")


if __name__ == "__main__":
    main()