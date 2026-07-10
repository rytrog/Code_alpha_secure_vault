import logging
import os
from pathlib import Path
from ..config import settings

LOG_DIR = settings.LOG_DIR
os.makedirs(LOG_DIR, exist_ok=True)


def _create_logger(name: str, filename: str, level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fh = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding="utf-8")
        fh.setLevel(level)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger


attack_logger = _create_logger("sentinelx.attack", "attack.log")
auth_logger = _create_logger("sentinelx.auth", "auth.log")
system_logger = _create_logger("sentinelx.system", "system.log")
ai_logger = _create_logger("sentinelx.ai", "ai.log")
