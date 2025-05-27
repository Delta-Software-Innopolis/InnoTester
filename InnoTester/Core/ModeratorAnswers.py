from aiogram.types import Message, User
from aiogram.utils.formatting import Code

from InnoTester.Core.Logic.Models import Assignment


# region utils

def build_assignments_list(assignments: list) -> str:
    return "\n".join(
        a.to_list_with_id()
        for a in assignments
    )

# endregion


async def answerUsageRemoveReference(message: Message) -> Message:
    return await message.answer(
        "Usage:\n"
        "`/removereference <assignment_id>`\n"
        "Use /list to see all the assignments",
        parse_mode="MarkdownV2"
    )


async def answerUsageRemoveTestGen(message: Message) -> Message:
    return await message.answer(
        "Usage:\n"
        "`/removetestgen <assignment_id>`\n"
        "Use /list to see all the assignments",
        parse_mode="MarkdownV2"
    )


async def answerUsageUploadReference(message: Message) -> Message:
    return await message.answer(
        "Usage:\n"
        "`/uploadreference <assignment_id>`\n"
        "Document has to be attached to the message\!\n"
        "Use /list to see all the assignments",
        parse_mode="MarkdownV2"
    )


async def answerUsageUploadTestGen(message: Message) -> Message:
    return await message.answer(
        "Usage:\n"
        "`/uploadtestgen <assignment_id>`\n"
        "Document has to be attached to the message\!\n"
        "Use /list to see all the assignments",
        parse_mode="MarkdownV2"
    )


async def answerUsageAddModer(message: Message) -> Message:
    return await message.answer(
        "Usage: /addmoder <user_id>\n"
        "Provide a numeric user_id please, not a username\n\n"
        "You may see id of any user, by toggling:\n"
        "Telegam Settings > " 
        "Advanced > " 
        "Experimental Settings > " 
        "Show peer IDs in Profile"
    )


async def answerUsageRemoveModer(message: Message) -> Message:
    return await message.answer(
        "Usage: /removemoder <user_id or username>"
    )


async def answerAttachedFileRequired(message: Message) -> Message:
    return await message.answer(
        "You need to perform this command in "
        "the message with attached file"
    )


async def answerReferenceRemoved(message: Message, id: str) -> Message:
    return await message.answer(
        f"Reference \(`{id}`\) removed successfuly",
        parse_mode="MarkdownV2"
    )


async def answerReferenceUploaded(message: Message) -> Message:
    return await message.answer("Reference Successfully uploaded")


async def answerTestGenRemoved(message: Message, id: str) -> Message:
    return await message.answer(
        f"TestGen \(`{id}`\) removed successfuly",
        parse_mode="MarkdownV2"
    )


async def answerTestGenUploaded(message: Message) -> Message:
    return await message.answer("TestGen Successfully uploaded")


async def answerReferenceNotFound(message: Message) -> Message:
    return await message.answer("Reference not found :(")


async def answerTestGenNotFound(message: Message) -> Message:
    return await message.answer("TestGen not found :(")

async def answerAssignmentNotFound(message: Message) -> Message:
    return await message.answer("Corresponding assignment not found :(")


async def answerSomethingWentWrong(message: Message, e: Exception) -> Message:
    return await message.answer(
        "Something went wrong:\n"
        f"{str(e)}"
    )


async def answerNoPermission(message: Message) -> Message:
    return await message.answer("Sorry, but you don't have permission to perform this command")


async def answerUnknownUser(message: Message, id: int) -> Message:
    return await message.answer(
        f"I don't know anyone with id {id}\n"
        "Make sure the user had texted me before"
    )


async def answerAddedNewModer(message: Message, moder: User) -> Message:
    return await message.answer(f"Added new moderator: @{moder.username}")


async def answerNotStupid(message: Message) -> Message:
    return await message.answer("I am not so stupid lol")


async def answerNotInModerList(message: Message) -> Message:
    return await message.answer("This person is not in moderator list")


async def answerRemovedModerator(message: Message, removed: tuple[str, str]) -> Message:
    return await message.answer(
        f"Removed moderator {Code(removed[0]).as_html()} @{removed[1]}",
        parse_mode="HTML"
    )


async def answerModerList(message: Message, moderList: list[tuple[int, str]]) -> Message:
    msg = "Moderators:\n"
    for id, username in moderList:
        msg += f"- {Code(id).as_html()} @{username}\n"
    return await message.answer(msg, parse_mode="HTML")


async def answerModerHelp(message: Message) -> Message:
    return await message.answer(
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


async def answerUsageRemoveProbe(message: Message) -> Message:
    return await message.answer("Usage: /removeprobe <username>")


async def answerProbeRemoved(message: Message) -> Message:
    return await message.answer("Probe was removed successfully")


async def answerProbeNotExist(message: Message) -> Message:
    return await message.answer("Such probe does not exists")


async def answerProbeList(message: Message, probeList: list[str]) -> Message:
    msg = "Probes:\n"
    for probe in probeList:
        msg += probe + "\n"

    return await message.answer(msg)


async def answerAssignmentsList(
        message: Message,
        assignments: list[Assignment] 
    ) -> Message:
    assignments_list = build_assignments_list(assignments)

    return await message.answer(
        "Here are all the assignments:\n"
        f"{assignments_list}",
        parse_mode="MarkdownV2"
    )


async def answerNewAssignmentCreated(
        message: Message,
        new_assignment: Assignment
    ) -> Message:
    return await message.answer(
        f"New assignment created:\n"
        fr"🛠 \(`{new_assignment.id}`\) {new_assignment.name}"
        "\n\n"
        "Consider uploading reference and testgen for it",
        parse_mode="MarkdownV2"
    )


async def answerAssignmentAlreadyExists(
        message: Message,
        assignment_name: str
    ) -> Message:
    return await message.answer(
        f"Assignment named: \"{assignment_name}\" already exists\n"
        "Unusual, but consider renaming"
    )


async def answerUsageAddAssignment(message: Message) -> Message:
    return await message.answer(
        "Usage:\n"
        "`/addassignment <assignment name>`",
        parse_mode="MarkdownV2"
    )


async def answerAssignmentsListRefreshed(
        message: Message,
        old: list[Assignment],
        new: list[Assignment]
    ) -> Message:

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

    return await message.answer(
        "Assignments List Refreshed:\n"
        + (status_message or "Nothing New"),
        parse_mode="MarkdownV2"
    )
