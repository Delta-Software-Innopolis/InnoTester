import os

from InnoTester.Core.InnoTesterBot import instance, dp
from InnoTester.Core.ModeratorHandles import * # noqa F403
from InnoTester.Core.UserHandles import * # noqa F403


async def start():
    if not os.path.exists(path := "data/probes"): os.mkdir(path) # noqa E701
    if not os.path.exists(path := "data/references"): os.mkdir(path) # noqa E701
    if not os.path.exists(path := "data/testgens"): os.mkdir(path) # noqa E701

    await dp.start_polling(instance)

