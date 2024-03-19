from typing import Any, Dict, List

from abc import ABC, abstractmethod


class BaseITSClient(ABC):
    """BaseITSClient"""

    @abstractmethod
    def __init__(
        self, url: str, username: str, password: str, its_config: Dict, **kwargs
    ) -> None:
        pass

    @abstractmethod
    def get_issues_by_project(self, project: str, **kwargs) -> List[Dict]:
        pass

    @abstractmethod
    def format_issues(self, issues: List[Dict], **kwargs) -> List[Dict]:
        pass

    @abstractmethod
    def create_issue(self, project: str, summary: str, description: str, extra_fields: Dict[str, Any]) -> Dict:
        pass
