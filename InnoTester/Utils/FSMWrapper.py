from typing import Any
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


class FSMWrapper():
    def __init__(self, state: FSMContext):
        self.state = state
        self._data = None

    async def set_state(self, state: State):
        await self.state.set_state(state)

    async def get_state(self) -> State:
        return await self.state.get_state()

    async def set(self, key: str, data: Any):
        if not self._data:
            self._data = await self.state.get_data()
        self._data[key] = data
        await self.state.set_data(self._data)


    async def get(self, key: str, default: Any = None) -> Any | None:
        if not self._data:
            self._data = await self.state.get_data()
        return self._data.get(key)


    async def clean_last_message(self):
        last_message: Message = await self.get("last_message")
        if last_message:
            await last_message.delete()