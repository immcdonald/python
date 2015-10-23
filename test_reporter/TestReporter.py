import os, sys
import argparse
parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *

class TestReporter():
	import mysql.connector as mysql

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
			self.log = my_log(verbosity=1)
		else:
			self.log = log

		if sql_host is not None:
			self.set_sql_host(sql_host)

		if sql_usr is not None:
			self.set_sql_user_name(sql_usr)

		if sql_pwd is not None:
			self.set_sql_user_pwd(sql_pwd)

		if db_name is not None:
			self.set_sql_db(db_name)

		if mask is not None:
			self.mask = mask;

	def __del__(self):
		self.close_connection()

	def close_connection(self):
		if self.sql is not None:
			self.sql.close()
			self.sql = None
			return True
		else:
			self.log.out("SQL close requested on already close connection.", DEBUG, 1, mask=self.mask)
			return False

	def set_sql_host(self, sql_host):
		if sql_host is not None:
			self.sql_host = sql_host
			if self.sql is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log.out("SQL host can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_db(self, sql_db):
		if sql_db is not None:
			self.db_name = sql_db
			if self.sql is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log.out("SQL db can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_user_name(self, sql_user):
		if sql_user is not None:
			self.sql_usr = sql_user
			if self.sql is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log.out("SQL user name can not be set to None", ERROR, mask=self.mask)
			return False

	def set_sql_user_pwd(self, sql_pwd):
		if sql_pwd is not None:
			self.sql_pwd = sql_pwd
			if self.sql is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self.log.out("SQL user password can not be set to None", ERROR, mask=self.mask)
			return False

	def sql_connect(self):
		if self.sql is None:
			self.sql = TestReporter.mysql.connect(host=self.sql_host,
                                               	  user=self.sql_usr,
                                               	  passwd=self.sql_pwd)

			if self.sql:
				self.log.out("Connected to the server: %s" % self.sql_host, INFO, mask=self.mask)
				return True
			else:
				self.log.out("Failed to connect to sql server: %s" % self.sql_host, ERROR, mask=self.mask)
				return False
		else:
			self.log.out("SQL user password can not be set to None", ERROR, mask=self.mask)
			return False


dog = TestReporter("serenity.bts.rim.net", "root", "q1!w2@e3#");

#dog.sql_connect()






