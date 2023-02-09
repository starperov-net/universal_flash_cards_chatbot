from aiogram import Dispatcher

# тут додавати импорт нових регістраторов
from app.handlers.personal.settings import register_handler_settings
from app.handlers.personal.start import register_handler_start
from app.handlers.personal.study import register_handler_study


def register_handlers_personal(dp: Dispatcher) -> None:
    # тут теж треба додати цей регістратор
    handlers: tuple = (
        register_handler_settings,
        register_handler_study,
        register_handler_start,
    )

    for handler in handlers:
        handler(dp)
