from my_log import *

class My_SQL(object):
	import mysql.connector as mysql
	import traceback

	MASK=0x00000001

	def init(self):
		self.host = None
		self.usr = None
		self.passwd = None
		self.log = None
		self.conn = None
		self.db = None
		self.commit_on_close = False
		self.mask = My_SQL.MASK
		self.error = None
		self.cursor = None

	def __init__(self, host=None, usr=None, passwd=None, db_name=None, log=None, commit_on_close=False, mask=None):
		self.init()

		if log is None:
			self.log = my_log(verbosity=0)
		else:
			self.log = log

		if commit_on_close:
			self.commit_on_close = True

		if host is not None:
			self.set_host(host)

		if usr is not None:
			self.set_user_name(usr)

		if passwd is not None:
			self.set_user_pwd(passwd)

		if db_name is not None:
			self.set_db_name(db_name)

		if mask is not None:
			self.mask = mask

	def __del__(self):
		self.close_connection()

	def _error_macro(self, msg, verbosity=0, frameinfo=None):
		self.error = msg

		if frameinfo is None:
			frameinfo =  getframeinfo(stack()[1][0])

		self.log.out(self.error, ERROR, v=verbosity, mask=self.mask, frameinfo=frameinfo)

	def close_connection(self):
		if self.conn is not None:
			if self.commit_on_close:
				self.log.out("Commiting on close.", WARNING, v=1, mask=self.mask)
				self.conn.commit()

			self.conn.close()
			self.conn = None
			return True
		else:
			return False

	'''
		The data passed to this function is used for the connect command below.
	'''
	def set_host(self, host):
		if host is not None:
			self.host = str(host)
			if self.conn is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self._error_macro("SQL host can not be set to None", fi=getframeinfo(currentframe()))
			return False

	'''
		The data passed to this function is used for the connect command below.
	'''
	def set_db_name(self, db_name):
		if db_name is not None:
			self.db_name = str(db_name)
			if self.conn is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self._error_macro("SQL db can not be set to None", fi=getframeinfo(currentframe()))
			return False

	'''
		The data passed to this function is used for the connect command below.
	'''
	def set_user_name(self, user):
		if user is not None:
			self.usr = str(user)
			if self.conn is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self._error_macro("SQL user name can not be set to None", fi=getframeinfo(currentframe()))
			return False

	'''
		The data passed to this function is used for the connect command below.
	'''
	def set_user_pwd(self, pwd):
		if pwd is not None:
			self.pwd = str(pwd)
			if self.conn is not None:
				self.log.out("Already connect to sql server. You must disconnect and reconnect for this change to take affect.", WARNING, mask=self.mask)
			return True
		else:
			self._error_macro("SQL user password can not be set to None", fi=getframeinfo(currentframe()))
			return False

	def connect(self):
		if self.conn is None:
			if self.db_name is not None:
				self.conn = My_SQL.mysql.connect(host=self.host,
												user=self.usr,
											    passwd=self.pwd,
											    database=self.db_name)
			else:
				self.conn = My_SQL.mysql.connect(host=self.host,
											    user=self.usr,
											    passwd=self.pwd)
			if self.conn:
				if self.db_name is not None:
					self.log.out("Connected to the server: %s (%s)" % (self.host, self.db_name), DEBUG, v=1, mask=self.mask)
				else:
					self.log.out("Connected to the server: %s" % self.host, DEBUG, v=1, mask=self.mask)


				self.cursor = self.conn.cursor()
				if self.cursor:
					return self.query("START TRANSACTION")
				else:
					self._error_macro("Failed why attempting to create a cursor.", fi=getframeinfo(currentframe()))
					return False
			else:
				self._error_macro("Failed to connect to sql server: %s" % self.host, fi=getframeinfo(currentframe()))
				return False
		else:
			self._error_macro("SQL user password can not be set to None", fi=getframeinfo(currentframe()))
			return False


	def last_error(self):
		return self.error

	def query(self, query, data=None):
		if self.conn is not None:
			if self.cursor is not None:
				if data is not None:
					if type(data) is not tuple:
						data = (data)

				self.cursor.execute(query, data)
				return True
			else:
				self._error_macro("Cursor handle was set to None", fi=getframeinfo(currentframe()))
				return False
		else:
			self._error_macro("Query failed because there is no active connection", fi=getframeinfo(currentframe()))
			return False

	def create_db(self, db_name):
		if db_name is not None:
			return self.query("CREATE DATABASE IF NOT EXISTS "+str(db_name))
		else:
			self._error_macro("Database name cannot be None.", fi=getframeinfo(currentframe()))
			return False

	def select_db(self, db_name):
		if db_name is not None:
			db_name = str(db_name)

			server_databases = self.list_databases()
			if server_databases is not None:
				if db_name in server_databases:
					return self.query("USE "+str(db_name))
				else:
					self._error_macro('Database: '+ db_name + ' not found on the server.', fi=getframeinfo(currentframe()))
					return False
			else:
				self._error_macro('list_database return None.', fi=getframeinfo(currentframe()))
				return False
		else:
			self._error_macro("Database name cannot be None.", fi=getframeinfo(currentframe()))
			return False

	def list_databases(self):
		if self.query('SHOW DATABASES'):
			rows = self.cursor.fetchall()
			data = []
			for line in rows:
				data.append(line[0])
			return data
		else:
			return None

	def list_tables(self, db_name=None):
		if db_name is None:
			query = 'SELECT TABLE_NAME FROM information_schema.tables'
		else:
			query = 'SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA="' + db_name + '"'

		if self.query(query):
			rows = self.cursor.fetchall()
			data = []
			for line in rows:
				data.append(line[0])
			return data
