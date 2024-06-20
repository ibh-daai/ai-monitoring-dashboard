"""
Validate the data in a Datafram to ensure it meets the requirements specified in the JSON config file and the JSON schema.
"""

from unittest import result
import pandas as pd
import json
import jsonschema
from jsonschema import validate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(filepath):
    """
    Load configuration file.
    """
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {filepath}")
        raise
    except json.JSONDecodeError:
        logger.error("Error decoding JSON configuration.")
        raise


def config_mappings(json_obj, cols={}):
    """
    Extract column mappings from the JSON config file.
    """
    for key, value in json_obj.items():
        if isinstance(value, dict):
            config_mappings(value, cols)
        elif isinstance(value, list):
            cols[key] = value
        else:
            cols[key] = value
    return cols


def extract_columns(mapping, columns):
    """
    Extract column names from the mapping.
    """
    for key, value in mapping.items():
        if isinstance(value, dict):
            extract_columns(value, columns)
        elif isinstance(value, list):
            columns.update(value)
        elif value is not None:
            columns.add(value)
    return columns


def construct_nested_json(row, mapping):
    """
    Construct JSON structure needed to validate a row of data against the JSON schema.
    """
    result = {
        "outputs": [
            {
                "study_id": row[mapping["study_id"]],
                "model_id": row[mapping["model_id"]],
                "predictions": {
                    "regression_prediction": row[
                        mapping.get("regression_prediction", None)
                    ],
                    "classification_prediction": row[
                        mapping.get("classification_prediction", None)
                    ],
                },
                "labels": {
                    "regression_label": row[mapping.get("regression_label", None)],
                    "classification_label": row[
                        mapping.get("classification_label", None)
                    ],
                },
                "features": {
                    key: row[key] for key in mapping["features"] if key in row
                },
            }
        ]
    }
    return result


def validate_feature(data, feature, rules):
    """
    Validate a feature in the DataFrame against the rules specified in the JSON config file.
    """
    if feature not in data.columns:
        logger.error(f"Feature '{feature}' in validation rules not in DataFrame.")
        return False

    column_data = data[feature].dropna()
    rule_type = rules.get("type")

    if rule_type == "enum":
        if not column_data.isin(rules["values"]).all():
            logger.error(
                f"Value error for '{feature}': values not in {rules['values']}"
            )
            return False

    elif rule_type == "range":
        if not column_data.between(rules["min"], rules["max"]).all():
            logger.error(
                f"Value error for '{feature}': values out of range [{rules['min']}, {rules['max']}]"
            )
            return False
    else:
        logger.error(
            f"Unsupported rule type for '{feature}': {rule_type}. Please edit the JSON config file."
        )
        return False
    return True


def validate_row(row, mapping, schema):
    """
    Validate a row of data against the JSON schema.
    """
    try:
        instance = construct_nested_json(row, mapping)
        jsonschema.validate(instance, schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        logger.error(f"Validation error on row {row.to_dict()}: {err}")
        return False


def validate_schema(data: pd.DataFrame, mapping) -> bool:
    """
    Validate the data in a dataframe against the JSON schema
    """
    # load the JSON schema file
    with open("config/schema.json", "r") as f:
        schema = json.load(f)

    valid_rows = data.apply(validate_row, axis=1, args=(mapping, schema))
    if not valid_rows.all():
        logger.error("Data validation failed.")
        raise ValueError("Data validation failed")
    return True


def validate_data(data: pd.DataFrame) -> bool:
    """
    Main function to validate the data in a DataFrame
    """
    # if the DataFrame is empty, raise an error
    if data.empty:
        logger.error("DataFrame is empty.")
        raise ValueError("DataFrame is empty")
    # load the JSON config file
    config = load_config("config/config.json")

    # call helper functions to extract mappings and columns
    mapping = config_mappings(config["columns"])
    validation_rules = config["validation_rules"]
    model_type = config["model_config"]["model_type"]
    columns = set()
    columns = extract_columns(mapping, columns)

    # Check for required column presence in DataFrame
    if not columns.issubset(data.columns):
        missing_columns = columns - set(data.columns)
        logger.error(f"Missing required columns in DataFrame: {missing_columns}")
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # Model type validation, check for prediction and label columns
    if model_type["regression"]:
        if not mapping.get("regression_prediction") or not mapping.get(
            "regression_label"
        ):
            logger.error("Regression columns are not properly configured.")
            raise ValueError("Regression columns are not properly configured.")

    if model_type["binary_classification"]:
        if not mapping.get("classification_prediction") or not mapping.get(
            "classification_label"
        ):
            logger.error("Classification columns are not properly configured.")
            raise ValueError("Regression columns are not properly configured.")

    # check for duplicates
    if data.duplicated().any():
        raise ValueError("Data contains duplicates")

    # check for missing values
    if data.isnull().values.any():
        raise ValueError("Data contains missing values")

    # validate features
    for feature, rules in validation_rules.items():
        if not validate_feature(data, feature, rules):
            logger.error(f"Validation failed for feature '{feature}'")
            return False

    # validate schema for each row of the DataFrame
    validate_schema(data, mapping)
    logger.info("Data validation successful")
    return True


test_instance = {
    "outputs": [
        {
            "study_id": "003",
            "model_id": "Model1",
            "predictions": {
                "regression_prediction": "thirty",
                "classification_prediction": 0,
            },
            "labels": {"regression_label": 30, "classification_label": 1},
            "features": {
                "sex": "M",
                "age": 34,
                "ethnicity": "Asian",
                "height": 170,
                "weight": 75,
                "smoker": False,
                "alcohol": True,
            },
        }
    ]
}

try:
    with open("config/schema.json", "r") as f:
        schema = json.load(f)
    jsonschema.validate(instance=test_instance, schema=schema)
    print("Validation passed.")
except jsonschema.exceptions.ValidationError as err:
    print(f"Validation failed: {err}")
