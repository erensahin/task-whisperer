import os
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback
import tiktoken

from task_whisperer.src.task_generation.base import BaseTaskGenerator


GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "prompt_templates")

JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=True)


class OpenAITaskGenerator(BaseTaskGenerator):
    """OpenAITaskGenerator"""

    kind = "openai"

    def __init__(
        self,
        api_key: str,
        faiss_index_root_path: str,
        model: str = GPT_MODEL,
        embedding_model: str = EMBEDDING_MODEL,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.faiss_index_root_path = faiss_index_root_path

    def get_n_tokens(self, query: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(query))

    def read_embeddings(self, project: str):
        embedding_path = os.path.join(
            self.faiss_index_root_path,
            self.kind,
            f"faiss_index_{project}_{self.embedding_model}",
        )

        embedder = OpenAIEmbeddings(api_key=self.api_key, model=self.embedding_model)
        faiss_db = FAISS.load_local(embedding_path, embedder)
        return embedder, faiss_db

    def get_task_embedding(
        self, embedder: OpenAIEmbeddings, task_summary: str, task_desc: str = ""
    ) -> Tuple[List[float], int]:
        task_def = f"Summary: {task_summary}\nDescription: {task_desc}"
        n_tokens = self.get_n_tokens(task_def)
        embedded = embedder.embed_query(task_def)
        return embedded, n_tokens

    def get_similar_queries(
        self,
        faiss_db,
        embedder: OpenAIEmbeddings,
        task_summary: str,
        task_desc: str = "",
        n_similar: int = 5,
    ):
        task_embed, n_tokens = self.get_task_embedding(
            embedder, task_summary, task_desc
        )
        similar_questions = faiss_db.similarity_search_by_vector(
            task_embed, k=n_similar
        )
        similar_questions = [
            similar_question.page_content for similar_question in similar_questions
        ]
        return similar_questions, n_tokens

    def get_system_prompt(self):
        with open(os.path.join(TEMPLATES_PATH, "system.txt"), "r") as f:
            return f.read()

    def get_user_prompt(self, task_summary: str, similar_tasks: List[str]):
        similar_tasks = "\n\n".join(
            [f'"""\n{similar_task}\n"""' for similar_task in similar_tasks]
        )
        template = JINJA_ENV.get_template("user.txt")

        return template.render(similar_tasks=similar_tasks, task_summary=task_summary)

    def get_answer(self, prompt, temperature: float = 0):
        chat = ChatOpenAI(
            api_key=self.api_key, model_name=self.model, temperature=temperature
        )
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt),
        ]
        with get_openai_callback() as cb:
            response = chat.invoke(messages)
            return response, cb

    def create_task_description(
        self,
        project: str,
        task_summary: str,
        task_desc: str = "",
        n_similar_tasks: int = 5,
        temperature: float = 0,
    ):
        embedder, faiss_db = self.read_embeddings(project)

        if n_similar_tasks > 0:
            similar_tasks, n_tokens = self.get_similar_queries(
                faiss_db, embedder, task_summary, task_desc, n_similar_tasks
            )
        else:
            similar_tasks = []
            n_tokens = 0

        prompt = self.get_user_prompt(task_summary, similar_tasks)
        answer, callback = self.get_answer(prompt, temperature)

        # TODO: use a logger here
        print(callback)

        return {
            "answer": answer.content,
            "callback": callback,
            "n_tokens": n_tokens,
            "similar_tasks": similar_tasks,
        }
