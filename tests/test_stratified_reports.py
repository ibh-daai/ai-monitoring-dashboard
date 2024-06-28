import pytest
import pandas as pd
from src.stratified_reports import split_data


@pytest.fixture
def mock_config():
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
        "validation_rules": {
            "sex": {"type": "enum", "values": ["M", "F"]},
            "hospital": {"type": "enum", "values": ["hospital1", "hospital2"]},
            "age": {"type": "range", "min": 0, "max": 120},
            "ethnicity": {"type": "enum", "values": ["White", "Black", "Asian"]},
            "height": {"type": "range", "min": 50, "max": 250},
            "weight": {"type": "range", "min": 2, "max": 500},
            "smoker": {"type": "enum", "values": [True, False]},
            "alcohol": {"type": "enum", "values": [True, False]},
        },
    }


@pytest.fixture
def correct_data():
    return pd.DataFrame(
        {
            "StudyID": ["001", "002", "003"],
            "ModelID": ["Model1", "Model1", "Model1"],
            "sex": ["M", "F", "M"],
            "hospital": ["hospital1", "hospital2", "hospital1"],
            "age": [9, 11, 34],
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


def test_split_data_by_sex(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["male_report"]["sex"] == "M")
    assert all(results["female_report"]["sex"] == "F")
    assert len(results["male_report"]) == 2  # Expecting two males in the correct_data
    assert (
        len(results["female_report"]) == 1
    )  # Expecting one female in the correct_data


def test_split_data_by_hospital(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    assert all(results["hospital1"]["hospital"] == "hospital1")
    assert all(results["hospital2"]["hospital"] == "hospital2")
    assert len(results["hospital1"]) == 2  # Two records for hospital1
    assert len(results["hospital2"]) == 1  # One record for hospital2


def test_split_data_by_age_tertiles(correct_data, mock_config):
    results = split_data(correct_data, mock_config)
    # These checks assume tertiles are split at the 33rd and 66th percentiles of ages in correct_data
    # which are 9, 11, and 34. Thus, tertiles would split at around 11 and 22.
    assert all(
        results["age1"]["age"] <= 11
    )  # The first tertile should have the youngest age group
    assert all(
        (results["age2"]["age"] >= 11) & (results["age2"]["age"] <= 22)
    )  # Second tertile
    assert all(results["age3"]["age"] >= 22)  # Third tertile


def test_split_data_completeness(correct_data, mock_config):
    # Ensure no data is lost in the split
    results = split_data(correct_data, mock_config)
    combined_df = pd.concat(
        [
            results["male_report"],
            results["female_report"],
            results["hospital1"],
            results["hospital2"],
            results["age1"],
            results["age2"],
            results["age3"],
        ],
        ignore_index=True,
    )
    # Deduplicate because the same row will appear in multiple reports if it fits their criteria
    combined_df = combined_df.drop_duplicates()
    assert len(combined_df) == len(
        correct_data
    ) 
