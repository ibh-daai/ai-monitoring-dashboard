"""
File to handle test suite generation with Evidently AI. Split file into data, regression, and classification tests. Integrate with ETL pipeline.
"""

import pandas as pd
import json
import importlib
import os
import logging
from evidently.test_suite import TestSuite
from src.monitoring.metrics import setup_column_mapping


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> None:
    """
    Check if the directory exists and create it if it doesn't.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_json(file_path: str) -> dict:
    """
    Load a JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def import_function(module_name: str, function_name: str):
    """
    Import a function from a module.
    """
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def get_tags(folder_path: str) -> list:
    """
    Get the tags from the folder path.
    """
    tags = folder_path.split("/")[-1].split("_")
    tags = tags[:-1]
    return tags


def get_tests(
    config: dict,
    tests_mapping: dict,
    test_type: str,
) -> list:
    """
    Get the tests from the configuration file, and use the mapping to get the test functions.
    """
    test_configs = config["tests"][test_type]
    tests = []
    for test_config in test_configs:
        test_name = test_config["name"]
        params = test_config.get("params", {})
        try:
            test_function = tests_mapping[test_type.replace("_tests", "")][test_name]
            module_name = "evidently.tests"
            test_class = import_function(module_name, test_function)
            tests.append(test_class(**params) if params else test_class())
        except KeyError as e:
            logger.error(f"KeyError: {e}")
        except Exception as e:
            logger.error(f"Error instantiating test {test_name}: {e}")
    return tests


def get_data_tests(config: dict, tests_mapping: dict) -> list:
    """
    Get the data tests from the config file.
    """
    return get_tests(config, tests_mapping, "data_quality_tests") + get_tests(
        config, tests_mapping, "data_drift_tests"
    )


def get_regression_tests(config: dict, tests_mapping: dict) -> list:
    """
    Get the regression tests from the config file.
    """
    return get_tests(config, tests_mapping, "regression_tests")


def get_classification_tests(config: dict, tests_mapping: dict) -> list:
    """
    Get the classification tests from the config file.
    """
    return get_tests(config, tests_mapping, "classification_tests")


def data_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    tests_mapping: dict,
    folder_path: str,
    timestamp: str,
    details: dict,
) -> None:
    """
    Generate data test results.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        data_mapping = setup_column_mapping(config, "data", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        return
    try:
        test_functions = get_data_tests(config, tests_mapping)

        t = get_tags(folder_path)
        if len(t) == 1:
            t.append("single")
        t.append("data")
        data_test_suite = TestSuite(tests=test_functions, tags=t, timestamp=timestamp)
        data_test_suite.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=data_mapping,
        )
        # will save to AWS S3 instead of local in the future
        data_test_suite.save(f"snapshots/{timestamp}/{folder_path}//data_test_suite.json")
    except Exception as e:
        logger.error(f"Error running data tests: {e}")
        return


def regression_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    tests_mapping: dict,
    folder_path: str,
    timestamp: str,
    details: dict,
) -> None:
    """
    Generate regression test results.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        regression_mapping = setup_column_mapping(config, "regression", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        return

    try:
        test_functions = get_regression_tests(config, tests_mapping)
        t = get_tags(folder_path)
        if len(t) == 1:
            t.append("single")
        t.append("regression")
        regression_test_suite = TestSuite(tests=test_functions, tags=t, timestamp=timestamp)
        regression_test_suite.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=regression_mapping,
        )
        regression_test_suite.save(f"snapshots/{timestamp}/{folder_path}/regression_test_suite.json")
    except Exception as e:
        logger.error(f"Error running regression tests: {e}")


def classification_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    tests_mapping: dict,
    folder_path: str,
    timestamp: str,
    details: dict,
) -> None:
    """
    Generate classification test results.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        classification_mapping = setup_column_mapping(config, "classification", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        return

    try:
        test_functions = get_classification_tests(config, tests_mapping)
        t = get_tags(folder_path)
        if len(t) == 1:
            t.append("single")
        t.append("classification")
        classification_test_suite = TestSuite(tests=test_functions, tags=t, timestamp=timestamp)
        classification_test_suite.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=classification_mapping,
        )
        classification_test_suite.save(f"snapshots/{timestamp}/{folder_path}/classification_test_suite.json")
    except Exception as e:
        logger.error(f"Error running classification tests: {e}")
        return


def generate_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    folder_path: str,
    timestamp: str,
    details: dict,
) -> None:
    """
    Generate the test suite based on the model type.
    """
    try:
        tests_mapping = load_json("src/utils/tests_map.json")
    except Exception as e:
        logger.error(f"Error loading tests mapping: {e}")
        return

    # Generate the data tests
    try:
        data_tests(data, reference_data, config, tests_mapping, folder_path, timestamp, details)
    except Exception as e:
        logger.error(f"Error running data tests: {e}")

    # Generate the regression tests
    if model_type["regression"]:
        try:
            regression_tests(data, reference_data, config, tests_mapping, folder_path, timestamp, details)
        except Exception as e:
            logger.error(f"Error running regression tests: {e}")

    # Generate the classification tests
    if model_type["binary_classification"]:
        try:
            classification_tests(data, reference_data, config, tests_mapping, folder_path, timestamp, details)
        except Exception as e:
            logger.error(f"Error running classification tests: {e}")
        return
