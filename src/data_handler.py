"""
File to handle data ingestion and validation
"""

import pandas as pd
from validate import validate_data


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file
    """
    return pd.read_csv(file_path)


def ingest_and_validate(file_path: str) -> pd.DataFrame:
    """
    Load and validate data from a CSV file
    """
    data = load_data(file_path)
    if validate_data(data):
        return data
    else:
        raise ValueError("Data validation failed")


def main():
    data = ingest_and_validate("data/data.csv")


if __name__ == "__main__":
    main()
