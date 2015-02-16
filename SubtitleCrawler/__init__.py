# -*- coding: utf-8 -*-

import os
import time
import json
import re as regex
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes
import subprocess as sp
import multiprocessing as mp

from . import Tools
from .Log import Log as L
from .DatabaseManager import DatabaseManager

class SubtitleCrawler:
	BASEDIR = "crawled"
	NAME = "crawled"
	WORDFILE = "crawl-url.json"

	CONTENT_REGEX = regex.compile(".*filename=\"?([^\"]*)\"?;?.*")

	def __init__(self, basedir=BASEDIR, savedir=None, dm=None, log=None):
		mp.freeze_support()

		if not os.path.exists(basedir):
			os.mkdir(basedir)

		if not savedir:
			self.time = Tools.timestamp()
			savedir = os.sep.join((basedir, self.time))
			if not os.path.exists(savedir):
				os.makedirs(savedir, exist_ok=True)
		self.savedir = savedir
		
		if dm: self.dm = dm
		else: self.dm = DatabaseManager(self.NAME)

		l = self.l = log if log else L(filename="{}.log".format(self.NAME), filepath=savedir)

	def words(self, filename=WORDFILE):
		l = self.l

		self.filename = filename

		urls = None
		if os.path.exists(filename):
			ro = open(filename, "r")
			try:
				urls = json.loads(ro.read())
			except Exception as e:
				l.og("Error: json.loads()")
				l.og("\t{}".format(e))
		return urls

	def download(self, key, category, post, file, filename):
		l = self.l

		headers = { "User-Agent": "Mozilla AppleWebKit Chrome Safari" }
		headers = None
		response = requests.get(file, headers=headers)
		if response.ok:
			content = response.content

			if not filename:
				headers = response.headers
				if "Content-disposition" in headers:
					content_disposition = headers["Content-disposition"]
					matched = self.CONTENT_REGEX.match(content_disposition)
					if matched: filename = matched.group(1)

			if not filename:
				parsed = urlparse(file)
				paths = parsed.path.split('/')
				filename = paths[-1]

			if filename:
				try: filename = unquote_to_bytes(filename).decode("utf-8")
				except:
					try: filename = unquote_to_bytes(filename).decode("euc-kr")
					except:
						l.og("Error: Can't find filename.")
						filename = Tools.md5(file)
						l.og("\tSave to: {}".format(filename))

				data = self.dm.find(post, filename)
				if not data:
					l.og("[Download] {}".format(filename))

					wo = open(os.sep.join((self.savedir, filename)), "wb")
					wo.write(content)
					wo.close()

					self.dm.add(key, category, post, file, filename)

					return True
		else:
			l.og("Error: requests.get()")
			l.og("\t{}".format(file))