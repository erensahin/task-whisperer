from .base import BaseTaskGenerator
from .factory import task_generator_factory
from .openai import OpenAITaskGenerator

task_generator_factory.register("openai", OpenAITaskGenerator)

__all__ = ["BaseTaskGenerator", "task_generator_factory"]
