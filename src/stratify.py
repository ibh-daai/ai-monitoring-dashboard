"""
File to split both reference and current data into stratified reports and tests by sex, hospital, age, instrument_type, and patient_class.
"""

import logging
import pandas as pd
import warnings
from itertools import product
from sklearn.exceptions import UndefinedMetricWarning
from src.config_manager import load_config
from src.etl import etl_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSplitter:
    def __init__(self):
        self.filter_dict = None

    def stratify_age(self, data: pd.DataFrame, config: dict) -> dict:
        """
        Split the data into stratified data based on age.
        """
        filter_dict = {}
        # get the filter type from the config, default to default if not specified
        filter_type = config["age_filtering"].get("filter_type", "default")

        try:
            # split the data into three evenly sized terciles
            if filter_type == "statistical":
                # sort the ages
                sorted_ages = data[config["columns"]["age"]].sort_values()
                n = len(sorted_ages)
                tercile_size = n // 3

                # get the cutoffs for the terciles
                cutoff1 = sorted_ages.iloc[tercile_size - 1]
                cutoff2 = sorted_ages.iloc[2 * tercile_size - 1]

                # split the data into terciles
                filter_dict[f"[{int(sorted_ages.min())}-{int(cutoff1)}]"] = data[
                    data[config["columns"]["age"]] <= cutoff1
                ]
                filter_dict[f"[{int(cutoff1)}-{int(cutoff2)}]"] = data[
                    (data[config["columns"]["age"]] > cutoff1) & (data[config["columns"]["age"]] <= cutoff2)
                ]
                filter_dict[f"[{int(cutoff2)}-{int(sorted_ages.max())}]"] = data[
                    data[config["columns"]["age"]] > cutoff2
                ]

            # split the data into custom ranges
            elif filter_type == "custom":
                custom_ranges = config["age_filtering"]["custom_ranges"]

                # split the data into custom ranges specified in the config
                for custom_range in custom_ranges:
                    # log a warning if the custom range is less than the minimum age or greater than the maximum age
                    if (
                        custom_range["min"] < data[config["columns"]["age"]].min()
                        or custom_range["max"] > data[config["columns"]["age"]].max()
                    ):
                        logger.warning(f"Age {custom_range} is outside the data age range.")

                    key = f"[{custom_range['min']}-{custom_range['max']}]"
                    filter_dict[key] = data[
                        (data[config["columns"]["age"]] >= custom_range["min"])
                        & (data[config["columns"]["age"]] <= custom_range["max"])
                    ]
                # send a warning if the custom ranges do not cover all the data
                if sum([len(filter_dict[key]) for key in filter_dict.keys()]) != len(data):
                    logger.warning("Custom age ranges do not cover all data. Consider adding more ranges.")

            # split age into under 18, 18-65, and over 65
            else:
                filter_dict["[0-18]"] = data[data[config["columns"]["age"]] < 18]
                filter_dict["[18-65]"] = data[
                    (data[config["columns"]["age"]] >= 18) & (data[config["columns"]["age"]] <= 65)
                ]
                filter_dict["[65+]"] = data[data[config["columns"]["age"]] > 65]

        except Exception as e:
            filter_dict["[0-18]"] = data[data[config["columns"]["age"]] < 18]
            filter_dict["[18-65]"] = data[
                (data[config["columns"]["age"]] >= 18) & (data[config["columns"]["age"]] >= 18)
            ]
            filter_dict["[65+]"] = data[data[config["columns"]["age"]] > 65]
        return filter_dict

    def stratify_sex(self, data: pd.DataFrame, config: dict) -> dict:
        """
        Split the data into stratified data based on sex (M/F).
        """
        filter_dict = {}

        sex_values = config["categorical_validation_rules"][config["columns"]["sex"]]
        for sex in sex_values:
            if sex.lower() == "f":
                sex_name = "female"
            elif sex.lower() == "m":
                sex_name = "male"
            else:
                sex_name = sex

            filter_dict[sex_name] = data[data[config["columns"]["sex"]] == sex]

        return filter_dict

    def stratify_list(self, data: pd.DataFrame, config: dict, column: str) -> dict:
        """
        Split the data into stratified data based on a list of values in a column.
        """
        filter_dict = {}

        for value in data[config["columns"][column]].unique():
            filter_dict[value] = data[data[config["columns"]["column"]] == value]

        return filter_dict

    def strata_products(self, data: pd.DataFrame, filter_dict: dict, operation: str = "report") -> dict:
        """
        Generate all unique combinations of two strata for the data.
        """
        filter_product_dict = {}
        # Generate combinations of two strata
        keys = list(filter_dict.keys())

        # Generate all combinations of two strata, use set to avoid duplicates. e.g. age1_sex1 = sex1_age1
        combinations = set()
        for key1, key2 in product(keys, repeat=2):
            # if the keys are different, combine the dataframes
            if key1 != key2:
                # Sort the keys to avoid duplicates (i.e. age1_sex1 = sex1_age1)
                sorted_keys = sorted([key1, key2])

                # handle case where combining with main data (original filter is from main, so unnecessary)
                if "main" in key1 or "main" in key2:
                    combined_key = f"{key1}_{operation}" if "main" in key2 else f"{key2}_{operation}"
                else:  # combine the keys and operation, e.g. age1_sex1_report
                    combined_key = f"{'_'.join(sorted_keys)}_{operation}"

                # add the combined key to the set
                if combined_key not in combinations:
                    combinations.add(combined_key)

                # merge the two dataframes
                combined_df = filter_dict[sorted_keys[0]].merge(filter_dict[sorted_keys[1]], how="inner")
                # if the combined dataframe is not empty, add it to the dictionary
                if not combined_df.empty:  # handles case where filters from the same category are combined
                    filter_product_dict[combined_key] = combined_df

                # add main data to new dict
                filter_product_dict[f"main_{operation}"] = data

        return filter_product_dict

    def split_data(self, data: pd.DataFrame, config: dict, operation: str = "report") -> dict:
        """
        Split the data into stratified dataframes for reports and tests by sex, hospital, age, and instrument_type.

        Return all possible combinations of two strata, along with the main data and individual strata.
        """
        if self.filter_dict is not None:
            return self.strata_products(data, self.filter_dict, operation)

        filter_dict = {}

        try:
            # save the main data
            filter_dict[f"main_{operation}"] = data

            # Split the data by sex
            filter_dict.update(self.stratify_sex(data, config))

            # Split the data by age
            filter_dict.update(self.stratify_age(data, config))

            # Split the data by hospital
            filter_dict.update(self.stratify_list(data, config, "hospital"))

            # Split the data by instrument type
            if config["columns"]["instrument_type"]:
                filter_dict.update(self.stratify_list(data, config, "instrument_type"))

            # Split the data by patient class
            if config["columns"]["patient_class"]:
                filter_dict.update(self.stratify_list(data, config, "patient_class"))

            # Cache the filter_dict for subsequent runs
            self.filter_dict = filter_dict

            # Generate combinations of two strata
            filter_product_dict = self.strata_products(data, filter_dict, operation)

        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise

        return filter_product_dict


if __name__ == "__main__":
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)
    warnings.simplefilter(action="ignore", category=RuntimeWarning)
    warnings.simplefilter(action="ignore", category=UserWarning)

    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        exit(1)

    try:
        data, reference_data = etl_pipeline(config)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        exit(1)

    splitter = DataSplitter()
    filter_product_dict = splitter.split_data(data, config)
