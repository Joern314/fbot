import sqlite3

import botpackage.helper.argparse as argparse
from botpackage.helper import helper
from botpackage.helper.mystrip import normalize_name
from botpackage.helper.split import split_with_quotation_marks

_botname = 'Luise'
_help = '#name nick [-s|-a <int>|-r <int>]'
_unfreie_punkte_liste = ['fp', 'jp', 'op', 'tp']
_unfreie_punkte = ['!' + x for x in _unfreie_punkte_liste]

def processMessage(message_object, db_connection):
	args = split_with_quotation_marks(message_object["message"])
	if len(args) < 2:
		return

	if '' in args[:2]:
		return

	if args[0][0] not in ['#'] and args[0].lower() not in _unfreie_punkte:
		return


	parser = argparse.ArgumentParser()
	parser.add_argument('punktName', metavar='Punkt')
	parser.add_argument('username', metavar='Nick', nargs='?', default='self')
	parser.add_argument('-s', dest='toAdd', action='store_const', const=0)
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-a', dest='toAdd', nargs='?', type=int, default=+1)
	group.add_argument('-r', dest='toAdd', nargs='?', type=negative_int, const=-1)
	try:
		parsedArgs = vars(parser.parse_known_args([x if x != '--' else '-r' for x in args])[0])
	except argparse.ArgumentError:
		return helper.botMessage(str.replace(parser.format_usage(), '\n', ''), _botname)

	if parsedArgs['toAdd'] == None:
		parsedArgs['toAdd'] = 1


	cursor = db_connection.cursor()

	if parsedArgs['username'] in ['self', 'selbst']:
		username = normalize_name(message_object['name'])
	else:
		username = parsedArgs['username']
	userid = helper.useridFromUsername(cursor, username)

	if userid is None:
		return helper.botMessage('Ich kenne %s nicht.'%username, _botname)

	username = helper.usernameFromUserid(cursor, userid)

	punktid = punktidFromPunktName(cursor, args[0])
	punktname = punktNameFromPunktid(cursor, punktid)
	if punktname == None:
		punktname = args[0]
	punktnameToDisplay = punktname[1:]

	anzahl = anzahlFromPunktidAndUserid(cursor, punktid, userid)

	if parsedArgs['toAdd'] == 0:
		if anzahl == None:
			anzahl = 0
		return helper.botMessage(username + ' hat ' + str(anzahl)  + ' ' + punktnameToDisplay + '.', punktnameToDisplay)
	else:
		if punktid is None:
			cursor.execute(
						'INSERT INTO freiepunkteliste (name) VALUES (?);',
						(punktname,)
					)
			punktid = cursor.execute(
						'SELECT id FROM freiepunkteliste WHERE name == ?;',
						(punktname,)
					).fetchone()[0]
		if anzahl is None:
			anzahl = parsedArgs['toAdd']
			cursor.execute(
							'INSERT INTO freiepunkte '
							'(userid, freiepunkteid, anzahl) '
							'VALUES (?, ?, ?) '
							';', (userid, punktid, anzahl)
						)
		else:
			anzahl += parsedArgs['toAdd']
			cursor.execute(
						'UPDATE freiepunkte '
						'SET anzahl = ? '
						'WHERE freiepunkteid = ? '
						'AND userid = ? '
						';', (anzahl, punktid, userid)
					)
		db_connection.commit()
		return helper.botMessage(username + ' hat jetzt ' + str(anzahl)  + ' ' + punktnameToDisplay + '.', punktnameToDisplay)
	return


def punktidFromPunktName(cursor, punktName):
	query = cursor.execute(
				'SELECT id FROM freiepunkteliste WHERE lower(name) = ?;',
				(punktName.lower(),)
			).fetchone()
	return None if query is None else query[0]


def anzahlFromPunktidAndUserid(cursor, punktid, userid):
	if punktid is None:
		return None
	query = cursor.execute(
				'SELECT anzahl '
				'FROM freiepunkte '
				'WHERE freiepunkteid == ? '
				'AND userid == ? '
				';', (punktid, userid,)
			).fetchone()

	return None if query is None else query[0]


def punktNameFromPunktid(cursor, punktid):
	query = cursor.execute(
				'SELECT alias FROM freiepunkteliste WHERE id = ?',
				(punktid,)
			).fetchone()
	if query != None:
		return query[0]
	return None

def negative_int(i):
	return -int(i)
