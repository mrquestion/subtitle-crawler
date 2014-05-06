# -*- coding: utf-8 -*-

import os

class Log:
	LOGDIR = "log"

	def __init__(self, filename=None, filepath=LOGDIR, error=True):
		self.filename = filename
		self.filepath = filepath
		self.error = error

		self.og = self.print

	def print(self, *args, sep=' ', linesep=True):
		linesep = os.linesep if linesep else ''
		#s = ' '.join(x.decode() if type(x) is bytes else str(x) for x in args)
		#s = ' '.join(str(x) for x in args)
		s = ''
		for arg in args:
			if len(s) == 0:
				if type(arg) == bytes:
					try: s = arg.decode()
					except: s = str(arg)
				elif type(arg) == list:
					s = sep.join(str(x) for x in arg)
				else: s = str(arg)
			else:
				if type(arg) == bytes:
					try: s = sep.join((s, arg.decode()))
					except: s = sep.join((s, str(arg)))
				elif type(arg) == list:
					for x in arg: s = sep.join((s, x))
				else: s = sep.join((s, str(arg)))

		try:
			print(s, end=linesep, flush=True)
		except Exception as e:
			if self.error: print("Error1: {}".format(e))

		if self.filename:
			if not os.path.exists(self.filepath):
				os.makedirs(self.filepath, exist_ok=True)

			filename = "{}{}{}".format(self.filepath, os.sep, self.filename)
			abo = open(filename, "a", newline=linesep)
			try:
				#abo.write(s)
				print(s, file=abo, end=linesep, flush=True)
			except Exception as e:
				if self.error: print("Error2: {}".format(e))
			abo.close() 