from abc import ABC, abstractmethod

from task_whisperer.src.vector_store.base import BaseVectorStore


class BaseTaskGenerator(ABC):
    """OpenAITaskGenerator"""

    @abstractmethod
    def __init__(
        self,
        api_key: str,
        vector_store: BaseVectorStore,
        model: str,
    ) -> None:
        pass

    @abstractmethod
    def create_task_description(
        self,
        project: str,
        task_summary: str,
        task_desc: str = "",
        n_similar_tasks: int = 5,
        temperature: float = 0,
    ):
        pass
