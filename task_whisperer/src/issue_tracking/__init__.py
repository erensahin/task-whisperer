from .base import BaseITSClient
from .factory import ITS_factory
from .jira import JiraClient

MANDATORY_FIELDS = ["key", "project", "summary", "description", "issuetype"]

ITS_factory.register("jira", JiraClient)

__all__ = ["BaseITSClient", "ITS_factory"]
