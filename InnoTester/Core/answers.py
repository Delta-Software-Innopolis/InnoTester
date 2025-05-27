from aiogram import F
from aiogram.types import (
    Message, CallbackQuery, User
)

from InnoTester.Utils import Config
from InnoTester.Core.InnoTesterBot import instance
from InnoTester.Core.Logic.Models import Assignment
from InnoTester.Utils.Keyboards import (
    CHOOSE_ASSIGNMENT_KB,
    CHANGE_ASSIGNMENT_KB,
    SHARE_KB, SHARE_CANCEL_KB,
    CHOOSE_ASSIGNMENT_SHARE_KB,
    stopTestKeyboard, assigListKeyboard,
)


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


async def queryAnswerAssignmentNotConfigured(
        query: CallbackQuery, assignment: Assignment
    ):
    reference_emoji = '✅' if assignment.has_reference else '❌'
    testgen_emoji = '✅' if assignment.has_testgen else '❌'
    return await query.answer(
        "This assignment is not yet configured 🥺\n\n"
        "Current status:\n"
        f" {reference_emoji} Reference Solution\n"
        f" {testgen_emoji} Test Generator\n\n"
        "If YOU want to share your solution or "
        "test generator - type /share, be a hero 😎",
        show_alert=True
    )


async def editAssignmentChosen(message: Message, assign: Assignment) -> Message:
    return await message.edit_text(
        text=(
            "Chosen Assignment:\n"
            f"{str(assign)}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editTestingStarted(
        message: Message,
        assignment: Assignment,
        user: User
    ) -> Message:
    return await message.edit_text(
        text=(
            "Testing started\n"
            f"Assignment: {assignment}\n"
            "⚠️ Please, wait until the previous code finishes testing process"
        ),
        reply_markup=stopTestKeyboard(user.username)
    )


async def answerChooseAssignmentFirst(message: Message) -> Message:
    return await message.answer(
        text="You need first to choose the assignment",
        reply_markup=CHOOSE_ASSIGNMENT_KB
    )


async def editChooseAssignmentFirst(message: Message):
    return await message.edit_text(
        text="You need first to choose the assignment",
        reply_markup=CHOOSE_ASSIGNMENT_KB
    )


async def answerSupportedExtensions(
        message: Message, extensions: str
    ) -> Message:
    return await message.answer(f"Only {extensions} files are accepted")


async def answerTestingStarted(
        message: Message, assign: Assignment
    ) -> Message:
    return await message.answer(
        text=(
            "Testing started\n"
            f"Assignment: {assign}"
        ),
        reply_markup=stopTestKeyboard(message.from_user.username)
    )


async def editTestingTerminated(message: Message) -> Message:
    return await message.edit_text(
        text=(
            "Testing process terminated"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editTestingError(message: Message, containerLog: list) -> Message:
    return await message.edit_text(
        text=(
            "Error occurred while testing your solution:\n"
            f"{"".join(containerLog)}\n"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editContainerError(message: Message, e: Exception) -> Message:
    return await message.edit_text(
        text=(
            "Error occurred when running container:\n"
            f"{e}\n"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editNothingToStop(message: Message):
    return await message.edit_text(
        text="Testing process was not ran. Nothing to stop.",
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editTestingStopped(message: Message, assign: Assignment):
    return await message.edit_text(
        text=(
            "Testing stopped\n"
            f"Assignment: {assign}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


async def editErrorHandler(message: Message, ans: list[str], testCount: int):
    return await message.edit_text(
        **Config.errorHandler(ans, testCount).as_kwargs(),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )
