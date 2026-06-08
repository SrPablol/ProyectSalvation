"""
Uses Groq (llama-3.3-70b-versatile) to generate personalized cold emails.
Get your free API key at: console.groq.com
"""

import re
import time
from groq import Groq, RateLimitError
from src import config
from src.apollo_reader import Lead
from templates.email_prompt import build_system_prompt, build_user_prompt

_MAX_RETRIES = 5


def personalize(lead: Lead) -> dict:
    """
    Returns a dict with keys: subject, body, recommended_service
    Retries on rate limit (429) by parsing the wait time from the error message.
    """
    client = Groq(api_key=config.get("GROQ_API_KEY"))

    for attempt in range(_MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": build_user_prompt(lead)},
                ],
                max_tokens=600,
                temperature=0.7,
            )
            raw = response.choices[0].message.content.strip()
            return _parse_response(raw)

        except RateLimitError as e:
            wait = _parse_wait_seconds(str(e))
            if attempt < _MAX_RETRIES - 1:
                print(f"  ⏳ Groq rate limit — esperando {wait}s antes de reintentar...")
                time.sleep(wait)
            else:
                raise


def _parse_wait_seconds(error_msg: str) -> int:
    """Extract wait time from Groq rate limit error, default 60s."""
    m = re.search(r"try again in (\d+)m(\d+(?:\.\d+)?)s", error_msg)
    if m:
        return int(m.group(1)) * 60 + int(float(m.group(2))) + 5
    m = re.search(r"try again in (\d+(?:\.\d+)?)s", error_msg)
    if m:
        return int(float(m.group(1))) + 5
    return 60


def _parse_response(raw: str) -> dict:
    """
    Expects the model to return:
      SUBJECT: <subject line>
      SERVICE: <service name>
      ---
      <email body>
    """
    lines = raw.splitlines()
    subject = ""
    service = ""
    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.startswith("SERVICE:"):
            service = line.replace("SERVICE:", "").strip()
        elif line.strip() == "---":
            in_body = True
        elif in_body:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    if not subject or not body:
        # Fallback: treat entire response as body
        subject = "Idea para tu negocio"
        body = raw

    return {
        "subject": subject,
        "body": body,
        "recommended_service": service,
    }
