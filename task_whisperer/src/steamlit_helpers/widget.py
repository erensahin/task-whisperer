from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union, Type

from streamlit.delta_generator import DeltaGenerator


@dataclass
class InputWidgetOption:
    """Class for keeping information of an input widget"""

    label: str
    value: Optional[Union[List[Any], Any]] = None
    required: bool = False
    is_text_input: bool = False
    is_numeric_input: bool = False
    data_type: Optional[Type] = None
    prereq: Optional[Callable] = None
    min_value: float = None
    max_value: float = None
    step: float = None
    password: bool = False

    def render(self, st_container: DeltaGenerator, **kwargs: Dict):
        """
        Helper method to render a widget

        :param st_container: streamlit container object
        :type st_container: DeltaGenerator
        :param kwargs: additional options will be passed to prereq
            of the widget, if prereq is given
        :type kwargs: Dict
        """
        if self.prereq:
            condition, return_value = self.prereq(kwargs)
            if not condition:
                return return_value

        if isinstance(self.value, list):
            input_value = st_container.selectbox(
                label=self.label, options=self.value, key=self.label
            )
        elif self.is_numeric_input:
            input_value = st_container.number_input(
                label=self.label,
                min_value=self.min_value,
                max_value=self.max_value,
                value=self.value,
                step=self.step,
                key=self.label,
            )
            input_value = (
                input_value if self.data_type is None else self.data_type(input_value)
            )
        elif self.is_text_input:
            input_value = st_container.text_input(
                label=self.label,
                value=self.value,
                type="password" if self.password else "default",
                key=self.label,
            )
        else:
            raise ValueError(f"Cant render {self.label}")

        if input_value is None and self.required:
            raise ValueError(f"{self.label} is required")

        return input_value
