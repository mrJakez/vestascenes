import logging
import os
import sys
import time
import requests


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

logger = setup_custom_logger(__file__)
logger.info("runner started. Python version: " + sys.version)

time.sleep(5)  # pause for 5 seconds - to provide time for the controller to boot up
while True:
    logger.debug("runner executed")
    r = requests.get("http://api:80/execute")
    # print(r.text)

    time.sleep(15)  # pause for 15 seconds
