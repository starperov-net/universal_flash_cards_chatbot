import random
from uuid import UUID
from typing import List, Any

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.handlers.personal.callback_data_states import (
    StudyFourOptionsCallbackData,
    ToStudyCallbackData,
    KnowDontKnowCallbackData,
    CustomTranslationCallbackData,
    MyWordCallbackData,
    DeletingMyWordCallbackData,
)

KEY_UP: InlineKeyboardButton = InlineKeyboardButton(text="UP", callback_data="#UP")
KEY_DOWN: InlineKeyboardButton = InlineKeyboardButton(
    text="DOWN", callback_data="#DOWN"
)


class ScrollKeyboardGenerator:
    """Creates a scrollable keyboard object.

    input data:
    - scrollkeys - a list consisting of lists of inline buttons that will be able to scroll.
    Important - a row of buttons scrolls - that is, the element being processed is the list
    item at the top level. If there are several buttons in one row, then when shifting up/down,
    all the buttons in one row are shifted synchronously.
    - max_rows_num - the maximum number of simultaneously displayed rows of buttons (one row - one
    top-level list in the scrollcase list). This number also includes possible buttons "up"\"down."
    - start_row - the number of the row (that is, the list at the top level) that should be
    displayed at the top.

    """

    def __init__(
        self,
        scrollkeys: List[List[InlineKeyboardButton]],
        max_rows_number: int = 5,
        start_row: int = 0,
    ) -> None:
        self.scrollkeys = scrollkeys
        self.max_rows_number = max_rows_number
        self.start_row = start_row

    def _get_current_scroll_keyboard_list(self) -> List[List[InlineKeyboardButton]]:
        """Get current scroll keyboard list.

        Depending on the total number of rows displayed in the list, the first row displayed
        and the total number of items displayed (together with the possible "up" - "down" buttons),
        forms a keyboard for displaying.
        """
        numbers_of_buttons_to_show = self.max_rows_number
        current_scroll_keyboard: List[List[InlineKeyboardButton]] = []
        if self.start_row != 0:
            current_scroll_keyboard = [[KEY_UP]] + current_scroll_keyboard
            numbers_of_buttons_to_show -= 1
        if numbers_of_buttons_to_show >= len(self.scrollkeys) - self.start_row:
            return (
                current_scroll_keyboard
                + self.scrollkeys[
                    self.start_row : (self.start_row + numbers_of_buttons_to_show)
                ]
            )
        else:
            return (
                current_scroll_keyboard
                + self.scrollkeys[
                    self.start_row : (self.start_row + numbers_of_buttons_to_show - 1)
                ]
                + [[KEY_DOWN]]
            )

    def markup(self) -> InlineKeyboardMarkup:
        """Get the current state of the scrolling keyboard."""

        return InlineKeyboardMarkup(
            inline_keyboard=self._get_current_scroll_keyboard_list()
        )

    def markup_up(self) -> InlineKeyboardMarkup:
        """Get the keyboard "one step up".

        Changes the values of internal variables that store the state of the keyboard after
        the "up" step and returns a new keyboard object.
        """
        self.start_row = self.start_row - 1 if self.start_row > 0 else self.start_row
        return self.markup()

    def markup_down(self) -> InlineKeyboardMarkup:
        """Get the keyboard "one step down".

        Changes the values of internal variables that store the state of the keyboard after
        the down step and returns a new keyboard object.
        """
        self.start_row = (
            (self.start_row + 1)
            if (self.start_row + (self.max_rows_number - 1)) < len(self.scrollkeys)
            else self.start_row
        )
        return self.markup()


class CombiKeyboardGenerator(ScrollKeyboardGenerator):
    """Creates a combo keyboard object: scrollable plus additional buttons."""

    def __init__(
        self,
        scrollkeys: List[List[InlineKeyboardButton]],
        additional_buttons_list: List[List[InlineKeyboardButton]],
        max_rows_number: int = 5,
        start_row: int = 0,
    ) -> None:
        super().__init__(scrollkeys, max_rows_number, start_row)
        self.additional_buttons_list = additional_buttons_list

    def markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=self._get_current_scroll_keyboard_list()
            + self.additional_buttons_list
        )


class MyWordsScrollKeyboardGenerator(ScrollKeyboardGenerator):
    """A scrolling keyboard generator with user's words."""

    def build_context_menu_for_one_word(self, card_id: UUID) -> InlineKeyboardMarkup:  # type: ignore
        """Returns a keyboard with a word and a context menu for it.

        Parameters:
            card_id: identifier of the card for which the keyboard is generated.
        """

        context_menu_button: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text="⚡️ DELETE ⚡️",
                    callback_data=DeletingMyWordCallbackData(card_id=card_id).pack(),
                ),
                InlineKeyboardButton(
                    text="BACK TO LIST", callback_data="#BACK TO LIST"
                ),
            ]
        ]
        for row in self.scrollkeys:
            if row[0].callback_data.endswith(str(card_id)):  # type: ignore
                return InlineKeyboardMarkup(inline_keyboard=[row] + context_menu_button)


def create_set_of_buttons_with_user_words(
    list_of_words: list[dict[str, Any]]
) -> list[list[InlineKeyboardButton]]:
    """Returns a list of InlineKeyboardButton lists containing the user's words.

    Converts user cards data into a set of rows consisting of buttons,
    one card per button, one button per line.

    Parameters:
        list_of_words: user card dataset, contains:
            {'card_id': UUID, 'foreign_word': str, 'native_word': str,
            'learning_status_code': int , 'learning_status': str}
    """
    return [
        [
            InlineKeyboardButton(
                text="{foreign_word}:  {native_word}  👉  {learning_status}".format(
                    **card
                ),
                callback_data=MyWordCallbackData(card_id=card["card_id"]).pack(),
            ),
        ]
        for card in list_of_words
    ]


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
def what_to_do_with_text_keyboard(
    item_relation_id: UUID, text: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="to train",
                    callback_data=ToStudyCallbackData(
                        item_relation_id=item_relation_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="my_variant",
                    callback_data=CustomTranslationCallbackData(text=text).pack(),
                ),
            ]
        ]
    )


def know_dont_know(
    card_id: UUID,
    memorization_stage: int,
    repetition_level: int,
) -> InlineKeyboardMarkup:
    """
    keyboard "know", "don't know" for train card
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅",
        callback_data=KnowDontKnowCallbackData(
            state=1,
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level,
        ),
    )
    builder.button(
        text="❎",
        callback_data=KnowDontKnowCallbackData(
            state=0,
            card_id=card_id,
            memorization_stage=memorization_stage,
            repetition_level=repetition_level,
        ),
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
