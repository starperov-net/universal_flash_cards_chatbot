from uuid import UUID
from zoneinfo import ZoneInfo
from typing import List, Optional
from datetime import datetime, timedelta
from app.tables import Card


async def get_actual_card(
    user_id: UUID,
    authors: Optional[List[UUID]],
    interval: timedelta = timedelta(seconds=300),
):
    """
    ideal: this is a generator of which at each step return one actual card
    generator will raise StopIteration when card1s of time are exhausted

    general algorythm:
    https://github.com/starperov-net/universal_flash_cards_chatbot/wiki/Card-selection-algorithm-for-studying%5Crepetition

    input: userid, user_context, author, time(?)
    output: card
    """
    authors_str = (
        ({", ".join(map(lambda x: "'" + str(x) + "'", authors))})
        if authors
        else "'" + str(user_id) + "'"
    )
    query = f"""
    WITH actual_card AS (
        SELECT (
            card.id AS id,
            card.memorization_stage,
            card.repetition_level,
            card.last_date,
            item_1.text AS item_1,
            item_2.text AS item_2
        )
        FROM card
        JOIN item_relation ON card.item_relation = item_relation.id
        JOIN item AS item_1 ON item_1.id = item_relation.item_1
        JOIN item AS item_2 ON item_2.id = item_relation.item_2
        WHERE (
            card.user = '{str(user_id)}' AND
            card.author IN ({authors_str}) AND
            item_1.context IN (
                SELECT context.id
                FROM user_context
                JOIN context ON context.id IN (user_context.context_1, user_context.context_2)
                WHERE user_context.user = '{str(user_id)}'
                ORDER BY last_date DESC
                LIMIT 2) AND
            item_2.context IN (
                SELECT context.id
                FROM user_context
                JOIN context ON context.id IN (user_context.context_1, user_context.context_2)
                WHERE user_context.user = '{str(user_id)}'
                ORDER BY last_date DESC
                LIMIT 2)
        )
    )
    SELECT *
    FROM actual_card
    WHERE
        (
        (memorization_stage = 0 AND (last_date + INTERVAL '5 seconds') < current_timestamp(0)) OR
        (memorization_stage = 1 AND (last_date + INTERVAL '25 seconds') < current_timestamp(0)) OR
        (memorization_stage = 2 AND (last_date + INTERVAL '120 seconds') < current_timestamp(0)) OR
        (memorization_stage = 3 AND (last_date + INTERVAL '600 seconds') < current_timestamp(0)) OR
        (memorization_stage = 4 AND (last_date + INTERVAL '3600 seconds') < current_timestamp(0)) OR
        (memorization_stage = 5 AND (last_date + INTERVAL '18000 seconds') < current_timestamp(0)) OR
        (memorization_stage = 6 AND (last_date + INTERVAL '84600 seconds') < current_timestamp(0))
        )
        OR
        repetition_level IN (0, 1, 2, 3, 4, 5, 6, 7)
        OR
        repetition_level = 8 AND (last_date + INTERVAL '180 days') < current_timestamp(0)
    ORDER BY memorization_stage, repetition_level, last_date
    LIMIT 1;
    """
    start_time = datetime.now(tz=ZoneInfo("UTC"))
    if (start_time + interval) < datetime.now(tz=ZoneInfo("UTC")):
        res = await Card.raw(query)
        res = res[0] if res else res
        yield res
    raise StopIteration
