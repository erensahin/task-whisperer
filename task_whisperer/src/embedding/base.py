from abc import ABC, abstractmethod
import os
from typing import Any, List, Tuple

from langchain_core.documents import Document

import pandas as pd


class BaseEmbeddings(ABC):
    """BaseEmbeddings"""

    @abstractmethod
    def __init__(
        self,
        api_key: str,
        faiss_index_root_path: str,
        embedding_model: str,
    ) -> None:
        pass

    @abstractmethod
    def load_documents(
        self,
        project: str,
        issues_df: pd.DataFrame,
        summary_col_name: str = "summary",
        description_col_name: str = "description_cleaned",
    ) -> List[Document]:
        pass

    @abstractmethod
    def split_documents(
        documents: List[Document], chunk_size: int = 8000
    ) -> List[Document]:
        pass

    @abstractmethod
    def embed_documents(
        self, project: str, documents: List[Document]
    ) -> Tuple[str, Any]:
        pass

    @abstractmethod
    def generate_embeddings(
        self,
        project: str,
        issues_df: pd.DataFrame,
        chunk_size: int = 8000,
        summary_col_name: str = "summary",
        description_col_name: str = "description_cleaned",
    ) -> Tuple[str, Any]:
        pass
