import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class WorkflowConfiguration:
    is_dry_run: bool


def get_workflow_configuration():
    """
    Returns the configuration for the execution of the workflow, i.e. any execution-related parameters that are not
    specific to a particular client or service, but rather to the workflow as a whole.
    """
    load_dotenv()

    print("Initializing workflow configuration...")

    configuration = WorkflowConfiguration(
        is_dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
    )

    print(f"Workflow configuration initialized successfully")

    return configuration
