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

            for id in self.reseiver_ids:
                asyncio.create_task(
                    self.bot.send_message(
                        chat_id=id,
                        text=msg
                    )
                )

        except Exception as e:
            self.handleError(record)


readableFormatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt=DATEFMT
)

jsonFormatter = JsonFormatter(
    "{asctime}{levelname}{message}{exc_info}",
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