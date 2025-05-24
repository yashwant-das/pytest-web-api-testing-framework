import logging
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def get_logger(name: str, level: str = LOG_LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)

    # Check if handlers are already added to avoid duplication if called multiple times
    if not logger.handlers:
        logger.setLevel(getattr(logging, level, logging.INFO))  # Default to INFO if invalid level

        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)

        # File Handler (optional, useful for debugging CI or long runs)
        # log_file_path = "test_run.log"
        # fh = logging.FileHandler(log_file_path)
        # fh.setLevel(logging.DEBUG) # Log more details to file

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        )
        ch.setFormatter(formatter)
        # fh.setFormatter(formatter)

        logger.addHandler(ch)
        # logger.addHandler(fh)

        # Prevent log messages from propagating to the root logger if it has handlers
        logger.propagate = False

    return logger


# Example of a root logger setup (optional, if you want a global default)
# logging.basicConfig(level=LOG_LEVEL,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     handlers=[logging.StreamHandler(sys.stdout)])
