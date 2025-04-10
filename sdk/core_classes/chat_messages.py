from typing import List, Dict, TypedDict

# defines a message as a Typed Dictionary
class Message(TypedDict):
  role: str
  content: str

# defines the structure of a message
class ChatMessages:
  def __init__(self, initial_prompt: str):
    self.messages: List[Message] = []
    self.add_system_message(initial_prompt)
  
  # adds a message to the stack from the system
  def add_system_message(self, content: str) -> None:
    self.messages.append({"role": "system", "content": content})

  # adds a message to the stack from the user
  def add_user_message(self, content: str) -> None:
    self.messages.append({"role": "user", "content": content})
  
  # adds a message to the stack from the assistant
  def add_assistant_message(self, content: str) -> None:
    self.messages.append({"role": "assistant", "content": content})\
    
  # adds a message to the stack from the tool
  def add_tool_message(self, content: str) -> None:
    self.messages.append({"role": "tool", "content": content})
  
  # gets all messages in the stack
  def get_messages(self) -> List[Dict[str, str]]:
    return self.messages