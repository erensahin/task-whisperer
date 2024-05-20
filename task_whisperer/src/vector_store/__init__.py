from .base import BaseVectorStore
from .factory import vector_store_factory
from .faiss_store import FaissVectorStore

vector_store_factory.register("faiss", FaissVectorStore)

__all__ = ["FaissVectorStore", "vector_store_factory"]
