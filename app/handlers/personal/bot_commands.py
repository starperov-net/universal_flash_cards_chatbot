# <command name> <command description> <command number>
# Attention! <command number> is determined in order and once,
# because there is a link to it in help.py (for rendering text).
# And it is also used in main.py for building the menu commands.
bot_commands: tuple = (
    ("start", "start", 0),
    ("study", "study", 1),
    ("selftest", "self-test", 2),
    ("mywords", "my-words", 3),
    ("help", "help", 4),
    ("cancel", "cancel", 5),
)
