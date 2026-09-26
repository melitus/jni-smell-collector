import argparse
import pandas as pd
import json
import os
from datetime import datetime
from config import (
    OUTPUT_DIR, 
    PHASE1_BASELINE_KEYWORDS, PHASE1_BASELINE_FORUMS,
    PHASE1_EXTENSION_KEYWORDS, PHASE1_EXTENSION_FORUMS,
    PHASE2_DOCUMENTATION_URLS,
    PHASE3_BASELINE_REPOS
)
from scraper import RealSmellCollector
from documentation_extractor import DocumentationExtractor
from source_code_analyzer import SourceCodeAnalyzer

def run_phase1_baseline():
    """Phase 1A: Baseline Forum Mining (matching paper exactly)"""
    print("\n" + "="*60)
    print("📋 PHASE 1A: Baseline Forum Mining")
    print("="*60)
    
    collector = RealSmellCollector()
    df = collector.run(
        phase_name="PHASE 1A: BASELINE FORUMS",
        forums=PHASE1_BASELINE_FORUMS,
        keywords=PHASE1_BASELINE_KEYWORDS
    )
    
    path = f"{OUTPUT_DIR}/phase1a_baseline_forums_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(path, index=False)
    print(f"\n💾 Phase 1A saved: {len(df)} results → {path}")
    return df

def run_phase1_extension():
    """Phase 1B: Extension Forum Mining (your contribution)"""
    print("\n" + "="*60)
    print("📋 PHASE 1B: Extension Forum Mining")
    print("="*60)
    
    collector = RealSmellCollector()
    df = collector.run(
        phase_name="PHASE 1B: EXTENSION FORUMS",
        forums=PHASE1_EXTENSION_FORUMS,
        keywords=PHASE1_EXTENSION_KEYWORDS
    )
    
    path = f"{OUTPUT_DIR}/phase1b_extension_forums_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(path, index=False)
    print(f"\n💾 Phase 1B saved: {len(df)} results → {path}")
    return df

def run_phase2():
    """Phase 2: Documentation Extraction"""
    print("\n" + "="*60)
    print("📋 PHASE 2: Documentation Extraction")
    print("="*60)
    
    extractor = DocumentationExtractor(PHASE2_DOCUMENTATION_URLS)
    patterns = extractor.extract_all_documentation()
    
    df = pd.DataFrame(patterns)
    path = f"{OUTPUT_DIR}/phase2_documentation_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(path, index=False)
    print(f"\n💾 Phase 2 saved: {len(df)} documentation patterns → {path}")
    return df

def run_phase3():
    """Phase 3: Source Code Analysis"""
    print("\n" + "="*60)
    print("📋 PHASE 3: Source Code Analysis")
    print("="*60)
    
    analyzer = SourceCodeAnalyzer(PHASE3_BASELINE_REPOS)
    analyzer.clone_repositories()
    findings = analyzer.analyze_all_repositories()
    
    df = pd.DataFrame(findings)
    path = f"{OUTPUT_DIR}/phase3_source_code_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(path, index=False)
    print(f"\n💾 Phase 3 saved: {len(df)} source code findings → {path}")
    return df

