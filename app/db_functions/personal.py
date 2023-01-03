import datetime
import random
from typing import Optional
from zoneinfo import ZoneInfo
import aiogram

from app.tables import Context, User, UserContext, Item, ItemRelation, Card


async def add_card_db(telegram_user_id: int, item_relation_id: ItemRelation.id, author: int = None) -> Card:
    user: User = await get_user_db(telegram_user_id)
    if author is None:
        author = user
    card: Card = Card(
        user=user,
        item_relation=item_relation_id,
        box_number=1,
        last_date=datetime.datetime.now(tz=ZoneInfo('UTC')),
        repeats_amount=0,
        author=author
    )
    await card.save()
    return card


async def add_item_db(text: str, context: Context.id, author: User.id) -> Item:
    item: Item = Item(
        author=author,
        context=context,
        text=text
    )
    await item.save()
    return item


async def add_item_relation_db(author: User.id, item_1: Item.id, item_2: Item.id) -> ItemRelation:
    item_relation: ItemRelation = ItemRelation(
        author=author,
        item_1=item_1,
        item_2=item_2
    )
    await item_relation.save()
    return item_relation


async def add_user_db(data_telegram: aiogram.types.User) -> User:
    user: User = User(
        telegram_user_id=data_telegram.id,
        telegram_language=data_telegram.language_code or "",
        user_name=data_telegram.username or "",
        first_name=data_telegram.first_name,
        last_name=data_telegram.last_name or "",
    )
    await user.save()
    return user


async def add_user_context_db(data_callback_query, user_db):
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


async def is_exist_item_db(text: str, context: Context.id) -> bool:
    return await Item.exists().where((Item.text == text) & (Item.context == context))


async def is_words_in_card_db(telegram_user_id: int, item_relation_id: ItemRelation.id) -> bool:
    '''
    The function checks if the user already has the item_relation to study.
    '''
    card: list[Card] = await Card.objects().where(
        (Card.user.telegram_user_id == telegram_user_id) &
        (Card.item_relation.id == item_relation_id)
    )
    return bool(card)


async def get_or_create_item_db(text: str, context: Context.id, author: User.id) -> Item:
    item = await Item.objects().get_or_create((Item.text == text) & (Item.context == context),
                                              defaults={'author': author,
                                                        'context': context,
                                                        'text': text})
    return item


async def get_or_create_user_db(data_telegram: aiogram.types.User) -> User:
    user = await User.objects().get_or_create(User.telegram_user_id == data_telegram.id, defaults={
        'telegram_language': data_telegram.language_code or "",
        'user_name': data_telegram.username or "",
        'first_name': data_telegram.first_name,
        'last_name': data_telegram.last_name or ""})
    return user


async def get_context_id_db(name_alfa2: str) -> Context.id:
    context: Context = await Context.objects().get(Context.name_alfa2 == name_alfa2)
    return context.id


async def get_item_relation_by_id_db(item_relation_id: ItemRelation.id) -> ItemRelation:
    item_relation: ItemRelation = await ItemRelation.objects()\
        .get(ItemRelation.id == item_relation_id)
    return item_relation


async def get_item_relation_by_text_db(text: str, telegram_user_id: int, context_1: Context.id, context_2: Context.id) \
        -> ItemRelation:
    '''
    беремо всі переклади авторства юзера чи гугла(telegram_iser_id=0)
    додаемо умову пошуку тільки тих слів, де мови такі ж як і у user_context
    отримали як би "словничок" саме цього юзера
    тепер із цього словничка обираємо записи з співпадінням слів
    відсортовуємо в зворотньому напрямку, щоб першим стояв переклад юзера, а гугла  - в кінці
    беремо перший переклад, тобто переклад юзера.
    '''
    item_relation: ItemRelation = await ItemRelation.objects(ItemRelation.all_related()).where(
        (ItemRelation.author.telegram_user_id.is_in([telegram_user_id, 0])) &
        (ItemRelation.item_1.context.is_in((context_1, context_2))) &
        (ItemRelation.item_2.context.is_in((context_1, context_2)))).where(
        (ItemRelation.item_1.text == text) | (ItemRelation.item_2.text == text)).order_by(
        ItemRelation.author.telegram_user_id, ascending=False).first()
    return item_relation


async def get_list_cards_to_study_db(telegram_user_id: int) -> list[Card]:
    '''
    The function returns a list with up to 10 random user cards.
    '''
    cards: list[Card] = await Card.objects().where(Card.user.telegram_user_id == telegram_user_id)
    k = 10 if len(cards) >= 10 else len(cards)
    cards_10_pcs: list[Card] = random.sample(cards, k)
    return cards_10_pcs


async def get_user_context_db(telegram_user_id: int) -> Optional[UserContext]:
    user_context = (
        await UserContext.objects(UserContext.all_related())
        .get(UserContext.user.telegram_user_id == telegram_user_id)
        .order_by(UserContext.last_date, ascending=False)
        .first()
    )

    return user_context


async def get_user_db(telegram_user_id: int) -> Optional[User]:
    user: Optional[User] = await User.objects(User.all_related()).get(
        User.telegram_user_id == telegram_user_id
    )
    return user


def get_translated_text_from_item_relation(text: str, item_relation: ItemRelation) -> Optional[str]:
    '''
     Із item_relation беру два слова і із них прибираю те слово, яке користувач ввів для перекладу(text),
     значить інше слово і є переклад.
    '''
    text1, text2 = item_relation.item_1.text, item_relation.item_2.text
    translated_text: str = list(set((text1, text2)) - set((text,)))[0]
    return translated_text
