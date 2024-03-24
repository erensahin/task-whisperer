from typing import Any, Dict, Optional

import streamlit as st

from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar
from task_whisperer.src.page_helpers.generate_task_description import (
    create_task_description,
)

STAGE_NAME = "3_generate_task_description_stage"


class GenerateTaskDescriptionRenderer:
    def __init__(self, its_config: Dict[str, Any], llm_config: Dict[str, Any]):
        self.its_config = its_config
        self.llm_config = llm_config
        self.its_kind = self.its_config["selected_its"]
        self.llm_kind = self.llm_config["selected_llm"]
        self.projects = self.its_config["projects"].split(",")
        self.projects = [p for p in self.projects if p]

    def render_task_summary_input(self) -> str:
        st.markdown("### Enter Task Summary")
        task_summary = st.text_area("Task Summary", "")
        return task_summary

    def render_project_selection(self) -> str:
        st.markdown("### Project")
        project = st.selectbox("Select Project", self.projects)
        return project

    def render_task_description_layout(self, task_summary: str, project: str):
        with st.spinner(f"Generating Task description. Please wait..."):
            # task_response = {
            #     "answer": "This is a task description",
            #     "similar_tasks": [
            #         "Summary: Summary 1\nDescription: Description 1",
            #         "Summary: Summary 2\nDescription: Description 2",
            #     ]
            # }
            task_response = create_task_description(
                self.llm_kind, self.llm_config, task_summary, project
            )
            return self.render_task_description_output(task_summary, task_response)

    def render_task_description_output(
        self,
        task_summary: str,
        task_response: Dict[str, Any],
    ):
        with st.container(border=True):
            col1, col2 = st.columns([0.6, 0.4])
            with col1:
                st.markdown(f"#### Task Summary: {task_summary}")
                st.markdown(f"#### Task Description")
                st.markdown(task_response["answer"])

            with col2:
                if task_response.get("similar_tasks"):
                    st.markdown("### Similar Tasks")
                    for i, similar_task in enumerate(task_response["similar_tasks"]):
                        similar_task = self._parse_similar_task_string(similar_task)
                        st.markdown(
                            f"**Similar Task {i+1}**\n\n"
                            f"**Summary:** {similar_task['summary']}\n\n"
                            f"**Description:** {similar_task['description']}"
                        )
                        if i < len(task_response["similar_tasks"]) - 1:
                            st.divider()

        return task_response["answer"]

    def render_task_summary_form(self, project: str) -> Optional[str]:
        task_summary = self.render_task_summary_input()

        def _on_create_task_description_click():
            st.session_state[STAGE_NAME] = "task_description_submitted"
            st.session_state["submitted_task_summary"] = task_summary

        st.button(
            "Create Task Description 🚀",
            on_click=_on_create_task_description_click,
            type="primary",
        )

        if st.session_state[STAGE_NAME] == "task_description_submitted":
            if not task_summary:
                st.warning("Task Summary cannot be empty.", icon="⚠️")
                return None

            if not project:
                st.warning("A project should be selected.", icon="⚠️")
                return None

        return task_summary

    def render_page_container(self):
        if STAGE_NAME not in st.session_state:
            st.session_state[STAGE_NAME] = "task_summary_input"

        project = self.render_project_selection()
        task_summary = self.render_task_summary_form(project)
        task_desription_generated = None

        if not task_summary:
            st.session_state[STAGE_NAME] = "task_summary_input"
            return
        elif st.session_state.get("submitted_task_summary"):
            task_summary = st.session_state["submitted_task_summary"]

        if st.session_state[STAGE_NAME] in ["task_description_submitted"]:
            task_desription_generated = self.render_task_description_layout(
                task_summary, project
            )

        if task_desription_generated:
            st.session_state[STAGE_NAME] = "task_description_generated"
            st.session_state["submitted_task_summary"] = task_summary
            st.session_state["task_description_generated"] = task_desription_generated

        if st.session_state[STAGE_NAME] == "task_description_generated":
            if st.button("Go to Task Generation 👉"):
                st.session_state.pop(STAGE_NAME, None)
                st.switch_page("pages/4_create_task.py")

    @staticmethod
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
    st.set_page_config(
        page_title="Generate Task Description", page_icon="🔮", layout="wide"
    )
    sidebar_config = render_sidebar()
    st.title("Generate Task Description From Summary")

    renderer = GenerateTaskDescriptionRenderer(
        sidebar_config["its_config"], sidebar_config["llm_config"]
    )

    with st.container(border=True):
        renderer.render_page_container()
