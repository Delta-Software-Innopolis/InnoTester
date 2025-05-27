import os
import shutil
import aiofiles
from aiogram import F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile

import aiodocker
import aiodocker.exceptions

from InnoTester.Core.Logic.Models import Assignment
from InnoTester.Core.InnoTesterBot import (
    instance, dp, Config,
    modersManager, assignmentsManager
)
from InnoTester.Utils.Keyboards import (
    CHOOSE_ASSIGNMENT_CB,
    SHARE_CANCEL_CB,
    CHOOSE_ASSIGNMENT_SHARE_CB,
    SHARE_REFERENCE_CB, SHARE_TESTGEN_CB,
    ASSIGNMENT_CB_PREFIX, STOP_CB_PREFIX,
)
from InnoTester.Utils.FSMWrapper import FSMWrapper
from InnoTester.Utils.Logging import logInfo, logError

from InnoTester.Core import UserAnswers as answers


class ShareStates(StatesGroup):
    CHOOSE_ASSIGNMENT = State()
    SEND_REFERENCE = State()
    SEND_TESTGEN = State()


@dp.message(CommandStart())
async def onCmdStart(message: Message, context: FSMWrapper):
    await context.set_state(None) # to revert the ShareStates
    await context.clean_last_message()
    msg = await answers.answerWelcome(message)
    await context.set("last_message", msg)
    logInfo(message, "Issued /start")


@dp.message(Command("share"))
async def onCmdShare(message: Message, context: FSMWrapper):
    await context.clean_last_message()
    assignment: Assignment = await context.get("assignment")
    if assignment:
        msg = await answers.answerShare(message, assignment)
        logInfo(message, f"Issued /share ({assignment})")
    else:
        msg = await answers.answerShareNoAssign(message)
        logInfo(message, "Issued /share (no assignment)")
    await context.set("last_message", msg)


@dp.callback_query(F.data == SHARE_TESTGEN_CB)
async def onShareTestGenButton(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)
    await context.set_state(ShareStates.SEND_TESTGEN)
    await answers.editSendTestGen(query.message)
    logInfo(query, "Clicked SHARE_TESTGEN")


@dp.callback_query(F.data == SHARE_REFERENCE_CB)
async def onShareReferenceButton(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)
    await context.set_state(ShareStates.SEND_REFERENCE)
    await answers.editSendReference(query.message)
    logInfo(query, "Clicked SHARE_REFERENCE")


@dp.message(StateFilter(ShareStates.SEND_REFERENCE), F.document)
async def onShareReferenceDocument(message: Message, context: FSMWrapper):
    await context.clean_last_message()
    assignment: Assignment = await context.get("assignment")

    if not assignment:
        logInfo(message, "Failed to send reference (no assignment)")
        await onCmdShare(message, context)
        return

    if not message.from_user.username:
        await answers.answerNeedUsername(message)
        logInfo(message, "Failed share reference (no username)")
        return

    msg = await answers.answerThanksForReference(message, assignment)
    logInfo(message, f"Succesfully sent reference ({assignment})")

    await context.set("last_message", msg)
    await context.set_state(None)

    moder_count = 0
    for moder_id in await modersManager.get(): # TODO: make adding reference by buttons
        await answers.sendAdminReference(message, moder_id, assignment)
        moder_count += 1
    logInfo(message, f"{moder_count} moders received sent reference")


@dp.message(StateFilter(ShareStates.SEND_TESTGEN), F.document)
async def onShareTestGenDocument(message: Message, context: FSMWrapper):
    await context.clean_last_message()
    assignment : Assignment = await context.get("assignment")

    if not assignment:
        logInfo(message, "Failed to send testgen (no assignment)")
        await onCmdShare(message, context)
        return

    if not message.from_user.username:
        await answers.answerNeedUsername(message)
        logInfo(message, "Failed share testgen (no username)")
        return

    msg = await answers.answerThanksForTestGen(message, assignment)
    logInfo(message, f"Succesfully sent testgen ({assignment})")

    await context.set("last_message", msg)
    await context.set_state(None)

    moder_count = 0
    for moder_id in await modersManager.get(): # TODO: make adding testgen by buttons
        await answers.sendAdminTestGen(message, moder_id, assignment)
        moder_count += 1
    logInfo(message, f"{moder_count} moders received sent testgen")


@dp.callback_query(F.data == SHARE_CANCEL_CB)
async def onCancelShare(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)
    await context.set_state(None)
    assignment: Assignment = await context.get("assignment")
    if assignment:
        await answers.editShare(query.message, assignment)
        logInfo(query, f"Canceled /share ({assignment})")
    else:
        await answers.editShareNoAssignment(query.message)
        logInfo(query, "Canceled /share (assignment NOT chosen)")


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_CB)
async def onOpenAssignmentsList(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)

    assignments = assignmentsManager.cached

    chosen = await context.get("assignment")
    await context.set("assignment", None)

    await answers.editAssignmentsList(query.message, assignments, chosen)
    logInfo(query, "Opened users' assignments list")


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_SHARE_CB)
async def onOpenAssignmentsListForShare(query: CallbackQuery, context: FSMWrapper):
    await context.set_state(ShareStates.CHOOSE_ASSIGNMENT)
    await onOpenAssignmentsList(query, context)


@dp.callback_query(
    StateFilter(ShareStates.CHOOSE_ASSIGNMENT),
    F.data.startswith(ASSIGNMENT_CB_PREFIX))
async def onChooseAssignmentForShare(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)

    id = query.data.split("_")[1]
    assignment = await assignmentsManager.getAssignment(id)
    await context.set("assignment", assignment)
    await context.set_state(None)

    await answers.editShare(query.message, assignment)
    logInfo(query, f"Chosen assignment for /share ({assignment})")


