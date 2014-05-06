# -*- coding: utf-8 -*-

def logo():
	print("==================")
	print(" Subtitle Crawler")
	print("==================")
	print()

basedir = "crawled"

# Debug
import inspect
def args(f): return inspect.getargspec(f)
def mems(f): return inspect.getmembers(f)
import pprint
def pp(s): pprint.PrettyPrinter(indent=4).pprint(s)

import time

# Prepare Directory
import os

if not os.path.exists(basedir):
	os.mkdir(basedir)

# Use Regular Expression
import re as regex

# Use JSON
import json

# Use HTTP Library
import requests
from bs4 import BeautifulSoup as bs

# Use URL Library
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes

# Use MD5 Hash
import hashlib

# Use Database via SQLite 3
import sqlite3 as sqlite

# Multiprocessing
import multiprocessing as mp
import subprocess

# Unicode Issue
import codecs
import unicodedata

def normalize(s, encoding="utf-8", ascii='_', filename=False):
	bs = s if type(s) is bytes else s.encode(encoding)
	if type(ascii) is bytes: ascii = ascii.decode()
	if len(ascii) == 0: ascii = '_'

	if filename:
		for c in "\\/:*?\"<>|":
			bs = bs.replace(c.encode("ascii"), ascii.encode("ascii"))

	if encoding == "ascii":
		ba = bytearray()
		for b in bs: ba.append(ord(ascii[0]) if b > 127 else b)
		bs = bytes(ba)

	if type(s) is bytes: s = bs
	elif type(s) is str: s = bs.decode(encoding)
	return s

# Convert Encoding
def convert(s):
	bs = s
	if not type(bs) is bytes: bs = bs.encode()
	ba = bytearray()
	temp = 0
	for b in bs:
		if b in (0xC2, 0xC3):
			if b == 0xC3: temp = 0x40
		else:
			try: ba.append(b + temp)
			except: ba.append(b)
			temp = 0
	bs = bytes(ba)
	if not type(s) is bytes: return bs.decode()
	else: return bs

# Make MD5 Hash from String
def md5(s):
	md5 = hashlib.md5(s.encode("utf-8"))
	s = md5.hexdigest()
	return s

# Redirect Message
def printcheck(s):
	try:
		stdout = os.dup(1)
		wo = open("temp", "wb")
		os.dup2(wo.fileno(), 1)
		print(s)
		os.dup2(stdout, 1)
		wo.close()
		return True
	except:
		raise

