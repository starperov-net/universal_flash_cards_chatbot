from typing import Any, Optional, List
from uuid import UUID

import aiogram

from app import serializers
from app.exceptions.custom_exceptions import NotFullSetException
from app.tables import Card, Context, Item, ItemRelation, User, UserContext


async def add_card_db(
    telegram_user_id: int, item_relation_id: UUID, author: Optional[int] = None
) -> Card:
    user: UUID = await get_existing_user_id_db(telegram_user_id)
    card: Card = Card(user=user, item_relation=item_relation_id, author=author or user)
    await card.save()
    return card


async def update_card_db(card: serializers.Card) -> None:
    """Updates tables.Card row.

    As argument uses serializers.Cart type for checkin in possible types for fields."""
    await Card.update(card.to_dict_ignore_none()).where(Card.id == card.id)


async def add_item_relation_db(
    author_id: UUID, item_1_id: UUID, item_2_id: UUID
) -> UUID:
    item_relation: ItemRelation = ItemRelation(
        author=author_id, item_1=item_1_id, item_2=item_2_id
    )
    await item_relation.save()
    return item_relation.id


async def add_user_context_db(
    data_callback_query: dict[str, Any], user_db: User
) -> UserContext:
    context_1 = await Context.objects().get(
        Context.name == data_callback_query["native_lang"]
    )
    context_2 = await Context.objects().get(
        Context.name == data_callback_query["target_lang"]
    )
    user_context = UserContext(
        context_1=context_1,
        context_2=context_2,
        user=user_db,
    )
    await user_context.save()
    return user_context


async def is_words_in_card_db(telegram_user_id: int, item_relation_id: UUID) -> bool:
    """
    The function checks if the user already has the item_relation to study.
    """
    card: list[Card] = await Card.objects().where(
        (Card.user.telegram_user_id == telegram_user_id)
        & (Card.item_relation.id == item_relation_id)
    )
    return bool(card)


async def get_or_create_item_db(text: str, context_id: UUID, author_id: UUID) -> UUID:
    item: Item = await Item.objects().get_or_create(
        (Item.text == text) & (Item.context == context_id),
        defaults={"author": author_id, "context": context_id, "text": text},
    )
    return item.id


async def get_or_create_user_db(data_telegram: aiogram.types.User) -> User:
    user = await User.objects().get_or_create(
        User.telegram_user_id == data_telegram.id,
        defaults={
            "telegram_language": data_telegram.language_code or "",
            "user_name": data_telegram.username or "",
            "first_name": data_telegram.first_name,
            "last_name": data_telegram.last_name or "",
        },
    )
    return user


async def get_context_id_db(name_alfa2: str) -> UUID:
    context: Context = await Context.objects().get(Context.name_alfa2 == name_alfa2)
    return context.id


async def get_item_relation_with_related_items_by_id_db(
    item_relation_id: UUID,
) -> ItemRelation:
    """
    return: {ItemRelation}:
            author = {UUID}
            id = {UUID}
            item_1 = {Item}
            item_2 = {Item}
    """
    item_relation: ItemRelation = await ItemRelation.objects(
        [ItemRelation.item_1, ItemRelation.item_2]
    ).get(ItemRelation.id == item_relation_id)
    return item_relation


async def get_item_relation_by_text_db(
    text: str, user_context: UserContext
) -> Optional[ItemRelation]:
    """
    беремо всі переклади авторства юзера чи гугла(telegram_iser_id=0)
    додаемо умову пошуку тільки тих слів, де мови такі ж як і у user_context
    отримали як би "словничок" саме цього юзера
    тепер із цього словничка обираємо записи з співпадінням слів
    відсортовуємо в зворотньому напрямку, щоб першим стояв переклад юзера, а гугла  - в кінці
    беремо перший переклад, тобто переклад юзера.

    return: Optional[ItemRelation]:
            author = {UUID}
            id = {UUID}
            item_1 = {Item}
            item_2 = {Item}
    """
    item_relation: ItemRelation = (
        await ItemRelation.objects([ItemRelation.item_1, ItemRelation.item_2])
        .where(
            (
                ItemRelation.author.telegram_user_id.is_in(
                    [user_context.user.telegram_user_id, 0]
                )
            )
            & (
                ItemRelation.item_1.context.is_in(
                    [user_context.context_1.id, user_context.context_2.id]
                )
            )
            & (
                ItemRelation.item_2.context.is_in(
                    [user_context.context_1.id, user_context.context_2.id]
                )
            )
        )
        .where((ItemRelation.item_1.text == text) | (ItemRelation.item_2.text == text))
        .order_by(ItemRelation.author.telegram_user_id, ascending=False)
        .first()
    )
    return item_relation


