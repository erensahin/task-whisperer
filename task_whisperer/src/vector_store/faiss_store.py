import os
from typing import List, Tuple

from langchain_community.vectorstores.faiss import FAISS
import tiktoken

from task_whisperer.src.embedding.base import BaseEmbeddings

EMBEDDING_MODEL = "text-embedding-ada-002"


class FaissVectorStore:
    """FaissVectorStore"""

    kind = "faiss"

    def __init__(
        self, faiss_index_root_path: str, embedding_generator: BaseEmbeddings
    ) -> None:
        assert faiss_index_root_path, "faiss_index_root_path is required"
        self.faiss_index_root_path = faiss_index_root_path
        self.embedding_generator = embedding_generator

    def _get_embedding_path(self, project: str) -> str:
        embedding_model = self.embedding_generator.embedding_model
        return os.path.join(
            self.faiss_index_root_path,
            "openai",
            f"faiss_index_{project}_{embedding_model}",
        )

    def get_n_tokens(self, query: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(query))

    def read_vector_index(self, project: str):
        embedding_path = self._get_embedding_path(project)
        faiss_db = FAISS.load_local(
            embedding_path, self.embedding_generator.embedding_model
        )
        return faiss_db

    def get_embedding(
        self, task_summary: str, task_desc: str = ""
    ) -> Tuple[List[float], int]:
        task_def = f"Summary: {task_summary}\nDescription: {task_desc}"
        n_tokens = self.get_n_tokens(task_def)
        embedded = self.embedding_generator.embed_query(task_def)
        return embedded, n_tokens

    def similarity_search(
        self,
        project: str,
        task_summary: str,
        task_desc: str = "",
        n_similar: int = 5,
    ) -> Tuple[List[str], int]:
        faiss_db = self.read_vector_index(project)
        task_embed, n_tokens = self.get_embedding(task_summary, task_desc)
        similar_questions = faiss_db.similarity_search_by_vector(
            task_embed, k=n_similar
        )
        similar_questions = [
            similar_question.page_content for similar_question in similar_questions
        ]
        return similar_questions, n_tokens
