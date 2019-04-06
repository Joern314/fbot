# the glorious demo-bot!

from botpackage.helper import helper
from botpackage.helper.mystrip import _space_chars, normalize_name
from botpackage.helper.split import split_with_quotation_marks


def processMessage(message_object, db_connection):
    # sample bot "!demo arg1 [arg2 ...]"
    # echoes ARG1 with normalized name of caller
    args = split_with_quotation_marks(message_object["message"])
    if len(args) < 1 or args[0].lower() != "!demo":
        return  # not us
    if len(args) is 1:
        # illegal arguments
        return helper.botMessage("usage: !demo arg1 [arg2 ...]", "demo-bot")

    return helper.botMessage(args[1].swapcase(), normalize_name(message_object["name"]))
