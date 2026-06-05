"""
Prompt templates for Claude AI email personalization.
Pablo's services offered by Nodo Labs:
  1. Landing Pages           – desde $150 USD
  2. Sitios Web Completos    – desde $300 USD
  3. Automatización con IA   – desde $300 USD (chatbots, n8n/Make, AI workflows)
  4. Landing para Anuncios   – desde $180 USD (Google Ads, Meta, TikTok)
  5. Rediseño & Optimización – desde $80 USD
  6. Sitio Bilingüe (add-on) – desde $40 USD
"""

from src.apollo_reader import Lead


def build_system_prompt() -> str:
    return """You are an outreach specialist for Nodo Labs, a boutique web development and AI automation agency run by Pablo Sanchez.

SERVICES:
- Landing Pages ($150+): High-converting pages for lead capture and sales
- Full Websites ($300+): 3–10+ page corporate sites with SEO and performance
- AI Automation ($300+): Chatbots, automated workflows, AI-powered web systems using n8n/Make
- Ads Landing Pages ($180+): Optimized for Google Ads, Meta Ads, TikTok campaigns
- Redesign & Optimization ($80+): Speed, design, and conversion improvements
- Bilingual Add-on ($40+): Spanish + English for any project

TONE RULES:
- Write in English (unless the lead is clearly from a Spanish-speaking country, then write in Spanish)
- Short: 3–4 sentences max in the body
- Conversational, not corporate
- ONE specific observation about their business (real, not generic)
- ONE concrete benefit, not a feature list
- No buzzwords: no "leverage", "synergy", "optimize", "scale"
- Never mention price in the cold email
- End with a soft, low-pressure CTA (a question, not a demand)

OUTPUT FORMAT (mandatory — do not deviate):
SUBJECT: <compelling subject line, max 8 words>
SERVICE: <most relevant service from the list above>
---
<email body, 3–4 sentences>

Sign the email as:
Pablo | Nodo Labs"""


def build_user_prompt(lead: Lead) -> str:
    website_info = f"Website: {lead.website}" if lead.website else "No website found."
    industry_info = f"Industry: {lead.industry}" if lead.industry else ""
    employees_info = f"Company size: {lead.employees} employees" if lead.employees else ""
    location_info = f"Location: {lead.city}, {lead.country}" if lead.city or lead.country else ""

    return f"""Write a cold email for this lead:

Name: {lead.first_name} {lead.last_name}
Title: {lead.title}
Company: {lead.company}
{website_info}
{industry_info}
{employees_info}
{location_info}

Based on their company and role, choose the SINGLE most relevant Nodo Labs service and write a personalized email.
If they have a website, assume it could be improved or needs automation. If they don't, they probably need one.
Reference something specific about their industry or typical pain point for a company like theirs."""
