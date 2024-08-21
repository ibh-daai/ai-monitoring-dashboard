"""
Script for comparing and storing details about the expected data.
"""

import logging
import os
import pandas as pd
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DETAILS_FILE_PATH = "src/utils/details.json"


def load_details(file_path=DETAILS_FILE_PATH) -> dict:
    """
    Load the details JSON file. If the file doesn't exist, create it with a default structure.
    """
    default_content = {
        "num_rows": 0,
        "hospital_unique_values": [],
        "sex_unique_values": [],
        "instrument_type_unique_values": [],
        "patient_class_unique_values": [],
        "categorical_columns": [],
    }

    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump(default_content, file, indent=2)
            logger.info(f"Created new details file at {file_path}")
        return default_content

    with open(file_path, "r") as file:
        return json.load(file)


def save_details(details: dict, file_path=DETAILS_FILE_PATH) -> None:
    """
    Save the updated details dictionary to the JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(details, file, indent=2)
        logger.info(f"Details updated and saved to {file_path}")


def update_details(data: pd.DataFrame, config: dict, details: dict) -> dict:
    """
    Update the details dictionary with new data and return the updated dictionary.
    """
    logger.info("Updating details...")

    if details["num_rows"] == 0:
        details["num_rows"] = len(data)

    update_unique_values(data, config, details)
    set_categorical_columns(data, config, details)

    return details



def update_unique_values(data: pd.DataFrame, config: dict, details: dict) -> None:
    """
    Update the unique values for the categorical columns in the details dictionary.
    """
    for key in ["hospital", "sex", "instrument_type", "patient_class"]:
        if config["columns"].get(key):
            unique_values = data[config["columns"][key]].unique().tolist()
            details_key = f"{key}_unique_values"
            details[details_key] = list(set(details[details_key] + unique_values))


def set_categorical_columns(data: pd.DataFrame, config: dict, details: dict) -> None:
    """
    Identify and set the categorical columns in the details dictionary.
    """
    for column in data.columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            if (
                column not in details["categorical_columns"]
                and column != config["columns"]["timestamp"]
                and column != "timestamp"
            ):
                details["categorical_columns"].append(column)


def data_details(data: pd.DataFrame, config: dict, file_path=DETAILS_FILE_PATH) -> None:
    """
    Function to handle the process of updating and saving details.
    """
    details = load_details(file_path)
    updated_details = update_details(data, config, details)
    save_details(updated_details, file_path)
