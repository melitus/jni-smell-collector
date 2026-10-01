import requests
import re
import time
import warnings
import pandas as pd
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote_plus
from tqdm import tqdm

from config import STACKEXCHANGE_API_KEY

warnings.filterwarnings("ignore", category=RuntimeWarning)

class RealSmellCollector:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    # --- 1. STACK OVERFLOW (FIXED: Creation date + Link validation) ---
    def search_stackexchange(self, keyword: str) -> List[Dict]:
        all_items = []
        clean_keyword = keyword.strip()
        if not clean_keyword:
            return []
            
        for page in range(1, 6):
            try:
                url = "https://api.stackexchange.com/2.3/search/advanced"
                params = {
                    "order": "desc",
                    "sort": "relevance",
                    "q": clean_keyword,
                    "site": "stackoverflow",
                    "pagesize": 100,
                    "page": page,
                    "filter": "withbody",
                    "key": STACKEXCHANGE_API_KEY
                }
                
                if any(term in clean_keyword.lower() for term in ['jni', 'java', 'jvm', 'native', 'c++', 'android']):
                    params["tagged"] = "java-native-interface;jni;jniwrapper;jna" 
                
                resp = self.session.get(url, params=params, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [])
                    if not items:
                        break
                    
                    for i in items:
                        # FIX 1: Extract actual creation date from API
                        raw_timestamp = i.get("creation_date")
                        if raw_timestamp:
                            creation_date = datetime.fromtimestamp(raw_timestamp).strftime('%Y-%m-%d')
                        else:
                            creation_date = "Unknown"
                        
                        # FIX 2: Validate link is a specific question, not landing page
                        link = i.get("link", "")
                        if "/questions/" not in link:
                            continue  # Skip invalid links
                        
                        all_items.append({
                            "title": i.get("title", ""), 
                            "link": link, 
                            "score": i.get("score", 0), 
                            "snippet": (i.get("body") or "")[:400],
                            "creation_date": creation_date  # Actual post date!
                        })
                    
                    time.sleep(0.5)
                    
                elif resp.status_code == 400:
                    error_msg = resp.json().get('error_message', 'Unknown error')
                    print(f"      ⚠️ StackOverflow bad request for '{keyword}': {error_msg}")
                    
                    if "tagged" in params:
                        del params["tagged"]
                        resp2 = self.session.get(url, params=params, timeout=15)
                        if resp2.status_code == 200:
                            items = resp2.json().get("items", [])
                            for i in items:
                                raw_timestamp = i.get("creation_date")
                                creation_date = datetime.fromtimestamp(raw_timestamp).strftime('%Y-%m-%d') if raw_timestamp else "Unknown"
                                link = i.get("link", "")
                                if "/questions/" in link:
                                    all_items.append({
                                        "title": i.get("title", ""), 
                                        "link": link, 
                                        "score": i.get("score", 0), 
                                        "snippet": (i.get("body") or "")[:400],
                                        "creation_date": creation_date
                                    })
                            time.sleep(0.5)
                    break
                    
                elif resp.status_code == 403:
                    print(f"      ⚠️ StackOverflow rate limit. Waiting 60s...")
                    time.sleep(60)
                    continue
                    
                else:
                    print(f"      ⚠️ StackOverflow error {resp.status_code} for '{keyword}'")
                    break
                    
            except requests.exceptions.Timeout:
                print(f"      ⚠️ StackOverflow timeout for '{keyword}'")
                break
            except Exception as e:
                print(f"      ❌ StackOverflow Error on page {page}: {e}")
                break
        
        if not all_items: 
            print(f"      (StackOverflow: 0 results for '{keyword}')")
        else:
            print(f"      ✅ StackOverflow: {len(all_items)} results for '{keyword}'")
        
        return all_items
    
    # --- 2. GITHUB ISSUES (FIXED: Creation date + Link validation) ---
    def search_github(self, keyword: str) -> List[Dict]:
        try:
            repos = "repo:google/conscrypt repo:libgdx/libgdx repo:eclipse-openj9/openj9 repo:facebook/react-native repo:realm/realm-java"
            url = "https://api.github.com/search/issues"
            resp = self.session.get(
                url, 
                params={"q": f"{keyword} {repos} type:issue", "per_page": 30}, 
                timeout=15
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if not items:
                    print(f"      (GitHub: 0 results for '{keyword}')")
                
                results = []
                for i in items:
                    # FIX 1: Extract actual creation date
                    created_at = i.get("created_at", "")
                    creation_date = created_at[:10] if created_at else "Unknown"  # Extract YYYY-MM-DD
                    
                    # FIX 2: Validate link is a specific issue
                    link = i.get("html_url", "")
                    if "/issues/" not in link:
                        continue  # Skip invalid links
                    
                    results.append({
                        "title": i.get("title", ""), 
                        "link": link, 
                        "score": 0, 
                        "snippet": (i.get("body") or "")[:400],
                        "creation_date": creation_date  # Actual issue date!
                    })
                
                time.sleep(6)
                return results
            elif resp.status_code == 403:
                print("      ⚠️ GitHub rate limit. Waiting 60s...")
                time.sleep(60)
        except Exception as e:
            print(f"      ❌ GitHub Error: {e}")
        return []

    # --- 3. BUGZILLA (FIXED: Creation date) ---
    def search_bugzilla(self, keyword: str) -> List[Dict]:
        try:
            url = "https://bugzilla.mozilla.org/rest/bug"
            params = {
                "summary": keyword, 
                "limit": 50, 
                "include_fields": "summary,id,creation_time"
            }
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                bugs = resp.json().get("bugs", [])
                if not bugs:
                    print(f"      (Bugzilla: 0 results for '{keyword}')")
                
                results = []
                for b in bugs:
                    # FIX: Extract actual creation date
                    creation_time = b.get("creation_time", "")
                    creation_date = creation_time[:10] if creation_time else "Unknown"
                    
                    results.append({
                        "title": f"Bug {b.get('id')}: {b.get('summary', '')}", 
                        "link": f"https://bugzilla.mozilla.org/show_bug.cgi?id={b.get('id')}", 
                        "score": 0, 
                        "snippet": "",
                        "creation_date": creation_date  # Actual bug report date!
                    })
                return results
        except Exception as e:
            print(f"      ❌ Bugzilla Error: {e}")
        return []

    # --- 4. NATIVE FORUM APIS (FIXED: Creation dates) ---
    def search_lobsters(self, keyword: str) -> List[Dict]:
        try:
            url = f"https://lobste.rs/search.json?q={quote_plus(keyword)}"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                results = resp.json()
                if not results:
                    print(f"      (Lobsters: 0 results for '{keyword}')")
                
                return [
                    {
                        "title": r.get("title", ""), 
                        "link": r.get("short_id_url", ""), 
                        "score": r.get("score", 0), 
                        "snippet": (r.get("description") or "")[:400],
                        "creation_date": datetime.fromtimestamp(r.get("created_at", 0)).strftime('%Y-%m-%d') if r.get("created_at") else "Unknown"
                    } 
                    for r in results[:10]
                ]
        except Exception as e:
            print(f"      ❌ Lobsters Error: {e}")
        return []

    def search_llvm_discourse(self, keyword: str) -> List[Dict]:
        try:
            url = f"https://discourse.llvm.org/search.json?q={quote_plus(keyword)}&limit=10"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                items = resp.json().get("posts", [])
                if not items:
                    print(f"      (LLVM Discourse: 0 results for '{keyword}')")
                
                return [
                    {
                        "title": i.get("topic_title", ""), 
                        "link": f"https://discourse.llvm.org/t/{i.get('topic_slug')}/{i.get('topic_id')}", 
                        "score": 0, 
                        "snippet": (i.get("blurb") or "")[:400],
                        "creation_date": i.get("created_at", "Unknown")[:10] if i.get("created_at") else "Unknown"
                    } 
                    for i in items[:10]
                ]
        except Exception as e:
            print(f"      ❌ LLVM Discourse Error: {e}")
        return []

    def search_apache_lists(self, keyword: str) -> List[Dict]:
        try:
            url = f"https://lists.apache.org/api/lucene.lua?q={quote_plus(keyword)}&size=10"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                docs = resp.json().get("response", {}).get("docs", [])
                if not docs:
                    print(f"      (Apache Lists: 0 results for '{keyword}')")
                
                return [
                    {
                        "title": doc.get("subject", ""), 
                        "link": doc.get("id", ""), 
                        "score": 0, 
                        "snippet": (doc.get("body") or "")[:400],
                        "creation_date": doc.get("date", "Unknown")[:10] if doc.get("date") else "Unknown"
                    } 
                    for doc in docs[:10]
                ]
        except Exception as e:
            print(f"      ❌ Apache Lists Error: {e}")
        return []

    # --- 5. FALLBACK ENGINE (SearXNG) ---
    def search_fallback_engine(self, keyword: str, site: str) -> List[Dict]:
        query = f"{keyword} site:{site}"
        searx_instances = [
            "https://searx.be", 
            "https://search.ononoki.org", 
            "https://searx.nicfab.eu"
        ]
        
        for instance in searx_instances:
            try:
                time.sleep(2)
                url = f"{instance}/search?q={quote_plus(query)}&format=json"
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            print(f"      ✅ SearXNG ({instance.split('//')[1]}) succeeded!")
                            return [
                                {
                                    "title": r.get("title", ""), 
                                    "link": r.get("url", ""), 
                                    "score": 1, 
                                    "snippet": (r.get("content") or "")[:400],
                                    "creation_date": "Unknown"  # SearXNG doesn't provide dates
                                } 
                                for r in results[:10]
                            ]
                    except ValueError:
                        continue
            except Exception:
                continue
                
        print(f"      ❌ All SearXNG instances failed for '{keyword}' on {site}")
        return []
    
    # --- 6. REDDIT (FIXED: Creation date) ---
    def search_reddit(self, keyword: str) -> List[Dict]:
        try:
            url = f"https://old.reddit.com/search.json?q={quote_plus(keyword)}&sort=relevance&limit=10"
            resp = requests.get(url, headers=self.session.headers, timeout=15)
            if resp.status_code == 200:
                children = resp.json().get("data", {}).get("children", [])
                if not children:
                    print(f"      (Reddit: 0 results for '{keyword}')")
                
                return [
                    {
                        "title": c['data'].get("title", ""), 
                        "link": f"https://reddit.com{c['data'].get('permalink', '')}", 
                        "score": c['data'].get("score", 0), 
                        "snippet": (c['data'].get("selftext") or "")[:400],
                        "creation_date": datetime.fromtimestamp(c['data'].get("created_utc", 0)).strftime('%Y-%m-%d') if c['data'].get("created_utc") else "Unknown"
                    } 
                    for c in children
                ]
            else:
                print(f"      ⚠️ Reddit blocked (Status {resp.status_code})")
        except Exception as e:
            print(f"      ❌ Reddit Error: {e}")
        return []
    
    # --- 7. HACKER NEWS (FIXED: Creation date) ---
    def search_hackernews(self, keyword: str) -> List[Dict]:
        try:
            resp = self.session.get(
                "http://hn.algolia.com/api/v1/search", 
                params={"query": keyword, "tags": "story,comment", "hitsPerPage": 10}, 
                timeout=15
            )
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if not hits:
                    print(f"      (HackerNews: 0 results for '{keyword}')")
                
                return [
                    {
                        "title": h.get("title") or h.get("story_title", ""), 
                        "link": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}", 
                        "score": h.get("points", 0) or 0, 
                        "snippet": (h.get("comment_text") or h.get("story_text") or "")[:400],
                        "creation_date": h.get("created_at", "Unknown")[:10] if h.get("created_at") else "Unknown"
                    } 
                    for h in hits if h.get("title") or h.get("story_title")
                ]
        except Exception as e:
            print(f"      ❌ HackerNews Error: {e}")
        return []
    
        # --- 8. MICROSOFT Q&A (Direct Search API) ---
    def search_microsoft_qa(self, keyword: str) -> List[Dict]:
        """Search Microsoft Q&A using their internal search API.

        NOTE: This API returns Microsoft Learn documentation, not Q&A forum posts.
        Creation dates are not reliably available from this endpoint.
        """
        try:
            url = "https://learn.microsoft.com/api/search"

            # Corrected parameters (no $ prefix)
            params = {
                "search": keyword,
                "locale": "en-us",
                "top": 20,
                "category": "answers"
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://learn.microsoft.com/en-us/search/'
            }

            resp = self.session.get(url, params=params, headers=headers, timeout=15)

            if resp.status_code == 200:
                data = resp.json()

                # Try different result field names
                results = data.get("results", []) or data.get("value", []) or data.get("items", [])

                if not results:
                    print(f"      (Microsoft Q&A: 0 results for '{keyword}')")
                    return []

                formatted_results = []
                for r in results:
                    # Try different field names for date
                    # NOTE: Microsoft Learn API only provides lastUpdatedDate, not creation_date
                    creation_date = (
                        r.get("lastUpdatedDate", "") or
                        "Unknown"
                    )
                    creation_date = creation_date[:10] if creation_date and creation_date != "Unknown" else "Unknown"

                    formatted_results.append({
                        "title": r.get("title", "") or r.get("name", ""),
                        "link": r.get("url", "") or r.get("link", "") or r.get("uri", ""),
                        "score": 0,
                        "snippet": (r.get("summary", "") or r.get("description", "") or r.get("content", ""))[:400],
                        "creation_date": creation_date
                    })

                print(f"      ✅ Microsoft Q&A: {len(formatted_results)} results for '{keyword}'")
                return formatted_results

            elif resp.status_code == 403:
                print(f"      ⚠️ Microsoft Q&A blocked (403). Skipping...")
            else:
                print(f"      ⚠️ Microsoft Q&A returned status {resp.status_code}")

        except Exception as e:
            print(f"      ❌ Microsoft Q&A Error: {e}")

        return []
    
    # --- DISPATCHER ---
    def search_forum(self, forum: Dict, keyword: str) -> List[Dict]:
        method = forum.get("method", "fallback")
        site = forum.get("site", "")
        
        if method == "stackexchange":
            return self.search_stackexchange(keyword)
        elif method == "github":
            return self.search_github(keyword)
        elif method == "bugzilla_api":
            return self.search_bugzilla(keyword)
        elif method == "reddit_json":
            return self.search_reddit(keyword)
        elif method == "hn_api":
            return self.search_hackernews(keyword)
        elif method == "lobsters_api":
            return self.search_lobsters(keyword)
        elif method == "llvm_api":
            return self.search_llvm_discourse(keyword)
        elif method == "apache_api":
            return self.search_apache_lists(keyword)
        elif method == "microsoft_qa_api":  # <-- ADD THIS LINE
            return self.search_microsoft_qa(keyword)  # <-- ADD THIS LINE
        elif method in ["duckduckgo", "fallback"]:
            return self.search_fallback_engine(keyword, site)
        return []
    
    # --- MAIN RUNNER (FIXED: Save creation_date) ---
    def run(self, phase_name: str, forums: List[Dict], keywords: List[str]) -> pd.DataFrame:
        print(f"\n{'='*60}")
        print(f"🚀 {phase_name}")
        print(f"   Keywords: {len(keywords)} | Forums: {len(forums)}")
        print(f"{'='*60}\n")
        
        self.results = []
        total_expected = len(forums) * len(keywords)
        
        with tqdm(total=total_expected, desc="Overall Progress") as pbar:
            for forum in forums:
                print(f"\n🔍 [{forum['name']}]")
                forum_count = 0
                for kw in keywords:
                    results = self.search_forum(forum, kw)
                    for res in results:
                        link = res.get("link", "")
                        if not link or link == "#" or len(link) < 10:
                            continue
                        
                        self.results.append({
                            "phase": phase_name,
                            "forum": forum["name"],
                            "keyword": kw,
                            "title": res["title"],
                            "link": link,
                            "snippet": res.get("snippet", ""),
                            "score": res.get("score", 0),
                            "creation_date": res.get("creation_date", "Unknown"),  # Actual post date!
                            "collected_at": datetime.now().isoformat()
                        })
                        forum_count += 1
                    
                    if forum.get("method") not in ["github", "bugzilla_api", "lobsters_api", "llvm_api", "apache_api"]:
                        time.sleep(1.5)
                    pbar.update(1)
                
                if forum_count == 0:
                    print(f"   ❌ WARNING: Found 0 results for entire {forum['name']} forum!")
                else:
                    print(f"   ✅ Found {forum_count} real results")
        
        return pd.DataFrame(self.results)