@dp.callback_query(F.data.startswith(ASSIGNMENT_CB_PREFIX))
async def onChooseAssignment(query: CallbackQuery, context: FSMWrapper):
    await context.set("last_message", query.message)

    id = query.data.split("_")[1]
    assignment = await assignmentsManager.getAssignment(id)

    if not assignment.is_configured():
        logInfo(query, f"Tried to choose NOTCONFIGURED assignment ({assignment})")
        await answers.queryAnswerAssignmentNotConfigured(query, assignment)
        return

    await context.set("assignment", assignment)
    await answers.editAssignmentChosen(query.message, assignment)

    logInfo(query, f"Chosen assignment ({assignment})")


@dp.message(F.document)
async def onDocument(message: Message, context: FSMWrapper):
    dockerClient = aiodocker.Docker()

    assignment: Assignment = await context.get("assignment")
    last_message: Message = await context.get("last_message")

    if not message.from_user.username:
        await answers.answerNeedUsername(message)
        await dockerClient.close()
        logInfo(message, "Failed to start testing (no username)")
        return

    if os.path.exists("data/probes/" + message.from_user.username):
        await answers.editTestingStarted(last_message, assignment, message.from_user)
        await dockerClient.close()
        logInfo(message, "Failed to start testing (already testing)")
        return

    await context.clean_last_message()

    if not assignment:
        last_message = await answers.answerChooseAssignmentFirst(message)
        await context.set("last_message", last_message)
        await dockerClient.close()
        logInfo(message, "Failed to start testing (no assignment)")
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

        await answers.answerSupportedExtensions(message, supportedExtensions)
        await dockerClient.close()
        logInfo(message, "Failed to start testing (inacceptable ext)")
        return

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

    last_message = await answers.answerTestingStarted(message, assignment)
    await context.set("last_message", last_message)
    logInfo(message, f"Started testing ({assignment}) ({probeExtension})")

    pwd = os.getcwd()
    referenceExtension = Config.getLanguage(assignment.reference_id, f"{pwd}/data/references")
    testgenExtension = Config.getLanguage(assignment.testgen_id, f"{pwd}/data/testgens")
    username = message.from_user.username

    containerConfig = {
        "Image": Config.dockerImageNum,
        "HostConfig": {
            "AutoRemove": True,
            "Memory": 256 * 1024 * 1024,  # 256MB
            "Binds": [
                f"{pwd}/resources/compile.yaml:/testEnv/compile.yaml",
                f"{pwd}/data/probes/{username}/probe.{probeExtension}:/testEnv/probe.{probeExtension}",
                f"{pwd}/data/references/{assignment.reference_id}.{referenceExtension}:/testEnv/reference.{referenceExtension}",
                f"{pwd}/data/testgens/{assignment.testgen_id}.{testgenExtension}:/testEnv/testgen.{testgenExtension}",
                f"{pwd}/data/probes/{username}/protocol.txt:/testEnv/protocol.txt",
                f"{pwd}/data/probes/{username}/comparison_page.html:/testEnv/comparison_page.html",
                f"{pwd}/data/probes/{username}/iterations.txt:/testEnv/iterations.txt",
            ],
        },
        "WorkingDir": "/testEnv",
    }

    try:
        container = await dockerClient.containers.run(config=containerConfig)
        await context.set("container", container)

        containerLog = []
        async for log in container.log(stderr=True, follow=True):
            containerLog.append(log)

        result = await container.wait()

        if await context.has_key("testing_killed"):
            print('killed')
            await answers.editTestingTerminated(last_message)
            shutil.rmtree(f"data/probes/{message.from_user.username}", ignore_errors=True)
            await context.del_key("testing_killed")
            await dockerClient.close()
            return

        if result['StatusCode'] != 0:
            await answers.editTestingError(last_message, containerLog)
            logInfo(message, f"Error while testing: {''.join(containerLog)}")
        else:
            async with aiofiles.open(f"data/probes/{message.from_user.username}/protocol.txt") as proto:
                ans = await proto.readlines()
                try:
                    await answers.editErrorHandler(last_message, ans, testCount)
                except TelegramBadRequest:
                    protocol = FSInputFile(f"data/probes/{message.from_user.username}/protocol.txt")
                    await message.answer_document(protocol)
                logInfo(message, f"Finished testing: {''.join(ans)}")

            async with aiofiles.open(f"data/probes/{message.from_user.username}/comparison_page.html") as comparison:
                comp = await comparison.readlines()

                if len(comp) != 0:
                    compPage = FSInputFile(f"data/probes/{message.from_user.username}/comparison_page.html")
                    await message.answer_document(compPage)

    except aiodocker.exceptions.DockerContainerError as e:
        await answers.editContainerError(last_message, e)
        logError(message, f"Error running container: {e}")
    except aiodocker.exceptions.DockerError as e:
        await answers.editContainerError(last_message, e)
        logError(message, f"Error running container: {e}")

    shutil.rmtree(f"data/probes/{message.from_user.username}", ignore_errors=True)
    await dockerClient.close()


@dp.callback_query(F.data.startswith(STOP_CB_PREFIX))
async def onStopTesting(query: CallbackQuery, context: FSMWrapper):
    assignment: Assignment = await context.get("assignment")

    if not assignment:
        await answers.editChooseAssignmentFirst(query.message)
        logInfo(query, "Failed to stop testing (no assignment)")
        return

    if not await context.has_key("container"):
        await answers.editNothingToStop(query.message)
        logInfo(query, "Failed to stop testing (nothing to stop)")
        return

    cont = await context.get("container")

    await context.del_key("container")
    await context.set("testing_killed", True)

    await cont.kill()

    await answers.editTestingStopped(query.message, assignment)
    logInfo(query, "Stopped testing forcefully")
