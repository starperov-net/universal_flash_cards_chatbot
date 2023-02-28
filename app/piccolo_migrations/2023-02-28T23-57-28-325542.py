from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-02-28T23:57:28:325542"
VERSION = "0.96.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    def run():
        print(f"running {ID}")

    manager.add_raw(run)

    return manager
