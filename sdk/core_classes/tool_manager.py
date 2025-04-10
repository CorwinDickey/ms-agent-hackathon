from ollama import Client, ChatResponse
from logging import Logger
from typing import Dict, List, Any

from sdk.utils.logger import get_logger
from sdk.core_classes.chat_messages import ChatMessages, Message
from sdk.core_classes.tool_interface import ToolInterface
from sdk.services.ollama_client_factory import OllamaClientFactory

class ToolManager:
  # Manages one or more tools. Allows you:
  #   - Register multiple tools
  #   - Retrieve their definitions
  #   - Invoke the correct tool by name
  #   - Handle the entire tool call sequence
  def __init__(
    self,
    logger: Logger = None,
    client: Client = None
  ):
    self.tools: Dict[str, ToolInterface] = {}
    self.logger = logger or get_logger(self.__class__.__name__)
    self.client = client or OllamaClientFactory.create_client()

  def register_tool(self, tool: ToolInterface) -> None:
    # Register a tool by using its function name as the key.
    tool_def = tool.get_definition()
    tool_name = tool_def["function"]["name"]
    self.tools[tool_name] = tool
    self.logger.debug(f"Registered tool '{tool_name}': {tool_def}")

  def get_tool_definitions(self) -> List[Dict[str, Any]]:
    # Return the list of tool definitions in the format expected by the Ollama API.
    definitions = []
    for name, tool in self.tools.items():
      tool_def = tool.get_definition()["function"]
      self.logger.debug(f"Tool definition retrieved for '{name}': {tool_def}")
      definitions.append({"type": "function", "function": tool_def})
    return definitions
  
  def handle_tool_call_sequence(
    self,
    response: ChatResponse,
    return_tool_response_as_is: bool,
    messages: ChatMessages,
    model_name: str
  ) -> str:
    # If the model wants to call a tool, parse the function arguments, invoke the tool,
    # then optionally return the tool's raw output or feed it back to the model for a final answer.

    # we take the first tool call from the model's response
    first_tool_call = response.message.tool_calls[0]
    tool_name = first_tool_call.function.name
    self.logger.info(f"Handling tool call: {tool_name}")

    args = first_tool_call.function.arguments
    self.logger.info(f"Tool arguments: {args}")

    if tool_name not in self.tools:
      error_message = f"Error: The requested tool '{tool_name}' is not registered."
      self.logger.error(error_message)
      raise ValueError(error_message)
    
    # invoke the tool
    self.logger.debug(f"Invoking tool '{tool_name}'")
    tool_response = self.tools[tool_name].run(args)
    self.logger.info(f"Tool '{tool_name}' response: {tool_response}")

    # if returning the tool response "as is", just store and return the response
    if return_tool_response_as_is:
      self.logger.debug("Returning the tool response as-is without further LLM calls.")
      messages.add_assistant_message(tool_response)
      return tool_response
    
    self.logger.debug(f"Tool call: {first_tool_call}")
    # otherwise, feed the tool's response back to the LLM for a final answer
    function_call_result_message: Message = {
      "role": "tool",
      "content": tool_response
    } 

    complete_payload = messages.get_messages()
    complete_payload.append(response.message)
    complete_payload.append(function_call_result_message)

    self.logger.debug("Calling the model again with the tool response to get the final answer.")
    # build parameter dict
    params = {
      "model": model_name,
      "messages": complete_payload
    }

    response_after_tool_call: ChatResponse = self.client.chat(**params)

    final_message = response_after_tool_call.message.content
    self.logger.debug("Received final answer from model after tool call.")
    return final_message