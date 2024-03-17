import os
from typing import Any, List, Tuple

import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback
import tiktoken

from task_whisperer.src.task_generation.base import BaseTaskGenerator


GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"


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
        encoding = tiktoken.encoding_for_model(self.model)
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

    def get_prompt(self, task_summary, similar_tasks):
        similar_tasks = "\n\n".join(
            [f'"""\n{similar_task}\n"""' for similar_task in similar_tasks]
        )

        prompt = (
            "Use the task summary and description pairs below to create a JIRA task description for the subsequent question:\n\n"
            f"{similar_tasks}\n"
            f"Please create a new JIRA task description from the Summary: {task_summary}"
        )
        return prompt

    def get_answer(self, prompt, temperature: float = 0):
        chat = ChatOpenAI(
            api_key=self.api_key, model_name=self.model, temperature=temperature
        )
        messages = [
            SystemMessage(
                content=(
                    "You are a detail oriented Software Product Owner responsible for defining tasks in a software development team. "
                    "When you do your job, you always try to be as clear and detailed as possible, you provide diagrams, code snippets, pseudocodes, etc. "
                    "Your aim is to make sure that developers understand the requirements. "
                    "You have been tasked with creating JIRA tickets for defining development requirements in the following format:\n"
                    "I want you create JIRA task descriptions in the following format:\n"
                    "1. Description: Intoduction to the task. You should come up with a story here and detail "
                    "why we are implementing this task, what is the purpose.\n"
                    "2. How: Detailed clarification of how the task should implemented. This would require "
                    "details about the implementation and tooling, libraries to be used etc. "
                    "You can be creative and include diagrams, code snippets, and suggest your own ideas from your knowledge base. "
                    "Come up with clear directives, so that the development team can understand it better.\n"
                    "3. Key Contacts: Name of stakeholders\n"
                    "4. Definition of Done:steps that should be completed before transition of task into DONE status. "
                    "You can keep it simple and dont repeat everything you have mentioned in 'How' section. "
                    "You can also include the acceptance criteria here.\n"
                )
            ),
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
        similar_tasks, n_tokens = self.get_similar_queries(
            faiss_db, embedder, task_summary, task_desc, n_similar_tasks
        )
        prompt = self.get_prompt(task_summary, similar_tasks)
        answer, callback = self.get_answer(prompt, temperature)

        return {
            "answer": answer.content,
            "callback": callback,
            "n_tokens": n_tokens,
            "similar_tasks": similar_tasks,
        }