# Blog Parameters
# TODO: include regex
class Blog:
	NAVER = 1
	EGLOOS = 2
	TISTORY = 3
	XE = 4
	
	NAVER_REGEX = regex.compile(r".*blog\.naver\.com.*")
	NAVER_CATEGORY_URL = "http://blog.naver.com/PostList.nhn?blogId={}&categoryNo={}"
	NAVER_CATEGORY_ASYNC_URL = "http://blog.naver.com/PostTitleListAsync.nhn?blogId={}&categoryNo={}&countPerPage={}&currentPage={}"
	NAVER_POST_URL = "http://blog.naver.com/PostView.nhn?blogId={}&categoryNo={}&logNo={}"
	EGLOOS_REGEX = regex.compile(r".*[^\.]+\.egloos\.com.*")
	EGLOOS_CATEGORY_URL = "http://{}.egloos.com/category/{}"
	EGLOOS_TAG_URL = "http://{}.egloos.com/tag/{}"
	EGLOOS_POST_URL = "http://{}.egloos.com/{}"
	TISTORY_REGEX = regex.compile(r".*[^\.]+\.tistory\.com.*")
	TISTORY_CATEGORY_URL = "http://{}.tistory.com/category/{}"
	TISTORY_TAG_URL = "http://{}.tistory.com/tag/{}"
	TISTORY_POST_URL = "http://{}.tistory.com/{}"
	XE_REGEX = regex.compile(r".*[^/]+/xe")
	XE_CATEGORY_URL = "http://{}/xe/index.php?mid={}&listStyle=list"
	XE_POST_URL = "http://{}/xe/index.php?mid={}&document_srl={}"
	
	EXTENSIONS = [
		"smi", "srt", "ass", "sub",
		"zip", "rar", "7z", "ace", "alz", "egg",
		"lha", "lzh",
		"tar", "gz", "tgz", "bz", "bz2", "tbz", "tbz2",
		"lzma",
		"txt"
	]
	EXTENSION_REGEX = regex.compile(r".*/(([^/]+)\.({}))".format(r"|".join(EXTENSIONS)))

	CONTENT_REGEX = regex.compile(b".*filename=\"?([^\"]*)\"?;?.*")
	
	def __init__(self, database=None):
		self.dm = database
	
	# Select Next Process
	def parse(self, url, index=None, domain=None):
		if index:
			#if index == Blog.NAVER: self.naver(url)
			if index == Blog.NAVER: self.naver(url)
			elif index == Blog.EGLOOS: self.egloos(url)
			elif index == Blog.TISTORY: self.tistory(url, domain=domain)
			elif index == Blog.XE: self.xe(url)
			else: print("Error: Not supported index {}".format(index))
			print()
		else:
			parsed = urlparse(url)
			index = None
			domain = None
			if Blog.NAVER_REGEX.match(parsed.hostname):
				index = Blog.NAVER
			elif Blog.EGLOOS_REGEX.match(parsed.hostname):
				index = Blog.EGLOOS
			elif Blog.TISTORY_REGEX.match(parsed.hostname):
				domain = parsed.hostname
				index = Blog.TISTORY
			elif Blog.XE_REGEX.match(url):
				index = Blog.XE
			else:
				index = None

				response = requests.get(url)
				if response.ok:
					content = response.content
					dom = bs(content)
					navibar_login = dom.find("div", id="navibar_login")
					tistorytoolbarid = dom.find("div", id="tistorytoolbarid")
					if navibar_login: index = Blog.EGLOOS
					elif tistorytoolbarid: index = Blog.TISTORY
				'''
				response = requests.get("{}://{}/admin".format(parsed.scheme, parsed.hostname), allow_redirects=False)
				if response.ok and response.status_code in (302, 200):
					headers = response.headers
					if "location" in headers and Blog.TISTORY_REGEX.match(headers["location"]):
						domain = parsed.hostname
						uri = parsed.path
						parsed = urlparse(headers["location"])
						url = "{}://{}{}".format(parsed.scheme, parsed.hostname, uri)
						index = Blog.TISTORY
						'''

			if index:
				self.parse(url, index=index, domain=domain)
			else:
				print("Error: Not supported URL")
				print("\t'blog.naver.com', 'egloos.com', 'tistory.com'")
	
	# Fit in with NAVER
	'''
	def naver(self, url, blogId=None, categoryNo=None, logNo=None):
		if blogId and categoryNo:
			if type(blogId) is list:
				blogId = "&blogId=".join(x for x in blogId)
			else:
				blogId = str(blogId)
				
			if type(categoryNo) is list:
				categoryNo = "&categoryNo=".join(x for x in categoryNo)
			else:
				categoryNo = str(categoryNo)
			
			# blogId, categoryNo, logNo
			if logNo:
				if type(logNo) is list:
					logNo = "&logNo".join(x for x in logNo)
				else:
					logNo = str(logNo)
				
				bp = BlogProperty(category=Blog.NAVER_CATEGORY_URL.format(blogId, categoryNo))

				url = Blog.NAVER_POST_URL.format(blogId, categoryNo, logNo)
				bp.post = url

				response = requests.get(url)
				if response.ok:
					# TODO: Post Not Found Check
					content = response.content
					pattern = regex.compile(b".*aPostFiles\[[^\[]*(\[.*\]);")
					for s in content.split(b'\n'):
						#s = s.replace(b'\r', b'')
						matched = pattern.match(s)
						if matched:
							aPostFiles = matched.group(1)
							aPostFiles = quote_from_bytes(aPostFiles, safe="/'\": {}[],")
							#aPostFiles = normalize(aPostFiles)
							aPostFiles = aPostFiles.replace("'", '"')
							try:
								aPostFiles = json.loads(aPostFiles)
								if type(aPostFiles) is list:
									for aPostFile in aPostFiles:
										bp.file = unquote(aPostFile["encodedAttachFileUrl"])
										self.download(bp)
								elif type(aPostFiles) is dict:
									bp.file = unquote(aPostFiles["encodedAttachFileUrl"])
									self.download(bp)
							except Exception as e:
								print("Error: json.loads()")
								print("\t{}".format(e))
								raise e
							break
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
			# blogId, categoryNo
			else:
				url = Blog.NAVER_CATEGORY_URL.format(blogId, categoryNo)

				print("Get list from \"{}\"".format(url))

				response = requests.get(url)
				if response.ok:
					# TODO: Category Not Found Check
					content = response.content
					dom = bs(content)
					postListBody = dom.find("div", id="postListBody")
					list_txts = postListBody.findAll("p", attrs={"class": "list_txt"})
					list_dates = postListBody.findAll("p", attrs={"class": "list_date"})
					for i in range(0, len(list_txts)):
						list_txt = list_txts[i]
						list_date = list_dates[i]
						
						anchor = list_txt.find("a", attrs={"href": True})
						if anchor:
							href = anchor["href"]
							parsed = urlparse(href)
							qs = parse_qs(parsed.query)
							self.naver(url, blogId=blogId, categoryNo=categoryNo, logNo=qs["logNo"])
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
		else:
			parsed = urlparse(url)
			qs = parse_qs(parsed.query)
			if "blogId" in qs and "categoryNo" in qs:
				self.naver(url, blogId=qs["blogId"], categoryNo=qs["categoryNo"])
			else:
				print("Error: Not supported Naver URL(need 'blogId', 'categoryNo')")
				'''
	def naver(self, url, blogId=None, categoryNo=None, logNo=None):
		if blogId and categoryNo:
			if type(blogId) is list:
				blogId = "&blogId=".join(x for x in blogId)
			else:
				blogId = str(blogId)
				
			if type(categoryNo) is list:
				categoryNo = "&categoryNo=".join(x for x in categoryNo)
			else:
				categoryNo = str(categoryNo)
			
			# blogId, categoryNo, logNo
			if logNo:
				logNo = str(logNo)
				
				bp = BlogProperty(category=Blog.NAVER_CATEGORY_URL.format(blogId, categoryNo))

				url = Blog.NAVER_POST_URL.format(blogId, categoryNo, logNo)
				bp.post = url

				response = requests.get(url)
				if response.ok:
					# TODO: Post Not Found Check
					content = response.content
					pattern = regex.compile(b".*aPostFiles\[[^\[]*(\[.*\]);")
					for s in content.split(b'\n'):
						#s = s.replace(b'\r', b'')
						matched = pattern.match(s)
						if matched:
							aPostFiles = matched.group(1)
							aPostFiles = quote_from_bytes(aPostFiles, safe="/'\": {}[],")
							#aPostFiles = normalize(aPostFiles)
							aPostFiles = aPostFiles.replace("'", '"')
							try:
								aPostFiles = json.loads(aPostFiles)
								if type(aPostFiles) is list:
									first = True
									for aPostFile in aPostFiles:
										bp.file = unquote(aPostFile["encodedAttachFileUrl"])
										self.download(bp, repeat=first==False)
										if first: first = False
								elif type(aPostFiles) is dict:
									bp.file = unquote(aPostFiles["encodedAttachFileUrl"])
									self.download(bp)
							except Exception as e:
								print("Error: json.loads()")
								print("\t{}".format(e))
								raise e
							break
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
			# blogId, categoryNo
			else:
				parsed = urlparse(url)
				queries = parse_qs(parsed.query)

				url = Blog.NAVER_CATEGORY_URL.format(blogId, categoryNo)

				currentPage = 1
				if "currentPage" in queries and len(queries["currentPage"]) > 0:
					currentPage = int(queries["currentPage"])
					url = "{}?currentPage={}".format(url, currentPage)

				print("Get list from \"{}\"".format(url))

				countPerPage = 10
				currentPage = int(currentPage / countPerPage + 1)
				async = Blog.NAVER_CATEGORY_ASYNC_URL.format(blogId, categoryNo, countPerPage, currentPage)
				
				response = requests.get(async)
				if response.ok:
					content = response.content
					content = content.replace(b"\\\'", b"\'")
					content = convert(content)
					content = normalize(content, encoding="ascii")
					jsondata = json.loads(content.decode())
					if "postList" in jsondata:
						postList = jsondata["postList"]
						if type(postList) is list:
							for post in postList:
								if "logNo" in post:
									self.naver(url, blogId=blogId, categoryNo=categoryNo, logNo=post["logNo"])
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
		else:
			parsed = urlparse(url)
			qs = parse_qs(parsed.query)
			if "blogId" in qs and "categoryNo" in qs:
				self.naver(url, blogId=qs["blogId"], categoryNo=qs["categoryNo"])
			else:
				print("Error: Not supported Naver URL(need 'blogId', 'categoryNo')")
	
	# Fit in with egloos
	def egloos(self, url, user=None, category=None, tag=None, index=None, retry=True):
		if user and (category or tag):
			# user, category or tag, index
			if index:
				index = str(index)
				
				bp = BlogProperty()

				if category: bp.category = Blog.EGLOOS_CATEGORY_URL.format(user, category)
				elif tag: bp.category = Blog.EGLOOS_TAG_URL.format(user, tag)

				url = Blog.EGLOOS_POST_URL.format(user, index)
				bp.post = url

				response = requests.get(url)
				if response.ok:
					# TODO: Post Not Found Check
					content = response.content
					dom = bs(content)
					section_content = dom.find(id="section_content")
					div = section_content.find("div")
					post_view = div.find("div", attrs={"class": "post_view"})
					post_content = post_view.find("div", attrs={"class": "post_content"})
					hentry = post_content.find("div", attrs={"class": "hentry"})
					anchors = hentry.findAll("a", attrs={"href": True})
					pattern = regex.compile(r".*/(([^/]+)\.({}))".format(r"|".join(Blog.EXTENSIONS)))
					first = True
					for anchor in anchors:
						href = anchor["href"]
						matched = pattern.match(href)
						if matched:
							bp.file = href
							filename = matched.group(1)
							bp.filename = filename
							self.download(bp, repeat=first==False)
							if first: first = False
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
			# user, category or tag
			else:
				parsed = urlparse(url)
				queries = parse_qs(parsed.query)

				if category: url = Blog.EGLOOS_CATEGORY_URL.format(user, category)
				elif tag: url = Blog.EGLOOS_TAG_URL.format(user, tag)

				if "page" in queries and len(queries["page"]) > 0:
					url = "{}?page={}".format(url, queries["page"][0])

				print("Get list from \"{}\"".format(unquote(url)))

				response = requests.get(url)
				if response.ok:
					# TODO: Category Not Found Check
					content = response.content
					dom = bs(content)
					titlelist_list = dom.find("div", id="titlelist_list")
					if titlelist_list:
						f_clear = titlelist_list.find("ul", attrs={"class": "f_clear"})
						lis = f_clear.findAll("li")
						pattern = regex.compile(r"/(.*)")
						for li in lis:
							anchor = li.find("a", attrs={"href":True})
							matched = pattern.match(anchor["href"])
							if matched:
								index = matched.group(1)
								if category: self.egloos(url, user=user, category=category, index=index)
								elif tag: self.egloos(url, user=user, tag=tag, index=index)
					else:
						if retry:
							print("Retry: Can't find \"titlelist_list\"")
							self.egloos(url, user=user, category=category, tag=tag, index=index, retry=False)
						else: print("Error: Can't find \"titlelist_list\"")
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
		else:
			parsed = urlparse(url)
			path = parsed.path
			if path.startswith(("/category/", "/tag/")):
				matched = regex.match(r"([^.]+)\.egloos\.com", parsed.hostname)
				if matched:
					user = matched.group(1)
					matched = regex.match(r"/(category|tag)/(.*)", path)
					if matched:
						category = matched.group(2)
						if matched.group(1) == "category":
							self.egloos(url, user=user, category=category)
						elif matched.group(1) == "tag":
							self.egloos(url, user=user, tag=category)
						else:
							print("Error", url)
			else:
				print("Error: Not supported Egloos URL")
				print("\t'*.egloos.com/category/Category_Name' or")
				print("\t'*.egloos.com/tag/Tag_Name'")
	
	# Fit in tistory
	def tistory(self, url, user=None, category=None, tag=None, index=None, domain=None, retry=True):
		if user and (category or tag):
			# user, category or tag, index
			if index:
				index = str(index)

				bp = BlogProperty()

				if category: bp.category = Blog.TISTORY_CATEGORY_URL.format(user, category)
				elif tag: bp.category = Blog.TISTORY_TAG_URL.format(user, tag)

				url = Blog.TISTORY_POST_URL.format(user, index)
				bp.post = url

				response = requests.get(url)
				if response.ok:
					# TODO: Post Not Found Check
					content = response.content
					dom = bs(content)
					anchors = dom.findAll("a", attrs={"href": True})
					pattern = Blog.EXTENSION_REGEX
					first = True
					for anchor in anchors:
						href = anchor["href"]
						matched = pattern.match(href)
						if matched:
							bp.file = href
							bp.filename = anchor.text.strip()
							self.download(bp, repeat=first==False)
							if first: first = False
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
			# user, category or tag
			else:
				parsed = urlparse(url)
				queries = parse_qs(parsed.query)

				if category: url = Blog.TISTORY_CATEGORY_URL.format(user, category)
				elif tag: url = Blog.TISTORY_TAG_URL.format(user, tag)

				if "page" in queries and len(queries["page"]) > 0:
					url = "{}?page={}".format(url, queries["page"][0])

				print("Get list from \"{}\"".format(unquote(url)))

				response = requests.get(url)
				if response.ok:
					# TODO: Category Not Found Check
					content = response.content
					dom = bs(content)
					anchors = dom.findAll("a", attrs={"href": True})
					pattern1 = regex.compile(r"(http://[^/]*|)/(entry/.+|[0-9]+)$")
					pattern2 = regex.compile(r".*{}/(entry/.+|[0-9]+)$".format(domain))
					posts = []
					for anchor in anchors:
						href = anchor["href"]

						matched = pattern1.match(href)
						if matched:
							recent = anchor.parent.findAll("span", id=regex.compile(r"commentCountOnRecentEntries[0-9]+"))
							if not recent:
								post = matched.group(2)
								if post in posts: pass
								else: posts.append(post)

						matched = pattern2.match(href)
						if matched:
							recent = anchor.parent.findAll("span", id=regex.compile(r"commentCountOnRecentEntries[0-9]+"))
							if not recent:
								post = matched.group(1)
								if post in posts: pass
								else: posts.append(post)

					for post in posts:
						index = post
						if category: self.tistory(url, user=user, category=category, index=index, domain=domain)
						elif tag: self.tistory(url, user=user, tag=tag, index=index, domain=domain)
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
		else:
			parsed = urlparse(url)
			path = parsed.path
			if path.startswith(("/category/", "/tag/")):
				matched = regex.match(r"([^.]+)\.tistory\.com", parsed.hostname)
				if matched:
					user = matched.group(1)
					matched = regex.match(r"/(category|tag)/(.*)", path)
					if matched:
						category = matched.group(2)
						if matched.group(1) == "category":
							self.tistory(url, user=user, category=category, domain=domain)
						elif matched.group(1) == "tag":
							self.tistory(url, user=user, tag=category, domain=domain)
						else:
							print("Error", url)
			else:
				print("Error: Not supported Tistory URL")
				print("\t'*.tistory.com/category/Category_Name' or")
				print("\t'*.tistory.com/tag/Tag_Name'")

	# Fit in xe
	def xe(self, url, domain=None, category=None, index=None):
		if domain and category:
			# domain, category, index
			if index:
				index = str(index)

				bp = BlogProperty(category=Blog.XE_CATEGORY_URL.format(domain, category))
				
				url = Blog.XE_POST_URL.format(domain, category, index)
				bp.post = url

				response = requests.get(url)
				if response.ok:
					# TODO: Post Not Found Check
					content = response.content
					dom = bs(content)
					anchors = dom.findAll("a", attrs={ "href": True })

					pattern = regex.compile(r".*/xe/.*\?module=file&act=procFileDownload&file_srl=([0-9]*)&sid=([a-f0-9]*)")
					first = True
					for anchor in anchors:
						href = anchor["href"]
						matched = pattern.match(href)
						if matched:
							bp.file = href
							bp.filename = anchor.text.strip()
							self.download(bp, repeat=first==False)
							if first: first = False
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
			# domain, category
			else:
				if type(category) is list:
					category = "&mid=".join(x for x in category)
				else:
					category = str(category)

				parsed = urlparse(url)
				queries = parse_qs(parsed.query)

				url = Blog.XE_CATEGORY_URL.format(domain, category)
				if "page" in queries and len(queries["page"]) > 0:
					url = "{}&page={}".format(url, queries["page"][0])

				print("Get list from \"{}\"".format(unquote(url)))

				response = requests.get(url)
				if response.ok:
					# TODO: Category Not Found Check
					content = response.content
					dom = bs(content)
					anchors = dom.findAll("a", attrs={ "href": True })

					pattern1 = regex.compile(r".*/xe/index.php\?mid={}.*document_srl=([0-9]*)[^#]*$".format(category))
					pattern2 = regex.compile(r".*/xe/{}/([0-9]*)[^#]*$".format(category))
					posts = []
					for anchor in anchors:
						notice = False
						parents = anchor.parents
						for parent in parents:
							if "class" in parent.attrs:
								if "notice" in parent.attrs["class"]:
									notice = True
									break

						if not notice:
							href = anchor["href"]
							matched = pattern1.match(href)
							if matched:
								post = matched.group(1)
								if post in posts: pass
								else: posts.append(post)
							matched = pattern2.match(href)
							if matched:
								post = matched.group(1)
								if post in posts: pass
								else: posts.append(post)

					for post in posts:
						index = post
						self.xe(url, domain=domain, category=category, index=index)
				else:
					print("Error: requests.get()")
					print("\t{}".format(url))
		else:
			parsed = urlparse(url)
			path = parsed.path
			if path == "/xe/index.php":
				queries = parse_qs(parsed.query)
				if "mid" in queries:
					self.xe(url, domain=parsed.hostname, category=queries["mid"])
			else:
				matched = regex.match(r".*/xe/?(.*)", path)
				if matched:
					self.xe(url, domain=parsed.hostname, category=matched.group(1))
				else:
					print("Error: Not supported XE URL")
					print("\t'*/xe/Category_Name' or")
					print("\t'*/xe/index.php?mid=Category_Name'")

	# Download File
	def download(self, bp, repeat=False):
		filename = bp.filename
		if not repeat: print("Get from \"{}\"".format(bp.post))
		#response = requests.get(bp.file)
		headers = { "User-Agent": "Mozilla AppleWebKit Chrome Safari" }
		response = requests.get(bp.file, headers=headers)
		if response.ok:
			headers = response.headers
			if "Content-disposition" in headers:
				content_disposition = headers["Content-disposition"]
				content_disposition = convert(content_disposition.encode())
				matched = Blog.CONTENT_REGEX.match(content_disposition)
				if matched: filename = matched.group(1)
			content = response.content

			if not filename:
				parsed = urlparse(bp.file)
				paths = parsed.path.split('/')
				filename = paths[-1]
				if len(filename) == 0:
					filename = "{}_{}".format(basedir, md5(bp.file))
					print("Error: Can't find filename.")
					print("\tSave to: {}".format(filename))
			
			if type(filename) is str: filename = filename.encode()

			try:
				temp = filename.decode("utf-8")
				temp = unquote(temp, encoding="utf-8")
				if printcheck(temp): filename = temp
			except Exception as e:
				try:
					temp = filename.decode("ms949")
					temp = unquote(temp, encoding="ms949")
					if printcheck(temp): filename=temp
				except Exception as e:
					print("Error: Can't find filename.")
					if type(filename) is str: print("\t{}".format(filename.encode()))
					else: print("\t{}".format(str(filename)))
					filename = "{}_{}".format(basedir, md5(bp.file))
					print("\tSave to: {}".format(filename))

			filename = normalize(filename, filename=True)
			bp.filename = filename

			data = self.dm.select(bp.post, bp.filename)
			if not data:
				print("\tGet \"{}\"".format(bp.filename))
				filename = "{}\\{}".format(basedir, filename)
				wo = open(filename, "wb")
				wo.write(content)
				wo.close()
			
				self.dm.insert(bp.filename, bp.category, bp.post, bp.file)
		else:
			print("Error: requests.get()")
			print("\t{}".format(bp.post))

