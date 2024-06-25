"""
File to handle metric report generation with Evidently AI. Split file into data, regression, and classification metrics. Integrate with ETL pipeline.
"""

from sklearn.exceptions import UndefinedMetricWarning
from src.validate import load_config
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

# Load the JSON config file
config = load_config("config/config.json")

# Extract model type from the config file
model_type = config["model_config"]["model_type"]

# Load the data
data, reference_data = etl_pipeline("data/data.csv", "data/reference_data.csv")


# split the features into numerical and categorical based on the validation rules
def split_features(validation_rules):
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


def data_report(data, reference_data, config):
    """
    Generate data quality metrics report.
    """
    data_mapping = ColumnMapping()

    # split the features into numerical and categorical based on the validation rules
    numerical_features, categorical_features = split_features(
        config["validation_rules"]
    )

    # if regression, use the regression label else use the classification label
    if config["model_config"]["model_type"]["regression"]:
        data_mapping.prediction = config["columns"]["predictions"][
            "regression_prediction"
        ]
        data_mapping.target = config["columns"]["labels"]["regression_label"]
        if config["model_config"]["model_type"]["binary_classification"]:
            categorical_features.append(
                config["columns"]["predictions"]["classification_prediction"]
            )
            categorical_features.append(
                config["columns"]["labels"]["classification_label"]
            )
    else:
        data_mapping.prediction = config["columns"]["predictions"][
            "classification_prediction"
        ]
        data_mapping.target = config["columns"]["labels"]["classification_label"]

    # check if timestamp is provided
    if config["columns"]["timestamp"]:
        data_mapping.datetime = config["columns"]["timestamp"]
    else:
        data_mapping.datetime = None

    data_mapping.id = config["columns"]["study_id"]
    data_mapping.numerical_features = numerical_features
    data_mapping.categorical_features = categorical_features

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
    data_quality_report.save_html("reports/data_quality_report.html")


def regression_report(data, reference_data, config):
    """
    Generate regression metrics report.
    """
    regression_mapping = ColumnMapping()

    regression_mapping.target = config["columns"]["labels"]["regression_label"]
    regression_mapping.prediction = config["columns"]["predictions"][
        "regression_prediction"
    ]
    regression_mapping.id = config["columns"]["study_id"]

    # check if timestamp is None
    if config["columns"]["timestamp"]:
        regression_mapping.datetime = config["columns"]["timestamp"]
    else:
        regression_mapping.datetime = None

    # split the features into numerical and categorical based on the validation rules
    numerical_features, categorical_features = split_features(
        config["validation_rules"]
    )

    regression_mapping.numerical_features = numerical_features
    regression_mapping.categorical_features = categorical_features

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
    regression_report.save_html("reports/regression_report.html")


def classification_report(data, reference_data, config):
    """
    Generate classification metrics report.
    """
    classification_mapping = ColumnMapping()

    classification_mapping.target = config["columns"]["labels"]["classification_label"]
    classification_mapping.prediction = config["columns"]["predictions"][
        "classification_prediction"
    ]
    classification_mapping.id = config["columns"]["study_id"]

    # check if timestamp is None
    if config["columns"]["timestamp"]:
        classification_mapping.datetime = config["columns"]["timestamp"]
    else:
        classification_mapping.datetime = None

    # split the features into numerical and categorical based on the validation rules
    numerical_features, categorical_features = split_features(
        config["validation_rules"]
    )

    classification_mapping.numerical_features = numerical_features
    classification_mapping.categorical_features = categorical_features

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
    classification_report.save_html("reports/classification_report.html")


def generate_report(data, reference_data, config):
    """
    Generate the metrics report based on the model type.
    """
    # Generate the data quality metrics report
    data_report(data, reference_data, config)

    # Generate the regression metrics report
    if model_type["regression"]:
        regression_report(data, reference_data, config)

    # Generate the classification metrics report
    if model_type["binary_classification"]:
        classification_report(data, reference_data, config)


def main():
    """
    Main function to generate metrics report.
    """
    # Ignore warnings to clear output (for now)
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)

    # Load the JSON config file
    config = load_config("config/config.json")

    # Load the data
    data, reference_data = etl_pipeline("data/data.csv", "data/reference_data.csv")

    # Generate the metrics report
    generate_report(data, reference_data, config)


if __name__ == "__main__":
    main()
