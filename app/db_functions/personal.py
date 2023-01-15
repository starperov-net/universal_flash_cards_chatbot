import random
from typing import Optional, Any, Union

from uuid import UUID

import aiogram
import piccolo

from app.exceptions.custom_exceptions import NotFullSetException
from app.tables import Context, User, UserContext, Item, ItemRelation, Card
from app import serializers


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


async def get_list_cards_to_study_db(telegram_user_id: int) -> list[Card]:
    """
    The function returns a list with up to 10 random user cards.
    """
    # # OLD
    # cards: list[Card] = await Card.objects().where(
    #     Card.user.telegram_user_id == telegram_user_id
    # )
    # NEW
    cards: list[Card] = await Card.objects(Card.all_related()).where(
        Card.user.telegram_user_id == telegram_user_id
    )
    k = 10 if len(cards) >= 10 else len(cards)
    cards_10_pcs: list[Card] = random.sample(cards, k)
    return cards_10_pcs


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


async def get_user_id_db(telegram_user_id: int) -> Optional[UUID]:
    user: Optional[User] = await User.objects().get(
        User.telegram_user_id == telegram_user_id
    )
    return user.id if user else None


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


async def get_three_random_words(context_id: UUID) -> list[dict]:
    """Return dict like """
    query = f"""
    SELECT i.text
    FROM item i
    WHERE(i.context='{str(context_id)}')
    ORDER BY random()
    ASC
    LIMIT 3;
    """
    random_words: list[dict] = await Item.raw(query)
    if len(random_words) < 3:
        raise NotFullSetException
    return random_words
