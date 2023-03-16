from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from app.tables import Context, Help

ID = "2023-03-14T23:11:54:507314"
VERSION = "0.96.0"
DESCRIPTION = "filling in basic help descriptions for states in the <Help> table"

native_language_state = {
    "state_name": "FSMChooseLanguage:native_language",
    "state_description": "the bot is waiting for your native language to be entered by you",
}

target_language_state = {
    "state_name": "FSMChooseLanguage:target_language",
    "state_description": "the bot is waiting for you to enter the language in which you "
    "want to receive the translation of words",
}

studying_one_from_four_state = {
    "state_name": "FSMStudyOneFromFour:studying",
    "state_description": "{_1} by choosing this mode, a user gets an opportunity to study his words, receiving, "
    "according to the memorization algorithm, some word for memorization and four translation options, one of "
    "which is correct. By choosing one of the proposed translation options, the user will receive feedback on "
    "the status of his choice. The correctness or incorrectness of the selected option affects the intervals "
    "in learning for the word being checked.",
}

custom_translation_state = {
    "state_name": "FSMCustomTranslation:custom_translation",
    "state_description": "the bot is waiting for your custom translation of the word you are working with",
}

my_words_state = {
    "state_name": "FSMMyWords:mywords",
    "state_description": "{_3} by choosing this mode, a user gets an opportunity to get acquainted with a list "
    "of words in the translation of which he was interested and added for study. An additional functionality of "
    "this mode is the ability to delete words unnecessary to the user",
}

self_test_state = {
    "state_name": "FSMSelfTest:selftest",
    "state_description": "{_2} by choosing this mode, a user gets an opportunity to check himself for knowledge "
    "of the translation of the proposed word. In an interface, the user will be prompted for the word and its "
    "hidden translation. The user notes whether he knows the translation or not and at any stage can open "
    "a hidden translation for self-checking.",
}

none_state = {
    "state_name": "None",
    "state_description": """
Using this bot, a user can translate words or short phrases in the Google Translate functionality, save them for \
study and subsequent self-examination.
The bot menu provides access to the following modes of operation:
{_0} - start working with the bot
{_1} - study and test knowledge of the user's words
{_2} - self-checking the user's words
{_3} - access to the list of user words with the ability to delete unnecessary words
{_4} - getting general help or help in a certain mode of this bot
{_5} - the user gets the opportunity to finish the work being in any of the modes and return to the mode {_0}
    """,
}

states_list = [
    native_language_state,
    target_language_state,
    studying_one_from_four_state,
    custom_translation_state,
    my_words_state,
    self_test_state,
    none_state,
]


async def forwards() -> MigrationManager:
    english_context = await Context.objects().get(Context.name_alfa2 == "en")

    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    async def run() -> None:
        for state_info in states_list:
            new_help = Help(
                state=state_info["state_name"],
                help_text=state_info["state_description"],
                language=english_context.id,
            )
            await new_help.save()

    manager.add_raw(run)

    return manager
