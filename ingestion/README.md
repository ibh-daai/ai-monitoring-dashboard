# Ingestion Endpoints Instructions

## Ingestion Endpoints
There are two ingestion endpoints required to ingest data into the system. The first endpoint is used to ingest the predictions/results of the AI Model. The second endpoint is used to ingest the ground truth data, or the labels. You can either interact with the endpoints using the available web interface or by sending HTTP requests to the endpoints. If you use the web interface, you can upload a CSV file containing the data to be ingested. If you choose to send HTTP requests, you can use the provided API documentation to understand the required parameters and the expected response. Please note that the file limit for the web interface is 16MB per CSV file.

### Ingest Results Endpoint Data Schema
The data schema for the ingestion of the predictions/results is as follows (**Note: Column names must match mapping in `config.json`**):

- **Required Columns:** `study_id`, `sex`, `hospital`, `age`
- **Optional Columns (based on config):** `instrument_type`, `patient_class`, `timestamp`

If the model is regression: `regression_prediction` column is required.  
If the model is classification: `classification_prediction` column is required.

Any additional columns will be treated as features, and should be specified in the configuration file.

### Ingest Labels Endpoint Data Schema
The data schema for the ingestion of the labels is as follows (**Note: Column names must match mapping in `config.json`**):

- **Required Columns:** `study_id`, `label`
- **Optional Columns:** `timestamp`

If the model is regression: `regression_label` column is required.  
If the model is classification: `classification_label` column is required.

Any additional columns will be ignored. **Note: To match predictions and labels, the `study_id` must match**.

### Web Interface Ingestion Instructions

1. Open the web interface in your browser. The URL for the web interface will be provided (**TODO: Add URL**).
2. Enter your `model_id` when prompted. This must be the same `model_id` written in the configuration file, `config.json`.
3. If this is your first time ingesting data for this model, click the "Sign Up" button to register it in the database. If you have already registered the model, click the "Log In" button.
4. Once logged in, select either the "Ingest Predictions" or "Ingest Labels" endpoint from the "Select Endpoint" dropdown menu.
5. Click the "Select CSV File" button to upload the CSV file containing the data to be ingested.
6. Click the "Upload" button to ingest the data, and wait for the response.

**Note:** If you are using the web interface for the first time, you will need to register the model in the database. If you attempt to sign up with a `model_id` that already exists in the database, you will receive an error message. If you receive this error message, please select a new `model_id` by changing your `config.json` file and try again.

### HTTP Request Ingestion Instructions

**Note:** You are more than welcome to interact with the API using different code/libraries. This is just an example.

1. Ensure you have Python installed on your machine. Install the `requests` library by running the following command in your terminal:
    ```bash
    pip install requests
    ```
2. Use the following Python script to sign in to the ingestion endpoint. Replace the `model_id` and `endpoint` variables with the appropriate values. Replace the `file_path` variable with the path to the CSV file containing the data to be ingested.
    ```python
    import requests

    base_url = "http://<URL>:<PORT>"
    model_id = "your_model_id"
    sign_up = False

    action = "login"
    if sign_up:
        action = "signup"

    # Sign in
    response = requests.post(f"{base_url}/authenticate", json={"model_id": model_id, "action": action})

    if response.status_code != 200:
        print(f"Failed to sign in: {response.json()}")
        exit()

    print("Signed in successfully")
    ```
3. Use the following Python script to ingest the results. Replace the `model_id` variable with the appropriate value. Replace the `results_file_path` variable with the path to the CSV file containing the results.
    ```python
    import requests

    base_url = "http://<URL>:<PORT>"
    model_id = "your_model_id"
    results_file_path = 'path/to/your/results.csv'

    with open(results_file_path, 'rb') as results_file:
        results_response = requests.post(
            f"{base_url}/ingest_results",
            files={'csvFile': results_file},
            data={'model_id': model_id}
        )

    if results_response.status_code == 200:
        print("Results ingested successfully")
    else:
        print(f"Results ingestion failed: {results_response.json()['message']}")
    ```
4. Repeat the above steps for the labels endpoint, replacing the `ingest_results` endpoint with `ingest_labels` and the `results_file_path` with the path to the labels CSV file.

5. **Error Handling:** If you receive an error message, please check the following:
    - Ensure the `model_id` in the configuration file matches the `model_id` used in the Python script.
    - Ensure the CSV file contains the required columns and that the column names match the mapping in the configuration file.
    - Check the response message for more information on the error.
