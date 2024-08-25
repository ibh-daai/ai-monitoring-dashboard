from evidently.ui.workspace import Workspace, WorkspaceBase
import os

WORKSPACE_NAME = "/app/workspace"


class WorkspaceManager:
    _instance = None

    @staticmethod
    def get_instance():
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
        return Workspace.create(workspace_name)

    def reload_workspace(self):
        self.workspace = self.load_or_create_workspace(WORKSPACE_NAME)


# Ensure the workspace directory exists
def ensure_directory(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


ensure_directory(WORKSPACE_NAME)
