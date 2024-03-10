from typing import Any, Dict

import streamlit as st

from task_whisperer import CONFIG

ITS_OPTIONS = list(CONFIG["its_config"].keys())


def render_sidebar():
    sidebar_config = {}

    with st.sidebar:
        selected_its = st.selectbox(
            label="Select ITS (Issue Tracking System)", options=ITS_OPTIONS, index=0
        )
        its_options: Dict[str, Any] = CONFIG["its_config"][selected_its]

        for key, options in its_options.items():
            sidebar_config[key] = st.text_input(
                label=options.get("label", key),
                value=options.get("default_value", {}),
                type="password" if options.get("password") else "default",
            )

        sidebar_config["selected_its"] = selected_its

    return sidebar_config
