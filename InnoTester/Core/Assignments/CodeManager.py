import os
import aiofiles
import json
import asyncio
from typing import Literal

from InnoTester.Core.Assignments.Models import *
from InnoTester.Core.Assignments.Exceptions import *


REFERENCES_PATH = "data/references"
TESTGENS_PATH = "data/testgens"

PATHS = {
    "references": REFERENCES_PATH,
    "testgens": TESTGENS_PATH
}


class CodeManager:
    __ioLocks = {
        "references": asyncio.Lock(),
        "testgens": asyncio.Lock(),
        "code": asyncio.Lock()
    }


    def __init__(self):
        self.references: list[Reference] = self.__readJSONSync("references")
        self.testgens: list[TestGen] = self.__readJSONSync("testgens")

    
    async def getReference(self, id: str) -> Reference:
        for r in self.references:
            if r.id == id:
                return r
        raise CodeRecordNotFound(id)

    
    async def getTestGen(self, id: str) -> TestGen:
        for tg in self.testgens:
            if tg.id == id:
                return tg
        raise CodeRecordNotFound(id)

    
    async def addReference(self, assignment_id: str, author: str, ext: str, code: str) -> Reference:
        new_reference = Reference(assignment_id, assignment_id, ext, author)
        self.references.append(new_reference)
        await self.__writeJSON("references", self.references)
        await self.__writeCode("references", new_reference, code)
        return new_reference


    async def addTestGen(self, assignment_id: str, author: str, ext: str, code: str) -> Reference:
        new_testgen = TestGen(assignment_id, assignment_id, ext, author)
        self.testgens.append(new_testgen)
        await self.__writeJSON("testgens", self.testgens)
        await self.__writeCode("testgens", new_testgen, code)
        return new_testgen

    
    async def removeReference(self, reference: Reference):
        os.remove(f"data/references/{reference.id}.{reference.ext}")
        for i, ref in enumerate(self.references):
            if (ref.id, ref.assignment_id) == (reference.id, reference.assignment_id):
                del self.references[i]
        await self.__writeJSON("references", self.references)


    async def removeTestGen(self, testgen: TestGen):
        os.remove(f"data/testgens/{testgen.id}.{testgen.ext}")
        for i, tg in enumerate(self.testgens):
            if (tg.id, tg.assignment_id) == (testgen.id, testgen.assignment_id):
                del self.testgens[i]
        await self.__writeJSON("testgens", self.testgens)


    async def updateAll(self):
        self.references = await self.__readJSON("references")
        self.testgens = await self.__readJSON("testgens")


    def __readJSONSync(self, which: Literal["references", "testgens"]) -> list[CodeRecord]:
        data = []; path = f"data/{which}.json"

        if not os.path.exists(path):
            with open(path, 'w') as file: file.write("[]")

        with open(path, 'r') as file:
            data = json.load(file)

        if data:
            return [CodeRecord.from_dict(d) for d in data]
        else:
            return []

    
    async def __readJSON(self, which: Literal["references", "testgens"]) -> list[CodeRecord]:
        data = []; path = f"data/{which}.json"

        async with self.__ioLocks[which]:
            async with aiofiles.open(path, 'r') as file:
                data = json.loads(await file.read())
        
        if data:
            return [CodeRecord.from_dict(d) for d in data]
        else:
            return []


    async def __writeJSON(self, which: Literal["references", "testgens"], what: list[CodeRecord]):
        data = [r.to_dict() for r in what]
        path = f"data/{which}.json"

        async with self.__ioLocks[which]:
            async with aiofiles.open(path, 'w') as file:
                await file.write(json.dumps(data, indent=2))

            
    async def __writeCode(self, which: Literal["references", "testgens"], codeRecord: CodeRecord, code: str):
        path = os.path.join(PATHS[which], f"{codeRecord.id}.{codeRecord.ext}")
        async with self.__ioLocks["code"]:
            async with aiofiles.open(path, 'w', encoding="utf-8") as file:
                await file.write(code)


    async def __readCode(self, which: Literal["references", "testgens"], codeRecord: CodeRecord) -> str:
        path = os.path.join(PATHS[which], f"{codeRecord.id}.{codeRecord.ext}")
        async with self.__ioLocks["code"]:
            async with aiofiles.open(path, 'r', encoding="utf-8") as file:
                return await file.read()
