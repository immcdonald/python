import os, sys
import argparse
import user
import gzip
import shutil

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *
from my_ftp import *

class TestReporter(My_SQL):

	def reset_project_child(self):
		self.project_child_id = None
		self.result_tag_dict = {}
		self.crash_type_dict = {}

	def reset_project_root(self):
		self.reset_project_child()
		self.project_root_id = None

	'''
	Desc: Basic init funciton.

		-= Params =-
		N/A

		-= Returns =-
		N/A
	'''
	def init(self):
		super(TestReporter, self).init()
		self.reset_project_root()
		self.line_marker_dict = {}

	'''
	Desc: Constructor for this class

		-= Params =-
	   host 	- sql host
	   usr 		- sql user name
	   passwd 	- sql password
	   db_name 	- database name


		-= Returns =-
		N/A
	'''
	def __init__(self, host, usr, passwd, db_name, log=None, commit_on_close=False, mask=None):
		self.init()
		super(TestReporter, self).__init__(host, usr, passwd, db_name, log, commit_on_close, mask)
		self.pre_check = True

	'''
	Desc:

		-= Params =-
		N/A

		-= Returns =-
		N/A
	'''
	def connect(self):
		rc = super(TestReporter, self).connect()
		if rc:
			rc = self.load_line_marker_types()
		return rc

	def common_check(self, project_root=False, project_child=False):
		if self.conn is None:
			self._error_macro("Not connected to the database. Please call connect before this call.")
			return False

		if project_root:
			if self.project_root_id is None:
				self._error_macro("Project root not selected. Please call select_project_root to select the project")
				return False

		if project_child:
			if self.project_child_id is None:
				self._error_macro("Project child not selected. Please call select_project_child to select the project")
				return False
		return True

	def history(self, string, type_enum="general", entry_enum="manual", use_child_id=True, pre_check=False):
		valid_type_enum = ['general', 'error', 'project_root_added', 'project_child_added', 'result_tag', 'target' ,'suite', 'test', 'exec', "crash_type"]
		valid_entry_enum = ['auto', 'manual']

		if self.pre_check:
			pre_check = True

		if self.common_check(project_root=True, project_child=use_child_id):
			fields = []
			data = []

			fields.append("fk_project_root_id")
			data.append(self.project_root_id)

			if use_child_id:
				fields.append("fk_project_child_id")
				data.append(self.project_child_id)

			if entry_enum not in valid_entry_enum:
				self._error_macro(entry_enum + " is not a valid entry enum.")
				return -1
			else:
				fields.append("entry_enum")
				data.append(entry_enum)

			if type_enum not in valid_type_enum:
				self._error_macro(type_enum + " is not a valid type enum.")
				return -1
			else:
				fields.append("type_enum")
				data.append(type_enum)

			fields.append("comment")
			data.append(string)

			if pre_check:
				history_rows = self.select("history_id", "history", fields, data)

				if self.size(history_rows) > 0:
					return history_rows[0][0]

			history_id = self.insert("history", fields, data, created=True)

			return history_id
		else:
			return -1

	def add_project_root(self,  project_root, comment=None):
		project_root = project_root.replace(" ", "_")

		if self.common_check():
			if self.size(project_root) > 45:
				self._error_macro("Project name is too long.")
				return -1

			if self.size(project_root) > 0:
				fields = []
				data = []

				fields.append("name")
				data.append(project_root)

				project_rows = self.select("project_root_id", "project_root", fields, data)

				if self.size(project_rows) > 0:
					self.reset_project_root()
					self.project_root_id = project_rows[0][0]
				else:
					if comment:
						fields.append("comment")
						data.append(comment)

					db_id = self.insert("project_root", fields, data, True)

					if db_id > 0:
						self.reset_project_root()
						self.project_root_id = db_id
						self.history(str(project_root) + " added as project root.", "project_root_added", "auto", use_child_id=False)
					else:
						return -1

				return self.project_root_id
			else:
				self._error_macro("Project name is too short.")
				return -1
		else:
			return -1

	def select_project_root(self, project_root):
		project_root = project_root.replace(" ", "_")
		if self.common_check():
			fields = []
			data = []

			fields.append("name")
			data.append(project_root)

			project_rows = self.select("project_root_id", "project_root", fields, data)

			if self.size(project_rows) > 0:
				self.reset_project_root()
				self.project_root_id = project_rows[0][0]
				return self.project_root_id
			else:
				self._error_macro(project_root + " not found in the database")
				return -1

		else:
			return -1


	def add_project_child(self, project_child, attach_path, ftp_host, ftp_user_name, ftp_password, comment=None):
		project_child = project_child.replace(" ", "_")
		attach_path = attach_path.rstrip("/")
		attach_path = attach_path.rstrip("\\")

		if self.common_check(project_root=True):

			if self.size(project_child) > 60:
				self._error_macro("Project child is too long.")
				return -1

			if self.size(project_child) > 0:
				fields = []
				data = []

				fields.append("fk_project_root_id")
				data.append(self.project_root_id)

				fields.append("name")
				data.append(project_child)

				project_rows = self.select("project_child_id", "project_child", fields, data)

				if self.size(project_rows) > 0:
					self.reset_project_child()
					self.project_child_id = project_rows[0][0]
				else:
					if self.size(attach_path) > 0:
						if self.size(attach_path) < 65535:
							fields.append("attach_path")
							data.append(attach_path)
						else:
							self._error_macro("The attachment path is too long")
							return -1
					else:
						self._error_macro("The attachment path is too short")
						return -1

					if self.size(ftp_host) > 0:
						if self.size(ftp_host) < 65535:
							fields.append("ftp_host")
							data.append(ftp_host)
						else:
							self._error_macro("The ftp host path is too long")
							return -1
					else:
						self._error_macro("The ftp host path is too short")
						return -1

					if self.size(ftp_user_name) > 0:
						if self.size(ftp_user_name) < 65535:
							fields.append("ftp_user_name")
							data.append(ftp_user_name)
						else:
							self._error_macro("The ftp user name is too long")
							return -1
					else:
						self._error_macro("The ftp user name is too short")
						return -1


					if self.size(ftp_password) > 0:
						if self.size(ftp_password) < 65535:
							fields.append("ftp_password")
							data.append(ftp_password)
						else:
							self._error_macro("The ftp password is too long")
							return -1
					else:
						self._error_macro("The ftp password is too short")
						return -1

					if comment:
						if self.size(comment) > 0:
							if self.size(comment) < 65535:
								fields.append("comment")
								data.append(comment)
							else:
								self._error_macro("The comment is too long")
								return -1
						else:
							self._error_macro("The comment is too short")
							return -1

					db_id = self.insert("project_child", fields, data, True)

					if db_id > 0:
						self.reset_project_child()
						self.project_child_id = db_id

						self._load_child_project_properties()

						self.history(str(project_child) + " added as project child.", "project_child_added", "auto")
					else:
						return -1

				return self.project_root_id
			else:
				self._error_macro("Project_child is too short.")
				return -1
		else:
			return -1

	def select_project_child(self, project_child):
		project_child = project_child.replace(" ", "_")

		if self.common_check(project_root=True):
			fields = []
			data = []

			fields.append("name")
			data.append(project_child)
			project_rows = self.select("project_child_id", "project_child", fields, data)

			if self.size(project_rows) > 0:
				self.reset_project_child()
				self.project_child_id = project_rows[0][0]

				#Reload things for the selected project:
				self._load_child_project_properties()

				return self.project_child_id
			else:
				self._error_macro(str(project_child) + " not found in the database.")
				return -1
		else:
			return -1

	def _load_child_project_properties(self):
		#Reload things for the selected project:
		self.load_result_tags()
		self.load_crash_types()


	def add_arch(self, arch):
		arch = arch.replace(" ", "_")

		if self.common_check():
			if self.size(arch) > 0:
				if self.size(arch) < 46:
					fields = []
					data = []

					fields.append("name")
					data.append(arch)

					arch_rows = self.select("arch_id", "arch", fields, data)

					if self.size(arch_rows) > 0:
						return arch_rows[0][0]
					else:
						db_id = self.insert("arch", fields, data, True)

						if db_id > 0:
							return db_id
					return -1
				else:
					self._error_macro("Arch is too long")
					return -1
			else:
				self._error_macro("Arch is too short")
				return -1
		else:
			return -1


	def load_line_marker_types(self):
		if self.common_check():
			fields = []
			fields.append("line_marker_type_id")
			fields.append("name")

			line_marker_type_rows = self.select(fields, "line_marker_type", None, None)

			if self.size(line_marker_type_rows) > 0:
				self.line_marker_dict = {}
				for row in line_marker_type_rows:
					self.line_marker_dict[row[1]] = row[0]
			return True
		else:
			return False

	def get_line_marker(self, line_marker_type, show_error=True):
		if line_marker_type in self.line_marker_dict:
			return self.line_marker_dict[line_marker_type]
		else:
			if show_error:
				self._error_macro(str(line_marker_type) + " line marker type not found. Try calling add first.")
			return -1

	def add_line_marker_type(self, line_marker_type):
		if self.common_check():
			if self.size(line_marker_type) > 0:
				if self.size(line_marker_type) < 46:

					line_marker_id = self.get_line_marker(line_marker_type, False)

					if line_marker_id > 0:
						return line_marker_id
					else:
						fields = []
						data = []

						fields.append("name")
						data.append(line_marker_type)


						db_id = self.insert("line_marker_type", fields, data, True)

						if db_id > 0:
							self.line_marker_dict[line_marker_type] = db_id
							return db_id
					return -1
				else:
					self._error_macro("Line marker type is too long")
					return -1
			else:
				self._error_macro("Line marker type is too short")
				return -1
		else:
			return -1




	def load_result_tags(self):
		if self.common_check(project_root=True, project_child=True):
			get_fields = []
			where_fields = []
			where_data = []

			get_fields.append("result_tag_id")
			get_fields.append("name")
			get_fields.append("offset")

			where_fields.append("fk_project_child_id")
			where_data.append(self.project_child_id)

			tag_result_rows = self.select(get_fields, "result_tag", where_fields, where_data)

			if self.size(tag_result_rows) > 0:
				self.result_tag_dict = {}
				for row in tag_result_rows:
					self.result_tag_dict[row[1]] = {"id":row[0], "offset": row[2]}
			return True
		else:
			return False

	def get_tag_result_id(self, tag, show_error=True):
		if tag in self.result_tag_dict:
			return self.result_tag_dict[tag]["id"]
		else:
			if show_error:
				self._error_macro(str(tag) + " result tag not found. Try calling add first.")
			return -1

	def add_result_tag(self, tag, comment=None):
		if self.common_check(project_root=True, project_child=True):
			if self.size(tag) > 0:
				if self.size(tag) < 16:

					result_id = self.get_tag_result_id(tag, False)

					if result_id > 0:
						return result_id
					else:
						fields = []
						data = []

						fields.append("name")
						data.append(tag)


						if comment:
							if self.size(comment) > 0:
								if self.size(comment) < 65535:
									fields.append("comment")
									data.append(comment)
								else:
									self._error_macro("The comment is too long")
									return -1
							else:
								self._error_macro("The comment is too short")
								return -1

						fields.append("fk_project_child_id")
						data.append(self.project_child_id)

						fields.append("offset")
						data.append(self.size(self.result_tag_dict))

						db_id = self.insert("result_tag", fields, data, True)

						if db_id > 0:
							self.history("Result tag: " + str(tag) + " added.", "result_tag", "auto")
							self.result_tag_dict[tag] = {"id":db_id, "offset": self.size(self.result_tag_dict)}
							return db_id
					return -1
				else:
					self._error_macro("Line marker type is too long")
					return -1
			else:
				self._error_macro("Line marker type is too short")
				return -1
		else:
			return -1

	def add_target(self, name, comment=None):
		if self.common_check(project_root=True, project_child=True):
			if self.size(name) > 0:
				if self.size(name) < 46:
					fields = []
					data = []

					fields.append("name")
					data.append(name)

					target_rows = self.select("target_id", "target", fields, data)

					if self.size(target_rows) > 0:
						return target_rows[0][0]
					else:
						if comment:
							if self.size(comment) > 0:
								if self.size(comment) < 65535:
									fields.append("comment")
									data.append(comment)
								else:
									self._error_macro("The comment is too long")
									return -1
							else:
								self._error_macro("The comment is too short")
								return -1

						fields.append("fk_project_child_id")
						data.append(self.project_child_id)

						db_id = self.insert("target", fields, data, True)

						if db_id > 0:
							self.history("Target: " + str(name) + " added.", "target", "auto")
							return db_id
					return -1
				else:
					self._error_macro("Target name is too long")
					return -1
			else:
				self._error_macro("Target name is too short")
				return -1
		else:
			return -1


	def add_bug_root(self, recorder_type, unique_ref, summary=None, comment=None):
		valid_record_type = ["pr", "jira"]

		if recorder_type not in valid_record_type:
			self._error_macro(str(recorder_type) + " is not a valid recorder type.")
			return -1

		if self.common_check():

			if self.size(unique_ref) > 0:
				if self.size(unique_ref) < 65535:

					fields = []
					data = []

					fields.append("recorder_enum")
					data.append(recorder_type)

					fields.append("unique_ref")
					data.append(unique_ref)

					bug_root_rows = self.select("bug_root_id", "bug_root", fields, data)

					if self.size(bug_root_rows) > 0:
						return bug_root_rows[0][0]
					else:

						if comment:
							if self.size(comment) > 0:
								if self.size(comment) < 65535:
									fields.append("comment")
									data.append(comment)
								else:
									self._error_macro("The comment is too long")
									return -1
							else:
								self._error_macro("The comment is too short")
								return -1

						if summary:
							if self.size(summary) > 0:
								if self.size(summary) < 65535:
									fields.append("summary")
									data.append(summary)
								else:
									self._error_macro("The summary is too long")
									return -1
							else:
								self._error_macro("The summary is too short")
								return -1

						db_id = self.insert("bug_root", fields, data, True)

						if db_id > 0:
							return db_id
					return -1
				else:
					self._error_macro("Unique reference is too long")
					return -1
			else:
				self._error_macro("Unique refernce is too short")
				return -1
		else:
			return -1

	def load_crash_types(self):
		if self.common_check(project_root=True, project_child=True):
			get_fields = []
			where_fields = []
			where_data = []

			get_fields.append("crash_type_id")
			get_fields.append("name")

			where_fields.append("fk_project_child_id")
			where_data.append(self.project_child_id)

			crash_type_rows = self.select(get_fields, "crash_type", where_fields, where_data)

			if self.size(crash_type_rows) > 0:
				self.crash_type_dict = {}
				for row in crash_type_rows:
					self.crash_type_dict[row[1]] = row[0]
			return True
		else:
			return False

	def get_crash_type(self, name, show_error=True):
		if name in self.crash_type_dict:
			return self.crash_type_dict[name]
		else:
			if show_error:
				self._error_macro(str(name) + " crash type not found. Try calling add first.")
			return -1

	def add_crash_type(self, name, comment=None):
		if self.common_check(project_root=True, project_child=True):
			if self.size(name) > 0:
				if self.size(name) < 46:

					crash_type_id = self.get_crash_type(name, False)

					if crash_type_id  > 0:
						return crash_type_id
					else:
						fields = []
						data = []

						fields.append("name")
						data.append(name)

						if comment:
							if self.size(comment) > 0:
								if self.size(comment) < 65535:
									fields.append("comment")
									data.append(comment)
								else:
									self._error_macro("The comment is too long")
									return -1
							else:
								self._error_macro("The comment is too short")
								return -1

						fields.append("fk_project_child_id")
						data.append(self.project_child_id)

						db_id = self.insert("crash_type", fields, data, True)

						if db_id > 0:
							self.history("name tag: " + str(name) + " added.", "crash_type", "auto")
							self.crash_type_dict[name] = db_id
							return db_id
					return -1
				else:
					self._error_macro("Line marker type is too long")
					return -1
			else:
				self._error_macro("Line marker type is too short")
				return -1
		else:
			return -1


