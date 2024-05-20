import os
from typing import List

from jinja2 import Environment, FileSystemLoader

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback

from task_whisperer.src.task_generation.base import BaseTaskGenerator
from task_whisperer.src.vector_store.base import BaseVectorStore


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
        vector_store: BaseVectorStore,
        model: str = GPT_MODEL,
    ) -> None:
        assert api_key, "api_key is required"
        assert model, "model is required"
        self.api_key = api_key
        self.model = model
        self.vector_store = vector_store

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
        if n_similar_tasks > 0:
            similar_tasks, n_tokens = self.vector_store.similarity_search(
                project, task_summary, task_desc, n_similar=n_similar_tasks
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
