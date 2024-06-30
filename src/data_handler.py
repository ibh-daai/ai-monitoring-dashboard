"""
File to handle data ingestion and validation
"""

import pandas as pd


def load_data(
    file_path: str, reference_path: str = None
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """
    Load data from a CSV file
    """
    data = pd.read_csv(file_path)
    reference_data = None

    if reference_path:
        reference_data = pd.read_csv(reference_path)

    return data, reference_data
