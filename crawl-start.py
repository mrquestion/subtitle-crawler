# -*- coding: utf-8 -*-

import os
import sys
from time import time
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, quote_from_bytes, unquote_to_bytes

from SubtitleCrawler import SubtitleCrawler
from SubtitleCrawler import Tools

from SubtitleCrawler.Blog import Blog

from SubtitleCrawler.Blog.BlogNaver import BlogNaver
from SubtitleCrawler.Blog.BlogEgloos import BlogEgloos
from SubtitleCrawler.Blog.BlogTistory import BlogTistory
from SubtitleCrawler.Blog.BlogXe import BlogXe

def main(argc, args):
	sc = SubtitleCrawler()

	l = sc.l

	l.og(Tools.getlogo("Subtitle Crawler"), sep=os.linesep)

	l.og("[Word] Load from '{}'...".format(sc.WORDFILE))
	urls = sc.words()
	l.og("\t{} words loaded.".format(len(urls), 's' if len(urls) > 1 else ''), os.linesep)

	blog = Blog(savedir=sc.savedir, log=l)
	blog.adds([ BlogNaver, BlogEgloos, BlogTistory, BlogXe ])

	t = time()
	total = complete = ignore = 0

	if urls:
		for url in urls:
			bps, key, url, name = blog.parse(url)
			if bps:
				l.og("[Search-{}] {}".format(key, name if name else unquote(url)))
				bps.reverse()
				for bp in bps:
					# TODO: error on content-disposition
					# move to download or other logic
					#data = sc.dm.find(bp.post, bp.filename)
					#if not data:
						success = sc.download(bp.key, bp.category, bp.post, bp.file, bp.filename)
						total = total + 1 if success else 0
				l.og()
				complete = complete + 1
			else: ignore = ignore + 1

		l.og("[Result]")
		l.og("\tTotal: {}".format(total))
		l.og("\tElapsed: {}".format(time()-t))
		l.og()

		l.og("[Total Result]")
		l.og("\tComplete: {} word{} done.".format(complete, 's' if complete > 1 else ''))
		l.og("\tIgnore: {} word{} ignored.".format(ignore, 's' if ignore > 1 else ''))
		l.og("\tTotal data in '{}': {}".format(sc.dm.filename, sc.dm.count()))
		l.og()

if __name__ == "__main__":
	main(len(sys.argv), sys.argv)