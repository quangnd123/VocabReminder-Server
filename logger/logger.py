import logging
import os

base_dir = os.path.dirname(__file__)

def get_logger(name: str, file_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # ← Prevent propagation to root logger

    if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(file_name) for h in logger.handlers):
        log_path = os.path.join(base_dir, "logs", file_name)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger

def get_error_logger(name: str = "error_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    logger.propagate = False  # ← Prevent propagation to root logger

    log_path = os.path.join(base_dir, "logs", "errors.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith("errors.log") for h in logger.handlers):
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger
