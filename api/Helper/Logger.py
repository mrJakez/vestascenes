import logging
import os
import sys


def setup_custom_logger(file):
    logger = logging.getLogger(os.path.splitext(os.path.basename(file))[0])
    logger.setLevel(logging.DEBUG)

    # Entferne alte Handler, um doppelte Logs zu vermeiden
    if logger.hasHandlers():
        logger.handlers.clear()

    # Hinzufügen des Console Handlers
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

