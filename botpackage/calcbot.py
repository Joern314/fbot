import botpackage.helper.calc as calc
import botpackage.helper.timeout as timeout
from botpackage.helper import helper
from botpackage.helper.mystrip import stripFromBegin, _space_chars
from botpackage.helper.split import split_with_quotation_marks

_botname = '۞'
_bottrigger = 'calc'
_help = '%s <mathematischer Ausdruck>' % _bottrigger


def processMessage(message_object, db_connection):
    if True: #deactivated
        return

    args = split_with_quotation_marks(message_object["message"])
    if len(args) < 1 or args[0].lower() != "!" + _bottrigger:
        return

    expr = stripFromBegin(message_object["message"], [
                          "!" + _bottrigger]).strip(_space_chars)

    ret = timeout.timed_run(calc.evaluate, [expr])

    if isinstance(ret, Exception):
        return helper.botMessage("Ein Fehler trat auf: %s" % ret, _botname)
    elif ret is None:
        return helper.botMessage("Die Evaluierung dauerte zu lange.", _botname)
    else:
        return helper.botMessage("%s" % ret, _botname)
