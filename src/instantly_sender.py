"""
Sends a personalized lead to an Instantly.ai campaign via REST API v2.

Instantly API v2 reference:
  POST https://api.instantly.ai/api/v2/leads
  Headers: Authorization: Bearer <api_key>, Content-Type: application/json
  Body: { email, campaign_id, firstName, lastName, companyName, personalization, ... }
"""

import requests
from src import config
from src.apollo_reader import Lead

INSTANTLY_BASE = "https://api.instantly.ai/api/v2"


def send(lead: Lead, personalized: dict) -> dict:
    """
    Adds a lead to the Instantly campaign with personalized email content.
    Raises requests.HTTPError on failure.
    """
    headers = {
        "Authorization": f"Bearer {config.get('INSTANTLY_API_KEY')}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": lead.email,
        "campaign_id": config.get("INSTANTLY_CAMPAIGN_ID"),
        "skip_if_in_workspace": True,
        "firstName": lead.first_name,
        "lastName": lead.last_name,
        "companyName": lead.company,
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

    resp = requests.post(
        f"{INSTANTLY_BASE}/leads",
        json=payload,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
