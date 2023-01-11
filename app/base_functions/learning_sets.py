# mypy: allow-untyped-defs
from uuid import UUID
from zoneinfo import ZoneInfo
from typing import List, Optional, AsyncGenerator
from datetime import datetime, timedelta
from app.tables import Card
from app import serializers
from app.db_functions.personal import update_card_db


async def set_res_studying_card(
    current_card_status: serializers.Card, result: bool
) -> None:
    if (
        current_card_status.repetition_level is None
        or current_card_status.memorization_stage is None
    ):
        raise ValueError(
            "'repetition_level' and 'memorisation_stage' attributes cannot be None for 'current_card_status'"
        )
    if result:
        repetition_level = (
            current_card_status.repetition_level + 1
            if current_card_status.repetition_level < 8
            else 8
        )
    else:
        repetition_level = (
            current_card_status.repetition_level - 1
            if current_card_status.repetition_level > 0
            else 0
        )
    memorisation_stage = (
        current_card_status.memorization_stage + 1
        if current_card_status.memorization_stage < 7
        else 7
    )
    last_date = datetime.now(tz=ZoneInfo("UTC"))

    card_data = serializers.Card(
        id=current_card_status.id,
        last_date=last_date,
        memorization_stage=memorisation_stage,
        repetition_level=repetition_level,
    )
    await update_card_db(card_data)


async def get_actual_card(
    user_id: UUID,
    authors: Optional[List[UUID]] = None,
    interval: timedelta = timedelta(seconds=300),
) -> AsyncGenerator:
    """
    this is a generator of which at each step return one actual card
    generator will raise StopIteration when card1s of time are exhausted

    general algorythm:
    https://github.com/starperov-net/universal_flash_cards_chatbot/wiki/Card-selection-algorithm-for-studying%5Crepetition

    input: userid (UUID) - obligatory, authors (list(UUID)) - optional, interval (timedelta) - optional
    output: all data for last usercontext
        dict {
            'id': UUID (for actual Card),
            'memorization_stage': int (for actual Card),
            'repetition_level': int (for actual Card),
            'last_date': datetime (for actual Card),
            'item_1': str,
            'item_2': str,
            #######################
            'context_item_1': UUID,
            'context_item_2': UUID
    }
    """
    authors_str = (
        ({", ".join(map(lambda x: "'" + str(x) + "'", authors))})
        if authors
        else "'" + str(user_id) + "'"
    )
    query = f"""
    WITH actual_card AS (
        SELECT
            card.id AS id,
            card.memorization_stage,
            card.repetition_level,
            card.last_date,
            item_1.text AS item_1,
            item_2.text AS item_2,
            item_1.context AS context_item_1,
            item_2.context AS context_item_2
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
    while (start_time + interval) > datetime.now(tz=ZoneInfo("UTC")):
        res = await Card.raw(query)
        if not res:
            break
        yield res[0]  # type: ignore
    raise StopIteration
