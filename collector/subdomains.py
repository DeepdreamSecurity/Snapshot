from typing import List, Dict
import dns.resolver
from urllib.parse import urlparse

def enumerate_subdomains(domain: str, words: List[str], resolvers: List[str]) -> Dict[str, str]:
    r = dns.resolver.Resolver()
    r.nameservers = resolvers
    found = {}
    for w in words:
        sub = f"{w}.{domain}"
        try:
            answers = r.resolve(sub, "A")
            ips = sorted({a.to_text() for a in answers})
            found[sub] = ",".join(ips)
        except Exception:
            continue
    return found
