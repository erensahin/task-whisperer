from typing import Any, Dict, List

import streamlit as st

from task_whisperer.src.page_helpers.generate_embeddings import (
    create_embeddings,
    save_embeddings_paths,
    load_metadata,
)
from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar


def generate_embeddings(
    llm_kind: str, its_kind: str, llm_config: Dict[str, Any], projects: List[str]
):
    embeddings_paths = {}
    for project in projects:
        embeddings_path = create_embeddings(llm_kind, its_kind, project, llm_config)
        embeddings_paths[project] = embeddings_path

    save_embeddings_paths(llm_kind, embeddings_paths)


def render_embedding_generation_layout(
    llm_kind: str, its_kind: str, llm_config: Dict[str, Any], projects: List[str]
):
    st.markdown("### Click Generate Embeddings button to create embeddings")
    project_names = ",".join(projects)
    st.markdown(
        f"Projects: {project_names}. A separate embedding index will be "
        "created for each project."
    )
    submitted = st.button("Generate Embeddings")
    if submitted:
        if not llm_config["api_key"]:
            st.warning(f"Please enter your {llm_kind} API key to continue.", icon="⚠️")
        else:
            with st.spinner(
                f"Generating {llm_kind} embeddings for {project_names}. "
                "Please wait..."
            ):
                generate_embeddings(llm_kind, its_kind, llm_config, projects)
                st.success("Embeddings generated successfully! 🎉")


if __name__ == "__main__":
    st.set_page_config(page_title="Embeddings", page_icon="📈", layout="wide")
    sidebar_config = render_sidebar()
    st.title("Generate Embeddings From Task Summaries & Descriptions")

    its_kind = sidebar_config["its_config"]["selected_its"]
    llm_config = sidebar_config["llm_config"]
    llm_kind = llm_config["selected_llm"]
    projects = sidebar_config["its_config"]["projects"].split(",")
    projects = [p for p in projects]

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            render_embedding_generation_layout(llm_kind, its_kind, llm_config, projects)

        with col2:
            st.markdown("### Project - Faiss Indices on Internal Datastore")
            jira_task_metadata = load_metadata(llm_kind)
            st.table(jira_task_metadata)
