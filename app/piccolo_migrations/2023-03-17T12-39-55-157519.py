from typing import Any

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2023-03-17T12:39:55:157519"
VERSION = "0.96.0"
DESCRIPTION = (
    "Clearing the migration table and deleting the rest of the existing tables."
)


# This is just a dummy table we use to execute raw SQL with:
class RawTable(Table):
    pass


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    async def run() -> None:
        app_tables: tuple = (
            "help",
            "context_class",
            "context",
            "users",
            "item",
            "item_relation",
            "card",
            "user_context",
        )
        existing_tables: list[Any] = await RawTable.raw(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public';"
        )
        for table in existing_tables:
            table_name: str = table["table_name"]
            if table_name in app_tables:
                await RawTable.raw(f"DROP TABLE {table_name} CASCADE;")
            if table_name == "migration":
                await RawTable.raw(f"TRUNCATE TABLE {table_name};")

    manager.add_raw(run)

    return manager
