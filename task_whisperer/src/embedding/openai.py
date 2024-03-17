import os
from typing import Any, List, Tuple

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback


EMBEDDING_MODEL = "text-embedding-ada-002"


class OpenAIEmbeddingGenerator:
    """OpenAIEmbeddingGenerator"""

    kind = "openai"

    def __init__(
        self,
        api_key: str,
        faiss_index_root_path: str,
        embedding_model: str = EMBEDDING_MODEL,
    ) -> None:
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.faiss_index_root_path = faiss_index_root_path

    def load_documents(
        self,
        project: str,
        issues_df: pd.DataFrame,
        summary_col_name: str = "summary",
        description_col_name: str = "description_cleaned",
    ) -> List[Document]:
        loaded_docs = []
        for _, row in issues_df.iterrows():
            doc = Document(
                page_content=(
                    f"summary: {row[summary_col_name]}\n"
                    f"description: {row[description_col_name]}"
                ),
                metadata={
                    "project": project,
                    "key": row["key"],
                },
            )
            loaded_docs.append(doc)

        return loaded_docs

    def split_documents(
        self, documents: List[Document], chunk_size: int = 8000
    ) -> List[Document]:
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
        splitted_docs = text_splitter.split_documents(documents)
        return splitted_docs

    def embed_documents(
        self, project: str, documents: List[Document]
    ) -> Tuple[str, Any]:
        embedder = OpenAIEmbeddings(api_key=self.api_key, model=self.embedding_model)
        embedding_path = os.path.join(
            self.faiss_index_root_path,
            self.kind,
            f"faiss_index_{project}_{self.embedding_model}",
        )
        with get_openai_callback() as cb:
            faiss_db = FAISS.from_documents(documents, embedder)
            faiss_db.save_local(embedding_path)

        return embedding_path, cb

    def generate_embeddings(
        self,
        project: str,
        issues_df: pd.DataFrame,
        chunk_size: int = 8000,
        summary_col_name: str = "summary",
        description_col_name: str = "description_cleaned",
    ):
        docs = self.load_documents(
            project, issues_df, summary_col_name, description_col_name
        )
        splitted_docs = self.split_documents(docs, chunk_size)
        embedding_path, cb = self.embed_documents(project, splitted_docs)
        return embedding_path, cb
