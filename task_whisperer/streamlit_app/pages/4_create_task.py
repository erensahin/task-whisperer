from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from task_whisperer import CONFIG
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar
from task_whisperer.src.page_helpers.create_task import create_task
from task_whisperer.src.steamlit_helpers.widget import InputWidgetOption

STAGE_NAME = "4_create_task_stage"


class CreateTaskRenderer:
    def __init__(self, its_config: Dict[str, Any]):
        self.its_config = its_config
        self.its_kind = self.its_config["selected_its"]
        self.projects = self.its_config["projects"].split(",")
        self.projects = [p for p in self.projects if p]

    def can_submit(self, task_summary: str, task_description: str, extra_options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        # construct from config template for its configuration
        config_template = CONFIG["its_config"][self.its_kind]
        required_but_missing = []

        for key, value in config_template.items():
            if value.get("required") and not self.its_config.get(key):
                required_but_missing.append(value.get("label") or key)

        for field_id, field_value in extra_options.items():
            if not field_value:
                required_but_missing.append(field_id)

        if not task_summary:
            required_but_missing.append("Task Summary")
        if not task_description:
            required_but_missing.append("Task Description")

        return len(required_but_missing) == 0, required_but_missing

    def render_task_summary_input(self) -> str:
        st.markdown("### Enter Task Summary")
        task_summary = st.text_area("Task Summary", "")
        return task_summary

    def render_fields_and_custom_fields(
        self, issue_create_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        options = {}
        for field_definition in issue_create_options.get("fields", []):
            options[field_definition["field_id"]] = self._render_field(field_definition)

        for field_definition in issue_create_options.get("custom_fields", []):
            options[field_definition["field_id"]] = self._render_field(field_definition)

        return options

    def render_task_creation_layout(
        self, task_summary: str, task_description: str, project: str
    ) -> Optional[str]:
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
            extra_options = self.render_fields_and_custom_fields(
                self.its_config["issue_create_options"]
            )

            can_submit, missing_values = self.can_submit(task_summary, task_description, extra_options)

            submitted = st.form_submit_button(f"Create Task 🚀", type="primary")
            if not submitted:
                return task_id

        if can_submit:
            with st.spinner("Creating task. Please wait..."):
                # response = {"key": "1234"}
                response = create_task(
                    self.its_kind,
                    self.its_config,
                    task_summary,
                    task_description,
                    project,
                    extra_options,
                )
                task_id = response["key"]
                st.success(f"Task created successfully. Task ID: {response['key']}")
            _refresh_session_stage()
        else:
            for value in missing_values:
                st.warning(f"'{value}' is required but it is missing!", icon="⚠️")

        return task_id

    def render_project_selection(self) -> str:
        st.markdown("### Project")
        project = st.selectbox("Select Project", self.projects)
        return project

    def render_task_summary_form(self) -> str:
        task_summary = self.render_task_summary_input()
        submitted = False
        with st.form(f"Create {self.its_kind} Task Description"):
            submitted = st.form_submit_button(
                f"Create {self.its_kind} Task Description"
            )
            if submitted:
                st.session_state[STAGE_NAME] = "task_creation_submitted"
                st.session_state["submitted_task_summary"] = task_summary

        if (
            st.session_state[STAGE_NAME] == "task_creation_submitted"
            and not task_summary
        ):
            st.error("Task Summary cannot be empty.")
            return None

        return task_summary

    def render_page_container(self) -> Optional[str]:
        if STAGE_NAME not in st.session_state:
            st.session_state[STAGE_NAME] = "page_initialized"

        task_summary = st.session_state.get("submitted_task_summary", "")
        task_desription_generated = st.session_state.get(
            "task_description_generated", ""
        )

        selected_project = self.render_project_selection()

        task_id = self.render_task_creation_layout(
            task_summary, task_desription_generated, selected_project
        )
        return task_id

    def _render_field(self, field_definition: Dict[str, Any]) -> Any:
        default_value = field_definition.get("value", "")
        widget = InputWidgetOption(
            label=field_definition["label"],
            value=default_value,
            is_text_input=isinstance(default_value, str),
        )
        return widget.render(st)


def _refresh_session_stage():
    st.session_state.pop("submitted_task_summary", None)
    st.session_state.pop("task_description_generated", None)


if __name__ == "__main__":
    st.set_page_config(page_title="Create Task", page_icon="🚀", layout="wide")
    sidebar_config = render_sidebar()
    st.title("Create Task")

    its_config = sidebar_config["its_config"]
    renderer = CreateTaskRenderer(its_config)

    with st.container(border=True):
        renderer.render_page_container()