# Object Include Category URL, Post URL, File URL, File Name
class BlogProperty:
	def __init__(self, type=None, category=None, post=None, file=None, filename=None):
		self.type = type
		self.category = category
		self.post = post
		self.file = file
		self.filename = filename

# Database Manager
class DatabaseManager:
	CREATE = "\
		Create table If not exists SUBTITLE(\
			index_subtitle integer,\
			subtitle_hash text,\
			subtitle_file_name text,\
			subtitle_category_url text,\
			subtitle_post_url text,\
			subtitle_file_url text,\
			subtitle_insert_time text\
		)\
	"
	INSERT = "\
		Insert into SUBTITLE(\
			index_subtitle,\
			subtitle_hash,\
			subtitle_file_name,\
			subtitle_category_url,\
			subtitle_post_url,\
			subtitle_file_url,\
			subtitle_insert_time\
		)\
		Select\
			ifnull(max(index_subtitle), 0)+1,\
			?,\
			?,\
			?,\
			?,\
			?,\
			datetime('now', 'localtime')\
		From\
			SUBTITLE\
	"
	SELECT = "\
		Select\
			index_subtitle\
		From\
			SUBTITLE\
		Where\
			subtitle_hash = ?\
	"
	filename = "{}.db".format(basedir)
	
	def __init__(self, filename=None):
		if filename: self.filename = filename
		self.db = sqlite.connect(self.filename)
		self.db.execute(self.CREATE)
		self.db.commit()
		self.db.close()
	
	def select(self, post, filename):
		self.db = sqlite.connect(self.filename)
		filehash = md5("{}:{}".format(post, filename))
		rs = self.db.execute(self.SELECT, (filehash, ))
		data = rs.fetchone()
		self.db.close()
		return data
	
	def insert(self, filename, category, post, file):
		self.db = sqlite.connect(self.filename)
		filehash = md5("{}:{}".format(post, filename))
		self.db.execute(self.INSERT, (filehash, filename, category, post, file))
		self.db.commit()
		self.db.close()
	
	def close(self):
		self.db.close()
		
# Get URL List by JSON
def urllist():
	filename = "{}.json".format(basedir)
	urls = None
	if os.path.exists(filename):
		ro = open(filename, "r")
		try:
			urls = json.loads(ro.read())
		except Exception as e:
			print("Error: json.loads()")
			print("\t{}".format(e))
	return urls

# Main
import sys

def main(argc, args):
	logo()
	dm = DatabaseManager()
	blog = Blog(database=dm)

	urls = urllist()

	t = time.time()
	if type(urls) is list:
		#pools = mp.Pool(processes=mp.cpu_count())
		#pools.map(blog.parse, urls)
		for url in urls:
			blog.parse(url)
			#break
	print("Elapsed: {}".format(time.time()-t))

	#dm.close()

if __name__ == "__main__":
	mp.freeze_support()
	main(len(sys.argv), sys.argv)