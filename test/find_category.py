# -*- coding: utf-8 -*-

import os, sys
import time, datetime
import re
import json
import requests as rq
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, urlunparse, parse_qs as qsparse, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes
from collections import Counter

import inspect
import pprint
def pp(o): pprint.PrettyPrinter(indent=4).pprint(o)

BASE_URL1 = "http://www.anissia.net/anitime/list?w={}"
BASE_URL2 = "http://www.anissia.net/anitime/cap?i={}"
FIRST_DATE = "20140701000000"
LAST_DATE = "20141231235959"
WEEKDAY = { 0: "[일]", 1: "[월]", 2: "[화]", 3: "[수]", 4: "[목]", 5: "[금]", 6: "[토]" }

def get_weekday(min=0, max=7):
	for i in range(min, max):
		yield { "WEEKDAY": WEEKDAY[i] }
		url = BASE_URL1.format(i)
		rs = rq.get(url)
		if rs.ok:
			datas = json.loads(rs.content.decode())
			for data in datas: yield data

def get_subtitle(data):
	url = BASE_URL2.format(data["i"])
	rs = rq.get(url)
	if rs.ok:
		datas = json.loads(rs.content.decode())
		for data in datas: yield data

def get_fastest(datas):
	episode = "00000"
	fastest = LAST_DATE
	url = None
	for data in datas:
		d, s, a = data["d"], data["s"], data["a"]
		if s > episode: episode, fastest, url = s, d, a
		elif FIRST_DATE < d < fastest: fastest, url = d, a
		if fastest == LAST_DATE: fastest = None
	return episode, fastest, url

def naver_prepare(url):
	m = re.match(r"(?P<fixed>.*blog\.naver\.com/[^/]+/[0-9]+).*", url)
	url = m.groupdict()["fixed"] if m else url
	if not url.startswith("http://"): url = "http://{}".format(url)
	rs = rq.get(url)
	dom = bs(rs.content) if rs.ok else None
	if dom:
		mainFrame = dom.find("frame", id="mainFrame")
		p = urlparse(url)
		url = urlunparse([ p.scheme, p.netloc, mainFrame["src"], p.params, p.query, p.fragment ])
		return url

def naver(url):
	if not url.startswith("http://"): url = "http://{}".format(url)
	rs = rq.get(url)
	dom = bs(rs.content) if rs.ok else None
	if dom:
		p = urlparse(url)
		title_1 = dom.find("div", id="title_1")
		if title_1:
			cate = title_1.find("span", class_=[ "cate", "pcol2" ])
			pcol2s = cate.find_all("a", class_="pcol2", href=True)
			for pcol2 in pcol2s:
				path = urlparse(pcol2["href"]).path
				qs = qsparse(urlparse(pcol2["href"]).query)
				if "blogId" in qs and "categoryNo" in qs:
					queries = []
					for key in [ "blogId", "categoryNo" ]:
						queries += [ '='.join([ key, value ]) for value in qs[key] ]
					qs = '&'.join(queries)
					url = urlunparse([ p.scheme, p.netloc, path, p.params, qs, p.fragment ])

					rs = rq.get(url)
					dom = bs(rs.content) if rs.ok else None
					category_name = dom.find("div", id="category-name")
					if category_name:
						postlisttitle = category_name.find("div", class_="postlisttitle")
						toplistSpanBlind = postlisttitle.find("span", id="toplistSpanBlind")
						title = toplistSpanBlind.previousSibling.strip()

						yield url, title

def naver_check(url):
	if not url.startswith("http://"): url = "http://{}".format(url)
	rs = rq.get(url)
	dom = bs(rs.content) if rs.ok else None
	if dom:
		screenFrame = dom.find("frame", id="screenFrame")
		if screenFrame: return naver_prepare(screenFrame["src"])

