from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from app.base_functions.translator import translate_client
from app.scheme.transdata import ISO639_1
from app.tables import Context, ContextClass

ID = "2023-03-14T22:59:42:587824"
VERSION = "0.96.0"
DESCRIPTION = "filling Context table with context_class, name and name_alfa2 values"

async def forwards() -> MigrationManager:
    manager = MigrationManager(migration_id=ID, app_name="app", description=DESCRIPTION)

    async def run() -> None:
        cont_name = await Context.select()
        google_languages = translate_client.get_languages()
        if not cont_name:
            for language in google_languages:
                new_language = Context(
                    name=language["name"], name_alfa2=language["language"]
                )
                await new_language.save()

        elif cont_name and len(cont_name) == len(ISO639_1):
            google_names_alfa2 = [i["language"] for i in google_languages]
            for i in cont_name:
                if i["name_alfa2"] in google_names_alfa2:
                    google_names_alfa2.remove(i["name_alfa2"])
                else:
                    await Context.delete().where(Context.id == i["id"])

            for j in google_languages:
                if j["language"] in google_names_alfa2:
                    new_language = Context(name=j["name"], name_alfa2=j["language"])
                    await new_language.save()

        context_class: ContextClass = await ContextClass.objects().get_or_create(
            (ContextClass.name == "language"),
            defaults={"description": "learning language. language - language"},
        )

        await Context.update({Context.context_class: context_class}).where(
            Context.context_class.is_null()
        )

    manager.add_raw(run)

    return manager
