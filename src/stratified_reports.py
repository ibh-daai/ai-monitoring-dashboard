"""
File to split both reference and current data into stratified reports by sex, hospital, and age.

Reports (9 total):
- main report
- male report
- female report
- first tertile age report
- second tertile age report
- third tertile age report
- hospital A report
- hospital B report
- hospital C report
"""

import pandas as pd
from src.config_manager import load_config
from src.metrics import generate_report


"""
plan:
- load data
- split data into the 9 dataframes (1 for each report)
- save each dataframe to its respective directory
- generate the 9 reports, save them each in their respective directories
"""


def split_data(data: pd.DataFrame, config: dict) -> dict:
    """
    Split the data into 9 dataframes for stratified reports
    """
    split_data = {}
    # save the main data
    split_data["main_report"] = data
    # Split the data into stratified reports
    for sex in config["validation_rules"][config["columns"]["sex"]]["values"]:
        if sex == "F" or sex == "f":
            sex_name = "female"
        elif sex == "M" or sex == "m":
            sex_name = "male" 
        else:
            sex_name = sex

        split_data[f"{sex_name}_report"] = data[data[config["columns"]["sex"]] == sex]

    # Split the age range into tertiles
    tertiles = data[config["columns"]["age"]].quantile([0.33, 0.66]).values
    split_data["age1"] = data[data[config["columns"]["age"]] <= tertiles[0]]
    split_data["age2"] = data[
        (data[config["columns"]["age"]] > tertiles[0])
        & (data[config["columns"]["age"]] <= tertiles[1])
    ]
    split_data["age3"] = data[data[config["columns"]["age"]] > tertiles[1]]

    # Split the data by hospital
    unique_hospitals = data[config["columns"]["hospital"]].unique()
    for hospital in unique_hospitals:
        split_data[hospital] = data[
            data[config["columns"]["hospital"]] == hospital
        ]

    return split_data


def generate_reports(
    data: pd.DataFrame, reference_data: pd.DataFrame, config: dict, model_type: dict
) -> None:
    """
    Generate the reports for each stratified dataset
    """
    data_stratifications = split_data(data, config)
    reference_stratifications = split_data(reference_data, config)
    for key, data_stratification in data_stratifications.items():
        reference_stratification = reference_stratifications[key]
        generate_report(
            data_stratification,
            reference_stratification,
            config,
            model_type,
            folder_path=key,
        )


def main():
    # load config and test split function
    config = load_config()
    data = pd.read_csv("data/data.csv")
    reference_data = pd.read_csv("data/reference_data.csv")
    generate_reports(data, reference_data, config, config["model_config"]["model_type"])

if __name__ == "__main__":
    main()