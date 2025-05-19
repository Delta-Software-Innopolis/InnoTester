from typing import overload
from InnoTester.Utils import AsyncFileManager


FILE_PATH = "resources/moderators.txt"


class ModersManager:
    def __init__(self):
        self._file = AsyncFileManager(FILE_PATH)
        
    @overload
    async def get(self) -> list[int]: ...
    @overload
    async def get(self, get_usernames: bool = True) -> list[tuple[int, str]]: ...

    async def get(self, get_usernames: bool = False):
        """
        Returns the list of moder-id
        or list of tuples [moder-id, moder-username]
        from moderators.txt
        """
        async with self._file.open('r') as file:
            moders = list(map(lambda x: x.strip("\n").split(' @'), await file.readlines()))
            moders = [(int(id), username) for id, username in moders]
            if not get_usernames: moders = [m[0] for m in moders]
            return moders

    async def set(self, moders: list[tuple[int, str]]):
        async with self._file.open('w') as file:
            await file.writelines(f"{id} @{username}\n" for id, username in moders)
        
    async def hasModerWithId(self, id: int) -> bool:
        moder_ids = await self.get()
        return id in moder_ids

    async def hasModerWithUsername(self, username: str) -> bool:
        moders = await self.get(get_usernames=True)
        return username in [username for id, username in moders]

    async def hasModer(self, identifier: int | str) -> bool:
        moders = await self.get(get_usernames=True)
        for m in moders:
            for id_or_username in m:
                if identifier == id_or_username:
                    return True
        return False
