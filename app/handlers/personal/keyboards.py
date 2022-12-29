from aiogram.utils.keyboard import (InlineKeyboardBuilder,
                                    InlineKeyboardButton,
                                    InlineKeyboardMarkup)
from asyncpg.pgproto.pgproto import UUID

from app.handlers.personal.callback_data_states import ToStudyCallbackData

# ------- keyboard for choice languages
languages = [
    "Albanian",
    "Belarusian",
    "Chinese",
    "Croatian",
    "English",
    "Estonian",
    "French",
    "German",
    "Russian",
    "Ukrainian",
]

select_language_keyboard_builder = InlineKeyboardBuilder()

for i in range(0, len(languages) - 1, 3):
    select_language_keyboard_builder.row(
        InlineKeyboardButton(text=languages[i], callback_data=languages[i]),
        InlineKeyboardButton(text=languages[i + 1], callback_data=languages[i + 1]),
        InlineKeyboardButton(text=languages[i + 2], callback_data=languages[i + 2]),
    )
select_language_keyboard_builder.row(
    InlineKeyboardButton(text=languages[-1], callback_data=languages[-1])
)
select_language_keyboard = select_language_keyboard_builder.as_markup(resize_keyboard=True)


# ------ keyboard add new item to train
def what_to_do_with_text_keyboard(item_relation_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="to train",
                   callback_data=ToStudyCallbackData(text="to_train", item_relation_id=item_relation_id))
    builder.button(text="my_variant",
                   callback_data="my_variant")
    builder.button(text="nothing to do",
                   callback_data="nothing_to_do")
    return builder.as_markup()
