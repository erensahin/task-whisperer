from typing import Dict, Type

from task_whisperer.src.issue_tracking.base import BaseITSClient


class ITSClientFactory:
    """ITSClientFactory"""

    def __init__(self):
        self._its_clients: Dict[str, BaseITSClient] = {}

    def register(self, kind: str, its_client: BaseITSClient):
        self._its_clients[kind] = its_client

    def get(self, kind: str) -> Type[BaseITSClient]:
        klass = self._its_clients.get(kind)
        if not klass:
            raise ValueError(
                f"{kind} is not a registered ITSClient. Registered ITSClient "
                f"classes are: {list(self._its_clients.keys())}"
            )

        return klass


ITS_factory = ITSClientFactory()
