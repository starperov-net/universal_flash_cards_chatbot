from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from app.tables import Help

ID = "2023-03-06T23:24:55:361452"
VERSION = "0.96.0"
DESCRIPTION = "Fill in basic help description for states in the <Help> table"

study_text = """
-study-

by choosing this mode, the user gets the opportunity to study his words,
receiving, according to the memorization algorithm, some word for memorization
and four translation options, one of which is correct. By choosing one of the
proposed translation options, the user will receive feedback on the status of
his choice. The correctness or incorrectness of the selected option affects
the intervals in learning for the word being checked.
"""




async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="", description=DESCRIPTION
    )

    async def run() -> None:
        await Help.update(
            {
                Help.state: "study",
                Help.help_text: study_text,
            }
        )

    manager.add_raw(run)

    return manager
