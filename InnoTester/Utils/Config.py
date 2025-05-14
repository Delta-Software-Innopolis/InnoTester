import aiofiles
import os
import sys
import yaml
import aiodocker

from aiogram.utils.formatting import *

if len(sys.argv) == 1:
    print("Docker image file is not specified", file=sys.stderr)
    sys.exit(0)

dockerImageNum = sys.argv[1]

with open("token.yaml") as f:
    token = yaml.safe_load(f)["token"]

with open("compile.yaml") as f:
    compileCommands = yaml.safe_load(f)

with open("messages.yaml") as f:
    messages = yaml.safe_load(f)

with open("banlist.yaml") as f:
    banlist = yaml.safe_load(f)['banned']


def getLanguage(filename, dir = "."):
    for file in os.listdir(dir):
        name = file.split(".")[0]
        extension = file.split(".")[-1]

        if filename == name:
            return extension

    return "undefined"


async def getWhoLoaded():
    async with aiofiles.open("assign.txt") as f:
        await f.readline()
        return await f.readline()


def checkReady():
    return os.path.exists("testgen." + getLanguage("testgen")) and os.path.exists(
        "reference." + getLanguage("reference"))


async def updateWhoLoaded(username):
    async with aiofiles.open("assign.txt") as f:
        assignNum = int(await f.readline())

    async with aiofiles.open("assign.txt", "w") as f:
        text = f"{assignNum}\n{username}"
        await f.write(text)


async def updateAssignNum(num):
    async with aiofiles.open("assign.txt") as f:
        await f.readline()
        moder = await f.readline()

    async with aiofiles.open("assign.txt", "w") as f:
        text = f"{num}\n{moder}"
        await f.write(text)


async def getModerators():
    async with aiofiles.open("moderators.txt") as f:
        return list(map(lambda x: x.strip("\n"), await f.readlines()))


async def getAssignNum():
    async with aiofiles.open("assign.txt") as f:
        return await f.readline()


def errorHanler(protocol, testCount: int):
    match (protocol[0].strip("\n")):
        case "ok":
            return Text(f"All {testCount} tests have been passed successfully. This does not mean at all that your program 100% will pass all Codeforces tests. We recommend running a few more checks to make sure that the program is really working correctly.")
        case "error":
            match (protocol[1].strip("\n")):
                case "running":
                    return Text(f"An error occurred when starting the tester. Message: {''.join(protocol[2::])}")
                case "testgen":
                    return Text(f"An error occurred when generating the test. Message: {''.join(protocol[2::])}")
                case "reference":
                    return Text(f"An error occurred when running the reference. Message: {''.join(protocol[2::])}")
                case "probe":
                    return Text(f"An error occurred when running the probe. Message: {''.join(protocol[2::])}")
                case "testing":
                    return Text(f"An error occurred during the testing process. Message: {''.join(protocol[2::])}")
                case "answer":
                    return Text(f"Got invalid answer from probe program. Message:\n") + Code(''.join(protocol[2::]))

