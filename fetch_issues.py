#!/usr/bin/env python3
"""Fetch all SonarQube issues and write them to a timestamped CSV in outputs/."""

import csv
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

ENDPOINT_FILE = os.path.join(os.path.dirname(__file__), "endpoint.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
PAGE_SIZE = 500
FIELDS = ["project", "rule", "severity", "author", "effort", "creationDate", "updateDate"]


def load_config() -> tuple[str, str]:
    with open(ENDPOINT_FILE) as f:
        cfg = json.load(f)
    return cfg["endpoint_url"].rstrip("/"), cfg["endpoint_token"]


def fetch_page(base_url: str, token: str, page: int) -> dict:
    params = urllib.parse.urlencode({"p": page, "ps": PAGE_SIZE})
    url = f"{base_url}/api/issues/search?{params}"
    request = urllib.request.Request(url, method="GET")
    # SonarQube token auth: token as username, empty password
    import base64
    credentials = base64.b64encode(f"{token}:".encode()).decode()
    request.add_header("Authorization", f"Basic {credentials}")
    request.add_header("Content-Length", "0")
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def extract_fields(issue: dict) -> dict:
    return {field: issue.get(field, "") for field in FIELDS}


def main() -> None:
    base_url, token = load_config()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(OUTPUT_DIR, f"{timestamp}.csv")

    page = 1
    total_written = 0

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()

        while True:
            print(f"Fetching page {page}...", flush=True)
            data = fetch_page(base_url, token, page)

            paging = data.get("paging", {})
            page_index = paging.get("pageIndex", page)
            page_size = paging.get("pageSize", PAGE_SIZE)
            total = paging.get("total", 0)

            issues = data.get("issues", [])
            for issue in issues:
                writer.writerow(extract_fields(issue))
            total_written += len(issues)

            print(f"  Got {len(issues)} issues (total so far: {total_written} / {total})")

            # Stop if we've received all issues
            if page_index * page_size >= total or not issues:
                break

            page += 1

    print(f"\nDone. {total_written} issues written to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
