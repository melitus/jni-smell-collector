"""
Analyze re-mined CSV files: total posts, date range, Pre/Post GenAI split
Usage: python3 scripts/analyze_remined.py <csv_file>
"""

import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

GENAI_CUTOFF = "2022-11-30"  # ChatGPT launch date


def analyze_csv(csv_path):
    """Analyze a re-mined CSV file and print statistics."""
    df = pd.read_csv(csv_path)

    print(f"\n{'='*60}")
    print(f"📊 ANALYSIS: {Path(csv_path).name}")
    print(f"{'='*60}")

    # Basic stats
    print(f"\nTotal posts: {len(df)}")
    print(f"Date range: {df['creation_date'].min()} to {df['creation_date'].max()}")
    print(f"Unique dates: {df['creation_date'].nunique()}")

    # Pre/Post GenAI split
    pre = df[df['creation_date'] <= GENAI_CUTOFF]
    post = df[df['creation_date'] > GENAI_CUTOFF]

    print(f"\n--- GenAI Split (cutoff: {GENAI_CUTOFF}) ---")
    print(f"Pre-GenAI  (≤ {GENAI_CUTOFF}): {len(pre)} posts ({len(pre)/len(df)*100:.1f}%)")
    print(f"Post-GenAI (> {GENAI_CUTOFF}):  {len(post)} posts ({len(post)/len(df)*100:.1f}%)")

    # Posts by year
    df['year'] = df['creation_date'].str[:4]
    print(f"\n--- Posts by Year ---")
    for year, count in df['year'].value_counts().sort_index().items():
        print(f"  {year}: {count}")

    # Top keywords
    if 'keyword' in df.columns:
        print(f"\n--- Top 10 Keywords ---")
        for kw, count in df['keyword'].value_counts().head(10).items():
            print(f"  {kw}: {count}")

    # Score stats (if available)
    if 'score' in df.columns:
        print(f"\n--- Score Statistics ---")
        print(f"  Average: {df['score'].mean():.1f}")
        print(f"  Median:  {df['score'].median():.0f}")
        print(f"  Min:     {df['score'].min()}")
        print(f"  Max:     {df['score'].max()}")

    print(f"\n{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/analyze_remined.py <csv_file>")
        print("\nAvailable CSV files in output/:")
        for f in Path("output").glob("*_remined_*.csv"):
            print(f"  {f.name}")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    analyze_csv(csv_path)


if __name__ == "__main__":
    main()