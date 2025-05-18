import os

from InnoTester.Core.InnoTesterBot import *
from InnoTester.Core.ModeratorHandles import *
from InnoTester.Core.UserHandles import *


async def start():
    if not os.path.exists(path := "data/probes"): os.mkdir(path)
    if not os.path.exists(path := "data/references"): os.mkdir(path)
    if not os.path.exists(path := "data/testgens"): os.mkdir(path)

    await dp.start_polling(instance)

