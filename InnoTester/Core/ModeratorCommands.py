from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.utils.formatting import Code
import aiofiles
import os
import shutil
from io import BytesIO


from InnoTester.Core.InnoTesterBot import (
    dp, instance, assignmentsManager, codeManager
)
import InnoTester.Utils.Config as Config
from InnoTester.Utils.Exceptions import *


# utils

def build_assignments_list(assignments: list) -> str:
    return "\n".join(
        a.to_list_with_id()
        for a in assignments
    )


# handlers


@dp.message(Command("removereference", "removeref"))
async def cmdClearReference(message: types.Message):
    if message.from_user.id in await Config.getModerators():

        if len(message.text.split()) != 2:
            await message.answer(
                "Usage:\n"
                "`/removereference <assignment_id>`\n"
                "Use /list to see all the assignments",
                parse_mode="MarkdownV2"
            ); return

        id = message.text.split()[1]

        try:
            reference = await codeManager.getReference(id)
            await codeManager.removeReference(reference)

            assignment = await assignmentsManager.getAssignment(id)
            assignment.has_reference = False
            assignment.reference_id = None
            assignment.status = assignment.Status.NOTCONFIGURED
            await assignmentsManager.setAssignment(assignment)

            await message.answer(
                f"Reference \(`{id}`\) removed successfuly",
                parse_mode="MarkdownV2"
            )
        except CodeRecordNotFound:
            await message.answer("Reference not found :(")
        except AssignmentNotFound:
            await message.answer("Corresponding assignment not found :(")

        except Exception as e:
            await message.answer(
                "Something went wrong:\n"
                f"{str(e)}"
            )
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removetestgen", "removetg"))
async def cmdClearTestGen(message: types.Message):
    if message.from_user.id in await Config.getModerators():

        if len(message.text.split()) != 2:
            await message.answer(
                "Usage:\n"
                "`/removetestgen <assignment_id>`\n"
                "Use /list to see all the assignments",
                parse_mode="MarkdownV2"
            ); return

        id = message.text.split()[1]

        try:
            testgen = await codeManager.getTestGen(id)
            await codeManager.removeTestGen(testgen)

            assignment = await assignmentsManager.getAssignment(id)
            assignment.has_testgen = False
            assignment.testgen_id = None
            assignment.status = assignment.Status.NOTCONFIGURED
            await assignmentsManager.setAssignment(assignment)

            await message.answer(
                f"TestGen \(`{id}`\) removed successfuly",
                parse_mode="MarkdownV2"
            )
        except CodeRecordNotFound:
            await message.answer("TestGen not found :(")
        except AssignmentNotFound:
            await message.answer("Corresponding assignment not found :(")

        except Exception as e:
            await message.answer(
                "Something went wrong:\n"
                f"{str(e)}"
            )
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("uploadreference", "ureference", "uref", "aref"))
async def uploadReference(message: types.Message):
    if message.from_user.id in await Config.getModerators():

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


@dp.message(Command("uploadtestgen", "utestgen", "utg", "atg"))
async def uploadTestGen(message: types.Message):
    if message.from_user.id in await Config.getModerators():
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


@dp.message(Command("addmoder", "amoder"))
async def addModer(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /addmoder <user_id>")

        else:
            moder_id = args[1]
            if not moder_id.isnumeric():
                await message.answer(
                    "Usage: /addmoder <user_id>\n"
                    "Provide a numeric user_id please, not a username\n\n"
                    "You may see id of any user, by toggling:\n"
                    "Telegam Settings > " 
                    "Advanced > " 
                    "Experimental Settings > " 
                    "Show peer IDs in Profile"
                )
                return

            try:
                moder = await instance.get_chat(moder_id)
            except TelegramBadRequest as e:
                await message.answer(
                    f"I don't know anyone with id {moder_id}\n"
                    "Make sure the user had texted me before"
                )
                return

            with open("moderators.txt", "a") as moders:
                moders.write(f"{moder_id} @{moder.username}\n")

            await message.answer(f"Added new moderator: @{moder.username}")
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removemoder"))
async def removeModer(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        args = message.text.split()


        if len(args) == 1:
            await message.answer("Usage: /removemoder <user_id or username>")
        else:

            identifier = args[1]
            if identifier.isnumeric(): identifier = int(identifier)

            moders = await Config.getModerators(get_usernames=True)

            if identifier in moders[0]:
                await message.answer(f"I am not so stupid lol")
                return

            if identifier not in [id_or_name for m in moders for id_or_name in m]:
                await message.answer(f"This person is not in moderator list")
                return

            removed = ("id-here", "username-here")

            async with aiofiles.open("data/moderators.txt", "w") as mods: # TODO : make it asyncio Lock'ed
                data = ""                                                 # TODO : move the logic out of handler

                for id, username in moders:
                    if identifier in (id, username):
                        removed = (id, username)
                        continue # skipping removed moder

                    data += f"{id} @{username}\n"

                await mods.write(data)

            await message.answer(
                f"Removed moderator {Code(removed[0]).as_html()} @{removed[1]}",
                parse_mode="HTML"
            )
    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("moderlist", "mlist"))
async def moderList(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        msg = "Moderators:\n"
        for id, username in await Config.getModerators(get_usernames=True):
            msg += f"- {Code(id).as_html()} @{username}\n"

        await message.answer(msg, parse_mode="HTML")

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("moderhelp", "mhelp"))
async def moderHelp(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        await message.answer(
            "Moderator commands:\n"
            "/moderhelp - Shows this message\n"
            "/moderlist - Get the list of all moderators\n"
            "/addmoder <user_id> - Add a new moderator\n"
            "/removemoder <user_id or username> - Remove a moderator\n"
            "/probelist - list all currently running probes\n"
            "/removeprobe <username> - kill currently running probe\n"
            "\n"
            "Commands in dev:\n"
            "/assignments (/list) - list assignments\n"
            "/addassignment <assignment name> - add new assignment (🛠)\n"
            "/refresh - reread the .json files (after manual change)\n"
            "/uploadreference <assignment id> - You need to perform this command only in the message with attached reference\n"
            "/uploadtestgen <assignment id> - You need to perform this command only in the message with attached test generator\n"
            "/removetestgen <assignment id> - Removes the test generator\n"
            "/removereference <assignment id> - Removes the reference\n"
        )

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("removeprobe", "rprobe"))
async def removeProbe(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        args = message.text.split()

        if len(args) == 1:
            await message.answer("Usage: /removeprobe <username>")
        else:
            if os.path.exists(f"probes/{args[1]}"): # TODO : "data/probes"
                shutil.rmtree(f"probes/{args[1]}")  # TODO : "data/probes"
                await message.answer("Probe was removed successfully")
            else:
                await message.answer("Such probe does not exists")

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("probelist", "probes"))
async def probeList(message: types.Message):
    if message.from_user.id in await Config.getModerators():
        msg = "Probes:\n"
        for probe in os.listdir("probes"): # TODO : "data/probes"
            msg += probe + "\n"

        await message.answer(msg)

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")


@dp.message(Command("assignments", "list"))
async def listAssignments(message: types.Message):
    if message.from_user.id in await Config.getModerators():

        assignments_list = build_assignments_list(assignmentsManager.cached)

        await message.answer(
            "Here are all the assignments:\n"
            f"{assignments_list}",
            parse_mode="MarkdownV2"
        )

    else:
        await message.answer("Sorry, but you don't have permission to perform this command")



@dp.message(Command("addassignment", "adda"))
async def addAssignment(message: types.Message):
    if message.from_user.id in await Config.getModerators():
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
    if message.from_user.id in await Config.getModerators():

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
