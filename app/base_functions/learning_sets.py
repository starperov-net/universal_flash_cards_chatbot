from uuid import UUID
from typing import List, Union
from tables import Card

async def get_actual_learning_set(
    user_id: UUID,
    context_id: UUID,
    authors: Union[List[UUID], None]
):
    """
    ideal: this is a generator of which at each step return one actual card
    generator will raise StopIteration when card1s of time are exhausted

    general algorythm: https://github.com/starperov-net/universal_flash_cards_chatbot/wiki/Card-selection-algorithm-for-studying%5Crepetition

    input: userid, user_context, author, time(?)
    output: card
    """
    if not authors:
        authors = [user_id]
    res = await Card.raw(f"""
        SELECT * 
        FROM card
        WHERE card_id = {user_id}
    """)