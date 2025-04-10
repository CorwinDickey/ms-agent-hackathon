from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional
from ollama import Client, ChatResponse

from sdk.utils.logger import get_logger
from sdk.core_classes.chat_messages import ChatMessages
from sdk.core_classes.tool_manager import ToolManager
from sdk.core_classes.agent_signature import AgentSignature

class BaseAgent(ABC):
  # An abstract base agent that defines the high-level approach to handling user tasks
  # and orchestrating calls to the Ollama API
  def __init__(
    self,
    initial_prompt: str,
    model_name: str,
    logger: Logger = None,
    client: Client = None,
  ):
    self.initial_prompt = initial_prompt
    self.model_name = model_name
    self.messages = ChatMessages(initial_prompt)
    self.tool_manager: Optional[ToolManager] = None
    self.logger = logger or get_logger(self.__class__.__name__)
    self.client = client
    
  @abstractmethod
  def setup_tools(self) -> None:
    pass

  def add_context(self, content: str) -> None:
    self.logger.debug(f"Adding context: {content}")
    self.messages.add_user_message(content)

  def add_message(self, content: str) -> None:
    self.logger.debug(f"Adding user message: {content}")
    self.messages.add_user_message(content)

  def task(
    self,
    user_task: str,
    tool_call_enabled: bool = True,
    return_tool_response_as_is: bool = False
  ) -> str:
    if self.client is None:
      error_message = "Error: Cannot execute a task without the Client."
      self.logger.error(error_message)
      raise ValueError(error_message)
    
    self.logger.debug(f"Starting task: {user_task} (tool_call_enabled={tool_call_enabled})")

    # add user message
    self.add_message(user_task)

    tools = []
    if tool_call_enabled and self.tool_manager:
      tools = self.tool_manager.get_tool_definitions()
      self.logger.debug(f"Tools available: {tools}")

    # build parameter dict
    params = {
      "model": self.model_name,
      "messages": self.messages.get_messages(),
      "tools": tools
    }

    self.logger.debug("Sending request to LLM client...")
    response: ChatResponse = self.client.chat(**params)

    tool_calls = response.message.tool_calls
    if tool_call_enabled and self.tool_manager and tool_calls:
      self.logger.debug(f"Tool calls requested: {tool_calls}")
      return self.tool_manager.handle_tool_call_sequence(
        response,
        return_tool_response_as_is,
        self.messages,
        self.model_name
      )
    
    # no tool call, normal assistant response
    response_message = response.message.content
    self.messages.add_assistant_message(response_message)
    self.logger.debug("Task completed successfully.")
    return response.message
  
  def signature(self) -> dict:
    # Return a dictionary with:
    # - The developer prompt
    # - The model name
    # - The tool definition (function schemas)
    # - The default reasoning effort if set
    signature_obj = AgentSignature(
      developer_prompt=self.initial_prompt,
      model_name=self.model_name,
      tool_manager=self.tool_manager,
    )
    return signature_obj.to_dict()