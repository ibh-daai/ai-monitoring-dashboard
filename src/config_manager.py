"""
File to load the JSON config file globally so it doesn't have to be loaded in every module.
"""

import json


def load_config(filepath):
    """
    Load the JSON config file
    """
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {filepath}")
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON config.")


_config = None


def get_config(filepath="config/config.json"):
    """
    Get the JSON config file
    """
    global _config
    if _config is None:
        _config = load_config(filepath)
    return _config
