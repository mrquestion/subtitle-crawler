# -*- coding: utf-8 -*-

from . import *

class BlogXe(BlogAbstract):
	KEY = "XE"
	URL = regex.compile(r".*[^/]+/xe")

	CATEGORY_URL = "http://{}/xe/index.php?listStyle=list&mid={}"
	POST_URL = "http://{}/xe/index.php?mid={}&document_srl={}"
	CATEGORY_REGEX = regex.compile(r".*/xe/?(.*)")
	POST_REGEX_FORMAT1 = r".*/xe/index.php\?.*mid={}.*document_srl=([0-9]*)[^#]*$"
	POST_REGEX_FORMAT2 = r".*/xe/{}/([0-9]*)[^#]*$"
	FILE_REGEX = regex.compile(r".*/xe/.*\?module=file&act=procFileDownload&file_srl=([0-9]*)&sid=([a-f0-9]*)")
	NOT_FOUND_CATEGORY1 = "잘못된 요청입니다."
	NOT_FOUND_CATEGORY2 = "template file does not exists."
	NOT_FOUND_POST = "alert(\"대상을 찾을 수 없습니다.\");"

	def __init__(self, log=None):
		super(self.__class__, self).__init__(log)
		
	def search(self, url, hostname=None, category=None, index=None):
		l = self.l

		if hostname and category:
			# Step 3: hostname, category, index
			if index:
				index = str(index)

				url = self.POST_URL.format(hostname, category, index)

				response = requests.get(url)
				if response.ok or response.status_code == 404:
					content = response.content
					dom = bs(content)
					
					s = self.NOT_FOUND_POST
					if any([ x in content for x in [ s.encode("utf-8"), s.encode("euc-kr")] ]):
						l.og("Error: Post not exists.")
						l.og("\t{}".format(unquote(url)))
					else:
						anchors = dom.find_all("a", href=self.FILE_REGEX)
						for anchor in anchors:
							bp = BlogProperty(key=self.KEY)
							bp.category = self.CATEGORY_URL.format(hostname, category)
							bp.post = url
							bp.file = anchor["href"]
							try: bp.filename = anchor.text.strip()
							except: bp.filename = None
							yield bp
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(url))
			# Step 2: hostname, category
			else:
				if type(category) is list: category = category[0]
				else: category = str(category)

				parsed = urlparse(url)
				qs = parse_qs(parsed.query)

				url = self.CATEGORY_URL.format(hostname, category)

				if "page" in qs and type(qs["page"]) is list:
					url = "{}&page={}".format(url, qs["page"][0])

				response = requests.get(url)
				if response.ok or response.status_code == 404:
					content = response.content
					dom = bs(content)

					s1 = self.NOT_FOUND_CATEGORY1
					s2 = self.NOT_FOUND_CATEGORY2

					if any([ x in content for x in [ s1.encode("utf-8"), s1.encode("euc-kr"), s2.encode("utf-8"), s2.encode("euc-kr") ]]):
						l.og("Error: Post not exists.")
						l.og("\t{}".format(unquote(url)))
					else:
						indexes = []

						pattern1 = regex.compile(self.POST_REGEX_FORMAT1.format(category))
						pattern2 = regex.compile(self.POST_REGEX_FORMAT2.format(category))

						anchors = dom.find_all("a", href=pattern1)
						for anchor in anchors:
							href = anchor["href"]
							parents = anchor.parents
							notices = [ parent for parent in parents if "class" in parent.attrs and "notice" in parent.attrs["class"] ]
							if not notices:
								matched = pattern1.match(href)
								if matched:
									index = matched.group(1)
									if not index in indexes: indexes.append(index)

						anchors = dom.find_all("a", href=pattern2)
						for anchor in anchors:
							href = anchor["href"]
							parents = anchor.parents
							notices = [ parent for parent in parents if "class" in parent.attrs and "notice" in parent.attrs["class"] ]
							if not notices:
								matched = pattern2.match(href)
								if matched:
									index = matched.group(1)
									if not index in indexes: indexes.append(index)

						for index in indexes:
							iter = self.search(url, hostname=hostname, category=category, index=index)
							bps = [ x for x in iter ]
							yield bps
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(url))
		# Step 1: URL
		else:
			parsed = urlparse(url)
			path = parsed.path

			iter = None
			if path == "/xe/index.php":
				qs = parse_qs(parsed.query)
				if "mid" in qs: iter = self.search(url, hostname=parsed.hostname, category=qs["mid"])
			else:
				matched = self.CATEGORY_REGEX.match(path)
				if matched: iter = self.search(url, hostname=parsed.hostname, category=matched.group(1))

			if iter:
				bps = []
				for x in iter: bps = bps + x
				yield bps
			else: l.og("Error: Not supported '{}' URL".format(self.KEY))




			'''
		if (user or hostname) and (category or tag):
			# Step 3: user, category or tag, index
			if index:
				index = str(index)

				if user: url = self.POST_URL1.format(user, index)
				elif hostname: url = self.POST_URL2.format(hostname, index)

				response = requests.get(url)
				if response.ok:
					content = response.content
					dom = bs(content)
					anchors = dom.find_all("a", href=self.EXTENSION_REGEX)
					for anchor in anchors:
						bp = BlogProperty(key=self.KEY)
						if user:
							if category: bp.category = self.CATEGORY_URL1.format(user, "category", category)
							elif tag: bp.category = self.CATEGORY_URL1.format(user, "tag", tag)
						elif hostname:
							if category: bp.category = self.CATEGORY_URL2.format(hostname, "category", category)
							elif tag: bp.category = self.CATEGORY_URL2.format(hostname, "tag", tag)
						bp.post = url
						bp.file = anchor["href"]
						#try: bp.filename = anchor.text.strip()
						#except: bp.filename = None
						yield bp
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(url))
			#Step 2: user, category or tag
			else:
				parsed = urlparse(url)
				qs = parse_qs(parsed.query)

				if user:
					if category: url = self.CATEGORY_URL1.format(user, "category", category)
					elif tag: url = self.CATEGORY_URL1.format(user, "tag", tag)
				elif hostname:
					if category: url = self.CATEGORY_URL2.format(hostname, "category", category)
					elif tag: url = self.CATEGORY_URL2.format(hostname, "tag", tag)

				if "page" in qs and type(qs["page"]) is list:
					url = "{}?page={}".format(url, qs["page"][0])

				response = requests.get(url)
				if response.ok:
					content = response.content
					dom = bs(content)
					titlelist_list = dom.find("div", id="titlelist_list")
					if titlelist_list:
						f_clear = titlelist_list.find("ul", attrs={ "class": "f_clear" })
						lis = f_clear.find_all("li")
						for li in lis:
							anchor = li.find("a", href=self.POST_REGEX)
							matched = self.POST_REGEX.match(anchor["href"])
							if matched:
								index = matched.group(1)

								iter = None
								if user:
									if category: iter = self.search(url, user=user, category=category, index=index)
									elif tag: iter = self.search(url, user=user, tag=tag, index=index)
								elif hostname:
									if category: iter = self.search(url, category=category, index=index, hostname=hostname)
									elif tag: iter = self.search(url, tag=tag, index=index, hostname=hostname)

								if iter:
									bps = [ x for x in iter ]
									yield bps
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(url))
		# Step 1: URL
		else:
			parsed = urlparse(url)
			path = parsed.path
			if path.startswith(("/category/", "/tag/")):
				hostname = parsed.hostname
				matched = self.USER_REGEX.match(hostname)
				if matched:
					user = matched.group(1)
					matched = self.CATEGORY_REGEX.match(path)
					if matched:
						category = matched.group(2)
						iter = None
						if matched.group(1) == "category":
							iter = self.search(url, user=user, category=category)
						elif matched.group(1) == "tag":
							iter = self.search(url, user=user, tag=category)
						else: l.og("Error: Not supported '{}' URL".format(self.KEY))

						if iter:
							bps = []
							for x in iter: bps = bps + x
							yield bps
				else:
					matched = self.CATEGORY_REGEX.match(path)
					if matched:
						category = matched.group(2)
						iter = None
						if matched.group(1) == "category":
							iter = self.search(url, category=category, hostname=hostname)
						elif matched.group(1) == "tag":
							iter = self.search(url, tag=category, hostname=hostname)
						else: l.og("Error: Not supported '{}' URL".format(self.KEY))

						if iter:
							bps = []
							for x in iter: bps = bps + x
							yield bps
			else: l.og("Error: Not supported '{}' URL".format(self.KEY))
			'''