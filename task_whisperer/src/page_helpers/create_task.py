from typing import Any, Dict

from task_whisperer.src.issue_tracking.factory import ITS_factory


def create_task(
    its_kind: str,
    its_config: Dict[str, Any],
    task_summary: str,
    task_description: str,
    project: str,
    extra_fields: Dict[str, Any] = {},
):
    its_client = ITS_factory.get(its_kind)(
        url=its_config["url"],
        username=its_config["username"],
        password=its_config["password"],
        its_config=its_config,
    )
    response = its_client.create_issue(
        project, task_summary, task_description, extra_fields
    )
    return response
