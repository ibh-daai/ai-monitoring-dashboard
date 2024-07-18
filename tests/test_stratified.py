import pytest
import pandas as pd
from src.stratify import split_data, stratify_age, stratify_sex, stratify_list
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_config():
    """
    Fixture to mock the configuration file
    """
    return {
        "model_config": {
            "model_type": {"regression": True, "binary_classification": True}
        },
        "columns": {
            "study_id": "StudyID",
            "model_id": "ModelID",
            "sex": "sex",
            "hospital": "hospital",
            "age": "age",
            "instrument_type": "instrument_type",
            "patient_class": "patient_category",
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
        "categorical_validation_rules": {
            "sex": ["M", "F"],
            "hospital": ["hospital1", "hospital2"],
            "instrument_type": ["type1", "type2"],
            "patient_category": ["IP", "OP", "ER"],
            "ethnicity": ["White", "Black", "Asian"],
            "smoker": [True, False],
            "alcohol": [True, False],
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
def correct_data():
    """
    Fixture to generate correct data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003", "004", "005", "006"],
            "ModelID": ["Model1", "Model1", "Model1", "Model1", "Model1", "Model1"],
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
            "instrument_type": ["type1", "type2", "type1", "type2", "type1", "type2"],
            "patient_category": ["IP", "OP", "IP", "OP", "ER", "ER"],
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


def test_split_data_by_sex(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["male_report"]["sex"] == "M")
    assert all(results["female_report"]["sex"] == "F")
    assert len(results["male_report"]) == 3  # Expecting three males
    assert len(results["female_report"]) == 3  # Expecting three females


def test_split_data_by_hospital(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["hospital1_report"]["hospital"] == "hospital1")
    assert all(results["hospital2_report"]["hospital"] == "hospital2")
    assert len(results["hospital1_report"]) == 3  # Three records for hospital1
    assert len(results["hospital2_report"]) == 3  # Three records for hospital2


def test_split_data_by_instrument_type(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["type1_report"]["instrument_type"] == "type1")
    assert all(results["type2_report"]["instrument_type"] == "type2")
    assert len(results["type1_report"]) == 3  # Three records for instrument type 1
    assert len(results["type2_report"]) == 3  # Three records for instrument type 2


def test_split_data_by_patient_category(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["IP_report"]["patient_category"] == "IP")
    assert all(results["OP_report"]["patient_category"] == "OP")
    assert all(results["ER_report"]["patient_category"] == "ER")
    assert len(results["IP_report"]) == 2  # Two records for IP
    assert len(results["OP_report"]) == 2  # Two records for OP
    assert len(results["ER_report"]) == 2  # Two records for ER


def test_split_data_by_age_default(correct_data, mock_config):
    mock_config["age_filtering"]["filter_type"] = "default"
    results = stratify_age(correct_data, mock_config)
    logger.debug(f"Results keys: {results.keys()}")
    assert all(results["[0-18]"]["age"] < 18)
    assert all((results["[18-65]"]["age"] >= 18) & (results["[18-65]"]["age"] <= 65))
    assert all(results["[65+]"]["age"] > 65)
    # confirm that all the data is accounted for
    assert len(results["[0-18]"]) + len(results["[18-65]"]) + len(
        results["[65+]"]
    ) == len(correct_data)


def test_split_data_by_age_statistical(correct_data, mock_config):
    mock_config["age_filtering"]["filter_type"] = "statistical"
    results = stratify_age(correct_data, mock_config)
    logger.debug(f"Results keys: {results.keys()}")
    sorted_ages = correct_data[mock_config["columns"]["age"]].sort_values()
    tercile_size = len(sorted_ages) // 3
    cutoff1 = sorted_ages.iloc[tercile_size - 1]
    cutoff2 = sorted_ages.iloc[2 * tercile_size - 1]
    assert all(results[f"[{int(sorted_ages.min())}-{int(cutoff1)}]"]["age"] <= cutoff1)
    assert all(
        (results[f"[{int(cutoff1)}-{int(cutoff2)}]"]["age"] > cutoff1)
        & (results[f"[{int(cutoff1)}-{int(cutoff2)}]"]["age"] <= cutoff2)
    )
    assert all(results[f"[{int(cutoff2)}-{int(sorted_ages.max())}]"]["age"] > cutoff2)

    # confirm that all the data is accounted for
    assert len(results[f"[{int(sorted_ages.min())}-{int(cutoff1)}]"]) + len(
        results[f"[{int(cutoff1)}-{int(cutoff2)}]"]
    ) + len(results[f"[{int(cutoff2)}-{int(sorted_ages.max())}]"]) == len(correct_data)


def test_split_data_by_age_custom(correct_data, mock_config):
    mock_config["age_filtering"]["filter_type"] = "custom"
    results = stratify_age(correct_data, mock_config)
    logger.debug(f"Results keys: {results.keys()}")
    for custom_range in mock_config["age_filtering"]["custom_ranges"]:
        key = f"[{custom_range['min']}-{custom_range['max']}]"
        assert all(
            (results[key]["age"] >= custom_range["min"])
            & (results[key]["age"] <= custom_range["max"])
        )


def test_split_data_by_age_invalid(correct_data, mock_config):
    mock_config["age_filtering"]["filter_type"] = "invalid"
    results = stratify_age(correct_data, mock_config)
    logger.debug(f"Results keys: {results.keys()}")
    assert all(results["[0-18]"]["age"] < 18)
    assert all((results["[18-65]"]["age"] >= 18) & (results["[18-65]"]["age"] <= 65))
    assert all(results["[65+]"]["age"] > 65)
