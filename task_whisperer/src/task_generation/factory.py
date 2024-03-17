from typing import Dict, Type

from task_whisperer.src.task_generation.base import BaseTaskGenerator


class TaskGeneratorFactory:
    """TaskGeneratorFactory"""

    def __init__(self):
        self._its_clients: Dict[str, BaseTaskGenerator] = {}

    def register(self, kind: str, its_client: BaseTaskGenerator):
        self._its_clients[kind] = its_client

    def get(self, kind: str) -> Type[BaseTaskGenerator]:
        klass = self._its_clients.get(kind)
        if not klass:
            raise ValueError(
                f"{kind} is not a registered TaskGenerator. Registered TaskGenerator "
                f"classes are: {list(self._its_clients.keys())}"
            )

        return klass


task_generator_factory = TaskGeneratorFactory()
