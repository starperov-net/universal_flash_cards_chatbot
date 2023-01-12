from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.defaults.timestamptz import TimestamptzCustom
from piccolo.columns.defaults.timestamptz import TimestamptzNow


ID = "2023-01-03T23:49:04:746014"
VERSION = "0.96.0"
DESCRIPTION = "Change Card(Table): deleted fields box_number, repeats_amount and added fefault value in last_date"


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    manager.drop_column(
        table_class_name="Card",
        tablename="card",
        column_name="repeats_amount",
        db_column_name="repeats_amount",
    )

    manager.alter_column(
        table_class_name="Card",
        tablename="card",
        column_name="last_date",
        db_column_name="last_date",
        params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=21, second=4, microsecond=744608
            )
        },
        old_params={"default": TimestamptzNow()},
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
                year=2023, month=1, day=1, hour=21, second=4, microsecond=741624
            )
        },
        old_params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=7, second=58, microsecond=926355
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamptz,
    )

    return manager
