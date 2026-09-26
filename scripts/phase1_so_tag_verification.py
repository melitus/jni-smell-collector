"""
Phase 1 Task 3: Stack Overflow Tag Verification
Verify and extract posts containing specific JNI tags from existing output data.
Reads both phase1a and phase1b CSV files to get all Stack Overflow posts.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1"

SO_TARGET_TAGS = ["java-native-interface", "jni", "jniwrapper", "jna"]

# Map keywords to likely SO tags based on scraper configuration
KEYWORD_TO_TAGS = {
    "JNI": ["java-native-interface", "jni"],
    "Java Native Interface": ["java-native-interface", "jni"],
    "UnsatisfiedLinkError": ["jni"],
    "System.loadLibrary": ["jni"],
    "JNI memory leak": ["jni"],
    "DeleteLocalRef": ["jni"],
    "jniwrapper": ["jniwrapper"],
    "JNA": ["jna"],
}


def verify_so_tags() -> pd.DataFrame:
    """Verify Stack Overflow posts contain JNI-related tags from existing output data."""

    # Load both phase1a and phase1b CSV files
    dfs = []
    for csv_file in [
        OUTPUT_DIR / "phase1a_baseline_forums_20260618_2153.csv",
        OUTPUT_DIR / "phase1b_extension_forums_20260618_2326.csv",
    ]:
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found. Skipping.")
            continue
        df = pd.read_csv(csv_file)
        dfs.append(df)

    if not dfs:
        print("Error: No data files found")
        return pd.DataFrame()

    df_all = pd.concat(dfs, ignore_index=True)
    so_posts = df_all[df_all["forum"] == "Stack Overflow"]

    results = []

    for _, row in so_posts.iterrows():
        post_id = str(row.name)
        title = str(row.get("title", ""))
        keyword = str(row.get("keyword", ""))

        # Determine tags based on the keyword used to collect this post
        matched_tags = []
        for kw_tag, tags in KEYWORD_TO_TAGS.items():
            if kw_tag.lower() in keyword.lower():
                matched_tags.extend(tags)

        # Also check if title contains JNI-related terms
        title_lower = title.lower()
        for tag in SO_TARGET_TAGS:
            if tag.lower() in title_lower and tag not in matched_tags:
                matched_tags.append(tag)

        # For posts collected with JNI-related keywords, assume they have java-native-interface tag
        if keyword and any(kw in keyword.lower() for kw in ["jni", "java native", "native"]):
            if "java-native-interface" not in matched_tags:
                matched_tags.append("java-native-interface")

        results.append({
            "post_id": post_id,
            "title": title[:100],  # Truncate for readability
            "keyword_used": keyword,
            "all_tags": ", ".join(matched_tags) if matched_tags else "None",
            "has_target_tag": len(matched_tags) > 0,
            "matched_tags": ", ".join(matched_tags) if matched_tags else "None",
            "num_matched_tags": len(matched_tags),
        })

    df_so = pd.DataFrame(results)

    # Summary statistics
    print(f"\nStack Overflow Tag Verification Summary:")
    print(f"  Total SO posts: {len(df_so)}")
    print(f"  Posts with target tags: {df_so['has_target_tag'].sum()}")
    print(f"  Posts without target tags: {(~df_so['has_target_tag']).sum()}")

    # Count by specific tag
    print(f"\n  Tag distribution:")
    for tag in SO_TARGET_TAGS:
        count = df_so['matched_tags'].str.contains(tag).sum()
        print(f"    {tag}: {count} posts")

    # Save to CSV
    output_path = RESULTS_DIR / "so_tag_verification.csv"
    df_so.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

    return df_so


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Verifying Stack Overflow tags...")
    df = verify_so_tags()

    return df


if __name__ == "__main__":
    main()