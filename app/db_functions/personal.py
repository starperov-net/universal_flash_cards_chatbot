from typing import Optional

import aiogram

from app.tables import Context, User, UserContext, Item, ItemRelation


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
    last_name: Optional[str] = data_telegram.last_name
    user: User = User(
        telegram_user_id=data_telegram.id,
        telegram_language=data_telegram.language_code or "",
        user_name=data_telegram.username or "",
        first_name=data_telegram.first_name,
        last_name=last_name or "",
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


async def get_user_context_db(telegram_user_id) -> Optional[UserContext]:
    user_context = (
        await UserContext.objects(UserContext.all_related())
        .get(UserContext.user.telegram_user_id == telegram_user_id)
        .order_by(UserContext.last_date, ascending=False)
        .first()
    )

    return user_context


async def get_user_db(data_telegram: aiogram.types.User) -> Optional[User]:
    user: Optional[User] = await User.objects(User.all_related()).get(
        User.telegram_user_id == data_telegram.id
    )
    return user


async def get_translated_word_db(word: str, telegram_user_id, ) -> Optional[tuple[str]]:
    '''
     беремо всі переклади авторства юзера чи гугла(telegram_iser_id=0)
     додаемо умову пошуку тільки тих слів, де мови такі ж як і у user_context
     отримали як би "словничок" саме цього юзера
     тепер із цього словничка обираємо записи з співпадінням слів
     відсортовуємо в зворотньому напрямку, щоб першим стояв переклад юзера, а гугла  - в кінці
      беремо перший переклад, тобто переклад юзера.

     потім з отриманого запису беру два слова і із них прибираю те слово, по якому шукали
     значить інше слово і є переклад
    '''
    user_context: UserContext = await get_user_context_db(telegram_user_id)
    translation: ItemRelation = await ItemRelation.objects(ItemRelation.all_related()).where(
        (ItemRelation.author.telegram_user_id.is_in([telegram_user_id, 0])) &
        (ItemRelation.item_1.context.is_in((user_context.context_1, user_context.context_2))) &
        (ItemRelation.item_2.context.is_in((user_context.context_1, user_context.context_2)))).where(
        (ItemRelation.item_1.text == word) | (ItemRelation.item_2.text == word)).order_by(
        ItemRelation.author.telegram_user_id, ascending=False).first()

    if translation:
        word1, word2 = translation.item_1.text, translation.item_2.text
        translated_word: str = list(set((word1, word2)) - set((word,)))[0]
        return translated_word

    return None
