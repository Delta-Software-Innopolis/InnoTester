import asyncio
import aiofiles
import os
import shutil
from aiogram import F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import *
from aiogram.types import FSInputFile

from InnoTester.Core.InnoTesterBot import *
from InnoTester.Utils.Keyboards import *

import aiodocker
import aiodocker.exceptions


class ShareStates(StatesGroup):
    CHOOSE_ASSIGNMENT = State()
    SEND_REFERENCE = State()
    SEND_TESTGEN = State()


@dp.message(CommandStart())
async def onCmdStart(message: Message, state: FSMContext):
    await state.set_state(None) # to revert the ShareStates

    data = await state.get_data()
    
    last_message: Message = data.get("last_message")
    if last_message: await last_message.delete()

    last_message = await message.answer(
        "Welcome to InnoTester, blah blah",
        reply_markup=CHOOSE_ASSIGNMENT_KB
    )

    data["last_message"] = last_message
    await state.set_data(data)


@dp.message(Command("share"))
async def onCmdShare(message: Message, state: FSMContext):
    data = await state.get_data()

    last_message: Message = data.get("last_message")
    if last_message: await last_message.delete()

    assignment: Assignment = data.get("assignment")

    if assignment:
        last_message = await message.answer(
            text=(
                "Wanna share?\n"
                f"Chosen: {assignment}\n\n"
                "What are you sharing, fellow coder?"
            ),
            reply_markup=SHARE_KB
        )
    else:
        last_message = await message.answer(
            text=(
                "Wanna share?\n"
                "Choose the Assignment first"
            ),
            reply_markup=CHOOSE_ASSIGNMENT_SHARE_KB
        )

    data["last_message"] = last_message
    await state.set_data(data)


