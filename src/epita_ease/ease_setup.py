import os
import toml
from InquirerPy import inquirer
import subprocess
import sys
from .config import get_config_path, create_dirs

current_config = {
    "username": "NONE",
    "password": "NONE",
    "export_filename": "schedule.ics",
    "use_cal_share": False,
    "cal_share_key": "NONE",
    "cal_share_url": "https://calshare.dev.lacaulac.ovh",
}


def setup():
    # Installing firefox for playwright
    # os.system("playwright install firefox")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "firefox"],
        capture_output=True,
        text=True,
        check=True,
    )

    create_dirs()

    # Try to load the config file
    try:
        with open(get_config_path(), "r") as f:
            config = toml.load(f)
            current_config.update(config)
    except FileNotFoundError:
        pass

    # Ask for username and password. If left empty, store None
    username = inquirer.text(
        message="Enter your username",
        long_instruction='(leave empty to keep "'
        + str(current_config["username"])
        + '", type NONE to remove):',
    ).execute()
    if username:
        current_config["username"] = username
        print("Username changed to:", username)
    elif username == "NONE":
        current_config["username"] = "NONE"
    else:
        print("Keeping current username.")

    password = inquirer.secret(
        message="Enter your password",
        long_instruction="(leave empty to keep current, type NONE to remove):",
    ).execute()
    if password:
        current_config["password"] = password
        print("Password changed.")
    elif password == "NONE":
        current_config["password"] = "NONE"
    else:
        print("Keeping current password.")

    # Ask for export filename
    export_filename = inquirer.text(
        message="Enter the export filename",
        long_instruction='(leave empty to keep "'
        + current_config["export_filename"]
        + '")',
    ).execute()
    if export_filename:
        current_config["export_filename"] = export_filename
        print("Export filename changed to:", export_filename)
    else:
        print("Keeping current export filename.")

    # Ask for calshare usage
    use_cal_share = inquirer.confirm(
        message="Do you want to use CalShare?",
        default=current_config["use_cal_share"],
    ).execute()
    current_config["use_cal_share"] = use_cal_share

    if use_cal_share:
        # Ask for calshare key
        cal_share_key = inquirer.text(
            message="Enter your CalShare key",
            long_instruction="(leave empty to keep the curent key)",
        ).execute()
        if cal_share_key:
            current_config["cal_share_key"] = cal_share_key
            print("CalShare key changed to:", cal_share_key)
        else:
            print("Keeping current CalShare key.")

        # Ask for calshare url
        cal_share_url = inquirer.text(
            message="Enter your CalShare URL",
            long_instruction='(leave empty to keep "'
            + current_config["cal_share_url"]
            + '")',
        ).execute()
        if cal_share_url:
            current_config["cal_share_url"] = cal_share_url
            print("CalShare URL changed to:", cal_share_url)
        else:
            print("Keeping current CalShare URL.")

    # Save the config file
    with open(get_config_path(), "w") as f:
        toml.dump(current_config, f)


if __name__ == "__main__":
    setup()
