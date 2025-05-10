from aiogram import types
from aiogram.filters.command import Command
import aiofiles
import os
import shutil
from io import BytesIO


from ITPHelper.Core.ITPHelperBot import dp, instance, assignmentsManager, codeManager
import ITPHelper.Utils.Config as Config
from ITPHelper.Utils.Exceptions import *


# utils

def build_assignments_list(assignments: list) -> str:
    return "\n".join(
        str(assignment)
            .replace("(", r"\(`") # for markdown coolness
            .replace(")", r"`\)")
        for assignment in assignments
    )


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

        if (caption := message.caption) == None or len(caption.split()) != 2:
            await message.answer(
                "Usage:\n"
                "`/uploadreference <assignment_id>`\n"
                "Document has to be attached to the message\!\n"
                "Use /list to see all the assignments",
                parse_mode="MarkdownV2"
            )
            return

        if message.document is None:
            await message.answer("You need to perform this command in the message with attached file")
            return

        try:
            ext = message.document.file_name.split('.')[-1]
            id = message.caption.split()[1]
            assignment = await assignmentsManager.getAssignment(id)

            file = await instance.get_file(message.document.file_id)
            io_code = BytesIO()
            await instance.download_file(file.file_path, io_code)
            code = io_code.read().decode("utf-8")

            new_reference = await codeManager.addReference(id, message.from_user.username, ext, code)
            assignment.has_reference = True
            assignment.reference_id = new_reference.id

            if all([assignment.has_reference, assignment.has_testgen]):
                assignment.status = assignment.Status.RUNNING

            await assignmentsManager.setAssignment(assignment)

            await message.answer("Reference Successfully uploaded")

        except AssignmentNotFound:
            await message.answer(
                f"Assignment with id: `{id}` not found",
                parse_mode="MarkdownV2"
            )

        return

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("uploadtestgen"))
async def uploadTestGen(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        if (caption := message.caption) == None or len(caption.split()) != 2:
            await message.answer(
                "Usage:\n"
                "`/uploadtestgen <assignment_id>`\n"
                "Document has to be attached to the message\!\n"
                "Use /list to see all the assignments",
                parse_mode="MarkdownV2"
            )
            return

        if message.document is None:
            await message.answer("You need to perform this command in the message with attached file")
            return

        try:
            ext = message.document.file_name.split('.')[-1]
            id = message.caption.split()[1]
            assignment = await assignmentsManager.getAssignment(id)

            file = await instance.get_file(message.document.file_id)
            io_code = BytesIO()
            await instance.download_file(file.file_path, io_code)
            code = io_code.read().decode("utf-8")

            new_reference = await codeManager.addTestGen(id, message.from_user.username, ext, code)
            assignment.has_testgen = True
            assignment.testgen_id = new_reference.id

            if all([assignment.has_reference, assignment.has_testgen]):
                assignment.status = assignment.Status.RUNNING

            await assignmentsManager.setAssignment(assignment)

            await message.answer("TestGen Successfully uploaded")

        except AssignmentNotFound:
            await message.answer(
                f"Assignment with id: `{id}` not found",
                parse_mode="MarkdownV2"
            )

        return
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
        await message.answer(
            "Moderator commands:\n"
            "/moderhelp - Shows this message\n"
            "/moderlist - Get the list of all moderators\n"
            "/addmoder <username> - Add a new moderator\n"
            "/removemoder <username> - Remove a moderator\n"
            "/whatsmissing - Shows what is not uploaded to the bot: test generator or reference\n"
            "/uploadtestgen - You need to perform this command only in the message with attached test generator\n"
            "/removetestgen - Removes the test generator\n"
            "/removereference - Removes the reference\n"
            "/probelist - list all currently running probes\n"
            "/removeprobe <username> - kill currently running probe\n"
            "\n"
            "Commands in dev:\n"
            "/assignments (/list) - list assignments\n"
            "/addassignment <assignment name> - add new assignment (🛠)\n"
            "/refresh - reread the .json files (after manual change)\n"
            "/uploadreference <assignment id> - You need to perform this command only in the message with attached reference\n"
        )

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


@dp.message(Command("addassignment"))
async def addAssignment(message: types.Message):
    if message.from_user.username in await Config.getModerators():
        try:

            assignment_name = ' '.join(message.text.split()[1:])
            new_assignment = await assignmentsManager.addAssignment(assignment_name)

            await message.answer(
                f"New assignment created:\n"
                fr"🛠 \(`{new_assignment.id}`\) {new_assignment.name}"
                "\n\n"
                "Consider uploading reference and testgen for it",
                parse_mode="MarkdownV2"
            )

        except AlreadyExists:
            await message.answer(
                f"Assignment named: \"{assignment_name}\" already exists\n"
                "Unusual, but consider renaming"
            )

        except NoNameProvided:
            await message.answer(
                "Usage:\n"
                "`/addassignment <assignment name>`",
                parse_mode="MarkdownV2"
            )
        
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("refresh"))
async def refreshAssignments(message: types.Message):
    if message.from_user.username in await Config.getModerators():

        old = assignmentsManager.cached.copy()
        await assignmentsManager.updateAssignments()
        new = assignmentsManager.cached

        status_message = ""
        removed, added = ([], [])

        if old != new:
            removed = [a for a in old if a not in new]
            added = [a for a in new if a not in old]
        
        if removed:
            status_message += "Removed:\n"
            status_message += build_assignments_list(removed)
            status_message += "\n"
        
        if added:
            status_message += "Added:\n"
            status_message += build_assignments_list(added)
        
        await message.answer(
            "Assignments List Refreshed:\n"
            + (status_message or "Nothing New"),
            parse_mode="MarkdownV2"
        )

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")
