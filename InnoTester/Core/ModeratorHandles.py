import os
import shutil
from io import BytesIO
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command

from InnoTester.Core.InnoTesterBot import (
    dp, instance, assignmentsManager, codeManager, modersManager
)
from InnoTester.Utils.Exceptions import (
    CodeRecordNotFound,
    AssignmentNotFound,
    AlreadyExists,
    NoNameProvided
)
from InnoTester.Utils.Logging import (
    logInfo, logError, logCritical,
    logMissuse, logNotPermitted
)
from InnoTester.Core import ModeratorAnswers as answers


@dp.message(Command("removereference", "removeref"))
async def cmdClearReference(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "removereference")
        return

    if len(message.text.split()) != 2:
        await answers.answerUsageRemoveReference(message)
        logMissuse(message, "removereference")
        return

    id = message.text.split()[1]

    try:
        reference = await codeManager.getReference(id)
        await codeManager.removeReference(reference)

        assignment = await assignmentsManager.getAssignment(id)
        assignment.has_reference = False
        assignment.reference_id = None
        assignment.status = assignment.Status.NOTCONFIGURED
        await assignmentsManager.setAssignment(assignment)

        await answers.answerReferenceRemoved(message, id)
        logInfo(message, f"Reference {id} removed {assignment}")

    except CodeRecordNotFound:
        await answers.answerReferenceNotFound(message)
        logInfo(message, "Reference not found (/removereference))")

    except AssignmentNotFound:
        await answers.answerAssignmentNotFound(message)
        logInfo(message, "Assignment not found (/removereference)")

    except Exception as e:
        await answers.answerSomethingWentWrong(message, e)
        logError(message,"While using /removereference\n\n"+str(e))


@dp.message(Command("removetestgen", "removetg"))
async def cmdClearTestGen(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "removetestgen")
        return

    if len(message.text.split()) != 2:
        await answers.answerUsageRemoveTestGen(message)
        logMissuse(message, "removeretestgen")
        return

    id = message.text.split()[1]

    try:
        testgen = await codeManager.getTestGen(id)
        await codeManager.removeTestGen(testgen)

        assignment = await assignmentsManager.getAssignment(id)
        assignment.has_testgen = False
        assignment.testgen_id = None
        assignment.status = assignment.Status.NOTCONFIGURED
        await assignmentsManager.setAssignment(assignment)

        await answers.answerTestGenRemoved(message, id)
        logInfo(message, f"TestGen {id} succesfully removed")

    except CodeRecordNotFound:
        await answers.answerTestGenNotFound(message)
        logInfo(message, f"TestGen {id} not found (/removetestgen)")

    except AssignmentNotFound:
        await answers.answerAssignmentNotFound(message)
        logInfo(message, "Assignment not found (/removetestgen)")

    except Exception as e:
        await answers.answerSomethingWentWrong(message, e)
        logError(message,"while using /removetestgen\n\n" + str(e))


@dp.message(Command("uploadreference", "ureference", "uref", "aref"))
async def uploadReference(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "uploadreference")
        return

    if (caption := message.caption) is None or len(caption.split()) != 2:
        await answers.answerUsageUploadReference(message)
        logMissuse(message, "uploadreference")
        return

    if message.document is None:
        await answers.answerAttachedFileRequired(message)
        logInfo(message, "File not attached for /uploadreference")
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

        await answers.answerReferenceUploaded(message)
        logInfo(message, "File succesfully uploaded (/uploadreference)")

    except AssignmentNotFound:
        await answers.answerAssignmentNotFound(message)
        logInfo(message, f"Assignment not found {id} (/uploadreference)")


@dp.message(Command("uploadtestgen", "utestgen", "utg", "atg"))
async def uploadTestGen(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "uploadtestgen")
        return

    if (caption := message.caption) is None or len(caption.split()) != 2:
        await answers.answerUsageUploadTestGen(message)
        logMissuse(message, "uploadtestgen")
        return

    if message.document is None:
        await answers.answerAttachedFileRequired(message)
        logInfo(message, "File not attached for /uploadtestgen")
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

        await answers.answerTestGenUploaded(message)
        logInfo(message, "File succesfully uploaded (/uploadtestgen)")

    except AssignmentNotFound:
        await answers.answerAssignmentNotFound(message)
        logInfo(message, f"Assignment not found {id} (/uploadtestgen)")


