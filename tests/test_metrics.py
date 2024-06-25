"""
Script to test the metrics code.
"""

import pytest
import pandas as pd
from src.metrics import generate_report
from unittest.mock import patch


@pytest.fixture
def mock_config(monkeypatch):
    config = {
        "model_config": {
            "model_type": {"regression": False, "binary_classification": True}
        },
        "columns": {
            "study_id": "StudyID",
            "model_id": "ModelID",
            "predictions": {
                "regression_prediction": None,
                "classification_prediction": "class",
            },
            "labels": {
                "regression_label": None,
                "classification_label": "class_true",
            },
            "features": ["sex", "age", "bmi", "exercise_frequency", "diabetes"],
            "timestamp": "date",
        },
        "validation_rules": {
            "sex": {"type": "enum", "values": ["M", "F"]},
            "age": {"type": "range", "min": 0, "max": 120},
            "bmi": {"type": "range", "min": 0, "max": 50},
            "exercise_frequency": {
                "type": "enum",
                "values": ["daily", "weekly", "monthly", "never"],
            },
            "diabetes": {"type": "enum", "values": [1, 0]},
        },
    }
    #monkeypatch.setattr("src.config_manager.load_config", lambda x: config)
    return config


@pytest.fixture
def mock_data():
    return pd.DataFrame(
        {
            "StudyID": [1, 2, 3, 4],
            "ModelID": [1, 2, 3, 4],
            "class": [1, 0, 1, 0],
            "class_true": [1, 0, 1, 0],
            "sex": ["M", "F", "M", "F"],
            "age": [25, 30, 35, 40],
            "bmi": [20, 25, 30, 35],
            "exercise_frequency": ["daily", "monthly", "weekly", "never"],
            "diabetes": [1, 0, 1, 1],
        }
    )


@pytest.fixture
def mock_reference_data():
    return pd.DataFrame(
        {
            "StudyID": [1, 2, 3, 4],
            "ModelID": [1, 2, 3, 4],
            "class": [1, 0, 1, 1],
            "class_true": [1, 0, 1, 0],
            "sex": ["M", "M", "M", "F"],
            "age": [25, 30, 38, 20],
            "bmi": [20, 28, 40, 32],
            "exercise_frequency": ["daily", "monthly", "never", "weekly"],
            "diabetes": [0, 0, 1, 0],
        }
    )


def test_generate_report(mock_config, mock_data, mock_reference_data):
    with patch("src.metrics.data_report") as mock_data_report, patch(
        "src.metrics.classification_report"
    ) as mock_class_report, patch(
        "src.metrics.regression_report"
    ) as mock_regression_report:

        model_type = mock_config["model_config"]["model_type"]
        generate_report(mock_data, mock_reference_data, mock_config, model_type)

        # Check that data report and classification report are called
        mock_data_report.assert_called_once()
        mock_class_report.assert_called_once()

        # Check that regression report is not called
        mock_regression_report.assert_not_called()
