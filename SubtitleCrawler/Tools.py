# -*- coding: utf-8 -*-

import time
from datetime import datetime as dt
import hashlib
import inspect
import pprint

def logo(s="Please Input Logo Text"):
	s = str(s)
	border = ''.join('=' for i in range(0, len(s)+2))
	print(border)
	print(" {} ".format(s))
	print(border)
	print()

def getlogo(s="Please Input Logo Text"):
	border = ''.join('=' for i in range(0, len(s)+2))
	logo = [ border, " {} ".format(str(s)), border, '' ]
	return logo

def timestamp(format="%Y%m%d-%H%M%S"):
	now = dt.fromtimestamp(time.time()).strftime(format)
	return now

def md5(s):
	md5 = hashlib.md5(s.encode("utf-8"))
	s = md5.hexdigest()
	return s

def normalize(s, encoding="utf-8", ascii=b'_', filename=False):
	bs = s if type(s) is bytes else s.encode(encoding)
	if type(ascii) is str: ascii = ascii.encode("ascii")
	if len(ascii) == 0: ascii = b'_'

	if not check(s, error=False):
		ba = bytearray()
		for b in bs: ba.append(ord(ascii) if b > 127 else b)
		bs = bytes(ba)

	if filename:
		for c in "\\/:*?\"<>|":
			bs = bs.replace(c.encode("ascii"), ascii)

	if type(s) is bytes: s = bs
	elif type(s) is str: s = bs.decode(encoding)
	return s

def check(s, error=True):
	try:
		stdout = os.dup(1)
		wo = open("Tools.temp", "wb")
		os.dup2(wo.fileno(), 1)
		print(s)
		os.dup2(stdout, 1)
		wo.close()
		return True
	except:
		if error: raise
		else: return False

def pp(s): pprint.PrettyPrinter(indent=4).pprint(s)
def mems(o): return inspect.getmembers(o)
def args(f): return inspect.getargspec(f)