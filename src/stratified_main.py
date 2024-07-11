"""
File to split both reference and current data into stratified reports and tests by sex, hospital, age, and instrument_type.
"""

import logging
import pandas as pd
import warnings
from itertools import product
from sklearn.exceptions import UndefinedMetricWarning
from src.config_manager import load_config
from src.metrics import generate_report
from src.tests import generate_tests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def split_data(data: pd.DataFrame, config: dict, operation: str = "report") -> dict:
    """
    Split the data into stratified dataframes for reports and tests by sex, hospital, age, and instrument_type.

    Return all possible combinations of two strata, along with the main data and individual strata.
    """
    filter_dict = {}
    filter_product_dict = {}

    try:
        # save the main data
        filter_dict[f"main_{operation}"] = data

        # Split the data into stratified reports by sex
        sex_values = config["validation_rules"][config["columns"]["sex"]]["values"]
        for sex in sex_values:
            if sex.lower() == "f":
                sex_name = "female"
            elif sex.lower() == "m":
                sex_name = "male"
            else:
                sex_name = sex

            filter_dict[sex_name] = data[data[config["columns"]["sex"]] == sex]

        # Split the age range into tertiles
        tertiles = data[config["columns"]["age"]].quantile([0.33, 0.66]).values
        filter_dict["age1"] = data[data[config["columns"]["age"]] <= tertiles[0]]
        filter_dict["age2"] = data[
            (data[config["columns"]["age"]] > tertiles[0])
            & (data[config["columns"]["age"]] <= tertiles[1])
        ]
        filter_dict["age3"] = data[data[config["columns"]["age"]] > tertiles[1]]

        # Split the data by hospital
        for hospital in data[config["columns"]["hospital"]].unique():
            filter_dict[hospital] = data[
                data[config["columns"]["hospital"]] == hospital
            ]

        # Split the data by instrument_type
        for instrument in data[config["columns"]["instrument_type"]].unique():
            filter_dict[instrument] = data[
                data[config["columns"]["instrument_type"]] == instrument
            ]

        # Generate combinations of two strata
        keys = list(filter_dict.keys())
        logger.debug(f"Keys: {keys}")

        # Generate all combinations of two strata, use set to avoid duplicates. e.g. age1_sex1 = sex1_age1
        combinations = set()
        for key1, key2 in product(keys, repeat=2):
            # set all the keys to lower case, and replace all spaces with underscores
            if key1 != key2:
                # Sort the keys to avoid duplicates
                sorted_keys = sorted([key1, key2])

                # handle case where combining with main data
                if "main" in key1 or "main" in key2:
                    combined_key = (
                        f"{key1}_{operation}"
                        if "main" in key2
                        else f"{key2}_{operation}"
                    )
                else:
                    combined_key = f"{'_'.join(sorted_keys)}_{operation}"
                if combined_key not in combinations:
                    combinations.add(combined_key)
                combined_df = filter_dict[sorted_keys[0]].merge(
                    filter_dict[sorted_keys[1]], how="inner"
                )
                # if the combined dataframe is not empty, add it to the dictionary
                if not combined_df.empty:
                    filter_product_dict[combined_key] = combined_df

                # add main data to the combined data
                filter_product_dict[f"main_{operation}"] = data

    except Exception as e:
        logger.error(f"Error splitting data: {e}")
        raise

    return filter_product_dict


def generate_stratified_reports(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    timestamp: str,
) -> None:
    """
    Generate the reports for each stratified dataset
    """
    try:
        data_stratifications = split_data(data, config, "report")

        for key, data_stratification in data_stratifications.items():
            logger.info(f"Generating report for {key}")
            generate_report(
                data_stratification,
                reference_data,
                config,
                model_type,
                folder_path=f"/reports/{key}",
                timestamp=timestamp,
            )
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        raise


def generate_stratified_tests(
    data: pd.DataFrame,
    reference_data: pd.DataFrame,
    config: dict,
    model_type: dict,
    timestamp: str,
) -> None:
    """
    Generate the test suite for each stratified dataset
    """
    try:
        data_stratifications = split_data(data, config, "tests")

        for key, data_stratification in data_stratifications.items():
            logger.info(f"Generating tests for {key}")
            generate_tests(
                data_stratification,
                reference_data,
                config,
                model_type,
                folder_path=f"/tests/{key}",
                timestamp=timestamp,
            )
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise


def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)
    warnings.simplefilter(action="ignore", category=RuntimeWarning)
    warnings.simplefilter(action="ignore", category=UserWarning)

    try:
        # load config and test split function
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    try:
        data = pd.read_csv("data/data.csv")
        reference_data = pd.read_csv("data/reference_data.csv")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    try:
        generate_stratified_reports(
            data,
            reference_data,
            config,
            config["model_config"]["model_type"],
            timestamp,
        )
    except Exception as e:
        logger.error(f"Failed to generate stratified reports: {e}")

    try:
        generate_stratified_tests(
            data,
            reference_data,
            config,
            config["model_config"]["model_type"],
            timestamp,
        )
    except Exception as e:
        logger.error(f"Failed to generate stratified tests: {e}")


if __name__ == "__main__":
    main()
