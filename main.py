import argparse, os, json, pathlib, time
from dotenv import load_dotenv
from utils.logger import log
import json

from infra.supabase_client import upsert, insert, upload_artifact
from collector.subdomains import enumerate_subdomains
from collector.nmap_shodan import run_nmap_shodan
from collector.web_checks import run_web_checks
from enrich.intel_enrich import enrich_intel
from reports.generate import build_html, write_report

def load_settings():
    import json
    with open("configs/settings.json","r") as f:
        return json.load(f)

def ensure_artifacts_dir():
    p = pathlib.Path("artifacts")/ str(int(time.time()))
    p.mkdir(parents=True, exist_ok=True)
    return p

def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Primary domain, e.g., example.com")
    parser.add_argument("--tier", choices=["lite","deep"], default="lite")
    args = parser.parse_args()

    company = os.getenv("REPORT_COMPANY_NAME","DeepDream Security")
    settings = load_settings()
    domain = args.client
    tier = args.tier
    log(f"[bold]Snapshot[/] for {domain} ({tier})")

    # persist org (optional if supabase not configured)
    upsert("organizations", {"domain": domain, "name": domain})
    run_rec = insert("runs", {"tier": tier})
    run_id = (run_rec and run_rec.data[0]["id"]) if run_rec else None

    # subdomains
    words = settings["subdomain_wordlist_lite"] if tier=="lite" else settings["subdomain_wordlist_deep"]
    hosts = enumerate_subdomains(domain, words, settings["dns_resolvers"])
    if not hosts:
        hosts = {domain: ""}

    # nmap + shodan
    nmap_args = settings["nmap"]
    shodan_key = os.getenv("SHODAN_API_KEY","")
    ns = run_nmap_shodan({"domain":domain, "hosts": list(hosts.keys())}, tier, nmap_args["lite_args"], nmap_args["deep_args"], shodan_key)

    # web checks
    ssl_base = os.getenv("SSL_LABS_API_BASE","https://api.ssllabs.com/api/v3")
    moz_base = os.getenv("MOZ_OBSERVATORY_API_BASE","https://http-observatory.security.mozilla.org/api/v1")
    web = run_web_checks(domain, ssl_base, moz_base)

    # intel
    abuse = os.getenv("ABUSEIPDB_API_KEY","")
    gn = os.getenv("GREYNOISE_API_KEY","")
    intel = enrich_intel(ns.get("nmap",{}).get("json",{}), ns.get("shodan",{}), abuse, gn)

    # write artifacts
    adir = ensure_artifacts_dir()
    (adir/"nmap.xml").write_text(ns.get("nmap",{}).get("xml",""), encoding="utf-8")
    (adir/"nmap.json").write_text(json.dumps(ns.get("nmap",{}).get("json",{})), encoding="utf-8")
    (adir/"shodan.json").write_text(json.dumps(ns.get("shodan",{})), encoding="utf-8")
    (adir/"ssllabs.json").write_text(json.dumps(web.get("ssl_labs",{})), encoding="utf-8")
    (adir/"observatory.json").write_text(json.dumps(web.get("mozilla_observatory",{})), encoding="utf-8")
    (adir/"intel.json").write_text(json.dumps(intel), encoding="utf-8")

    # build report
    html = build_html(domain, tier, hosts, ns.get("nmap",{}).get("json",{}), ns.get("shodan",{}), web.get("ssl_labs",{}), web.get("mozilla_observatory",{}), intel, company)
    html_path = write_report(domain, tier, html)

    log(f"HTML report: {html_path}")

    # optional: upload artifacts to Supabase storage if configured
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        for f in adir.iterdir():
            remote = f"{domain}/{tier}/{f.name}"
            upload_artifact(str(f), remote)

if __name__ == "__main__":
    main()
