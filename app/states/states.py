from aiogram.fsm.state import State, StatesGroup


class FSMChooseLanguage(StatesGroup):
    native_language = State()
    target_language = State()


class FSMStudyOneFromFour(StatesGroup):
    """Creates <State Machine> for <study> handler.

    Inherits from <StateGroup> class
    """

    studying = State()


class FSMCustomTranslation(StatesGroup):
    """State machine class for holding state while custom translation"""

    custom_translation = State()


class FSMMyWords(StatesGroup):
    mywords = State()
    mywords_up = State()
    mywords_down = State()
