from aiogram import Dispatcher
from aiogram.filters import Command

def quick_self_test():
    pass

def register_handler_quick_selt_test(dp: Dispatcher) -> None:
    dp.message.register(
        quick_self_test, Command(commands=["self-test", "quick self-test", "швидка самоперевірка"])
    )

    # register handler two times for getting <1> or <0> reply from buttons
    dp.callback_query.register(...
    )