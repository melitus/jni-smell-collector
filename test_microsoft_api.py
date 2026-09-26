import requests
from typing import List, Dict

def test_microsoft_qa_search(keyword: str = "JNI memory leak"):
    """Test Microsoft Q&A search API with corrected parameters."""
    print(f"🔍 Testing Microsoft Q&A search for: '{keyword}'\n")
    
    session = requests.Session()
    
    try:
        # Microsoft's search endpoint (corrected parameters)
        url = "https://learn.microsoft.com/api/search"
        
        # FIXED: Use 'search' instead of '$search', remove invalid $filter
        params = {
            "search": keyword,
            "locale": "en-us",
            "top": 20,
            "category": "answers"  # Try different filter approaches
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://learn.microsoft.com/en-us/search/'
        }
        
        print(f"📡 Sending request to: {url}")
        print(f"📋 Parameters: {params}\n")
        
        resp = session.get(url, params=params, headers=headers, timeout=15)
        
        print(f"📊 Response Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Debug: Show raw response structure
            print(f"\n🔬 Response keys: {list(data.keys())}")
            
            # Try different result field names
            results = data.get("results", []) or data.get("value", []) or data.get("items", [])
            
            if not results:
                print(f"\n❌ No results found for '{keyword}'")
                print(f"\n📄 Full response (first 1000 chars):")
                print(str(data)[:1000])
                return []
            
            print(f"\n✅ Found {len(results)} results!\n")
            
            formatted_results = []
            for i, r in enumerate(results[:5], 1):  # Show first 5
                # Try different field names for date
                creation_date = (
                    r.get("date", "") or 
                    r.get("datePublished", "") or 
                    r.get("publishedDate", "") or 
                    "Unknown"
                )[:10] if r.get("date") or r.get("datePublished") or r.get("publishedDate") else "Unknown"
                
                result = {
                    "title": r.get("title", "") or r.get("name", ""),
                    "link": r.get("url", "") or r.get("link", "") or r.get("uri", ""),
                    "score": 0,
                    "snippet": (r.get("summary", "") or r.get("description", "") or r.get("content", ""))[:400],
                    "creation_date": creation_date
                }
                formatted_results.append(result)
                
                print(f"--- Result {i} ---")
                print(f"Title: {result['title']}")
                print(f"Link: {result['link']}")
                print(f"Date: {result['creation_date']}")
                print(f"Snippet: {result['snippet'][:100]}...")
                print()
            
            print(f"\n✅ SUCCESS! Microsoft API is working.")
            print(f"   Total results: {len(results)}")
            print(f"   Showing first 5 above.")
            return formatted_results
            
        elif resp.status_code == 403:
            print(f"\n❌ BLOCKED (403 Forbidden)")
            print(f"   Microsoft is blocking automated requests.")
            return []
        elif resp.status_code == 404:
            print(f"\n❌ ENDPOINT NOT FOUND (404)")
            print(f"   The API endpoint may have changed.")
            return []
        elif resp.status_code == 400:
            print(f"\n❌ BAD REQUEST (400)")
            print(f"\n📄 Response text:")
            print(resp.text[:1000])
            return []
        else:
            print(f"\n⚠️ Unexpected status code: {resp.status_code}")
            print(f"\n📄 Response text:")
            print(resp.text[:1000])
            return []
            
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT: Request took too long (>15 seconds)")
        return []
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Cannot reach Microsoft servers")
        return []
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        return []

if __name__ == "__main__":
    print("="*60)
    print("MICROSOFT API TEST (CORRECTED)")
    print("="*60)
    print()
    
    # Test with a few different keywords
    test_keywords = [
        "JNI memory leak",
        "UnsatisfiedLinkError"
    ]
    
    for keyword in test_keywords:
        results = test_microsoft_qa_search(keyword)
        print("\n" + "="*60 + "\n")
        
        if results:
            print("✅ API IS WORKING - You can add this to scraper.py")
            break
        else:
            print("❌ API FAILED - Try alternative approaches")
            print()