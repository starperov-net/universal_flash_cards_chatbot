from datetime import datetime

from app import tables
from app.tests.utils import (
    TELEGRAM_USER_1,
    TELEGRAM_USER_2,
    TELEGRAM_USER_3,
    TELEGRAM_USER_GOOGLE,
)

CONTEXT_en = tables.Context(name="English", name_alfa2="en")

CONTEXT_de = tables.Context(name="German", name_alfa2="de")

CONTEXT_uk = tables.Context(name="Ukrainian", name_alfa2="uk")

CONTEXT_ru = tables.Context(name="Russian", name_alfa2="ru")

USER_GOOGLE = tables.User(
    telegram_user_id=TELEGRAM_USER_GOOGLE.id,
    telegram_language=TELEGRAM_USER_GOOGLE.language_code or "",
    user_name=TELEGRAM_USER_GOOGLE.username or "",
    first_name=TELEGRAM_USER_GOOGLE.first_name or "",
    last_name=TELEGRAM_USER_GOOGLE.last_name or "",
)

USER_1 = tables.User(
    telegram_user_id=TELEGRAM_USER_1.id,
    telegram_language=TELEGRAM_USER_1.language_code or "",
    user_name=TELEGRAM_USER_1.username or "",
    first_name=TELEGRAM_USER_1.first_name or "",
    last_name=TELEGRAM_USER_1.last_name or "",
)

USER_2 = tables.User(
    telegram_user_id=TELEGRAM_USER_2.id,
    telegram_language=TELEGRAM_USER_2.language_code or "",
    user_name=TELEGRAM_USER_2.username or "",
    first_name=TELEGRAM_USER_2.first_name or "",
    last_name=TELEGRAM_USER_2.last_name or "",
)

USER_3 = tables.User(
    telegram_user_id=TELEGRAM_USER_3.id,
    telegram_language=TELEGRAM_USER_3.language_code or "",
    user_name=TELEGRAM_USER_3.username or "",
    first_name=TELEGRAM_USER_3.first_name or "",
    last_name=TELEGRAM_USER_3.last_name or "",
)

USER_CONTEXT_1_uk_en = tables.UserContext(
    context_1=CONTEXT_uk,
    context_2=CONTEXT_en,
    user=USER_1,
    last_date=datetime(2022, 2, 24),
)

USER_CONTEXT_2_uk_en = tables.UserContext(
    context_1=CONTEXT_uk,
    context_2=CONTEXT_en,
    user=USER_2,
    last_date=datetime(2022, 2, 24),
)

USER_CONTEXT_3_ru_de = tables.UserContext(
    context_1=CONTEXT_ru,
    context_2=CONTEXT_de,
    user=USER_3,
    last_date=datetime(2022, 2, 24),
)

ITEM_en_auto = tables.Item(author=USER_1.id, context=CONTEXT_en.id, text="auto")
ITEM_de_auto = tables.Item(author=USER_1.id, context=CONTEXT_de.id, text="auto")
ITEM_de_wagen = tables.Item(author=USER_GOOGLE.id, context=CONTEXT_de.id, text="wagen")

ITEM_uk_automobil = tables.Item(
    author=USER_1.id, context=CONTEXT_uk.id, text="автомобіль"
)

ITEM_ru_mashina = tables.Item(author=USER_1.id, context=CONTEXT_ru.id, text="машина")

ITEM_RELATION_1_ru_de = tables.ItemRelation(
    author=USER_1.id, item_1=ITEM_ru_mashina, item_2=ITEM_de_auto
)

ITEM_RELATION_1_uk_en = tables.ItemRelation(
    author=USER_1.id, item_1=ITEM_uk_automobil, item_2=ITEM_en_auto
)

ITEM_RELATION_GOOGLE_en_uk = tables.ItemRelation(
    author=USER_GOOGLE.id, item_1=ITEM_en_auto, item_2=ITEM_uk_automobil
)

ITEM_RELATION_3_ru_de = tables.ItemRelation(
    author=USER_3.id, item_1=ITEM_ru_mashina, item_2=ITEM_de_auto
)

ITEM_RELATION_GOOGLE_ru_de = tables.ItemRelation(
    author=USER_3.id, item_1=ITEM_ru_mashina, item_2=ITEM_de_wagen
)
