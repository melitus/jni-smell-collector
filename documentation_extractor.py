import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict

class DocumentationExtractor:
    """Extracts JNI anti-patterns from official documentation (matching paper methodology)."""
    
    def __init__(self, urls: List[Dict]):
        self.urls = urls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        })
    
    def extract_from_url(self, url: str, source_name: str) -> List[Dict]:
        """Extract anti-patterns from a single documentation URL."""
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"❌ Failed to fetch {source_name}: HTTP {resp.status_code}")
                return []
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            content = soup.get_text()
            
            anti_patterns = []
            
            patterns_to_find = [
                ("Exception handling", r"(?i)(exception|error|throw).{0,150}(jni|native)"),
                ("Memory management", r"(?i)(memory|leak|free|allocat|release).{0,150}(jni|global|local)"),
                ("String handling", r"(?i)(string|utf|char).{0,150}(jni|native|encode)"),
                ("Thread safety", r"(?i)(thread|concurrent|sync|attach).{0,150}(jni|native)"),
                ("Performance", r"(?i)(performance|slow|overhead|critical).{0,150}(jni|native)"),
                ("Formal JNI Rules", r"(?i)(native method|JNI function|DeleteLocalRef|NewGlobalRef).{0,150}(must|should|require)"),
            ]
                        
            for pattern_name, regex in patterns_to_find:
                matches = re.finditer(regex, content)
                for match in matches:
                    context = match.group(0)
                    anti_patterns.append({
                        "source": source_name,
                        "url": url,
                        "category": pattern_name,
                        "context": context[:300].replace('\n', ' '),
                        "type": "documentation",
                        "creation_date": "N/A"  # Documentation doesn't have post dates
                    })
            
            print(f"✅ {source_name}: Extracted {len(anti_patterns)} potential anti-patterns")
            return anti_patterns
            
        except Exception as e:
            print(f"❌ Error extracting {source_name}: {e}")
            return []
    
    def extract_all_documentation(self) -> List[Dict]:
        """Extract from all official documentation sources."""
        print("\n" + "="*60)
        print("📖 EXTRACTING FROM OFFICIAL DOCUMENTATION")
        print("="*60 + "\n")
        
        all_patterns = []
        for doc in self.urls:
            name = doc.get("name", "Unknown Source")
            url = doc.get("url", "")
            print(f"🔍 Processing: {name}")
            patterns = self.extract_from_url(url, name)
            all_patterns.extend(patterns)
            
        return all_patterns

if __name__ == "__main__":
    from config import PHASE2_DOCUMENTATION_URLS
    
    extractor = DocumentationExtractor(PHASE2_DOCUMENTATION_URLS)
    patterns = extractor.extract_all_documentation()
    
    with open("output/documentation_anti_patterns.json", "w") as f:
        json.dump(patterns, f, indent=2)
    
    print(f"\n💾 Saved {len(patterns)} documentation-based anti-patterns")