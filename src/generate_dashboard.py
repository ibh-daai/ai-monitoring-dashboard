"""
Generate the Evidently AI monitoring dashboard.
"""

from scripts.workspace_manager import WorkspaceManager
from scripts.create_project import create_project
from src.config_manager import load_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_dashboard():
    """
    Generate the Evidently AI monitoring dashboard.
    """
    try:
        # create or load workspace
        workspace_instance = WorkspaceManager.get_instance()
        logger.info("Workspace created successfully.")

        # load config
        config = load_config()
        logger.info("Config loaded successfully.")

        # create project
        create_project(workspace_instance.workspace, config)
        logger.info("Project created successfully.")

    except Exception as e:
        logger.error(f"Error occurred while building project. Please try again.: {e}")
        raise e


if __name__ == "__main__":
    generate_dashboard()
