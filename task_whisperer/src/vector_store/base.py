from abc import ABC, abstractmethod
from typing import List, Tuple

from task_whisperer.src.embedding.base import BaseEmbeddings


class BaseVectorStore(ABC):
    """BaseVectorStore"""

    @abstractmethod
    def __init__(
        self, faiss_index_root_path: str, embedding_generator: BaseEmbeddings
    ) -> None:
        pass

    @abstractmethod
    def read_embeddings(self, project: str):
        pass

    @abstractmethod
    def get_embedding(
        self, task_summary: str, task_desc: str = ""
    ) -> Tuple[List[float], int]:
        pass

    @abstractmethod
    def similarity_search(
        self,
        project: str,
        task_summary: str,
        task_desc: str = "",
        n_similar: int = 5,
    ) -> Tuple[List[str], int]:
        pass
