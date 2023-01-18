from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.defaults.timestamptz import (TimestamptzCustom,
                                                  TimestamptzNow)

ID = "2023-01-04T11:48:36:040051"
VERSION = "0.96.0"
DESCRIPTION = "attempt to create a dynamic default parameter using ORM"


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    manager.alter_column(
        table_class_name="Card",
        tablename="card",
        column_name="last_date",
        db_column_name="last_date",
        params={"default": TimestamptzNow},
        old_params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=21, second=4, microsecond=744608
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamptz,
    )

    manager.alter_column(
        table_class_name="UserContext",
        tablename="user_context",
        column_name="last_date",
        db_column_name="last_date",
        params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=11, second=36, microsecond=14765
            )
        },
        old_params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=21, second=4, microsecond=741624
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamptz,
    )

    return manager
