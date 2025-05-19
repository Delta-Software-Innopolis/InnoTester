from aiogram import Bot, Dispatcher
import InnoTester.Utils.Config as Config
from InnoTester.Utils.Logging import *

from InnoTester.Core.Logic import (
    AssignmentsManager, CodeManager,
    ModersManager
)


class InnoTesterBot(Bot):
    def __init__(self):
        super().__init__(token=Config.token)


instance = InnoTesterBot()
dp = Dispatcher()

assignmentsManager = AssignmentsManager()
codeManager = CodeManager()
modersManager = ModersManager()

logging.getLogger().debug("Configuration issued")