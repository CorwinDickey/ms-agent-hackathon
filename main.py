import logging
import requests
from tkinter.filedialog import askopenfilename
from agents.python_agent import PythonAgent
from sdk.utils.global_variables import DEFAULT_MODEL_NAME
from sdk.utils.docker_utils import compose_up, copy_file_to_container
from sdk.utils.logger import get_logger

app_logger = get_logger("tdd.aiLogger", level=logging.INFO)

print("Composing docker...")
compose_up(app_logger)
print("Docker environment ready.")

print("Setting up Ollama...")
url = "http://localhost:11434/api/pull"
data = {"model":DEFAULT_MODEL_NAME}
headers = {"content-type":"application/json"}
response = requests.post(url, json=data, headers=headers)
print("Finished setting up Ollama.")