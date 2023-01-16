import sys

from prefect_notebook_runner.core import schedule_notebook

if __name__ == "__main__":
    schedule_notebook(sys.argv[1])
