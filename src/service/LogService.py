from __future__ import annotations
from typing import Optional
from pathlib import Path
from loguru import logger
from enum import Enum
import sys


class LogLevel(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class LogService:
    __instance: LogService = None
    __flagInitialized: bool = False

    def __init__(self, path: Optional[Path] = Path.cwd().parent / 'log'):

        if not LogService.__flagInitialized:
            path_log: Path = path
            logger.remove()
            # Ajouter une nouvelle configuration de fichier
            logger.add(path_log,
                       format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}")
            # logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

            __flagInitialized: bool = True

    def callbackLogException(self, e: Exception):
        self.debug(str(e))

    @staticmethod
    def debug(message: str):
        logger.debug(message)

    @staticmethod
    def info(message: str):
        logger.info(message)

    @staticmethod
    def warn(message: str):
        logger.warning(message)

    @staticmethod
    def error(message: str):
        logger.error(message)

    @staticmethod
    def critical(self, message: str):
        logger.critical(message)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance
