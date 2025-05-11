import os

from InnoTester.Core.InnoTesterBot import *
from InnoTester.Core.ModeratorCommands import *
# from InnoTester.Core.UserCommands import *
from InnoTester.Core.UserNewUI import *


async def start():
    if not os.path.exists(path :="probes"): os.mkdir(path)
    if not os.path.exists(path := "data/references"): os.mkdir(path)
    if not os.path.exists(path := "data/testgens"): os.mkdir(path)

    await dp.start_polling(instance)

