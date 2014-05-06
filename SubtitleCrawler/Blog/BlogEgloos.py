# -*- coding: utf-8 -*-

from . import *

class BlogEgloos(BlogAbstract):
	KEY = "EGLOOS"
	URL = regex.compile(r".*[^\.]+\.egloos\.com.*")
	CATEGORY_URL1 = "http://{}.egloos.com/{}/{}"
	CATEGORY_URL2 = "http://{}/{}/{}"
	POST_URL1 = "http://{}.egloos.com/{}"
	POST_URL2 = "http://{}/{}"
	USER_REGEX = regex.compile(r"([^.]+)\.egloos\.com")
	CATEGORY_REGEX = regex.compile(r"/(category|tag)/(.*)")
	POST_REGEX = regex.compile(r"/(.*)")
	NOT_FOUND_POST = "등록된 포스트가 없습니다."

	def __init__(self, log=None):
		super(self.__class__, self).__init__(log)
		
	def search(self, url, user=None, category=None, tag=None, index=None, hostname=None):
		l = self.l

		if (user or hostname) and (category or tag):
			# Step 3: user, category or tag, index
			if index:
				index = str(index)

				if user: url = self.POST_URL1.format(user, index)
				elif hostname: url = self.POST_URL2.format(hostname, index)

				response = requests.get(url)
				if response.ok or response.status_code == 404:
					content = response.content
					dom = bs(content)

					s = self.NOT_FOUND_POST
					if any([ x in content for x in [ s.encode("utf-8"), s.encode("euc-kr") ]]):
						l.og("Error: Post not exists.")
						l.og("\t{}".format(unquote(url)))
					else:
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
					l.og("\t{}".format(unquote(url)))
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
					l.og("\t{}".format(unquote(url)))
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