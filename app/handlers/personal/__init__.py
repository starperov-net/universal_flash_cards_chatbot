from aiogram import Dispatcher

# тут додавати импорт нових регістраторов
from app.handlers.personal.settings import register_handler_settings
from app.handlers.personal.start import register_handler_start
from app.handlers.personal.study import register_handler_study
from app.handlers.personal.quick_self_test import register_handler_quick_selt_test
from app.handlers.personal.help import register_handler_help
from app.handlers.personal.cancel import register_handler_cancel
from app.handlers.personal.list_of_user_words import register_handler_list


def register_handlers_personal(dp: Dispatcher) -> None:
    # тут теж треба додати цей регістратор

    handlers: tuple = (
        register_handler_settings,
        register_handler_study,
        register_handler_quick_selt_test,
        register_handler_help,
        register_handler_cancel,
        register_handler_list,
        register_handler_start,
    )

    for handler in handlers:
        handler(dp)
