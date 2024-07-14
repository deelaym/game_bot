import logging


def setup_logging(app) -> None:
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
