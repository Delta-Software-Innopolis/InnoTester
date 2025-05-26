from aiogram import F
from aiogram.types import (
    Message, CallbackQuery, Document
)

from InnoTester.Utils.Keyboards import (
    CHOOSE_ASSIGNMENT_KB, CHOOSE_ASSIGNMENT_CB,
    CHANGE_ASSIGNMENT_KB,
    SHARE_KB, SHARE_CANCEL_KB, SHARE_CANCEL_CB,
    CHOOSE_ASSIGNMENT_SHARE_KB, CHOOSE_ASSIGNMENT_SHARE_CB,
    SHARE_REFERENCE_CB, SHARE_TESTGEN_CB,
    ASSIGNMENT_CB_PREFIX, STOP_CB_PREFIX,
    stopTestKeyboard, assigListKeyboard,
)
from InnoTester.Core.InnoTesterBot import instance
from InnoTester.Core.Logic.Models import Assignment


async def answerWelcome(message: Message) -> Message:
    return await message.answer(
        "Welcome to InnoTester, blah blah",
        reply_markup=CHOOSE_ASSIGNMENT_KB
    )


async def answerShare(message: Message, assign: Assignment) -> Message:
    return await message.answer(
        text=(
            "Wanna share?\n"
            f"Chosen: {assign}\n\n"
            "What are you sharing, fellow coder?"
        ),
        reply_markup=SHARE_KB
    )


async def answerShareNoAssign(message: Message) -> Message:
    return await message.answer(
        text=(
            "Wanna share?\n"
            "Choose the Assignment first"
        ),
        reply_markup=CHOOSE_ASSIGNMENT_SHARE_KB
    )


async def editSendTestGen(message: Message) -> Message:
    return await message.edit_text(
        "Now please, send the TestGen code as a file",
        reply_markup=SHARE_CANCEL_KB
    )


async def editSendReference(message: Message) -> Message:
    return await message.edit_text(
        "Now please, send the send the Reference code as a file",
        reply_markup=SHARE_CANCEL_KB
    )


async def answerNeedUsername(message: Message) -> Message:
    return await message.answer(
        "To use the bot you need to have a @username\n"
        "Set one in the Telegram settings to proceed"
    )


async def answerThanksForReference(message: Message, assign: Assignment) -> Message:
    return await message.answer(
        "Thanks, hero!\n"
        f"Reference sent for {assign}\n\n"
        "We'll review your code and send "
        "you the acceptance verdict afterwards\n\n"
        "Stay tuned :)"
    )


async def answerThanksForTestGen(message: Message, assign: Assignment) -> Message:
    return await message.answer(
        "Thanks, hero!\n"
        f"TestGen sent for {assign}\n\n"
        "We'll review your code and send "
        "you the acceptance verdict afterwards\n\n"
        "Stay tuned :)"
    )


async def sendAdminWhat(
        what: str, message: Message,
        moder_id: int, assign: Assignment
    ) -> Message:
    return await instance.send_document(
        moder_id,
        caption=(
            f"One hero want to share his {what}\!\n"
            f"{assign.to_list_with_id()}\n"
            f"@{message.from_user.username}\n"
        ),
        document=message.document.file_id,
        parse_mode="MarkdownV2"
    )


async def sendAdminReference(
        message: Message, moder_id: int,
        assign: Assignment
    ) -> Message:
    return await sendAdminWhat(
        "Reference", message, moder_id, assign
    )


async def sendAdminTestGen(
        message: Message, moder_id: int,
        assign: Assignment
    ) -> Message:
    return await sendAdminWhat(
        "TestGen", message, moder_id, assign
    )


async def editShare(message: Message, assign: Assignment) -> Message:
    return await message.edit_text(
        text=(
            "Wanna share?\n"
            f"Chosen: {assign}\n\n"
            "What are you sharing, fellow coder?"
        ),
        reply_markup=SHARE_KB
    )


async def editShareNoAssignment(message: Message) -> Message:
    return await message.edit_text(
        text=(
            "Wanna share?\n"
            "Choose the Assignment first"
        ),
        reply_markup=CHOOSE_ASSIGNMENT_SHARE_KB
    )


async def editAssignmentsList(
        message: Message,
        assignments: list[Assignment],
        chosen: Assignment
    ) -> Message:
    return await message.edit_text(
        text="Here are all the assignments:",
        reply_markup=assigListKeyboard(assignments, chosen)
    )
