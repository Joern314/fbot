#!/usr/bin/env python

import requests # http requests
import websocket # websocket connections
import sqlite3 # database

# system libraries
import json # encode and decode websocket-traffic
import argparse # command line start of fbot
import threading # lock
import time # sleep()

from varspace.settings import *
import botpackage

from botpackage.helper.mystrip import _space_chars, stripFromBegin
from botpackage.helper.split import split_with_quotation_marks

#global variables
args = None
db_connection = sqlite3.connect('varspace/fbotdb.sqlite')

def on_close(ws): #callback
	print('ws closed')

def on_error(ws, error): #callback
	print('ws error: ' + error)

def on_message(ws, message_string): #callback
	message_object = json.loads(message_string)
	print('received', repr(message_object['message']))
	if int(message_object['bottag']) != 0:
		return #guarantee to ignore posts with bottag

	for bot in botpackage.__all__: #iteriert über alle dateien im subdirectory ./botpackage
		answer = bot.processMessage(message_object, db_connection)
		if answer is not None:
			if not is_rate_limited(ws, message_object['id'], bot, answer):
				send(ws, answer['name'], answer['message'], message_object['id'] + 1)
			else:
				continue #todo: add warning

def is_rate_limited(ws, message_id, bot, answer):
	#todo: implement a good ratelimiter
	return False

def send(ws, name, message, delay=0):
	message_object = dict(
		name = name,
		message = message,
		delay = delay,
		publicid = '1', #todo: why string?
		bottag = 1
	)
	message_string = json.dumps(message_object)
	with sending_lock: #todo: is single-threading really not guaranteed?
		ws.send(message_string)

def getCookies():
	#login into chat, retry on error
	while True:
		try:
			req = requests.post('https://chat.qed-verein.de/rubychat/account', 	data=credentials)
		except ConnectionResetError as e:
			print('Error while downloading cookies:', e)
		else:
			return req.cookies
		time.sleep(1) # todo: why? while True with multi-threading? freezing the system?

def create_ws(cookies, channel):
	#open a new ws for a specific channel
	try:
		cookies['userid']
		cookies['pwhash']
	except AttributeError:
		print('cookies not right')
		return

	ws = websocket.WebSocketApp('wss://chat.qed-verein.de/websocket?channel=' + channel + '&position=-0&version=2',
			cookie = format_cookies(dict(
						userid = cookies['userid'],
						pwhash = cookies['pwhash'],
					)),
			on_message = on_message,
			on_error = on_error,
			on_close = on_close,
			)
	return ws


def format_cookies(obj):
	#utility function
	retval = ''
	for key in obj:
		retval += key + '=' + obj[key] + ';'
	return retval


def mainloop(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--interactive', action='store_true')
	parser.add_argument('--channel', default='fbot')
	parser.add_argument('--mainchannel-on-my-own-risk', action='store_true')
	parsedArgs = vars(parser.parse_args())

	if parsedArgs['interactive'] == True:
		print('fbot interactive mode. first word will be used as nick')
		eiDii = 0
		while True:
			eiDii += 1
			try:
				inp = input('> ')
			except EOFError:
				exit(0)
			except:
				raise
			inpSplit = split_with_quotation_marks(inp)
			message = {
				'name': ''.join(inpSplit[:1]),
				'username' : None,
				'message': stripFromBegin(inp, inpSplit[:1]),
				'id' : eiDii,
			}
			#todo: logic not the same, instead create a fake ws-connection. or better: internal server eg with docker from Lukas
			for bot in botpackage.__all__:
				x = bot.processMessage(inpSplit[1:], message, db_connection)
				if x is not None:
					print(repr(x['name']), ':', repr(x['message']))
			print()

	if parsedArgs['mainchannel_on_my_own_risk'] == True:
		parsedArgs['channel'] = ''
	cookies = getCookies()
	while True:
		print('creating new websocket')
		ws = create_ws(cookies, parsedArgs['channel'])
		if ws:
			ws.run_forever() #async? why create new ones all the time? todo: read websocket library api
		time.sleep(1) # todo: magic number 1, how does reconenct work etc?

if __name__ == '__main__':
	sending_lock = threading.Lock()

	try:
		mainloop(args)
	except KeyboardInterrupt:
		pass
