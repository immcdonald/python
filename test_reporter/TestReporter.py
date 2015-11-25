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
		self.project_dict = {}
		self.arch_dict = {}
		self.selected_project = None
		self.tag_dict = {}

		self.report_user_name= None
		self.exec_id = None
		self.variant_id = None

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
				self._error_macro("Please call connect before this this function.", frame_info=frameinfo)
				return False

		if project:
			if self.selected_project is None:
				self._error_macro("Please select a project before calling this function.", frame_info=frameinfo)
				return False

		if user_name:
			if self.report_user_name is None:
				self._error_macro("Please set a username before calling this function.", frame_info=frameinfo)
				return False

		if exec_id:
			if self.exec_id is None:
				self._error_macro("Please register an exec_id before calling this function.", frame_info=frameinfo)
				return False

		if variant_id:
			if self.variant_id is None:
				self._error_macro("Please register a variant before calling this function", frame_info=frameinfo)
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
						query = "INSERT INTO project (name, description, created) VALUES (%s, %s, %s)"
						data =  (project_name, description, "NOW()")
					else:
						query = "INSERT INTO project (name, description, project_html_style, created) VALUES (%s, %s, %s, %s)"
						data =  (project_name, description, html_style, "NOW()")

					self.query(query,data)

					self.project_dict[project_name] = self.cursor.lastrowid

					self.select_project(project_name)

					self.log.out("(" + project_name + ") registered as project name.", v=1)
					return True

			else:
				self._error_macro("Project name cannot be None")
				return False

	def select_project(self, project_name):
		if self._common_checks():
			if project_name in self.project_dict:
				self.selected_project = project_name
				self.refresh_tags()
				self.log.out("(" + project_name + ") is now the active project")
			else:
				self._error_macro("(" + project_name + ") does not appear in the database. Try reconnecting or calling refresh_projects_list")
				return False

	def refresh_arch_list(self):
		if self._common_checks():
			self.arch_dict={}
			query = "SELECT arch_id, name from arch"
			self.query(query)
			for row in self.cursor:
				self.arch_dict[row[1]] = row[0]
			return True

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
						query = "INSERT INTO arch (name, created) VALUES (%s, %s)"
						data = (arch, "NOW()")
					else:
						query = "INSERT INTO arch (name, arch_html_style, created) VALUES (%s, %s, %s)"
						data = (arch, html_style, "NOW()")

					self.query(query, data)

					self.arch_dict[arch] = {self.cursor.lastrowid}

					self.log.out("Arch (" + arch + ")  added to the database.", v=1)

				return True
			else:
				self._error_macro("Arch can not be None.")
				return False


	def refresh_tags(self):
		if self._common_checks(project=True):
			self.tags = {}
			query = "SELECT tag_id, result from tag WHERE fk_project_id=" + str(self.project_dict[self.selected_project]) + " ORDER BY tag_id ASC"
			self.query(query)
			for row in self.cursor:
				self.tags[row[1]] = row[0]
			return True


	def add_tag(self, tag, comment=None, html_style=None):
		if self._common_checks(project=True):
			if tag is not None:
				if tag in self.tag_dict:
					self.log.out('result tag (' + tag + ") already in the database", WARNING, v=1)
				else:
					value  = ["fk_project_id"]
					format = ["%s"]
					data = [self.project_dict[self.selected_project]]

					value.append("created")
					format.append("%s")
					data.append("NOW()")

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

						if len(comment) > 65535:
							self._error_macro("comment is to long")
							return False

						value.append("comment")
						format.append("%s")
						data.append(comment)

					if 	html_style is not None:
						if len(html_style) < 2:
							self._error_macro("Comment is to short")

						if len(html_style) > 65535:
							self._error_macro("comment is to long")
							return False

						value.append("tag_html_style")
						format.append("%s")
						data.append(html_style)

					query = "INSERT INTO tag (" + ",".join(value) + ") VALUES (" + ",".join(format) + ")"
					self.query(query, data)

					self.tag_dict[tag] = {self.cursor.lastrowid}

					self.log.out("Result tag (" + tag + ")  added to the database.", v=1)

					return True
			else:
				self._error_macro("Result tag can not be None.")
				return False

dog = TestReporter("serenity.bts.rim.net", user.sql_name, user.sql_password, db_name="result_db");

dog.connect()

dog.select_db("result_db")

dog.add_arch("x86","Red")
dog.add_arch("sh", "Green")
dog.add_arch("mips", "Black")
dog.add_arch("ppc", "Blue")
dog.add_arch("arm", "Yellow")
dog.add_arch("x86_64", "Purple")
dog.add_arch("aarch64", "Cyan")

dog.register_project("Ian", "This is a project for Ian", "Red")
dog.register_project("Rebecca", "This is a project for Rebecca", "Green")
dog.select_project("Ian")

dog.add_tag("Horse", "Woo hoo we passed!!!!!", "Some stupid color and font stuff")

dog.commit()
