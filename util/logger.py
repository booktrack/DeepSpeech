import logging


# setup our logger from config
def setup_logging(config):
    if not "Logging" in config:
        raise ValueError("invalid configuration, missing [Logging]")
    logging_config = config["Logging"]
    logger = logging.getLogger("ds-logger")
    file_handler = logging.FileHandler(logging_config['filename'])
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    level = logging_config["level"].lower()
    if level == "debug":
        logger.setLevel(logging.DEBUG)
    elif level == "warn" or level == "warning":
        logger.setLevel(logging.WARNING)
    elif level == "info" or level == "information":
        logger.setLevel(logging.INFO)
    elif level == "error":
        logger.setLevel(logging.ERROR)
