from evidently.ui.workspace import Workspace, WorkspaceBase

WORKSPACE = "workspace"
PROJECT_NAME = "sample project"
PROJECT_DESCRIPTION = "This is a sample project for Evidently AI dashboard testing."


def create_project(workspace: WorkspaceBase):
    project = workspace.create_project(PROJECT_NAME)
    project.description = PROJECT_DESCRIPTION
    # no panels yet, add here:

    project.save()
    return project


def create_workspace(workspace: str):
    ws = Workspace.create(WORKSPACE)
    project = create_project(ws)


if __name__ == "__main__":
    create_workspace(WORKSPACE)
