import pytest

from loguru import logger
from retry import retry

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru


class LoguruRetryLogger:
    @staticmethod
    def warning(fmt, error, delay):
        logger.warning("Retrying", error=error, delay=delay)


@pytest.mark.slow
def test():
    try:
        retry(tries=3, delay=0.1, logger=LoguruRetryLogger)(lambda: 1 / 0)()
    except Exception as e:
        logger.exception("Failed", error=e)


if __name__ == "__main__":
    configure_loguru()
    test()
