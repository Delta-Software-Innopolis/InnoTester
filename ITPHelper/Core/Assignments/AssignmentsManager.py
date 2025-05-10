import os
import aiofiles
import json
import asyncio

from ITPHelper.Core.Assignments.Models import *
from ITPHelper.Core.Assignments.Exceptions import *
from ITPHelper.Core.Assignments import RIDGenerator


if not os.path.exists("data"): os.mkdir("data")


ASSIGNMENTS_FILE = "data/assignments.json"


class AssignmentsManager:
    def __init__(self):
        self.cached = self.__readAssignmentsSync()
        self.__ioLock = asyncio.Lock()

    
    async def addAssignment(self, name: str) -> Assignment:
        if not name: raise NoNameProvided()
        if any(a.name == name for a in self.cached):
            raise AlreadyExists(name)
        new_assignment=Assignment(
            id=RIDGenerator.generate(),
            name=name,
            status=Assignment.Status.NOTCONFIGURED
        )
        self.cached.append(new_assignment)
        await self.__writeAssignments(self.cached)
        return new_assignment

    
    async def setAssignment(self, assignment: Assignment):
        for i in range(len(self.cached)):
            if self.cached[i].id == assignment.id:
                self.cached[i] = assignment
                await self.__writeAssignments(self.cached)
                return
        raise AssignmentNotFound(assignment.id)

    
    async def getAssignment(self, id: str) -> Assignment:
        for a in self.cached:
            if a.id == id:
                return a
        raise AssignmentNotFound()

    
    async def updateAssignments(self):
        self.cached = await self.__readAssignments()


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
        async with self.__ioLock:
            async with aiofiles.open(
                ASSIGNMENTS_FILE, 'r', encoding="utf-8"
            ) as file:
                data = json.loads(await file.read())
        if data:
            return [Assignment.from_dict(d) for d in data]
        else:
            return []


    async def __writeAssignments(self, assignments: list[Assignment]):
        data = [a.to_dict() for a in assignments]
        async with self.__ioLock:
            async with aiofiles.open(
                ASSIGNMENTS_FILE, 'w', encoding="utf-8"
            ) as file:
                await file.write(json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                ))
