from evidently.ui.workspace import Workspace, WorkspaceBase
import os

WORKSPACE_NAME = "/app/workspace"


class WorkspaceManager:
    _instance = None

    @staticmethod
    def get_instance():
        """
        Get the singleton instance of the WorkspaceManager.
        """
        if WorkspaceManager._instance is None:
            WorkspaceManager()
        return WorkspaceManager._instance

    def __init__(self):
        if WorkspaceManager._instance is not None:
            raise Exception("This class is a singleton")
        else:
            WorkspaceManager._instance = self
            self.workspace = self.load_or_create_workspace(WORKSPACE_NAME)

    def load_or_create_workspace(self, workspace_name: str) -> WorkspaceBase:
        """
        Load or create a workspace.
        """
        return Workspace.create(workspace_name)

    def reload_workspace(self):
        """
        Reload the workspace.
        """
        self.workspace = self.load_or_create_workspace(WORKSPACE_NAME)


def ensure_directory(directory: str) -> None:
    """
    Check if the directory exists and create it if it doesn't.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


ensure_directory(WORKSPACE_NAME)
