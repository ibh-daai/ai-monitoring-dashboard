"""
File to split both reference and current data into stratified reports and tests by sex, hospital, and age.
"""

import pandas as pd
import warnings
from sklearn.exceptions import UndefinedMetricWarning
from src.config_manager import load_config
from src.metrics import generate_report
from src.tests import generate_tests


def split_data(data: pd.DataFrame, config: dict, operation: str = "report") -> dict:
    """
    Split the data into stratified dataframes for reports and tests by sex, hospital, and age.
    """
    split_data = {}
    # save the main data
    split_data[f"main_{operation}"] = data
    # Split the data into stratified reports
    for sex in config["validation_rules"][config["columns"]["sex"]]["values"]:
        if sex.lower() == "f":
            sex_name = "female"
        elif sex.lower() == "m":
            sex_name = "male"
        else:
            sex_name = sex

        split_data[f"{sex_name}_{operation}"] = data[
            data[config["columns"]["sex"]] == sex
        ]

    # Split the age range into tertiles
    tertiles = data[config["columns"]["age"]].quantile([0.33, 0.66]).values
    split_data["age1"] = data[data[config["columns"]["age"]] <= tertiles[0]]
    split_data["age2"] = data[
        (data[config["columns"]["age"]] > tertiles[0])
        & (data[config["columns"]["age"]] <= tertiles[1])
    ]
    split_data["age3"] = data[data[config["columns"]["age"]] > tertiles[1]]

    # Split the data by hospital
    for hospital in data[config["columns"]["hospital"]].unique():
        split_data[hospital] = data[data[config["columns"]["hospital"]] == hospital]

    return split_data


def generate_stratified_reports(
    data: pd.DataFrame, reference_data: pd.DataFrame, config: dict, model_type: dict
) -> None:
    """
    Generate the reports for each stratified dataset
    """
    data_stratifications = split_data(data, config, "report")
    reference_stratifications = split_data(reference_data, config, "report")

    for key, data_stratification in data_stratifications.items():
        reference_stratification = reference_stratifications[key]
        generate_report(
            data_stratification,
            reference_stratification,
            config,
            model_type,
            folder_path=key,
        )


def generate_stratified_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
) -> None:
    """
    Generate the test suite for each stratified dataset
    """
    data_stratifications = split_data(data, config, "tests")
    reference_stratifications = split_data(reference_data, config, "tests")

    for key, data_stratification in data_stratifications.items():
        reference_stratification = reference_stratifications[key]
        generate_tests(
            data_stratification,
            reference_stratification,
            config,
            model_type,
            folder_path=key,
        )


def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)
    # load config and test split function
    config = load_config()
    data = pd.read_csv("data/data.csv")
    reference_data = pd.read_csv("data/reference_data.csv")

    generate_stratified_reports(
        data, reference_data, config, config["model_config"]["model_type"]
    )
    generate_stratified_tests(
        data, reference_data, config, config["model_config"]["model_type"]
    )


if __name__ == "__main__":
    main()
