"""
validate the data in a dataframe against the JSON schema, using the JSON config file
"""

import pandas as pd
import json
import jsonschema
from jsonschema import validate


def get_json_columns(json_obj, cols={}):
    """
    Extract column mappings from the JSON config file.
    """
    for key, value in json_obj.items():
        if isinstance(value, dict):
            get_json_columns(value, cols)
        elif isinstance(value, list):
            cols[key] = value
        else:
            cols[key] = value
    return cols


def construct_nested_json(row, mapping):
    """
    Construct the nested JSON structure needed to validate a row of data against the JSON schema.
    """
    return {
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


def validate_data(data: pd.DataFrame) -> bool:
    """
    Validate the data in a dataframe against the JSON schema, using the JSON config file
    """
    # load the JSON config file
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # load the JSON schema file
    with open("config/schema.json", "r") as f:
        schema = json.load(f)

    # get the columns from the JSON config file
    mapping = get_json_columns(config["columns"])
    validation_rules = config["validation_rules"]
    model_type = config["model_config"]["model_type"]

    # Extract all column names from the mapping
    required_columns = set()

    def extract_columns(mapping):
        for key, value in mapping.items():
            if isinstance(value, dict):
                extract_columns(value)
            elif isinstance(value, list):
                required_columns.update(value)
            elif value is not None:
                required_columns.add(value)

    extract_columns(mapping)

    # Check for required column presence in DataFrame
    if not required_columns.issubset(data.columns):
        missing_columns = required_columns - set(data.columns)
        print(f"Missing required columns in DataFrame: {missing_columns}")
        return False

    print(mapping)
    # Model type validation

    if model_type["regression"]:
        if not mapping.get("regression_prediction") or not mapping.get(
            "regression_label"
        ):
            print(
                "Regression model type is enabled, but necessary regression columns are not properly configured."
            )
            return False

    if model_type["binary_classification"]:
        if not mapping.get("classification_prediction") or not mapping.get(
            "classification_label"
        ):
            print(
                "Binary classification model type is enabled, but necessary classification columns are not properly configured."
            )
            return False
    # check for duplicates
    if data.duplicated().any():
        raise ValueError("Data contains duplicates")

    # check for missing values
    if data.isnull().values.any():
        raise ValueError("Data contains missing values")

    # Validate ranges for each feature
    for feature, rules in validation_rules.items():
        if feature in data.columns:
            if isinstance(rules[0], str):
                # Handle categorical data
                if not data[feature].dropna().isin(rules).all():
                    print(f"Value error for '{feature}': values not in {rules}")
                    return False
            elif isinstance(rules[0], (int, float)) and len(rules) == 2:
                # Handle numerical ranges
                if not data[feature].dropna().between(rules[0], rules[1]).all():
                    print(f"Value error for '{feature}': values out of range {rules}")
                    return False
            else:
                print(f"Unsupported range specification for '{feature}': {rules}")
                return False
        else:
            print(
                f"Feature '{feature}' specified in validation rules not found in DataFrame."
            )
            return False

    # validate the data against the JSON schema
    for _, row in data.iterrows():
        try:
            instance = construct_nested_json(row, mapping)
            validate(instance, schema)
        except jsonschema.exceptions.ValidationError as err:
            print(f"Validation error: {err}")
            return False
    print("Data is valid")
    return True


if __name__ == "__main__":
    data = pd.read_csv("data/data.csv")
    validate_data(data)
