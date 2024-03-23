from typing import Any, Dict, List

import streamlit as st

from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar
from task_whisperer.src.page_helpers.create_task import create_task
from task_whisperer.src.steamlit_helpers.widget import InputWidgetOption

STAGE_NAME = "4_create_task_stage"


def render_task_summary_input():
    st.markdown("### Enter Task Summary")
    task_summary = st.text_area("Task Summary", "")
    return task_summary


def render_fields_and_custom_fields(issue_create_options: Dict[str, Any]):
    # render fields first
    options = {}
    for field_definition in issue_create_options.get("fields", []):
        default_value = field_definition.get("value", "")
        widget = InputWidgetOption(
            label=field_definition["label"],
            value=default_value,
            is_text_input=isinstance(default_value, str),
        )
        options[field_definition["field_id"]] = widget.render(st)

    for field_definition in issue_create_options.get("custom_fields", []):
        default_value = field_definition.get("value", "")
        widget = InputWidgetOption(
            label=field_definition["label"],
            value=default_value,
            is_text_input=isinstance(default_value, str),
        )
        options[field_definition["field_id"]] = widget.render(st)

    return options


def render_task_creation_layout(
    its_kind: str,
    its_config: Dict[str, Any],
    task_summary: str,
    task_description: str,
    project: str,
):
    task_id = None
    if st.session_state.get(STAGE_NAME, "") not in ["", "page_initialized"]:
        task_summary = ""
        task_description = ""

    st.markdown("### Task Creation")
    with st.form("Task Creation Details"):
        task_summary = st.text_input("Task Summary", task_summary)
        task_description = st.text_area(
            "Task Description", task_description, height=400
        )
        extra_options = render_fields_and_custom_fields(
            its_config["issue_create_options"]
        )
        submitted = st.form_submit_button(
            f"Create Task 🚀", on_click=_refresh_session_stage, type="primary"
        )
        if submitted:
            with st.spinner("Creating task. Please wait..."):
                # response = {"key": "1234"}
                response = create_task(
                    its_kind,
                    its_config,
                    task_summary,
                    task_description,
                    project,
                    extra_options,
                )
                task_id = response["key"]
                st.success(f"Task created successfully. Task ID: {response['key']}")

    return task_id


def render_project_selection(projects: List[str]):
    st.markdown("### Project")
    project = st.selectbox("Select Project", projects)
    return project


def render_task_summary_form(its_kind: str):
    task_summary = render_task_summary_input()
    submitted = False
    with st.form(f"Create {its_kind} Task Description"):
        submitted = st.form_submit_button(f"Create {its_kind} Task Description")
        if submitted:
            st.session_state["stage"] = "task_description_submitted"
            st.session_state["submitted_task_summary"] = task_summary

    if st.session_state["stage"] == "task_description_submitted" and not task_summary:
        st.error("Task Summary cannot be empty.")
        return None

    return task_summary


def render_page_container(its_config: Dict[str, Any], projects: List[str]):
    if STAGE_NAME not in st.session_state:
        st.session_state[STAGE_NAME] = "page_initialized"

    its_kind = its_config["selected_its"]

    task_summary = st.session_state.get("submitted_task_summary", "")
    task_desription_generated = st.session_state.get("task_description_generated", "")

    selected_project = render_project_selection(projects)

    task_id = render_task_creation_layout(
        its_kind, its_config, task_summary, task_desription_generated, selected_project
    )
    return task_id


def _refresh_session_stage():
    st.session_state.pop("submitted_task_summary", None)
    st.session_state.pop("task_description_generated", None)


if __name__ == "__main__":
    st.set_page_config(page_title="Create Task", page_icon="🚀", layout="wide")
    sidebar_config = render_sidebar()
    st.title("Create Task")

    its_config = sidebar_config["its_config"]
    projects = its_config["projects"].split(",")
    projects = [p for p in projects]

    with st.container(border=True):
        render_page_container(its_config, projects)
