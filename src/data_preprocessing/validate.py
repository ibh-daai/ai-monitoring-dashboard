"""
Validate the data in a Dataframe to ensure it meets the requirements specified in the JSON config file and the JSON schema.
"""

import pandas as pd
import json
import jsonschema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def config_mappings(json_obj: dict, cols: dict = {}) -> dict:
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


def extract_columns(mapping: dict, columns: set, config: dict) -> set:
    """
    Extract column names from the mapping based on model configuration.
    """
    model_type = config["model_config"]["model_type"]
    for key, value in mapping.items():
        # Recursively extract columns from nested dictionaries
        if isinstance(value, dict):
            extract_columns(value, columns, config)
        # Feature columns
        elif isinstance(value, list):
            columns.update(value)
        elif value is not None:
            # Cases where the model_type is set to False, but its columns are present in the configuration.
            if key.startswith("regression") and not model_type.get("regression", False):
                continue
            if key.startswith("classification") and not model_type.get("binary_classification", False):
                continue
            columns.add(value)
        else:  # value is None
            # Cases where the model_type is set to True, but is columns are set to None in the configuration.
            if key.startswith("regression") and model_type.get("regression", False):
                raise ValueError(f"Regression column '{key}' is None, update config and/or data.")
            if key.startswith("classification") and model_type.get("binary_classification", False):
                raise ValueError(f"Classification column '{key}' is None, update config.")
    return columns


def construct_nested_json(row: pd.Series, mapping: dict) -> dict:
    """
    Construct JSON structure needed to validate a row of data against the JSON schema.
    """
    output = {
        "study_id": row[mapping["study_id"]],
        "sex": row[mapping["sex"]],
        "hospital": row[mapping["hospital"]],
        "age": row[mapping["age"]],
        "predictions": {},
        "labels": {},
        "features": {key: row[key] for key in mapping["features"] if key in row},
    }
    if mapping["instrument_type"] is not None and row[mapping["instrument_type"]]:
        output["instrument_type"] = row[mapping["instrument_type"]]
    if mapping["patient_class"] is not None and row[mapping["patient_class"]]:
        output["patient_class"] = row[mapping["patient_class"]]
    # Add prediction and label columns for both model types if they exist in the mapping
    if mapping.get("regression_prediction"):
        output["predictions"]["regression_prediction"] = row.get(mapping["regression_prediction"])
    if mapping.get("classification_prediction"):
        output["predictions"]["classification_prediction"] = row.get(mapping["classification_prediction"])

    if mapping.get("regression_label"):
        output["labels"]["regression_label"] = row.get(mapping["regression_label"])
    if mapping.get("classification_label"):
        output["labels"]["classification_label"] = row.get(mapping["classification_label"])

    return {"outputs": [output]}


def validate_row(row: pd.Series, mapping: dict, schema: dict) -> bool:
    """
    Validate a row of data against the JSON schema.
    """
    try:
        instance = construct_nested_json(row, mapping)
        jsonschema.validate(instance, schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        logger.warning(f"Validation error on row {row.to_dict()}: {err}")
        return False


def validate_schema(data: pd.DataFrame, mapping: dict) -> bool:
    """
    Validate the data in a dataframe against the JSON schema
    """
    # load the JSON schema file
    with open("config/schema.json", "r") as f:
        schema = json.load(f)

    # validate each row of the DataFrame
    valid_rows = data.apply(validate_row, axis=1, args=(mapping, schema))
    if not valid_rows.all():
        logger.error("Data validation failed.")
        raise ValueError("Data validation failed")
    return True


def validate_data(data: pd.DataFrame, config: dict) -> bool:
    """
    Main function to validate the data in a DataFrame
    """
    # extract model type from the config file
    model_type = config["model_config"]["model_type"]

    # if the DataFrame is empty, raise an error
    if data.empty:
        logger.info("No new data available. Pipeline will exit normally.")
        return False

    # call helper functions to extract mappings and columns
    mapping = config_mappings(config["columns"])
    columns = set()
    columns = extract_columns(mapping, columns, config)

    # Check for required columns in DataFrame (extra columns are allowed)
    if not columns.issubset(data.columns):
        missing_columns = columns - set(data.columns)
        logger.error(f"Missing required columns in DataFrame: {missing_columns}")
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")

    # Model type validation, check for prediction and label columns
    if model_type.get("regression", False):
        if "regression_prediction" not in mapping or "regression_label" not in mapping:
            logger.error("Regression columns are not properly configured.")
            raise ValueError("Regression columns are not properly configured.")
    if model_type.get("binary_classification", False):
        if "classification_prediction" not in mapping or "classification_label" not in mapping:
            logger.error("Classification columns are not properly configured.")
            raise ValueError("Classification columns are not properly configured.")

    # validate schema for each row of the DataFrame
    validate_schema(data, mapping)
    return True
