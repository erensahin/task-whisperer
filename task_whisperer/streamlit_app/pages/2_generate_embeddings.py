from typing import Any, Dict

import streamlit as st

from task_whisperer.src.page_helpers.generate_embeddings import (
    GenerateEmbeddingsService,
)
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar


class GenerateEmbeddingsRenderer:
    def __init__(self, its_config: Dict[str, Any], llm_config: Dict[str, Any]):
        self.its_config = its_config
        self.llm_config = llm_config
        self.its_kind = self.its_config["selected_its"]
        self.llm_kind = self.llm_config["selected_llm"]
        self.projects = self.its_config["projects"].split(",")
        self.projects = [p for p in self.projects if p]
        self.generate_embeddings_service = GenerateEmbeddingsService(
            self.llm_kind, self.its_kind, self.llm_config
        )

    def generate_embeddings(self) -> None:
        embeddings_paths = {}
        for project in self.projects:
            embeddings_path = self.generate_embeddings_service.create_embeddings(
                project
            )
            embeddings_paths[project] = embeddings_path

        self.generate_embeddings_service.save_embeddings_paths(embeddings_paths)

    def render_embedding_generation_layout(self) -> None:
        st.markdown("### Click Generate Embeddings button to create embeddings")
        project_names = ",".join(self.projects)
        st.markdown(f"**Projects: {project_names}**")
        st.markdown("A separate embedding index will be created for each project.")
        submitted = st.button("Generate Embeddings 🚀", type="primary")
        if submitted:
            if not self.llm_config["api_key"]:
                st.warning(
                    f"Please enter your {self.llm_kind} API key to continue.", icon="⚠️"
                )
                return

            if not self.projects:
                st.warning(f"'Projects' is required but it is missing!", icon="⚠️")
                return

            with st.spinner(
                f"Generating {self.llm_kind} embeddings for {project_names}. "
                "Please wait..."
            ):
                self.generate_embeddings()
                st.success("Embeddings generated successfully! 🎉")

    def render_page_container(self) -> None:
        with st.container(border=True):
            col1, col2 = st.columns(2)

            with col1:
                renderer.render_embedding_generation_layout()

            with col2:
                st.markdown("### Project - Faiss Indices on Internal Datastore")
                jira_task_metadata = self.generate_embeddings_service.load_metadata()
                st.table(jira_task_metadata)


if __name__ == "__main__":
    st.set_page_config(page_title="Embeddings", page_icon="🔢", layout="wide")
    sidebar_config = render_sidebar()
    st.title("Generate Embeddings From Task Summaries & Descriptions")

    renderer = GenerateEmbeddingsRenderer(
        sidebar_config["its_config"], sidebar_config["llm_config"]
    )

    renderer.render_page_container()
