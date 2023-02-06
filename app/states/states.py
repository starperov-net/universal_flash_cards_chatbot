from aiogram.fsm.state import State, StatesGroup


class FSMChooseLanguage(StatesGroup):
    native_language = State()
    target_language = State()


class FSMCustomTranslation(StatesGroup):
    """State machine class for holding state while custom translation"""
    custom_translation = State()