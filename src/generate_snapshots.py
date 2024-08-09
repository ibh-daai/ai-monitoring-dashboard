"""
File to generate stratified reports and tests.
"""

import logging
import pandas as pd
import warnings
from src.config_manager import load_config
from src.metrics import generate_report
from src.tests import generate_tests
from src.etl import etl_pipeline
from src.stratify import DataSplitter
from sklearn.exceptions import UndefinedMetricWarning
from datetime import datetime
from scripts.data_details import load_details

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_stratified_reports(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    timestamp: str,
    splitter: DataSplitter,
    details: dict,
) -> None:
    """
    Generate the reports for each stratified dataset
    """
    try:
        data_stratifications = splitter.split_data(data, config, details, "report")
        for key, data_stratification in data_stratifications.items():
            logger.info(f"Generating reports for {key}")
            generate_report(
                data_stratification,
                reference_data,
                config,
                model_type,
                folder_path=f"/reports/{key}",
                timestamp=timestamp,
                details=details,
            )
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        raise


def generate_stratified_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    timestamp: str,
    splitter: DataSplitter,
    details: dict,
) -> None:
    """
    Generate the test suite for each stratified dataset
    """
    try:
        data_stratifications = splitter.split_data(data, config, details, "test")
        for key, data_stratification in data_stratifications.items():
            logger.info(f"Generating tests for {key}")
            generate_tests(
                data_stratification,
                reference_data,
                config,
                model_type,
                folder_path=f"/tests/{key}",
                timestamp=timestamp,
                details=details,
            )
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise


if __name__ == "__main__":
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)
    warnings.simplefilter(action="ignore", category=RuntimeWarning)
    warnings.simplefilter(action="ignore", category=UserWarning)

    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        exit(1)

    try:
        details = load_details()
    except Exception as e:
        logger.error(f"Failed to load data details: {e}")
        exit(1)

    try:
        data, reference_data = etl_pipeline(config)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        exit(1)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    splitter = DataSplitter()

    try:
        generate_stratified_reports(
            data,
            reference_data,
            config,
            config["model_config"]["model_type"],
            timestamp,
            splitter,
            details,
        )
    except Exception as e:
        logger.error(f"Failed to generate stratified reports: {e}")

    try:
        generate_stratified_tests(
            data,
            reference_data,
            config,
            config["model_config"]["model_type"],
            timestamp,
            splitter,
            details,
        )
    except Exception as e:
        logger.error(f"Failed to generate stratified tests: {e}")
