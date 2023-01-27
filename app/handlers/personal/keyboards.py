import random
from uuid import UUID

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.handlers.personal.callback_data_states import (
    StudyCardCallbackData,
    StudyFourOptionsCallbackData,
    ToStudyCallbackData,
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="to train",
                    callback_data=ToStudyCallbackData(
                        item_relation_id=item_relation_id
                    ).pack(),
                ),
                InlineKeyboardButton(text="my_variant", callback_data="my_variant"),
                InlineKeyboardButton(
                    text="nothing to do", callback_data="nothing_to_do"
                ),
            ]
        ]
    )


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
    words_list: list[dict],
    card_id: UUID,
    memorization_stage: int,
    repetition_level: int,
) -> InlineKeyboardMarkup:
    """A keyboard for four words study mode.

    Creates and adjusts a keyboard object for four words
    studying mode.

    Parameters:
        words_list:
            a list of four dicts for picking on correct option
            from four given options
        card_id:
            card identifier in <UUID> format
        memorization_stage:
            memorization stage according to user's db data
        repetition_level:
            repetition level according to user's db data

    Returns:
        InlineKeyboardMarkup:
            see base class
    """

    random.shuffle(words_list)
    builder = InlineKeyboardBuilder()

    # words_list = [{"text": "some_word", "state": 0}, ...]
    for el in words_list:
        builder.button(
            text=el["text"],
            callback_data=StudyFourOptionsCallbackData(
                state=el["state"],
                card_id=card_id,
                memorization_stage=memorization_stage,
                repetition_level=repetition_level,
            ),
        )

    builder.adjust(2)
    return builder.as_markup()
