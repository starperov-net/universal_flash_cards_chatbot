import random

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from uuid import UUID

from app.handlers.personal.callback_data_states import (
    ToStudyCallbackData,
    StudyCardCallbackData, StudyFourOptionsCallbackData,
)

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
select_language_keyboard = select_language_keyboard_builder.as_markup(
    resize_keyboard=True
)


# ------ keyboard add new item to train
def what_to_do_with_text_keyboard(item_relation_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="to train",
        callback_data=ToStudyCallbackData(item_relation_id=item_relation_id),
    )
    builder.button(text="my_variant", callback_data="my_variant")
    builder.button(text="nothing to do", callback_data="nothing_to_do")
    return builder.as_markup()


# --------keyboard "know", "don't know" for train card
def what_to_do_with_card(card_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="know", callback_data=StudyCardCallbackData(card_id=card_id))
    builder.button(
        text="don't know", callback_data=StudyCardCallbackData(card_id=card_id)
    )
    return builder.as_markup()


# ------ keyboard correct or wrong choice for study keyboard
def check_one_correct_from_four_study_keyboard(
        words_list: list[dict], card_id: UUID, memorization_stage: int, repetition_level: int
) -> InlineKeyboardMarkup:
    random.shuffle(words_list)
    builder = InlineKeyboardBuilder()
    builder.button(
        text=words_list[0]["text"],
        callback_data=StudyFourOptionsCallbackData(
            state=words_list[0]["state"],
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level
        ),
    )
    builder.button(
        text=words_list[1]["text"],
        callback_data=StudyFourOptionsCallbackData(
            state=words_list[1]["state"],
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level
        )
    )
    builder.button(
        text=words_list[2]["text"],
        callback_data=StudyFourOptionsCallbackData(
            state=words_list[2]["state"],
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level
        )
    )
    builder.button(
        text=words_list[3]["text"],
        callback_data=StudyFourOptionsCallbackData(
            state=words_list[3]["state"],
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level
        )
    )
    return builder.as_markup()
