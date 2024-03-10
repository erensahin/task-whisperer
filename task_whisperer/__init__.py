import os
import yaml

PROJECT_ROOT = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yml")

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)
    DEFAULTS = CONFIG.get("defaults", {})
