"""Structured logging setup using Loguru."""

import sys
from loguru import logger

# Remove default handler
logger.remove()

# Console — pretty format for development
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# Rotating file log
logger.add(
    "logs/studyrag_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="14 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
)

import logging
# Suppress telemetry/posthog library warnings from ChromaDB
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)

__all__ = ["logger"]
