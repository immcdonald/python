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

	def init(self):
		super(TestReporter, self).init()
		self.selected_project = None
		self.report_user_name = None

		# can be a number between 0 and 128
		self.unique_root_test_id = 0

		#Identififiers
		self.project_id = None
		self.exec_id = None
		self.variant_id = None
		self.suite_id = None
		self.test_revision_id = None
		self.test_id = None
		self.root_bug_id = None
		self.project_bug_id = None


		# Dictionaries
		self.project_dict = {}
		self.arch_dict = {}
		self.variant_dict = {}
		self.target_dict = {}
		self.tag_dict = {}
		self.crash_type_dict = {}
		self.suite_dict = {}
		self.test_root_dict = {}
		self.test_revision_dict = {}
		self.test_dict = {}
		self.bug_root_dict = {}
		self.project_bug_dict = {}

	def __init__(self, host, usr, passwd, db_name, log=None, commit_on_close=False, mask=None):
		self.init()
		super(TestReporter, self).__init__(host, usr, passwd, db_name, log, commit_on_close, mask)

	def connect(self):
		super(TestReporter, self).connect()
		self.refresh_projects_list()
		self.refresh_arch_list()
		self.refresh_target_list()
		self.refresh_bug_root()

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

			query = "SELECT project_id, name, attachment_path, ftp_host, ftp_user_name, ftp_password, attachment_path from project"
			self.query(query)

			for row in self.cursor:
				self.project_dict[row[1]] = {"id":row[0], "attachment_path":row[2], "ftp_host":row[3], "ftp_user_name":row[4], "ftp_password":row[5], "attachment_path":row[6]}
			return True
		else:
			return False

	'''
	Add a project to the database. Note: the new project name automatically becomes the
	default project.
	'''
	def register_project(self, project_name, description, ftp_host, ftp_user_name, ftp_password, attachment_path, html_style=None):
		if self._common_checks():
			if project_name is not None:
				if project_name in self.project_dict:
					self.log.out(project_name + " already registered in the database", WARNING, v=2)
					self.select_project(project_name)
					return True

				else:
					value = []
					format = []
					data = []

					if len(project_name) < 3:
						self._error_macro("Project name is to short")
						return False

					if len(project_name) > 45:
						self._error_macro("Project name is to long")
						return False

					value.append("name")
					format.append("%s")
					data.append(project_name)

					if description is None:
						self._error_macro("Project description can not be None")
						return False

					if len(description) < 10:
						self._error_macro("Project description is to short")
						return False

					if len(description) > 65535:
						self._error_macro("Project description is to long")
						return False

					value.append("description")
					format.append("%s")
					data.append(description)

					if len(ftp_host) < 10:
						self._error_macro("FTP host is to short")
						return False

					if len(ftp_host) > 65535:
						self._error_macro("ftp host is to long")
						return False

					value.append("ftp_host")
					format.append("%s")
					data.append(ftp_host)

					if len(ftp_user_name) < 1:
						self._error_macro("FTP user name is to short")
						return False

					if len(ftp_user_name) > 20:
						self._error_macro("ftp user name is to long")
						return False

					value.append("ftp_user_name")
					format.append("%s")
					data.append(ftp_user_name)

					if len(ftp_password) < 1:
						self._error_macro("FTP password is to short")
						return False

					if len(ftp_password) > 64:
						self._error_macro("ftp password is to long")
						return False

					value.append("ftp_password")
					format.append("%s")
					data.append(ftp_password)

					if len(attachment_path) < 1:
						self._error_macro("FTP host is to short")
						return False

					if len(attachment_path) > 65535:
						self._error_macro("ftp host is to long")
						return False

					value.append("attachment_path")
					format.append("%s")
					data.append(attachment_path)

					if html_style is not None:
						value.append("project_html_style")
						format.append("%s")
						data.append(html_style)

					query = "INSERT INTO project (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"

					self.query(query, data)

					self.refresh_projects_list()

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
				self.project_id = self.project_dict[project_name]["id"]
				self.refresh_tags()
				self.refresh_crash_type()
				self.refresh_test_root()
				self.refresh_test_revision()
				self.refresh_project_bugs()

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
				self.arch_dict[row[1]] = {"id":row[0]}
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

					self.refresh_arch_list()

					self.log.out("Arch (" + arch + ") added to the database.", v=1)

				return True
			else:
				self._error_macro("Arch can not be None.")
				return False
		else:
			return False

	def refresh_target_list(self):
		if self._common_checks():
			self.target_dict={}
			query = "SELECT target_id, target_name from target ORDER BY target_name"
			self.query(query)
			for row in self.cursor:
				self.target_dict[row[1]] = {"id":row[0]}
			return True
		else:
			return False

	def add_target(self, target_name, description=None, html_style=None):
		if self._common_checks():
			if target_name in self.target_dict:
				self.log.out('Target (' + target_name + ") already registered in the database", WARNING, v=0)
			else:
				value = []
				format = []
				data = []

				if len(target_name) < 5:
					self._error_macro("Target name is to short")
					return False

				if len(target_name) > 45:
					self._error_macro("Target name is to long")
					return False

				value.append("target_name")
				format.append("%s")
				data.append(target_name)

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

				query = "INSERT INTO target (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", Now())"

				self.query(query, data)

				self.refresh_target_list()

				self.log.out("Target (" + target_name + ") added to the database.", v=0)

				return True
		else:
			return False

	def refresh_tags(self):
		if self._common_checks(project=True):
			self.tag_dict = {}
			query = "SELECT tag_id, result, project_offset from tag WHERE fk_project_id=" + str(self.project_id) + " ORDER BY tag_id ASC"
			self.query(query)
			for row in self.cursor:
				self.tag_dict[row[1]] = {"id":row[0], "project_offset": row[2]}
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
					data = [self.project_id]

					value.append("project_offset")
					format.append("%s")
					data.append(len(self.tag_dict))

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

					self.refresh_tags()

					self.log.out("Result tag (" + tag + ") added to the database.", v=1)

					return True
			else:
				self._error_macro("Result tag can not be None.")
				return False
		else:
			return False

	def refresh_crash_type(self):
		if self._common_checks(project=True):
			self.crash_type_dict = {}
			query = "SELECT crash_id, name from crash_type WHERE fk_project_id=" + str(self.project_id) + " ORDER BY crash_id ASC"
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
					data = [self.project_id]

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

					self.refresh_crash_type();

					self.log.out("Crash type (" + crash_type + ") added to the database.", v=1)

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
			data = [self.project_id]
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
			query = 'SELECT exec_id FROM exec WHERE fk_project_id=' + str(self.project_id) +  ' and exec_id=' + str(exec_id)
			self.query(query)
			rows = self.cursor.fetchall()

			if len(rows) == 1:
				self.exec_id = exec_id
				self.refresh_suite_names()
				self.refresh_test_dict()
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
		else:
			return False

	def refresh_suite_names(self):
		if self._common_checks(project=True, exec_id=True):
			self.suite_dict = {}
			query = "SELECT test_suite_id, suite_name from test_suite WHERE fk_exec_id=" + str(self.exec_id) + " ORDER BY suite_name"
			self.query(query)
			for row in self.cursor:
				self.suite_dict[row[1]] = {"id":row[0]}
			return True
		else:
			return False

	def add_test_suite(self, suite_name, description=None, html_style=None):
		if self._common_checks(project=True, exec_id=True):
			if suite_name in self.suite_dict:
				self.log.out('Suite name (' + suite_name + ") already in the database.", WARNING, v=0)
				self.suite_id =  self.suite_dict[suite_name]["id"];
				return self.suite_id
			else:
				value = []
				format = []
				data = []

				value.append("fk_project_id")
				format.append("%s")
				data.append(self.project_id)

				value.append("fk_exec_id")
				format.append("%s")
				data.append(self.exec_id)

				if len(suite_name) < 3:
					self._error_macro("suite name is to short")
					return -1

				if len(suite_name) > 45:
					self._error_macro("suite name is to long")
					return -1

				value.append("suite_name")
				format.append("%s")
				data.append(suite_name)

				if description is not None:
					if len(description) < 5:
						self._error_macro("description is to short")
						return -1

					if len(description) > 65535:
						self._error_macro("description is to long")
						return -1

					value.append("description")
					format.append("%s")
					data.append(description)

				if 	html_style is not None:
					if len(html_style) < 2:
						self._error_macro("html style is to short")
						return -1

					if len(html_style) > 65535:
						self._error_macro("html style is to long")
						return -1

					value.append("tag_html_style")
					format.append("%s")
					data.append(html_style)

				query = "INSERT INTO test_suite (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
				self.query(query, data)

				self.suite_id = self.cursor.lastrowid;

				self.refresh_suite_names()

				self.log.out("Test Suite (" + suite_name + ") added to the database.", v=1)
				return  self.suite_id

		else:
			return -1

	def add_variant(self, target, arch, variant):
		if self._common_checks(project=True, exec_id=True, user_name=True):
			if arch in self.arch_dict:
				if target in self.target_dict:
					root_variant_id = None

					data = (self.arch_dict[arch]["id"], self.target_dict[target]["id"], variant)

					# Check to see if we have a root variant of this combination exists
					query = 'SELECT root_variant_id FROM root_variant WHERE fk_arch_id=%s and fk_target_id=%s and variant=%s'
					self.query(query, data)

					rows = self.cursor.fetchall()

					if len(rows) > 0:
						root_variant_id = rows[0][0];
					else:
						query = 'INSERT INTO root_variant (fk_arch_id, fk_target_id, variant, created) VALUES (%s, %s, %s, NOW())'
						self.query(query, data)
						root_variant_id = self.cursor.lastrowid
						self.log.out("Root Variant (" +  str(target) + "-" + str(arch) + "-" +  str(variant) + ") added to the database.", v=0)

					if root_variant_id:

						value = []
						format = []
						data = []

						value.append("fk_project_id")
						format.append("%s")
						data.append(self.project_id)

						value.append("fk_exec_id")
						format.append("%s")
						data.append(self.exec_id)

						value.append("fk_root_variant_id")
						format.append("%s")
						data.append(root_variant_id)

						value.append("user_name")
						format.append("%s")
						data.append(self.report_user_name)

						# check to see if the variant already exists
						query = "SELECT variant_id FROM variant WHERE " + "=%s and ".join(value) + "=%s"

						self.query(query, data)

						rows = self.cursor.fetchall()

						if len(rows) > 0:
							self.log.out('Variant (' + str(target) + "-" + str(arch) + "-" +  str(variant)  + ") already exists for Execution: " + str(self.exec_id), WARNING, v=0)

							self.variant_id = rows[0][0]

							self.variant_dict[self.variant_id] = {"target": target, "arch": arch, "variant": variant}

						else:
							query = "INSERT INTO variant (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"
							self.query(query, data)

							self.variant_id = self.cursor.lastrowid

							self.log.out("Variant (" +  str(target) + "-" + str(arch) + "-" +  str(variant) + ") added to the database for Execution: " + str(self.exec_id))

							self.variant_dict[self.variant_id] = {"target": target, "arch": arch, "variant": variant}

							return True
					else:
						self._error_macro("Failed to resolve root variant")
						return False

				else:
					self._error_macro("Target (" + str(target) + ") is not in the database. Please call add_target before this function.")
					return False

			else:
				self._error_macro("Arch (" + str(arch) + ") is not in the database. Please call add_arch before this function.")
				return False
		else:
			return False

	def add_attachments(self, full_attachment_src_path, attachment_type="general", mime_type="application/octet-stream", comment=None, omit_exec_id=False, omit_variant_id=False):
		if self._common_checks(project=True):
			known_compressed_extensions = [".zip", ".gz"]
			valid_attachment_types = ['primary', 'general', 'crash', 'symbol', 'profile', 'json', 'history', 'pre_json', 'post_json']

			if attachment_type not in valid_attachment_types:
				self._error_macro(str(attachment_type) + " is an unknown attachment type.")
				return -1

			if os.path.exists(full_attachment_src_path):

				ftp = my_ftp(self.project_dict[self.selected_project]["ftp_host"],
							 self.project_dict[self.selected_project]["ftp_user_name"],
							 self.project_dict[self.selected_project]["ftp_password"],
							 log=self.get_log()
							)

				if ftp.connect():
					value = []
					format = []
					data = []

					value.append("fk_project_id")
					format.append("%s")
					data.append(self.project_id)

					dest_path = ""


					# Attempt to change to the project directory.
					if ftp.chdir(self.project_dict[self.selected_project]["attachment_path"]) is not True:
						return -1
					else:
						dest_path = self.project_dict[self.selected_project]["attachment_path"]

					# Is exec_id set:
					if self.exec_id is not None:

						value.append("fk_exec_id")
						format.append("%s")
						data.append(self.exec_id)

						if omit_exec_id is False:
							exec_id_dir = "%06d" % int(self.exec_id);

							if ftp.mkdir(str(exec_id_dir), True):
								dest_path = os.path.join(dest_path, exec_id_dir)

								if ftp.chdir(dest_path) is not True:
									return -1
							else:
								return -1

						if self.variant_id is not None:

							value.append("fk_variant_id")
							format.append("%s")
							data.append(self.variant_id)

							if ftp.mkdir(str(self.variant_dict[self.variant_id]["target"]), True):
								dest_path = os.path.join(dest_path, str(self.variant_dict[self.variant_id]["target"]))

								if ftp.chdir(dest_path) is not True:
									return -1
							else:
								return -1

							if ftp.mkdir(str(self.variant_dict[self.variant_id]["arch"]), True):
								dest_path = os.path.join(dest_path, str(self.variant_dict[self.variant_id]["arch"]))

								if ftp.chdir(dest_path) is not True:
									return -1
							else:
								return -1

							if ftp.mkdir(str(self.variant_dict[self.variant_id]["variant"]), True):
								dest_path = os.path.join(dest_path, str(self.variant_dict[self.variant_id]["variant"]))

								if ftp.chdir(dest_path) is not True:
									return -1
							else:
								return -1

					local_dir_name = os.path.dirname(full_attachment_src_path)
					base_name = os.path.basename(full_attachment_src_path)
					root_file_name, extension = os.path.splitext(base_name)

					# We want to store only compressed files on the server
					# so see if this file is already compressed.
					if extension not in known_compressed_extensions:
						# if not then we will compress it before we copy it

						new_file_name = "";
						index = 0
						output_path = ""

						for index in range(-1, 1000):
							if index == -1:
								file_name = root_file_name + extension + ".gz"
							else:
								file_name = root_file_name + extension + "-%03d" % index + ".gz"

							output_path = os.path.join(local_dir_name, file_name)

							if os.path.exists(output_path) is False:
								break

						if index >= 1000:
							self._error_macro(full_attachment_src_path + " Failed to find an acceptable name to generate a compressed file.")
							return -1

						dest_file_name = os.path.join(dest_path, file_name)

						value.append("path")
						format.append("%s")
						data.append(dest_file_name)

						# Look to see if we already have this file int he database
						query = "SELECT attachment_id FROM attachment WHERE " + "=%s and ".join(value) + "=%s"
						self.query(query, data)

						rows = self.cursor.fetchall()

						if len(rows) > 0:
							self.log.out(dest_file_name + " already exists in the database.", WARNING, v=0)
							return rows[0][0]

						value.append("attach_type")
						format.append("%s")
						data.append(attachment_type)

						value.append("mime_type")
						format.append("%s")
						data.append(mime_type)


						value.append("compress_mode")
						format.append("%s")
						data.append("post_compressed_gz")


						if comment is not None:
							if len(comment) < 3:
								self._error_macro("comment is to short")
								return -1

							if len(comment) > 65535:
								self._error_macro("comment is to long")
								return -1

							value.append("comment")
							format.append("%s")
							data.append(comment)

						with open(full_attachment_src_path, "rb") as fp_in:
							with gzip.open(output_path, "wb") as fp_output:
								shutil.copyfileobj(fp_in, fp_output)

						if ftp.binary_file_transfer_2_file(output_path, dest_file_name):
							query = "INSERT INTO attachment (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
							self.query(query, data)
							#Remove the file that we created
							os.remove(output_path)
							return self.cursor.lastrowid
						else:
							return -1
					else:
						dest_file_name = os.path.join(dest_path, file_name)

						# Look to see if we already have this file int he database
						query = "SELECT attachment_id FROM attachment WHERE " + "=%s and ".join(value) + "=%s"
						self.query(query, data)

						rows = self.cursor.fetchall()

						if len(rows) > 0:
							self.log.out(dest_file_name + " already exists in the database.", WARNING, v=0)
							return rows[0][0]

						value.append("attach_type")
						format.append("%s")
						data.append(attachment_type)

						value.append("mime_type")
						format.append("%s")
						data.append(mime_type)

						if comment is not None:
							if len(comment) < 3:
								self._error_macro("comment is to short")
								return -1

							if len(comment) > 65535:
								self._error_macro("comment is to long")
								return -1
							value.append("comment")
							format.append("%s")
							data.append(comment)


						value.append("compress_mode")
						format.append("%s")
						data.append("src_compressed")


						if ftp.binary_file_transfer_2_file(full_attachment_src_path, dest_file_name):
							query = "INSERT INTO attachment (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
							self.query(query, data)

							return self.cursor.lastrowid
						else:
							return -1
				else:
					return -1
			else:
				self._error_macro(full_attachment_src_path + " was not found or is not accessible.")
				return -1


	def refresh_test_root(self):
		if self._common_checks():
			self.suite_dict = {}
			query = "SELECT test_root_id, exec_path, name, params from test_root WHERE fk_project_id=" + str(self.project_id) + " ORDER BY name"
			self.query(query)
			for row in self.cursor:
				test_key = os.path.join(row[1], row[2])
				test_key = test_key.replace("\\", "/")

				if len(row[3]) > 0:
					test_key = test_key + " " + row[3]

				self.test_root_dict[test_key] = {"id": row[0]}
			return True
		else:
			return False

	def add_test_root(self, exec_path, name, params=None, src_path=None):
		if self._common_checks(project=True):
			test_key = os.path.join(exec_path, name)
			test_key = test_key.replace("\\", "/")
			exec_path = exec_path.replace("\\", "/")

			if params:
				if len(params) > 0:
					test_key = test_key + " " + params

			if test_key in self.test_root_dict:
				self.log.out('Test Root (' + test_key + ") already in the database.", WARNING, v=1)
				return self.test_root_dict[test_key]["id"]
			else:
				value = []
				format = []
				data = []

				value.append("fk_project_id")
				format.append("%s")
				data.append(self.project_id)

				if len(exec_path) < 2:
					self._error_macro("test name is to short")
					return -1

				if len(exec_path) > 65535:
					self._error_macro("test name is to long")
					return -1

				value.append("exec_path")
				format.append("%s")
				data.append(exec_path)

				if len(name) < 2:
					self._error_macro("test name is to short")
					return -1

				if len(name) > 50:
					self._error_macro("test name is to long")
					return -1

				value.append("name")
				format.append("%s")
				data.append(name)

				if params is not None:
					if len(params) > 100:
						self._error_macro("test name is to long")
						return -1

					value.append("params")
					format.append("%s")
					data.append(params)

				if 	src_path is not None:
					if len(src_path) < 10:
						self._error_macro("source path is to short")
						return -1

					if len(src_path) > 256:
						self._error_macro("source path is to long")
						return -1

					value.append("src_path")
					format.append("%s")
					data.append(src_path)

				query = "INSERT INTO test_root (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"

				self.query(query, data)

				self.refresh_test_root();

				self.log.out("Test Root (" + test_key + ") added to the database.")
				return self.cursor.lastrowid
		else:
			return -1

	def refresh_test_revision(self):
		if self._common_checks():
			self.test_revision_dict = {}
			query = "SELECT test_revision_id, fk_test_root_id, unique_rev_id from test_revision, test_root WHERE fk_test_root_id=test_root_id and fk_project_id=" + str(self.project_id)
			self.query(query)
			for row in self.cursor:
				test_key = str(row[1]) +"_"+ str(row[2])
				self.test_revision_dict[test_key] = {"id":row[0]}
			return True
		else:
			return False

	def add_test_revision(self, exec_path, name, params, unique_rev_id="base", arch="all", src_path=None, description=None, html_style=None):
		test_root_id = self.add_test_root(exec_path, name, params, src_path)

		if test_root_id > 0:
			test_key = str(test_root_id) + "_" + str(unique_rev_id)

			if test_key in self.test_revision_dict:
			   	self.log.out('Test Revision (' + os.path.join(exec_path, name) + " " + str(params) + " rev_ud: " + str(unique_rev_id) + ") already in the database.", WARNING, v=0)
				self.test_revision_id = self.test_revision_dict[test_key]["id"]
				return self.test_revision_id
			else:
				value = []
				format = []
				data = []

				value.append("fk_test_root_id")
				format.append("%s")
				data.append(test_key)

				if len(unique_rev_id) < 1:
					self._error_macro("unique revision id is to short")
					return -1

				if len(unique_rev_id) > 80:
					self._error_macro("unique revision id is to long")
					return -1

				value.append("unique_rev_id")
				format.append("%s")
				data.append(unique_rev_id)

				arch_value = ""
				if arch != "all":
					for arch_part in arch.split(","):
						arch_part = arch_part.strip()
						if arch_part in self.arch_dict:
							if len(arch_value) == 0:
								arch_value = str(self.arch_dict[arch_part]["id"])
							else:
								arch_value = arch_value + ", " + str(self.arch_dict[arch_part]["id"])
						else:
							self._error_macro(arch_part + " is not recognize as a valid architecture.")
							return False

				else:
					arch_value = arch

				if len(arch_value) < 2:
					self._error_macro("support arch is to short")
					return -1

				if len(arch_value) > 100:
					self._error_macro("support arch is to long")
					return -1

				value.append("arch_list")
				format.append("%s")
				data.append(arch_value)

				if description is not None:
					if len(description) > 2:
						self._error_macro("description is to short")
						return -1

					if len(description) > 65535:
						self._error_macro("description is to long")
						return -1

					value.append("description")
					format.append("%s")
					data.append(description)

				if html_style is not None:
					if len(html_style) < 3:
						self._error_macro("html style is to short")
						return -1

					if len(html_style) > 65535:
						self._error_macro("html style is to long")
						return -1

					value.append("test_rev_html_style")
					format.append("%s")
					data.append(html_style)

				query = "INSERT INTO test_revision (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
				self.query(query, data)

				# Get the last row value before the queries in refresh the test list blow it away.
				self.test_revision_id = self.cursor.lastrowid;

				self.refresh_test_revision()

				return self.test_revision_id
		else:
			return -1

	def refresh_test_dict(self):
		if self._common_checks():
			self.test_dict = {}
			query = "SELECT test_id, fk_test_suite_id, fk_test_revision_id from test, test_suite WHERE fk_test_suite_id=test_suite_id and fk_exec_id=" + str(self.exec_id)
			self.query(query)
			for row in self.cursor:
				test_key = str(row[1]) + "_" + str(row[2])
				self.test_dict[test_key] = {"id":row[0]}
			return True
		else:
			return False

	def add_test(self, test_suite_id=None, test_rev_id=None):
		if self._common_checks(project=True, exec_id=True):

			if test_suite_id is None:
				if self.suite_id is not None:
					test_suite_id = self.suite_id
				else:
					self._error_macro("Test suite id was not previously set")
					return -1

			if test_rev_id is None:
				if self.test_revision_id is not None:
					test_rev_id = self.test_revision_id
				else:
					self._error_macro("test revision id was not previously set")
					return -1

			test_key = str(suite_id) + "_" + str(test_rev_id)
			if test_key in self.test_dict:
				self.log.out('Test already in the database.', WARNING, v=0)
				self.test_id = self.test_dict[test_key]["id"]
				return self.test_id
			else:
				value = []
				format = []
				data = []

				value.append("fk_test_suite_id")
				format.append("%s")
				data.append(test_suite_id)

				value.append("fk_test_revision_id")
				format.append("%s")
				data.append(test_rev_id)

				query = "INSERT INTO test (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"
				self.query(query, data)

				# Get the last row value before the queries in refresh the test list blow it away.
				self.test_id = self.cursor.lastrowid;

				self.refresh_test_dict()

				return self.test_id
		else:
			return -1

	def add_test_result(self, result, start_line=-1, end_line=-1, exec_time=-1, other_time=-1, crash_counter=0, custom_jason=None, pre_check=True):
		if self._common_checks(project=True, exec_id=True, variant_id=True):
			if self.test_id is not None:
				tag_id = None

				# Get result map value
				if result in self.tag_dict:
					tag_id = self.tag_dict[result]["id"]
				else:
					self._error_macro(str(result) + " result not found, please call add_tag and add this result type.")
					return False

				value = []
				format = []
				data = []

				value.append("fk_project_id")
				format.append("%s")
				data.append(self.project_id)

				value.append("fk_exec_id")
				format.append("%s")
				data.append(self.exec_id)

				value.append("fk_variant_id")
				format.append("%s")
				data.append(self.variant_id)

				value.append("fk_tag_id")
				format.append("%s")
				data.append(tag_id)

				value.append("fk_test_id")
				format.append("%s")
				data.append(self.test_id)

				value.append("start_line")
				format.append("%s")
				data.append(start_line)

				value.append("end_line")
				format.append("%s")
				data.append(end_line)

				value.append("exec_time")
				format.append("%s")
				data.append(exec_time)

				value.append("crash_counter")
				format.append("%s")
				data.append(crash_counter)

				if pre_check:
					query = "SELECT result_id FROM test_result WHERE " + "=%s and ".join(value) + "=%s"
					self.query(query, data)

					rows = self.cursor.fetchall()

					if len(rows) > 0:
						self.log.out('Test result is already in the database.', WARNING, v=0)
						return True

				if custom_jason:
					value.append("crash_counter")
					format.append("%s")
					data.append(crash_counter)

				query = "INSERT INTO test_result (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"

				self.query(query, data)

				return True
			else:
				self._error_macro("Please call add_test before calling this function.")
				return False
		else:
			return False

	def refresh_bug_root(self):
		if self._common_checks():
			self.bug_root_dict = {}

			query = "SELECT bug_root_id, recorder, reference from bug_root";
			self.query(query)
			for row in self.cursor:
				bug_root_key = str(row[1]) + "_" + str(row[2])
				self.bug_root_dict[bug_root_key] = {"id":row[0], "recorder":row[1], "reference":row[2]}
			return True
		else:
			return False

	def add_bug_root(self, record_type, reference_id, summary=None, html_style=None):
		if self._common_checks():
			valid_report_type = ['pr', 'jira']

			if record_type in valid_report_type:
				bug_root_key = str(record_type) + "_" + str(reference_id)

				if bug_root_key in self.bug_root_dict:

					self.root_bug_id = self.bug_root_dict[bug_root_key]["id"]
					return self.root_bug_id
				else:
					value = []
					format = []
					data = []

					value.append("recorder")
					format.append("%s")
					data.append(record_type)

					value.append("reference")
					format.append("%s")
					data.append(reference_id)

					if summary is not None:
						value.append("summary")
						format.append("%s")
						data.append(summary)

					if html_style is not None:
						value.append("html_style")
						format.append("%s")
						data.append(html_style)

					query = "INSERT INTO bug_root (" + ",".join(value) + ",created) VALUES (" + ",".join(format) + ", NOW())"
					self.query(query, data)
					self.root_bug_id  = self.cursor.lastrowid;

					self.refresh_bug_root()

					return self.root_bug_id
			else:
				self._error_macro(record_type + " is not a valid record type")
				return -1
		else:
			return -1


	def refresh_project_bugs(self):
		if self._common_checks(project=True):
			self.project_bug_dict = {}
			query = "SELECT bug_id, fk_bug_root_id from project_bug WHERE fk_project_id=" + str(self.project_id);
			self.query(query)
			for row in self.cursor:
				self.project_bug_dict[str(row[1])] = {"id":row[0]}
			return True
		else:
			return False

	def add_project_bug(self, record_type, reference_id, summary=None, entered="test_reference"):
		if self._common_checks(project=True):
			valid_entered_values = ['test_reference', 'website', 'other']

			if entered in valid_entered_values:
				bug_root_id = self.add_bug_root(record_type,reference_id, summary)

				if bug_root_id > 0:
					if str(bug_root_id) in self.project_bug_dict:
						self.project_bug_id = self.project_bug_dict[str(bug_root_id)]["id"];
						return self.project_bug_id
					else:
						value = []
						format = []
						data = []

						value.append("fk_project_id")
						format.append("%s")
						data.append(self.project_id)

						value.append("fk_bug_root_id")
						format.append("%s")
						data.append(bug_root_id)

						value.append("tracked")
						format.append("%s")
						data.append(entered)

						query = "INSERT INTO project_bug (" + ",".join(value) + ", created) VALUES (" + ",".join(format) + ", NOW())"
						self.query(query, data)

						self.project_bug_dict[bug_root_id] = {"id": self.cursor.lastrowid}

						return self.project_bug_dict[bug_root_id]["id"]

				else:
					return bug_root_id
			else:
				self._error_macro(entered + " is not a bug entry type.")
				return -1
		else:
			return -1


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

