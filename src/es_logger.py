import logging

def setup_logging(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        '[%(asctime)s: %(levelname)s] %(module)s.%(funcName)s: %(message)s'
    ))
    logger.addHandler(ch)
    return logger

def es_log(message, payload={}):
    return 'message="{}" payload="{}"'.format(message, str(payload))

class EsLogger:

    def __init__(self, name, level=logging.INFO, setup=False):
        if setup:
            setup_logging(name)
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

    def info(self, msg, payload={}):
        self._logger.info(es_log(msg, payload))

    def error(self, msg, payload={}):
        self._logger.error(es_log(msg, payload), exc_info=True)

    def warn(self, msg, payload={}):
        self._logger.warning(es_log(msg, payload))

    def debug(self, msg, payload={}):
        self._logger.debug(es_log(msg, payload))