@dp.callback_query(F.data == SHARE_TESTGEN_CB)
async def onShareTestGenButton(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    await state.set_state(ShareStates.SEND_TESTGEN)

    await query.message.edit_text(
        "Now please, send the send the TestGen code as a file",
        reply_markup=SHARE_CANCEL_KB
    )


@dp.callback_query(F.data == SHARE_REFERENCE_CB)
async def onShareReferenceButton(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    await state.set_state(ShareStates.SEND_REFERENCE)

    await query.message.edit_text(
        "Now please, send the send the Reference code as a file",
        reply_markup=SHARE_CANCEL_KB
    )


@dp.message(StateFilter(ShareStates.SEND_REFERENCE), F.document)
async def onShareReferenceDocument(message: Message, state: FSMContext):
    data = await state.get_data()

    last_message: Message = data["last_message"]
    if last_message: await last_message.delete()

    assignment: Assignment = data.get("assignment")

    if not assignment:
        await onCmdShare(message, state)

    # TODO : add verificitaion of username != None

    last_message = await message.answer(
        "Thanks, hero!\n"
        f"Reference sent for {assignment}\n\n"
        "We'll review your code and send "
        "you the acceptance verdict afterwards\n\n"
        "Stay tuned :)"
    )

    for moder_id in await Config.getModerators(): # TODO: make adding reference by buttons
        await instance.send_document(             #       instead of manual
            moder_id,
            caption=(
                "One hero want to share his Reference\!\n"
                f"{assignment.to_list_with_id()}\n"
                f"@{message.from_user.username}\n"
            ),
            document=message.document.file_id,
            parse_mode="MarkdownV2"
        )

    data["last_message"] = last_message
    await state.set_data(data)

    await state.set_state(None)


@dp.message(StateFilter(ShareStates.SEND_TESTGEN), F.document)
async def onShareTestGenDocument(message: Message, state: FSMContext):
    data = await state.get_data()

    assignment : Assignment = data.get("assignment")

    if not assignment:
        await onCmdShare(message, state)

    last_message: Message = data["last_message"]
    if last_message: await last_message.delete()

    # TODO : add verificitaion of username != None

    last_message = await message.answer(
        "Thanks, hero!\n"
        f"TestGen sent for {assignment}\n\n"
        "We'll review your code and send "
        "you the acceptance verdict afterwards\n\n"
        "Stay tuned :)"
    )

    for moder_id in await Config.getModerators(): # TODO: make adding testgen by buttons
        await instance.send_document(             #       instead of manual
            moder_id,
            caption=(
                "One hero want to share his TestGen\!\n"
                f"{assignment.to_list_with_id()}\n"
                f"@{message.from_user.username}\n"
            ),
            document=message.document.file_id,
            parse_mode="MarkdownV2"
        )

    data["last_message"] = last_message
    await state.set_data(data)

    await state.set_state(None)


@dp.callback_query(F.data == SHARE_CANCEL_CB)
async def onCancelShare(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    await state.set_state(None)
    assignment: Assignment = data.get("assignment")

    if assignment:
        await query.message.edit_text(
            text=(
                "Wanna share?\n"
                f"Chosen: {assignment}\n\n"
                "What are you sharing, fellow coder?"
            ),
            reply_markup=SHARE_KB
        )
    else:
        await query.message.edit_text(
            text=(
                "Wanna share?\n"
                "Choose the Assignment first"
            ),
            reply_markup=CHOOSE_ASSIGNMENT_SHARE_KB
        )


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_CB)
async def onOpenAssignmentsList(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    assignments = assignmentsManager.cached
    chosenAssignment = data.get("assignment")

    data["assignment"] = None
    await state.set_data(data)

    await query.message.edit_text(
        text="Here are all the assignments:",
        reply_markup=assigListKeyboard(assignments, chosenAssignment)
    )


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_SHARE_CB)
async def onOpenAssignmentsListForShare(query: CallbackQuery, state: FSMContext):
    await state.set_state(ShareStates.CHOOSE_ASSIGNMENT)
    await onOpenAssignmentsList(query, state)


@dp.callback_query(
    StateFilter(ShareStates.CHOOSE_ASSIGNMENT),
    F.data.startswith(ASSIGNMENT_CB_PREFIX))
async def onChooseAssignmentForShare(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    id = query.data.split("_")[1]
    assignment = await assignmentsManager.getAssignment(id)

    data["assignment"] = assignment
    await state.set_data(data)

    await query.message.edit_text(
        text=(
           f"Chosen: {assignment}\n\n"
            "What are you sharing, fellow coder?"
        ),
        reply_markup=SHARE_KB
    )
    await state.set_state(None)


@dp.callback_query(F.data.startswith(ASSIGNMENT_CB_PREFIX))
async def onChooseAssignment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

    id = query.data.split("_")[1]
    assignment = await assignmentsManager.getAssignment(id)

    if not assignment.is_configured():
        reference_emoji = '✅' if assignment.has_reference else '❌'
        testgen_emoji = '✅' if assignment.has_testgen else '❌'
        await query.answer(
            "This assignment is not yet configured 🥺\n\n"
            "Current status:\n"
            f" {reference_emoji} Reference Solution\n"
            f" {testgen_emoji} Test Generator\n\n"
            "If YOU want to share your solution or "
            "test generator - type /share, be a hero 😎",
            show_alert=True
        ); return

    data["assignment"] = assignment
    await state.set_data(data)

    await query.message.edit_text(
        text=(
            "Chosen Assignment:\n"
            f"{str(assignment)}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


@dp.message(F.document)
async def onDocument(message: Message, state: FSMContext): # TODO: please, handle should not be
    dockerClient = aiodocker.Docker()                      #               93 lines of code XD
    data = await state.get_data()

    assignment = data.get("assignment")
    last_message: Message = data.get("last_message")


    if not message.from_user.username:
        await message.answer(
            "To use the bot you need to have a @username\n"
            "Set one in the Telegram settings to proceed"
        ); return

    if os.path.exists("data/probes/" + message.from_user.username):
        await last_message.edit_text(
            text=(
                "Testing started\n"
                f"Assignment: {assignment}\n"
                "⚠️ Please, wait until the previous code finishes testing process"
            ),
            reply_markup=stopTestKeyboard(message.from_user.username)
        )

        return

    if last_message: # That's important, to delete the message before document sent
        await last_message.delete()    


    if not assignment:
        last_message = await message.answer(
            text="You need first to choose the assignment",
            reply_markup=CHOOSE_ASSIGNMENT_KB
        )
        data["last_message"] = last_message
        await state.set_data(data)
        return

    path = (await instance.get_file(message.document.file_id)).file_path
    probeExtension = str(path).split(".")[-1]

    if probeExtension not in Config.compileCommands.keys():
        supportedExtensions = ""

        for i, ext in enumerate(Config.compileCommands.keys()):
            if i == len(Config.compileCommands.keys()) - 1:
                supportedExtensions += f"and .{ext}"
            else:
                supportedExtensions += f".{ext}, "

        await message.answer(f"Only {supportedExtensions} files are accepted")
        return

    await logger.info(f"{message.from_user.username} started testing solution ({probeExtension})")
    os.mkdir("data/probes/" + message.from_user.username)
    await instance.download_file(path, f"data/probes/{message.from_user.username}/probe.{probeExtension}")

    testCount = 100

    async with aiofiles.open(f"data/probes/{message.from_user.username}/iterations.txt", "w") as iters:
        if message.caption is not None:
            try:
                await iters.write(f"{int(message.caption)}")
                testCount = int(message.caption)
            except ValueError:
                await iters.write("100")
        else:
            await iters.write("100")

    async with aiofiles.open(f"data/probes/{message.from_user.username}/protocol.txt", "w") as proto:
        await proto.write("")

    async with aiofiles.open(f"data/probes/{message.from_user.username}/comparison_page.html", "w") as proto:
        await proto.write("")

    last_message = await message.answer(
        text=(
            "Testing started\n"
            f"Assignment: {assignment}"
        ),
        reply_markup=stopTestKeyboard(message.from_user.username)
    )

    data["last_message"] = last_message
    await state.set_data(data)

    pwd = os.getcwd()
    referenceExtension = Config.getLanguage(data['assignment'].reference_id, f"{pwd}/data/references")
    testgenExtension = Config.getLanguage(data['assignment'].testgen_id, f"{pwd}/data/testgens")
    username = message.from_user.username


    containerConfig = {
        "Image": Config.dockerImageNum,
        "HostConfig": {
            "AutoRemove": True,
            "Memory": 256 * 1024 * 1024,  # 256MB
            "Binds": [
                f"{pwd}/resources/compile.yaml:/testEnv/compile.yaml",
                f"{pwd}/data/probes/{username}/probe.{probeExtension}:/testEnv/probe.{probeExtension}",
                f"{pwd}/data/references/{data['assignment'].reference_id}.{referenceExtension}:/testEnv/reference.{referenceExtension}",
                f"{pwd}/data/testgens/{data['assignment'].testgen_id}.{testgenExtension}:/testEnv/testgen.{testgenExtension}",
                f"{pwd}/data/probes/{username}/protocol.txt:/testEnv/protocol.txt",
                f"{pwd}/data/probes/{username}/comparison_page.html:/testEnv/comparison_page.html",
                f"{pwd}/data/probes/{username}/iterations.txt:/testEnv/iterations.txt",
            ],
        },
        "WorkingDir": "/testEnv",
    }

    try:
        container = await dockerClient.containers.run(config=containerConfig)


        data['container'] = container
        await state.set_data(data)

        containerLog = []
        async for log in container.log(stderr=True, follow=True):
            containerLog.append(log)

        result = await container.wait()
        data = await state.get_data()

        if "testing_killed" in data:
            await last_message.edit_text(
                text=(
                    "Testing process terminated"
                ),
                reply_markup=CHANGE_ASSIGNMENT_KB
            )
            shutil.rmtree(f"data/probes/{message.from_user.username}", ignore_errors=True)
            del data["testing_killed"]

            await state.set_data(data)
            await dockerClient.close()

            return

        if result['StatusCode'] != 0:
            await last_message.edit_text(
                text=(
                    "Error occurred while testing your solution:\n"
                    f"{"".join(containerLog)}\n"
                ),
                reply_markup=CHANGE_ASSIGNMENT_KB
            )
        else:
            async with aiofiles.open(f"data/probes/{message.from_user.username}/protocol.txt") as proto:
                ans = await proto.readlines()
                await logger.info(f"Finished testing {message.from_user.username}'s solution: {''.join(ans)}")
                try:
                    await last_message.edit_text(**Config.errorHandler(ans, testCount).as_kwargs(), reply_markup=CHANGE_ASSIGNMENT_KB)
                except TelegramBadRequest as e:
                    protocol = FSInputFile(f"data/probes/{message.from_user.username}/protocol.txt")
                    await message.answer_document(protocol)

            async with aiofiles.open(f"data/probes/{message.from_user.username}/comparison_page.html") as comparison:
                comp = await comparison.readlines()

                if len(comp) != 0:
                    compPage = FSInputFile(f"data/probes/{message.from_user.username}/comparison_page.html")
                    await message.answer_document(compPage)


    except aiodocker.exceptions.DockerContainerError as e:
        await last_message.edit_text(
            text=(
                "Error occurred when running container:\n"
                f"{e}\n"
            ),
            reply_markup=CHANGE_ASSIGNMENT_KB
        )
    except aiodocker.exceptions.DockerError as e:
        await last_message.edit_text(
            text=(
                "Error occurred when running container:\n"
                f"{e}\n"
            ),
            reply_markup=CHANGE_ASSIGNMENT_KB
        )

    shutil.rmtree(f"data/probes/{message.from_user.username}", ignore_errors=True)
    await dockerClient.close()



@dp.callback_query(F.data.startswith(STOP_CB_PREFIX))
async def onStopTesting(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    assignment = data.get("assignment")

    if not assignment:
        await query.message.edit_text(
            text="You need first to choose the assignment",
            reply_markup=CHOOSE_ASSIGNMENT_KB
        ); return

    if "container" not in data.keys():
        await query.message.edit_text(
            text=(
                "Testing process was not ran. Nothing to stop.\n"
            ),
            reply_markup=CHANGE_ASSIGNMENT_KB)

        return

    cont = data["container"]

    del data["container"]
    data["testing_killed"] = True
    await state.set_data(data)

    await cont.kill()

    await query.message.edit_text(
        text=(
            "Testing stopped\n"
            f"Assignment: {assignment}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )
