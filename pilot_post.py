"""
Fetch 5 Stack Overflow posts WITH inclusion/exclusion criteria applied.
"""

import requests
import pandas as pd
import html2text
import time
from datetime import datetime

API_BASE = "https://api.stackexchange.com/2.3"
SITE = "stackoverflow"
TAGS = "java-native-interface;jni"  # Multiple tags
NUM_POSTS = 5
FETCH_EXTRA = 10  # Fetch more to account for filtering

# Inclusion criteria (from your spreadsheet)
INCLUSION_RULES = {
    "keywords": ["JNI", "Java Native Interface"],
    "tags": ["java-native-interface", "jni", "jniwrapper", "jna"],
    "min_length": 100,
}

# Exclusion criteria (pilot version - lenient)
EXCLUSION_RULES_PILOT = {
    "min_score": -5,
    "allow_closed": True,
    "allow_duplicates": True,
}


def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(html_content).strip()


def passes_inclusion(question: dict) -> tuple[bool, str]:
    """Check if post meets inclusion criteria. Returns (passes, reason)."""
    title = question.get("title", "").lower()
    body = question.get("body", "").lower()
    tags = question.get("tags", [])
    
    # Rule 1: Keywords OR tags
    has_keyword = any(kw.lower() in title or kw.lower() in body 
                      for kw in INCLUSION_RULES["keywords"])
    has_tag = any(tag in tags for tag in INCLUSION_RULES["tags"])
    
    if not (has_keyword or has_tag):
        return False, "No relevant keywords or tags"
    
    # Rule 2: Minimum length
    if len(body) < INCLUSION_RULES["min_length"]:
        return False, f"Body too short ({len(body)} < {INCLUSION_RULES['min_length']})"
    
    return True, "Passes inclusion"


def passes_exclusion_pilot(question: dict) -> tuple[bool, str]:
    """Pilot version: lenient exclusions. Returns (passes, reason)."""
    title = question.get("title", "").lower()
    score = question.get("score", 0)
    
    # Exclude job posts
    if "job" in title and "hiring" in title:
        return False, "Job posting"
    
    # Exclude very low scores
    if score < EXCLUSION_RULES_PILOT["min_score"]:
        return False, f"Score too low ({score} < {EXCLUSION_RULES_PILOT['min_score']})"
    
    return True, "Passes exclusion"


def fetch_questions_filtered(tags: str, num_posts: int) -> list[dict]:
    """Fetch questions and apply inclusion/exclusion criteria."""
    url = f"{API_BASE}/questions"
    
    # Fetch more than needed to account for filtering
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": tags,
        "site": SITE,
        "pagesize": num_posts * 2,  # Fetch double
        "filter": "withbody",
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    all_questions = data.get("items", [])
    
    # Apply criteria
    filtered = []
    excluded_log = []
    
    for question in all_questions:
        # Check inclusion
        inc_passes, inc_reason = passes_inclusion(question)
        if not inc_passes:
            excluded_log.append({
                "title": question.get("title", "")[:50],
                "reason": f"INCLUSION: {inc_reason}"
            })
            continue
        
        # Check exclusion
        exc_passes, exc_reason = passes_exclusion_pilot(question)
        if not exc_passes:
            excluded_log.append({
                "title": question.get("title", "")[:50],
                "reason": f"EXCLUSION: {exc_reason}"
            })
            continue
        
        # Passes both criteria
        filtered.append(question)
        
        if len(filtered) >= num_posts:
            break
    
    print(f"\n📊 Filtering Summary:")
    print(f"  Fetched: {len(all_questions)} posts")
    print(f"  Excluded: {len(excluded_log)} posts")
    print(f"  Passed criteria: {len(filtered)} posts")
    
    if excluded_log:
        print(f"\n❌ Excluded posts (first 3):")
        for item in excluded_log[:3]:
            print(f"  - {item['title']}: {item['reason']}")
    
    return filtered


def fetch_answers(question_id: int) -> tuple[str, list[str]]:
    """Fetch all answers for a question."""
    url = f"{API_BASE}/questions/{question_id}/answers"
    params = {"site": SITE, "filter": "withbody", "sort": "votes"}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        answers = data.get("items", [])
        
        accepted_answer = ""
        all_answers_text = []
        
        for answer in answers:
            body = clean_html(answer.get("body", ""))
            author = answer.get("owner", {}).get("display_name", "Unknown")
            score = answer.get("score", 0)
            is_accepted = answer.get("is_accepted", False)
            
            answer_text = f"[{author}] (Score: {score})\n{body}"
            all_answers_text.append(answer_text)
            
            if is_accepted:
                accepted_answer = answer_text
        
        return accepted_answer, all_answers_text
        
    except Exception as e:
        print(f"Warning: Could not fetch answers: {e}")
        return "", []


