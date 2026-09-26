import pandas as pd
import glob
import os

print("🔍 Loading combined data for Validation Protocol...\n")

# Find the latest combined CSV file
csv_files = glob.glob("output/COMBINED_final_report_*.csv")
if not csv_files:
    print("❌ No combined CSV found in the output/ folder!")
    exit()
latest_csv = max(csv_files, key=os.path.getctime)
df = pd.read_csv(latest_csv)

print(f"✅ Loaded {len(df)} raw posts from {latest_csv}\n")

# ============================================================
# THE VALIDATION PROTOCOL (From your methodology document)
# A post must pass at least 2 of these 3 checks:
# ============================================================

# Check 1: The "Two-Language" Test
TWO_LANG_WORDS = ['java', 'c++', 'c/c++', 'jni', 'ndk', 'jvm', 'native method', 'native code', 'c and java']

# Check 2: The "Boundary Error" Test
BOUNDARY_ERROR_WORDS = ['unsatisfiedlinkerror', 'sigsegv', 'sigabrt', 'hs_err', 'crash', 'core dump', 
                        'exceptionininitializererror', 'fatal error', 'segmentation fault']

# Check 3: The "Translation" Test
TRANSLATION_WORDS = ['marshaling', 'marshalling', 'struct padding', 'pointer', 'utf-8', 'modified utf-8', 
                     'jstring', 'jbytearray', 'memory ownership', 'pinning', 'deletelocalref', 'global reference']

def apply_validation_protocol(row):
    """Applies the 3-check validation protocol to a single row."""
    text = f"{row['title']} {row['snippet']}".lower()
    
    passed_checks = 0
    
    # Check 1
    if any(word in text for word in TWO_LANG_WORDS):
        passed_checks += 1
    # Check 2
    if any(word in text for word in BOUNDARY_ERROR_WORDS):
        passed_checks += 1
    # Check 3
    if any(word in text for word in TRANSLATION_WORDS):
        passed_checks += 1
        
    return passed_checks

# Apply the protocol to all rows
print("⚙️ Applying Validation Protocol to 578 posts...")
df['validation_score'] = df.apply(apply_validation_protocol, axis=1)

# ============================================================
# FILTERING & PRIORITIZING
# ============================================================

# Rule 1: Keep posts that passed at least 2 checks (Score >= 2)
df_strong_match = df[df['validation_score'] >= 2].copy()

# Rule 2: Keep posts that passed 1 check BUT had a very high original keyword match score
df_weak_but_relevant = df[(df['validation_score'] == 1) & (df['score'] >= 3)].copy()

# Combine and remove duplicates
df_final = pd.concat([df_strong_match, df_weak_but_relevant]).drop_duplicates(subset=['link'])

# Sort by Validation Score (desc), then Original Score (desc)
df_final = df_final.sort_values(by=['validation_score', 'score'], ascending=[False, False])

# Reset index
df_final = df_final.reset_index(drop=True)

# ============================================================
# EXPORT FOR YOUR BOSS
# ============================================================
output_path = "output/FILTERED_for_manual_review.csv"
df_final.to_csv(output_path, index=False)

print("\n" + "="*60)
print("✅ VALIDATION PROTOCOL COMPLETE!")
print("="*60)
print(f"📥 Raw posts collected:      {len(df)}")
print(f"🗑️ Filtered out (Noise):     {len(df) - len(df_final)}")
print(f"✅ Validated for Review:     {len(df_final)}")
print(f"\n📊 Breakdown of Validated Posts:")
print(f"   • Passed 3 checks (High Confidence): {len(df_final[df_final['validation_score'] == 3])}")
print(f"   • Passed 2 checks (Medium Confidence): {len(df_final[df_final['validation_score'] == 2])}")
print(f"   • Passed 1 check + High Keyword Match: {len(df_final[df_final['validation_score'] == 1])}")

print(f"\n💾 Ready for you and your boss!")
print(f"   Open this file: {output_path}")