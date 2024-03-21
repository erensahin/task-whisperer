import pandas as pd
import re

VALID_ISSUE_TYPES = ["Task", "Bug"]


def clean_description(description: str) -> str:
    # remove accountid from text
    cleaned_text = re.sub(r"\[~accountid:[^\]]+\]", "", description)
    # remove file attachments [^file.extension]
    cleaned_text = re.sub(r"\[\^.*?\]", "", description)
    # remove image attachment !image-xxx.png|width=111,height=111!
    cleaned_text = re.sub(r"\!image.*?\!", "", description)
    return cleaned_text.strip()


def preprocess_issues(
    df: pd.DataFrame,
    description_col_name: str = "description",
    description_length_threshold: int = 100,
):
    cleaned_col_name = f"{description_col_name}_cleaned"

    df = df[df[description_col_name].notna()]
    df = df[df["issuetype"].isin(VALID_ISSUE_TYPES)]

    df[cleaned_col_name] = df[description_col_name].apply(clean_description)
    df[f"{description_col_name}_len"] = df[cleaned_col_name].str.len()

    return df[df[f"{description_col_name}_len"] >= description_length_threshold]