def egloos(url):
	if not url.startswith("http://"): url = "http://{}".format(url)
	rs = rq.get(url)
	dom = bs(rs.content) if rs.ok else None
	if dom:
		p = urlparse(url)
		anchors = dom.find_all("a", href=re.compile(r"^/category/.*"))
		hrefs = [ href for href, count in Counter([ anchor["href"] for anchor in anchors ]).most_common(3) ]
		for href in hrefs:
			path = urlparse(href).path
			url = urlunparse([ p.scheme, p.netloc, path, p.params, p.query, p.fragment ])
			yield unquote(url)

def tistory(url):
	if not url.startswith("http://"): url = "http://{}".format(url)
	rs = rq.get(url)
	dom = bs(rs.content) if rs.ok else None
	if dom:
		p = urlparse(url)
		anchors = dom.find_all("a", href=re.compile(r"^/category/.*"))
		hrefs = [ href for href, count in Counter([ anchor["href"] for anchor in anchors ]).most_common(3) ]
		for href in hrefs:
			path = urlparse(href).path
			url = urlunparse([ p.scheme, p.netloc, path, p.params, p.query, p.fragment ])
			yield unquote(url)

# TODO: http://*/xe
def xe(url):
	pass

def timestamp(format="%Y%m%d-%H%M%S"):
	return datetime.datetime.fromtimestamp(time.time()).strftime(format)

def save(titles, categories, filename="{}.json".format(timestamp()), encoding="utf-8"):
	content = [ '[', os.linesep, os.linesep ]
	first = True
	for category in categories:
		if first: first = False
		else:
			content.append(',')
			content.append(os.linesep)
		line = ", ".join('"{}": "{}"'.format(key, value) for key, value in category.items())
		content.append("{{ {} }}".format(line))
	content.extend([ os.linesep, os.linesep, ']' ])
	with open(filename, "wb") as wbo:
		wbo.write(''.join(content).encode())

# TODO: consider presented url is not posting url, just default blog url
# just find all anchor tags for candidate
def main(argc, args):
	sc = []
	for data in get_weekday(max=7):
		if "WEEKDAY" in data: print(data["WEEKDAY"])
		else:
			datas = [ data for data in get_subtitle(data) ]
			if not datas: continue

			title, (episode, fastest, url) = data["s"], get_fastest(datas)
			try: print("- {} ({}) E{} / {}".format(title, url, episode, fastest))
			except: print("- {} ({}) E{} / {}".format(title.encode(), url, episode, fastest))
			if not url: continue

			result = None
			if re.match(r"^blog\.naver\.com/.*", url):
				if not re.match(r"^blog\.naver\.com/PostView\.nhn.*", url): url = naver_prepare(url)
				if url: result = [ dict(NAME=title, NAVER=x, TEST=y) for x, y in naver(url) ]
				else: raise ValueError(title)
			elif re.match(r"^[^.]+\.blog\.me/.*", url):
				url = naver_check(url)
				if url: result = [ dict(NAME=title, NAVER=x, TEST=y) for x, y in naver(url) ]
				else: raise ValueError(title)
			elif re.match(r"^[^.]+\.egloos.com/.*", url):
				result = [ dict(NAME=title, EGLOOS=x) for x in egloos(url) ]
			elif re.match(r"^[^.]+\.tistory.com/.*", url):
				result = [ dict(NAME=title, TISTORY=x) for x in tistory(url) ]
			elif re.match(r"^[^/]+/xe/.*", url):
				pass
			else:
				checked = naver_check(url)
				if checked: result = [ dict(NAME=title, NAVER=x, TEST=y) for x, y in naver(checked) ]

			if result:
				sc.extend(result)
				print("  > {} candidate{}.".format(len(result), 's' if len(result) > 1 else ''))
				for i in range(0, len(result)):
					try: print("    => {}. {}".format(i+1, result[i]))
					except: print("    => {}. {}".format(i+1, str(result[i]).encode()))
			else:
				sc.append(dict(NAME=title, NOT_SUPPORTED=url))
				print("  > Error: not supported url.")
	save(None, sc)
	#pp(sc)
	#print(json.dumps(json.loads(str(sc).replace("'", '"')), indent=4))

if __name__ == "__main__":
	main(len(sys.argv), sys.argv)