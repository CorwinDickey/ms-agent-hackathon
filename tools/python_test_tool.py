import subprocess
from typing import Tuple, Dict, Any

from sdk.core_classes.tool_interface import ToolInterface
from main import DEFAULT_CONTAINER_NAME

class PythonTestTool(ToolInterface):
  # A tool that tests python code securely in a container.

  def get_definition(self) -> Dict[str, Any]:
    # Return the JSON/dict definition of the tool's function
    # in the format expected by the Ollama tool calling API.
    return {
      "function": {
        "name": "test_python_code",
        "description": "Tests python code securely in a container. The container uses the latest Python image, and has pandas and numpy installed. The container supports testing using PyTest and PyUnit (unittest), and uses coverage.py to report on the results.",
        "parameters": {
          "type": "object",
          "properties": {
            "test_file_name": {
              "type": "string",
              "description": "The file containing the tests to be run."
            },
          },
          "required": ["test_file_name"]
      }
    }
  }

  def run(self, arguments: Dict[str, Any]) -> str:
    # Test the code in a Docker container and return output report.
    test_file_name = arguments["test_file_name"]
    python_code = f"coverage {test_file_name}"
    
    output, errors = self._run_code_in_container(python_code)
    if errors:
      return f"[Error]\n{errors}"
    
    return output
  
  @staticmethod
  def _run_code_in_container(
    code: str,
    container_name: str = DEFAULT_CONTAINER_NAME,
  ) -> Tuple[str, str]:
    # Helper function that actually runs the Python tests/code inside a Docker container named 'sandbox' (by default).
    cmd = ["docker", "exec", "-i", container_name, "python", "-c", "import sys; exec(sys.stdin.read())"]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate(code)
    return out, err