from datetime import datetime
import os
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from task_whisperer import CONFIG, PROJECT_ROOT
from task_whisperer.src.page_helpers.issues import IssueService
from task_whisperer.src.embedding import embedding_factory

ISSUES_DATASTORE_PATH = os.path.join(PROJECT_ROOT, CONFIG["datastore_path"], "issues")
EMBEDDINGS_ROOT_PATH = os.path.join(
    PROJECT_ROOT, CONFIG["datastore_path"], "embeddings"
)
FAISS_ROOT_PATH = os.path.join(EMBEDDINGS_ROOT_PATH, "faiss")


class GenerateEmbeddingsService:
    def __init__(self, llm_kind: str, its_kind: str, llm_config: Dict[str, Any]):
        self.llm_kind = llm_kind
        self.its_kind = its_kind
        self.llm_config = llm_config

    def get_issues_meta(self) -> Dict[str, Dict[str, Any]]:
        issue_service = IssueService(its_config={}, its_kind=self.its_kind)
        issues_meta = issue_service.load_metadata()
        issues_meta = {row["project"]: row for row in issues_meta}
        return issues_meta

    def create_embeddings(self, project: str) -> str:
        os.makedirs(FAISS_ROOT_PATH, exist_ok=True)
        issues_meta = self.get_issues_meta()
        project_meta = issues_meta[project]
        processed_issues_df = pd.read_csv(
            os.path.join(PROJECT_ROOT, project_meta["processed_issues_path"])
        )

        embedding_client = embedding_factory.get(self.llm_kind)(
            api_key=self.llm_config["api_key"],
            faiss_index_root_path=FAISS_ROOT_PATH,
            embedding_model=self.llm_config["embedding_model"],
        )

        embedding_path, embedding_cb = embedding_client.generate_embeddings(
            project, processed_issues_df
        )

        # TODO: use a logger here
        print(embedding_cb)

        return embedding_path

    def load_metadata(self) -> Optional[List[Dict]]:
        try:
            meta_path = os.path.join(FAISS_ROOT_PATH, self.llm_kind, "_meta.yml")
            meta = self._read_metadata(meta_path)

            meta_prepared = []
            for project, project_meta in meta.items():
                created_at = datetime.utcfromtimestamp(project_meta["_created_at"])
                updated_at = datetime.utcfromtimestamp(project_meta["_updated_at"])
                meta_prepared.append(
                    {
                        "project": project,
                        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "embedding_path": os.path.relpath(
                            project_meta["embedding_path"], PROJECT_ROOT
                        )
                    }
                )

            return meta_prepared
        except:
            return None

    def save_embeddings_paths(self, project_embedding_paths: Dict[str, Any]) -> None:
        meta_path = os.path.join(FAISS_ROOT_PATH, self.llm_kind, "_meta.yml")
        meta = self._read_metadata(meta_path)

        for project, embedding_path in project_embedding_paths.items():
            now_ts = datetime.now().timestamp()

            new_info = {"_updated_at": now_ts, "embedding_path": embedding_path}

            if project in meta:
                meta[project] = {**meta[project], **new_info}
            else:
                meta[project] = {"_created_at": now_ts, **new_info}

        self._write_metadata(meta, meta_path)

    @staticmethod
    def _read_metadata(meta_path: str) -> Dict[str, Any]:
        try:
            with open(meta_path) as f:
                meta = yaml.safe_load(f) or {}
        except:
            meta = {}

        return meta

    @staticmethod
    def _write_metadata(meta: Dict, meta_path: str):
        with open(meta_path, "w") as f:
            yaml.dump(meta, f)
