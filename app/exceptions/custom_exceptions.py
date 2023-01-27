class NotFullSetException(IndexError):
    """Exception when set words is not full."""

    pass


class NotNoneValueError(ValueError):
    """
    repetition_level' and 'memorisation_stage' attributes cannot be None for 'current_card_status
    """
    pass
