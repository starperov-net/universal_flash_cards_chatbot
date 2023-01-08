from typing import Callable

from aiogram import Dispatcher

# тут додавати импорт нових регістраторов
from app.handlers.personal.start import register_handler_start


def register_handlers_personal(dp: Dispatcher) -> None:
    # тут теж треба додати цей регістратор
    handlers: tuple[Callable[[Dispatcher], None]] = (register_handler_start,)
    for handler in handlers:
        handler(dp)
