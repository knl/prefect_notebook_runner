import os
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from prefect import flow, get_run_logger, task
from prefect.context import get_run_context
from prefect.deployments import Deployment
from prefect.orion import schemas
from prefect.settings import PREFECT_API_URL, temporary_settings
from pydantic import AnyHttpUrl, NonNegativeInt, validate_arguments


@validate_arguments
def schedule(
    prefect_api_url: AnyHttpUrl,
    name: str,
    notebook_url: AnyHttpUrl,
    queue: str,
    schedule: schemas.schedules.SCHEDULE_TYPES,
    parameters: Optional[Dict[str, Any]] = None,
) -> Deployment:
    """
    Schedule a run of a notebook

    Args:
        prefect_api_url: the URL for the Prefect Orion instance
        name: the name of the report
        notebook_url: a notebook object describing how to fetch a notebook
        queue: a Prefect queue on which to run the notebook.
        schedule: a schedule to use to run this notebook. One of the values as described in
                  https://docs.prefect.io/concepts/schedules/.
        parameters: an optional dictionary of values to pass to the notebook, just like on JupyterHub.
    """

    with temporary_settings(updates={PREFECT_API_URL: prefect_api_url}):
        rflow = run_report.with_options(name=name)
        d = Deployment.build_from_flow(
            flow=rflow,
            parameters={
                "name": name,
                "notebook_url": notebook_url,
                "parameters": parameters,  # what we pass to the notebook
            },
            name=name,
            schedule=schedule,
            version=1,
            work_queue_name=queue,
            skip_upload=True,
            apply=True,
            # must have path and entrypoint set to avoid https://github.com/PrefectHQ/prefect/issues/6777
            path=".",
            entrypoint="prefect_notebook_runner:run_report",
        )

        return d


@task
def execute_notebook(notebook_url: AnyHttpUrl, parameters: Optional[Dict[str, Any]]):
    logger = get_run_logger()

    logger.info(f"Will run {notebook_url} with the following parameters {parameters}")

    return "intentionally left blank"


@flow(
    description="Run a notebook and report via email.",
)
def run_report(
    name: str,
    notebook_url: AnyHttpUrl,
    parameters: Optional[Dict[str, Any]] = None,
    retries: int = 1,
):
    body = execute_notebook(
        notebook_url=notebook_url,
        parameters=parameters,
    )

    logger = get_run_logger()

    logger.info(f"Notebook returned: {body}")


__all__ = ["schedule"]
