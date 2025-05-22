import os
import logging
import aiogram
import asyncio
from logging.handlers import RotatingFileHandler, QueueHandler
from pythonjsonlogger.json import JsonFormatter

import InnoTester.Utils.Config as Config


DATEFMT = "%d.%m.%Y-%H:%M:%S"


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot: aiogram.Bot, reseiver_ids: list[int], level=logging.ERROR):
        super().__init__(level)
        self.bot = bot
        self.reseiver_ids = reseiver_ids

    def emit(self, record):
        try:
            msg = self.format(record)

            try: asyncio.get_running_loop()
            except: return

            for id in self.reseiver_ids:
                asyncio.create_task(
                    self.bot.send_message(
                        chat_id=id,
                        text=msg
                    )
                )

        except Exception as e:
            self.handleError(record)

        
class UserFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = 'N/A'
        if not hasattr(record, 'username'):
            record.username = 'unknown'
        return super().format(record)


readableFormatter = UserFormatter(
    "%(asctime)s [%(levelname)s] (%(user_id)s @%(username)s) %(message)s",
    datefmt=DATEFMT
)

jsonFormatter = JsonFormatter(
    "{asctime}{levelname}{message}",
    style="{",
    datefmt=DATEFMT
)

telegramFormatter = logging.Formatter(
    "ERROR HAPPENED\n\n"
    "%(message)s"
)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(readableFormatter)

if not os.path.exists(path := "data/logs"): os.mkdir(path)
fileHandler = RotatingFileHandler(
    "data/logs/InnoTester.log",
    encoding="utf-8",
    maxBytes = 512000, # 512kb
)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(jsonFormatter)

logger_bot = aiogram.Bot(token=Config.token)
maintainers = [
    1815094825
]
telegramHandler = TelegramLogHandler(logger_bot, maintainers)
telegramHandler.setFormatter(telegramFormatter)

logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        streamHandler,
        fileHandler,
        telegramHandler
    ]
)


from typing import Literal, TypeAlias
from aiogram.types import Message, CallbackQuery

LevelStr: TypeAlias = Literal["debug", "info", "warn", "error", "critical"]


def _rawLog(event: Message | CallbackQuery, level: int, msg: str):
    user = event.from_user
    logging.log(
        level, msg,
        extra={
            "user_id": user.id,
            "username": user.username
        }
    )


def log(event: Message | CallbackQuery, level: LevelStr, msg: str):
    match level:
        case 'debug': level = logging.DEBUG
        case 'info': level = logging.INFO
        case 'warn': level = logging.WARN
        case 'error': level = logging.ERROR
        case 'critical': level = logging.CRITICAL

    return _rawLog(event, level, msg)


def logInfo(event: Message | CallbackQuery, msg: str):
    return _rawLog(event, logging.INFO, msg)

def logError(event: Message | CallbackQuery, msg: str):
    return _rawLog(event, logging.ERROR, msg)

def logCritical(event: Message | CallbackQuery, msg: str):
    return _rawLog(event, logging.CRITICAL, msg)


def logMissuse(event: Message | CallbackQuery, command: str):
    if command.startswith('/'): command = command[1:]
    return logInfo(event, f"Missused /{command}")

def logNotPermitted(event: Message | CallbackQuery, command: str):
    if command.startswith('/'): command = command[1:]
    return logInfo(event, f"Not permitted to use /{command}")
