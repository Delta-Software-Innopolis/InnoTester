from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.exceptions import *
from aiogram.types import FSInputFile
import asyncio
import aiofiles
import os
import shutil


from ITPHelper.Core.ITPHelperBot import *
import ITPHelper.Utils.Config as Config


@dp.message(Command("refstat"))
async def refStat(message: types.Message):
    await logger.info(f"{message.from_user.username} performed /refstat command")
    await message.answer(f"Reference for assignment #{await Config.getAssignNum()} was loaded by @{await Config.getWhoLoaded()}" if Config.checkReady() else "Bot is not configured at the current moment")


@dp.message(Command("start"))
async def cmdStart(message: types.Message):
    await logger.info(f"{message.from_user.username} performed /start command")
    await message.answer(Config.messages["start"], parse_mode=ParseMode.HTML)


@dp.message()
async def anyMessage(message: types.Message):
    if message.from_user.id in Config.banlist:
        await logger.info(f"{message.from_user.username} from banlist tried to test solution")
        return

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
