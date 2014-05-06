# -*- coding: utf-8 -*-

import json
import re as regex
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes
from abc import ABCMeta as abstractmeta, abstractmethod

from .. import Tools
from ..Log import Log as L

class Blog:
	def __init__(self, savedir=None, log=None):
		if not savedir:
			self.time = Tools.timestamp()
			savedir = os.sep.join((basedir, self.time))
			if not os.path.exists(savedir):
				os.makedirs(savedir, exist_ok=True)
		self.savedir = savedir

		self.list = []
		self.l = log if log else L(filename="{}.log".format(Tools.timestamp()))

	def adds(self, blogs):
		if type(blogs) is list or type(blogs) is tuple:
			for blog in blogs: self.add(blog)
		elif type(blogs) is type or type(blogs) is abstractmeta: self.add(blog)

	def add(self, blog):
		if not self.list: self.list = []
		if (type(blog) is type or type(blog) is abstractmeta) and not blog in self.list: self.list.append(blog(log=self.l))

	def parse(self, url):
		l = self.l

		bps = key = name = None

		found = False
		for blog in self.list:
			if type(url) is str and blog.URL.match(url):
				found = True
			if type(url) is dict and blog.KEY in url:
				found = True
				if "NAME" in url: name = url["NAME"]
				url = url[blog.KEY]
			if found:
				key = blog.KEY
				bps = []
				iter = blog.search(url)
				for x in iter: bps = bps + x;
				break

		if not found:
			l.og("Error: Not supported {} URL".format(", ".join("'{}'".format(blog.KEY) for blog in self.list)))
			l.og("\t{}".format(unquote(url)))
			'''
		if type(url) is str:
			for blog in self.list:
				if blog.URL.match(url):
					key = blog.KEY
					bps = []
					bps = blog.search(url)
					for x in iter: bps = bps + x
					break
		elif type(url) is dict:
			for blog in self.list:
				if blog.KEY in url:
					key = blog.KEY
					url = url[blog.KEY]
					bps = []
					iter = blog.search(url)
					for x in iter: bps = bps + x
					break
					'''
		return bps, key, url, name
	'''
	def download(self, bp):
		filename = bp.filename
		headers = { "User-Agent": "Mozilla AppleWebKit Chrome Safari" }
		headers = None
		response = requests.get(bp.file, headers=headers)
		if response.ok:
			if not filename:
				headers = response.headers
				if "Content-disposition" in headers:
					content_disposition = headers["Content-disposition"]
					matched = self.CONTENT_REGEX.match(content_disposition)
					if matched: filename = matched.group(1)

			if not filename:
				parsed = urlparse(bp.file)
				paths = parsed.path.split('/')
				filename = paths[-1]

			if filename:
				try: filename = unquote_to_bytes(filename).decode("utf-8")
				except:
					try: filename = unquote_to_bytes(filename).decode("euc-kr")
					except:
				print(unquote_to_bytes(filename).decode("euc-kr"))
				'''

class BlogAbstract(metaclass=abstractmeta):
	EXTENSIONS = [
		"smi", "srt", "ass", "sub", "sup",
		"zip", "rar", "7z", "ace", "alz", "egg",
		"lha", "lzh",
		"tar", "gz", "tgz", "bz", "bz2", "tbz", "tbz2",
		"lzma",
		"txt"
	]
	EXTENSION_REGEX = regex.compile(r".*/(([^/]+)\.({}))".format(r"|".join(EXTENSIONS)))

	@abstractmethod
	def __init__(self, log=None):
		self.l = log if log else L(filename="{}-{}.log".format(self.KEY, Tools.timestamp()))

	@abstractmethod
	def search(self): pass
	
class BlogProperty:
	def __init__(self, key=None, category=None, post=None, file=None, filename=None):
		self.key = key
		self.category = category
		self.post = post
		self.file = file
		self.filename = filename