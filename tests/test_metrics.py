"""
Script to test the metrics code.
"""

import pytest
import pandas as pd
from src.metrics import generate_report
from unittest.mock import patch


@pytest.fixture
def mock_config():
    """
    Fixture to mock the configuration file
    """
    config = {
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
                "classification_prediction": "class",
            },
            "labels": {
                "regression_label": None,
                "classification_label": "class_true",
            },
            "features": ["bmi", "exercise_frequency", "diabetes"],
            "timestamp": "date",
        },
        "validation_rules": {
            "sex": ["M", "F"],
            "hospital": ["hospital1", "hospital2"],
            "instrument_type": ["type1", "type2"],
            "patient_category": ["IP", "OP"],
            "exercise_frequency": ["daily", "weekly", "monthly", "never"],
            "diabetes": [1, 0],
        },
    }
    return config


@pytest.fixture
def mock_data():
    """
    Fixture to generate mock data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": [1, 2, 3, 4],
            "sex": ["M", "F", "M", "F"],
            "hospital": ["hospital1", "hospital2", "hospital1", "hospital2"],
            "age": [25, 30, 35, 40],
            "instrument_type": ["type1", "type2", "type1", "type2"],
            "patient_category": ["IP", "OP", "IP", "OP"],
            "class": [1, 0, 1, 0],
            "class_true": [1, 0, 1, 0],
            "bmi": [20, 25, 30, 35],
            "exercise_frequency": ["daily", "monthly", "weekly", "never"],
            "diabetes": [1, 0, 1, 1],
        }
    )


@pytest.fixture
def mock_reference_data():
    """
    Fixture to generate mock reference data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": [1, 2, 3, 4],
            "sex": ["M", "F", "M", "F"],
            "hospital": ["hospital1", "hospital2", "hospital1", "hospital2"],
            "age": [25, 30, 35, 40],
            "instrument_type": ["type1", "type2", "type1", "type2"],
            "patient_category": ["IP", "OP", "IP", "OP"],
            "class": [1, 0, 1, 1],
            "class_true": [1, 0, 1, 0],
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
        generate_report(
            mock_data,
            mock_reference_data,
            mock_config,
            model_type,
            "folder",
            "timestamp",
        )

        # Check that data report and classification report are called
        mock_data_report.assert_called_once()
        mock_class_report.assert_called_once()

        # Check that regression report is not called
        mock_regression_report.assert_not_called()
