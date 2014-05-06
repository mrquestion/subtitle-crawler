# -*- coding: utf-8 -*-

import sqlite3 as sqlite

from . import Tools

class DatabaseManager:
	CREATE_SQL = "\
		Create table If not exists SUBTITLE(\
			index_subtitle integer,\
			subtitle_hash text,\
			subtitle_key text,\
			subtitle_category_url text,\
			subtitle_post_url text,\
			subtitle_file_url text,\
			subtitle_file_name text,\
			subtitle_insert_time text\
		)\
	"
	ADD_SQL = "\
		Insert into SUBTITLE(\
			index_subtitle,\
			subtitle_hash,\
			subtitle_key,\
			subtitle_category_url,\
			subtitle_post_url,\
			subtitle_file_url,\
			subtitle_file_name,\
			subtitle_insert_time\
		)\
		Select\
			ifnull(max(index_subtitle), 0)+1,\
			?,\
			?,\
			?,\
			?,\
			?,\
			?,\
			datetime('now', 'localtime')\
		From\
			SUBTITLE\
	"
	FIND_SQL = "\
		Select\
			index_subtitle\
		From\
			SUBTITLE\
		Where\
			subtitle_hash = ?\
	"
	COUNT_SQL = "Select count(index_subtitle) From SUBTITLE"

	def __init__(self, filename="{}.db".format(Tools.timestamp())):
		if not filename.endswith(".db"):
			filename = "{}.db".format(filename)

		self.filename = filename

		db = sqlite.connect(self.filename)
		db.execute(self.CREATE_SQL)
		db.commit()
		db.close()

	def add(self, key, category, post, file, filename):
		db = sqlite.connect(self.filename)
		filehash = Tools.md5("{}:{}".format(post, filename))
		result = db.execute(self.ADD_SQL, (filehash, key, category, post, file, filename))
		db.commit()
		db.close()
		return result.rowcount

	def find(self, post, filename):
		db = sqlite.connect(self.filename)
		filehash = Tools.md5("{}:{}".format(post, filename))
		rs = db.execute(self.FIND_SQL, (filehash, ))
		data = rs.fetchone()
		db.close()
		return data

	def count(self):
		db = sqlite.connect(self.filename)
		rs = db.execute(self.COUNT_SQL)
		data = rs.fetchone()
		count = data[0]
		db.close()
		return count