"""
Creates the Evidently AI workspace.
"""

from evidently.ui.workspace import Workspace, WorkspaceBase
import os

WORKSPACE_NAME = "workspace"


class WorkspaceManager:
    """
    Manages the workspace.
    """

    _instance = None

    @staticmethod
    def get_instance():
        """
        Get the workspace manager instance.
        """
        if WorkspaceManager._instance is None:
            WorkspaceManager()
        return WorkspaceManager._instance

    def __init__(self):
        if WorkspaceManager._instance is not None:
            raise Exception("This class is a singleton")
        else:
            WorkspaceManager._instance = self
            self.workspace = self.create_workspace(WORKSPACE_NAME)

    def create_workspace(self, workspace_name: str) -> WorkspaceBase:
        """
        Create the workspace.
        """
        return Workspace.create(workspace_name)


# Ensure the workspace directory exists
def ensure_directory(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


ensure_directory(WORKSPACE_NAME)
