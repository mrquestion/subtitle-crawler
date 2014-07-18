# -*- coding: utf-8 -*-

import os, sys
import re
import json
import requests as rq
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, urlunparse, parse_qs as qsparse, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes#, ParseResult
from collections import Counter

import inspect
import pprint
def pp(o): pprint.PrettyPrinter(indent=4).pprint(o)

BASE_URL1 = "http://www.anissia.net/anitime/list?w={}"
BASE_URL2 = "http://www.anissia.net/anitime/cap?i={}"
FIRST_DATE = "20140701000000"
LAST_DATE = "20141231235959"

def get_weekday():
	for i in range(0, 1):
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
	#print(url)
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
				yield url

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
		#for anchor in anchors:
		for href in hrefs:
			#path = urlparse(anchor["href"]).path
			path = urlparse(href).path
			url = urlunparse([ p.scheme, p.netloc, path, p.params, p.query, p.fragment ])
			yield url

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
			yield url

# TODO: http://*/xe
def xe(url):
	pass

# TODO: consider presented url is not posting url, just default blog url
# just find all anchor tags for candidate
def main(argc, args):
	sc = []
	for data in get_weekday():
		datas = [ data for data in get_subtitle(data) ]
		if not datas: continue
		title, url = data["s"], get_fastest(datas)[2]
		try: print(title, url)
		except: print(title.encode(), url, type(url))

		if not url: continue

		result = None
		if re.match(r"^blog\.naver\.com/.*", url):
			if not re.match(r"^blog\.naver\.com/PostView.nhn.*", url): url = naver_prepare(url)
			#if url: result = dict(NAME=title, NAVER=naver(url))
			if url:
				result = []
				for x in naver(url): result.append(dict(NAME=title, NAVER=x))
			else: print("Error: {}".format(title))
		elif re.match(r"^[^.]+\.blog.me/.*", url):
			url = naver_check(url)
			if url:
				result = []
				for x in naver(url): result.append(dict(NAME=title, NAVER=x))
		elif re.match(r"^[^.]+\.egloos.com/.*", url):
			result = []
			for x in egloos(url): result.append(dict(NAME=title, EGLOOS=x))
		elif re.match(r"^[^.]+\.tistory.com/.*", url):
			result = []
			for x in tistory(url): result.append(dict(NAME=title, TISTORY=x))
		else:
			#if naver_check(url): result = dict(NAME=title, NAVER=naver(naver_check(url)))
			url_checked = naver_check(url)
			if url_checked:
				result = []
				for x in naver(url_checked): result.append(dict(NAME=title, NAVER=x))
			url_checked = xe_check
		if result:
			if type(result) == list: sc += result
			else: sc.append(result)
		else:
			pass
			print(url, "not support")
			break
	pp(sc)
	#print(json.dumps(json.loads(str(sc).replace("'", '"')), indent=4))

if __name__ == "__main__":
	main(len(sys.argv), sys.argv)