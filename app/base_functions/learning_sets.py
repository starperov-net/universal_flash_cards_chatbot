from uuid import UUID
from typing import List, Optional
from tables import Card

async def get_actual_learning_set(
    user_id: UUID,
    context_id: UUID,
    authors: Optional[List[UUID]]
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
    res = await Card.raw("""
        select *
        from card
        where (
        (memorization_stage = 0 AND (card.last_date + interval '5 second') < now()) OR
        (memorization_stage = 1 AND (card.last_date + interval '25 second') < now()) OR
        (memorization_stage = 2 AND (card.last_date + interval '120 second') < now()) OR
        (memorization_stage = 3 AND (card.last_date + interval '600 second') < now()) OR
        (memorization_stage = 4 AND (card.last_date + interval '3600 second') < now()) OR
        (memorization_stage = 5 AND (card.last_date + interval '18000 second') < now()) OR
        (memorization_stage = 6 AND (card.last_date + interval '84600 second') < now())
        ) AND card.user = {}
        ORDER BY memorization_stage, card.last_date;
    """, f"{user_id}")
