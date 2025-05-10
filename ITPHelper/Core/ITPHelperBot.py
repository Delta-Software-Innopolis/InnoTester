from aiogram import Bot, Dispatcher
from ITPHelper.Utils.Logger import Logger
import ITPHelper.Utils.Config as Config

from ITPHelper.Core.Assignments import AssignmentsManager, CodeManager


class ITPHelperBot(Bot):
    def __init__(self):
        super().__init__(token=Config.token)


instance = ITPHelperBot()
dp = Dispatcher()
logger = Logger("log.txt")

assignmentsManager = AssignmentsManager()
codeManager = CodeManager()
