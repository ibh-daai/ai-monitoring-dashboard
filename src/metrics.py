"""
File to handle metric report generation with Evidently AI. Split file into data, regression, and classification metrics. Integrate with ETL pipeline.
"""

import os
from sklearn.exceptions import UndefinedMetricWarning
from src.config_manager import load_config
from src.etl import etl_pipeline
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    DatasetSummaryMetric,
    DatasetDriftMetric,
    DataDriftTable,
    ColumnDriftMetric,
    RegressionQualityMetric,
    RegressionPredictedVsActualScatter,
    RegressionPredictedVsActualPlot,
    RegressionErrorPlot,
    RegressionAbsPercentageErrorPlot,
    RegressionErrorDistribution,
    ClassificationQualityMetric,
    ClassificationConfusionMatrix,
    ClassificationClassBalance,
)
import warnings
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> None:
    """
    Check if the directory exists and create it if it doesn't.
    """
    base_dir = "reports/"
    full_path = os.path.join(base_dir, directory)
    print(f"Directory {full_path} created.")
    if not os.path.exists(full_path):
        os.makedirs(full_path)


def split_features(validation_rules: dict) -> tuple[list, list]:
    """
    Split the features into numerical and categorical based on the validation rules.
    """
    numerical_features = []
    categorical_features = []

    for feature, rules in validation_rules.items():
        if rules["type"] == "range":
            numerical_features.append(feature)
        elif rules["type"] == "enum":
            categorical_features.append(feature)

    return numerical_features, categorical_features


def setup_column_mapping(config: dict, report_type: str) -> ColumnMapping:
    """
    Configure column mapping for different types of reports based on the configuration.
    """
    features = split_features(config["validation_rules"])
    numerical_features, categorical_features = features

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


def data_report(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "reports",
) -> None:
    """
    Generate data quality metrics report.
    """
    ensure_directory(folder_path)
    data_mapping = setup_column_mapping(config, "data")
    """
    Data Quality Report:
    - Dataset Summary Metric: Summary statistics for the dataset
    - Dataset Drift Metric: Number and share of drifted features
    - Data Drift Table: Data drift results and visualizations for all columns (TODO: edit to include only specific columns)
    - Column Drift Metric: Detailed drift metrics for the prediction and target columns
    """
    data_quality_report = Report(
        metrics=[
            DatasetSummaryMetric(),
            DatasetDriftMetric(),
            DataDriftTable(),
            ColumnDriftMetric(data_mapping.prediction),
            ColumnDriftMetric(data_mapping.target),
        ],
    )
    data_quality_report.run(
        reference_data=reference_data, current_data=data, column_mapping=data_mapping
    )
    data_quality_report.save(f"reports/{folder_path}/data_quality_report.json")


def regression_report(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "reports",
) -> None:
    """
    Generate regression metrics report.
    """
    ensure_directory(folder_path)
    regression_mapping = setup_column_mapping(config, "regression")
    """
    Regression Report:
        - Regression Quality Metric: Regression quality metrics (RMSE, ME, MAE, MAPE, Max AE)
        - Regression Predicted vs Actual Scatter: Scatter plot of predicted vs actual values
        - Regression Predicted vs Actual Line: Line plot of predicted vs actual values
        - Regression Error Plot: Error plot of residuals
        - Regression Absolute Percentage Error Plot: Absolute percentage error plot
        - Regression Error Distribution: Distribution of errors
    """
    regression_report = Report(
        metrics=[
            RegressionQualityMetric(),
            RegressionPredictedVsActualScatter(),
            RegressionPredictedVsActualPlot(),
            RegressionErrorPlot(),
            RegressionAbsPercentageErrorPlot(),
            RegressionErrorDistribution(),
        ]
    )
    regression_report.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=regression_mapping,
    )
    regression_report.save(f"reports/{folder_path}/regression_report.json")


def classification_report(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    folder_path: str = "reports",
) -> None:
    """
    Generate classification metrics report.
    """
    ensure_directory(folder_path)
    classification_mapping = setup_column_mapping(config, "classification")
    """
    Classification Report:
        - Classification Quality Metric: Classification quality metrics (Accuracy, F1, Precision, Recall)
        - Classification Confusion Matrix: Confusion matrix for the classification predictions with TPR, FPR, FNR, TNR
        - Classification Class Balance: Class balance metrics
    """
    classification_report = Report(
        metrics=[
            ClassificationQualityMetric(),
            ClassificationConfusionMatrix(),
            ClassificationClassBalance(),
        ]
    )
    classification_report.run(
        reference_data=reference_data,
        current_data=data,
        column_mapping=classification_mapping,
    )
    classification_report.save(f"reports/{folder_path}/classification_report.json")


def generate_report(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    folder_path: str = "reports",
) -> None:
    """
    Generate the metrics report based on the model type.
    """
    # Generate the data quality metrics report
    data_report(data, reference_data, config, folder_path)

    # Generate the regression metrics report
    if model_type["regression"]:
        regression_report(data, reference_data, config, folder_path)

    # Generate the classification metrics report
    if model_type["binary_classification"]:
        classification_report(data, reference_data, config, folder_path)


def main():
    """
    Main function to generate metrics report.
    """
    # Ignore warnings to clear output (for now)
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)

    # Load the JSON config file
    config = load_config()

    # Extract model type from the config file
    model_type = config["model_config"]["model_type"]

    # Load the data
    data, reference_data = etl_pipeline(
        "data/data.csv", "data/reference_data.csv", config
    )

    # Generate the metrics report
    generate_report(data, reference_data, config, model_type)


if __name__ == "__main__":
    main()
