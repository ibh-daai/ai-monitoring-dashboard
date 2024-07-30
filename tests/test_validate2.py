import pytest
import pandas as pd
from src.validate import validate_data


@pytest.fixture
def mock_config():
    """
    Fixture to mock the configuration file
    """
    return {
        "model_config": {
            "model_type": {"regression": False, "binary_classification": True}
        },
        "columns": {
            "study_id": "StudyID",
            "sex": "sex",
            "hospital": "hospital",
            "age": "age",
            "instrument_type": "instrument_type",
            "patient_class": "patient_category",
            "predictions": {
                "regression_prediction": None,
                "classification_prediction": "classification",
            },
            "labels": {
                "regression_label": None,
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
        "validation_rules": {
            "sex": ["M", "F"],
            "hospital": ["hospital1", "hospital2"],
            "instrument_type": ["type1", "type2"],
            "patient_category": ["IP", "OP", "ER"],
            "ethnicity": ["White", "Black", "Asian"],
            "smoker": [True, False],
            "alcohol": [True, False],
        },
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
            "instrument_type": ["type1", "type2", "type1"],
            "patient_category": ["IP", "OP", "ER"],
            # "regression_output": [17.1, 20.5, 30],
            "classification": [1, 0, 0],
            # "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 200],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


@pytest.fixture
def including_regression():
    """
    Fixture to generate data including regression output
    """
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "sex": ["M", "F", "M"],
            "age": [9, 11, 34],
            "instrument_type": ["type1", "type2", "type1"],
            "patient_category": ["IP", "OP", "ER"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
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


def test_validate_data_including_regression(including_regression, mock_config):
    assert validate_data(including_regression, mock_config) == True
