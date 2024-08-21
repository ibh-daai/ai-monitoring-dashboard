"""
File to handle metric report generation with Evidently AI. Split file into data, regression, and classification metrics. Integrate with ETL pipeline.
"""

import os
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    DatasetSummaryMetric,
    DatasetDriftMetric,
    DataDriftTable,
    ColumnDriftMetric,
    RegressionQualityMetric,
    RegressionPredictedVsActualScatter,
    ClassificationQualityMetric,
    ClassificationConfusionMatrix,
)
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> None:
    """
    Check if the directory exists and create it if it doesn't.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_tags(folder_path: str) -> list:
    """
    Get the tags from the folder path.
    """
    tags = folder_path.split("/")[-1].split("_")
    tags = tags[:-1]
    return tags


def split_features(config: dict, details: dict) -> tuple[list, list]:
    """
    Split the features into numerical and categorical based on the validation rules.
    """
    numerical_features = []
    categorical_features = []

    categorical_features.extend(
        [
            config["columns"]["sex"],
            config["columns"]["hospital"],
        ]
    )

    if config["columns"]["instrument_type"]:
        categorical_features.append(config["columns"]["instrument_type"])

    if config["columns"]["patient_class"]:
        categorical_features.append(config["columns"]["patient_class"])

    # Iterate through all features to classify them based on validation rules
    for feature in config["columns"]["features"]:
        if feature in details["categorical_columns"]:
            if feature not in categorical_features:
                categorical_features.append(feature)
        else:
            numerical_features.append(feature)

    # Correctly classify 'age' as a numerical feature
    if config["columns"]["age"] not in numerical_features:
        numerical_features.append(config["columns"]["age"])

    return numerical_features, categorical_features


def setup_column_mapping(config: dict, report_type: str, details: dict) -> ColumnMapping:
    """
    Configure column mapping for different types of reports based on the configuration.
    """
    features = split_features(config, details)
    numerical_features, categorical_features = features

    try:
        mapping = ColumnMapping()
        mapping.id = config["columns"]["study_id"]
        mapping.datetime = config["columns"]["timestamp"]
        mapping.numerical = numerical_features
        mapping.categorical = categorical_features

        predictions = config["columns"]["predictions"]
        labels = config["columns"]["labels"]

        if report_type == "data":
            mapping.target = labels["regression_label"]
            mapping.prediction = predictions["regression_prediction"]
            if config["model_config"]["model_type"]["binary_classification"]:
                categorical_features.append(predictions["classification_prediction"])
                categorical_features.append(labels["classification_label"])
        elif report_type == "regression":
            mapping.target = labels["regression_label"]
            mapping.prediction = predictions["regression_prediction"]
        elif report_type == "classification":
            mapping.target = labels["classification_label"]
            mapping.prediction = predictions["classification_prediction"]
        else:
            logger.error("Incorrect report type")
            raise ValueError("Incorrect report type")

        return mapping
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise ValueError(f"Missing config key: {e}. Please fix the config.") from e


def data_report(
    data: pd.DataFrame, reference_data: pd.DataFrame, config: dict, folder_path: str, timestamp: str, details: dict
) -> None:
    """
    Generate data quality metrics report.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        data_mapping = setup_column_mapping(config, "data", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        raise
    """
    Data Quality Report:
    - Dataset Summary Metric: Summary statistics for the dataset
    - Dataset Drift Metric: Number and share of drifted features
    - Data Drift Table: Data drift results and visualizations for all columns (TODO: edit to include only specific columns)
    - Column Drift Metric: Detailed drift metrics for the prediction and target columns
    """
    t = get_tags(folder_path)
    if len(t) == 1:
        t.append("single")
    t.append("data")
    data_quality_report = Report(
        metrics=[
            DatasetSummaryMetric(),
            DatasetDriftMetric(),
            DataDriftTable(),
            ColumnDriftMetric(data_mapping.prediction),
            ColumnDriftMetric(data_mapping.target),
        ],
        tags=t,
        timestamp=timestamp,
    )
    data_quality_report.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=data_mapping,
    )
    data_quality_report.save(f"snapshots/{timestamp}/{folder_path}/data_quality_report.json")


def regression_report(
    data: pd.DataFrame, reference_data: pd.DataFrame, config: dict, folder_path: str, timestamp: str, details: dict
) -> None:
    """
    Generate regression metrics report.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        regression_mapping = setup_column_mapping(config, "regression", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        raise
    """
    Regression Report:
        - Regression Quality Metric: Regression quality metrics (RMSE, ME, MAE, MAPE, Max AE)
        - Regression Predicted vs Actual Scatter: Scatter plot of predicted vs actual values
        - Regression Predicted vs Actual Line: Line plot of predicted vs actual values
        - Regression Error Plot: Error plot of residuals
        - Regression Absolute Percentage Error Plot: Absolute percentage error plot
        - Regression Error Distribution: Distribution of errors
    """
    t = get_tags(folder_path)
    if len(t) == 1:
        t.append("single")
    t.append("regression")
    regression_report = Report(
        metrics=[
            RegressionQualityMetric(),
            RegressionPredictedVsActualScatter(),
        ],
        tags=t,
        timestamp=timestamp,
    )
    regression_report.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=regression_mapping,
    )
    regression_report.save(f"snapshots/{timestamp}/{folder_path}/regression_report.json")


def classification_report(
    data: pd.DataFrame, reference_data: pd.DataFrame, config: dict, folder_path: str, timestamp: str, details: dict
) -> None:
    """
    Generate classification metrics report.
    """
    ensure_directory(f"snapshots/{timestamp}/{folder_path}")
    try:
        classification_mapping = setup_column_mapping(config, "classification", details)
    except Exception as e:
        logger.error(f"Error setting up column mapping: {e}")
        raise
    """
    Classification Report:
        - Classification Quality Metric: Classification quality metrics (Accuracy, F1, Precision, Recall)
        - Classification Confusion Matrix: Confusion matrix for the classification predictions with TPR, FPR, FNR, TNR
        - Classification Class Balance: Class balance metrics
    """
    t = get_tags(folder_path)
    if len(t) == 1:
        t.append("single")
    t.append("classification")
    classification_report = Report(
        metrics=[
            ClassificationQualityMetric(),
            ClassificationConfusionMatrix(),
        ],
        tags=t,
        timestamp=timestamp,
    )
    classification_report.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=classification_mapping,
    )
    classification_report.save(f"snapshots/{timestamp}/{folder_path}/classification_report.json")


def generate_report(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    folder_path: str,
    timestamp: str,
    details: dict,
) -> None:
    """
    Generate the metrics report based on the model type.
    """
    try:
        # Generate the data quality report
        data_report(data, reference_data, config, folder_path, timestamp, details)
    except Exception as e:
        logger.error(f"Failed to generate data quality report: {e}")

    # Generate the regression and classification reports based on the model type
    if model_type["regression"]:
        try:
            regression_report(data, reference_data, config, folder_path, timestamp, details)
        except Exception as e:
            logger.error(f"Failed to generate regression report: {e}")

    if model_type["binary_classification"]:
        try:
            classification_report(data, reference_data, config, folder_path, timestamp, details)
        except Exception as e:
            logger.error(f"Failed to generate classification report: {e}")
