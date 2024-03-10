import streamlit as st

from task_whisperer.src.streamlit_utils.sidebar import render_sidebar
from task_whisperer.src.streamlit_utils.onboard import (
    fetch_issues,
    save_issues,
    load_issues,
    load_metadata,
)


st.set_page_config(page_title="Onboarding", page_icon="📈", layout="wide")
sidebar_config = render_sidebar()
its_config = sidebar_config["its_config"]
its_kind = its_config["selected_its"]

st.title("Fetch Task Information")

with st.container():
    with st.container(border=True):
        projects = its_config["projects"].split(",")
        projects = [p for p in projects]
        project_names = ",".join(projects)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"When you hit the button, {its_kind} tasks will be fetched "
                f"for the selected projects: {its_config['projects']}"
            )
            submitted = st.button("Fetch")
            if submitted:
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
        with col2:
            st.markdown("### Project - Tasks on Internal Datastore")
            project_task_metadata = load_metadata(its_kind)
            st.table(project_task_metadata)

    selected_project = st.selectbox(
        label="Select a project to overview its issues", options=projects
    )
    if selected_project:
        issues = load_issues(its_kind, selected_project)
        st.dataframe(issues)
