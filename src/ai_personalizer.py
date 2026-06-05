"""
Uses Google Gemini (free tier) to generate personalized cold emails.
Get your free API key at: aistudio.google.com → Get API Key
No credit card required — 1M tokens/day free.
"""

from google import genai
from google.genai import types
from src import config
from src.apollo_reader import Lead
from templates.email_prompt import build_system_prompt, build_user_prompt


def personalize(lead: Lead) -> dict:
    """
    Returns a dict with keys: subject, body, recommended_service
    """
    client = genai.Client(api_key=config.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=build_user_prompt(lead),
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            max_output_tokens=600,
            temperature=0.7,
        ),
    )

    raw = response.text.strip()
    return _parse_response(raw)


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
