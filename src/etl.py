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


def load_and_validate(config, file_path: str, reference_path: str = None) -> tuple:
    """
    Load and validate data from a CSV file
    """
    data, reference_data = load_data(file_path, reference_path)

    # Validate the data
    if not validate_data(data):
        logger.error(f"Data validation failed for main dataset: {file_path}")
        raise ValueError("Main data validation failed")

    # Validate the reference data if provided
    if config["model_config"].get("provide_reference", False) and reference_data:
        logger.debug("Validating reference data")
        if not validate_data(reference_data):
            logger.error("Reference data validation failed")
            raise ValueError("Reference data validation failed")

    return data, reference_data


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
    file_path: str, reference_path: str = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETL pipeline for loading, validating, and possibly splitting data.
    """
    config = load_config("config/config.json")
    data, reference_data = load_and_validate(config, file_path, reference_path)

    # Split the data into reference and current data if required
    if not config["model_config"].get("provide_reference", False):
        if not os.path.exists("data/reference_data.csv"):
            data, reference_data = split_to_reference_data(data)

            # write the data to a new CSV file
            data.to_csv("data/current_data.csv", index=False)
            reference_data.to_csv("data/reference_data.csv", index=False)
        else:
            logger.info("Reference data already exists.")
    else:
        logger.info("Reference data provided in the config file.")

    return data, reference_data


etl_pipeline("data/data.csv")