def fetch_comments(post_id: int, post_type: str = "questions") -> list[str]:
    """Fetch comments for a question or answer."""
    url = f"{API_BASE}/{post_type}/{post_id}/comments"
    params = {"site": SITE, "filter": "withbody"}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        comments = []
        for comment in data.get("items", []):
            body = clean_html(comment.get("body", ""))
            author = comment.get("owner", {}).get("display_name", "Unknown")
            comments.append(f"[{author}]: {body}")
        
        return comments
        
    except Exception as e:
        print(f"Warning: Could not fetch comments: {e}")
        return []


def build_post_record(question: dict) -> dict:
    """Build complete record with criteria tracking."""
    question_id = question["question_id"]
    
    title = clean_html(question.get("title", ""))
    body = clean_html(question.get("body", ""))
    tags = question.get("tags", [])
    score = question.get("score", 0)
    creation_date = datetime.fromtimestamp(
        question.get("creation_date", 0)
    ).strftime("%Y-%m-%d")
    
    # Check criteria (for documentation)
    inc_passes, inc_reason = passes_inclusion(question)
    exc_passes, exc_reason = passes_exclusion_pilot(question)
    
    accepted_answer, all_answers = fetch_answers(question_id)
    
    question_comments = fetch_comments(question_id, "questions")
    all_comments = question_comments.copy()
    
    try:
        answers_data = requests.get(
            f"{API_BASE}/questions/{question_id}/answers",
            params={"site": SITE, "filter": "withbody"},
            timeout=30
        ).json().get("items", [])
        
        for answer in answers_data:
            answer_comments = fetch_comments(answer["answer_id"], "answers")
            all_comments.extend(answer_comments)
    except:
        pass
    
    time.sleep(0.5)
    
    return {
        "post_id": question_id,
        "title": title,
        "post_body": body,
        "tags": ", ".join(tags),
        "score": score,
        "creation_date": creation_date,
        "accepted_answer": accepted_answer if accepted_answer else "None",
        "group_of_answers": "\n\n---\n\n".join(all_answers) if all_answers else "No answers",
        "num_answers": len(all_answers),
        "comments": "\n".join(all_comments) if all_comments else "No comments",
        "num_comments": len(all_comments),
        "url": f"https://stackoverflow.com/questions/{question_id}",
        "inclusion_criteria": inc_reason,
        "exclusion_criteria": exc_reason,
    }


def main():
    print(f"Fetching {NUM_POSTS} posts with inclusion/exclusion criteria...")
    print(f"Tags: {TAGS}")
    print(f"\n📋 Inclusion Criteria:")
    print(f"  - Keywords: {INCLUSION_RULES['keywords']}")
    print(f"  - Tags: {INCLUSION_RULES['tags']}")
    print(f"  - Min length: {INCLUSION_RULES['min_length']} chars")
    print(f"\n📋 Exclusion Criteria (Pilot - Lenient):")
    print(f"  - Min score: {EXCLUSION_RULES_PILOT['min_score']}")
    print(f"  - Allow closed: {EXCLUSION_RULES_PILOT['allow_closed']}")
    
    questions = fetch_questions_filtered(TAGS, NUM_POSTS)
    
    if not questions:
        print("❌ No posts passed the criteria!")
        return
    
    print(f"\n✅ Building records for {len(questions)} posts...\n")
    
    records = []
    for i, question in enumerate(questions, 1):
        title_preview = question.get('title', '')[:60]
        print(f"Processing {i}/{len(questions)}: {title_preview}...")
        record = build_post_record(question)
        records.append(record)
    
    df = pd.DataFrame(records)
    
    output_file = "stackoverflow_posts_filtered.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Posts")
        
        worksheet = writer.sheets["Posts"]
        for column in worksheet.columns:
            max_length = min(max(len(str(cell.value or "")) for cell in column) + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = max_length
    
    csv_file = "stackoverflow_posts_filtered.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"\n✅ Saved to {output_file} and {csv_file}")
    print(f"Total posts: {len(records)}")


if __name__ == "__main__":
    main()