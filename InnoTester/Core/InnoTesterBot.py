from aiogram import Bot, Dispatcher

from InnoTester.Utils import Config 
from InnoTester.Utils.Logging import logging
from InnoTester.Utils.Middlewares import CustomMiddleware
from InnoTester.Core.Logic import (
    AssignmentsManager, CodeManager,
    ModersManager
)


class InnoTesterBot(Bot):
    def __init__(self):
        super().__init__(token=Config.token)


instance = InnoTesterBot()
dp = Dispatcher()

dp.message.middleware(CustomMiddleware())
dp.callback_query.middleware(CustomMiddleware())

assignmentsManager = AssignmentsManager()
codeManager = CodeManager()
modersManager = ModersManager()
