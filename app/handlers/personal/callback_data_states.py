from uuid import UUID

from aiogram.filters.callback_data import CallbackData


class ToStudyCallbackData(CallbackData, prefix="to_study"):
    """
    Class user-defined callbacks.
    CallbackData - Base class for callback data wrapper.
    The class-keyword :code:`prefix` is required to define prefix

    Fields of the class can have only these types: int, str, float, Decimal, Fraction, UUID, Enum.
    """

    item_relation_id: UUID


class CustomTranslationCallbackData(CallbackData, prefix="my_variant"):
    """
    Class user-defined callbacks.
    CallbackData - Base class for callback data wrapper.
    The class-keyword :code:`prefix` is required to define prefix

    Fields of the class can have only these types: int, str, float, Decimal, Fraction, UUID, Enum.
    """

    text: str


class KnowDontKnowCallbackData(CallbackData, prefix="self_test"):
    """
    CallbackQuerry  - "know", "don't know"
    """

    state: int
    card_id: UUID
    memorization_stage: int
    repetition_level: int


class StudyFourOptionsCallbackData(CallbackData, prefix="study_four_options"):
    """CallbackData for studying four words mode."""

    state: int
    card_id: UUID
    memorization_stage: int
    repetition_level: int
