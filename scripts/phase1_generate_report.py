"""
Phase 1 Task 2: Search Criteria Documentation
Generate search criteria summary from config file.
"""

import yaml
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1"


def generate_search_criteria() -> pd.DataFrame:
    """Generate search criteria summary from config."""
    config_path = CONFIG_DIR / "search_criteria.yaml"

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    results = []

    for forum_key, forum_config in config["forums"].items():
        results.append({
            "forum_name": forum_key.replace("_", " ").title(),
            "search_type": forum_config["search_type"],
            "keywords": ", ".join(forum_config.get("keywords", [])),
            "tags": ", ".join(forum_config.get("tags", [])) or "N/A",
            "filters": "; ".join(forum_config.get("filters", [])) or "N/A",
            "api_endpoint": forum_config.get("api_endpoint", "Manual"),
            "justification": forum_config.get("justification", ""),
        })

    return pd.DataFrame(results)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating search criteria documentation...")
    df = generate_search_criteria()

    output_path = RESULTS_DIR / "search_criteria.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSearch Criteria Summary:")
    print(df.to_string(index=False))
    print(f"\nSaved to {output_path}")

    return df


if __name__ == "__main__":
    main()