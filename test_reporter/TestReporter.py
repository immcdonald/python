import os, sys
import argparse
import user

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *

class TestReporter(My_SQL):

	def init(self):
		super(TestReporter, self).init()
		self.selected_project = None
		self.report_user_name = None

		#Identififiers
		self.exec_id = None
		self.variant_id = None
		self.suite_id = None

		# Dictionaries
		self.project_dict = {}
		self.arch_dict = {}
		self.tag_dict = {}
		self.crash_type_dict = {}
		self.suite_dictionary = {}


	def __init__(self, host, usr, passwd, db_name, log=None, commit_on_close=False, mask=None):
		self.init()
		super(TestReporter, self).__init__(host, usr, passwd, db_name, log, commit_on_close, mask)

	def connect(self):
		super(TestReporter, self).connect()
		self.refresh_projects_list()
		self.refresh_arch_list()

	def set_report_user_name(self, user_name):
		if user_name is not None:
			if len(user_name) > 1:
				if len(user_name) <= 45:
					self.report_user_name = user_name
				else:
					self._error_macro("User name is to long")
					return False
			else:
				self._error_macro("User name is to short")
				return False
		else:
			self._error_macro("user_name can not be None")
			return False

	'''

	'''
	def _common_checks(self, project=False, user_name=False, exec_id=False, variant_id=False, connected=True):
		frameinfo =  getframeinfo(stack()[1][0])

		if connected:
			if self.conn is None:
				self._error_macro("Please call connect before this this function.", frameinfo=frameinfo)
				return False

		if project:
			if self.selected_project is None:
				self._error_macro("Please select a project before calling this function.", frameinfo=frameinfo)
				return False

		if user_name:
			if self.report_user_name is None:
				self._error_macro("Please set a username before calling this function.", frameinfo=frameinfo)
				return False

		if exec_id:
			if self.exec_id is None:
				self._error_macro("Please register an exec_id before calling this function.", frameinfo=frameinfo)
				return False

		if variant_id:
			if self.variant_id is None:
				self._error_macro("Please register a variant before calling this function", frameinfo=frameinfo)
				return False

		return True

	def refresh_projects_list(self):
		if self._common_checks():
			self.project_dict = {}

			query = "SELECT project_id, name from project"
			self.query(query)

			for row in self.cursor:
				self.project_dict[row[1]] = row[0]
			return True
		else:
			return False

	'''
	Add a project to the database. Note: the new project name automatically becomes the
	default project.
	'''
	def register_project(self, project_name, description, html_style=None):
		if self._common_checks():
			if project_name is not None:
				if project_name in self.project_dict:
					self.log.out(project_name + " already registered in the database", WARNING, v=2)
					self.select_project(project_name)
					return True
				else:
					if len(project_name) < 3:
						self._error_macro("Project name is to short")
						return False

					if len(project_name) > 45:
						self._error_macro("Project name is to long")
						return False

					if description is None:
						self._error_macro("Project description can not be None")
						return False

					if len(description) < 10:
						self._error_macro("Project description is to short")
						return False

					if len(description) > 65535:
						self._error_macro("Project description is to long")
						return False

					if html_style is None:
						query = "INSERT INTO project (name, description, created) VALUES (%s, %s, NOW())"
						data =  (project_name, description)
					else:
						query = "INSERT INTO project (name, description, project_html_style, created) VALUES (%s, %s, %s, NOW())"
						data =  (project_name, description, html_style)

					self.query(query,data)

					self.project_dict[project_name] = self.cursor.lastrowid

					self.select_project(project_name)

					self.log.out("(" + project_name + ") registered as project name.", v=1)
					return True

			else:
				self._error_macro("Project name cannot be None")
				return False
		else:
			return False

	def select_project(self, project_name):
		if self._common_checks():
			if project_name in self.project_dict:
				self.selected_project = project_name
				self.refresh_tags()
				self.refresh_crash_type()

				self.log.out("(" + project_name + ") is now the active project")
			else:
				self._error_macro("(" + project_name + ") does not appear in the database. Try reconnecting or calling refresh_projects_list")
				return False
		else:
			return False

	def refresh_arch_list(self):
		if self._common_checks():
			self.arch_dict={}
			query = "SELECT arch_id, name from arch"
			self.query(query)
			for row in self.cursor:
				self.arch_dict[row[1]] = row[0]
			return True
		else:
			return False

	def add_arch(self, arch, html_style=None):
		if self._common_checks():
			if arch is not None:
				if arch in self.arch_dict:
					self.log.out('Arch (' + arch + ") already registered in the database", WARNING, v=1)
				else:
					if len(arch) < 1:
						self._error_macro("Arch is to short")
						return False

					if len(arch) > 45:
						self._error_macro("Arch is to long")
						return False

					if html_style is None:
						query = "INSERT INTO arch (name, created) VALUES (%s, NOW()))"
						data = (arch,)
					else:
						query = "INSERT INTO arch (name, arch_html_style, created) VALUES (%s, %s, NOW())"
						data = (arch, html_style)

					self.query(query, data)

					self.arch_dict[arch] = self.cursor.lastrowid

					self.log.out("Arch (" + arch + ")  added to the database.", v=1)

				return True
			else:
				self._error_macro("Arch can not be None.")
				return False
		else:
			return False

	def refresh_tags(self):
		if self._common_checks(project=True):
			self.tag_dict = {}
			query = "SELECT tag_id, result from tag WHERE fk_project_id=" + str(self.project_dict[self.selected_project]) + " ORDER BY tag_id ASC"
			self.query(query)
			for row in self.cursor:
				self.tag_dict[row[1]] = row[0]
			return True
		else:
			return False

	def add_tag(self, tag, comment=None, html_style=None):
		if self._common_checks(project=True):
			if tag is not None:
				if tag in self.tag_dict:
					self.log.out('result tag (' + tag + ") already in the database", WARNING, v=1)
				else:
					value  = ["fk_project_id"]
					format = ["%s"]
					data = [self.project_dict[self.selected_project]]

					if len(tag) < 2:
						self._error_macro("Tag is to short")
						return False

					if len(tag) > 15:
						self._error_macro("Tag is to long")
						return False

					value.append("result")
					format.append("%s")
					data.append(tag)

					if comment is not None:
						if len(comment) < 5:
							self._error_macro("Comment is to short")
							return False

						if len(comment) > 65535:
							self._error_macro("comment is to long")
							return False

						value.append("comment")
						format.append("%s")
						data.append(comment)

					if 	html_style is not None:
						if len(html_style) < 2:
							self._error_macro("html style is to short")
							return False

						if len(html_style) > 65535:
							self._error_macro("html style is to long")
							return False

						value.append("tag_html_style")
						format.append("%s")
						data.append(html_style)

					query = "INSERT INTO tag (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
					self.query(query, data)

					self.tag_dict[tag] = self.cursor.lastrowid

					self.log.out("Result tag (" + tag + ")  added to the database.", v=1)

					return True
			else:
				self._error_macro("Result tag can not be None.")
				return False
		else:
			return False

	def refresh_crash_type(self):
		if self._common_checks(project=True):
			self.crash_type_dict = {}
			query = "SELECT crash_id, name from crash_type WHERE fk_project_id=" + str(self.project_dict[self.selected_project]) + " ORDER BY crash_id ASC"
			self.query(query)
			for row in self.cursor:
				self.crash_type_dict[row[1]] = row[0]
			return True
		else:
			return False


	def add_crash_type(self, crash_type, comment, html_style=None):
		if self._common_checks(project=True):
			if crash_type is not None:
				if crash_type in self.crash_type_dict:
					self.log.out('crash type (' + crash_type + ") already in the database", WARNING, v=1)
				else:
					value  = ["fk_project_id"]
					format = ["%s"]
					data = [self.project_dict[self.selected_project]]

					if len(crash_type) < 2:
						self._error_macro("Crash type is to short")
						return False

					if len(crash_type) > 15:
						self._error_macro("Crash type is to long")
						return False

					value.append("name")
					format.append("%s")
					data.append(crash_type)

					if comment is not None:
						if len(comment) < 5:
							self._error_macro("Comment is to short")
							return False

						if len(comment) > 65535:
							self._error_macro("comment is to long")
							return False

						value.append("comment")
						format.append("%s")
						data.append(comment)

					if 	html_style is not None:
						if len(html_style) < 2:
							self._error_macro("html style is to short")
							return False

						if len(html_style) > 65535:
							self._error_macro("html style  is to long")
							return False

						value.append("tag_html_style")
						format.append("%s")
						data.append(html_style)

					query = "INSERT INTO crash_type (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"
					self.query(query, data)

					self.crash_type_dict[crash_type] = self.cursor.lastrowid

					self.log.out("Crash type (" + crash_type + ")  added to the database.", v=1)

					return True
			else:
				self._error_macro("Crash type can not be None.")
				return False
		else:
			return False

	def register_exec(self):
		if self._common_checks(project=True, user_name=True):
			value  = ["fk_project_id"]
			format = ["%s"]
			data = [self.project_dict[self.selected_project]]
			value.append("user_name")
			format.append("%s")
			data.append(self.report_user_name)
			query = "INSERT INTO exec (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
			self.query(query, data)
			self.exec_id = self.cursor.lastrowid
			self.log.out("Exec registered as (" + str(self.exec_id) + ").", v=0)
			return True
		else:
			return False

	def set_exec_id(self, exec_id):
		if self._common_checks(project=True):
			query = 'SELECT exec_id FROM exec WHERE fk_project_id=' + str(self.project_dict[self.selected_project]) +  ' and exec_id=' + str(exec_id)
			self.query(query)
			rows = self.cursor.fetchall()

			if len(rows) == 1:
				self.exec_id = exec_id
				self.refresh_suite_names()
				return True
			else:
				self._error_macro("Execution ID: " + str(exec_id) + " could not be found for project: " + self.selected_project)
				return False
		else:
			return False

	def register_src(self, source_type, url_path, unique_id, description=None):
		allowed_source_types = ['build', 'cvs', 'svn', 'git', 'other', 'path']
		if self._common_checks(project=True, exec_id=True):
			if source_type in allowed_source_types:
				value = []
				format = []
				data = []

				value.append("fk_exec_id")
				format.append("%s")
				data.append(self.exec_id)

				value.append("src_type")
				format.append("%s")
				data.append(source_type)

				if len(url_path) < 5:
					self._error_macro("url/path is to short")
					return False

				if len(url_path) > 65535:
					self._error_macro("url/path is to long")
					return False

				value.append("url_path")
				format.append("%s")
				data.append(url_path)

				if len(unique_id) < 5:
					self._error_macro("unique id is to short")
					return False

				if len(unique_id) > 65535:
					self._error_macro("unique id is to long")
					return False

				value.append("unique_id")
				format.append("%s")
				data.append(unique_id)

				if description is not None:
					if len(description) < 5:
						self._error_macro("description is to short")
						return False

					if len(description) > 65535:
						self._error_macro("description is to long")
						return False

					value.append("description")
					format.append("%s")
					data.append(description)

				# check to see if it already exits
				query = "SELECT src_id FROM src WHERE " + "=%s and ".join(value) + "=%s"
				self.query(query, data)

				rows = self.cursor.fetchall()
				if len(rows) > 0:
					self.log.out(source_type + "> " + url_path + ":" + unique_id + " is already in the database.", WARNING, v=1)
				else:
					query = "INSERT INTO src (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"
					self.query(query, data)
					self.log.out(source_type + "> " + url_path + ":" + unique_id + " added to the database.")
				return True
			else:
				self._error_macro(str(source_type) + " is not a valid source type")
				return False

	def refresh_suite_names(self):
		if self._common_checks(project=True, exec_id=True):
			self.suite_dictionary = {}
			query = "SELECT test_suite_id, suite_name from test_suite WHERE fk_exec_id=" + str(self.exec_id) + " ORDER BY suite_name"
			self.query(query)
			for row in self.cursor:
				self.suite_dictionary[row[1]] = row[0]
			return True

	def add_test_suite(self, suite_name, description=None, html_style=None):
		if self._common_checks(project=True, exec_id=True):
			if suite_name in self.suite_dictionary:
				self.log.out('Suite name (' + suite_name + ") already in the database.", WARNING, v=0)
				self.suite_id =  self.suite_dictionary[suite_name];
				return True
			else:
				value = []
				format = []
				data = []

				value.append("fk_project_id")
				format.append("%s")
				data.append(self.project_dict[self.selected_project])

				value.append("fk_exec_id")
				format.append("%s")
				data.append(self.exec_id)

				if len(suite_name) < 3:
					self._error_macro("suite name is to short")
					return False

				if len(suite_name) > 45:
					self._error_macro("suite name is to long")
					return False

				value.append("suite_name")
				format.append("%s")
				data.append(suite_name)

				if description is not None:
					if len(description) < 5:
						self._error_macro("description is to short")
						return False

					if len(description) > 65535:
						self._error_macro("description is to long")
						return False

					value.append("description")
					format.append("%s")
					data.append(description)

				if 	html_style is not None:
						if len(html_style) < 2:
							self._error_macro("html style is to short")
							return False

						if len(html_style) > 65535:
							self._error_macro("html style is to long")
							return False

						value.append("tag_html_style")
						format.append("%s")
						data.append(html_style)

				query = "INSERT INTO test_suite (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
				self.query(query, data)

				self.suite_dictionary[suite_name] = self.cursor.lastrowid

				self.log.out("Test Suite (" + suite_name + ")  added to the database.", v=1)
				return True

		else:
			return False

