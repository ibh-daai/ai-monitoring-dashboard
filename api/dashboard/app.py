"""
Backend file for the monitoring dashboard. This file contains the API endpoints for the dashboard.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from src.dashboard.workspace_manager import WorkspaceManager
from scripts.data_details import load_details
from src.utils.config_manager import load_config
from src.dashboard.create_project import update_panels
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://dashboard_frontend:3000",
    os.environ.get("DASHBOARD_FRONTEND_URL", ""),
]

allowed_origins = list(filter(None, allowed_origins))

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": allowed_origins}},
)

config = load_config()
details = load_details()
workspace_instance = WorkspaceManager.get_instance()
ws = workspace_instance.workspace

dashboard_url = os.environ.get("DASHBOARD_URL", "http://localhost:3000")
evidently_url = os.environ.get("EVIDENTLY_URL", "http://localhost:8000")


def get_filters(config: dict) -> dict:
    """
    Get the filter options for the dashboard.
    """
    cols = config["columns"]
    strata_mapping = {
        "hospital": details["hospital_unique_values"],
    }
    if cols["instrument_type"]:
        strata_mapping["instrument_type"] = details["instrument_type_unique_values"]
    if cols["patient_class"]:
        strata_mapping["patient_class"] = details["patient_class_unique_values"]

    sex_values = details["sex_unique_values"]
    sex_list = []
    for sex in sex_values:
        if sex.lower() == "f":
            sex_list.append("female")
        elif sex.lower() == "m":
            sex_list.append("male")
        else:
            sex_list.append(sex)
    strata_mapping["sex"] = sex_list

    if config["age_filtering"]["filter_type"] == "custom":
        custom_ranges = config["age_filtering"]["custom_ranges"]
        range_list = [f"[{range_['min']}-{range_['max']}]" for range_ in custom_ranges]
        strata_mapping["age"] = range_list
    else:
        strata_mapping["age"] = [
            "[0-18]",
            "[18-65]",
            "[65+]",
        ]
    return strata_mapping


@app.route("/get_filter_options", methods=["GET"])
def get_filter_options():
    """
    Get the filter options for the dashboard.
    """
    return jsonify(get_filters(config))


@app.route("/apply_filters", methods=["POST"])
def apply_filters():
    """
    Apply the selected filters to the dashboard.
    """
    filters = request.json
    tags = [v for k, v in filters.items() if v]

    # if exactly one tag, add the tag 'single' to the list of tags
    if len(tags) == 1:
        tags.append("single")

    logger.debug("tags: %s", tags)

    workspace_instance = WorkspaceManager.get_instance()
    workspace_instance.reload_workspace()
    ws = workspace_instance.workspace

    if tags:
        logger.info("Applying filters: %s", tags)
        update_panels(ws, config, tags)
    else:
        logger.info("No filters applied")
        update_panels(ws, config)

    filtered_url = f"{dashboard_url}/dashboard"
    return jsonify({"status": "updated", "filtered_url": filtered_url})


@app.route("/get_dashboard_url", methods=["GET"])
def get_dashboard_url():
    """
    Get the URL for the Evidently dashboard.
    """
    try:
        workspace_instance = WorkspaceManager.get_instance()
        workspace_instance.reload_workspace()
        ws = workspace_instance.workspace
        project = ws.search_project(config["info"]["project_name"])[0]
        if not evidently_url:
            return jsonify({"status": "error", "message": "Evidently URL not configured"}), 500
        dashboard_url = f"{evidently_url}/projects/{project.id}"
        return jsonify({"dashboard_url": dashboard_url})
    except IndexError:
        return jsonify({"status": "error", "message": "Project not found, please create the project."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_API_PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
