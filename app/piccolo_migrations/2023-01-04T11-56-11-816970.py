from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.defaults.timestamptz import TimestamptzCustom
from piccolo.columns.defaults.timestamptz import TimestamptzNow


ID = "2023-01-04T11:56:11:816970"
VERSION = "0.96.0"
DESCRIPTION = "attempt to create a dynamic default parameter using ORM - for table UserContext"


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="app", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="UserContext",
        tablename="user_context",
        column_name="last_date",
        db_column_name="last_date",
        params={"default": TimestamptzNow},
        old_params={
            "default": TimestamptzCustom(
                year=2023, month=1, day=1, hour=11, second=36, microsecond=14765
            )
        },
        column_class=Timestamptz,
        old_column_class=Timestamptz,
    )

    return manager
