#!/usr/bin/env python3
"""
Python Client for the cal-share Service.
Uploads .ical / .ics files to the cal-share API using non-expiring JWT Bearer authentication.

Usage:
    python calshare_client.py --url http://localhost:8080 --token <JWT_TOKEN> --file schedule.ics

    Or use as a reusable Python module in your project:
        from calshare_client import CalShareClient
        client = CalShareClient("http://localhost:8080", token="<JWT_TOKEN>")
        client.upload_file("path/to/my_calendar.ics")
"""

import argparse
import os
import sys
from typing import Optional
import urllib.request
import urllib.error
import json


class CalShareClient:
    """Client for uploading and replacing .ical feeds on the cal-share server."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()

    def upload_file(self, file_path: str) -> dict:
        """Uploads an .ics file from disk, replacing any existing calendar for the token's identifier."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"iCalendar file not found: {file_path}")

        with open(file_path, "rb") as f:
            data = f.read()

        return self.upload_data(data)

    def upload_data(self, ical_bytes: bytes) -> dict:
        """Uploads raw .ical bytes to the /upload endpoint."""
        endpoint = f"{self.base_url}/upload"

        req = urllib.request.Request(
            endpoint,
            data=ical_bytes,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/calendar; charset=utf-8",
                "User-Agent": "Python-CalShare-Uploader/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"HTTP {err.code} error from cal-share server: {err_body}"
            ) from err
        except urllib.error.URLError as err:
            raise ConnectionError(
                f"Failed to connect to {endpoint}: {err.reason}"
            ) from err

    def fetch_calendar(self, identifier: str) -> str:
        """Fetches the raw .ical file content for the given identifier."""
        endpoint = f"{self.base_url}/calendar/{identifier}"
        req = urllib.request.Request(endpoint, method="GET")

        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")

    @classmethod
    def provision_token(cls, base_url: str, secret: str, identifier: str) -> dict:
        """Admin helper: Calls /create_user to generate a non-expiring JWT."""
        endpoint = f"{base_url.rstrip('/')}/create_user"
        payload = json.dumps({"secret": secret, "identifier": identifier}).encode(
            "utf-8"
        )

        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Upload .ical to cal-share service.")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Base URL of the cal-share service",
    )
    parser.add_argument("--token", required=True, help="Non-expiring JWT Bearer token")
    parser.add_argument(
        "--file", required=True, help="Path to .ics / .ical file to upload"
    )

    args = parser.parse_args()

    client = CalShareClient(args.url, args.token)
    try:
        print(f"Uploading {args.file} to {args.url}/upload...")
        result = client.upload_file(args.file)
        print("Upload successful!")
        print(f"Identifier: {result.get('identifier')}")
        print(f"Bytes written: {result.get('bytes_written')}")
        print(f"Calendar URL: {args.url}{result.get('calendar_url')}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
