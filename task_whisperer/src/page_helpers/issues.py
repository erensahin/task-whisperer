from datetime import datetime
import os
from typing import Any, Dict, List

import pandas as pd
import yaml

from task_whisperer import CONFIG, PROJECT_ROOT
from task_whisperer.src.issue_tracking import (
    BaseITSClient, ITS_factory, MANDATORY_FIELDS
)
from task_whisperer.src.embedding.preprocessing import preprocess_issues

DATASTORE_PATH = os.path.join(PROJECT_ROOT, CONFIG["datastore_path"], "issues")
os.makedirs(DATASTORE_PATH, exist_ok=True)


class IssueService:
    def __init__(self, its_config: Dict[str, Any], its_kind: str):
        self.its_config = its_config
        self.its_kind = its_kind

    def fetch_issues(self, projects: List[str]) -> Dict[str, List[Dict]]:
        assert projects, "projects list must be non-empty!"

        its_client: BaseITSClient = ITS_factory.get(self.its_kind)(
            url=self.its_config["url"],
            username=self.its_config["username"],
            password=self.its_config["password"],
            its_config=self.its_config,
        )

        issue_list_dict = {}
        for project in projects:
            issues = its_client.get_issues_by_project(project)
            formatted_issues = its_client.format_issues(issues)
            issue_list_dict[project] = formatted_issues

        return issue_list_dict

    def save_issues(self, issue_list_by_project: Dict[str, List[Dict]]):
        its_kind_root_path = os.path.join(DATASTORE_PATH, self.its_kind)
        os.makedirs(its_kind_root_path, exist_ok=True)
        meta_path = os.path.join(its_kind_root_path, "_meta.yml")

        meta = self._read_metadata(meta_path)

        for project, issues in issue_list_by_project.items():
            issues_path = os.path.join(its_kind_root_path, f"{project}_issues.csv")
            df = pd.DataFrame(issues)
            df.to_csv(issues_path, index=False)

            issues_processed_path = os.path.join(
                its_kind_root_path, f"{project}_issues_processed.csv"
            )
            df_processed = preprocess_issues(df)
            df_processed.to_csv(issues_processed_path, index=False)

            now_ts = datetime.now().timestamp()
            new_info = {
                "_updated_at": now_ts,
                "issue_count": len(df),
                "issue_count_after_preprocess": len(df_processed),
                "processed_issues_path": issues_processed_path,
            }

            if project in meta:
                meta[project] = {**meta[project], **new_info}
            else:
                meta[project] = {"_created_at": now_ts, **new_info}

        self._write_metadata(meta, meta_path)

    def load_issues(self, project: str) -> pd.DataFrame:
        try:
            issues_path = os.path.join(
                DATASTORE_PATH, self.its_kind, f"{project}_issues.csv"
            )
            df = pd.read_csv(issues_path)
            return df
        except:
            return pd.DataFrame(columns=[])

    def load_metadata(self, include_path: bool = True) -> List[Dict]:
        try:
            meta_path = os.path.join(DATASTORE_PATH, self.its_kind, "_meta.yml")

            with open(meta_path) as f:
                meta = yaml.safe_load(f)

            if not meta:
                return None

            meta_prepared = []
            for project, project_meta in meta.items():
                created_at = datetime.utcfromtimestamp(project_meta["_created_at"])
                updated_at = datetime.utcfromtimestamp(project_meta["_updated_at"])
                meta_prepared.append(
                    {
                        "project": project,
                        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "issue_count": project_meta["issue_count"],
                        "issue_count_after_preprocess": project_meta[
                            "issue_count_after_preprocess"
                        ],
                        "processed_issues_path": os.path.relpath(
                            project_meta["processed_issues_path"], PROJECT_ROOT
                        ),
                    }
                )

            return meta_prepared
        except:
            return None

    def upload_issues(self, project: str, uploaded_file: Any):
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        assert set(MANDATORY_FIELDS).issubset(df.columns), f"Missing mandatory fields: {MANDATORY_FIELDS}"

        its_kind_root_path = os.path.join(DATASTORE_PATH, self.its_kind)
        os.makedirs(its_kind_root_path, exist_ok=True)
        meta_path = os.path.join(its_kind_root_path, "_meta.yml")

        issues_path = os.path.join(
            DATASTORE_PATH, self.its_kind, f"{project}_issues.csv"
        )
        df.to_csv(issues_path, index=False)

        issues_processed_path = os.path.join(
            its_kind_root_path, f"{project}_issues_processed.csv"
        )
        df_processed = preprocess_issues(df)
        df_processed.to_csv(issues_processed_path, index=False)

        meta = self._read_metadata(meta_path)

        now_ts = datetime.now().timestamp()
        new_info = {
            "_updated_at": now_ts,
            "issue_count": len(df),
            "issue_count_after_preprocess": len(df_processed),
            "processed_issues_path": issues_processed_path,
        }

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
    def _write_metadata(meta: Dict, meta_path: str) -> None:
        with open(meta_path, "w") as f:
            yaml.dump(meta, f)
