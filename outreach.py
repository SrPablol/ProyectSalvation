"""
Nodo Labs – Outreach Automation System
=======================================
Usage:
  python outreach.py data/sample_leads.csv --dry-run         # Test only (no API calls to Instantly)
  python outreach.py data/sample_leads.csv --dry-run --limit 3
  python outreach.py data/my_apollo_export.csv               # Live mode – sends to Instantly
  python outreach.py data/my_apollo_export.csv --limit 10    # Send first 10 leads only

Environment:
  Copy .env.example to .env and fill in your API keys before running.
"""

import sys
import time
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import src.config as config
from src.apollo_reader import read_csv
from src.ai_personalizer import personalize
from src.instantly_sender import send


def parse_args():
    parser = argparse.ArgumentParser(
        description="Nodo Labs – Cold Email Outreach Automation"
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default="data/sample_leads.csv",
        help="Path to Apollo CSV export (default: data/sample_leads.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and preview emails without sending to Instantly",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of leads to process (0 = all)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip first N leads (useful to resume after a partial run)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Seconds between API calls to avoid rate limits (default: 1.5)",
    )
    return parser.parse_args()


def print_header(dry_run: bool):
    mode = "DRY RUN – solo preview, no se envía nada" if dry_run else "LIVE – enviando a Instantly"
    print("\n" + "=" * 60)
    print("  Nodo Labs — Outreach Automation System")
    print(f"  Modo: {mode}")
    print("=" * 60 + "\n")


def print_preview(lead, personalized: dict):
    print(f"  {'─'*50}")
    print(f"  Lead     : {lead}")
    print(f"  Service  : {personalized.get('recommended_service', 'N/A')}")
    print(f"  Subject  : {personalized['subject']}")
    print(f"  Body preview:\n")
    for line in personalized["body"].splitlines():
        print(f"    {line}")
    print()


def main():
    args = parse_args()

    # Validate .env is loaded and all keys are present
    config.validate()

    print_header(args.dry_run)

    # Load leads from CSV
    leads = read_csv(args.csv_file)
    if not leads:
        print("No leads found. Verifica el CSV y vuelve a intentar.")
        sys.exit(0)

    leads = leads[args.offset:] if args.offset > 0 else leads
    to_process = leads[: args.limit] if args.limit > 0 else leads
    offset_note = f" (saltando primeros {args.offset})" if args.offset > 0 else ""
    print(f"Procesando {len(to_process)} leads{offset_note}...\n")

    success, failed = 0, 0

    for i, lead in enumerate(to_process, start=1):
        print(f"[{i}/{len(to_process)}] {lead}")

        try:
            # Step 1: Generate personalized email via Claude AI
            personalized = personalize(lead)

            # Step 2: Preview or send
            if args.dry_run:
                print_preview(lead, personalized)
            else:
                send(lead, personalized)
                print(f"  ✓ Enviado a Instantly  |  Subject: {personalized['subject']}\n")

            success += 1

        except Exception as exc:
            print(f"  ✗ Error: {exc}\n")
            failed += 1

        # Respect rate limits between leads
        if i < len(to_process):
            time.sleep(args.delay)

    # Summary
    print("=" * 60)
    print(f"  Completado: {success} exitosos, {failed} fallidos")
    if args.dry_run:
        print("  Modo dry-run: ningún lead fue enviado a Instantly.")
        print("  Cuando estés listo, corre sin --dry-run.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
