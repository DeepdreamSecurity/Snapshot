from typing import Dict, Any, List
import subprocess, xmltodict, json, os, time, requests

def _run_nmap(targets: List[str], args: List[str]) -> Dict[str, Any]:
    cmd = ["nmap"] + args + targets
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        xml = p.stdout
        data = xmltodict.parse(xml)
        return {"xml": xml, "json": data, "cmd": " ".join(cmd)}
    except Exception as e:
        return {"error": str(e), "cmd": " ".join(cmd)}

def _shodan_host(ip: str, key: str) -> Dict[str, Any]:
    try:
        url = f"https://api.shodan.io/shodan/host/{ip}?key={key}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        return {"status": r.status_code, "text": r.text}
    except Exception as e:
        return {"error": str(e)}

def run_nmap_shodan(scope: Dict[str, Any], tier: str, nmap_args_lite: List[str], nmap_args_deep: List[str], shodan_key: str) -> Dict[str, Any]:
    targets = scope.get("hosts", [scope["domain"]])
    args = nmap_args_lite if tier == "lite" else nmap_args_deep
    nmap_out = _run_nmap(targets, args)

    # Shodan enrichment for discovered IPs or target
    shodan = {}
    if shodan_key:
        ips = set()
        try:
            # gather IPs from nmap json
            for h in nmap_out.get("json", {}).get("nmaprun", {}).get("host", []):
                addrs = h.get("address", [])
                if isinstance(addrs, dict):
                    addrs = [addrs]
                for a in addrs:
                    if a.get("@addrtype") == "ipv4":
                        ips.add(a.get("@addr"))
        except Exception:
            pass
        if not ips:
            # fallback: try resolving domain
            try:
                import socket
                ips.add(socket.gethostbyname(scope["domain"]))
            except Exception:
                pass
        for ip in ips:
            shodan[ip] = _shodan_host(ip, shodan_key)
    return {"nmap": nmap_out, "shodan": shodan}
