from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamp, Timestamptz
from piccolo.columns.defaults.timestamp import TimestampCustom, TimestampNow
from piccolo.columns.defaults.timestamptz import TimestamptzNow

ID = "2022-12-28T18:14:41:874701"
VERSION = "0.96.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    manager.alter_column(
        table_class_name="Card",
        tablename="card",
        column_name="last_date",
        db_column_name="last_date",
        params={"default": TimestamptzNow()},
        old_params={"default": TimestampNow()},
        column_class=Timestamptz,
        old_column_class=Timestamp,
    )

    manager.alter_column(
        table_class_name="UserContext",
        tablename="user_context",
        column_name="last_date",
        db_column_name="last_date",
        params={
            "default": TimestampCustom(
                year=2022,
                month=12,
                day=12,
                hour=18,
                second=41,
                microsecond=869634,
            )
        },
        old_params={
            "default": TimestampCustom(
                year=2022,
                month=12,
                day=12,
                hour=20,
                second=41,
                microsecond=295362,
            )
        },
        column_class=Timestamp,
        old_column_class=Timestamp,
    )

    return manager
