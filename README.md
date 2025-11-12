# DeepDream Snapshot - Complete Starter

A practical, testable pipeline for Snapshot Lite and Deep. Run locally or via GitHub Actions.

## Features
- Deterministic subdomain discovery (wordlist brute + DNS)
- Nmap host and service detection (XML parsed to JSON)
- Shodan enrichment (host intel)
- SSL Labs + Mozilla Observatory checks
- Threat intel: AbuseIPDB + GreyNoise
- Evidence artifacts stored locally and upload-ready for Supabase Storage
- HTML report rendered to PDF via Playwright (Chromium)
- Supabase schema + minimal persistence for org, assets, runs, findings
- On-demand and scheduled GitHub Actions

## Quick start
1. Copy `.env.example` to `.env` and set keys.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Local test: `python main.py --client example.com --tier lite`
5. Optional PDF: `python scripts/render_pdf.py reports/example.com_lite.html reports/example.com_lite.pdf`
6. Push to GitHub and set Actions secrets.

See `README_RUNBOOK.md` for process steps.
