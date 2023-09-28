import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def start(target):
    logger.info("start the cadence for the target: {}".format(target))