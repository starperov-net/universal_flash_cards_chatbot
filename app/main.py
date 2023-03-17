import asyncio
import logging

from aiogram import types

from app.base_functions.translator import translate_client
from app.create_bot import bot, dp
from app.db_functions.personal import get_or_create_user_db
from app.handlers import register_all_handlers
from app.handlers.personal.bot_commands import bot_commands
from app.scheme.transdata import ISO639_1
from app.tables import Context, ContextClass
from app.tests.utils import TELEGRAM_USER_GOOGLE


async def set_default_commands() -> None:
    await bot.set_my_commands(
        [types.BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]
    )


# DELETE FOLLOWING FUNC BEFORE RELEASE
async def add_languages_to_context() -> None:
    cont_name = await Context.select()
    google_languages = translate_client.get_languages()
    if not cont_name:
        for language in google_languages:
            new_language = Context(
                name=language["name"], name_alfa2=language["language"]
            )
            await new_language.save()

    # only for the first running of the bot,
    # to synchronize the data in the 'context' table with Google languages.
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


# DELETE FOLLOWING FUNC BEFORE RELEASE
async def fill_context_class() -> None:
    """
    It must work only one time for filling field context_class
    After some time this function must be deleted
    And we will change properties for field context_class as necessarily
    """
    context_class: ContextClass = await ContextClass.objects().get_or_create(
        (ContextClass.name == "language"),
        defaults={"description": "learning language. language - language"},
    )

    await Context.update({Context.context_class: context_class}).where(
        Context.context_class.is_null()
    )


async def add_user_google() -> None:
    await get_or_create_user_db(TELEGRAM_USER_GOOGLE)


async def on_startup() -> None:
    await set_default_commands()
    await add_user_google()


async def main(logger: logging.Logger) -> None:
    register_all_handlers(dp)
    dp.startup.register(on_startup)
    await dp.start_polling(bot, logger=logger)


if __name__ == "__main__":
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    try:
        logger.info("Bot started")
        asyncio.run(main(logger))

    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
