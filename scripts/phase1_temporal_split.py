"""
Phase 1 Task 4: Temporal Split
Divide existing posts into Pre-GenAI and Post-GenAI cohorts based on creation timestamp.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1"
TEMPORAL_DIR = RESULTS_DIR / "temporal_split"

GENAI_CUTOFF_DATE = datetime(2022, 11, 30)  # ChatGPT launch date


def load_all_posts():
    """Load all posts from existing output CSV files."""
    all_posts = []

    csv_files = [
        OUTPUT_DIR / "phase1a_baseline_forums_20260618_2153.csv",
        OUTPUT_DIR / "phase1b_extension_forums_20260618_2326.csv",
    ]

    for csv_file in csv_files:
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found. Skipping.")
            continue

        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            post = {
                "forum": row.get("forum", "Unknown"),
                "post_id": str(row.name),  # Use row index as ID
                "title": str(row.get("title", ""))[:100],
                "creation_date": str(row.get("creation_date", "")),
            }
            all_posts.append(post)

    return all_posts


def parse_date(date_str):
    """Parse a date string and return a datetime object."""
    if not date_str or date_str == "Unknown":
        return None

    # Remove leading '19' or '20' if date starts with single digit (common in CSV parsing)
    if len(date_str) >= 10:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            pass

    # Try other common formats
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(date_str[:19], fmt)
        except ValueError:
            continue

    return None


def temporal_split():
    """Split all posts into Pre-GenAI and Post-GenAI cohorts."""
    TEMPORAL_DIR.mkdir(parents=True, exist_ok=True)

    posts = load_all_posts()

    pre_genai_posts = []
    post_genai_posts = []

    for post in posts:
        post_date = parse_date(post["creation_date"])

        if post_date is None:
            continue

        # Add metadata
        post_record = {
            "forum": post["forum"],
            "post_id": post["post_id"],
            "title": post["title"],
            "creation_date": post_date.strftime("%Y-%m-%d"),
            "era": "Pre-GenAI" if post_date < GENAI_CUTOFF_DATE else "Post-GenAI",
        }

        if post_date < GENAI_CUTOFF_DATE:
            pre_genai_posts.append(post_record)
        else:
            post_genai_posts.append(post_record)

    pre_df = pd.DataFrame(pre_genai_posts)
    post_df = pd.DataFrame(post_genai_posts)

    # Save to CSV
    pre_df.to_csv(TEMPORAL_DIR / "pre_genai_posts.csv", index=False)
    post_df.to_csv(TEMPORAL_DIR / "post_genai_posts.csv", index=False)

    print(f"\nTemporal Split Summary:")
    print(f"  Pre-GenAI posts: {len(pre_df)}")
    print(f"  Post-GenAI posts: {len(post_df)}")
    print(f"  Total posts: {len(pre_df) + len(post_df)}")
    print(f"  Cutoff date: {GENAI_CUTOFF_DATE.strftime('%Y-%m-%d')}")

    return pre_df, post_df


def generate_temporal_summary(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary by forum and era."""
    all_posts = pd.concat([pre_df, post_df], ignore_index=True)

    if len(all_posts) == 0:
        return pd.DataFrame(columns=["forum", "Pre-GenAI", "Post-GenAI", "Total"])

    summary = all_posts.groupby(["forum", "era"]).size().unstack(fill_value=0)
    summary["Total"] = summary.sum(axis=1)
    summary = summary.reset_index()

    # Ensure both columns exist
    if "Pre-GenAI" not in summary.columns:
        summary["Pre-GenAI"] = 0
    if "Post-GenAI" not in summary.columns:
        summary["Post-GenAI"] = 0

    return summary[["forum", "Pre-GenAI", "Post-GenAI", "Total"]]


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Performing temporal split...")
    pre_df, post_df = temporal_split()

    print("\nGenerating temporal summary by forum...")
    summary = generate_temporal_summary(pre_df, post_df)

    output_path = RESULTS_DIR / "temporal_split_summary.csv"
    summary.to_csv(output_path, index=False)

    print(f"\nTemporal Split by Forum:")
    print(summary.to_string(index=False))
    print(f"\nSaved to {output_path}")

    return summary


if __name__ == "__main__":
    main()