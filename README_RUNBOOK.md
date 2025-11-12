# Snapshot Runbook

## Intake
- Collect primary domain, second-level domain, optional owned IP/CIDRs.
- Confirm tier: lite vs deep.

## Run
- `python main.py --client <domain> --tier lite|deep`

## Deliverables
- `reports/<domain>_<tier>.html` and `.pdf`
- `artifacts/<timestamp>/` raw evidence (Nmap XML, Shodan JSON, SSL Labs JSON, Observatory JSON, intel JSON)

## Scoring
- Severity mapping in `configs/settings.json`.
