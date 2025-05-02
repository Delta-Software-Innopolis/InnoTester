import os

from ITPHelper.Core.ITPHelperBot import *
from ITPHelper.Core.ModeratorCommands import *
from ITPHelper.Core.UserCommands import *


async def start():
    if not os.path.exists("probes"):
        os.mkdir("probes")

    await dp.start_polling(instance)

