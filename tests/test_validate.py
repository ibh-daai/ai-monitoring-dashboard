import pytest
import pandas as pd
from src.data_preprocessing.validate import validate_data
import numpy as np


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
            "instrument_type": "type",
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
    }


@pytest.fixture
def mock_details():
    """
    Fixture to mock the details file
    """
    return {
        "num_rows": 5,
        "hospital_unique_values": ["hospital1", "hospital2"],
        "sex_unique_values": ["M", "F"],
        "instrument_type_unique_values": ["type1", "type2"],
        "patient_class_unique_values": [],
        "categorical_columns": ["sex", "hospital", "type", "ethnicity"],
    }


@pytest.fixture
def correct_data():
    """
    Fixture to generate correct data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "sex": ["M", "F", "M"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
            "age": [9, 11, 34],
            "type": ["type1", "type2", "type1"],
            "regression_output": [17.1, 20.5, 30],
            "classification": [1, 0, 0],
            "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 200],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


@pytest.fixture
def data_with_wrong_types():
    """
    Fixture to generate data with wrong types for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "sex": ["M", "F", "M"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
            "age": [9, 11, 34],
            "type": ["type1", "type2", "type1"],
            "regression_output": ["ten", "twenty", "thirty"],  # Expected numeric
            "classification": [1, 0, 0],
            "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 170],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


@pytest.fixture
def large_data():
    """
    Fixture to generate larger data for testing
    """
    num_entries = 1000
    return pd.DataFrame(
        {
            "StudyID": ["ID" + str(i) for i in range(num_entries)],
            "sex": ["M", "F"] * (num_entries // 2),
            "age": [i % 100 for i in range(num_entries)],
            "hospital": ["hospital1", "hospital2"] * (num_entries // 2),
            "type": ["type1", "type2"] * (num_entries // 2),
            "regression_output": [i % 100 for i in range(num_entries)],
            "classification": [i % 2 for i in range(num_entries)],
            "label": [i % 100 for i in range(num_entries)],
            "classification_label": [i % 2 for i in range(num_entries)],
            "ethnicity": ["White", "Black", "Asian"] * (num_entries // 3) + ["White"],
            "height": [180, 160, 170] * (num_entries // 3) + [180],
            "weight": [80, 70, 75] * (num_entries // 3) + [80],
            "smoker": [True, False] * (num_entries // 2),
            "alcohol": [False, True] * (num_entries // 2),
        }
    )


@pytest.fixture
def corrupted_data():
    """
    Fixture to generate corrupted data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "sex": ["M", "F", "M"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
            "age": [9, 11, 34],
            "type": ["type1", "type2", "type1"],
            "regression_output": [
                10,
                20,
                np.nan,
            ],  # Missing value, replaced with np.nan
            "classification": [1, 0, 0],
            "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 170],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


@pytest.fixture
def missing_regression_output():
    """
    Fixture to generate data with missing regression output for testing
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "sex": ["M", "F", "M"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
            "age": [9, 11, 34],
            "type": ["type1", "type2", "type1"],
            # missing regression_output
            "classification": [1, 0, 0],
            "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 200],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


# Tests using the fixtures
def test_validate_correct_data(correct_data, mock_config):
    assert validate_data(correct_data, mock_config) == True


def test_validate_wrong_types(data_with_wrong_types, mock_config):
    with pytest.raises(ValueError):
        validate_data(data_with_wrong_types, mock_config)


def test_validate_large_data(large_data, mock_config):
    assert validate_data(large_data, mock_config) == True


def test_validate_corrupted_data(corrupted_data, mock_config):
    assert validate_data(corrupted_data, mock_config) == True


def test_validate_missing_regression_output(missing_regression_output, mock_config):
    with pytest.raises(ValueError):
        validate_data(missing_regression_output, mock_config)
