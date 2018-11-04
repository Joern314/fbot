from botpackage.helper import helper

from ctypes import cdll
lib = cdll.LoadLibrary('./botpackage/manu/libmanu.so')

class Manu(object):
	def __init__ (self):
		self.obj = lib.Foo_new()
	def bar(self):
		lib.Foo_bar(self.obj)

_botname = 'anonymous grammar nazi'

def processMessage(args, rawMessage, db_connection):
	f = Manu()
	f.bar()