exec_id=1

rdb = TestReporter("serenity.bts.rim.net", user.sql_name, user.sql_password, db_name="result_db");

rdb.connect()
rdb.set_report_user_name("iamcdonald")

rdb.select_db("result_db")

rdb.add_arch("x86","Red")
rdb.add_arch("sh", "Green")
rdb.add_arch("mips", "Black")
rdb.add_arch("ppc", "Blue")
rdb.add_arch("arm", "Yellow")
rdb.add_arch("x86_64", "Purple")
rdb.add_arch("aarch64", "Cyan")

rdb.register_project("Mainline", "Mainline/Trunk Regression Thread", "Red")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XPASS status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a XPASS status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a XPASS status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")

rdb.register_project("dev_64b", "64 Bit initial development project", "Yellow")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XPASS status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a XPASS status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a XPASS status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")

rdb.register_project("Qnx_sdp_7", "Qnx 7.0 SDP Branch")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XPASS status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a XPASS status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a XPASS status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")

rdb.select_project("Mainline");

if exec_id is None:
	rdb.register_exec()
else:
	rdb.set_exec_id(exec_id)

rdb.add_test_suite("testware_sanitytest")
rdb.add_test_suite("testware_Benchmark", "Benchmark Sanity tests")
rdb.add_test_suite("testware_aps", "APS specific tests")


rdb.register_src("svn", "http://svn.ott.qnx.com/qa/mainline/testware", "123457")
rdb.commit()
