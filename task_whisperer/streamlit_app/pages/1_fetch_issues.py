from typing import Any, Dict, List, Tuple

import streamlit as st

from task_whisperer import CONFIG
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar
from task_whisperer.src.page_helpers.issues import IssueService


class IssueFetchRenderer:
    def __init__(self, its_config: Dict[str, Any]):
        self.its_config = its_config
        self.its_kind = self.its_config["selected_its"]
        self.projects = self.its_config["projects"].split(",")
        self.projects = [p for p in self.projects if p]
        self.issue_service = IssueService(self.its_config, self.its_kind)

    def can_fetch(self) -> Tuple[bool, List[str]]:
        config_template = CONFIG["its_config"][self.its_kind]
        required_but_missing = []

        for key, value in config_template.items():
            if value.get("required") and not self.its_config.get(key):
                required_but_missing.append(value.get("label") or key)

        return len(required_but_missing) == 0, required_but_missing

    def render_project_fetch_container(self):
        st.markdown(
            f"When you hit the button, {self.its_kind} tasks will be fetched "
            f"for the selected projects:"
        )
        st.markdown(f"{self.its_config['projects']}")
        submitted = st.button("Fetch 🔽", type="primary")
        if not submitted:
            return

        can_fetch_issues, missing_values = self.can_fetch()

        if can_fetch_issues:
            project_names = ",".join(self.projects)
            with st.spinner(f"Fetching issues for {project_names}. Please wait..."):
                issue_list_by_project = self.issue_service.fetch_issues(self.projects)

                info_text = "Obtained issues successfully! 🎉 \n"
                for project, issues in issue_list_by_project.items():
                    info_text += f"{project}: {len(issues)}\n"

                st.success(info_text)
                self.issue_service.save_issues(issue_list_by_project)
        else:
            for value in missing_values:
                st.warning(f"'{value}' is required but it is missing!", icon="⚠️")

    def render_project_task_metadata_table(self) -> None:
        st.markdown("### Project - Tasks on Internal Datastore")
        project_task_metadata = self.issue_service.load_metadata()
        st.table(project_task_metadata)

    def render_issues_dataframe(self):
        selected_project = st.selectbox(
            label="Select a project to overview its issues", options=self.projects
        )
        if not selected_project:
            return

        issues = self.issue_service.load_issues(selected_project)
        st.dataframe(issues)


if __name__ == "__main__":
    st.set_page_config(page_title="Fetch Issues", page_icon="🔍", layout="wide")
    sidebar_config = render_sidebar()
    its_config = sidebar_config["its_config"]

    renderer = IssueFetchRenderer(its_config)

    st.title("Fetch Task Information")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            renderer.render_project_fetch_container()

        with col2:
            renderer.render_project_task_metadata_table()

    renderer.render_issues_dataframe()
