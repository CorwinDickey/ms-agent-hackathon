import logging
from logging import Logger
from ollama import Client

from sdk.utils.logger import get_logger
from sdk.core_classes.base_agent import BaseAgent
from sdk.core_classes.tool_manager import ToolManager
from sdk.services.ollama_client_factory import OllamaClientFactory
from tools.python_test_tool import PythonTestTool
from main import DEFAULT_MODEL_NAME

default_logger = get_logger("PythonCodeExecAgent", level=logging.INFO)

client = OllamaClientFactory.create_client()

class PythonAgent(BaseAgent):
  # An agent specialized in writing and testing python code in a docker container.

  def __init__(
    self,
    initial_prompt: str = """
    You are a senior software engineer specialized in writing python code. Your tasks include generating code to pass a set of unit tests, running the tests against the generated code, and repeating those two steps until the tests all pass. Follow these guidelines:

    1. The user will provide the name of the test file located in the directory '/home/sandboxuser'.
    2. The user will also supply context, including:
    - The definition of the method being tested, including typing of parameters and expected return type.
    - A brief description of what the code is expected to do.
    3. Generate python code to pass the tests and call the tool 'test_python_code' to test the code and get results.
    4. If the tests fail, identify which parts of the code are causing the tests to fail and fix them, then re-run the tests.
    5. Repeat until all tests pass and you have 100 percent branch and line coverage.
    6. You can use python libraries pandas and numpy, but try to avoid using external libraries wherever possible.
    7. Your code should be optimized for minimal space and time complexity.
    """,
    model_name: str = DEFAULT_MODEL_NAME,
    logger: Logger = default_logger,
    client: Client = client,
  ):
    super().__init__(
      initial_prompt,
      model_name,
      logger,
      client)
    self.setup_tools()

  def setup_tools(self) -> None:
    # create a ToolManager, instantiate the PythonTestTool and register it with the ToolManager.
    self.tool_manager = ToolManager(logger=self.logger, client=self.client)

    python_test_tool = PythonTestTool()

    self.tool_manager.register_tool(python_test_tool)