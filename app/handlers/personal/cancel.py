from typing import Optional
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


async def cmd_cancel(
    message: types.Message, state: Optional[FSMContext] = None
) -> None:
    if state:
        state_name = await state.get_state()
    else:
        state_name = "None"
    await message.answer(f"There will be cancel. Your state is {state_name}")


def register_handler_cancel(dp: Dispatcher) -> None:
    dp.message.register(cmd_cancel, Command(commands=["cancel"]))