async def get_user_context_db(telegram_user_id: int) -> Optional[UserContext]:
    user_context: Optional[UserContext] = (
        await UserContext.objects(UserContext.all_related())  # type: ignore
        .get(UserContext.user.telegram_user_id == telegram_user_id)
        .order_by(UserContext.last_date, ascending=False)
        .first()
    )

    return user_context


async def get_existing_user_id_db(telegram_user_id: int) -> UUID:
    user: User = await User.objects().get(User.telegram_user_id == telegram_user_id)
    return user.id


async def get_translated_text_from_item_relation(
    text: str, item_relation: ItemRelation
) -> str:
    """
    Із item_relation беру два слова і із них прибираю те слово, яке користувач ввів для перекладу(text),
    значить інше слово і є переклад.
    """
    text1, text2 = item_relation.item_1.text, item_relation.item_2.text
    translated_text: str = list(set((text1, text2)) - set((text,)))[0]
    return translated_text


async def get_all_items_according_context(context_id: UUID) -> list[dict]:
    """Collects all items.text

    Parameters:
        context_id:
            user's context identifier

    Returns:
        list[dict]:
            list of items from all items in db with shown context
            example:
                [{'text': 'Например'}, {'text': 'быстрый'}, ...]
    """

    query = f"""
    SELECT DISTINCT text
    FROM item
    WHERE context='{str(context_id)}';
    """
    random_words: list[dict] = await Item.raw(query)
    if len(random_words) < 3:
        raise NotFullSetException
    return random_words


async def get_context(
        context_class_id: Optional[UUID] = None,
        context_id: Optional[UUID] = None
) -> Any:
    """Get context.
    
    context_class_id: context_class.id (UUID) - optional
    context_id: context.id (UUID) - optional

    return: list of dicts {
        'id'
    }
    """
    if not context_class_id and not context_id:
        return await Context.select()
    elif not context_id and context_class_id:
        return await Context.select().where(Context.context_class == context_class_id)
    elif context_id and not context_class_id:
        return await Context.select().where(Context.id == context_id)
    else:
        return await Context.select().where(
            (Context.id == context_id) & (Context.context_class == context_class_id)
        )


