from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamp, Timestamptz
from piccolo.columns.defaults.timestamp import TimestampCustom
from piccolo.columns.defaults.timestamptz import TimestamptzCustom

ID = "2023-01-02T13:20:52:653636"
VERSION = "0.96.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    manager.alter_column(
        table_class_name="UserContext",
        tablename="user_context",
        column_name="last_date",
        db_column_name="last_date",
        params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=11, second=52, microsecond=648056
            )
        },
        old_params={
            "default": TimestampCustom(
                year=2022,
                month=12,
                day=12,
                hour=18,
                second=41,
                microsecond=869634,
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamp,
    )

    return manager
