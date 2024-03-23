import streamlit as st

from task_whisperer.src.steamlit_helpers.sidebar import render_sidebar

if __name__ == "__main__":
    st.set_page_config(page_title="Task Whisperer", page_icon="🐎")
    st.title("🐎 Task Whisperer")
    st.subheader("Welcome to Task Whisperer: Your Ultimate Task Description Assistant!")
    st.divider()

    st.subheader("Why Task Whisperer?")
    st.markdown(
        """
        TaskWhisperer is your one-stop solution for crafting detailed and
        precise task descriptions with ease. Say goodbye to tedious manual task
        creation and hello to streamlined workflows and increased productivity!
        """
    )

    st.subheader("Features")
    st.markdown(
        """
        - 🔍 Seamlessly Fetch Issues from Issue Tracking Systems. Currently, JIRA is supported.
        - 🚀 Generate Embeddings from Issue Descriptions to prepare for LLM-based task generation.
        - 🔮 Input a task summary and watch the magic happen with a single click!
        - 📝 Review and edit generated task descriptions and submit to ITS with a single click!
        """
    )

    st.subheader("How to Use Task Whisperer?")
    st.markdown("**Simply Navigate the Pages:**")
    st.page_link("pages/1_onboard_issues.py", label="Fetch Issues", icon="🔍")
    st.page_link(
        "pages/2_generate_embeddings.py", label="Generate Embeddings", icon="🔢"
    )
    st.page_link(
        "pages/3_generate_task_description.py",
        label="Generate Task Description",
        icon="🔮",
    )
    st.page_link("pages/4_create_task.py", label="Create Task", icon="🚀")

    sidebar_config = render_sidebar()
