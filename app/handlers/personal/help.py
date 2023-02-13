from typing import Optional
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


async def cmd_help(message: types.Message, state: Optional[FSMContext] = None) -> None:
    if state:
        state_name = await state.get_state()
    else:
        state_name = "None"
    await message.answer(f"There will be help. Your state is {state_name}")


def register_handler_help(dp: Dispatcher) -> None:
    dp.message.register(cmd_help, Command(commands=["help"]))
