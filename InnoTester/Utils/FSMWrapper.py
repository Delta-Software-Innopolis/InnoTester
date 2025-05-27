from typing import Any
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


class FSMWrapper():
    def __init__(self, state: FSMContext):
        self.state = state

    async def set_state(self, state: State):
        await self.state.set_state(state)

    async def get_state(self) -> State:
        return await self.state.get_state()

    async def set(self, key: str, data: Any):
        _data = await self.state.get_data()
        _data[key] = data
        await self.state.set_data(_data)

    async def get(self, key: str, default: Any = None) -> Any | None:
        _data = await self.state.get_data()
        return _data.get(key)

    async def has_key(self, key: str) -> bool:
        return key in await self.state.get_data()

    async def del_key(self, key: str):
        _data = await self.state.get_data()
        del _data[key]
        await self.state.set_data(_data)


    async def clean_last_message(self):
        last_message: Message = await self.get("last_message")
        if last_message:
            await last_message.delete()