# ./modules/logger.py
# ==================================================
# standard
import sys
# requirements
from loguru import logger
# --------------------------------------------------

watcher = logger

watcher_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
watcher.remove()
watcher.add(sys.stderr, format=watcher_format)
