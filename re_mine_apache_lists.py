"""
Re-mine Apache Mailing Lists using mbox archive download + local parsing.
This is the standard research approach (Bird et al. 2006, MSR 2013).

References:
- Bird et al. (2006) "Mining Email Social Networks" - cited 816 times
- MSR 2013 "Communication in OSS Development Mailing Lists"
"""

import requests
import time
import pandas as pd
import mailbox
import email
import io
import gzip
import re
from datetime import datetime
from pathlib import Path
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os

# Configuration
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
MBOX_CACHE_DIR = OUTPUT_DIR / "mbox_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MBOX_CACHE_DIR, exist_ok=True)

# Apache projects and their mailing lists
PROJECT_LISTS = {
    "hadoop": [
        "dev@hadoop.apache.org",
        "common-dev@hadoop.apache.org",
        "hdfs-dev@hadoop.apache.org",
        "mapreduce-dev@hadoop.apache.org",
    ],
    "spark": [
        "dev@spark.apache.org",
        "user@spark.apache.org",
    ],
    "kafka": [
        "dev@kafka.apache.org",
        "users@kafka.apache.org",
    ],
    "flink": [
        "dev@flink.apache.org",
        "user@flink.apache.org",
    ],
}

# Focused JNI keywords (reduced from 261)
# Import centralized keywords
from keyword_selection import load_selected_keywords

# Keywords for Apache Lists loaded from scientific selection
KEYWORDS = load_selected_keywords("apache")


# Time range
START_YEAR = 2015
END_YEAR = 2026


def decode_mime_header(header_value: str) -> str:
    """Decode MIME-encoded email headers."""
    if not header_value:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            else:
                result.append(part)
        return " ".join(result)
    except Exception:
        return str(header_value)


def get_email_body(msg: email.message.Message) -> str:
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    return payload.decode(charset, errors='replace')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            return payload.decode(charset, errors='replace')
    return ""


def download_mbox(list_name: str, year: int, month: int) -> str | None:
    """
    Download mbox archive for a specific list and month.
    
    Uses the standard Apache mbox URL format:
    https://mail-archives.apache.org/mod_mbox/{list_name}/{YYYYMM}.mbox
    """
    # Convert list name to archive path
    # e.g., "dev@hadoop.apache.org" → "hadoop-dev"
    local_part, domain = list_name.split("@")
    project = domain.split(".")[0]
    archive_name = f"{project}-{local_part}"
    
    date_str = f"{year}{month:02d}"
    
    # Try multiple URL formats
    urls = [
        f"https://mail-archives.apache.org/mod_mbox/{archive_name}/{date_str}.mbox",
        f"https://lists.apache.org/api/mbox.lua?list={local_part}&domain={domain}&d={year}-{month:02d}",
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=30, stream=True)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.text
        except Exception:
            continue
    
    return None


def parse_mbox(mbox_content: str, list_name: str, project: str) -> list[dict]:
    """Parse mbox content and extract emails."""
    try:
        # Create a temporary mbox file
        mbox_file = io.StringIO(mbox_content)
        
        # Use mailbox module to parse
        # For string content, we need to write to a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False, encoding='utf-8') as f:
            f.write(mbox_content)
            temp_path = f.name
        
        mbox_obj = mailbox.mbox(temp_path)
        
        emails = []
        for msg in mbox_obj:
            try:
                subject = decode_mime_header(msg.get("Subject", ""))
                from_addr = decode_mime_header(msg.get("From", ""))
                date_str = msg.get("Date", "")
                message_id = msg.get("Message-ID", "")
                
                # Parse date
                try:
                    parsed_date = parsedate_to_datetime(date_str)
                    creation_date = parsed_date.strftime('%Y-%m-%d')
                except Exception:
                    creation_date = "Unknown"
                
                body = get_email_body(msg)
                
                # Build link
                link = f"https://lists.apache.org/thread/{message_id}" if message_id else ""
                
                emails.append({
                    "title": subject,
                    "link": link,
                    "score": 0,
                    "snippet": body[:400] if body else "",
                    "creation_date": creation_date,
                    "project": project,
                    "list": list_name,
                    "thread_id": message_id,
                    "author": from_addr,
                    "full_body": body,
                })
            except Exception:
                continue
        
        mbox_obj.close()
        os.unlink(temp_path)
        
        return emails
    
    except Exception as e:
        print(f"    ⚠️  Error parsing mbox: {e}")
        return []


