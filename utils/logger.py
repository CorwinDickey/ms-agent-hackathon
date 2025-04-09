import logging

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Return a logger instance with a given name and logging level.
# If no formatter is provided, use the default formatter.
def get_logger(
    name: str,
    level: int = logging.INFO,
    formatter: logging.Formatter = DEFAULT_FORMAT
  ) -> logging.Logger:
  logger = logging.getLogger(name)
  logger.setLevel(level)

  if not logger.handlers:
    # create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(formatter)

    logger.addHandler(ch)

  return logger