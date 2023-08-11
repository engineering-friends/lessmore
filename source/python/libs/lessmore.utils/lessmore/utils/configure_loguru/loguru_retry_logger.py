from loguru import logger
from retry import retry
from utils_ak.loguru import configure_loguru


class LoguruRetryLogger:
    @staticmethod
    def warning(fmt, error, delay):
        logger.warning("Retrying", error=error, delay=delay)


def test():
    retry(tries=3, delay=1, logger=LoguruRetryLogger)(lambda: 1 / 0)()


if __name__ == "__main__":
    configure_loguru()
    test()
