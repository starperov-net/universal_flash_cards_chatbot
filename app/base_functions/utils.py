import re


def match_to_uuid4(text: str) -> bool:
    """Checks if a text format can be UUID-4 format."""
    uuid4_regex = (
        r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$"
    )
    return bool(re.findall(uuid4_regex, text, flags=re.IGNORECASE))
