# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Cold email outreach automation for **Nodo Labs** (Pablo Sanchez). Pipeline:
1. Read leads from an Apollo.io CSV export (`apollo_reader.py`)
2. Generate personalized email via **Groq API** — model `llama-3.3-70b-versatile` (`ai_personalizer.py`)
3. Add lead to an Instantly.ai campaign via **REST API v2** (`instantly_sender.py`)

## Commands

```bash
# Dry run — previews emails, no API calls to Instantly
python outreach.py data/sample_leads.csv --dry-run

# Dry run with limit
python outreach.py data/sample_leads.csv --dry-run --limit 3

# Live send
python outreach.py data/mi_export_apollo.csv

# Resume after partial run (skip first N leads)
python outreach.py data/mi_export_apollo.csv --offset 20 --limit 10

# Adjust rate limiting (default 1.5s between leads)
python outreach.py data/leads.csv --delay 2.0
```

## Required `.env` variables

```
GROQ_API_KEY=            # console.groq.com → API Keys (free, no card)
INSTANTLY_API_KEY=       # Instantly → Settings → API
INSTANTLY_CAMPAIGN_ID=   # ID of the target Instantly campaign
```

`APOLLO_API_KEY` is optional — only needed if reading leads via API instead of CSV.

## Architecture

- **`src/config.py`** — validates `GROQ_API_KEY`, `INSTANTLY_API_KEY`, `INSTANTLY_CAMPAIGN_ID` at startup.
- **`src/apollo_reader.py`** — maps two CSV column formats (Apollo title-case and lowercase_underscore) into `Lead` dataclass. Rows without email are skipped.
- **`src/ai_personalizer.py`** — calls Groq with retry on `RateLimitError` (parses wait time from error message). Expects strict `SUBJECT: / SERVICE: / --- / body` format from model; falls back to full response as body.
- **`src/instantly_sender.py`** — POSTs to `https://api.instantly.ai/api/v2/leads`. Sets `skip_if_in_workspace: true` to prevent duplicates. Raises `HTTPError` on failure.
- **`templates/email_prompt.py`** — all LLM prompt logic. Subject line is always `"Quick thought on [Company Name]"`. Tone rules and service heuristics are in the system prompt.

## Instantly template variables

The Instantly campaign template must use `{{personalization}}` for the email body and `{{custom_subject}}` for the subject line.

## Nodo Labs services (used in prompt)

| Servicio | Precio |
|---|---|
| Landing Pages | $150+ |
| Sitios Web Completos | $300+ |
| Automatización con IA (n8n/Make) | $300+ |
| Landing para Anuncios | $180+ |
| Rediseño & Optimización | $80+ |
| Sitio Bilingüe (add-on) | $40+ |
