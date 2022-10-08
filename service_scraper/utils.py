import logging


def get_stream_logger(logger_name=None, fmt=None, log_level=logging.DEBUG):
    fmt = fmt or "[%(asctime)s] [%(levelname)-8s] [%(name)s]: %(message)s"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level=log_level)
    formatter = logging.Formatter(fmt=fmt)
    ch = logging.StreamHandler()
    ch.setLevel(level=log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
