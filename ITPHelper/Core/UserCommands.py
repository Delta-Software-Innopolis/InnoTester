from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.exceptions import *
from aiogram.types import FSInputFile
import asyncio
import aiofiles
import os
import shutil


from ITPHelper.Core.ITPHelperBot import *
from ITPHelper.Utils.Exceptions import *
import ITPHelper.Utils.Config as Config


# utils

def build_assignments_list(assignments: list) -> str:
    return "\n".join(
        str(assignment)
            .replace("(", r"\(`") # for markdown coolness
            .replace(")", r"`\)")
        for assignment in assignments
    )


@dp.message(Command("refstat"))
async def refStat(message: types.Message):
    await logger.info(f"{message.from_user.username} performed /refstat command")
    await message.answer(f"Reference for assignment #{await Config.getAssignNum()} was loaded by @{await Config.getWhoLoaded()}" if Config.checkReady() else "Bot is not configured at the current moment")


@dp.message(Command("start"))
async def cmdStart(message: types.Message):
    await logger.info(f"{message.from_user.username} performed /start command")
    await message.answer(Config.messages["start"], parse_mode=ParseMode.HTML)


@dp.message(Command("assignment", 'a'), F.text)
async def chooseAssignment(message: types.Message, state: FSMContext):
    if len(message.text.split()) != 2:
        await message.answer(
            "Usage: `/assignment <id>`\n"
            "To see all running assignments, use /list",
            parse_mode="MarkdownV2"
        ); return
    id = message.text.split()[1]
    try:
        assignment = await assignmentsManager.getAssignment(id)

        if not assignment.is_configured():
            raise NotConfigured()

        await state.set_data({"assignment": assignment})
        await message.answer(
            "Assignment chosen:\n"
            +str(assignment)
                .replace("(", r"\(`") # for markdown coolness
                .replace(")", r"`\)")
            +"\nNow you can send the code",
            parse_mode="MarkdownV2"
        )
    except AssignmentNotFound:
        await message.answer(
            f"Assignment with id `{id}` not found\n"
            "To see all running assignments, use /list",
            parse_mode="MarkdownV2"
        )

    except NotConfigured:
        await message.answer(
            f"This assignment is not configured yet :(\n"
            "If YOU have the solution to the problem or a working test generator, "
            "share with us, be a hero)"
        )


@dp.message(Command("assignments", "list"))
async def listAssignments(message: types.Message):
    
    assignments_list = build_assignments_list(assignmentsManager.cached)

    await message.answer(
        "Here are all the assignments:\n"
        f"{assignments_list}",
        parse_mode="MarkdownV2"
    )


@dp.message(Command("help"))
async def cmdHelp(message: types.Message):
    await message.answer(
        "Available commands:\n"
        "`/assignment <id>` \- choose assignment to test on\n"
        "/list \- show all active assignments",
        parse_mode="MarkdownV2"
    )


@dp.message()
async def anyMessage(message: types.Message, state: FSMContext):
    if message.from_user.id in Config.banlist:
        await logger.info(f"{message.from_user.username} from banlist tried to test solution")
        return

    assignment = (await state.get_data()).get("assignment")
    if not assignment:
        await message.answer(
            "First, choose the assignment using:\n"
            "/assignment (shorthand /a) command"
        ); return

    if message.document is not None:
        if not Config.checkReady():
            await message.answer(Config.messages["notConfigured"])
            return

        path = (await instance.get_file(message.document.file_id)).file_path
        extension = str(path).split(".")[-1]

        if extension not in Config.compileCommands.keys():
            supportedExtensions = ""

            for i, ext in enumerate(Config.compileCommands.keys()):
                if i == len(Config.compileCommands.keys()) - 1:
                    supportedExtensions += f"and .{ext}"
                else:
                    supportedExtensions += f".{ext}, "

            await message.answer(f"Only {supportedExtensions} files are accepted")
            return

        if not os.path.exists("probes/" + message.from_user.username):
            await logger.info(f"{message.from_user.username} started testing solution ({extension})")
            await message.answer("Starting testing")
            os.mkdir("probes/" + message.from_user.username)
            await instance.download_file(path, f"probes/{message.from_user.username}/probe.{extension}")

            testCount = 100

            async with aiofiles.open(f"probes/{message.from_user.username}/iterations.txt", "w") as iters:
                if message.caption is not None:
                    try:
                        await iters.write(f"{int(message.caption)}")
                        testCount = int(message.caption)
                    except ValueError:
                        await iters.write("100")
                else:
                    await iters.write("100")

            async with aiofiles.open(f"probes/{message.from_user.username}/protocol.txt", "w") as proto:
                await proto.write("");

            async with aiofiles.open(f"probes/{message.from_user.username}/comparison_page.html", "w") as proto:
                await proto.write("");

            proc = await asyncio.create_subprocess_shell(
                f"docker container run --rm -m 256m -v $(pwd)/compile.yaml:/testEnv/compile.yaml -v $(pwd)/probes/{message.from_user.username}/probe.{extension}:/testEnv/probe.{extension} -v $(pwd)/reference.{Config.getLanguage('reference')}:/testEnv/reference.{Config.getLanguage('reference')} -v $(pwd)/testgen.{Config.getLanguage('testgen')}:/testEnv/testgen.{Config.getLanguage('testgen')} -v $(pwd)/probes/{message.from_user.username}/protocol.txt:/testEnv/protocol.txt -v $(pwd)/probes/{message.from_user.username}/comparison_page.html:/testEnv/comparison_page.html -v $(pwd)/probes/{message.from_user.username}/iterations.txt:/testEnv/iterations.txt -w /testEnv {Config.dockerImageNum}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await proc.communicate()

            if stderr:
                msg = stderr.decode()
                await logger.info(f"Docker error occured while checking {message.from_user.username}'s solution: {msg}")
                await message.answer(f"Docker error occurred: {msg}")
                shutil.rmtree(f"probes/{message.from_user.username}", ignore_errors=True)
                return

            async with aiofiles.open(f"probes/{message.from_user.username}/protocol.txt") as proto:
                ans = await proto.readlines()
                await logger.info(f"Finished testing {message.from_user.username}'s solution: {''.join(ans)}")
                try:
                    await message.answer(**Config.errorHanler(ans, testCount).as_kwargs())
                except TelegramBadRequest as e:
                    protocol = FSInputFile(f"probes/{message.from_user.username}/protocol.txt")
                    await message.answer_document(protocol)

            async with aiofiles.open(f"probes/{message.from_user.username}/comparison_page.html") as comparison:
                comp = await comparison.readlines()

                if len(comp) != 0:
                    compPage = FSInputFile(f"probes/{message.from_user.username}/comparison_page.html")
                    await message.answer_document(compPage)


            shutil.rmtree(f"probes/{message.from_user.username}", ignore_errors=True)

        else:
            await logger.info(f"{message.from_user.username} tries to send solution when another in testing process")
            await message.answer("Please, wait for the previous file to finish testing")
