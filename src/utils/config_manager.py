"""
File to load the JSON config file.
"""

import json


def load_config() -> dict:
    """
    Load the JSON config file
    """
    filepaths = [
        "config/config.json",
        "/app/config/config.json",
    ]
    for filepath in filepaths:

        try:
            with open(filepath, "r") as file:
                config = json.load(file)
            return config
        except FileNotFoundError:
            continue
    raise FileNotFoundError("Config file not found.")
