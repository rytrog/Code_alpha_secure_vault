from .utils.logger import system_logger
from .config import settings


def on_shutdown():
    system_logger.info(f"{settings.APP_NAME} shutting down...")
    system_logger.info("Cleanup completed. Goodbye.")
