#!/usr/bin/env python3
"""aer1-scan: check every zambo receipt in a file, a web page, or stdin.

A zambo receipt proves the saved result of an AI job was not changed
after the fact. This tool sends only the receipt ids, nothing else.
Pure standard library, no dependencies.
"""
import json
import re
import sys
import urllib.error
import urllib.request

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
LINK_RE = re.compile(r"zambo\.dev/[^\s\"'<>\])]*?(" + UUID + r")", re.IGNORECASE)
BARE_RE = re.compile(r"^\s*(" + UUID + r")\s*$", re.MULTILINE)
MAX = 50
TIMEOUT = 20


def raw_url(u):
    try:
        from urllib.parse import urlparse
        p = urlparse(u)
        if p.hostname == "gist.github.com":
            return u.rstrip("/") + "/raw"
        if p.hostname == "github.com" and "/blob/" in p.path:
            return u.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    except Exception:
        pass
    return u


def extract(text):
    seen = set()
    ids = []

    def add(rid):
        rid = rid.lower()
        if rid not in seen:
            seen.add(rid)
            ids.append(rid)

    # A pasted receipt JSON export: its own top-level id is a receipt id.
    if "receipt_schema_version" in text:
        jm = re.search(r'"id"\s*:\s*"(' + UUID + r')"', text, re.IGNORECASE)
        if jm:
            add(jm.group(1))
    for m in LINK_RE.finditer(text):
        if m.group(0).lower().startswith("zambo.dev/workflow/"):
            continue  # workflow ids are not receipt ids
        add(m.group(1))
    for m in BARE_RE.finditer(text):
        add(m.group(1))
    return ids[:MAX]


def read_input(arg):
    if not arg or arg == "-":
        return sys.stdin.read()
    if arg.lower().startswith(("http://", "https://")):
        req = urllib.request.Request(raw_url(arg), headers={"User-Agent": "aer1-scan"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return res.read().decode("utf-8", "replace")
    with open(arg, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def verify(rid):
    req = urllib.request.Request(
        "https://zambo.dev/api/v2/receipt/" + rid + "/verify",
        headers={"User-Agent": "aer1-scan"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            data = json.loads(res.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return "not found" if e.code == 404 else "could not verify"
    except Exception:
        return "could not verify"
    status = data.get("verification_status")
    return "verified" if status == "verified" else str(status or "could not verify")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        text = read_input(arg)
    except Exception as e:
        print("aer1-scan: " + str(e), file=sys.stderr)
        return 1
    ids = extract(text)
    if not ids:
        print("no zambo receipt links found. receipts look like zambo.dev/run/ followed by an id.",
              file=sys.stderr)
        return 1
    failed = False
    for rid in ids:
        state = verify(rid)
        if state != "verified":
            failed = True
        print(state + " " + rid + " https://zambo.dev/verify/?id=" + rid)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