def filter_by_keywords(emails: list[dict], keywords: list[str]) -> list[dict]:
    """Filter emails by JNI keywords."""
    filtered = []
    for em in emails:
        text = f"{em['title']} {em['full_body']}".lower()
        matched_keywords = [kw for kw in keywords if kw.lower() in text]
        if matched_keywords:
            em["matched_keywords"] = ", ".join(matched_keywords)
            filtered.append(em)
    return filtered


def main():
    print("=" * 60)
    print("🔍 RE-MINING APACHE MAILING LISTS (mbox approach)")
    print("=" * 60)
    print(f"Projects: {list(PROJECT_LISTS.keys())}")
    print(f"Keywords: {len(KEYWORDS)}")
    print(f"Time range: {START_YEAR}-{END_YEAR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    all_results = []
    total_emails = 0
    total_matched = 0
    
    for project, lists in PROJECT_LISTS.items():
        print(f"\n{'='*40}")
        print(f"📁 Project: {project}")
        print(f"{'='*40}")
        
        for list_name in lists:
            print(f"\n  📧 List: {list_name}")
            
            for year in range(START_YEAR, END_YEAR + 1):
                for month in range(1, 13):
                    # Skip future months
                    if year == END_YEAR and month > datetime.now().month:
                        break
                    
                    # Download mbox
                    mbox_content = download_mbox(list_name, year, month)
                    
                    if not mbox_content:
                        continue  # No archive for this month
                    
                    # Parse emails
                    emails = parse_mbox(mbox_content, list_name, project)
                    total_emails += len(emails)
                    
                    if emails:
                        # Filter by keywords
                        matched = filter_by_keywords(emails, KEYWORDS)
                        total_matched += len(matched)
                        
                        if matched:
                            print(f"    📅 {year}-{month:02d}: {len(emails)} emails, {len(matched)} JNI-related ✅")
                            
                            for em in matched:
                                all_results.append({
                                    "phase": "APACHE_LISTS_REMINING",
                                    "forum": "Apache Lists",
                                    "keyword": em.get("matched_keywords", ""),
                                    "title": em["title"],
                                    "link": em["link"],
                                    "snippet": em["snippet"],
                                    "score": 0,
                                    "creation_date": em["creation_date"],
                                    "project": em["project"],
                                    "list": em["list"],
                                    "thread_id": em["thread_id"],
                                    "author": em.get("author", ""),
                                    "collected_at": datetime.now().isoformat(),
                                })
                        
                        time.sleep(0.5)  # Rate limiting
    
    # Save results
    if all_results:
        df = pd.DataFrame(all_results)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        path = OUTPUT_DIR / f"apache_lists_remined_{timestamp}.csv"
        df.to_csv(path, index=False)
        
        print(f"\n{'='*60}")
        print(f"✅ REMINING COMPLETE!")
        print(f"   Total emails scanned: {total_emails}")
        print(f"   JNI-related emails: {total_matched}")
        print(f"   Unique posts saved: {len(df)}")
        print(f"   💾 Saved to: {path}")
        print(f"{'='*60}")
        
        # Summary
        print(f"\n📊 Summary:")
        non_unknown = df[df['creation_date'] != 'Unknown']['creation_date']
        if not non_unknown.empty:
            print(f"  Date range: {non_unknown.min()} to {non_unknown.max()}")
        print(f"  Project breakdown:")
        print(df['project'].value_counts().to_string())
        print(f"\n📋 Top keywords:")
        # Flatten matched keywords
        all_kw = []
        for kw_str in df['keyword']:
            all_kw.extend([k.strip() for k in str(kw_str).split(',')])
        kw_counts = pd.Series(all_kw).value_counts().head(10)
        for kw, count in kw_counts.items():
            print(f"  • {kw}: {count}")
        
        return df
    else:
        print("\n❌ No JNI-related emails found!")
        return pd.DataFrame()


if __name__ == "__main__":
    main()