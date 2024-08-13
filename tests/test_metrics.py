"""
Script to test the metrics code.
"""

import pytest
import pandas as pd
from src.monitoring.metrics import generate_report
from unittest.mock import patch


@pytest.fixture
def mock_config():
    """
    Fixture to mock the configuration file
    """
    config = {
        "model_config": {"model_type": {"regression": False, "binary_classification": True}},
        "columns": {
            "study_id": "StudyID",
            "sex": "sex",
            "hospital": "hospital",
            "age": "age",
            "instrument_type": None,  # equivalent to JSON null
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
    }
    return config


@pytest.fixture
def mock_details():
    """
    Fixture to mock the details file
    """
    return {
        "num_rows": 4,
        "statistical_terciles": [{"min": 0, "max": 0}, {"min": 0, "max": 0}, {"min": 0, "max": 0}],
        "hospital_unique_values": ["hospital1", "hospital2"],
        "sex_unique_values": ["M", "F"],
        "instrument_type_unique_values": [],
        "patient_class_unique_values": ["IP", "OP"],
        "categorical_columns": ["sex", "hospital", "patient_category", "exercise_frequency"],
    }


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
            "patient_category": ["IP", "OP", "IP", "OP"],
            "class": [1, 0, 1, 1],
            "class_true": [1, 0, 1, 0],
            "bmi": [20, 28, 40, 32],
            "exercise_frequency": ["daily", "monthly", "never", "weekly"],
            "diabetes": [0, 0, 1, 0],
        }
    )


def test_generate_report(mock_config, mock_data, mock_reference_data, mock_details):
    with patch("src.monitoring.metrics.data_report") as mock_data_report, patch(
        "src.monitoring.metrics.classification_report"
    ) as mock_class_report, patch("src.monitoring.metrics.regression_report") as mock_regression_report:

        model_type = mock_config["model_config"]["model_type"]
        generate_report(
            mock_data,
            mock_reference_data,
            mock_config,
            model_type,
            "folder",
            "timestamp",
            mock_details,
        )

        # Check that data report and classification report are called
        mock_data_report.assert_called_once()
        mock_class_report.assert_called_once()

        # Check that regression report is not called
        mock_regression_report.assert_not_called()
