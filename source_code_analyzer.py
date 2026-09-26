import os
import subprocess
import re
from typing import List, Dict
import json

class SourceCodeAnalyzer:
    """Analyzes actual source code for JNI anti-patterns (matching paper methodology)."""
    
    def __init__(self, baseline_repos: List[str], repos_dir: str = "/tmp/jni_repos"):
        self.baseline_repos = baseline_repos
        self.repos_dir = repos_dir
        os.makedirs(self.repos_dir, exist_ok=True)
        
        # JNI anti-patterns to search for in code
        self.code_patterns = {
            "Missing DeleteLocalRef": r"NewLocalRef|NewObject|NewStringUTF(?!.*DeleteLocalRef)",
            "Global Reference Hoarding": r"NewGlobalRef(?!.*DeleteGlobalRef)",
            "Unchecked JNI Exceptions": r"Call[A-Z].*Method(?!.*ExceptionCheck)",
            "Unsafe String Handling": r"GetStringUTFChars(?!.*ReleaseStringUTFChars)",
            "Unsafe Array Handling": r"Get[A-Z].*ArrayElements(?!.*Release)",
            "Missing extern C": r"JNIEXPORT.*JNICALL(?!.*extern\s+\"C\")",
        }
    
    def clone_repositories(self):
        """Clone all baseline repositories."""
        print("\n" + "="*60)
        print("📦 CLONING BASELINE REPOSITORIES")
        print("="*60 + "\n")
        
        for repo_url in self.baseline_repos:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.repos_dir, repo_name)
            
            if os.path.exists(repo_path):
                print(f"✓ {repo_name} already exists, skipping clone.")
                continue
            
            print(f"Cloning {repo_name}...")
            try:
                # --depth 1 makes it much faster by only downloading the latest commit
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, repo_path],
                    check=True,
                    capture_output=True,
                    timeout=120
                )
                print(f"✅ Cloned {repo_name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone {repo_name}: {e}")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Timeout cloning {repo_name}")
    
    def analyze_repository(self, repo_path: str) -> List[Dict]:
        """Analyze a single repository for JNI anti-patterns."""
        findings = []
        repo_name = os.path.basename(repo_path)
        
        # Find all C/C++ and Java files
        c_files = []
        java_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory to save time
            if '.git' in root:
                continue
            
            for file in files:
                if file.endswith(('.c', '.cpp', '.cc', '.h', '.hpp')):
                    c_files.append(os.path.join(root, file))
                elif file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        # Analyze C/C++ files for JNI patterns
        for c_file in c_files:
            try:
                with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern_name, regex in self.code_patterns.items():
                        matches = re.finditer(regex, content, re.MULTILINE | re.IGNORECASE)
                        for match in matches:
                            # Get surrounding context (50 chars before and after)
                            start = max(0, match.start() - 50)
                            end = min(len(content), match.end() + 50)
                            context = content[start:end].replace('\n', ' ').strip()
                            
                            findings.append({
                                "repository": repo_name,
                                "file": c_file.replace(repo_path, ''),
                                "pattern": pattern_name,
                                "context": context,
                                "type": "source_code"
                            })
            except Exception as e:
                # Ignore files that can't be read (e.g., binary files mislabeled as text)
                pass
        
        return findings
    
    def analyze_all_repositories(self) -> List[Dict]:
        """Analyze all cloned repositories."""
        print("\n" + "="*60)
        print("🔍 ANALYZING SOURCE CODE FOR JNI ANTI-PATTERNS")
        print("="*60 + "\n")
        
        all_findings = []
        
        for repo_url in self.baseline_repos:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.repos_dir, repo_name)
            
            if not os.path.exists(repo_path):
                print(f"⚠️ {repo_name} not found, skipping analysis.")
                continue
            
            print(f"Analyzing {repo_name}...")
            findings = self.analyze_repository(repo_path)
            all_findings.extend(findings)
            print(f"  ✅ Found {len(findings)} potential anti-patterns in {repo_name}")
        
        return all_findings

if __name__ == "__main__":
    # Test with the repos from config
    from config import PHASE3_BASELINE_REPOS
    
    analyzer = SourceCodeAnalyzer(PHASE3_BASELINE_REPOS)
    
    # Step 1: Clone repositories
    analyzer.clone_repositories()
    
    # Step 2: Analyze source code
    findings = analyzer.analyze_all_repositories()
    
    # Save results
    with open("output/source_code_findings.json", "w") as f:
        json.dump(findings, f, indent=2)
    
    print(f"\n💾 Saved {len(findings)} source code findings")
    
    # Summary by pattern
    pattern_counts = {}
    for finding in findings:
        pattern = finding['pattern']
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print("\n📊 Summary by Anti-Pattern:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count} occurrences")