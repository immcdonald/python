import os, sys
import argparse
parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *

class TestReporter():

	TEST_REPORTER_MASK=0x00000001

	def init(self):
		self.db_name = "test_report_db"
		self.sql_host = "localhost"
		self.sql_usr = "root"
		self.sql_pwd = None
		self.log = None
		self.mask = TestReporter.TEST_REPORTER_MASK;
		self.sql = None

	def __init__(self,
				 sql_host,
				 sql_usr,
				 sql_pwd,
				 bug_tool=None,
				 db_name=None,
				 log=None,
				 mask=None):

		self.init()

		if log is None:
			self.log = my_log()
		else:
			self.log = log

		if sql_host is not None:
			self.set_sql_host(sql_host)

		if sql_usr is not None:
			self.set_sql_user_name(sql_usr)

		if sql_pwd is not None:
			self.set_sql_user_name(sql_pwd)

		if db_name is not None:
			self.set_sql_db(db_name)

		if mask is not None:
			self.mask = mask;



	def __del__(self):
		pass

	def set_sql_host(self, sql_host):
		if sql_host is not None:
			self.sql_usr = sql_host
			if self.sql is not None:
				self.log("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log("SQL host can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_db(self, sql_db):
		if sql_db is not None:
			self.db_name = sql_db
			if self.sql is not None:
				self.log("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log("SQL db can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_user_name(self, sql_user):
		if sql_user is not None:
			self.sql_usr = sql_user
			if self.sql is not None:
				self.log("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log("SQL user name can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_user_pwd(self, sql_pwd):
		if sql_user is not None:
			self.sql_pwd = sql_pwd
			if self.sql is not None:
				self.log("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log("SQL user password can not be set to None", ERROR, mask=self.mask)
			return False

	def sql_connect(self):
