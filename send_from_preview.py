"""
Sends the 19 pre-generated emails from preview_emails.txt directly to Instantly.
Bypasses LLM calls — uses cached personalization from dry-run.
"""

import re
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
INSTANTLY_CAMPAIGN_ID = os.getenv("INSTANTLY_CAMPAIGN_ID")
INSTANTLY_BASE = "https://api.instantly.ai/api/v2"


def parse_preview(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-16-le").replace("\x00", "")
    except Exception:
        text = raw.decode("utf-8", errors="ignore")

    blocks = re.split(r"\[(\d+)/19\]", text)
    results = []
    for i in range(1, len(blocks), 2):
        block = blocks[i + 1] if i + 1 < len(blocks) else ""
        email_m = re.search(r"<([^>]+@[^>]+)>", block)
        subj_m = re.search(r"Subject\s*:\s*(.+)", block)
        body_m = re.search(r"Body preview:\s*\n+(.*?)(?=\n\s*\[|\Z)", block, re.DOTALL)
        if email_m and subj_m and body_m:
            body = body_m.group(1).strip()
            body = re.sub(r"\n?\s*Pablo\s*\|\s*Nodo Labs\s*$", "", body).strip()
            results.append({
                "email": email_m.group(1).strip(),
                "subject": subj_m.group(1).strip(),
                "body": body,
            })
    return results


def load_lead_meta(csv_path):
    df = pd.read_csv(csv_path)
    col_map = {}
    for col in df.columns:
        c = col.lower().replace(" ", "_")
        col_map[c] = col

    def get(row, *keys):
        for k in keys:
            if k in col_map:
                val = row.get(col_map[k], "")
                if pd.notna(val):
                    return str(val)
        return ""

    leads = {}
    for _, row in df.iterrows():
        email = get(row, "email")
        if not email:
            continue
        leads[email.strip().lower()] = {
            "first_name": get(row, "first_name", "firstname"),
            "last_name": get(row, "last_name", "lastname"),
            "company": get(row, "company", "company_name", "account_name"),
            "website": get(row, "website", "company_website"),
            "title": get(row, "title", "job_title"),
            "linkedin": get(row, "linkedin_url", "person_linkedin_url"),
            "city": get(row, "city"),
            "country": get(row, "country"),
            "industry": get(row, "industry"),
        }
    return leads


def send_lead(lead_meta, personalized):
    headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": personalized["email"],
        "campaign_id": INSTANTLY_CAMPAIGN_ID,
        "skip_if_in_workspace": False,
        "firstName": lead_meta.get("first_name", ""),
        "lastName": lead_meta.get("last_name", ""),
        "companyName": lead_meta.get("company", ""),
        "website": lead_meta.get("website", ""),
        "personalization": personalized["body"],
        "custom_subject": personalized["subject"],
        "linkedin": lead_meta.get("linkedin", ""),
        "title": lead_meta.get("title", ""),
        "industry": lead_meta.get("industry", ""),
        "city": lead_meta.get("city", ""),
        "country": lead_meta.get("country", ""),
    }
    resp = requests.post(f"{INSTANTLY_BASE}/leads", json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main():
    preview_path = "data/preview_emails.txt"
    csv_path = "data/apollo-contacts-export (1).csv"

    print("\n" + "=" * 60)
    print("  Enviando 19 leads desde preview cacheado")
    print("=" * 60 + "\n")

    previews = parse_preview(preview_path)
    meta = load_lead_meta(csv_path)

    print(f"Emails parseados del preview: {len(previews)}")
    print(f"Leads en CSV: {len(meta)}\n")

    success, failed = 0, 0
    for p in previews:
        email_key = p["email"].lower()
        lead_meta = meta.get(email_key, {})
        name = lead_meta.get("first_name", p["email"])
        print(f"[{success+failed+1}/{len(previews)}] {p['email']}")
        try:
            send_lead(lead_meta, p)
            print(f"  OK  |  {p['subject']}\n")
            success += 1
        except Exception as e:
            print(f"  ERROR: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"  Completado: {success} exitosos, {failed} fallidos")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
