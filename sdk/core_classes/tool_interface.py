from abc import ABC, abstractmethod
from typing import Dict, Any

# An abstract class for any 'tool' that an agent can call.
# Every tool must provide two things:
# 1) A definition (in JSON schema format) as expected by Ollama function calling specifications.
# 2) A 'run' method to handle the logic given the arguments.
class ToolInterface(ABC):
  @abstractmethod
  def get_definition(self) -> Dict[str, Any]:
    # Return the JSON/dict definition of the tool's function.
    # Example:
    # {
    #   "function": {
    #     "name": "<tool_function_name>",
    #     "description": "<what this function does>",
    #     "parameters": { <JSON schema> }
    #   }
    # }
    pass

  @abstractmethod
  def run(self, arguments: Dict[str, Any]) -> str:
    # Execute the tool using the provided arguments and return a result as a string.
    pass