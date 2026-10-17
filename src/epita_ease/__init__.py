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
from .calshare_client import CalShareClient
import sys
import os


def setup():
    ease_setup.setup()


def main() -> None:

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test" and len(sys.argv) > 2:
            filetotest = sys.argv[2]
            exporter.export(f"{filetotest}.ics", tmp_file=filetotest)
            sys.exit(0)

    print("Hello from epita-auriga-schedule-exporter!")

    if not conf_exists():
        print("Configuration directory does not exist. Running setup...")
        setup()

    # Load the config file
    config = toml.load(get_config_path())

    required_keys_and_version = [("use_cal_share", "0.3.0")]

    for key, version in required_keys_and_version:
        if key not in config:
            print(
                f"Configuration file is missing the '{key}' config element, added in version {version}.\n==> Please rerun setup! (`ease-setup`) <=="
            )
            sys.exit(1)

    USERNAME = config["username"]
    PASSWORD = config["password"]
    HEADLESS = False

    if "--headless" in sys.argv:
        if USERNAME != "NONE" and PASSWORD != "NONE":
            print("Running in headless mode with provided credentials.")
            HEADLESS = True
        else:
            print(
                "Headless mode requires both username and password to be set in the config file. Please provide them or run without --headless."
            )
            print("Proceeding without headless mode (headful ?)")

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
        browser = p.firefox.launch(headless=HEADLESS)

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
                if config["use_cal_share"]:
                    client = CalShareClient(
                        config["cal_share_url"], token=config["cal_share_key"]
                    )
                    cal_url_end = client.upload_file(config["export_filename"]).get(
                        "calendar_url"
                    )
                    print(
                        f"Calendar uploaded to CalShare: {config['cal_share_url']}{cal_url_end}"
                    )
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
