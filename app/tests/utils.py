from datetime import datetime

from aiogram.types import User

from app import tables


TELEGRAM_USER_1 = User(
    id=1,
    is_bot=False,
    first_name="Test",
    last_name="Bot",
    username="testbot_1",
    language_code="uk-UK",
    is_premium=False,
    added_to_attachment_menu=None,
    can_join_groups=None,
    can_read_all_group_messages=None,
    supports_inline_queries=None,
)

TELEGRAM_USER_2 = User(
    id=2,
    is_bot=False,
    first_name="Test",
    last_name=None,
    username=None,
    language_code=None,
    is_premium=False,
    added_to_attachment_menu=None,
    can_join_groups=None,
    can_read_all_group_messages=None,
    supports_inline_queries=None,
)

TELEGRAM_USER_GOOGLE = User(
    id=0,
    is_bot=False,
    first_name="Google",
    last_name=None,
    username=None,
    language_code=None,
    is_premium=False,
    added_to_attachment_menu=None,
    can_join_groups=None,
    can_read_all_group_messages=None,
    supports_inline_queries=None,
)

TELEGRAM_USER_3=User(
    id=3,
    is_bot=False,
    first_name="Bot3",
    last_name=None,
    username=None,
    language_code=None,
    is_premium=False,
    added_to_attachment_menu=None,
    can_join_groups=None,
    can_read_all_group_messages=None,
    supports_inline_queries=None,
)

TABLE_CONTEXT_en = tables.Context(
    name="English",
    name_alfa2="en"
)

TABLE_CONTEXT_de = tables.Context(
    name="German",
    name_alfa2="de"
)

TABLE_CONTEXT_uk = tables.Context(
    name="Ukrainian",
    name_alfa2="uk"
)

TABLE_CONTEXT_ru = tables.Context(
    name="Russian",
    name_alfa2="ru"
)

TABLE_USER_GOOGLE = tables.User(
    telegram_user_id=TELEGRAM_USER_GOOGLE.id,
    telegram_language=TELEGRAM_USER_GOOGLE.language_code or '',
    user_name=TELEGRAM_USER_GOOGLE.username or '',
    first_name=TELEGRAM_USER_GOOGLE.first_name or '',
    last_name=TELEGRAM_USER_GOOGLE.last_name or ''
)

TABLE_USER_1 = tables.User(
    telegram_user_id=TELEGRAM_USER_1.id,
    telegram_language=TELEGRAM_USER_1.language_code or '',
    user_name=TELEGRAM_USER_1.username or '',
    first_name=TELEGRAM_USER_1.first_name or '',
    last_name=TELEGRAM_USER_1.last_name or ''
)

TABLE_USER_2 = tables.User(
    telegram_user_id=TELEGRAM_USER_2.id,
    telegram_language=TELEGRAM_USER_2.language_code or '',
    user_name=TELEGRAM_USER_2.username or '',
    first_name=TELEGRAM_USER_2.first_name or '',
    last_name=TELEGRAM_USER_2.last_name or ''
)

TABLE_USER_3 = tables.User(
    telegram_user_id=TELEGRAM_USER_3.id,
    telegram_language=TELEGRAM_USER_3.language_code or '',
    user_name=TELEGRAM_USER_3.username or '',
    first_name=TELEGRAM_USER_3.first_name or '',
    last_name=TELEGRAM_USER_3.last_name or ''
)

TABLE_USER_CONTEXT_1_uk_en = tables.UserContext(
    context_1=TABLE_CONTEXT_uk.id,
    context_2=TABLE_CONTEXT_en.id,
    user=TABLE_USER_1.id,
    last_date=datetime(2022, 2, 24)
)

TABLE_USER_CONTEXT_2_uk_en = tables.UserContext(
    context_1=TABLE_CONTEXT_uk.id,
    context_2=TABLE_CONTEXT_en.id,
    user=TABLE_USER_2.id,
    last_date=datetime(2022, 2, 24)
)

TABLE_USER_CONTEXT_3_ru_de = tables.UserContext(
    context_1=TABLE_CONTEXT_ru.id,
    context_2=TABLE_CONTEXT_de.id,
    user=TABLE_USER_3.id,
    last_date=datetime(2022, 2, 24)
)

TABLE_ITEM_en_auto = tables.Item(
    author=TABLE_USER_1.id,
    context=TABLE_CONTEXT_en.id,
    text='auto'
)
TABLE_ITEM_de_auto = tables.Item(
    author=TABLE_USER_1.id,
    context=TABLE_CONTEXT_de.id,
    text='auto'
)
TABLE_ITEM_de_wagen = tables.Item(
    author=TABLE_USER_GOOGLE.id,
    context=TABLE_CONTEXT_de.id,
    text='wagen'
)

TABLE_ITEM_uk_automobil = tables.Item(
    author=TABLE_USER_1.id,
    context=TABLE_CONTEXT_uk.id,
    text='автомобіль'
)

TABLE_ITEM_ru_mashina = tables.Item(
    author=TABLE_USER_1.id,
    context=TABLE_CONTEXT_ru.id,
    text='машина'
)

TABLE_ITEM_RELATION_1_ru_de = tables.ItemRelation(
    author=TABLE_USER_1.id,
    item_1=TABLE_ITEM_ru_mashina,
    item_2=TABLE_ITEM_de_auto
)

TABLE_ITEM_RELATION_1_uk_en = tables.ItemRelation(
    author=TABLE_USER_1.id,
    item_1=TABLE_ITEM_uk_automobil,
    item_2=TABLE_ITEM_en_auto
)

TABLE_ITEM_RELATION_GOOGLE_en_uk = tables.ItemRelation(
    author=TABLE_USER_GOOGLE.id,
    item_1=TABLE_ITEM_en_auto,
    item_2=TABLE_ITEM_uk_automobil
)

TABLE_ITEM_RELATION_3_ru_de = tables.ItemRelation(
    author=TABLE_USER_3.id,
    item_1=TABLE_ITEM_ru_mashina,
    item_2=TABLE_ITEM_de_auto
)

TABLE_ITEM_RELATION_GOOGLE_ru_de = tables.ItemRelation(
    author=TABLE_USER_3.id,
    item_1=TABLE_ITEM_ru_mashina,
    item_2=TABLE_ITEM_de_wagen
)