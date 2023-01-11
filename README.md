A demo repository for an issue of creating deployments from a jupyterhub notebook.

## Motivation

My colleagues really like to use notebooks and sometimes they need to schedule
runs of various notebooks. We've been using crontab for that, but it's clunky
and doesn't support timezones. As I'm already susing Prefect, the idea was to
schedule notebooks to execute using Prefect. However, my colleagues do not want
to leave the comfort of their jupyterhub notebooks, so they would like to have
one notebook that contains all their scheduled runs. The idea is that they list
which notebooks need to be executed and when, in a notebook. Then, when they
execte that notebook, Prefect deployments and flows are created and ready to
use. Thus, this project was born, but I can't get it to have a deployment
created on prefect, for what I think is a bug.

## Setup

- Have a prefect deployment, note its `PREFECT_API_URL`
- Have a jupyterhub notebook
- In that notebook, have the following two cells that you'll execute:

```python
%pip install git+https://github.com/knl/prefect_notebook_runner.git
```

```python
import prefect_notebook_runner
from prefect.orion.schemas.schedules import CronSchedule

prefect_notebook_runner.schedule(
    prefect_api_url="YOUR SERVER'S PREFECT_API_URL",
    name="Amazing report",
    notebook_url='http://foo:8000/hub/user-redirect/lab/tree/examples/Untitled.ipynb',
    queue='SOME QUEUE',
    schedule=CronSchedule(cron="34 20 * * 1-5", timezone="Europe/Zurich"),
)
```

This should create a deployment on your prefect instance. However, it doesn't happen.

Instead, one gets `<coroutine object Deployment.build_from_flow at 0x7f2bb08b8710>`. Fine, let's try awaiting it:

```python
import prefect_notebook_runner
from prefect.orion.schemas.schedules import CronSchedule

await prefect_notebook_runner.schedule(
    prefect_api_url="YOUR SERVER'S PREFECT_API_URL",
    name="Amazing report",
    notebook_url='http://foo:8000/hub/user-redirect/lab/tree/examples/Untitled.ipynb',
    queue='SOME QUEUE',
    schedule=CronSchedule(cron="34 20 * * 1-5", timezone="Europe/Zurich"),
)
```

This, surprisingly, returns a Deployment (despite having `apply=True`)... Fine:

```python
import prefect_notebook_runner
from prefect.orion.schemas.schedules import CronSchedule

await (await prefect_notebook_runner.schedule(
    prefect_api_url="YOUR SERVER'S PREFECT_API_URL",
    name="Amazing report",
    notebook_url='http://foo:8000/hub/user-redirect/lab/tree/examples/Untitled.ipynb',
    queue='SOME QUEUE',
    schedule=CronSchedule(cron="34 20 * * 1-5", timezone="Europe/Zurich"),
)).apply()
```

Finally, this returns UUID. However, there is no deployment nor flow on prefect.
There is nothing in the logs, either...

Now, try the same from the command line, it should work.
