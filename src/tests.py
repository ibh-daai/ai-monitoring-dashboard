"""
File to handle test suite generation with Evidently AI. Split file into data, regression, and classification tests. Integrate with ETL pipeline.
"""

from cgi import test
import pandas as pd
import warnings
import json
import importlib
import os
import logging
from sklearn.exceptions import UndefinedMetricWarning
from evidently.test_suite import TestSuite

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


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


def import_function(module_name: str, function_name: str):
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def get_tests(
    config: dict,
    tests_mapping: dict,
    test_type: str,
) -> list:
    print(test_type)
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
    return get_tests(config, tests_mapping, "data_quality_tests") + get_tests(
        config, tests_mapping, "data_drift_tests"
    )


def get_regression_tests(config: dict, tests_mapping: dict) -> list:
    return get_tests(config, tests_mapping, "regression_tests")


def get_classification_tests(config: dict, tests_mapping: dict) -> list:
    return get_tests(config, tests_mapping, "classification_tests")


def data_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    tests_mapping: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate data test results.
    """
    ensure_directory(folder_path)
    data_mapping = setup_column_mapping(config, "data")
    test_functions = get_data_tests(config, tests_mapping)

    data_test_suite = TestSuite(tests=test_functions)
    data_test_suite.run(
        reference_data=reference_data, current_data=data, column_mapping=data_mapping
    )
    data_test_suite.save(f"test_suites/{folder_path}/data_test_suite.json")


def regression_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    tests_mapping: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate regression test results.
    """
    ensure_directory(folder_path)
    regression_mapping = setup_column_mapping(config, "regression")
    test_functions = get_regression_tests(config, tests_mapping)

    regression_test_suite = TestSuite(tests=test_functions)
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
    tests_mapping: dict,
    folder_path: str = "test_results",
) -> None:
    """
    Generate classification test results.
    """
    ensure_directory(folder_path)
    classification_mapping = setup_column_mapping(config, "classification")
    test_functions = get_classification_tests(config, tests_mapping)

    classification_test_suite = TestSuite(tests=test_functions)
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
    with open("src/tests_map.json", "r") as f:
        tests_mapping = json.load(f)

    # Generate the data tests
    data_tests(data, reference_data, config, tests_mapping, folder_path)

    # Generate the regression tests
    if model_type["regression"]:
        regression_tests(data, reference_data, config, tests_mapping, folder_path)

    # Generate the classification tests
    if model_type["binary_classification"]:
        classification_tests(data, reference_data, config, tests_mapping, folder_path)


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
