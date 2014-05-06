# -*- coding: utf-8 -*-

from . import *

class BlogNaver(BlogAbstract):
	KEY = "NAVER"
	URL = regex.compile(r".*blog\.naver\.com.*")
	CATEGORY_URL = "http://blog.naver.com/PostList.nhn?blogId={}&categoryNo={}"
	CATEGORY_ASYNC_URL = "http://blog.naver.com/PostTitleListAsync.nhn?blogId={}&categoryNo={}&countPerPage={}&currentPage={}"
	POST_URL = "http://blog.naver.com/PostView.nhn?blogId={}&categoryNo={}&logNo={}"
	POSTFILES = regex.compile(b".*aPostFiles\[[^\[]*(\[.*\]);")
	NOT_FOUND_POST = "삭제되었거나 존재하지 않는 게시물입니다."

	def __init__(self, log=None):
		super(self.__class__, self).__init__(log)

	def search(self, url, blogId=None, categoryNo=None, logNo=None):
		l = self.l

		if blogId and categoryNo:
			if blogId and type(blogId) is list: blogId = blogId[0]
			else: blogId = str(blogId)

			if categoryNo and type(categoryNo) is list: categoryNo = categoryNo[0]
			else: categoryNo = str(categoryNo)

			# Step 3: logNo
			if logNo:
				if type(logNo) is list: logNo = logNo[0]
				else: logNo = str(logNo)

				url = self.POST_URL.format(blogId, categoryNo, logNo)

				response = requests.get(url)
				if response.ok:
					content = response.content

					#error = False
					s = self.NOT_FOUND_POST
					#if all([ b"alert(msg)" in content, any([ x in content for x in [ s.encode("utf-8"), s.encode("euc-kr")] ]) ]):
					if b"alert(msg)" in content and any([ x in content for x in [ s.encode("utf-8"), s.encode("euc-kr")] ]):
						l.og("Error: Post not exists.")
						l.og("\t{}".format(unquote(url)))
						#error = True

						'''
					error = False
					if b"alert(msg)" in content:
						s = "삭제되었거나 존재하지 않는 게시물입니다."
						if s.encode("utf-8") in content or s.encode("euc-kr") in content:
							l.og("Error: Post not exist.")
							l.og("\t{}".format(url))
							error = True
							'''

					#if not error:
					else:
						for s in content.split(b'\n'):
							matched = self.POSTFILES.match(s)
							if matched:
								aPostFiles = matched.group(1)
								aPostFiles = quote_from_bytes(aPostFiles, safe="/'\": {}[],")
								aPostFiles = aPostFiles.replace("'", '"')
								try:
									jsondata = json.loads(aPostFiles)
									if type(jsondata) is list:
										first = True
										for aPostFile in jsondata:
											bp = BlogProperty(key=self.KEY)
											bp.category = self.CATEGORY_URL.format(blogId, categoryNo)
											bp.post = url
											bp.file = aPostFile["encodedAttachFileUrl"]
											bp.filename = aPostFile["encodedAttachFileName"]
											if bp.filename:
												try: bp.filename = unquote_to_bytes(bp.filename).decode("utf-8")
												except:
													try: bp.filename = unquote_to_bytes(bp.filename).decode("euc-kr")
													except: bp.filename = aPostFile["encodedAttachFileName"]
											yield bp
								except Exception as e:
									l.og("Error: json.loads()")
									l.og("\t{}".format(e))
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(unquote(url)))
			# Step 2: blogId, categoryNo
			else:
				parsed = urlparse(url)
				qs = parse_qs(parsed.query)

				url = self.CATEGORY_URL.format(blogId, categoryNo)

				currentPage = 1
				if "currentPage" in qs and type(qs["currentPage"]) is list:
					currentPage = qs["currentPage"][0]
				url = "{}&currentPage={}".format(url, currentPage)

				countPerPage = 10
				currentPage = int(currentPage / countPerPage + 1)
				async = self.CATEGORY_ASYNC_URL.format(blogId, categoryNo, countPerPage, currentPage)

				response = requests.get(async)
				if response.ok:
					content = response.content
					content = content.replace(b"\\\'", b"\'")
					content = Tools.normalize(content)
					jsondata = json.loads(content.decode())

					if "resultCode" in jsondata and jsondata["resultCode"] == 'E':
						l.og("Error: Category not exists.")
						l.og("\t{}".format(unquote(url)))
					else:
						if "postList" in jsondata:
							postList = jsondata["postList"]
							if type(postList) is list:
								for post in postList:
									if "logNo" in post:
										iter = self.search(url, blogId=blogId, categoryNo=categoryNo, logNo=post["logNo"])
										bps = [ x for x in iter ]
										yield bps
				else:
					l.og("Error: requests.get()")
					l.og("\t{}".format(unquote(url)))
		# Step 1: URL
		else:
			parsed = urlparse(url)
			qs = parse_qs(parsed.query)
			if "blogId" in qs and "categoryNo" in qs:
				iter = self.search(url, blogId=qs["blogId"], categoryNo=qs["categoryNo"])
				bps = []
				for x in iter: bps = bps + x
				yield bps
			else: l.og("Error: Not supported '{}' URL".format(self.KEY))