from typing import Dict, Type

from task_whisperer.src.vector_store.base import BaseVectorStore


class VectorStoreFactory:
    """VectorStoreFactory"""

    def __init__(self):
        self._vector_stores: Dict[str, BaseVectorStore] = {}

    def register(self, kind: str, vector_store: BaseVectorStore):
        self._vector_stores[kind] = vector_store

    def get(self, kind: str) -> Type[BaseVectorStore]:
        klass = self._vector_stores.get(kind)
        if not klass:
            raise ValueError(
                f"{kind} is not a registered VectorStore. "
                "Registered VectorStore "
                f"classes are: {list(self._vector_stores.keys())}"
            )

        return klass


vector_store_factory = VectorStoreFactory()