rdb.add_target("adsom-7222")
rdb.add_target("advantech-7226")
rdb.add_target("aimb272-12185")
rdb.add_target("amd64-dual-2")
rdb.add_target("amdk6ii-1")
rdb.add_target("amdk6iii-1")
rdb.add_target("amdk7-1")
rdb.add_target("atom-6354")
rdb.add_target("beagleblack")
rdb.add_target("beaglexm-1")
rdb.add_target("beaglexm-2")
rdb.add_target("bigbertha-8455")
rdb.add_target("bigintel-7990")
rdb.add_target("bigmac")
rdb.add_target("ct11eb")
rdb.add_target("ds81-shuttle-001")
rdb.add_target("hasswell-bc5ff4e8872e")
rdb.add_target("imb-151")
rdb.add_target("imb-151-6336")
rdb.add_target("imb-151-6342")
rdb.add_target("imb-151-6352")
rdb.add_target("imx600044-20015160")
rdb.add_target("imx6q-sabresmart-00049f02e082")
rdb.add_target("imx6q-sabresmart-6115")
rdb.add_target("ivybridge-2554")
rdb.add_target("jasper-8092")
rdb.add_target("kontron-flex-7229")
rdb.add_target("kontron-flex-7230")
rdb.add_target("ktron-uepc-7234")
rdb.add_target("mvdove-7213")
rdb.add_target("mvdove-7791")
rdb.add_target("mx6q-sabrelite-12252")
rdb.add_target("nvidia-7903")
rdb.add_target("nvidia-erista-8091")
rdb.add_target("nvidia-erista-8093")
rdb.add_target("nvidia-loki-6769")
rdb.add_target("nvidia-loki-6790")
rdb.add_target("nvidia-loki-6961")
rdb.add_target("omap3530-6363")
rdb.add_target("omap3530-7098")
rdb.add_target("omap3530-7099")
rdb.add_target("omap3530-7567")
rdb.add_target("omap4430-9095")
rdb.add_target("omap4430-9221")
rdb.add_target("omap5432-es2-2206")
rdb.add_target("omap5432-es2-2716")
rdb.add_target("panda-12659")
rdb.add_target("panda-12660")
rdb.add_target("panda-12676")
rdb.add_target("panda-12677")
rdb.add_target("pcm9562-8166")
rdb.add_target("qnet02")
rdb.add_target("qnet04")
rdb.add_target("qnet05")
rdb.add_target("sandybridge-001")
rdb.add_target("smpmpxpii")
rdb.add_target("tolapai-6109")

