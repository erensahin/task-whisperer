from typing import Any, Dict, List

import streamlit as st

from task_whisperer.src.page_helpers.create_task import create_task_description
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar


def render_task_summary_input():
    st.markdown("### Enter Task Summary")
    task_summary = st.text_area("Task Summary", "")
    return task_summary


def render_task_description_output(task_description: Dict[str, Any]):
    with st.container(border=True):
        st.markdown("### Task Description")
        st.markdown(task_description.get("answer"))
        st.divider()
        if task_description.get("similar_tasks"):
            st.markdown("### Similar Tasks")
            for i, similar_task in enumerate(task_description["similar_tasks"]):
                similar_task = _parse_similar_task_string(similar_task)
                st.markdown(
                    f"**Similar Task {i+1}**\n\n"
                    f"**Summary:** {similar_task['summary']}\n\n"
                    f"**Description:** {similar_task['description']}"
                )
                st.divider()


def render_project_selection(projects: List[str]):
    st.markdown("### Project")
    project = st.selectbox("Select Project", projects)
    return project


def _parse_similar_task_string(similar_task: str) -> Dict[str, str]:
    """
    Parse similar task into summary and description parts.

    :param similar_task: similar task string in the format
        "Summary: <summary>\nDescription: <description>"
    :type similar_task: str
    :return: dictionary of summary - description pair
    :rtype: Dict[str, str]
    """
    splitted = similar_task.split("\n")
    summary = ":".join(splitted[0].split(":")[1:]).strip()
    description = "\n".join(splitted[1:])
    description = ":".join(description.split(":")[1:]).strip()
    return {"summary": summary, "description": description}


if __name__ == "__main__":
    st.set_page_config(page_title="Create Task", page_icon="📈", layout="wide")
    sidebar_config = render_sidebar()
    st.title("Create Task Description From Summary")

    its_kind = sidebar_config["its_config"]["selected_its"]
    llm_config = sidebar_config["llm_config"]
    llm_kind = llm_config["selected_llm"]
    projects = sidebar_config["its_config"]["projects"].split(",")
    projects = [p for p in projects]

    with st.container(border=True):
        selected_project = render_project_selection(projects)
        task_summary = render_task_summary_input()
        submitted = st.button(f"Create {its_kind} Task Description")
        if submitted:
            if not task_summary:
                st.error("Task Summary cannot be empty.")

            else:
                with st.spinner(f"Generating {its_kind} description. Please wait..."):
                    task = create_task_description(
                        llm_kind, llm_config, task_summary, selected_project
                    )
                    render_task_description_output(task)
