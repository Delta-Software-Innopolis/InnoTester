import asyncio
import aiofiles

from contextlib import asynccontextmanager
from typing import Literal, AsyncGenerator
from aiofiles.threadpool.text import AsyncTextIOWrapper


class AsyncFileManager:
    """
    The class provides wrapper on `aiofiles.open(...)` \\
    Allowing safer IO operations using `asyncio.Lock`
    """
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def open(self, mode: str) -> AsyncGenerator[AsyncTextIOWrapper, None]:
        async with self._lock:
            async with aiofiles.open(self.file_path, mode, encoding="utf-8") as file:
                yield file