rdb.register_project("Mainline", "Mainline/Trunk Regression Thread", user.ftp_host, user.ftp_usr_name, user.ftp_password, "/media/BackUp/regression_data/logs/mainline" , "Red")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XFAIL status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a UNRESOLVED status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a UNTESTED status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")

rdb.register_project("dev_64b", "64 Bit initial development project", user.ftp_host, user.ftp_usr_name, user.ftp_password, "/media/BackUp/regression_data/logs/dev_64b", "Yellow")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XFAIL status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a UNRESOLVED status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a UNTESTED status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")

rdb.register_project("Qnx_sdp_7", "Qnx 7.0 SDP Branch", user.ftp_host, user.ftp_usr_name, user.ftp_password, "/media/BackUp/regression_data/logs/qnx7")
rdb.add_tag("PASS", "The test completed with a PASS status", "GREEN")
rdb.add_tag("FAIL", "The test completed with a FAILED status", "RED")
rdb.add_tag("XPASS", "The test completed with a XFAIL status", "YELLOW")
rdb.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
rdb.add_tag("UNRESOLVED", "The test completed with a UNRESOLVED status", "PURPLE")
rdb.add_tag("UNTESTED", "The test completed with a UNTESTED status", "BLUE")
rdb.add_crash_type("SIGSERV", "Crash")
rdb.add_crash_type("SIGILL", "Crash")
rdb.add_crash_type("SIGBUS", "Crash")
rdb.add_crash_type("KDUMP", "Crash")
rdb.add_crash_type("SHUTDOWN", "Crash")
rdb.select_project("Mainline");

exec_id=1

if rdb.set_exec_id(exec_id) is False:
	rdb.register_exec()

rdb.commit()


rdb.register_src("svn", "http://svn.ott.qnx.com/qa/mainline/testware", "123457")
rdb.add_variant("imb-151-6342", "x86", "o.smp")

suite_id = rdb.add_test_suite("testware_sanitytest")


test_rev_id = rdb.add_test_revision("/test/cool/", "ian", "is superman")

test_id =  rdb.add_test()

test_rev_id = rdb.add_test_revision("/test/cool/", "ian", "is superman")

testud = rdb.add_test()

test_rev_id = rdb.add_test_revision("/test/cool/", "ian", "is the green latern")

test_id = rdb.add_test()

test_rev_id = rdb.add_test_revision("/test/cool/", "ian", "is bob", arch="x86, x86_64")

test_id = rdb.add_test()

print rdb.add_test_result("PASS")

print rdb.add_bug_root("jira", "123456789", "This is a stupid JIRA summary")
print rdb.add_project_bug("jira", "123456789", "This is a stupid JIRA summary")

print rdb.add_attachments("./TestReporter.py")



rdb.commit()
