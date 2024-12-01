from main import monitoring_flow
from pathlib import Path


if __name__ == "__main__":

    source = str(Path(__file__).parent.parent.parent)

    monitoring_flow.from_source(
        source=source,
        entrypoint="/app/flow/main.py:monitoring_flow",
    ).deploy(
        name="monitoring-flow",
        work_pool_name="monitoring-pool",
        push=False,
    )
