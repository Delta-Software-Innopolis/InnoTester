import os

from ITPHelper.Core.ITPHelperBot import *
from ITPHelper.Core.ModeratorCommands import *
from ITPHelper.Core.UserCommands import *


async def start():
    if not os.path.exists(path :="probes"): os.mkdir(path)
    if not os.path.exists(path := "data/references"): os.mkdir(path)
    if not os.path.exists(path := "data/testgens"): os.mkdir(path)

    await dp.start_polling(instance)

