import pytest
import pandas as pd
from src.stratify import DataSplitter
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_config():
    """
    Fixture to mock the configuration file
    """
    return {
        "model_config": {"model_type": {"regression": True, "binary_classification": True}},
        "columns": {
            "study_id": "StudyID",
            "sex": "sex",
            "hospital": "hospital",
            "age": "age",
            "instrument_type": None,
            "patient_class": None,
            "predictions": {
                "regression_prediction": "regression_output",
                "classification_prediction": "classification",
            },
            "labels": {
                "regression_label": "label",
                "classification_label": "classification_label",
            },
            "features": [
                "ethnicity",
                "height",
                "weight",
                "smoker",
                "alcohol",
            ],
            "timestamp": None,
        },
        "age_filtering": {
            "filter_type": "default",  # Default filter type; change this in tests
            "custom_ranges": [
                {"min": 0, "max": 17},
                {"min": 18, "max": 64},
                {"min": 65, "max": 120},
            ],
        },
    }


@pytest.fixture
def mock_details():
    """
    Fixture to mock the details file
    """
    return {
        "num_rows": 6,
        "statistical_terciles": [{"min": 0, "max": 0}, {"min": 0, "max": 0}, {"min": 0, "max": 0}],
        "hospital_unique_values": ["hospital1", "hospital2"],
        "sex_unique_values": ["M", "F"],
        "instrument_type_unique_values": [],
        "patient_class_unique_values": [],
        "categorical_columns": ["sex", "hospital", "ethnicity"],
    }


@pytest.fixture
def correct_data():
    """
    Fixture to generate correct data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003", "004", "005", "006"],
            "sex": ["M", "F", "M", "F", "M", "F"],
            "hospital": [
                "hospital1",
                "hospital2",
                "hospital1",
                "hospital2",
                "hospital1",
                "hospital2",
            ],
            "age": [9, 11, 34, 65, 78, 50],
            "regression_output": [17.1, 20.5, 30, 40, 50, 60],
            "classification": [1, 0, 0, 1, 0, 1],
            "label": [10, 20, 30, 40, 50, 60],
            "classification_label": [1, 0, 1, 0, 1, 0],
            "ethnicity": ["White", "Black", "Asian", "White", "Black", "Asian"],
            "height": [180, 160, 200, 150, 170, 180],
            "weight": [80, 70, 75, 60, 85, 90],
            "smoker": [True, False, False, True, False, True],
            "alcohol": [False, True, True, False, True, False],
        }
    )


splitter = DataSplitter()


def test_split_data_by_sex(correct_data, mock_config, mock_details):
    results = splitter.split_data(correct_data, mock_config, mock_details)
    assert all(results["male_report"]["sex"] == "M")
    assert all(results["female_report"]["sex"] == "F")
    assert len(results["male_report"]) == 3  # Expecting three males
    assert len(results["female_report"]) == 3  # Expecting three females


def test_split_data_by_hospital(correct_data, mock_config, mock_details):
    results = splitter.split_data(correct_data, mock_config, mock_details)
    assert all(results["hospital1_report"]["hospital"] == "hospital1")
    assert all(results["hospital2_report"]["hospital"] == "hospital2")
    assert len(results["hospital1_report"]) == 3  # Three records for hospital1
    assert len(results["hospital2_report"]) == 3  # Three records for hospital2


def test_split_data_by_age_default(correct_data, mock_config, mock_details):
    mock_config["age_filtering"]["filter_type"] = "default"
    results = splitter.stratify_age(correct_data, mock_config, mock_details)
    logger.debug(f"Results keys: {results.keys()}")
    assert all(results["[0-18]"]["age"] < 18)
    assert all((results["[18-65]"]["age"] >= 18) & (results["[18-65]"]["age"] <= 65))
    assert all(results["[65+]"]["age"] > 65)
    # confirm that all the data is accounted for
    assert len(results["[0-18]"]) + len(results["[18-65]"]) + len(results["[65+]"]) == len(correct_data)


def test_split_data_by_age_custom(correct_data, mock_config, mock_details):
    mock_config["age_filtering"]["filter_type"] = "custom"
    results = splitter.stratify_age(correct_data, mock_config, mock_details)
    logger.debug(f"Results keys: {results.keys()}")
    for custom_range in mock_config["age_filtering"]["custom_ranges"]:
        key = f"[{custom_range['min']}-{custom_range['max']}]"
        assert all((results[key]["age"] >= custom_range["min"]) & (results[key]["age"] <= custom_range["max"]))


def test_split_data_by_age_invalid(correct_data, mock_config, mock_details):
    mock_config["age_filtering"]["filter_type"] = "invalid"
    results = splitter.stratify_age(correct_data, mock_config, mock_details)
    logger.debug(f"Results keys: {results.keys()}")
    assert all(results["[0-18]"]["age"] < 18)
    assert all((results["[18-65]"]["age"] >= 18) & (results["[18-65]"]["age"] <= 65))
    assert all(results["[65+]"]["age"] > 65)
