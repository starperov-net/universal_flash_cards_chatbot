class NotFullSetException(IndexError):
    """
    Use inside <check_one_correct_from_four_study_keyboard> func
    to check amount of words for learning process
    """
    pass


class NotNoneValueError(ValueError):
    """
    repetition_level' and 'memorisation_stage' attributes cannot be None for 'current_card_status
    """
    pass