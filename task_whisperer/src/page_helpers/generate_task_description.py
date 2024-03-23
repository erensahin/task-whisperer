import os
from typing import Any, Dict

from task_whisperer import PROJECT_ROOT, CONFIG
from task_whisperer.src.task_generation.factory import task_generator_factory

EMBEDDINGS_ROOT_PATH = os.path.join(
    PROJECT_ROOT, CONFIG["datastore_path"], "embeddings"
)
FAISS_ROOT_PATH = os.path.join(EMBEDDINGS_ROOT_PATH, "faiss")


def create_task_description(
    llm_kind: str,
    llm_config: Dict[str, Any],
    task_summary: str,
    project: str,
):
    task_generator_client = task_generator_factory.get(llm_kind)(
        api_key=llm_config["api_key"],
        faiss_index_root_path=FAISS_ROOT_PATH,
        model=llm_config["llm_model"],
        embedding_model=llm_config["embedding_model"],
    )
    response = task_generator_client.create_task_description(
        project,
        task_summary,
        n_similar_tasks=llm_config.get("similar_issues_count", 5),
        temperature=llm_config.get("llm_temperature", 0),
    )
    return response
