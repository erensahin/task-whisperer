from abc import ABC, abstractmethod
import os
from typing import Any, List, Tuple

import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback
import tiktoken


GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"


class BaseTaskGenerator(ABC):
    """OpenAITaskGenerator"""

    @abstractmethod
    def __init__(
        self, api_key: str, faiss_index_root_path: str, model: str, embedding_model: str
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
