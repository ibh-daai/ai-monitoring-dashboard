"""
ETL pipeline script. This script is responsible for loading, validating, and splitting the data into reference and current data.
"""

import os
from src.data_preprocessing.fetch_data import fetch_and_merge
from src.data_preprocessing.validate import validate_data
from scripts.data_details import data_details
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_load_and_validate(config: dict) -> pd.DataFrame:
    """
    Load and validate data from the database
    """
    data = fetch_and_merge(config)

    # Validate the data
    try:
        validate_data(data, config)
    except ValueError as e:
        logger.error(f"Data validation failed: {e}")
        raise

    return data


def reference_load_and_validate(config: dict, data: pd.DataFrame) -> pd.DataFrame:
    """
    Load and validate reference data from the database or the provided data.
    """
    reference_data = None

    reference_path = "data/reference_data.csv"
    if os.path.exists(reference_path):
        reference_data = pd.read_csv(reference_path)

        # If the reference data is smaller than 50 rows, log a warning
        if len(reference_data) < 50:
            logger.warning("Reference data has less than 50 rows, consider updating the reference data.")
    else:
        logger.info("Reference data not found or empty, copying the current data.")
        reference_data = data.copy()
        reference_data.to_csv(reference_path, index=False)
    try:
        validate_data(reference_data, config)
    except ValueError as e:
        logger.error(f"Reference data validation failed: {e}")
        raise
    return reference_data


def set_details(data: pd.DataFrame, config: dict) -> None:
    """
    Get details about the data and store them in a JSON file.
    """
    data_details(data, config)


def etl_pipeline(config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETL pipeline for loading and validating data.
    """
    logger.info("Starting ETL pipeline...")
    data = main_load_and_validate(config)
    logger.info("Data loaded and validated successfully.")
    reference_data = reference_load_and_validate(config, data)
    logger.info("Reference data loaded and validated successfully.")
    set_details(data, config)
    logger.info("Details updated and saved successfully.")
    return data, reference_data
