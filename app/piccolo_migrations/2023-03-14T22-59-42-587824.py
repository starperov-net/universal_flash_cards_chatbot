from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from app.base_functions.translator import translate_client
from app.tables import Context, ContextClass

ID = "2023-03-14T22:59:42:587824"
VERSION = "0.96.0"
DESCRIPTION = "filling Context table with context_class, name and name_alfa2 values"

google_languages = translate_client.get_languages()


async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    async def run() -> None:
        context_class = ContextClass(
            description="learning language. language - language", name="language"
        )
        await context_class.save()

        cont_class: ContextClass = await ContextClass.objects().get(
            ContextClass.name == "language"
        )

        for language in google_languages:
            new_language = Context(
                context_class=cont_class,
                name=language["name"],
                name_alfa2=language["language"],
            )
            await new_language.save()

    manager.add_raw(run)

    return manager
