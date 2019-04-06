import sqlite3
import parsedatetime
import datetime

from botpackage.helper import helper
from botpackage.helper.mystrip import _space_chars, stripFromBegin, normalize_name
from botpackage.helper.split import split_with_quotation_marks

import varspace.settings as settings

_botname = 'Navi'
_posts_since_ping = 25


def processMessage(message_object, db_connection):
    messages = deliver(message_object, db_connection)

    accept(message_object, db_connection)

    if len(messages) > 0:
        name = message_object['name'].strip(_space_chars)
        total = "%s, dir wollte jemand etwas sagen:" % name
        for msg in messages:
            total += "\n" + msg
        return helper.botMessage(total, _botname)


def deliver(message_object, db_connection):
    cursor = db_connection.cursor()

    if message_object['username'] != None:
        recipientNicks = [normalize_name(message_object['username'])]
    else:
        recipientNicks = [normalize_name(message_object['name'])]

    for nick in cursor.execute(
            'SELECT lower(nickname) '
            'FROM nicknames '
            'WHERE userid = ('
            'SELECT userid '
            'FROM nicknames '
            'WHERE lower(nickname) == ? '
            'ORDER BY deletable DESC'
            ');',
            (recipientNicks[0],)
    ):
        if nick[0].lower() not in recipientNicks:
            recipientNicks.append(nick[0].lower())

    messages = []  # list of all pings

    pingProperties = dict(print=True, delete=True)
    for nick in recipientNicks:
        cursor = db_connection.cursor()
        pongs = cursor.execute(
            'SELECT sender, message, messageid, id '
            'FROM pings '
            'WHERE lower(recipient) == ? '
            ';', (nick.lower(), )
        ).fetchall()
        for pong in pongs:
            if pong[2] + _posts_since_ping > message_object['id']:
                pingProperties['print'] = False
            # ~ pongSplit = split_with_quotation_marks(pong[1])
            # ~ if len(pongSplit) >= 3 \
                # ~ and pongSplit[0].startswith('-') \
                # ~ and pongSplit[0][1:] == 'pong':
                # ~ pongTime = datetime.datetime(*parsedatetime.Calendar().parse(pongSplit[1])[0][:6])
                # ~ if datetime.datetime.now() < pongTime:
                # ~ pingProperties['print'] = False
                # ~ else:
                # ~ pingProperties['delete'] = False

            if pingProperties['print'] == True:
                # if message == None:
                #    message = message_object['name'].strip(
                #        _space_chars) + ', dir wollte jemand etwas sagen:'
                messages.append(pong[0] + ' sagte: ' + pong[1])
            else:
                pingProperties['ping'] = True
            if pingProperties['delete']:
                cursor.execute(
                    'DELETE '
                    'FROM pings '
                    'WHERE id == ? '
                    ';', (pong[3],))
        db_connection.commit()
    return messages


def accept(message_object, db_connection):
    args = split_with_quotation_marks(message_object["message"])

    if len(args) < 1 or args[0].lower() != '!ping':
        return
    if not ''.join(args[2:]).strip(_space_chars) != '':  # wtf is this
        return

    cursor = db_connection.cursor()

    recipient = args[1]
    pingMessage = stripFromBegin(
        message_object['message'], args[0:2]).rstrip(_space_chars)
    sender = message_object['name'].strip(_space_chars)
    messageid = message_object['id']

    pingCount = cursor.execute(
        'SELECT count(*) '
        'FROM pings '
        'WHERE recipient == ? '
        'AND sender == ? '
        ';', (recipient, sender)
    ).fetchone()

    if pingCount[0] == 0 or not settings.overwrite_pings:
        cursor.execute(
            'INSERT OR REPLACE '
            'INTO pings '
            '(recipient, message, sender, messageid) '
            'VALUES (?, ?, ?, ?)'
            ';', (
                recipient,
                pingMessage,
                sender,
                messageid,
            )
        )
    else:
        cursor.execute(
            'UPDATE pings '
            'SET message = ?, messageid = ? '
            'WHERE recipient = ? '
            'AND sender = ?'
            ';', (
                pingMessage,
                messageid,
                recipient,
                sender,
            )
        )
    db_connection.commit()