report = TestReporter(user.sql_host,  user.sql_name, user.sql_password, "project_db")

if report.connect():
	print "Project Root:", report.add_project_root("Mainline")
	print "Select Project Root:", report.select_project_root("Mainline")
	print "Project Child:", report.add_project_child("Kernel", "/media/Backup/regression_data/logs/", user.ftp_host, user.ftp_usr_name, user.ftp_password)
	print "Select Child:", report.select_project_child("Kernel")
	print "Add Arch:", report.add_arch("x86")
	print "Add Arch:", report.add_arch("x86_64")
	print "Add Arch:", report.add_arch("arm")
	print "Add Arch:", report.add_arch("aarch64")
	print "Add Arch:", report.add_arch("ppc")
	print "Add Arch:", report.add_arch("mips")
	print "Add Arch:", report.add_arch("x86")
	print "Line Marker:", report.add_line_marker_type("test download")
	print "Line Marker:", report.add_line_marker_type("test")
	print "Line Marker:", report.add_line_marker_type("bug reference")
	print "Line Marker:", report.add_line_marker_type("crash")
	print "Line Marker:", report.add_line_marker_type("memory fault")
	print "Line Marker:", report.add_line_marker_type("test download")
	print "Result tag:", report.add_result_tag("pass")
	print "Result tag:", report.add_result_tag("xpass")
	print "Result tag:", report.add_result_tag("fail")
	print "Result tag:", report.add_result_tag("xfail")
	print "Result tag:", report.add_result_tag("unresolved")
	print "Result tag:", report.add_result_tag("untested")
	print "Result tag:", report.add_result_tag("pass")

	print "Add Target:", report.add_target("adsom-7222")
	print "Add Target:", report.add_target("advantech-7226")
	print "Add Target:", report.add_target("aimb272-12185")
	print "Add Target:", report.add_target("amd64-dual-2")
	print "Add Target:", report.add_target("amdk6ii-1")
	print "Add Target:", report.add_target("amdk6iii-1")
	print "Add Target:", report.add_target("amdk7-1")
	print "Add Target:", report.add_target("atom-6354")
	print "Add Target:", report.add_target("beagleblack")
	print "Add Target:", report.add_target("beaglexm-1")
	print "Add Target:", report.add_target("beaglexm-2")
	print "Add Target:", report.add_target("bigbertha-8455")
	print "Add Target:", report.add_target("bigintel-7990")
	print "Add Target:", report.add_target("bigmac")
	print "Add Target:", report.add_target("ct11eb")
	print "Add Target:", report.add_target("ds81-shuttle-001")
	print "Add Target:", report.add_target("hasswell-bc5ff4e8872e")
	print "Add Target:", report.add_target("imb-151")
	print "Add Target:", report.add_target("imb-151-6336")
	print "Add Target:", report.add_target("imb-151-6342")
	print "Add Target:", report.add_target("imb-151-6352")
	print "Add Target:", report.add_target("imx600044-20015160")
	print "Add Target:", report.add_target("imx6q-sabresmart-00049f02e082")
	print "Add Target:", report.add_target("imx6q-sabresmart-6115")
	print "Add Target:", report.add_target("ivybridge-2554")
	print "Add Target:", report.add_target("jasper-8092")
	print "Add Target:", report.add_target("kontron-flex-7229")
	print "Add Target:", report.add_target("kontron-flex-7230")
	print "Add Target:", report.add_target("ktron-uepc-7234")
	print "Add Target:", report.add_target("mvdove-7213")
	print "Add Target:", report.add_target("mvdove-7791")
	print "Add Target:", report.add_target("mx6q-sabrelite-12252")
	print "Add Target:", report.add_target("nvidia-7903")
	print "Add Target:", report.add_target("nvidia-erista-8091")
	print "Add Target:", report.add_target("nvidia-erista-8093")
	print "Add Target:", report.add_target("nvidia-loki-6769")
	print "Add Target:", report.add_target("nvidia-loki-6790")
	print "Add Target:", report.add_target("nvidia-loki-6961")
	print "Add Target:", report.add_target("omap3530-6363")
	print "Add Target:", report.add_target("omap3530-7098")
	print "Add Target:", report.add_target("omap3530-7099")
	print "Add Target:", report.add_target("omap3530-7567")
	print "Add Target:", report.add_target("omap4430-9095")
	print "Add Target:", report.add_target("omap4430-9221")
	print "Add Target:", report.add_target("omap5432-es2-2206")
	print "Add Target:", report.add_target("omap5432-es2-2716")
	print "Add Target:", report.add_target("panda-12659")
	print "Add Target:", report.add_target("panda-12660")
	print "Add Target:", report.add_target("panda-12676")
	print "Add Target:", report.add_target("panda-12677")
	print "Add Target:", report.add_target("pcm9562-8166")
	print "Add Target:", report.add_target("qnet02")
	print "Add Target:", report.add_target("qnet04")
	print "Add Target:", report.add_target("qnet05")
	print "Add Target:", report.add_target("sandybridge-001")
	print "Add Target:", report.add_target("smpmpxpii")
	print "Add Target:", report.add_target("tolapai-6109")
	print "Add Target:", report.add_target("adsom-7222")

	print "Add Bug Root:", report.add_bug_root("jira", "123456789", "This is a stupid summary")
	print "Add Bug Root:", report.add_bug_root("jira", "123456789", "This is a stupid summary")

	print "Add Crash Type: ", report.add_crash_type("sigsegv")
	print "Add Crash Type: ", report.add_crash_type("sigill")
	print "Add Crash Type: ", report.add_crash_type("sigbus")
	print "Add Crash Type: ", report.add_crash_type("shutdown")
	print "Add Crash Type: ", report.add_crash_type("kdump")
	print "Add Crash Type: ", report.add_crash_type("sigsegv")

	report.commit()
