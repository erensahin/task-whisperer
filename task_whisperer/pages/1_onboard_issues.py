from typing import Any, Dict, List, Tuple

import streamlit as st

from task_whisperer import CONFIG
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar
from task_whisperer.src.page_helpers.onboard import (
    fetch_issues,
    save_issues,
    load_issues,
    load_metadata,
)


def can_fetch(
    selected_its: str, selected_its_config: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    config_template = CONFIG["its_config"][selected_its]
    required_but_missing = []

    for key, value in config_template.items():
        if value.get("required") and not selected_its_config.get(key):
            required_but_missing.append(value.get("label") or key)

    return len(required_but_missing) == 0, required_but_missing


def render_project_fetch_container(
    its_kind: str, its_config: Dict[str, Any], projects: List[str]
):
    st.markdown(
        f"When you hit the button, {its_kind} tasks will be fetched "
        f"for the selected projects: {its_config['projects']}"
    )
    submitted = st.button("Fetch")
    if not submitted:
        return

    can_fetch_issues, missing_values = can_fetch(its_kind, its_config)

    if can_fetch_issues:
        project_names = ",".join(projects)
        with st.spinner(f"Fetching issues for {project_names}. Please wait..."):
            issue_list_by_project = fetch_issues(
                its_kind=its_kind,
                its_config=its_config,
                projects=projects,
            )

            info_text = "Obtained issues\n"
            for project, issues in issue_list_by_project.items():
                info_text += f"{project}: {len(issues)}\n"

            st.info(info_text)
            save_issues(its_kind, issue_list_by_project)
    else:
        for value in missing_values:
            st.warning(f"{value} is required but it is missing!", icon="⚠️")


def render_project_task_metadata_table(its_kind: str):
    st.markdown("### Project - Tasks on Internal Datastore")
    project_task_metadata = load_metadata(its_kind)
    st.table(project_task_metadata)


def render_issues_dataframe(its_kind: str, projects: List[str]):
    selected_project = st.selectbox(
        label="Select a project to overview its issues", options=projects
    )
    if not selected_project:
        return

    issues = load_issues(its_kind, selected_project)
    st.dataframe(issues)


if __name__ == "__main__":
    st.set_page_config(page_title="Onboarding", page_icon="📈", layout="wide")
    sidebar_config = render_sidebar()
    its_config = sidebar_config["its_config"]
    its_kind = its_config["selected_its"]

    st.title("Fetch Task Information")

    with st.container():
        with st.container(border=True):
            projects = its_config["projects"].split(",")
            projects = [p for p in projects]

            col1, col2 = st.columns(2)
            with col1:
                render_project_fetch_container(its_kind, its_config, projects)

            with col2:
                render_project_task_metadata_table(its_kind)

        render_issues_dataframe(its_kind, projects)
