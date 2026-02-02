#!/usr/bin/env python3
"""
Passive Wayback Recon Tool
Live-streaming • Debuggable • Reproducible • Scriptable

Author: Taylor Christian Newsome
Version: 3.3
"""

import argparse
import requests
import xml.etree.ElementTree as ET
import logging
import sys
import time
from datetime import datetime

CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
USER_AGENT = "Wayback-Recon/3.3 (Passive Research)"
REQUEST_TIMEOUT = 20
RATE_DELAY = 1.0

# ---------------- LOGGING ---------------- #

logger = logging.getLogger("wayback")
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

# ---------------- ASCII ---------------- #

def banner():
    print(r"""
██     ██  █████  ██    ██     ██████   █████   ██████ ██   ██
██     ██ ██   ██  ██  ██      ██   ██ ██   ██ ██      ██  ██
██  █  ██ ███████   ████       ██████  ███████ ██      █████
██ ███ ██ ██   ██    ██        ██   ██ ██   ██ ██      ██  ██
 ███ ███  ██   ██    ██        ██████  ██   ██  ██████ ██   ██

Passive Wayback Recon — streaming & reproducible
""")

# ---------------- CORE ---------------- #

def build_queries(domain: str):
    """
    Deterministic query set (reproducible)
    """
    return [
        f"{CDX_ENDPOINT}?url=*.{domain}&output=xml&fl=original&collapse=urlkey",
        f"{CDX_ENDPOINT}?url={domain}*&output=xml&fl=original&collapse=urlkey",
    ]

def fetch_xml(url: str):
    """
    Fetch CDX XML safely
    """
    headers = {"User-Agent": USER_AGENT}
    logger.debug(f"HTTP GET {url}")

    r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    if not r.content.startswith(b"<?xml"):
        logger.debug("Response not XML, skipping")
        return None

    return r.content

def parse_endpoints(xml_data: bytes):
    """
    Parse <original> entries
    """
    results = set()
    root = ET.fromstring(xml_data)

    for elem in root.iter("original"):
        endpoint = elem.text.strip()
        results.add(endpoint)

    return results

def run_scan(domain: str):
    """
    Run full passive scan with live output
    """
    all_results = set()

    for query in build_queries(domain):
        logger.info(f"Query: {query}")
        print(f"\n[>] Wayback query started")
        print(f"[>] {query}\n")

        try:
            xml_data = fetch_xml(query)
            if not xml_data:
                continue

            endpoints = parse_endpoints(xml_data)

            for ep in sorted(endpoints):
                if ep not in all_results:
                    all_results.add(ep)
                    print(ep, flush=True)   # LIVE FEEDBACK

        except Exception as e:
            logger.error(f"Query failed: {e}")

        time.sleep(RATE_DELAY)

    return sorted(all_results)

# ---------------- CLI ---------------- #

def cli(domain: str, curl: bool):
    banner()

    start_time = datetime.utcnow().isoformat() + "Z"
    logger.warning(f"Target: {domain}")
    logger.warning(f"Start: {start_time}")
    logger.warning("Mode: passive-wayback\n")

    results = run_scan(domain)

    print("\n--- SCAN COMPLETE ---")
    print(f"[+] Unique endpoints: {len(results)}")

    if curl and results:
        print("\n--- CURL COMMANDS ---")
        for r in results:
            print(f"curl '{r}'")

    end_time = datetime.utcnow().isoformat() + "Z"
    logger.warning(f"End: {end_time}")

    return 0 if results else 1

# ---------------- ENTRY ---------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Passive Wayback Recon Tool (live, reproducible, scriptable)",
        epilog="""
Examples:
  Live scan:
    python3 wayback.py -u example.com

  Debug mode:
    python3 wayback.py -u example.com --debug

  Curl output:
    python3 wayback.py -u example.com --curl

Pipeline usage:
  python3 wayback.py -u example.com | tee endpoints.txt
"""
    )

    parser.add_argument("-u", "--url", required=True, help="Target domain")
    parser.add_argument("--curl", action="store_true", help="Emit curl commands")
    parser.add_argument("--debug", action="store_true", help="Debug logging")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    exit_code = cli(args.url.strip(), args.curl)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
