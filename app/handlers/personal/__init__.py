from aiogram import Dispatcher

# тут додавати импорт нових регістраторов
from .start import register_handler_start
from .study import register_handler_study
# from .start import register_handler_start


def register_handlers_personal(dp: Dispatcher) -> None:
    # тут теж треба додати цей регістратор
    handlers = (
        register_handler_start,
        register_handler_study,
        # register_handler_start,
        )
    for handler in handlers:
        handler(dp)
