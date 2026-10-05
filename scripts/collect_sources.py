"""Download and validate the official IFAB source corpus listed in data/sources_manifest.csv."""

from __future__ import annotations

import csv
import hashlib
import mimetypes
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sources_manifest.csv"
RAW = ROOT / "data" / "raw"
TIMEOUT = 40

HEADERS = {
    "User-Agent": "football-laws-rag-capstone/1.0 (educational project; source validation)"
}


def safe_name(source_id: str, fmt: str) -> str:
    ext = ".pdf" if fmt.upper() == "PDF" else ".html"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", source_id) + ext


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_html(data: bytes, expected_title: str) -> tuple[bool, str]:
    soup = BeautifulSoup(data, "html.parser")
    text = " ".join(soup.stripped_strings)
    if len(text) < 500:
        return False, "HTML contains too little text"
    if "IFAB" not in text.upper():
        return False, "IFAB marker not found"
    return True, ""


def validate_pdf(data: bytes) -> tuple[bool, str]:
    if not data.startswith(b"%PDF"):
        return False, "response is not a PDF"
    if len(data) < 10_000:
        return False, "PDF response is unexpectedly small"
    return True, ""


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    updated = []
    ok_count = 0

    for row in rows:
        url = row["url"].strip()
        source_id = row["source_id"].strip()
        fmt = row["format"].strip().upper()
        target = RAW / safe_name(source_id, fmt)

        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            data = response.content

            if fmt == "PDF":
                valid, reason = validate_pdf(data)
            else:
                valid, reason = validate_html(data, row["title"])

            if not valid:
                raise ValueError(reason)

            target.write_bytes(data)
            row["status"] = "downloaded"
            row["local_path"] = str(target.relative_to(ROOT)).replace("\\", "/")
            row["accessed_on"] = date.today().isoformat()
            checksum = sha256(data)
            note = row.get("notes", "").strip()
            row["notes"] = f"{note}; sha256={checksum}" if note else f"sha256={checksum}"
            ok_count += 1
            print(f"[OK] {source_id} -> {target.name}")

        except Exception as exc:
            row["status"] = "failed"
            row["accessed_on"] = date.today().isoformat()
            note = row.get("notes", "").strip()
            row["notes"] = f"{note}; ERROR={exc}" if note else f"ERROR={exc}"
            print(f"[FAIL] {source_id}: {exc}")

        updated.append(row)

    with MANIFEST.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=updated[0].keys())
        writer.writeheader()
        writer.writerows(updated)

    print(f"\nCollected {ok_count}/{len(updated)} sources.")


if __name__ == "__main__":
    main()
