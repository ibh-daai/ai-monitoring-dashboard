"""
ETL pipeline script. This script is responsible for loading, validating, and splitting the data into reference and current data.
"""

import os
from data_handler import load_data
from validate import validate_data, load_config
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_load_and_validate(config, file_path: str) -> pd.DataFrame:
    """
    Load and validate data from a CSV file
    """
    data, _ = load_data(file_path)

    # Validate the data
    if not validate_data(data):
        logger.error(f"Data validation failed for main dataset: {file_path}")
        raise ValueError("Main data validation failed")

    return data


def reference_load_and_validate(config, file_path: str, reference_path: str) -> pd.DataFrame:
    """
    Load and validate reference data from a CSV file
    """
    _, reference_data = load_data(file_path, reference_path)

    # Validate the reference data if provided
    if not validate_data(reference_data):
        logger.error("Reference data validation failed")
        raise ValueError("Reference data validation failed")

    return reference_data


def split_to_reference_data(data: pd.DataFrame, reference_size=0.25) -> pd.DataFrame:
    """
    Split the data into reference and current data using the sliding window method if required.
    """
    if len(data) <= 50:
        logger.error("Data length is less than the threshold for splitting. (50)")
        raise ValueError("Data length is less than the threshold for splitting. (50)")

    # Split the data into reference and current data
    reference_data = data.sample(frac=reference_size)
    data = data.drop(reference_data.index)
    return data, reference_data


def etl_pipeline(
    file_path: str, reference_path: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETL pipeline for loading, validating, and possibly splitting data.
    """
    config = load_config("config/config.json")
    data = main_load_and_validate(config, file_path)

    # Split the data into reference and current data if required
    if not config["model_config"].get("provide_reference", False):
        if not os.path.exists("data/reference_data.csv"):
            data, reference_data = split_to_reference_data(data)

            # write the data to a new CSV file
            data.to_csv("data/data.csv", index=False)
            reference_data.to_csv("data/reference_data.csv", index=False)
        else:
            logger.info("Reference data already exists.")
    else:
        if not os.path.exists("data/reference_data.csv"):
            logger.error("Reference data is required but not provided.")
            raise ValueError("Reference data is required but not provided.")
        logger.info("Reference data provided.")

    reference_data = reference_load_and_validate(config, file_path, reference_path)

    return data, reference_data
