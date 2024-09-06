import logging


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


def get_logger():
    logger = logging.getLogger("ai_debug_mode")

    debug_formatter = logging.Formatter("\x1b[33;20mAI DEBUG: \x1b[0m%(message)s")
    error_formatter = logging.Formatter("\x1b[31;20mAI ERROR: \x1b[0m%(message)s")

    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(debug_formatter)
    debug_handler.addFilter(LevelFilter(logging.DEBUG))

    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.INFO)
    error_handler.setFormatter(error_formatter)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    logger.addHandler(debug_handler)
    logger.addHandler(error_handler)

    return logger
