from ollama import Client

class OllamaClientFactory:
  @staticmethod
  def create_client(base_url: str = "http://localhost:11434") -> Client:
    # Create and return an Ollama client instance.
    # Ollama is on port 11434 by default.
    return Client(base_url)