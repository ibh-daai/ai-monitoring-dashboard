"""
File to load the JSON config file.
"""

import json

def load_config(filepath: str = "config/config.json") -> dict:
    """
    Load the JSON config file
    """
    try:
        with open(filepath, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {filepath}")
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON config.")
