from typing import List, Any

from app.tables import Card


async def get_list_of_words(
    telegram_user_id: int, max_repetition_level: int = 8
) -> List[Any]:
    """
    fuction return all cards of user, sorted by learning_status and alphabet
    learning_status  counted by repetition_level
    repetition_level = 8  -> learning_status_code = 0 , learning_status = 'learned'
    repetition_level = between 1 and 7  -> learning_status_code = 1 , learning_status = 'in progress'
    repetition_level = 0  -> learning_status_code = 2 , learning_status = 'unstudied'

    returned dictionaries contain
    {'card_id': UUID,
    'foreign_word': str = item where context equals foreign language (user_context.context_2),
    'native_word': str = item where context equals native language (user_context.context_1),
    'learning_status_code': int any[0,1,2],
    'learning_status': str any['learned', 'in progress', 'unstudied']
    """

    query: str = create_select_for_list_of_words(telegram_user_id, max_repetition_level)
    res: List[dict] = await Card.raw(query)
    return res


def create_select_for_list_of_words(
    telegram_user_id: int, max_repetition_level: int
) -> str:
    """
    Create row query.
    Moved to separate function for cleanliness code
    """

    query: str = f"""
        SELECT  card.id as card_id,
                CASE WHEN item1.context = user_context.context_2
                    THEN item1.text
                    ELSE item2.text
                END AS foreign_word,
                CASE WHEN item2.context = user_context.context_1
                    THEN item2.text
                    ELSE item1.text
                END AS native_word,
                CASE WHEN repetition_level = {max_repetition_level}
                    THEN 0
                    WHEN repetition_level = 0
                    THEN 2
                    ELSE 1
                END AS learning_status_code,
                CASE WHEN repetition_level = {max_repetition_level}
                    THEN 'learned'
                    WHEN repetition_level = 0
                    THEN 'unstudied'
                    ELSE 'in progress'
                END AS learning_status
        FROM card
        INNER JOIN users ON card.user = users.id
        INNER JOIN item_relation ON card.item_relation = item_relation.id
        INNER JOIN item AS item1 ON item_relation.item_1 = item1.id
        INNER JOIN item AS item2 ON item_relation.item_2 = item2.id
        INNER JOIN user_context ON users.id = user_context.user
        WHERE users.telegram_user_id = {telegram_user_id} AND
            user_context.last_date = (SELECT MAX(last_date)
                                        FROM user_context
                                        INNER JOIN users ON user_context.user = users.id
                                        WHERE users.telegram_user_id = {telegram_user_id})
        ORDER BY learning_status_code, foreign_word;
        """
    return query
