from typing import Dict, Any, List, Set
import requests

def _abuseipdb_check(ip: str, key: str):
    try:
        r = requests.get("https://api.abuseipdb.com/api/v2/check",
                         headers={"Key": key, "Accept":"application/json"},
                         params={"ipAddress": ip, "maxAgeInDays": 180}, timeout=20)
        if r.status_code == 200:
            return r.json()
        return {"status": r.status_code, "text": r.text}
    except Exception as e:
        return {"error": str(e)}

def _greynoise_quick(ip: str, key: str):
    try:
        r = requests.get(f"https://api.greynoise.io/v3/community/{ip}",
                         headers={"key": key}, timeout=20)
        if r.status_code == 200:
            return r.json()
        return {"status": r.status_code, "text": r.text}
    except Exception as e:
        return {"error": str(e)}

def enrich_intel(nmap_json: Dict[str, Any], shodan_map: Dict[str, Any], abuse_key: str, gn_key: str) -> Dict[str, Any]:
    ips: Set[str] = set()
    try:
        hosts = nmap_json.get("nmaprun", {}).get("host", [])
        if isinstance(hosts, dict):
            hosts = [hosts]
        for h in hosts:
            addrs = h.get("address", [])
            if isinstance(addrs, dict):
                addrs = [addrs]
            for a in addrs:
                if a.get("@addrtype") == "ipv4":
                    ips.add(a.get("@addr"))
    except Exception:
        pass
    # include shodan keys
    ips |= set(shodan_map.keys())

    out = {"abuseipdb": {}, "greynoise": {}}
    for ip in sorted(ips):
        if abuse_key:
            out["abuseipdb"][ip] = _abuseipdb_check(ip, abuse_key)
        if gn_key:
            out["greynoise"][ip] = _greynoise_quick(ip, gn_key)
    return out
