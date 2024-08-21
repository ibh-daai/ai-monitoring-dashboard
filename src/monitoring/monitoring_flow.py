"""
Prefect flow for monitoring dashboard pipeline with parallel snapshot generation.
"""

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
import logging
from datetime import datetime
import warnings
from sklearn.exceptions import UndefinedMetricWarning

from src.utils.config_manager import load_config
from scripts.data_details import load_details
from src.data_preprocessing.etl import etl_pipeline
from src.monitoring.stratify import DataSplitter
from src.monitoring.metrics import generate_report
from src.monitoring.tests import generate_tests
from src.dashboard.workspace_manager import WorkspaceManager
from src.dashboard.create_project import create_or_update

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@task
def load_configuration():
    return load_config()


@task
def load_data_details():
    return load_details()


@task
def run_etl(config):
    return etl_pipeline(config)


@task
def split_data(data, config, details, operation):
    splitter = DataSplitter()
    return splitter.split_data(data, config, details, operation)


@task
def generate_report_for_stratification(
    data_stratification, reference_data, config, model_type, key, timestamp, details
):
    logger.info(f"Generating reports for {key}")
    generate_report(
        data_stratification,
        reference_data,
        config,
        model_type,
        folder_path=f"/reports/{key}",
        timestamp=timestamp,
        details=details,
    )


@task
def generate_test_for_stratification(data_stratification, reference_data, config, model_type, key, timestamp, details):
    logger.info(f"Generating tests for {key}")
    generate_tests(
        data_stratification,
        reference_data,
        config,
        model_type,
        folder_path=f"/tests/{key}",
        timestamp=timestamp,
        details=details,
    )


@task
def create_dashboard(config):
    workspace_instance = WorkspaceManager.get_instance()
    create_or_update(workspace_instance.workspace, config)


@flow(name="Monitoring Flow", task_runner=ConcurrentTaskRunner())
def monitoring_flow():
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    config = load_configuration()
    details = load_data_details()
    data, reference_data = run_etl(config)

    if data is None:
        logger.info("No new data available. Monitoring flow completed successfully with no updates.")
        return

    # Split data for reports and tests concurrently
    report_stratifications_future = split_data.submit(data, config, details, "report")
    test_stratifications_future = split_data.submit(data, config, details, "test")

    # Generate reports and tests concurrently
    report_tasks = []
    test_tasks = []

    for stratifications_future, generation_task, task_list in [
        (report_stratifications_future, generate_report_for_stratification, report_tasks),
        (test_stratifications_future, generate_test_for_stratification, test_tasks),
    ]:
        stratifications = stratifications_future.result()
        for key, data_stratification in stratifications.items():
            task = generation_task.submit(
                data_stratification,
                reference_data,
                config,
                config["model_config"]["model_type"],
                key,
                timestamp,
                details,
            )
            task_list.append(task)

    # Wait for all tasks to complete
    for task in report_tasks + test_tasks:
        task.result()

    create_dashboard(config)
    logger.info("Monitoring flow completed successfully.")


if __name__ == "__main__":
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UndefinedMetricWarning)
    warnings.simplefilter(action="ignore", category=RuntimeWarning)
    warnings.simplefilter(action="ignore", category=UserWarning)

    monitoring_flow()
