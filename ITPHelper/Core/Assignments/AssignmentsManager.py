import os
import aiofiles
import json
import asyncio

from ITPHelper.Core.Assignments.Models import *


ASSIGNMENTS_FILE = "assignments.json"


class AssignmentsManager:
    def __init__(self):
        self.cached = self.__readAssignmentsSync()
        self.__ioLock = asyncio.Lock()

    
    async def updateAssignments(self, assignments: list[Assignment]):
        self.cached = assignments
        await self.__writeAssignments(assignments)


    def __readAssignmentsSync(self) -> list[Assignment]:
        data = None
        if not os.path.exists(ASSIGNMENTS_FILE):
            with open(ASSIGNMENTS_FILE, 'w', encoding="utf-8") as file:
                file.write("[]")

        with open(ASSIGNMENTS_FILE, 'r', encoding="utf-8") as file:
            data = json.load(file)

        if data:
            return [Assignment.from_dict(d) for d in data]
        else:
            return []


    async def __readAssignments(self) -> list[Assignment]:
        data = None
        async with self.__ioLock():
            async with aiofiles.open(
                ASSIGNMENTS_FILE, 'r', encoding="utf-8"
            ) as file:
                data = json.load(file)
        if data:
            return [Assignment.from_dict(d) for d in data]
        else:
            return []


    async def __writeAssignments(self, assignments: list[Assignment]):
        data = [a.to_dict() for a in assignments]
        async with self.__ioLock():
            async with aiofiles.open(
                ASSIGNMENTS_FILE, 'w', encoding="utf-8"
            ) as file:
                json.dump(
                    data,file,
                    ensure_ascii=False,
                    indent=2
                )
