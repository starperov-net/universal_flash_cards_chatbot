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


class StudyCardCallbackData(CallbackData, prefix="study_card"):
    """
    CallbackQuerry  - "know", "don't know"
    data - 'card_id'
    """

    card_id: UUID

class KnowDontKnowCallbackData(CallbackData, prefix="self_test"):
    """
    CallbackQuerry  - "know", "don't know"
    data - 'state', 'card_id'
    """
    state: int
    card_id: UUID


class StudyFourOptionsCallbackData(CallbackData, prefix="study_four_options"):
    """CallbackData for studying four words mode."""

    state: int
    card_id: UUID
    memorization_stage: int
    repetition_level: int
