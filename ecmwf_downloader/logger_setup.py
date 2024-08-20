import logging


def setup_logger(name: str,
                 log_file: str = "ecmwf_downloader.log",
                 level=logging.INFO) -> logging.Logger:
    """
    Sets up and returns a logger.

    Args:
        name (str): The name of the logger.
        log_file (str): The file to log to.
        level (int): The logging level.

    Returns:
        logging.Logger: Configured logger instance.
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger
