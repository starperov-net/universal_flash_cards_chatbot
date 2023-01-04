from typing import Any

from aiogram import Dispatcher


def register_handlers_channel(dp: Dispatcher) -> None:
    handlers: set[Any] = ()
    for handler in handlers:
        handler(dp)
