import os
import pickle
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from prefect import flow, get_run_logger, task
from prefect.context import get_run_context
from prefect.deployments import Deployment
from prefect.orion import schemas
from prefect.settings import PREFECT_API_URL, temporary_settings
from pydantic import AnyHttpUrl, NonNegativeInt, validate_arguments

from prefect_notebook_runner import module_locator


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
    my_path = module_locator.module_path()

    params = {
        "token": "deadbeef",
        "prefect_api_url": prefect_api_url,
        "name": name,
        "notebook_url": notebook_url,
        "queue": queue,
        "schedule": schedule,
        "parameters": parameters,
    }

    with tempfile.NamedTemporaryFile(prefix="prefect-notebook-runner", delete=False) as fb:
        pickle.dump(params, fb, pickle.HIGHEST_PROTOCOL)

        params_file = fb.name

    print(f"Will run {sys.executable} with {my_path} on {params_file}")
    output = subprocess.check_output([sys.executable, my_path, params_file])
    print(f"Output is {output}")

    return output


def schedule_notebook(params_path: str) -> Deployment:
    """This method runs inside the script produced by schedule method."""
    with open(params_path, "rb") as f:
        params = pickle.load(f)

    if "token" not in params:
        raise ValueError("Wrong params passed to this function")

    with temporary_settings(updates={PREFECT_API_URL: params["prefect_api_url"]}):
        rflow = run_report.with_options(name=params["name"])
        d = Deployment.build_from_flow(
            flow=rflow,
            parameters={
                "name": params["name"],
                "notebook_url": params["notebook_url"],
                "parameters": params["parameters"],  # what we pass to the notebook
            },
            name=params["name"],
            schedule=params["schedule"],
            version=1,
            work_queue_name=params["queue"],
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


__all__ = ["schedule", "run_report"]
