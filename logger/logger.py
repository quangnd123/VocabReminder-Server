import logging
import os 

base_dir = os.path.dirname(__file__)

def get_logger(name: str, file_name: str) -> logging.Logger:
    """
    Gets a logger with the specified name.

    Args:
        name (str): The name of the logger.
        file_name (str): Log to this file.

    Returns:
        logging.Logger: The logger.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set logging level
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  # Log format
        datefmt="%Y-%m-%d %H:%M:%S",  # Timestamp format
        encoding="utf-8",  # Encoding
        filename=base_dir + "/logs/" + file_name,  # Log file
        filemode="a"  # Append to log file
    )

    logger = logging.getLogger(name)
    return logger