"""
File to handle test suite generation with Evidently AI. Split file into data, regression, and classification tests. Integrate with ETL pipeline.
"""

import pandas as pd
import warnings
import os
import logging
from sklearn.exceptions import UndefinedMetricWarning
from evidently.test_suite import TestSuite
from evidently.tests import (
    # Data tests
    TestNumberOfColumns,
    TestNumberOfEmptyRows,
    TestNumberOfDuplicatedRows,
    TestNumberOfMissingValues,
    # Column tests
    TestColumnAllUniqueValues,
    TestColumnValueMin,
    TestColumnValueMax,
    # Drift tests
    TestNumberOfDriftedColumns,
    TestShareOfDriftedColumns,
    # Regression tests
    TestValueMAE,
    TestValueRMSE,
    TestValueMeanError,
    TestValueMAPE,
    TestValueAbsMaxError,
    TestValueR2Score,
    # Classification tests
    TestAccuracyScore,
    TestPrecisionScore,
    TestRecallScore,
    TestF1Score,
    TestTNR,
    TestFPR,
    TestFNR,
)

from src.config_manager import load_config
from src.etl import etl_pipeline
from src.metrics import setup_column_mapping


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> None:
    """
    Check if the directory exists and create it if it doesn't.
    """
    base_dir = "test_suites/"
    full_path = os.path.join(base_dir, directory)
    logger.info(f"Directory {full_path} created.")
    if not os.path.exists(full_path):
        os.makedirs(full_path)


def regression_test_mapping() -> dict:
    """
    Generate the regression test mapping.
    """
    return {
        "mae": TestValueMAE(),
        "rmse": TestValueRMSE(),
        "mean_error": TestValueMeanError(),
        "mape": TestValueMAPE(),
        "absolute_max_error": TestValueAbsMaxError(),
        "r2": TestValueR2Score(),
    }


def get_regression_tests(config: dict) -> list:
    """
    Get the regression tests.
    """
    mapping = regression_test_mapping()

    # Add enabled tests from config to the list
    tests = []
    for test_config in config["tests"]["regression_tests"]:
        if test_config["enable"]:
            test_name = test_config["name"]
            tests.append(mapping[test_name])

    return tests


def classification_test_mapping() -> dict:
    """
    Generate the classification test mapping.
    """
    return {
        "accuracy": TestAccuracyScore(),
        "precision": TestPrecisionScore(),
        "recall": TestRecallScore(),
        "f1": TestF1Score(),
        "specificity": TestTNR(),
        "fpr": TestFPR(),
        "fnr": TestFNR(),
    }


def get_classification_tests(config: dict) -> list:
    """
    Get the classification tests.
    """
    mapping = classification_test_mapping()

    # Add enabled tests from config to the list
    tests = []
    for test_config in config["tests"]["classification_tests"]:
        if test_config["enable"]:
            test_name = test_config["name"]
            tests.append(mapping[test_name])

    return tests


def data_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate data test results.
    """
    ensure_directory(folder_path)
    data_mapping = setup_column_mapping(config, "data")
    data_test_suite = TestSuite(
        tests=[
            TestNumberOfColumns(),
            TestNumberOfEmptyRows(),
            TestNumberOfDuplicatedRows(),
            TestNumberOfMissingValues(),
            # consider column min/max here
            TestNumberOfDriftedColumns(),
            TestShareOfDriftedColumns(),
        ]
    )
    data_test_suite.run(
        reference_data=reference_data, current_data=data, column_mapping=data_mapping
    )
    data_test_suite.save(f"test_suites/{folder_path}/data_test_suite.json")


def regression_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate regression test results.
    """
    ensure_directory(folder_path)
    regression_mapping = setup_column_mapping(config, "regression")
    regression_test_suite = TestSuite(tests=get_regression_tests(config))
    regression_test_suite.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=regression_mapping,
    )
    regression_test_suite.save(f"test_suites/{folder_path}/regression_test_suite.json")


def classification_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate classification test results.
    """
    ensure_directory(folder_path)
    classification_mapping = setup_column_mapping(config, "classification")
    classification_test_suite = TestSuite(tests=get_classification_tests(config))
    classification_test_suite.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=classification_mapping,
    )
    classification_test_suite.save(
        f"test_suites/{folder_path}/classification_test_suite.json"
    )


def generate_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate the test suite based on the model type.
    """
    # Generate the data tests
    data_tests(data, reference_data, config, folder_path)

    # Generate the regression tests
    if model_type["regression"]:
        regression_tests(data, reference_data, config, folder_path)

    # Generate the classification tests
    if model_type["binary_classification"]:
        classification_tests(data, reference_data, config, folder_path)


def main():
    """
    Main function to run the test suite generation.
    """
    # Ignore warnings to clear output (for now)
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)

    # Load the configuration file
    config = load_config()

    # Extract the model type from the configuration file
    model_type = config["model_config"]["model_type"]

    # Load the data
    data, reference_data = etl_pipeline(
        "data/data.csv", "data/reference_data.csv", config
    )

    # Generate the test suite
    generate_tests(data, reference_data, config, model_type)


if __name__ == "__main__":
    main()
