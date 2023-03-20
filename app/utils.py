from uuid import UUID


def is_uuid(str: str) -> bool:
    """Check if value is uuid"""
    try:
        UUID(str, version=4)
        return True
    except Exception:
        return False


async def get_id_for_context_class_language():
    pass
