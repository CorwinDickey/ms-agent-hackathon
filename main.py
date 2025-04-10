DEFAULT_CONTAINER_NAME = "sandbox"
DEFAULT_MODEL_NAME = "qwen2.5-coder"

import logging
from tkinter.filedialog import askopenfilename
from agents.python_agent import PythonAgent
from docker.docker_utils import compose_up, copy_file_to_container
from sdk.utils.logger import get_logger

app_logger = get_logger("tdd.aiLogger", level=logging.INFO)

print("Composing docker...")
compose_up(app_logger)
print("Docker environment ready.")
