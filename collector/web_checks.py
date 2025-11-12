import time, requests
from typing import Dict, Any

def run_web_checks(domain: str, ssl_base: str, moz_base: str) -> Dict[str, Any]:
    data = {}

    # Mozilla Observatory
    try:
        start = f"{moz_base}/analyze?host={domain}&rescan=true"
        r = requests.post(start, timeout=60)
        if r.ok:
            scan_id = r.json().get("scan_id")
            time.sleep(5)
            r2 = requests.get(f"{moz_base}/getScanResults?scan={scan_id}", timeout=60)
            if r2.ok:
                data["mozilla_observatory"] = r2.json()
            else:
                data["mozilla_observatory_error"] = r2.text
        else:
            data["mozilla_observatory_error"] = r.text
    except Exception as e:
        data["mozilla_observatory_error"] = str(e)

    # SSL Labs
    try:
        kick = requests.get(f"{ssl_base}/analyze?host={domain}&publish=off&fromCache=on&all=done", timeout=30)
        if kick.ok:
            # poll
            for _ in range(20):
                time.sleep(10)
                st = requests.get(f"{ssl_base}/analyze?host={domain}", timeout=30)
                if st.ok and st.json().get("status") in ("READY","ERROR"):
                    data["ssl_labs"] = st.json()
                    break
        else:
            data["ssl_labs_error"] = kick.text
    except Exception as e:
        data["ssl_labs_error"] = str(e)

    return data
