"""
Phase 1 Task 5: Generate Master Spreadsheet
Combine all results into a single Excel file matching professor's table structure.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1"

# Search criteria definitions (from config/search_criteria.yaml)
SEARCH_CRITERIA = {
    "Stack Overflow": {
        "technique": "Hybrid (Tags + Keywords)",
        "keywords": "JNI, Java Native Interface, UnsatisfiedLinkError",
        "tags": "java-native-interface, jni, jniwrapper, jna",
        "inclusion": "Keywords OR Tags present; Body >= 100 chars",
        "exclusion": "Closed/deleted; Duplicates; Non-Java tags only",
    },
    "GitHub Issues": {
        "technique": "Term-based + Repo filter",
        "keywords": "JNI, native method, Java Native Interface",
        "tags": "N/A",
        "inclusion": "Keywords in title/body; Repo has Java + C/C++; Not a PR",
        "exclusion": "Build config only; Duplicates; Labeled 'invalid'",
    },
    "Reddit": {
        "technique": "Term-based + Subreddit filter",
        "keywords": "JNI, native code, Java Native Interface",
        "tags": "N/A",
        "inclusion": "Keywords present; In r/java, r/androiddev, r/programming",
        "exclusion": "Memes; NDK build only; < 3 comments",
    },
    "Hacker News": {
        "technique": "Term-based",
        "keywords": "JNI, Java Native Interface, native interop",
        "tags": "N/A",
        "inclusion": "Keywords present; Points >= 5; Comments >= 10",
        "exclusion": "Job listings; JVM-only; Off-topic",
    },
    "LLVM Discourse": {
        "technique": "Term-based + Category filter",
        "keywords": "JNI, Java, FFI, native interop",
        "tags": "N/A",
        "inclusion": "Keywords present; In Development/Users/LLVM categories",
        "exclusion": "LLVM IR only; Meeting announcements",
    },
    "Apache Lists": {
        "technique": "Term-based + Project filter",
        "keywords": "JNI, native, Java Native Interface",
        "tags": "N/A",
        "inclusion": "Keywords present; In hadoop/spark/kafka/flink lists",
        "exclusion": "Commit notifications; Maven/Gradle only",
    },
    "Bugzilla": {
        "technique": "Term-based + Component filter",
        "keywords": "JNI, native, Java",
        "tags": "N/A",
        "inclusion": "Keywords present; Status not INVALID/DUPLICATE",
        "exclusion": "UI/frontend only; Duplicates; No description",
    },
    "Microsoft Q&A": {
        "technique": "Term-based + Category filter",
        "keywords": "JNI, Java Native Interface, interop",
        "tags": "N/A",
        "inclusion": "Keywords present; In Java/Android/Cross-platform categories",
        "exclusion": ".NET-only; Product announcements; Closed without resolution",
    },
    "Oracle Community": {
        "technique": "Term-based + Forum filter",
        "keywords": "JNI, Java Native Interface, native method",
        "tags": "N/A",
        "inclusion": "Keywords present; In Java SE/Java Development forums",
        "exclusion": "Database-only; Product announcements; Duplicates",
    },
    "Lobsters": {
        "technique": "Term-based",
        "keywords": "JNI, native interop, FFI",
        "tags": "N/A",
        "inclusion": "Keywords present; Points >= 3; Comments >= 5",
        "exclusion": "Off-topic; JVM-only",
    },
    "Quora": {
        "technique": "Term-based + Manual expert-credential filtering",
        "keywords": "JNI, Java Native Interface, JNA",
        "tags": "N/A",
        "inclusion": "Keywords present; Architectural focus; Expert credentials",
        "exclusion": "Career advice; Beginner questions; Spam; Pure Java/C++",
    },
}


def generate_master_spreadsheet():
    """Generate the master spreadsheet matching professor's table structure."""

    # Load individual results
    forum_dist = pd.read_csv(RESULTS_DIR / "forum_distribution.csv")
    temporal_summary = pd.read_csv(RESULTS_DIR / "temporal_split_summary.csv")

    # Merge data
    master_data = []

    for _, row in forum_dist.iterrows():
        forum_name = row["forum_name"]

        # Get temporal data for this forum
        temporal_row = temporal_summary[temporal_summary["forum"] == forum_name]
        if not temporal_row.empty:
            pre_genai = int(temporal_row["Pre-GenAI"].values[0])
            post_genai = int(temporal_row["Post-GenAI"].values[0])
            total = int(temporal_row["Total"].values[0])
        else:
            pre_genai = 0
            post_genai = 0
            total = int(row["total_posts"])

        # Get search criteria
        criteria = SEARCH_CRITERIA.get(forum_name, {})

        master_data.append({
            "Forum Used for topic Search": forum_name,
            "Identification Technique (Rules)": criteria.get("technique", "Unknown"),
            "Pre Gen of AI": pre_genai,
            "Post Gen AI": post_genai,
            "Post Get": int(row["total_posts"]),
            "Inclusion Criteria": criteria.get("inclusion", "Unknown"),
            "Exclusion Criteria": criteria.get("exclusion", "Unknown"),
            "Total Post": total,
            "Time Period": row["time_period"],
            "Keywords": criteria.get("keywords", ""),
            "Tags": criteria.get("tags", ""),
        })

    df = pd.DataFrame(master_data)

    # Save to Excel
    output_path = RESULTS_DIR / "phase1_master_spreadsheet.xlsx"

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Master Summary")

        # Auto-adjust column widths
        worksheet = writer.sheets["Master Summary"]
        for column in worksheet.columns:
            max_length = min(max(len(str(cell.value or "")) for cell in column) + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = max_length

    # Also save as CSV
    csv_path = RESULTS_DIR / "phase1_master_spreadsheet.csv"
    df.to_csv(csv_path, index=False)

    print(f"\nMaster Spreadsheet Summary:")
    print(df.to_string(index=False))
    print(f"\nSaved to {output_path}")
    print(f"Also saved to {csv_path}")

    return df


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating master spreadsheet...")
    df = generate_master_spreadsheet()

    return df


if __name__ == "__main__":
    main()