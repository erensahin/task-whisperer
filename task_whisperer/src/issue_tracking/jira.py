from typing import Any, Dict, List

from atlassian import Jira

from task_whisperer.src.issue_tracking.base import BaseITSClient


class JiraClient(BaseITSClient):
    """JiraClient"""

    def __init__(
        self, url: str, username: str, password: str, its_config: Dict, **kwargs
    ) -> None:
        self.jira = Jira(
            url=url,
            username=username,
            password=password,
            cloud=its_config.get("cloud", True),
        )
        self.its_config = its_config
        self.issue_fields = self.its_config["api_options"]["fields"]
        self.api_limit = self.its_config["api_options"]["limit"]

    def _get_issues_with_jql(self, project: str, start: int = 0) -> Dict:
        issues = self.jira.jql(
            f"project = {project}",
            fields=self.issue_fields,
            start=start,
            limit=self.api_limit,
        )
        return issues

    def get_issues_by_project(self, project: str) -> List[Dict]:
        issue_list = []
        start = 0

        issues = self._get_issues_with_jql(project, start=start)
        n_issues_in_batch = issues["maxResults"]
        issue_list.extend(issues["issues"])
        n_issues = len(issue_list)

        while n_issues < issues["total"]:
            start += n_issues_in_batch
            issues = self._get_issues_with_jql(project, start=start)
            n_issues_in_batch = issues["maxResults"]
            issue_list.extend(issues["issues"])
            n_issues = len(issue_list)

        return issue_list

    def format_issues(self, issues: List[Dict]) -> List[Dict]:
        formatted_issues = []
        for issue in issues:
            formatted_issue = {"key": issue["key"]}

            for field in self.issue_fields:
                field_value = issue["fields"][field]
                if isinstance(field_value, dict) and "name" in field_value:
                    field_value = field_value["name"]
                formatted_issue[field] = field_value

            formatted_issues.append(formatted_issue)
        return formatted_issues

    def create_issue(
        self, project: str, summary: str, description: str, extra_fields: Dict[str, Any]
    ) -> Dict:
        issuetype = extra_fields.pop("issuetype", {"name": "Task"})
        if isinstance(issuetype, str):
            issuetype = {"name": issuetype}

        issue = self.jira.issue_create(
            fields={
                "project": {"key": project},
                "summary": summary,
                "description": description,
                "issuetype": issuetype,
                **extra_fields,
            }
        )
        # issue = {"id": "...", "key": "project-xxx", "self": "{atlassian_host}/rest/api/2/issue/{id}}
        return issue
