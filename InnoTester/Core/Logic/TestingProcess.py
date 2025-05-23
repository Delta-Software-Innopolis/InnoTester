import aiodocker
import aiofiles
import os
import shutil
import InnoTester.Utils.Config as Config
from InnoTester.Utils.Config import REFERENCES_PATH, TESTGENS_PATH, PROBES_PATH, RESOURCES_PATH


class TestingProcess:

    def __init__(self, assignment: str, username: str):
        self._container = None
        self._client = aiodocker.Docker()
        self._assignment = assignment
        self._username = username
        self._workdirPath = os.path.join(PROBES_PATH, self._username)
        self._isTerminated = False
        self._isClientClosed = False

    def isWorkDirExists(self) -> bool:
        return os.path.exists(self._workdirPath)

    def createWorkDir(self):
        if self.isWorkDirExists():
            return

        os.mkdir(self._workdirPath)

    async def prepare(self, iterationsCount: str) -> int:
        testsCount = 100
        async with aiofiles.open(os.path.join(self._workdirPath, "iterations.txt"), "w") as iters:
            if iterationsCount is not None:
                try:
                    await iters.write(f"{int(iterationsCount)}")
                    testsCount = int(iterationsCount)
                except ValueError:
                    await iters.write("100")
            else:
                await iters.write("100")

        async with aiofiles.open(os.path.join(self._workdirPath, "protocol.txt"), "w") as proto:
            await proto.write("")

        async with aiofiles.open(os.path.join(self._workdirPath, "comparison_page.html"), "w") as proto:
            await proto.write("")

        return testsCount

    async def run(self, referenceExtension: str, probeExtension: str, testgenExtension: str, referenceID: str,
                  testgenID: str):
        pwd = os.getcwd()

        containerConfig = {
            "Image": Config.dockerImageNum,
            "HostConfig": {
                "AutoRemove": True,
                "Memory": 256 * 1024 * 1024,  # 256MB
                "Binds": [
                    f'{os.path.join(pwd, RESOURCES_PATH, "compile.yaml")}:/testEnv/compile.yaml',
                    f'{os.path.join(pwd, PROBES_PATH, self._username, f"probe.{probeExtension}")}:/testEnv/probe.{probeExtension}',
                    f'{os.path.join(pwd, REFERENCES_PATH, f"{referenceID}.{referenceExtension}")}:/testEnv/reference.{referenceExtension}',
                    f'{os.path.join(pwd, TESTGENS_PATH, f"{testgenID}.{testgenExtension}")}:/testEnv/testgen.{testgenExtension}',
                    f'{os.path.join(pwd, PROBES_PATH, self._username, "protocol.txt")}:/testEnv/protocol.txt',
                    f'{os.path.join(pwd, PROBES_PATH, self._username, "comparison_page.html")}:/testEnv/comparison_page.html',
                    f'{os.path.join(pwd, PROBES_PATH, self._username, "iterations.txt")}:/testEnv/iterations.txt'
                ],
            },
            "WorkingDir": "/testEnv",
        }

        self._container = await self._client.containers.run(config=containerConfig)

    async def getContainerLog(self) -> str:
        containerLog = []
        async for log in self._container.log(stderr=True, follow=True):
            containerLog.append(log)

        return "".join(containerLog)

    async def closeClient(self):
        self._isClientClosed = True
        await self._client.close()

    async def terminate(self):
        self._isTerminated = True
        await self._container.kill()

    async def getResult(self):
        return await self._container.wait()

    def isTerminated(self) -> bool:
        return self._isTerminated

    def removeWorkdir(self):
        shutil.rmtree(os.path.join(PROBES_PATH, self._username), ignore_errors=True)

    def __del__(self):
        if not self._isClientClosed:
            self._client.close()

