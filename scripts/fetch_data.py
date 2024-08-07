"""
This script fetches data from the MongoDB database and stores it in a pandas DataFrame.
"""

import pandas as pd
from pymongo import MongoClient
from ingestion.api.config import Config
from src.config_manager import load_config


def get_db_connection(mongo_uri: str) -> MongoClient:
    """
    Get a connection to the MongoDB database.
    """
    client = MongoClient(mongo_uri)
    db = client["data_ingestion"]
    return db


def fetch_data(db: MongoClient, collection: str) -> pd.DataFrame:
    """
    Fetch data from the MongoDB database.
    """
    collection = db[collection]
    data = list(collection.find())
    return pd.DataFrame(data)


def process_duplicates(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Process duplicates in the DataFrame based on the timestamp column.
    """
    timestamp_col = config["columns"].get("timestamp")
    try:
        # timestamp is None in the config, set it to "timestamp"
        if not timestamp_col:
            timestamp_col = "timestamp"
        df.sort_values(by=timestamp_col, ascending=False, inplace=True)
        df.drop_duplicates(
            subset=config["columns"]["study_id"], keep="first", inplace=True
        )
    except Exception as e:
        print(f"Error processing duplicates: {e}")
    return df


def move_matched_data(
    db: MongoClient,
    merged_data: pd.DataFrame,
    matched_ids: list,
    results_collection: str,
    labels_collection: str,
    destination_collection: str,
    config: dict,
) -> None:
    """
    Move matched data from one collection to another.
    """
    try:
        results = db[results_collection]
        labels = db[labels_collection]
        destination = db[destination_collection]

        matched_records = merged_data.to_dict("records")
        records_to_delete = list(
            labels.find({config["columns"]["study_id"]: {"$in": matched_ids}})
        )

        if matched_records:
            destination.insert_many(matched_records)
            results.delete_many({config["columns"]["study_id"]: {"$in": matched_ids}})
            labels.delete_many({config["columns"]["study_id"]: {"$in": matched_ids}})
    except Exception as e:
        print(f"Error moving matched data: {e}")


def fetch_and_merge(config: dict) -> pd.DataFrame:
    """
    Fetch data from the MongoDB database and merge it into a single DataFrame.
    """
    db = get_db_connection(Config.MONGO_URI)

    model_id = config["model_config"]["model_id"]

    # Fetch results and labels data
    results = fetch_data(db, f"{model_id}_results")
    labels = fetch_data(db, f"{model_id}_labels")

    # check if the results or labels data is empty
    if results.empty or labels.empty:
        print("Results or labels data is empty.")
        # return an empty DataFrame
        return pd.DataFrame()

    # Process duplicates
    results = process_duplicates(results, config)
    labels = process_duplicates(labels, config)

    # Drop the _id columns from MongoDB
    results.drop(columns=["_id"], inplace=True)
    labels.drop(columns=["_id"], inplace=True)

    # Drop the timestamp column from the labels
    timestamp_col = config["columns"].get("timestamp")
    # timestamp is None in the config, set it to "timestamp"
    if not timestamp_col:
        timestamp_col = "timestamp"
    labels.drop(columns=[timestamp_col], inplace=True)

    # Merge results and labels data
    study_id_col = config["columns"]["study_id"]

    merged_data = pd.merge(
        results,
        labels,
        on=study_id_col,
    )

    # Move matched data to a new collection
    matched_ids = merged_data[study_id_col].tolist()
    move_matched_data(
        db,
        merged_data,
        matched_ids,
        f"{model_id}_results",
        f"{model_id}_labels",
        f"{model_id}_matched",
        config,
    )

    print(merged_data.head())
    return merged_data


if __name__ == "__main__":
    config = load_config()
    merged_data = fetch_and_merge(config)
    print(merged_data.head())
