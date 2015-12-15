from pprint import pformat

class dummy_file_op():
	def __init__(self, data):
		self.data_counter = 0
		self.data_size = len(data)
		self.data = data

	def read(self, blocksize):
		if self.data_counter >= self.data_size:
			return None
		else:
			block = self.data[self.data_counter:self.data_counter+blocksize]
			self.data_counter = self.data_counter + (blocksize)
			return block

class my_ftp():
	DEFAULT_LIST_REGEX_EXPRESSION = '^(?P<type>[-|d|l])(?P<owner_read>[-|r])(?P<owner_write>[-|w])(?P<owner_exec>[-|x])(?P<group_read>[-|r])(?P<group_write>[-|w])(?P<group_exec>[-|x])(?P<other_read>[-|r])(?P<other_write>[-|w])(?P<other_exec>[-|x])\s+(?P<number>\d+)\s+(?P<owner>[a-zA-z0-9\_\-]+)\s+(?P<group>[a-zA-z0-9\_\-]+)\s+(?P<size>\d+)\s+(?P<month>[a-zA-z0-9\_\-]+)\s+(?P<day>\d+)\s+(?P<time_year>[0-9\:]+)\s+(?P<name>.*)$'

	from ftplib import FTP
	import re
	import os

	def init(self):
		self.ftp = None
		self.host = None
		self.user_name = None
		self.password = None
		self.ftp_debug_level = 2  #2 or higher produces the max amount of debug logs from ftplib

	def __init__(self, host, user_name, password,
				 list_expression=DEFAULT_LIST_REGEX_EXPRESSION, ftp_debug_level=0, log=None):
		self.init()
		self.dir_list_pattern = my_ftp.re.compile(list_expression)
		self.ftp_debug_level = ftp_debug_level
		self.host = host
		self.user_name = user_name
		self.password = password

	def __del__(self):
		self.close()

	def close(self):
		if self.ftp is not None:
			self.ftp.quit()
			del self.ftp
			self.ftp = None

	def connect(self,host=None, user_name=None, password=None):
		if self.ftp is None:
			if host is not None:
				self.host = host

			if user_name is not None:
				self.user_name = user_name

			if password is not None:
				self.password = password

			self.ftp = my_ftp.FTP(self.host)
			self.ftp.set_debuglevel(self.ftp_debug_level)
			self.ftp.login(self.user_name, self.password)
			return True
		else:
			print "Error: FTP object already created, call close to destroy the current one."
			return False

	def dir_list(self):
		if self.ftp is not None:
			data = []
			file_info = {}

			self.ftp.dir(data.append)
			for line in data:
				result = self.dir_list_pattern.search(line)
				if result is not None:
					file_info[result.groupdict()["name"]] = result.groupdict()
			return file_info
		else:
			print("Not connected!")
			return None

	def chdir(self, directory):
		if self.ftp is not None:
			try:
				self.ftp.cwd(directory)
			except:
				print "Unable to change to %s" % directory
				return False
			return True
		else:
			print("Not connected!")
			return None

	def mkdir(self, directory, check_exists=False):
		if self.ftp is not None:
			if check_exists:
				dir_list = self.dir_list()
				if directory in dir_list:
					return True

			try:
				self.ftp.mkd(directory)
			except:
				print "Unable to make directory %s" % directory
				return False
			return True
		else:
			print("Not connected!")
			return None

	def rmdir(self, directory):
		if self.ftp is not None:
			try:
				self.ftp.rmd(directory)
			except:
				print "Unable to remove directory %s" % directory
				return False
			return True
		else:
			print("Not connected!")
			return None

	def del_file(self, file_name):
		if self.ftp is not None:
			try:
				self.ftp.delete(file_name)
			except:
				print "Unable to delete file %s" % file_name
				return False
			return True
		else:
			print("Not connected!")
			return None

	def bindary_data_transfer_2_file(self, file_name, data):
		if len(data) > 0:
			if self.ftp is not None:
				dummy_file = dummy_file_op(data);
				self.ftp.storbinary("STOR "+file_name, dummy_file)
				del dummy_file

				return True
			else:
				print("Not connected!")
				return False

		else:
			print("Data size can not be zero")
			return False

	def text_data_transfer_2_file(self, file_name, data):
		if len(data) > 0:

			if self.ftp is not None:
				dummy_file = dummy_file_op(data);
				self.ftp.storbinary("STOR "+file_name, dummy_file)
				del dummy_file
				return True
			else:
				print("Not connected!")
				return False

		else:
			print("Data size can not be zero")
			return False

	def binary_file_transfer_2_file(self, file_name, to_file_name=None):
		if self.ftp is not None:

			if to_file_name is None:
				to_file_name = my_ftp.os.path.basename(file_name)

			with open(file_name, "rb") as fp:
				self.ftp.storbinary("STOR "+to_file_name, fp)
			return True
		else:
			print("Not connected!")
			return False
