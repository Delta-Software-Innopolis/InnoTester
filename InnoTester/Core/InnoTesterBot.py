from aiogram import Bot, Dispatcher
from InnoTester.Utils.Logger import Logger
import InnoTester.Utils.Config as Config

from InnoTester.Core.Assignments import AssignmentsManager, CodeManager


class InnoTesterBot(Bot):
    def __init__(self):
        super().__init__(token=Config.token)


instance = InnoTesterBot()
dp = Dispatcher()
logger = Logger("log.txt")

assignmentsManager = AssignmentsManager()
codeManager = CodeManager()
