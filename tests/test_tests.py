import pytest
import pandas as pd
from src.tests import generate_tests
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
            "sex": "gender",
            "hospital": "clinic",
            "patient_class": "patient_category",
            "age": "age",
            "predictions": {
                "regression_prediction": None,
                "classification_prediction": "diagnosis",
            },
            "labels": {
                "regression_label": None,
                "classification_label": "diagnosis_true",
            },
            "features": ["weight", "height", "blood_pressure"],
            "timestamp": "date",
        },
        "tests": {
            "data_quality_tests": [
                {"name": "num_rows"},
                {"name": "num_empty_cols"},
                {"name": "num_duplicated_rows"},
                {
                    "name": "col_regex",
                    "params": {"column_name": "clinic", "regex": "clinic[1-3]"},
                },
                {"name": "num_missing_values"},
                {
                    "name": "test_col_range",
                    "params": {"column_name": "age", "min": 0, "max": 120},
                },
                {
                    "name": "test_col_list",
                    "params": {"column_name": "gender", "values": ["M", "F"]},
                },
            ],
            "data_drift_tests": [
                {"name": "num_drifted_cols"},
                {"name": "share_drifted_cols"},
            ],
            "regression_tests": [{"name": "rmse"}],
            "classification_tests": [
                {"name": "accuracy"},
                {"name": "precision"},
                {"name": "recall"},
                {"name": "f1"},
                {"name": "tnr"},
                {"name": "fpr"},
                {"name": "fnr"},
            ],
        },
    }
    return config


@pytest.fixture
def mock_details():
    return {
        "num_rows": 5,
        "statistical_terciles": [{"min": 0, "max": 0}, {"min": 0, "max": 0}, {"min": 0, "max": 0}],
        "hospital_unique_values": ["clinic1", "clinic2", "clinic3"],
        "sex_unique_values": ["M", "F"],
        "instrument_type_unique_values": [],
        "patient_class_unique_values": ["IP", "OP"],
        "categorical_columns": ["gender", "clinic", "patient_category"],
    }


@pytest.fixture
def mock_data():
    """
    Fixture to generate mock data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": [101, 102, 103, 104, 105],
            "gender": ["M", "F", "M", "F", "M"],
            "clinic": ["clinic1", "clinic2", "clinic1", "clinic2", "clinic1"],
            "patient_category": ["IP", "OP", "IP", "OP", "IP"],
            "age": [20, 25, 30, 35, 40],
            "diagnosis": [1, 0, 1, 0, 1],
            "diagnosis_true": [1, 0, 1, 0, 1],
            "weight": [70, 60, 80, 55, 90],
            "height": [170, 160, 180, 155, 190],
            "blood_pressure": [120, 110, 130, 115, 140],
        }
    )


@pytest.fixture
def mock_reference_data():
    """
    Fixture to generate mock reference data for testing
    """
    return pd.DataFrame(
        {
            "StudyID": [101, 102, 103, 104, 105],
            "gender": ["M", "F", "M", "F", "M"],
            "clinic": ["clinic1", "clinic2", "clinic1", "clinic2", "clinic1"],
            "patient_category": ["IP", "OP", "IP", "OP", "IP"],
            "age": [21, 26, 31, 36, 41],
            "diagnosis": [1, 0, 1, 1, 0],
            "diagnosis_true": [1, 0, 1, 0, 1],
            "weight": [71, 61, 81, 56, 91],
            "height": [171, 161, 181, 156, 191],
            "blood_pressure": [121, 111, 131, 116, 141],
        }
    )


def test_generate_tests(mock_config, mock_data, mock_reference_data):
    with patch("src.tests.data_tests") as mock_data_tests, patch(
        "src.tests.classification_tests"
    ) as mock_class_tests, patch("src.tests.regression_tests") as mock_regression_tests, patch("builtins.open"), patch(
        "json.load",
        return_value={
            "data_quality": {
                "num_rows": "TestNumberOfRows",
                "num_cols": "TestNumberOfColumns",
                "num_empty_rows": "TestNumberOfEmptyRows",
                "num_empty_cols": "TestNumberOfEmptyColumns",
                "num_duplicated_rows": "TestNumberOfDuplicatedRows",
                "num_duplicated_cols": "TestNumberOfDuplicatedColumns",
                "col_types": "TestColumnsType",
                "col_regex": "TestColumnRegExp",
                "num_missing_values": "TestNumberOfMissingValues",
                "share_missing_values": "TestShareOfMissingValues",
                "num_cols_with_missing_values": "TestNumberOfColumnsWithMissingValues",
                "num_rows_with_missing_values": "TestNumberOfRowsWithMissingValues",
                "test_col_range": "TestValueRange",
                "test_col_list": "TestValueList",
            },
            "data_drift": {
                "num_drifted_cols": "TestNumberOfDriftedColumns",
                "share_drifted_cols": "TestShareOfDriftedColumns",
                "test_drift": "TestColumnDrift",
            },
            "regression": {
                "mae": "TestValueMAE",
                "rmse": "TestValueRMSE",
                "me": "TestValueMeanError",
                "mape": "TestValueMAPE",
                "abs_max_error": "TestValueAbsMaxError",
                "r2": "TestValueR2Score",
            },
            "classification": {
                "accuracy": "TestAccuracyScore",
                "precision": "TestPrecisionScore",
                "recall": "TestRecallScore",
                "f1": "TestF1Score",
                "precision_by_class": "TestPrecisionByClass",
                "recall_by_class": "TestRecallByClass",
                "f1_by_class": "TestF1ByClass",
                "tpr": "TestTPR",
                "tnr": "TestTNR",
                "fpr": "TestFPR",
                "fnr": "TestFNR",
            },
        },
    ):

        model_type = mock_config["model_config"]["model_type"]
        generate_tests(
            mock_data,
            mock_reference_data,
            mock_config,
            model_type,
            "tests",
            "timestamp",
            mock_details,
        )

        # Check that data tests and classification tests are called
        mock_data_tests.assert_called_once()
        mock_class_tests.assert_called_once()

        # Check that regression tests are not called
        mock_regression_tests.assert_not_called()
