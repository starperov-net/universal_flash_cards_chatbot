from piccolo.columns.column_types import (
    UUID,
    BigInt,
    Boolean,
    ForeignKey,
    Integer,
    Text,
    Timestamptz,
    Varchar,
)
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.table import Table


class User(Table, tablename="users"):
    id = UUID(primary_key=True)
    telegram_user_id = BigInt(unique=True)
    telegram_language = Varchar()
    user_name = Varchar()
    first_name = Varchar()
    last_name = Varchar()


class ContextClass(Table):
    id = UUID(primary_key=True)
    description = Text()
    name = Varchar()  # TODO: add attribute unique=True


class Context(Table):
    id = UUID(primary_key=True)
    context_class = ForeignKey(references=ContextClass)
    name = Varchar()
    name_alfa2 = Varchar()
    description = Text()


class UserContext(Table):
    id = UUID(primary_key=True)
    context_1 = ForeignKey(references=Context)
    context_2 = ForeignKey(references=Context)
    user = ForeignKey(references=User)
    last_date = Timestamptz(default=TimestamptzNow)  # type:ignore
    active = Boolean(default=True)


class Item(Table):
    id = UUID(primary_key=True)
    author = ForeignKey(references=User)
    context = ForeignKey(references=Context)
    text = Text()


class ItemRelation(Table):
    id = UUID(primary_key=True)
    author = ForeignKey(references=User)
    item_1 = ForeignKey(references=Item)
    item_2 = ForeignKey(references=Item)


class Card(Table):
    id = UUID(primary_key=True)
    user = ForeignKey(references=User)
    item_relation = ForeignKey(references=ItemRelation)
    repetition_level = Integer(default=0)
    memorization_stage = Integer(default=0)
    last_date = Timestamptz(default=TimestamptzNow)  # type:ignore
    author = ForeignKey(references=User)


class Help(Table):
    id = UUID(primary_key=True)
    state = Varchar()
    help_text = Text()
    language = ForeignKey(references=Context)
