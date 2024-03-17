from typing import Any, Dict, List, Union

import streamlit as st

from task_whisperer import CONFIG

ITS_OPTIONS = list(CONFIG["its_config"].keys())
LLM_OPTIONS = list(CONFIG["llm_config"].keys())


def render_sidebar():
    sidebar_config = {"its_config": {}, "llm_config": {}}

    with st.sidebar:
        st.markdown("**ITS Selection**")
        its_config = _render_its_config()
        sidebar_config["its_config"] = its_config

        st.markdown("**LLM Selection**")
        llm_config = _render_llm_config()
        sidebar_config["llm_config"] = llm_config

    return sidebar_config


def _render_its_config():
    selected_its = st.selectbox(
        label="Select ITS (Issue Tracking System)", options=ITS_OPTIONS, index=0
    )
    its_options: Dict[str, Any] = CONFIG["its_config"][selected_its]
    its_config = _populate_options(its_options)

    its_config["selected_its"] = selected_its
    return its_config


def _render_llm_config():
    selected_llm = st.selectbox(
        label="Select LLM Backend", options=LLM_OPTIONS, index=0
    )
    llm_options: Dict[str, Any] = CONFIG["llm_config"][selected_llm]
    llm_config = _populate_options(llm_options)

    llm_config["selected_llm"] = selected_llm

    return llm_config


def _populate_options(options_dict: Dict[str, Union[Dict, List, str]]) -> Dict:
    option_config = {}

    for key, options in options_dict.items():
        if not options.get("hidden"):
            option_config[key] = st.text_input(
                label=options.get("label", key),
                value=options.get("default_value", {}),
                type="password" if options.get("password") else "default",
            )
        else:
            option_config[key] = options["options"]

    return option_config
