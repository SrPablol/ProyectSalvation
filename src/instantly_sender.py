"""
Sends a personalized lead to an Instantly.ai campaign via REST API.

Instantly API v1 reference:
  POST https://api.instantly.ai/api/v1/lead/add
  Headers: Content-Type: application/json
  Body: { api_key, campaign_id, skip_if_in_workspace, leads: [...] }

Each lead object supports custom variables that map to {{variable}} in
your Instantly email template. We send the AI-generated email as a
custom variable so Instantly can use it directly.
"""

import requests
from src import config
from src.apollo_reader import Lead

INSTANTLY_BASE = "https://api.instantly.ai/api/v1"


def send(lead: Lead, personalized: dict) -> dict:
    """
    Adds a lead to the Instantly campaign with personalized email content.
    Raises requests.HTTPError on failure.
    """
    payload = {
        "api_key": config.get("INSTANTLY_API_KEY"),
        "campaign_id": config.get("INSTANTLY_CAMPAIGN_ID"),
        "skip_if_in_workspace": True,
        "leads": [
            {
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "company_name": lead.company,
                "website": lead.website,
                "personalization": personalized["body"],
                "custom_subject": personalized["subject"],
                "recommended_service": personalized.get("recommended_service", ""),
                "linkedin": lead.linkedin,
                "title": lead.title,
                "industry": lead.industry,
                "city": lead.city,
                "country": lead.country,
            }
        ],
    }

    resp = requests.post(
        f"{INSTANTLY_BASE}/lead/add",
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
