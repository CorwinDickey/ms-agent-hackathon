import os
import subprocess
import logging

default_sandbox_name = "sandbox"

# runs the compose.yaml file to standup the docker environment
def compose_up(logger: logging.Logger) -> None:
  cmd = ["docker", "compose", "-p", "ms-agent-hackathon", "up", "-d", "--no-recreate"]
  result = subprocess.run(cmd, capture_output=True, text=True)
  if result.returncode != 0 or result.stdout.strip() != "":
    msg = f"The docker composition failed to stand up.\n\n{result.stdout}"
    logger.error(msg)
    raise RuntimeError(msg)

# checks to see if a specified container is running
def check_container(logger: logging.Logger, container_name: str = default_sandbox_name) -> None:
  cmd = ["docker", "inspect", "-f", "{{.State.Running}}", container_name]
  result = subprocess.run(cmd, capture_output=True, text=True)
  if result.returncode != 0 or result.stdout.strip() != "":
    msg = f"The container '{container_name}' is not running.\n\n{result.stdout}"
    logger.error(msg)
    raise RuntimeError(msg)
  
# copies a file from the local directory into the specified docker container
def copy_file_to_container(logger: logging.Logger, local_file_name: str, container_name: str = default_sandbox_name) -> str:
  container_home_path = "/home/sandboxuser"
  logger.debug(f"Copying '{local_file_name}' to container '{container_name}'.")
  
  # verify the file exists
  if not os.path.isfile(local_file_name):
    error_msg = f"The local file '{local_file_name}' does not exist."
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)
  
  # verify the container is up and running
  check_container(logger, container_name)

  # copy the file into the container
  container_path = f"{container_name}:{container_home_path}/{os.path.basename(local_file_name)}"
  logger.debug(f"Running command: docker cp {local_file_name} {container_path}")
  subprocess.run(["docker", "cp", local_file_name, container_path], check=True)

  # verify the file was copied into the container
  verify_cmd = ["docker", "exec", container_name, "test", "-f",
                f"{container_home_path}/{os.path.basename(local_file_name)}"]
  verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
  if verify_result.returncode != 0:
    error_msg = f"Failed to verify the file '{local_file_name}' in the container '{container_name}'."
    logger.error(error_msg)
    raise RuntimeError(error_msg)
  
  success_msg = f"Copied {local_file_name} into {container_name}:{container_home_path}"
  logger.debug(success_msg)
  return success_msg
