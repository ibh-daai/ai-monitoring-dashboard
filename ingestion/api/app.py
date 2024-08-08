"""
File to create API endpoints to ingest the results (predictions, data) and labels from the user.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from datetime import datetime, timezone
import pandas as pd
import logging

from src.config_manager import load_config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object("api.config.Config")
# app.secret_key = app.config["SECRET_KEY"]
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "http://localhost:3000"}},
)

# Load the database
mongo_uri = app.config["MONGO_URI"]
client = MongoClient(mongo_uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    logger.info("Pinged deployment. Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Load the configuration
config = load_config()
model_id = config["model_config"]["model_id"]

# Load the database
db = client["data_ingestion"]

ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    """
    Check if the file extension is allowed.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("upload.html")


def get_column_mapping():
    """
    Get the column mapping from the configuration.
    """
    return config["columns"]


def get_model_config():
    """
    Get the model configuration from the configuration.
    """
    return config["model_config"]


def validate_csv_columns(df, required_columns):
    """
    Validate the CSV columns against the required columns.
    """
    df_columns = df.columns.tolist()
    missing_columns = [col for col in required_columns if col not in df_columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")


def get_collection(model_id, collection_suffix):
    """
    Get the collection for the model.
    """
    collection_name = f"{model_id}_{collection_suffix}"
    return db[collection_name]


@app.route("/ingest_results", methods=["POST"])
def ingest_results():
    """
    Ingest the results from the user.
    """
    try:
        model_id = request.form.get("model_id")
        if not model_id:
            return jsonify({"message": "Model ID not in session."}), 400

        # Load the uploaded CSV file
        file = request.files["csvFile"]
        if not file or not allowed_file(file.filename):
            return jsonify({"message": "Invalid file."}), 400

        df = pd.read_csv(file)

        columns = get_column_mapping()
        model_config = get_model_config()

        # Prepare the list of required columns
        required_columns = [
            columns["study_id"],
            columns["sex"],
            columns["hospital"],
            columns["age"],
            columns["instrument_type"],
            columns["patient_class"],
        ]

        if model_config["model_type"]["regression"]:
            required_columns.append(columns["predictions"]["regression_prediction"])

        if model_config["model_type"]["binary_classification"]:
            required_columns.append(columns["predictions"]["classification_prediction"])

        # Validate that the CSV contains all required columns
        validate_csv_columns(df, required_columns)

        # Extract features (all keys that are not part of the defined columns)
        features = [col for col in df.columns if col not in columns.values()]

        # Convert dataframe to list of dictionaries
        data = df.to_dict("records")

        # Insert data into MongoDB
        results_collection = get_collection(model_id, "results")
        for row in data:
            new_result = {
                columns["study_id"]: row[columns["study_id"]],
                columns["sex"]: row.get(columns["sex"]),
                columns["hospital"]: row.get(columns["hospital"]),
                columns["age"]: row.get(columns["age"]),
                columns["instrument_type"]: row.get(columns["instrument_type"]),
                columns["patient_class"]: row.get(columns["patient_class"]),
            }
            for feature in features:
                new_result[feature] = row.get(feature)

            if model_config["model_type"]["regression"]:
                new_result[columns["predictions"]["regression_prediction"]] = row[
                    columns["predictions"]["regression_prediction"]
                ]

            if model_config["model_type"]["binary_classification"]:
                new_result[columns["predictions"]["classification_prediction"]] = row[
                    columns["predictions"]["classification_prediction"]
                ]

            if columns.get("timestamp") and columns["timestamp"] in row:
                new_result[columns["timestamp"]] = row[columns["timestamp"]]
            else:
                new_result["timestamp"] = datetime.now(timezone.utc)

            results_collection.insert_one(new_result)

        logger.info("Results ingested successfully.")
        return jsonify({"message": "Results ingested successfully."}), 200
    except Exception as e:
        logger.error(f"Error occurred while ingesting results: {e}")
        return jsonify({"message": f"Error occurred while ingesting results: {e}"}), 500


@app.route("/ingest_labels", methods=["POST"])
def ingest_labels():
    """
    Ingest the labels from the user.
    """
    try:
        model_id = request.form.get("model_id")
        if not model_id:
            return jsonify({"message": "Model ID not in session."}), 400

        # Load the uploaded CSV file
        file = request.files["csvFile"]
        if not file or not allowed_file(file.filename):
            return jsonify({"message": "Invalid file."}), 400

        df = pd.read_csv(file)
        columns = get_column_mapping()
        model_config = get_model_config()

        # Prepare the list of required columns based on user configuration
        required_columns = [
            columns["study_id"],
        ]

        if model_config["model_type"]["regression"]:
            required_columns.append(columns["labels"]["regression_label"])

        if model_config["model_type"]["binary_classification"]:
            required_columns.append(columns["labels"]["classification_label"])

        # Validate that the CSV contains all required columns
        validate_csv_columns(df, required_columns)

        # Convert dataframe to list of dictionaries
        data = df.to_dict("records")

        # Insert data into MongoDB
        labels_collection = get_collection(model_id, "labels")
        for row in data:
            new_label = {
                columns["study_id"]: row[columns["study_id"]],
            }
            if model_config["model_type"]["regression"]:
                new_label[columns["labels"]["regression_label"]] = row[columns["labels"]["regression_label"]]

            if model_config["model_type"]["binary_classification"]:
                new_label[columns["labels"]["classification_label"]] = row[columns["labels"]["classification_label"]]

            if columns.get("timestamp") and columns["timestamp"] in row:
                new_label[columns["timestamp"]] = row[columns["timestamp"]]
            else:
                new_label["timestamp"] = datetime.now(timezone.utc)

            labels_collection.insert_one(new_label)

        logger.info("Labels ingested successfully.")
        return jsonify({"message": "Labels ingested successfully."}), 200
    except Exception as e:
        logger.error(f"Error occurred while ingesting labels: {str(e)}")
        return (
            jsonify({"message": f"Error occurred while ingesting labels: {str(e)}"}),
            500,
        )


@app.route("/check_model_id", methods=["POST"])
def check_model_id():
    """
    Check if the model ID is already in use.
    """
    model_id = request.json.get("model_id")
    if not model_id:
        return jsonify({"message": "Model ID not provided."}), 400

    if db.list_collection_names(filter={"name": f"{model_id}_results"}):
        return (
            jsonify({"message": "Model ID already in use."}),
            409,
        )
    return jsonify({"message": "Model ID is available."}), 200


@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    Authenticate the user and set the model ID in the session.
    """
    model_id = request.json.get("model_id")
    action = request.json.get("action", "login")

    if not model_id:
        return jsonify({"message": "Model ID not provided."}), 400

    if action == "signup":
        if db.list_collection_names(filter={"name": f"{model_id}_results"}) or db.list_collection_names(
            filter={"name": f"{model_id}_labels"}
        ):
            return jsonify({"message": "Model ID is already in use."}), 409
        if model_id != config["model_config"]["model_id"]:
            return (
                jsonify({"message": "Model ID does not match the configuration file."}),
                400,
            )
        return jsonify({"message": "Sign up successful.", "model": model_id}), 200

    elif action == "login":
        if model_id == config["model_config"]["model_id"]:
            return (
                jsonify({"message": "Authentication successful.", "model": model_id}),
                200,
            )
        else:
            return (
                jsonify({"message": "Model ID not provided or different from configuration file."}),
                400,
            )

    return jsonify({"message": "Invalid action."}), 400


if __name__ == "__main__":
    app.run(port=5001, debug=True)