def run_triage():
    """Apply Validation Protocol"""
    print("\n" + "="*60)
    print("📋 TRIAGE: Applying Validation Protocol")
    print("="*60)
    
    import glob
    csv_files = glob.glob(f"{OUTPUT_DIR}/phase1*_forums_*.csv")
    if not csv_files:
        print("❌ No forum data found! Run Phase 1 first.")
        return
    
    latest_csv = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_csv)
    print(f"✅ Loaded {len(df)} raw posts from {latest_csv}\n")
    
    # Validation Protocol
    TWO_LANG_WORDS = ['java', 'c++', 'jni', 'ndk', 'jvm', 'native']
    BOUNDARY_ERROR_WORDS = ['unsatisfiedlinkerror', 'sigsegv', 'crash', 'hs_err']
    TRANSLATION_WORDS = ['marshaling', 'pointer', 'utf-8', 'jstring', 'deletelocalref']
    
    def validate(row):
        text = f"{row.get('title', '')} {row.get('snippet', '')}".lower()
        score = 0
        if any(w in text for w in TWO_LANG_WORDS): score += 1
        if any(w in text for w in BOUNDARY_ERROR_WORDS): score += 1
        if any(w in text for w in TRANSLATION_WORDS): score += 1
        return score
    
    print("⚙️ Applying Validation Protocol...")
    df['validation_score'] = df.apply(validate, axis=1)
    
    df_filtered = df[df['validation_score'] >= 2].copy()
    df_filtered = df_filtered.sort_values('validation_score', ascending=False)
    
    path = f"{OUTPUT_DIR}/FILTERED_for_manual_review_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df_filtered.to_csv(path, index=False)
    
    print(f"\n✅ TRIAGE COMPLETE!")
    print(f"   Raw: {len(df)}")
    print(f"   Filtered: {len(df_filtered)}")
    print(f"   💾 Saved to: {path}")

def run_summary():
    """Generate summary"""
    print("\n" + "="*60)
    print("📊 GENERATING SUMMARY")
    print("="*60)
    
    import glob
    
    summary = {}
    
    phase1a_files = glob.glob(f"{OUTPUT_DIR}/phase1a_baseline_forums_*.csv")
    if phase1a_files:
        df = pd.read_csv(max(phase1a_files, key=os.path.getctime))
        summary['phase1a_baseline'] = len(df)
    
    phase1b_files = glob.glob(f"{OUTPUT_DIR}/phase1b_extension_forums_*.csv")
    if phase1b_files:
        df = pd.read_csv(max(phase1b_files, key=os.path.getctime))
        summary['phase1b_extension'] = len(df)
    
    phase2_files = glob.glob(f"{OUTPUT_DIR}/phase2_documentation_*.csv")
    if phase2_files:
        df = pd.read_csv(max(phase2_files, key=os.path.getctime))
        summary['phase2_documentation'] = len(df)
    
    phase3_files = glob.glob(f"{OUTPUT_DIR}/phase3_source_code_*.csv")
    if phase3_files:
        df = pd.read_csv(max(phase3_files, key=os.path.getctime))
        summary['phase3_source_code'] = len(df)
    
    summary['total'] = sum(summary.values())
    
    path = f"{OUTPUT_DIR}/collection_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n✅ SUMMARY:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    print(f"\n📁 Saved to: {path}")

def main():
    parser = argparse.ArgumentParser(
        description="JNI Design Smell Collection Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --phase 1a          # Baseline forums
  python main.py --phase 1b          # Extension forums
  python main.py --phase 1           # Both 1a and 1b
  python main.py --phase 2           # Documentation extraction
  python main.py --phase 3           # Source code analysis
  python main.py --phase all         # All phases
  python main.py --phase triage      # Filter results
  python main.py --phase summary     # Generate summary
        """
    )
    
    parser.add_argument(
        '--phase',
        type=str,
        required=True,
        choices=['1a', '1b', '1', '2', '3', 'all', 'triage', 'summary'],
        help='Phase to run'
    )
    
    args = parser.parse_args()
    
    print("🚀 JNI Design Smell Collection")
    print(f"📁 Output: {OUTPUT_DIR}")
    
    if args.phase == '1a':
        run_phase1_baseline()
    elif args.phase == '1b':
        run_phase1_extension()
    elif args.phase == '1':
        run_phase1_baseline()
        run_phase1_extension()
    elif args.phase == '2':
        run_phase2()
    elif args.phase == '3':
        run_phase3()
    elif args.phase == 'all':
        run_phase1_baseline()
        run_phase1_extension()
        run_phase2()
        run_phase3()
        run_summary()
    elif args.phase == 'triage':
        run_triage()
    elif args.phase == 'summary':
        run_summary()

if __name__ == "__main__":
    main()