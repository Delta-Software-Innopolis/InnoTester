from aiogram import types
from aiogram.filters.command import Command
import aiofiles
import os
import shutil

from ITPHelper.Core.ITPHelperBot import dp, instance
import ITPHelper.Utils.Config as Config


@dp.message(Command("removereference"))
async def cmdClearReference(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        filename = "reference." + Config.getLanguage("reference")

        if os.path.exists(filename):
            os.remove(filename)
            await message.answer("Reference was removed successfully")
        else:
            await message.answer("Reference was not uploaded. Ignoring this command.")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removetestgen"))
async def cmdClearTestGen(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        filename = "testgen." + Config.getLanguage("testgen")

        if os.path.exists(filename):
            os.remove(filename)
            await message.answer("Test generator was removed successfully")
        else:
            await message.answer("Test generator was not uploaded. Ignoring this command.")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("uploadreference"))
async def uploadReference(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        if message.document is None:
            await message.answer("You need to perform this command in the message with attached file")
            return

        filename = "reference." + Config.getLanguage("reference")

        await Config.updateWhoLoaded(message.from_user.username)

        if not os.path.exists(filename):
            path = (await instance.get_file(message.document.file_id)).file_path
            extension = str(path).split(".")[-1]
            await instance.download_file(path, "reference." + extension)
            await message.answer("Reference has been uploaded successfully")
        else:
            await message.answer("Reference has already been uploaded")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("uploadtestgen"))
async def uploadTestGen(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        if message.document is None:
            await message.answer("You need to perform this command in the message with attached file")
            return

        filename = "testgen." + Config.getLanguage("testgen")

        if not os.path.exists(filename):
            path = (await instance.get_file(message.document.file_id)).file_path
            extension = str(path).split(".")[-1]
            await instance.download_file(path, "testgen." + extension)
            await message.answer("Test generator has been uploaded successfully")
        else:
            await message.answer("Test generator has already been uploaded")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("whatsmissing"))
async def whatsMissing(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        if not os.path.exists("testgen." + Config.getLanguage("testgen")):
            await message.answer("Test generator")

        if not os.path.exists("reference." + Config.getLanguage("reference")):
            await message.answer("Reference")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("assignnum"))
async def updateAssign(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /assignnum <number>")
        else:
            try:
                if not (1 <= int(args[1])):
                    await message.answer("Assignment number should be positive")
                    return

                await Config.updateAssignNum(int(args[1]))
                await message.answer("Assignment number was updated")
            except ValueError:
                await message.answer("Argument 1 should be a number")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("addmoder"))
async def addModer(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /addmoder <username>")
        else:
            with open("moderators.txt", "a") as moders:
                moders.write(f"{args[1]}\n")
                await message.answer(f"Added new moderator: @{args[1]}")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removemoder"))
async def removeModer(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /removemoder <username>")
        else:
            moders = await Config.getModerators()

            if args[1] == moders[0]:
                await message.answer(f"I am not so stupid lol")
                return

            if args[1] not in moders:
                await message.answer(f"This person does not in moderator list")
                return

            moders.remove(args[1])

            async with aiofiles.open("moderators.txt", "w") as mods:
                n = ""

                for name in moders:
                    n += name + "\n"

                await mods.write(n)

            await message.answer(f"Removed moderator @{args[1]}")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("moderlist"))
async def moderList(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        msg = "Moderators:\n"
        for name in await Config.getModerators():
            msg += f"- @{name}\n"

        await message.answer(msg)

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("moderhelp"))
async def moderHelp(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        await message.answer("Moderator commands:\n/moderhelp - Shows this message\n/moderlist - Get the list of all moderators\n/addmoder <username> - Add a new moderator\n/removemoder <username> - Remove a moderator\n/whatsmissing - Shows what is not uploaded to the bot: test generator or reference\n/uploadtestgen - You need to perform this command only in the message with attached test generator\n/uploadreference - You need to perform this command only in the message with attached reference\n/removetestgen - Removes the test generator\n/removereference - Removes the reference\n")

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removeprobe"))
async def removeProbe(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /removeprobe <username>")
        else:
            if os.path.exists(f"probes/{args[1]}"):
                shutil.rmtree(f"probes/{args[1]}")
                await message.answer("Probe was removed successfully")
            else:
                await message.answer("Such probe does not exists")

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("probelist"))
async def probeList(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        msg = "Probes:\n"
        for probe in os.listdir("probes"):
            msg += probe + "\n"

        await message.answer(msg)

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")

