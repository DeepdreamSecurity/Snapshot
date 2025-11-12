from typing import Dict, Any, List
from jinja2 import Template
from datetime import datetime
import json, pathlib

from .templates.template import TEMPLATE_HTML

def summarize_nmap(nmap_json: Dict[str, Any]) -> str:
    try:
        hosts = nmap_json.get("nmaprun", {}).get("host", [])
        if isinstance(hosts, dict):
            hosts = [hosts]
        lines = []
        for h in hosts:
            addr = None
            addrs = h.get("address", [])
            if isinstance(addrs, dict):
                addrs = [addrs]
            for a in addrs:
                if a.get("@addrtype") == "ipv4":
                    addr = a.get("@addr")
            ports = h.get("ports", {}).get("port", [])
            if isinstance(ports, dict):
                ports = [ports]
            open_ports = [p.get("@portid")+"-"+p.get("service",{}).get("@name","") for p in ports if p.get("state",{}).get("@state")=="open"]
            lines.append(f"{addr}: {', '.join(open_ports) if open_ports else 'no open ports'}")
        return "\n".join(lines)
    except Exception as e:
        return f"parse error: {e}"

def build_html(domain: str, tier: str, hosts: Dict[str,str], nmap_json: Dict[str,Any], shodan_map: Dict[str,Any], ssllabs: Dict[str,Any], moz: Dict[str,Any], intel: Dict[str,Any], company: str) -> str:
    tmpl = Template(TEMPLATE_HTML)
    key_findings = []
    # naive finding: no TLS grade yet
    if not ssllabs:
        key_findings.append({"title":"TLS evaluation unavailable","severity":"low"})
    nmap_summary = summarize_nmap(nmap_json)
    html = tmpl.render(
        company=company or "DeepDream Security",
        domain=domain,
        tier=tier,
        generated=datetime.utcnow().isoformat(timespec="seconds")+"Z",
        key_findings=key_findings,
        hosts=hosts,
        nmap_summary=nmap_summary,
        shodan_json=json.dumps(shodan_map, indent=2)[:50000],
        ssllabs_json=json.dumps(ssllabs, indent=2)[:50000],
        moz_json=json.dumps(moz, indent=2)[:50000],
        intel_json=json.dumps(intel, indent=2)[:50000],
        year=datetime.utcnow().year
    )
    return html

def write_report(domain: str, tier: str, html: str) -> str:
    out = pathlib.Path("reports") / f"{domain}_{tier}.html"
    out.write_text(html, encoding="utf-8")
    return str(out)
