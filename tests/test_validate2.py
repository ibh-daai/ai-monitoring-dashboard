import pytest
import pandas as pd
from src.validate import validate_data

@pytest.fixture
def correct_data():
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "ModelID": ["Model1", "Model1", "Model1"],
            # "regression_output": [17.1, 20.5, 30],
            "classification": [1, 0, 0],
            # "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "sex": ["M", "F", "M"],
            "age": [9, 11, 34],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 200],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


@pytest.fixture
def including_regression():
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "ModelID": ["Model1", "Model1", "Model1"],
            "regression_output": [17.1, 20.5, 30],
            "classification": [1, 0, 0],
            "label": [10, 20, 30],
            "classification_label": [1, 0, 1],
            "sex": ["M", "F", "M"],
            "age": [9, 11, 34],
            "ethnicity": ["White", "Black", "Asian"],
            "height": [180, 160, 200],
            "weight": [80, 70, 75],
            "smoker": [True, False, False],
            "alcohol": [False, True, True],
        }
    )


# Mocking configuration load using pytest fixture
@pytest.fixture
def mock_config():
    return {
        "model_config": {
            "model_type": {"regression": False, "binary_classification": True}
        },
        "columns": {
            "study_id": "StudyID",
            "model_id": "ModelID",
            "predictions": {
                "regression_prediction": None,
                "classification_prediction": "classification",
            },
            "labels": {
                "regression_label": None,
                "classification_label": "classification_label",
            },
            "features": [
                "sex",
                "age",
                "ethnicity",
                "height",
                "weight",
                "smoker",
                "alcohol",
            ],
            "timestamp": None,
        },
        "validation_rules": {
            "sex": {"type": "enum", "values": ["M", "F"]},
            "age": {"type": "range", "min": 0, "max": 120},
            "ethnicity": {"type": "enum", "values": ["White", "Black", "Asian"]},
            "height": {"type": "range", "min": 50, "max": 250},
            "weight": {"type": "range", "min": 2, "max": 500},
            "smoker": {"type": "enum", "values": [True, False]},
            "alcohol": {"type": "enum", "values": [True, False]},
        },
    }

# Tests using the fixtures
def test_validate_data_correct(correct_data, mock_config):
    assert validate_data(correct_data, mock_config) == True


def test_validate_data_including_regression(including_regression, mock_config):
    assert validate_data(including_regression, mock_config) == True
