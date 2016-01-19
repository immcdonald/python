import os, sys
import argparse
import user
import gzip
import shutil
import getpass

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *
from my_ftp import *

class TestReporter(My_SQL):

	def reset_variant_exec_id(self):
		self.variant_exec_id = None

	def reset_exec_id(self):
		self.reset_variant_exec_id()
		self.exec_id = None

	def reset_project_child(self):
		self.reset_exec_id()
		self.project_child_id = None
		self.project_child_name = ""
		self.result_tag_dict = {}
		self.crash_type_dict = {}

	def reset_project_root(self):
		self.reset_project_child()
		self.project_root_id = None
		self.project_root_name = ""

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
		self.line_marker_sub_type_dict={}
		self.set_user_name(getpass.getuser())


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

		if rc:
			rc = self.load_line_marker_sub_types()

		return rc

	def check_ftp_path(self, host, user_name, password, path):
		ftp = my_ftp(host, user_name, password, log=self.get_log())

		if ftp:
			if ftp.connect():

				if ftp.chdir(path):
					return True
				else:
					return False
			else:
				return False
		else:
			self._error_macro("Creation of FTP object failed");
			return False

	def common_check(self, project_root=False, project_child=False, exec_id=False, variant_exec_id=False):
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

		if exec_id:
			if self.exec_id is None:
				self._error_macro("Exec id has not been registered. Please call register exec before calling this function.")
				return False

		if variant_exec_id:
			if self.variant_exec_id is None:
				self._error_macro("variant exec id has not been registered. Please call add variant exec before calling this function.")
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
					self.project_root_name = project_root
					self.project_root_id = project_rows[0][0]
				else:
					if comment:
						fields.append("comment")
						data.append(comment)

					db_id = self.insert("project_root", fields, data, True)

					if db_id > 0:
						self.reset_project_root()
						self.project_root_id = db_id
						self.project_root_name = project_root
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
				self.project_root_name = project_root
				self.project_root_id = project_rows[0][0]
				return self.project_root_id
			else:
				self._error_macro(project_root + " not found in the database")
				return -1

		else:
			return -1


	def set_user_name(self, user_name):
		if self.size(user_name) > 0:
			if self.size(user_name) < 46:
				self.reporter_user_name = user_name
				return True
			else:
				self._error_macro("The attachment path is too long")
				return False
		else:
			self._error_macro("The attachment path is too short")
			return False

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
					self.project_child_name = project_child
					self.project_child_id = project_rows[0][0]
					self._load_child_project_properties()
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
						self.project_child_name = project_child
						self.ftp_host = ftp_host
						self.ftp_user_name = ftp_user_name
						self.ftp_password = ftp_password
						self.attachment_path = attach_path
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

			project_rows = self.select("project_child_id, ftp_host, ftp_user_name, ftp_password, attach_path", "project_child", fields, data)

			if self.size(project_rows) > 0:
				self.reset_project_child()

				self.project_child_id = project_rows[0][0]
				self.project_child_name = project_child
				self.ftp_host = project_rows[0][1]
				self.ftp_user_name = project_rows[0][2]
				self.ftp_password = project_rows[0][3]
				self.attachment_path = project_rows[0][4]

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


	def get_arch_id(self, arch, display_error=True):
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
						if display_error:
							self._error_macro("Arch not found.")
						return -2
				else:
					self._error_macro("Arch is too long")
					return -1
			else:
				self._error_macro("Arch is too short")
				return -1

		else:
			return -1

	def add_arch(self, arch):
		arch_id = self.get_arch_id(arch, display_error=False)

		if arch_id == -2:
			arch = arch.replace(" ", "_")
			fields = []
			data = []

			fields.append("name")
			data.append(arch)

			db_id = self.insert("arch", fields, data, True)
			return db_id
		else:
			return arch_id

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

	def load_line_marker_sub_types(self):
		if self.common_check():
			fields = []
			fields.append("line_marker_sub_type_id")
			fields.append("name")

			line_marker_type_rows = self.select(fields, "line_marker_sub_type", None, None)

			if self.size(line_marker_type_rows) > 0:
				self.line_marker_sub_type_dict= {}
				for row in line_marker_type_rows:
					self.line_marker_sub_type_dict[row[1]] = row[0]
			return True
		else:
			return False

	def get_line_marker_type_id(self, line_marker_type, display_error=True):
		if line_marker_type in self.line_marker_dict:
			return self.line_marker_dict[line_marker_type]
		else:
			if display_error:
				self._error_macro(str(line_marker_type) + " line marker type not found. Try calling add first.")
			return -1

	def get_line_marker_sub_type_id(self, sub_type, display_error=True):
		if sub_type in self.line_marker_sub_type_dict:
			return self.line_marker_sub_type_dict[sub_type]
		else:
			if display_error:
				self._error_macro(str(sub_type) + " line marker sub type not found. Try calling add first.")
			return -1

	def add_line_marker_type(self, line_marker_type, comment=None):
		if self.common_check():
			if self.size(line_marker_type) > 0:
				if self.size(line_marker_type) < 46:

					line_marker_id = self.get_line_marker_type_id(line_marker_type, display_error=False)


					if line_marker_id > 0:
						return line_marker_id
					else:
						fields = []
						data = []

						fields.append("name")
						data.append(line_marker_type)

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

	def add_line_marker_sub_type(self, sub_type, comment=None):
		if self.common_check():
			if self.size(sub_type) > 0:
				if self.size(sub_type) < 46:

					line_marker_sub_type_id = self.get_line_marker_sub_type_id(sub_type, display_error=False)

					if line_marker_id > 0:
						return line_marker_sub_type_id
					else:
						fields = []
						data = []

						fields.append("name")
						data.append(sub_type)

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

						db_id = self.insert("line_marker_sub_type", fields, data, True)

						if db_id > 0:
							self.line_marker_sub_type_dict[sub_type] = db_id
							return db_id
					return -1
				else:
					self._error_macro("Line marker sub type is too long")
					return -1
			else:
				self._error_macro("Line marker sub type is too short")
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

	def get_tag_result_id(self, tag, display_error=True):
		if tag in self.result_tag_dict:
			return self.result_tag_dict[tag]["id"]
		else:
			if display_error:
				self._error_macro(str(tag) + " result tag not found. Try calling add first.")
			return -1

	def add_result_tag(self, tag, comment=None):
		if self.common_check(project_root=True, project_child=True):
			if self.size(tag) > 0:
				if self.size(tag) < 16:

					result_id = self.get_tag_result_id(tag, display_error=False)

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

	def get_target_id(self, name, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			if self.size(name) > 0:
				if self.size(name) < 46:
					fields = []
					data = []

					fields.append("fk_project_child_id")
					data.append(self.project_child_id)

					fields.append("name")
					data.append(name)

					target_rows = self.select("target_id", "target", fields, data)

					if self.size(target_rows) > 0:
						return target_rows[0][0]
					else:
						if display_error:
							self._error_macro("target not found.")
						return -2
				else:
					self._error_macro("Target name is too long")
					return -1
			else:
				self._error_macro("Target name is too short")
				return -1
		else:
			return -1

	def add_target(self, name, comment=None):
		target_id = self.get_target_id(name, display_error=False)

		if target_id == -2:
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

			db_id = self.insert("target", fields, data, True)

			if db_id > 0:
				self.history("Target: " + str(name) + " added.", "target", "auto")
				return db_id
			else:
				return db_id
		else:
			return target_id

	def get_variant_root_id(self, target, arch, variant, display_error=True):
		target_id = self.get_target_id(target, display_error=display_error)

		if target_id > 0:
			arch_id = self.get_arch_id(arch, display_error=display_error)
			if arch_id > 0:
				fields = []
				data = []

				fields.append("fk_target_id")
				data.append(target_id)

				fields.append("fk_arch_id")
				data.append(arch_id)


				if self.size(variant) > 0:
					if self.size(variant) <  81:
						fields.append("variant")
						data.append(variant)
					else:
						self._error_macro("The variant is too long")
						return -1
				else:
					self._error_macro("The variant is too short")
					return -1

				variant_rows = self.select("variant_root_id", "variant_root", fields, data)

				if self.size(variant_rows) > 0:
					return variant_rows[0][0]
				else:
					if display_error:
						self._error_macro("Variant root not found.")
					return -2
			else:
				return arch_id
		else:
			return target_id


	def add_variant_root(self, target, arch, variant, comment=None):
		variant_root_id = self.get_variant_root_id(target, arch, variant, display_error=False)

		if variant_root_id == -2:
			target_id = self.get_target_id(target)
			arch_id = self.get_arch_id(arch)

			fields = []
			data = []

			fields.append("fk_target_id")
			data.append(target_id)

			fields.append("fk_arch_id")
			data.append(arch_id)

			fields.append("variant")
			data.append(variant)

			db_id = self.insert("variant_root", fields, data, True)

			if db_id > 0:
				return db_id
			else:
				return db_id

		else:
			return variant_root_id

	def get_variant_exec_info(self, variant_exec_id):
		if self.common_check():
			query = 'SELECT target.name as target, arch.name as arch, variant_root.variant FROM target, arch, variant_root, variant_exec WHERE variant_exec.fk_variant_root_id=variant_root.variant_root_id and variant_root.fk_target_id=target.target_id and variant_root.fk_arch_id=arch.arch_id and variant_exec_id=%s'
			self.query(query, (variant_exec_id, ))

			result_rows = self.cursor.fetchall()

			size = self.size(result_rows)

			if size == 0:
				self._error_macro("No records where found for the provided variant exec_id")
				return None
			elif size == 1:
				return {"target": result_rows[0][0], "arch": result_rows[0][1], "variant": result_rows[0][2]}
			elif size > 1:
				self._error_macro("Expected only one record to be found for the provided variant exec id, but found %d" % size)
				return None
			else:
				self._error_macro("This should not happen size value set to ")
				return None
		else:
			return None

	def get_variant_exec_id(self, target, arch, variant, display_error=True):
		if self.common_check(project_root=True, project_child=True, exec_id=True):
			variant_root_id = self.get_variant_root_id(target, arch, variant, display_error=display_error)

			if variant_root_id > 0:
				fields = []
				data = []

				fields.append("fk_exec_id")
				data.append(self.exec_id)

				fields.append("fk_variant_root_id")
				data.append(variant_root_id)

				variant_exec_rows = self.select("variant_exec_id", "variant_exec", fields, data)

				if self.size(variant_exec_rows) > 0:
					return variant_exec_rows[0][0]
				else:
					if display_error:
						self._error_macro("Variant root not found.")
					return -2
			else:
				return variant_root_id
		else:
			return -1


	def add_variant_exec(self, target, arch, variant, time=None, comment=None):
		variant_exec_id = self.get_variant_exec_id(target, arch, variant, display_error=False)

		if variant_exec_id != -2:
			self.reset_variant_exec_id()
			self.variant_exec_id = variant_exec_id
			return variant_exec_id
		else:
			variant_root_id = self.get_variant_root_id(target, arch, variant)

			if variant_root_id > 0:
				fields = []
				data = []

				fields.append("fk_exec_id")
				data.append(self.exec_id)

				fields.append("fk_variant_root_id")
				data.append(variant_root_id)

				if time:
					in_seconds = None
					try:
						in_seconds = int(time)
					except:
						pass

					if in_seconds:
						fields.append("exec_time_secs")
						data.append(in_seconds)

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

				db_id = self.insert("variant_exec", fields, data, True)

				if db_id > 0:
					self.reset_variant_exec_id()
					self.variant_exec_id = db_id
				return db_id
			else:
				return variant_root_id

	def get_bug_root_id(self, recorder_type, unique_ref, display_error=True):
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
						if display_error:
							self._error_macro("project root not found.")
						return -2
				else:
					self._error_macro("Unique reference is too long")
					return -1
			else:
				self._error_macro("Unique refernce is too short")
				return -1
		else:
			return -1

	def add_bug_root(self, recorder_type, unique_ref, summary=None, comment=None):
		bug_root_id = self.get_bug_root_id(recorder_type, unique_ref, display_error=False)

		if bug_root_id == -2:
			fields = []
			data = []

			fields.append("recorder_enum")
			data.append(recorder_type)

			fields.append("unique_ref")
			data.append(unique_ref)

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
			else:
				return -1
		else:
			return bug_root_id

	def get_project_bug_id(self, recorder_type, unique_ref, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			bug_root_id = self.get_bug_root_id(recorder_type, unique_ref, display_error=display_error)
			if bug_root_id > 0:
				fields = []
				data = []

				fields.append("fk_bug_root_id")
				data.append(bug_root_id)

				fields.append("fk_project_child_id")
				data.append(self.project_child_id)

				project_bug_rows = self.select("project_bug_id", "project_bug", fields, data)

				if self.size(project_bug_rows) > 0:
					return project_bug_rows[0][0]
				else:
					if display_error:
						self._error_macro("project bug not found.")
					return -2

			else:
				return bug_root_id
		else:
			return -1

	def add_project_bug(self, recorder_type, unique_ref, summary=None, comment=None):
		if self.common_check(project_root=True, project_child=True):
			bug_root_id = self.add_bug_root(recorder_type, unique_ref, summary, comment)

			if bug_root_id > 0:
				project_bug_id = self.get_project_bug_id(recorder_type, unique_ref, display_error=False)

				if project_bug_id > 0:
					return project_bug_id
				else:
					fields = []
					data = []

					fields.append("fk_bug_root_id")
					data.append(bug_root_id)

					fields.append("fk_project_child_id")
					data.append(self.project_child_id)

					fields.append("triaged_enum")
					data.append("no")

					fields.append("resolved_enum")
					data.append("no")

					fields.append("added_enum")
					data.append("test_ref")

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

					db_id = self.insert("project_bug", fields, data, True)

					if db_id > 0:
						return db_id
					else:
						return -1

			else:
				return bug_root_id
		else:
			return -1

	def get_bug_exec_id(self, line_marker_id, recorder_type, unique_ref, display_error=True):
		if self.common_check():
			project_bug_id = self.get_project_bug_id(recorder_type, unique_ref)

			if project_bug_id:
				fields = []
				data = []

				fields.append("fk_project_bug_id")
				data.append(project_bug_id)

				fields.append("fk_line_marker_id")
				data.append(line_marker_id)

				bug_exec_rows = self.select("bug_exec_id", "bug_exec", fields, data)

				if self.size(bug_exec_rows) > 0:
					return bug_exec_rows[0][0]
				else:
					if display_error:
						self._error_macro("Crash exec not found.")
					return -2
			else:
				return project_bug_id
		else:
			return -1

	def add_bug_exec(self, line_marker_id, recorder_type, unique_ref, comment=None):
		bug_exec_id = self.get_bug_exec_id(line_marker_id, recorder_type, unique_ref, display_error=False)

		if bug_exec_id == -2:
			project_bug_id = self.get_project_bug_id(recorder_type, unique_ref)

			if project_bug_id:
				fields = []
				data = []

				fields.append("fk_project_bug_id")
				data.append(project_bug_id)

				fields.append("fk_line_marker_id")
				data.append(line_marker_id)

				db_id = self.insert("bug_exec", fields, data, False)

				return db_id
			else:
				return project_bug_id
		else:
			return bug_exec_id

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

	def get_crash_type_id(self, name, display_error=True):
		if name in self.crash_type_dict:
			return self.crash_type_dict[name]
		else:
			if display_error:
				self._error_macro(str(name) + " crash type not found. Try calling add first.")
			return -1

	def add_crash_type(self, name, comment=None):
		if self.common_check(project_root=True, project_child=True):
			if self.size(name) > 0:
				if self.size(name) < 46:

					crash_type_id = self.get_crash_type_id(name, display_error=False)

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

	def get_test_suite_id(self, suite_name, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			if self.size(suite_name) > 0:
				if self.size(suite_name) < 61:
					fields = []
					data = []

					fields.append("fk_project_child_id")
					data.append(self.project_child_id)

					fields.append("name")
					data.append(suite_name)

					suite_name_rows = self.select("test_suite_root_id", "test_suite_root", fields, data)

					if self.size(suite_name_rows) > 0:
						return suite_name_rows[0][0]
					else:
						if display_error:
							self._error_macro("test suite name not found.")
						return -2
				else:
					self._error_macro("Suite name is too long")
					return -1
			else:
				self._error_macro("Suite name is too short")
				return -1
		else:
			return -1

	def add_test_suite(self, suite_name, comment=None):
		test_suite_id = self.get_test_suite_id(suite_name, display_error=False)

		if test_suite_id == -2:
			fields = []
			data = []

			fields.append("fk_project_child_id")
			data.append(self.project_child_id)

			fields.append("name")
			data.append(suite_name)

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

			db_id = self.insert("test_suite_root", fields, data, True)
			if db_id > 0:
				self.history("Test Suite: " + str(suite_name) + " added.", "suite", "auto")
				return db_id
		else:
			return test_suite_id

	def get_exec_abort_id(self, abort_name, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			if self.size(abort_name) > 0:
				if self.size(abort_name) < 46:
					fields = []
					data = []

					fields.append("fk_project_child_id")
					data.append(self.project_child_id)

					fields.append("name")
					data.append(abort_name)

					exec_abort = self.select("exec_abort_id", "exec_abort", fields, data)

					if self.size(exec_abort) > 0:
						return exec_abort[0][0]
					else:
						if display_error:
							self._error_macro("exec abort name not found.")
						return -2
				else:
					self._error_macro("Abort name is too long")
					return -1
			else:
				self._error_macro("Abort name is too short")
				return -1
		else:
			return -1

	def add_exec_abort(self, abort_name, comment=None):
		exec_abort_id = self.get_exec_abort_id(abort_name, display_error=False)

		if exec_abort_id == -2:
			fields = []
			data = []

			fields.append("fk_project_child_id")
			data.append(self.project_child_id)

			fields.append("name")
			data.append(abort_name)

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

			db_id = self.insert("exec_abort", fields, data, True)
			if db_id > 0:
				self.history("Abort Type: " + str(abort_name) + " added.", "exec", "auto")
				return db_id
		else:
			return exec_abort_id

	def get_test_root_id(self, exec_path, name, params=None, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			if self.size(exec_path) > 0:
				if self.size(exec_path) < 65535:
					if self.size(name) > 0:
						if self.size(name) < 50:
							fields = []
							data = []

							fields.append("fk_project_child_id")
							data.append(self.project_child_id)

							fields.append("name")
							data.append(name)

							fields.append("exec_path")
							data.append(exec_path)

							if params:
								if self.size(params) > 0:
									if self.size(params) < 65535:
										fields.append("params")
										data.append(params)
									else:
										self._error_macro("Parameter stringis too long")
										return -1
								else:
									self._error_macro("Parameter string is too short")
									return -1

							test_root_rows = self.select("test_root_id", "test_root", fields, data)

							if self.size(test_root_rows) > 0:
								return test_root_rows[0][0]
							else:
								if display_error:
									self._error_macro("Test root not found.")
								return -2

						else:
							self._error_macro("Test name is too long")
							return -1
					else:
						self._error_macro("Test name is too short")
						return -1
				else:
					self._error_macro("exec path is too long")
					return -1
			else:
				self._error_macro("exec_path is too short")
				return -1
		else:
			return -1

	def add_test_root(self, exec_path, name, params=None, comment=None):
		test_root_id = self.get_test_root_id(exec_path, name, params, display_error=False)

		if test_root_id == -2:
			fields = []
			data = []

			fields.append("fk_project_child_id")
			data.append(self.project_child_id)

			fields.append("name")
			data.append(name)

			fields.append("exec_path")
			data.append(exec_path)

			fields.append("params")
			data.append(params)

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

			db_id = self.insert("test_root", fields, data, True)
			if db_id > 0:
				self.history("Test root: " + str(exec_path) + "/" + str(name) + " " + str(params) + " added.", "test", "auto")
				return db_id
		else:
			return test_root_id

	def get_test_revision_id(self, exec_path, name, params, revision_string=None, display_error=True):
		test_root_id = self.get_test_root_id(exec_path, name, params, display_error=display_error)

		if test_root_id > 0:
			fields = []
			data = []

			fields.append("fk_test_root_id")
			data.append(test_root_id)

			if self.size(revision_string) > 0:
				if self.size(revision_string) < 65535:
					fields.append("unique_ref")
					data.append(revision_string)
				else:
					self._error_macro("The revision string is too long")
					return -1
			else:
				revision_string = "base"
				fields.append("unique_ref")
				data.append("base")

			test_rev_rows = self.select("test_revision_id", "test_revision", fields, data)

			if self.size(test_rev_rows) > 0:
				return test_rev_rows[0][0]
			else:
				if display_error:
					self._error_macro("Test revision was not found!")
				return -2
		else:
			return test_root_id

	def add_test_revision(self, exec_path, name, params, revision_string=None, comment=None):
		test_revisison_id = self.get_test_revision_id(exec_path, name, params, revision_string, display_error=False)
		if test_revisison_id > 0:
			return test_revisison_id
		else:
			test_root_id = self.add_test_root(exec_path, name, params, comment)

			if test_root_id > 0:
				fields = []
				data = []

				fields.append("fk_test_root_id")
				data.append(test_root_id)

				if self.size(revision_string) > 0:
					if self.size(revision_string) < 65535:
						fields.append("unique_ref")
						data.append(revision_string)
					else:
						self._error_macro("The revision string is too long")
						return -1
				else:
					revision_string = "base"
					fields.append("unique_ref")
					data.append("base")

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

				db_id = self.insert("test_revision", fields, data, True)

				if db_id > 0:
					self.history("Test revision: " + str(exec_path) + "/" + str(name) + " " + str(params) + "Rev: (" + revision_string + ") added.", "test", "auto")
					return db_id
				else:
					return db_id
			else:
				return -1

	def get_exec_type_id(self, exec_type, display_error=True):
		if self.common_check():
			fields = []
			data = []

			if self.size(exec_type) > 0:
				if self.size(exec_type) < 46:
					fields.append("name")
					data.append(exec_type)
				else:
					self._error_macro("The Execution type is too long")
					return -1
			else:
				self._error_macro("The Execution type is too short")
				return -1

			exec_type_rows = self.select("exec_type_id", "exec_type", fields, data)

			if self.size(exec_type_rows) > 0:
				return exec_type_rows[0][0]
			else:
				if display_error:
					self._error_macro("Execution type not found.")
				return -2
		else:
			return -1

	def add_exec_type(self, exec_type, comment):
		exec_type_id = self.get_exec_type_id(exec_type, False)

		if exec_type_id == 2:
			fields = []
			data = []

			fields.append("name")
			data.append(exec_type)

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

			db_id = self.insert("exec_type", fields, data, True)

			if db_id > 0:
				return db_id
			else:
				return db_id
		else:
			return exec_type_id

	def set_exec_id(self, exec_id):
		if self.common_check(project_root=True, project_child=True):
			if isinstance( exec_id, int ):
				if exec_id > 0:
					fields = []
					data = []
					fields.append("fk_project_child_id")
					data.append(self.project_child_id)

					fields.append("exec_id")
					data.append(exec_id)

					exec_rows = self.select("exec_id", "exec", fields, data)

					if self.size(exec_rows) > 0:
						self.reset_exec_id()
						self.exec_id = exec_rows[0][0]
						return exec_rows[0][0]
					else:
						self._error_macro("The provided exec id ("+ str(exec_id) +") was not found for the current specified child project.")
						return -2
				else:
					self._error_macro("Exec id must be an positive integer greater then 0.")
					return -1
			else:
				self._error_macro("Exec id must be an integer.")
				return -1
		else:
			return -1

	def register_exec(self, exec_type, comment=None):
		exec_type_id = self.get_exec_type_id(exec_type)

		if exec_type_id > 0:
			if self.common_check(project_root=True, project_child=True):
				fields = []
				data = []

				fields.append("fk_project_child_id")
				data.append(self.project_child_id)

				fields.append("fk_exec_type_id")
				data.append(exec_type_id)

				fields.append("user_name")
				data.append(self.reporter_user_name)

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

				db_id = self.insert("exec", fields, data, True)

				if db_id > 0:
					self.reset_exec_id()
					self.exec_id = db_id
					return db_id
				else:
					return db_id
			else:
				return -1
		else:
			return -1

	def add_src(self, src_type, url_path, unique_id, src_description, comment=None):
		if self.common_check(project_root=True, project_child=True, exec_id=True):
			valid_src_types  = ['build', 'cvs', 'svn', 'git', 'other', 'path']

			if src_type in valid_src_types:
				fields = []
				data = []

				fields.append("fk_exec_id")
				data.append(self.exec_id)

				if self.size(url_path) > 0:
					if self.size(url_path) < 65535:
						fields.append("url_path")
						data.append(url_path)
					else:
						self._error_macro("URL/Path is too long")
						return -1
				else:
					self._error_macro("URL/Path is too short")
					return -1

				if self.size(unique_id) > 0:
					if self.size(unique_id) < 65535:
						fields.append("unique_id")
						data.append(unique_id)
					else:
						self._error_macro("Unique identifier is too long")
						return -1
				else:
					self._error_macro("Unique identifier is too short")
					return -1

				# Check to see if this entry already exists.
				src_rows = self.select("src_id", "src", fields, data)

				if self.size(src_rows) > 0:
					return src_rows[0][0]
				else:
					if self.size(src_description) > 0:
						if self.size(src_description) < 65535:
							fields.append("description")
							data.append(src_description)
						else:
							self._error_macro("Unique identifier is too long")
							return -1
					else:
						self._error_macro("Unique identifier is too short")
						return -1

					db_id = self.insert("src", fields, data, True)
					return db_id
			else:
				self._error_macro(str(src_type) + " is not a valid source type.")
				return -1
		else:
			return -1

	def get_test_exec_id(self, result, test_suite_name, test_exec_path, test_name, test_params, test_unique_ref=None, display_error=True):
		if self.common_check(project_root=True, project_child=True, exec_id=True, variant_exec_id=True):
			result_tag_id = self.get_tag_result_id(result, display_error=display_error)

			if result_tag_id > 0:
				test_suite_id = self.get_test_suite_id(test_suite_name, display_error=display_error)

				if test_suite_id > 0:
					test_rev_id = self.get_test_revision_id(test_exec_path, test_name, test_params, test_unique_ref, display_error=display_error)

					if test_rev_id > 0:
						fields = []
						data = []

						fields.append("fk_variant_exec_id")
						data.append(self.variant_exec_id)

						fields.append("fk_test_suite_root_id")
						data.append(test_suite_id)

						fields.append("fk_test_revision_id")
						data.append(test_rev_id)

						fields.append("fk_result_tag_id")
						data.append(result_tag_id)

						# Check to see if this entry already exists.
						test_exec_rows = self.select("test_exec_id", "test_exec", fields, data)

						if self.size(test_exec_rows) > 0:
							return test_exec_rows[0][0]
						else:
							if display_error:
								self._error_macro("Test execution not found.")
							return -2
					else:
						return test_rev_id
				else:
					return test_suite_id
			else:
				return result_tag_id
		else:
			return -1

	def get_attachment_type_id(self, name, display_error=True):
		if self.common_check():
			fields = []
			data = []

			if self.size(name) > 0:
				if self.size(name) < 65535:
					fields.append("name")
					data.append(name)
				else:
					self._error_macro("Attachment type is too long")
					return -1
			else:
				self._error_macro("Attachment type is too short")
				return -1

			attachment_type_rows = self.select("attachment_type_id", "attachment_type", fields, data)

			if self.size(attachment_type_rows) > 0:
				return attachment_type_rows[0][0]
			else:
				if display_error:
					self._error_macro("Attachment type (" + str(name) + ") not found.")
				return -2
		else:
			return -1

	def add_attachment_type(self, name, mime_type, comment=None):
		attachment_type_id = self.get_attachment_type_id(name, display_error=False)

		if attachment_type_id == -2:
			fields = []
			data = []

			if self.size(name) > 0:
				if self.size(name) < 65535:
					fields.append("name")
					data.append(name)
				else:
					self._error_macro("Attachment type is too long")
					return -1
			else:
				self._error_macro("Attachment type is too short")
				return -1

			if self.size(mime_type) > 0:
				if self.size(mime_type) < 65535:
					fields.append("mime_type")
					data.append(mime_type)
				else:
					self._error_macro("The mime type is too long")
					return -1
			else:
				self._error_macro("The mime type is too short")
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

			db_id = self.insert("attachment_type", fields, data, True)

			return db_id

		else:
			return attachment_type_id


	def get_attachment_id(self, full_attachment_src_path, display_error=True):
		if self.common_check(project_root=True, project_child=True):
			fields = []
			data = []

			local_dir_name = os.path.dirname(full_attachment_src_path)
			base_name = os.path.basename(full_attachment_src_path)
			root_file_name, extension = os.path.splitext(base_name)

			if self.size(local_dir_name) == 0:
				local_dir_name = "."

			fields.append("fk_project_child_id")
			data.append(self.project_child_id)

			fields.append("src_path")
			data.append(local_dir_name)

			fields.append("base_file_name")
			data.append(root_file_name)

			fields.append("src_ext")
			data.append(extension)

			attachment_rows = self.select("attachment_id", "attachment", fields, data)

			if self.size(attachment_rows) > 0:
				return attachment_rows[0][0]
			else:
				if display_error:
					self._error_macro("Attachment (" + str(full_attachment_src_path) + ") not found.")
				return -2
		else:
			return -1

	def add_attachment(self, attachment_type, full_attachment_src_path, comment=None, supress_exec_id=False, supress_variant_exec_id=False):

		known_compressed_extensions = [".zip", ".gz"]

		if os.path.exists(full_attachment_src_path):
			if self.common_check(project_root=True, project_child=True):
				attachment_id = self.get_attachment_id(full_attachment_src_path, display_error=False)

				if attachment_id == -2:
					attachment_type_id = self.get_attachment_type_id(attachment_type)

					if attachment_type_id > 0:
						local_dir_name = os.path.dirname(full_attachment_src_path)
						base_name = os.path.basename(full_attachment_src_path)
						root_file_name, extension = os.path.splitext(base_name)
						storage_extension  = extension

						if self.size(local_dir_name) == 0:
							local_dir_name = "."

						fields = []
						data = []

						fields.append("fk_project_child_id")
						data.append(self.project_child_id)

						fields.append("fk_attachment_type_id")
						data.append(attachment_type_id)

						fields.append("src_path")
						data.append(local_dir_name)

						fields.append("base_file_name")
						data.append(root_file_name)

						fields.append("src_ext")
						data.append(extension)

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


						ftp = my_ftp(self.ftp_host,
									 self.ftp_user_name,
									 self.ftp_password,
									 log=self.get_log()
									)
						if ftp:
							if ftp.connect():

								# Attempt to change to the attachment directory.
								if ftp.chdir(str(self.attachment_path)) is not True:
									return -1

								dest_path = self.attachment_path
								relative_dest_path = "";

								if ftp.mkdir(self.project_root_name, True):
									if ftp.chdir(self.project_root_name):
										relative_dest_path = os.path.join(relative_dest_path, self.project_root_name)
									else:
										return -1
								else:
									return -1

								# Now create or move into the project child direcotry
								if ftp.mkdir(self.project_child_name, True):
									if ftp.chdir(self.project_child_name):
										relative_dest_path = os.path.join(relative_dest_path, self.project_child_name)

									else:
										return -1
								else:
									return -1

								if self.exec_id is not None:
									if supress_exec_id is False:
										fields.append("fk_exec_id")
										data.append(self.exec_id)

										exec_id_dir = "%06d" % int(self.exec_id);

										if ftp.mkdir(str(exec_id_dir), True):
											relative_dest_path = os.path.join(relative_dest_path, exec_id_dir)

											if ftp.chdir(os.path.join(dest_path, relative_dest_path)):

												if self.variant_exec_id is not None:
													if supress_variant_exec_id is False:
														variant_data = self.get_variant_exec_info(self.variant_exec_id)

														if variant_data:
															fields.append("fk_variant_exec_id")
															data.append(self.variant_exec_id)

															if ftp.mkdir(variant_data["target"], True):
																if ftp.chdir(variant_data["target"]):
																	relative_dest_path = os.path.join(relative_dest_path, variant_data["target"])
																else:
																	return -1
															else:
																return -1

															if ftp.mkdir(variant_data["arch"], True):
																if ftp.chdir(variant_data["arch"]):
																	relative_dest_path = os.path.join(relative_dest_path, variant_data["arch"])
																else:
																	return -1
															else:
																return -1

															if ftp.mkdir(variant_data["variant"], True):
																if ftp.chdir(variant_data["variant"]):
																	relative_dest_path = os.path.join(relative_dest_path, variant_data["variant"])
																else:
																	return -1
															else:
																return -1
														else:
															return -1
											else:
												return -1
										else:
											return -1


								fields.append("storage_rel_path")
								data.append(relative_dest_path)

								remote_path = os.path.join(dest_path, relative_dest_path)

								# We want to store only compressed files on the server
								# so see if this file is already compressed.
								if extension not in known_compressed_extensions:
									fields.append("compressed_state_enum")
									data.append("post_compressed_gz")

									# If not then we will compress it before we copy it
									new_file_name = "";
									index = 0
									output_path = ""

									for index in range(-1, 1000):
										if index == -1:
												storage_extension = ".gz"
												file_name = root_file_name + extension + storage_extension
										else:
												storage_extension = "-%03d" % index + ".gz"
												file_name = root_file_name + extension + storage_extension

										output_path = os.path.join(local_dir_name, file_name)

										if os.path.exists(output_path) is False:
											break

									if index >= 1000:
										self._error_macro(full_attachment_src_path + " Failed to find an acceptable name to generate a compressed file.")
										return -1

									fields.append("storage_ext")
									data.append(storage_extension)

									full_remote_path = os.path.join(remote_path, file_name)

									# Compressed the file
									with open(full_attachment_src_path, "rb") as fp_in:
										with gzip.open(output_path, "wb") as fp_output:
											shutil.copyfileobj(fp_in, fp_output)

									if ftp.binary_file_transfer_2_file(output_path, full_remote_path):
										# Now that the file has been stored. Remove the compressed file that we created from the local host.
										os.remove(output_path)

										db_id = self.insert("attachment", fields, data, True)

										return db_id
									else:
										return -1
								else:
									fields.append("compressed_state_enum")
									data.append("src_compressed")

									fields.append("storage_ext")
									data.append(storage_extension)

									full_remote_path = os.path.join(remote_path, base_name)

									if ftp.binary_file_transfer_2_file(full_attachment_src_path, full_remote_path):
										db_id = self.insert("attachment", fields, data, True)
										return db_id
									else:
										return -1
							else:
								return -1
						else:
							self._error_macro("Failed to create ftp object.")
							return -1
					else:
						return attachment_type_id
				else:
					return attachment_id
			else:
				return -1
		else:
			self._error_macro(full_attachment_src_path + " does not exist or is not accessable")
			return -1

	def get_line_marker_id(self, attachment_id, marker_type, start_line, end_line=None, sub_type="general", display_error=True):
		if self.common_check():
			marker_type_id = self.get_line_marker_type_id(marker_type,  display_error=display_error)

			if marker_type_id > 0:
				marker_sub_type_id = self.get_line_marker_sub_type_id(sub_type)

				if marker_sub_type_id > 0:

					fields = []
					data = []

					fields.append("fk_attachment_id")
					data.append(attachment_id)

					fields.append("fk_line_marker_type_id")
					data.append(marker_type_id)

					fields.append("fk_line_marker_sub_type_id")
					data.append(marker_sub_type_id)

					fields.append("start")
					data.append(start_line)

					query = 'SELECT line_marker_id FROM line_marker'

					query = query + " WHERE " + "=%s and ".join(fields) + "=%s"

					if end_line:
						query = query + " and end=%s"
						data.append(end_line)
					else:
						query = query + " and end IS NULL"

					self.query(query, data)

					line_markers_rows = self.cursor.fetchall()

					if self.size(line_markers_rows) > 0:
						return line_markers_rows[0][0]
					else:
						if display_error:
							self._error_macro("Matching line marker not found.")
						return -2
				else:
					return marker_sub_type_id
			else:
				return marker_type_id
		else:
			return -1

	def add_line_marker(self, attachment_id, marker_type, start_line, end_line=None, test_exec_id=None, sub_type="general", comment=None):
		if self.common_check():
			line_marker_id = self.get_line_marker_id(attachment_id, marker_type, start_line, end_line, display_error=False)

			if line_marker_id == -2:
				marker_type_id = self.get_line_marker_type_id(marker_type)

				if marker_type_id > 0:
					marker_sub_type_id = self.get_line_marker_sub_type_id(sub_type)

					if marker_sub_type_id > 0:

						fields = []
						data = []

						fields.append("fk_attachment_id")
						data.append(attachment_id)

						fields.append("fk_line_marker_type_id")
						data.append(marker_type_id)

						fields.append("fk_line_marker_sub_type_id")
						data.append(marker_sub_type_id)

						if end_line:
							fields.append("end")
							data.append(end_line)

						if test_exec_id:
							fields.append("fk_test_exec_id")
							data.append(test_exec_id)

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

						db_id = self.insert("line_marker", fields, data, True)

						return db_id
					else:
						return marker_sub_type_id
				else:
					return marker_type_id
			else:
				return line_marker_id
		else:
			return -1

	def get_test_exec_id(self, result, test_suite_name, test_exec_path, test_name, test_params, unique_test_rev_id=None, display_error=True):
		if self.common_check(project_root=True, project_child=True, exec_id=True, variant_exec_id=True):
			result_id = self.get_tag_result_id(result)
			if result_id > 0:
				suite_name_id = self.get_test_suite_id(test_suite_name)

				if suite_name_id > 0:
					test_revision_id = self.get_test_revision_id(test_exec_path, test_name, test_params, unique_test_rev_id)

					if test_revision_id:
						fields = []
						data = []

						fields.append("fk_variant_exec_id")
						data.append(self.variant_exec_id)

						fields.append("fk_test_suite_root_id")
						data.append(suite_name_id)

						fields.append("fk_test_revision_id")
						data.append(test_revision_id)

						fields.append("fk_result_tag_id")
						data.append(result_id)

						test_exec_rows = self.select("test_exec_id", "test_exec", fields, data)

						if self.size(test_exec_rows) > 0:
							return test_exec_rows[0][0]
						else:
							if display_error:
								self._error_macro("Test Exec: [" + str(test_suite_name) + "] " + str(test_exec_path) + "/"+ test_name + " " + test_params + " {" + result + "} not found.")
							return -2
					else:
						return test_revision_id
				else:
					return suite_name_id
			else:
				return result_id
		else:
			return -1

	def add_test_exec(self, result, test_suite_name, test_exec_path, test_name, test_params, exec_time=None, extra_time=None, unique_test_rev_id=None, comment=None):
		test_exec_id = self.get_test_exec_id(result, test_suite_name, test_exec_path, test_name, test_params, unique_test_rev_id, display_error=None)

		if test_exec_id == -2:
			result_id = self.get_tag_result_id(result)
			if result_id > 0:
				suite_name_id = self.get_test_suite_id(test_suite_name)

				if suite_name_id > 0:
					test_revision_id = self.get_test_revision_id(test_exec_path, test_name, test_params, unique_test_rev_id)

					if test_revision_id:
						fields = []
						data = []

						fields.append("fk_variant_exec_id")
						data.append(self.variant_exec_id)

						fields.append("fk_test_suite_root_id")
						data.append(suite_name_id)

						fields.append("fk_test_revision_id")
						data.append(test_revision_id)

						fields.append("fk_result_tag_id")
						data.append(result_id)

						if exec_time:
							try:
								exec_time = int(exec_time)
							except:
								exec_time = None

							if exec_time:
								fields.append("exec_time_secs")
								data.append(exec_time)
							else:
								self._error_macro("Exec time must be a whole number.")
								return -1

						if extra_time:
							try:
								extra_time = int(extra_time)
							except:
								extra_time = None

							if extra_time:
								fields.append("extra_time_secs")
								data.append(extra_time)
							else:
								self._error_macro("Extra time must be a whole number.")
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

						db_id = self.insert("test_exec", fields, data, False)

						return db_id

					else:
						return test_revision_id
				else:
					return suite_name_id
			else:
				return result_id
		else:
			return test_exec_id

	def get_test_metric_id(self, line_marker_id, value, unit, display_error=True):
		if self.common_check():
			fields = []
			data = []

			value = value + 1.0

			fields.append("fk_line_marker_id")
			data.append(line_marker_id)

			if self.size(unit) > 0:
				if self.size(unit) < 11:
					fields.append("unit")
					data.append(unit)
				else:
					self._error_macro("The unit is too long")
					return -1
			else:
				self._error_macro("The unit is too short")
				return -1


			query = 'SELECT test_metric_id FROM test_metric'

			query = query + " WHERE " + "=%s and ".join(fields) + "=%s"

			query = query + " and metric BETWEEN "  + str(value - 0.00000000001) + " and "  + str(value + 0.00000000001)

			self.query(query, data)

			line_markers_rows = self.cursor.fetchall()

			test_metric_rows = self.select("test_metric_id", "test_metric", fields, data)

			if self.size(test_metric_rows) > 0:
				return test_metric_rows[0][0]
			else:
				if display_error:
					self._error_macro("Test Metric not found.")
				return -2

		else:
			return -1

	def add_test_metric(self, line_marker_id, value, unit, comment=None):
		test_metric_id = self.get_test_metric_id(line_marker_id, value, unit, display_error=False)

		if test_metric_id == -2:
			fields = []
			data = []

			fields.append("fk_line_marker_id")
			data.append(line_marker_id)

			fields.append("metric")
			data.append(value * 1.0)

			fields.append("unit")
			data.append(unit)

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

			db_id = self.insert("test_metric", fields, data, False)

			return db_id
		else:
			return test_metric_id

	def get_crash_exec_id(self, line_marker_id, crash_type, display_error=True):
		if self.common_check():
			crash_type_id = self.get_crash_type_id(crash_type)

			if crash_type_id > 0:
				fields = []
				data = []

				fields.append("fk_line_marker_id")
				data.append(line_marker_id)

				fields.append("fk_crash_type_id")
				data.append(crash_type_id)

				crash_exec_rows = self.select("crash_exec_id", "crash_exec", fields, data)

				if self.size(crash_exec_rows) > 0:
					return crash_exec_rows[0][0]
				else:
					if display_error:
						self._error_macro("Crash exec not found.")
					return -2
			else:
				return crash_type_id
		else:
			return -1

	def add_crash_exec(self, line_marker_id, crash_type):
		crash_exec_id = self.get_crash_exec_id(line_marker_id, crash_type)

		if crash_exec_id == -2:
			crash_type_id = self.get_crash_type_id(crash_type)

			if crash_type_id > 0:
				fields = []
				data = []

				fields.append("fk_line_marker_id")
				data.append(line_marker_id)

				fields.append("fk_crash_type_id")
				data.append(crash_type_id)

				db_id = self.insert("crash_exec", fields, data, False)

				return db_id
			else:
				return crash_type_id
		else:
			return crash_exec_id

def test():
	report = TestReporter(user.sql_host,  user.sql_user_name, user.sql_password, "project_db")

	if report.connect():
		print "Project Root:", report.add_project_root("Mainline")
		print "Select Project Root:", report.select_project_root("Mainline")
		print "Project Child:", report.add_project_child("Kernel", "/media/BackUp/regression_data/logs", user.ftp_host, user.ftp_user_name, user.ftp_password)
		print "Select Child:", report.select_project_child("Kernel")

		print "Get Attachment Type:", report.get_attachment_type_id("primary_log")
		print "Add Attachment Type:", report.add_attachment_type("primary_log", "plain/text", "Primary log file")
		print "Add Attachment Type:", report.add_attachment_type("build", "plain/text", "BSP Build file")
		print "Add Attachment Type:", report.add_attachment_type("site", "plain/text", "Site EXP File")
		print "Add Attachment Type:", report.add_attachment_type("symbol", "binary", "Symbol File")
		print "Add Attachment Type:", report.add_attachment_type("image", "plain/text", "Image text file")
		print "Add Attachment Type:", report.add_attachment_type("sum", "plain/text", "Yoyo Sum File")
		print "Add Attachment Type:", report.add_attachment_type("kdump_index", "plain/text", "Kdump index file")
		print "Add Attachment Type:", report.add_attachment_type("kdump", "plain/text", "Kdump File")
		print "Get Attachment Type:", report.get_attachment_type_id("primary_log")

		print "Add Arch:", report.add_arch("x86")
		print "Add Arch:", report.add_arch("x86_64")
		print "Add Arch:", report.add_arch("arm")
		print "Add Arch:", report.add_arch("aarch64")
		print "Add Arch:", report.add_arch("ppc")
		print "Add Arch:", report.add_arch("mips")
		print "Add Arch:", report.add_arch("x86")
		print "Line Marker:", report.add_line_marker_type("test download")
		print "Line Marker:", report.add_line_marker_type("bad_transfer")
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

		print "Get Project Bug:", report.get_project_bug_id("jira", "123456789")
		print "Get Project Bug:", report.get_project_bug_id("jira", "123456790")
		print "Add Project Bug:", report.add_project_bug("jira", "123456789")
		print "Add Project Bug:", report.add_project_bug("jira", "123456789")
		print "Add Project Bug:", report.add_project_bug("jira", "123456790")
		print "Add Project Bug:", report.add_project_bug("jira", "123456790")
		print "Get Project Bug:", report.get_project_bug_id("jira", "123456789")
		print "Get Project Bug:", report.get_project_bug_id("jira", "123456790")


		print "Add Crash Type: ", report.add_crash_type("sigsegv")
		print "Add Crash Type: ", report.add_crash_type("sigill")
		print "Add Crash Type: ", report.add_crash_type("sigbus")
		print "Add Crash Type: ", report.add_crash_type("shutdown")
		print "Add Crash Type: ", report.add_crash_type("kdump")
		print "Add Crash Type: ", report.add_crash_type("sigsegv")
		print "Get Test Suite: ", report.get_test_suite_id("Testware_bob")
		print "Add Test Suite: ", report.add_test_suite("Testware_bob")
		print "Add Test Suite: ", report.add_test_suite("Testware_Fred")
		print "Add Test Suite: ", report.add_test_suite("Testware_Juan")
		print "Add Test Suite: ", report.add_test_suite("Testware_bob")
		print "Get Test Suite: ", report.get_test_suite_id("Testware_bob")
		print "Get Exec Abort: ", report.get_exec_abort_id("user_abort")
		print "Get Exec Abort: ", report.add_exec_abort("user_abort")
		print "Get Exec Abort: ", report.add_exec_abort("timeout")
		print "Get Exec Abort: ", report.add_exec_abort("user_abort")
		print "Get Exec Abort: ", report.get_exec_abort_id("user_abort")

		print "Get Test Root:", report.get_test_root_id("./", "Ian", "-is -the best")
		print "Get Test Root:", report.add_test_root("./", "Ian", "-is -the best")
		print "Get Test Root:", report.add_test_root("./", "Norman", "-is -odd")
		print "Get Test Root:", report.add_test_root("./", "Ian", "-is -the best")
		print "Get Test Root:", report.get_test_root_id("./", "Ian", "-is -the best")

		print "Get Test Rev:", report.get_test_revision_id("./", "Ian", "-is -the best", "2123411")
		print "Add Test Rev:", report.add_test_revision("./", "Ian", "-is -the best", "2123411")
		print "Add Test Rev:", report.add_test_revision("./", "Ian", "-is -the best", "2123411")
		print "Get Test Rev:", report.get_test_revision_id("./", "Ian", "-is -the best", "2123411")
		print "Add Test Rev:", report.add_test_revision("./", "Rebecca", "-awesome", "1")
		print "Get Test Rev:", report.get_test_revision_id("./", "Rebecca", "-awesome", "1")

		print "Get Test Rev:", report.get_test_revision_id("./", "None", "-awesome")
		print "Add Test Rev:", report.add_test_revision("./", "None", "-awesome")
		print "Get Test Rev:", report.get_test_revision_id("./", "None", "-awesome")

		print "Set Exec:", report.set_exec_id(100000)

		print "Set Exec:",


		rc = report.set_exec_id(1)
		print  rc

		if rc < 0:
			print "Register Exec:", report.register_exec("weekend")

		print "Set Exec:", report.set_exec_id(1)
		print "Add Src:", report.add_src("svn", "http://svn.shim.sham/man", "12345", "toolchain")
		print "Add Src:", report.add_src("svn", "http://svn.shim.sham/man", "12345", "toolchain")

		print "Get Test Rev:", report.get_test_revision_id("./", "None", "-awesome")

		print "Get Root Variant:", report.get_variant_root_id("qnet04", "x86_64", "o.smp")
		print "Add Root Variant:", report.add_variant_root("qnet04", "x86_64", "o.smp")
		print "Get Root Variant:", report.get_variant_root_id("qnet04", "x86_64", "o.smp")

		print "Get Variant Exec:", report.get_variant_exec_id("qnet04", "x86_64", "o.smp")
		print "Add Variant Exec:", report.add_variant_exec("qnet04", "x86_64", "o.smp")
		print "Add Variant Exec:", report.add_variant_exec("qnet20", "x86_64", "o.smp")
		print "Get Variant Exec:", report.get_variant_exec_id("qnet04", "x86_64", "o.smp")

		print "Get file id", report.get_attachment_id("./blob.txt")
		print "Add file", report.add_attachment("primary_log", "./blob.txt")

		print "Add file", report.add_attachment("primary_log", "TestReporter.py")
		print "Add file", report.add_attachment("primary_log", "TestReporter_2.py.zip")

		print "Get Test Exec:", report.get_test_exec_id("pass", "Testware_Juan", "./" ,"Ian",  "-is -the best", "2123411")
		print "Add Test Exec:", report.add_test_exec("pass", "Testware_Juan", "./" ,"Ian",  "-is -the best", "2123411")
		print "Get Test Exec:", report.get_test_exec_id("pass", "Testware_Juan", "./" ,"Ian",  "-is -the best", "2123411")

		print "Get Line Marker", report.get_line_marker_id(1,"test", 0, 100)
		print "Add Line Marker", report.add_line_marker(1,"test", 0, 100, test_exec_id=1)
		print "Get Line Marker", report.get_line_marker_id(1,"test", 0, 100)
		print "Add Line Marker", report.add_line_marker(1,"test", 0, None, test_exec_id=1)
		print "Get Line Marker", report.get_line_marker_id(1,"test", 0, None)


		print "Get Test Metric ID", report.get_test_metric_id(2, 0.234, "secs")
		print "Add Test Metric", report.add_test_metric(1, 0.234, "secs")
		print "Get Test Metric ID", report.get_test_metric_id(1, 0.234, "secs")

		print "Get Crash Exec ID", report.get_crash_exec_id(1, "sigsegv")
		print "Add Crash Exec", report.add_crash_exec(1, "sigsegv")
		print "Get Crash Exec ID", report.get_crash_exec_id(1, "sigsegv")

		print "Get Bug EXEC ID ", report.get_bug_exec_id(1, "jira", "123456789")
		print "Add Bug EXEC ", report.add_bug_exec(1, "jira", "123456789")
		print "Get Bug EXEC ID ", report.get_bug_exec_id(1, "jira", "123456789")


		print "Done"

		report.commit()

