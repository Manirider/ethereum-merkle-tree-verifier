import logging
import os

from dotenv import load_dotenv

load_dotenv()

ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()

LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a standard logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
