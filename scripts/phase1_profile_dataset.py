"""
Phase 1 Task 1: Forum Distribution
Count posts per forum from existing output CSV data and generate distribution summary.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1"


def load_posts_from_output():
    """Load posts from existing output CSV files."""
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
                "title": str(row.get("title", "")),
                "creation_date": str(row.get("creation_date", "")),
                "forum": row.get("forum", "Unknown"),
                "keyword": str(row.get("keyword", "")),
                "score": row.get("score", 0),
            }
            all_posts.append(post)

    return all_posts


def generate_forum_distribution() -> pd.DataFrame:
    """Generate forum distribution summary from existing output data."""
    posts = load_posts_from_output()

    # Get unique forums
    forums = list(set(p["forum"] for p in posts if p["forum"] != "Unknown"))

    results = []

    for forum_name in forums:
        forum_posts = [p for p in posts if p["forum"] == forum_name]

        # Count posts with valid dates
        valid_posts = 0
        date_range_start = None
        date_range_end = None

        for post in forum_posts:
            date_str = post["creation_date"]
            # Skip "Unknown" dates
            if date_str == "Unknown" or not date_str:
                continue
            try:
                # Try to parse the date
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d") if len(date_str) >= 10 else None
                if dt:
                    valid_posts += 1
                    if date_range_start is None or date_str < date_range_start:
                        date_range_start = date_str
                    if date_range_end is None or date_str > date_range_end:
                        date_range_end = date_str
            except ValueError:
                continue

        if date_range_start is None:
            date_range_start = "Unknown"
        if date_range_end is None:
            date_range_end = "Unknown"

        results.append({
            "forum_name": forum_name,
            "total_posts": len(forum_posts),
            "posts_with_valid_dates": valid_posts,
            "earliest_post": date_range_start,
            "latest_post": date_range_end,
            "time_period": f"{date_range_start} to {date_range_end}",
        })

    return pd.DataFrame(results)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating forum distribution...")
    df = generate_forum_distribution()

    # Save to CSV
    output_path = RESULTS_DIR / "forum_distribution.csv"
    df.to_csv(output_path, index=False)

    print(f"\nForum Distribution Summary:")
    print(df.to_string(index=False))
    print(f"\nSaved to {output_path}")

    return df


if __name__ == "__main__":
    main()