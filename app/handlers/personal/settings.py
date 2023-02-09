from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


async def cmd_settings(message: types.Message, state: FSMContext) -> None:
    await message.answer("There will be settings-block")


def register_handler_settings(dp: Dispatcher) -> None:
    dp.message.register(cmd_settings, Command(commands=["settings"]))
