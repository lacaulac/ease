import os
import sys

def get_config_path():
    # Detect if running on Linux or Windows and set the config path accordingly
    config_path = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        config_path +="\\AppData\\Local\\ease\\config.toml"
    else:
        config_path += "/.config/ease/config.toml"
    return config_path

def conf_exists():
    config_path = get_config_path()
    return os.path.exists(config_path)

def create_dirs():
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
