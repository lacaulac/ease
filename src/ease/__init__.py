#
# import os
import requests
from .classes import *
from . import exporter
from icalendar import Calendar, Event
from datetime import datetime
import toml
from . import ease_setup
from .config import get_config_path, conf_exists
import sys
import os

def setup():
    ease_setup.setup()

def main() -> None:
    print("Hello from epita-auriga-schedule-exporter!")

    if not conf_exists():
        print("Configuration directory does not exist. Running setup...")
        setup()

    # Load the config file
    config = toml.load(get_config_path())

    USERNAME = config["username"]
    PASSWORD = config["password"]

    def make_request(auth_token: str):

        url = "https://auriga.epita.fr/api/plannings/me"

        querystring = {
            "days": ["1", "2", "3", "4", "5", "6", "7"],
            "startDate": "2026-09-21",
            "endDate": "2027-09-27",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:156.0) Gecko/20100101 Firefox/156.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Authorization": "Bearer " + auth_token,
            "X-scope": "frontend",
            "Connection": "keep-alive",
            "Referer": "https://auriga.epita.fr/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }

        response = requests.get(url, headers=headers, params=querystring)

        return response.json()

    from playwright.sync_api import sync_playwright

    TOKEN_URL = (
        "https://ionisepita-auth.np-auriga.nfrance.net"
        "/auth/realms/npionisepita/protocol/openid-connect/token"
    )

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)

        # A fresh browser context: no existing cookies or saved login.
        context = browser.new_context()
        page = context.new_page()

        def observe_request(request):
            if request.url == TOKEN_URL:
                print(
                    "Keycloak token endpoint requested:",
                    request.method,
                    "(payload and credentials intentionally omitted)",
                )

        def observe_response(response):
            if response.url == TOKEN_URL:
                print("Token endpoint HTTP status:", response.status)
                access_token = response.json()["access_token"]
                result = make_request(access_token)
                with open("ex.json", "w", encoding="utf-8") as f:
                    import json

                    json.dump(result, f, ensure_ascii=False, indent=4)
                exporter.export(config["export_filename"])
                # Delete the temporary file
                os.remove("ex.json")
                sys.exit(0)

        # Register listeners BEFORE navigation so early requests aren't missed.
        context.on("request", observe_request)
        context.on("response", observe_response)

        page.goto(
            "https://auriga.epita.fr",
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        if USERNAME != "NONE":
            username_field = page.locator('input[name="username"]')
            username_field.wait_for(state="visible", timeout=60_000)
            username_field.fill(USERNAME)
            password_field = page.locator('input[name="password"]')
            if PASSWORD != "NONE":
                login_button = page.locator('input[name="login"]')

                password_field.wait_for(state="visible", timeout=60_000)

                password_field.fill(PASSWORD)

                login_button.click()
            else:
                password_field.focus()
                print(
                    "No password provided in config.toml. Please finish logging in manually in the browser."
                )
        else:
            print(
                "No username or password provided in config.toml. Please log in manually in the browser."
            )

        page.wait_for_load_state("domcontentloaded", timeout=60_000)
        page.wait_for_timeout(60_000)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
