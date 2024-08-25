"""
This script fetches data from the MongoDB database and stores it in a pandas DataFrame.
"""

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_db_connection(mongo_uri: str) -> MongoClient:
    """
    Get a connection to the MongoDB database.
    """
    print(f"Connecting to MongoDB: {mongo_uri}")
    client = MongoClient(mongo_uri)
    db_name = "data_ingestion"
    if db_name not in client.list_database_names():
        db = client[db_name]
        db.create_collection("dummy")
        db.drop_collection("dummy")
    return client[db_name]


def fetch_data(db: MongoClient, collection: str) -> pd.DataFrame:
    """
    Fetch data from the MongoDB database.
    """
    collection = db[collection]
    data = list(collection.find())
    return pd.DataFrame(data)


def get_timestamp_col(config: dict) -> str:
    """
    Get the timestamp column from the configuration.
    """
    timestamp_col = config["columns"].get("timestamp")
    if not timestamp_col:
        timestamp_col = "timestamp"
    return timestamp_col


def process_duplicates(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Process duplicates in the DataFrame based on the timestamp column.
    """

    try:
        timestamp_col = get_timestamp_col(config)
        if timestamp_col not in df.columns:
            timestamp_col = "timestamp"
            if timestamp_col not in df.columns:
                logger.error(f"Timestamp column not found in the DataFrame.")
                df.drop_duplicates(inplace=True)
                return df
        df.sort_values(by=timestamp_col, ascending=False, inplace=True)
        df.drop_duplicates(subset=config["columns"]["study_id"], keep="first", inplace=True)
    except Exception as e:
        logger.error(f"Error processing duplicates: {e}")
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
        records_to_delete = list(labels.find({config["columns"]["study_id"]: {"$in": matched_ids}}))

        if matched_records:
            destination.insert_many(matched_records)
            results.delete_many({config["columns"]["study_id"]: {"$in": matched_ids}})
            labels.delete_many({config["columns"]["study_id"]: {"$in": matched_ids}})
    except Exception as e:
        logger.error(f"Error moving matched data: {e}")


def fetch_and_merge(config: dict) -> pd.DataFrame:
    """
    Fetch data from the MongoDB database and merge it into a single DataFrame.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")

    db = get_db_connection(mongo_uri)

    model_id = config["model_config"]["model_id"]

    collections_to_create = [f"{model_id}_results", f"{model_id}_labels", f"{model_id}_matched"]
    for collection_name in collections_to_create:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

    # Fetch results and labels data
    try:
        results = fetch_data(db, f"{model_id}_results")
        labels = fetch_data(db, f"{model_id}_labels")
    except OperationFailure as e:
        logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()

    # check if the results or labels data is empty
    if results.empty or labels.empty:
        logger.info("Results or Labels data is empty.")
        # return an empty DataFrame
        return pd.DataFrame()

    # Process duplicates
    results = process_duplicates(results, config)
    labels = process_duplicates(labels, config)

    # Drop the _id columns from MongoDB
    results.drop(columns=["_id"], inplace=True)
    labels.drop(columns=["_id"], inplace=True)

    # Drop the timestamp column from the labels
    timestamp_col = get_timestamp_col(config)
    if timestamp_col not in labels.columns:
        timestamp_col = "timestamp"
        if timestamp_col not in labels.columns:
            logger.error(f"Timestamp column not found in the DataFrame.")
        else:
            labels.drop(columns=[timestamp_col], inplace=True)
    else:
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
    return merged_data
