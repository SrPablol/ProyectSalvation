# ProyectSalvation – Nodo Labs Outreach System

## Contexto del proyecto
Sistema de cold email outreach a escala para **Nodo Labs** (empresa de Pablo Sanchez).
Conecta Apollo.io (fuente de leads) → Claude AI (personalización) → Instantly.ai (envío).

## Empresa: Nodo Labs
- **Fundador:** Pablo Andres Sanchez
- **Email:** psanchezp2@miumg.edu.gt
- **WhatsApp:** +50235143543
- **Stack:** React, Next.js, Python, Node.js, n8n/Make, Firebase, Tailwind CSS

## Servicios ofrecidos
| Servicio                  | Precio base |
|---------------------------|-------------|
| Landing Pages             | $150 USD    |
| Sitios Web Completos      | $300 USD    |
| Automatización con IA     | $300 USD    |
| Landing para Anuncios     | $180 USD    |
| Rediseño & Optimización   | $80 USD     |
| Sitio Bilingüe (add-on)   | $40 USD     |

## Estructura del proyecto
```
ProyectSalvation/
├── outreach.py              # Entry point principal
├── requirements.txt         # Dependencias Python
├── .env.example             # Template de variables de entorno
├── .env                     # Tu .env real (NO commitear)
├── src/
│   ├── config.py            # Validación de .env
│   ├── apollo_reader.py     # Lectura de CSV de Apollo
│   ├── ai_personalizer.py   # Personalización con Claude AI
│   └── instantly_sender.py  # Envío a Instantly API
├── templates/
│   └── email_prompt.py      # Prompts del sistema y usuario para Claude
└── data/
    └── sample_leads.csv     # Leads de prueba (5 contactos)
```

## Comandos de uso
```bash
# 1. Setup (primera vez)
cp .env.example .env
# Edita .env con tus API keys

# 2. Test con leads de muestra (NO envía a Instantly)
python outreach.py data/sample_leads.csv --dry-run

# 3. Test limitado – solo 3 leads
python outreach.py data/sample_leads.csv --dry-run --limit 3

# 4. Live – envía a Instantly (con tu CSV de Apollo real)
python outreach.py data/mi_export_apollo.csv

# 5. Live limitado – primeros 10
python outreach.py data/mi_export_apollo.csv --limit 10
```

## Variables de entorno requeridas (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
INSTANTLY_API_KEY=...
INSTANTLY_CAMPAIGN_ID=...
SENDER_NAME=Pablo Sanchez
SENDER_COMPANY=Nodo Labs
```

## Flujo del sistema
1. `apollo_reader.py` lee el CSV exportado desde Apollo.io
2. `ai_personalizer.py` llama a Claude (claude-sonnet-4-6) con el contexto del lead
3. Claude genera: subject line + servicio recomendado + cuerpo del email personalizado
4. `instantly_sender.py` POST a `/api/v1/lead/add` con el contenido personalizado
5. Instantly usa `{{personalization}}` y `{{custom_subject}}` en su template

## Notas importantes
- Siempre usa `--dry-run` primero para validar el tono de los emails
- Apollo CSV export estándar: columnas en inglés (First Name, Last Name, Company, etc.)
- Rate limiting: 1.5s entre leads por defecto (configurable con `--delay`)
- `skip_if_in_workspace: true` previene duplicados en Instantly
