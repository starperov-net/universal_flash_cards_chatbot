import random
from uuid import UUID
from datetime import datetime
import pytz

from typing import List, Optional, Any
from dataclasses import dataclass

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.db_functions.personal import get_user_context, update_user_context

from app.handlers.personal.callback_data_states import (
    StudyFourOptionsCallbackData,
    ToStudyCallbackData,
    KnowDontKnowCallbackData,
    CustomTranslationCallbackData,
    MyWordCallbackData,
    DeletingMyWordCallbackData,
)
from app.db_functions.personal import get_context, create_user_context

KEY_UP: InlineKeyboardButton = InlineKeyboardButton(text="UP", callback_data="#UP")
KEY_DOWN: InlineKeyboardButton = InlineKeyboardButton(
    text="DOWN", callback_data="#DOWN"
)


@dataclass(frozen=True)
class KeyKeyboard:
    """Describes a key to identify a keyboard instance and a message."""

    __slots__ = ["bot_id", "chat_id", "user_id", "message_id"]

    bot_id: int
    chat_id: int | None | str
    user_id: int | None
    message_id: int | None


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
        scroll_step: int = 1,
    ) -> None:
        self.scrollkeys = scrollkeys
        self.max_rows_number = max_rows_number
        self.start_row = start_row
        self.scroll_step = scroll_step

    def _get_current_scroll_keyboard_list(self) -> List[List[InlineKeyboardButton]]:
        """Get current scroll keyboard list.

        Depending on the total number of rows displayed in the list, the first row displayed
        and the total number of items displayed (together with the possible "up" - "down" buttons),
        forms a keyboard for displaying.
        """
        self.numbers_of_buttons_to_show = self.max_rows_number
        current_scroll_keyboard: List[List[InlineKeyboardButton]] = []
        if self.start_row != 0:
            current_scroll_keyboard = [[KEY_UP]] + current_scroll_keyboard
            self.numbers_of_buttons_to_show -= 1
        if self.start_row + self.numbers_of_buttons_to_show >= len(self.scrollkeys) - 1:
            return (
                current_scroll_keyboard
                + self.scrollkeys[
                    self.start_row : (self.start_row + self.numbers_of_buttons_to_show)
                ]
            )
        else:
            self.numbers_of_buttons_to_show -= 1
            return (
                current_scroll_keyboard
                + self.scrollkeys[
                    self.start_row : (self.start_row + self.numbers_of_buttons_to_show)
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
        self.start_row = (
            self.start_row - self.scroll_step
            if self.start_row - self.scroll_step >= 0
            else 0
        )
        return self.markup()

    def markup_down(self) -> InlineKeyboardMarkup:
        """Get the keyboard "one step down".

        Changes the values of internal variables that store the state of the keyboard after
        the down step and returns a new keyboard object.
        """
        self.start_row = (
            (self.start_row + self.scroll_step)
            if (self.start_row + (self.scroll_step - 1)) < len(self.scrollkeys)
            else len(self.scrollkeys) - self.scroll_step
        )
        return self.markup()


class CombiKeyboardGenerator(ScrollKeyboardGenerator):
    """Creates a combo keyboard object: scrollable plus additional buttons."""

    def __init__(
        self,
        scrollkeys: List[List[InlineKeyboardButton]],
        additional_buttons_list: Optional[List[List[InlineKeyboardButton]]] = None,
        pre_additional_buttons_list: Optional[List[List[InlineKeyboardButton]]] = None,
        max_rows_number: int = 5,
        start_row: int = 0,
        scroll_step: int = 1,
    ) -> None:
        super().__init__(scrollkeys, max_rows_number, start_row, scroll_step)
        self.additional_buttons_list = additional_buttons_list or []
        self.pre_additional_buttons_list = pre_additional_buttons_list or []

    def markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=(
                self.pre_additional_buttons_list
                + self._get_current_scroll_keyboard_list()
                + self.additional_buttons_list
            )
        )


class KeyboardCreateUserContext(CombiKeyboardGenerator):
    """Creates a keyboard object for the "create new user context" menu item.

    Adds a date attribute (to store the selected settings), adds a property text to generate a message
    that matches the current state of the user's selection.
    """

    def __init__(
        self,
        scrollkeys: List[List[InlineKeyboardButton]],
        additional_buttons_list: Optional[List[List[InlineKeyboardButton]]] = None,
        pre_additional_buttons_list: Optional[List[List[InlineKeyboardButton]]] = None,
        max_rows_number: int = 5,
        start_row: int = 0,
        scroll_step: int = 1,
    ) -> None:
        # The attribute is set depending on the actions (buttons pressed by the user) of the user and responds
        # of the user's choice when creating a user context - self.data[0] - the first context,
        # self.data[1] - the second context. Values can take default values until assigned by the user
        # of the context (True\False) and this makes it possible to prioritize the assignment of the context
        # depending on of previously pressed buttons (SET FIRST\SET SECOND).
        # attribute self._data[2] signals that a new context is created in the method self.set_user_context(user_id)
        # --> self._data[2] = True. This is used in the self.text property to form a message about
        # creating a new status and setting it as current.
        self._data = [True, False, False]
        super().__init__(
            scrollkeys,
            additional_buttons_list,
            pre_additional_buttons_list,
            max_rows_number,
            start_row,
            scroll_step,
        )

    @property
    def text(self):
        """Returns the value that should be displayed on the screen (message to which the keyboard is locked).

        The image on the screen is displayed depending on the state of the self.data attribute.
        """
        first = (
            f"{self._data[0]['name']} ({self._data[0]['name_alfa2'].upper()})"
            if isinstance(self._data[0], dict)
            else "XXXXXXXXXX"
        )
        second = (
            f"{self._data[1]['name']} ({self._data[1]['name_alfa2'].upper()})"
            if isinstance(self._data[1], dict)
            else "XXXXXXXXXX"
        )
        if not self._data[2]:
            if self._data[0] is True:
                first = "set first language"
            elif self._data[1] is True:
                second = "set second language"
            return f"<b>{first} --- {second}</b>".center(35)
        return f"new language context created and set as current:\n{first} --- {second}"

    async def set_first(self, context: Optional[dict] = None):
        """Sets the initialization of the first context if it receives id_ctx, otherwise
        prepares the keyboard to install the second context in the next step.
        """
        if not context:
            self._data[0] = True
            self._data[1] = (
                False if not isinstance(self._data[1], dict) else self._data[1]
            )
        else:
            self._data[0] = context
        print(f"result set_first(): {self._data}")

    async def set_second(self, context: Optional[dict] = None):
        """Sets the default of the second context if it receives id_ctx, otherwise
        prepares the keyboard to install the second context in the next step.
        """
        if not context:
            self._data[1] = True
            self._data[0] = (
                False if not isinstance(self._data[0], dict) else self._data[0]
            )
        else:
            self._data[1] = context
        print(f"result set_second(): {self._data}")

    async def set_lng(self, id_ctx: UUID):
        """Depending on the values in self._data sets the value of the context by
        received id_ctx to the position that previously had the value True.
        """
        context = (await get_context(context_id=id_ctx))[0]
        if self._data[0] is True:
            await self.set_first(context)
        else:
            await self.set_second(context)

    async def set_user_context(self, user_id: UUID | int):
        """Checks the validity of self._dict
        - element 0 and element 1 are dict - set a new user_context for this user, change the state
        - not set 0 - set_first
        - not set 1 - set_second
        """
        if not isinstance(self._data[0], dict):
            await self.set_first()
        elif not isinstance(self._data[1], dict):
            await self.set_second()
        else:
            await create_user_context(
                user_id=user_id,
                context_1=self._data[0]["id"],
                context_2=self._data[1]["id"],
            )
            self._data[2] = True
        return self._data[2]


class KeyboardSetUserContext(CombiKeyboardGenerator):
    """Creates a keyboard object for the "/settings"-command menu item.

    Outputs:
    - a message that reflects the currently selected user context (changes depending on
    the context selected by the user)
    - a scrolling keyboard with a description of the contexts existing for the user (pressing
    leads to the display in the message and storing the state)
    - button "set context as actual"
    - button "create new context"
    - button "send context to archive"
    - button "extract context from archive"
    """

    async def __init__(self, user_id: int) -> None:
        user_contexts = await get_user_context(user_id)
        self.user_contexts_title_dict = {
            str(user_context["id"]): user_context["context_1"]["name"]
            + " - "
            + user_context["context_2"]["name"]
            for user_context in user_contexts
        }
        scrollkeys: List[List[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text=user_context["context_1"]["name"]
                    + "-"
                    + user_context["context_2"]["name"],
                    callback_data=str(user_context["id"]),
                )
            ]
            for user_context in user_contexts
        ]
        additional_buttons: List[List[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text="create new context", callback_data="#CREATE_NEW_CONTEXT"
                )
            ],
        ]
        self._current_context_id = str(user_contexts[0]["id"])
        self._current_context = user_contexts[0]
        super().__init__(
            scrollkeys=scrollkeys,
            additional_buttons_list=additional_buttons,
            max_rows_number=5,
            start_row=0,
            scroll_step=4,
        )

    @property
    def text(self) -> str:
        return f"<b>{self.user_contexts_title_dict[self._current_context_id]}</b>"

    async def set_existing_context(self, context_id: UUID) -> None:
        """ "Set the current datetime with timezone in user_context.latest_date."""
        last_date = datetime.now().replace(tzinfo=pytz.utc)
        await update_user_context(id=context_id, last_date=last_date)
        self._current_context_id = str(context_id)


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
