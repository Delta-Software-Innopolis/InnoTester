from typing import Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.context import FSMContext

from InnoTester.Utils.FSMWrapper import FSMWrapper


class CustomMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        # Before handler
        await add_context(data)

        result = await handler(event, data)

        # After handler

        return result

async def add_context(data: dict[str, Any]):
    state: FSMContext = data.get("state")
    data["context"] = FSMWrapper(state)
