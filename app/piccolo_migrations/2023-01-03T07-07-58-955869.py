from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer, Timestamptz
from piccolo.columns.defaults.timestamptz import TimestamptzCustom
from piccolo.columns.indexes import IndexMethod

ID = "2023-01-03T07:07:58:955869"
VERSION = "0.96.0"
DESCRIPTION = "Change and added columns in card-table"


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    manager.add_column(
        table_class_name="Card",
        tablename="card",
        column_name="repetition_level",
        db_column_name="repetition_level",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.rename_column(
        table_class_name="Card",
        tablename="card",
        old_column_name="box_number",
        new_column_name="memorization_stage",
        old_db_column_name="box_number",
        new_db_column_name="memorization_stage",
    )

    manager.alter_column(
        table_class_name="UserContext",
        tablename="user_context",
        column_name="last_date",
        db_column_name="last_date",
        params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=7, second=58, microsecond=926355
            )
        },
        old_params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=11, second=52, microsecond=648056
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamptz,
    )

    return manager