@dp.message(Command("addmoder", "amoder"))
async def addModer(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "addmoder")
        return

    args = message.text.split()

    if len(args) == 1:
        await answers.answerUsageAddModer(message)
        logMissuse(message, "addmoder")
    else:
        moder_id = args[1]
        if not moder_id.isnumeric():
            await answers.answerUsageAddModer(message)
            logInfo(message, "Missused /addmoder (username instead of user-id)")
            return

        try:
            moder = await instance.get_chat(moder_id)
        except TelegramBadRequest:
            await answers.answerUnknownUser(message, moder_id)
            logInfo(message, f"User not found {moder_id} (/addmoder)")
            return

        moders = await modersManager.get(get_usernames=True)
        moders.append((moder.id, moder.username))
        await modersManager.set(moders)

        await answers.answerAddedNewModer(message, moder)
        logInfo(message, f"New moder added {moder_id}")


@dp.message(Command("removemoder"))
async def removeModer(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "removemoder")
        return

    args = message.text.split()

    if len(args) == 1:
        await answers.answerUsageRemoveModer(message)
        logMissuse(message, "removemoder")
    else:
        identifier = args[1]
        if identifier.isnumeric():
            identifier = int(identifier)

        moders = await modersManager.get(get_usernames=True)

        if identifier in moders[0]:
            await answers.answerNotStupid(message)
            logInfo(message, "Tried to remove the head moderator")
            return

        if identifier not in [id_or_name for m in moders for id_or_name in m]:
            await answers.answerNotInModerList(message)
            logInfo(message, f"Tried to remove person that is not moderator: {identifier}")
            return

        removed = ("id-here", "username-here")

        for i in range(len(moders)):
            if identifier in moders[i]:
                removed = moders[i]
                del moders[i]
                break
        await modersManager.set(moders)

        await answers.answerRemovedModerator(message, removed)
        logInfo(message, f"Removed moderator: {removed[0]} @{removed[1]}")


@dp.message(Command("moderlist", "mlist"))
async def moderList(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "moderlist")
        return

    await answers.answerModerList(
        message,
        await modersManager.get(get_usernames=True)
    )

    logInfo(message, "Showed moder list")


@dp.message(Command("moderhelp", "mhelp"))
async def moderHelp(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "moderhelp")
        return

    await answers.answerModerHelp(message)
    logInfo(message, "Showed moder commands")


@dp.message(Command("removeprobe", "rprobe"))
async def removeProbe(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "removeprobe")
        return
        
    args = message.text.split()

    if len(args) == 1:
        await answers.answerUsageRemoveProbe(message)
        logMissuse(message, "removeprobe")
    else:
        if os.path.exists(f"data/probes/{args[1]}"):
            shutil.rmtree(f"data/probes/{args[1]}")
            await answers.answerProbeRemoved(message)
            logInfo(message, f"Removed probe of @{args[1]}")
        else:
            await answers.answerProbeNotExist(message)
            logInfo(message, "Probe to remove not found")


@dp.message(Command("probelist", "probes"))
async def probeList(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "probelist")
        return

    await answers.answerProbeList(message, os.listdir("data/probes"))
    logInfo(message, "Showed probe list")


@dp.message(Command("assignments", "list"))
async def listAssignments(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "assignments")
        return

    await answers.answerAssignmentsList(message, assignmentsManager.cached)
    logInfo(message, "Showed assignments list (moder)")
    

@dp.message(Command("addassignment", "adda"))
async def addAssignment(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "addassignment")
        return 

    try:
        assignment_name = ' '.join(message.text.split()[1:])
        new_assignment = await assignmentsManager.addAssignment(assignment_name)
        await answers.answerNewAssignmentCreated(message, new_assignment)
        logInfo(message, f"Added assignment {new_assignment}")

    except AlreadyExists:
        await answers.answerAssignmentAlreadyExists(message, assignment_name)
        logInfo(message, f"Assignment {new_assignment.name} already exists")

    except NoNameProvided:
        await answers.answerUsageAddAssignment(message)
        logMissuse(message, "addassignment")


@dp.message(Command("refresh"))
async def refreshAssignments(message: types.Message):
    if not await modersManager.hasModerWithId(message.from_user.id):
        await answers.answerNoPermission(message)
        logNotPermitted(message, "refresh")
        return

    old = assignmentsManager.cached.copy()
    await assignmentsManager.updateAssignments()
    new = assignmentsManager.cached

    await answers.answerAssignmentsListRefreshed(message, old, new)
    logInfo(message, "Assignments Refreshed")


@dp.message(Command("critical", "boom"))
async def onCritical(message: types.Message):
    if await modersManager.hasModerWithId(message.from_user.id):
        logCritical(message, "Testing critical logging, BOOM")
    else:
        # skipping silently, no message returned
        logNotPermitted(message, "critical")
