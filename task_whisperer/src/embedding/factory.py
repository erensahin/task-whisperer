from typing import Dict, Type

from task_whisperer.src.embedding.base import BaseEmbeddings


class EmbeddingFactory:
    """EmbeddingFactory"""

    def __init__(self):
        self._its_clients: Dict[str, BaseEmbeddings] = {}

    def register(self, kind: str, its_client: BaseEmbeddings):
        self._its_clients[kind] = its_client

    def get(self, kind: str) -> Type[BaseEmbeddings]:
        klass = self._its_clients.get(kind)
        if not klass:
            raise ValueError(
                f"{kind} is not a registered Embeddings. Registered Embeddings "
                f"classes are: {list(self._its_clients.keys())}"
            )

        return klass


embedding_factory = EmbeddingFactory()