async def get_user_context(
    user: UUID | int, user_context_id: Optional[UUID] = None
) -> Any:

    """Get user_context.

    user: user.id (UUID type) or user.telegram_user_id (int type)
    user_context_id: user_context.id (UUID type) - optional

    return: list of dicts {
        'id': UserContext.id (UUID),
        'context_1.id': Context.id (UUID),
        'context_1.context_class': ContextClass.id (UUID)
    }
    """
    if not isinstance(user, UUID):
        if not isinstance(user, int):
            raise TypeError(
                f"argument 'user' in 'get_user_context' must be 'int' or 'UUID' types, but {type(user)} goten."
            )
        if user_context_id is None:
            return (
                await UserContext.select(
                    UserContext.id,
                    UserContext.last_date,
                    UserContext.context_1.all_columns(
                        exclude=[UserContext.context_1.context_class]
                    ),
                    UserContext.context_1.context_class.all_columns(),
                    UserContext.context_2.all_columns(
                        exclude=[UserContext.context_2.context_class]
                    ),
                    UserContext.context_2.context_class.all_columns(),
                    UserContext.user.id,
                    UserContext.user.telegram_user_id,
                )
                .where(UserContext.user.telegram_user_id == user)
                .order_by(UserContext.last_date)
                .output(nested=True)
            )
        else:
            return (
                await UserContext.select(
                    UserContext.id,
                    UserContext.last_date,
                    UserContext.context_1.all_columns(
                        exclude=[UserContext.context_1.context_class]
                    ),
                    UserContext.context_1.context_class.all_columns(),
                    UserContext.context_2.all_columns(
                        exclude=[UserContext.context_2.context_class]
                    ),
                    UserContext.context_2.context_class.all_columns(),
                    UserContext.user.id,
                    UserContext.user.telegram_user_id,
                )
                .where(
                    UserContext.id == user_context_id,
                    UserContext.user.telegram_user_id == user,
                )
                .output(nested=True)
            )
    if user_context_id is None:
        return (
            await UserContext.select(
                UserContext.id,
                UserContext.last_date,
                UserContext.context_1.all_columns(
                    exclude=[UserContext.context_1.context_class]
                ),
                UserContext.context_1.context_class.all_columns(),
                UserContext.context_2.all_columns(
                    exclude=[UserContext.context_2.context_class]
                ),
                UserContext.context_2.context_class.all_columns(),
                UserContext.user.id,
                UserContext.user.telegram_user_id,
            )
            .where(UserContext.user.id == user)
            .order_by(UserContext.last_date)
            .output(nested=True)
        )
    else:
        return (
            await UserContext.select(
                UserContext.id,
                UserContext.last_date,
                UserContext.context_1.all_columns(
                    exclude=[UserContext.context_1.context_class]
                ),
                UserContext.context_1.context_class.all_columns(),
                UserContext.context_2.all_columns(
                    exclude=[UserContext.context_2.context_class]
                ),
                UserContext.user.id,
                UserContext.user.telegram_user_id,
            )
            .where(UserContext.user.id == user, UserContext.id == user_context_id)
            .order_by(UserContext.last_date)
            .output(nested=True)
        )


if __name__ == "__main__":
    import asyncio

    # this code uses user_id, telegram_user_id and user_context_id from a locally deployed debug database.
    # When testing in a different environment, replace their values with the actual ones.
    user_id_uuid = UUID("bffc39d2-03d2-46ea-93b9-521a602913e5")
    telegram_user_id = 144371650
    user_context_id = UUID("9296f4aa-b3b4-4fa0-b97f-ba90f658f576")

    async def test() -> None:
        res_1 = await get_user_context(user_id_uuid)
        print(f"user - UUID, user_context=None\n{res_1}")

        res_2 = await get_user_context(telegram_user_id)
        print(f"user - int, user_context=None\n{res_2}")

        res_3 = await get_user_context(user_id_uuid, user_context_id)
        print(f"user - UUID, user_context=UUID\n{res_3}")

        res_4 = await get_user_context(telegram_user_id, user_context_id)
        print(f"user - int, user_context=UUID\n{res_4}")

    asyncio.run(test())

# for examle:
# user - UUID, user_context=None
# [
#   {
#       'context_1': {
#           'context_class': {
#               'description': None,
#               'id': None,
#               'name': None
#               },
#           'description': '',
#           'id': UUID('03a8d71f-4b45-46fc-abe4-44cfbf83bedc'),
#           'name': 'Ukrainian', 'name_alfa2': 'uk'
#       },
#       'context_2': {
#           'context_class': {
#               'description': None,
#               'id': None,
#               'name': None
#               },
#           'description': '',
#           'id': UUID('b8d84138-97d1-40fe-a29f-cc3a312b4a0e'),
#           'name': 'English',
#           'name_alfa2': 'en'
#           },
#       'id': UUID('9296f4aa-b3b4-4fa0-b97f-ba90f658f576'),
#       'last_date': datetime.datetime(2023, 1, 5, 13, 8, 44, 783497, tzinfo=datetime.timezone.utc),
#       'user': {
#           'id': UUID('bffc39d2-03d2-46ea-93b9-521a602913e5'),
#           'telegram_user_id': 144371650
#           }
#   }
# ]
