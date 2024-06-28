"""
File to load the JSON config file globally so it doesn't have to be loaded in every module.
"""

import json


def load_config(filepath="config/config.json"): 
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
