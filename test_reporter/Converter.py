import os, sys
import user
import argparse
from pprint import pformat
from  TestReporter import *

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *


class Convert(My_SQL):

	def _copy_projects(self):
		query = 'SELECT * from project'
		self.query(query)
		rows = self.cursor.fetchall()
		for row in rows:
			project_id = self.report.register_project(row[1], row[2], user.ftp_host, user.ftp_usr_name, user.ftp_password, "/media/BackUp/regression_data/logs/" , "Red")
			self.project_dict[project_id] = row[1]
			self.report.add_tag("PASS", "The test completed with a PASS status", "GREEN")
			self.report.add_tag("FAIL", "The test completed with a FAILED status", "RED")
			self.report.add_tag("XPASS", "The test completed with a XFAIL status", "YELLOW")
			self.report.add_tag("XFAIL", "The test completed with a XPASS status", "ORANGE")
			self.report.add_tag("UNRESOLVED", "The test completed with a UNRESOLVED status", "PURPLE")
			self.report.add_tag("UNTESTED", "The test completed with a UNTESTED status", "BLUE")
			self.report.add_crash_type("SIGSERV", "Crash")
			self.report.add_crash_type("SIGILL", "Crash")
			self.report.add_crash_type("SIGBUS", "Crash")
			self.report.add_crash_type("KDUMP", "Crash")
			self.report.add_crash_type("SHUTDOWN", "Crash")


	def process_sources(self, exec_id):
		query = 'SELECT * from sources WHERE exec_id=' + str(exec_id)
		self.query(query)
		sources_rows = self.cursor.fetchall()
		for sources_row in sources_rows:
			self.report.register_src(sources_row[2], sources_row[4], sources_row[5], description=sources_row[3])

	def process_results(self, variant_id):
		query = 'SELECT id, start_line, end_line, download_time, exec_time, crash_counter, suite_name, result, test_path, test_name, test_params FROM master WHERE variant_id=' + str(variant_id)
		self.query(query)
		result_rows = self.cursor.fetchall()

		for result_row in result_rows:
			suite_id = self.report.add_test_suite(result_row[6])
			test_rev_id = self.report.add_test_revision(result_row[8], result_row[9], result_row[10])
			test_id = self.report.add_test(suite_id, test_rev_id)

			result_id = self.report.add_test_result(result_row[7].upper(), result_row[1], result_row[2], result_row[4], result_row[3], result_row[5])

			if result_id > 0:
				pass
			else:
				raise Exception("This is no good!")


	def process_variant_only_level_attachments(self, variant_id, exec_id, target, arch, variant):

		base_path = "/media/BackUp/regression_data/gz"

		project = self.report.get_project()

		file_path = os.path.join(base_path, project)
		file_path = os.path.join(file_path, str(exec_id))
		file_path = os.path.join(file_path, target)
		file_path = os.path.join(file_path, arch)
		file_path = os.path.join(file_path, variant)
		file_path = os.path.join(file_path, "yoyo.log.gz")

		add_id = self.report.add_attachments(file_path, "primary", "text/plain", force_post_compress_tag=True)

		if add_id < 0:
			raise Exception("Adding the file has failed!!!")

		query = 'SELECT type, file_name, file_comment, mime_type, exec_id from attachment WHERE  test_result_id=0 and  variant_id=' + str(variant_id)
		self.query(query)
		variant_attachment_rows = self.cursor.fetchall()

		if project is None:
			raise Exception("Project name was returned as NONE that should not happen.")

		for varinat_attachment_row in variant_attachment_rows:
			force_post_compress_tag = False
			file_path = os.path.join(base_path, project)
			file_path = os.path.join(file_path, str(exec_id))
			file_path = os.path.join(file_path, target)
			file_path = os.path.join(file_path, arch)
			file_path = os.path.join(file_path, variant)
			file_path = os.path.join(file_path, varinat_attachment_row[1])

			if not os.path.exists(file_path):
				file_path = file_path + ".gz"
				force_post_compress_tag = True

			if os.path.exists(file_path):

				comment = None
				if varinat_attachment_row[1] != "yoyo.sum":
					comment = varinat_attachment_row[1]

					if len(comment) <= 0:
						comment=None
				add_id = self.report.add_attachments(file_path, varinat_attachment_row[0], varinat_attachment_row[0], comment=comment, force_post_compress_tag=force_post_compress_tag)

				if add_id < 0:
					raise Exception("Adding the file has failed!!!")
			else:
				raise Exception(file_path + " does not exist");

	def process_variants(self, exec_id):
		query = 'SELECT id, target, arch, variant, hide, abort_flag, time from variant WHERE exec_id=' + str(exec_id)
		self.query(query)
		variant_rows = self.cursor.fetchall()

		for variant_row in variant_rows:
			varinat = variant_row[3]
			if varinat.find("smp") == -1:
				if varinat.find("uni") == -1:
					pos = varinat.find(".")
					if pos == -1:
						varinat = varinat + ".uni"
					else:
						varinat = varinat[:pos] + ".uni" + varinat[pos:]

			self.report.add_variant(variant_row[1], variant_row[2], varinat, variant_row[6],  variant_row[5], variant_row[4])

			# process variant only level attachments
			self.process_variant_only_level_attachments(variant_row[0], exec_id, variant_row[1], variant_row[2], variant_row[3])

			# update test results for this variant just after it was added.
			self.process_results(variant_row[0])
			self.report.commit()

	def process_on_exec(self):
		query = 'SELECT id, project_id, user_name, created, description from exec_tracker'
		self.query(query)
		exec_rows = self.cursor.fetchall()

		for exec_row in exec_rows:
			#First make sure we have the right project selected.
			self.report.select_project(self.project_dict[exec_row[1]])

			#Set the user name
			self.report.set_report_user_name(exec_row[2])

			print "=" * 20, exec_row[0], type(exec_row[0]), "=" * 20

			if exec_row[0] == 56:
				# We missed an exec (55) in the old database so add a stub for it here so 56 aligns correctly.
				self.report.register_exec()

			#Register the exec in the new DB
			if self.report.set_exec_id(exec_row[0]) is False:
				self.report.register_exec(exec_row[4], time=exec_row[3])

			# process the sources associated with the exec
			self.process_sources(exec_row[0])

			# process the variants for the execution
			self.process_variants(exec_row[0])

	def go(self, to_host, to_sql_user, to_sql_password, to_db):
		self.project_dict = {}
		self.report = TestReporter(to_host, to_sql_user, to_sql_password, db_name="result_db", log=self.get_log())
		if self.report:
			if self.report.connect():

				# add arches
				self.report.add_arch("x86","Red")
				self.report.add_arch("sh", "Green")
				self.report.add_arch("mips", "Black")
				self.report.add_arch("ppc", "Blue")
				self.report.add_arch("arm", "Yellow")
				self.report.add_arch("x86_64", "Purple")
				self.report.add_arch("aarch64", "Cyan")

				# add targets
				self.report.add_target("adsom-7222")
				self.report.add_target("advantech-7226")
				self.report.add_target("aimb272-12185")
				self.report.add_target("amd64-dual-2")
				self.report.add_target("amdk6ii-1")
				self.report.add_target("amdk6iii-1")
				self.report.add_target("amdk7-1")
				self.report.add_target("atom-6354")
				self.report.add_target("beagleblack")
				self.report.add_target("beaglexm-1")
				self.report.add_target("beaglexm-2")
				self.report.add_target("bigbertha-8455")
				self.report.add_target("bigintel-7990")
				self.report.add_target("bigmac")
				self.report.add_target("ct11eb")
				self.report.add_target("ds81-shuttle-001")
				self.report.add_target("hasswell-bc5ff4e8872e")
				self.report.add_target("imb-151")
				self.report.add_target("imb-151-6336")
				self.report.add_target("imb-151-6342")
				self.report.add_target("imb-151-6352")
				self.report.add_target("imx600044-20015160")
				self.report.add_target("imx6q-sabresmart-00049f02e082")
				self.report.add_target("imx6q-sabresmart-6115")
				self.report.add_target("ivybridge-2554")
				self.report.add_target("jasper-8092")
				self.report.add_target("kontron-flex-7229")
				self.report.add_target("kontron-flex-7230")
				self.report.add_target("ktron-uepc-7234")
				self.report.add_target("mvdove-7213")
				self.report.add_target("mvdove-7791")
				self.report.add_target("mx6q-sabrelite-12252")
				self.report.add_target("nvidia-7903")
				self.report.add_target("nvidia-erista-8091")
				self.report.add_target("nvidia-erista-8093")
				self.report.add_target("nvidia-loki-6769")
				self.report.add_target("nvidia-loki-6790")
				self.report.add_target("nvidia-loki-6961")
				self.report.add_target("omap3530-6363")
				self.report.add_target("omap3530-7098")
				self.report.add_target("omap3530-7099")
				self.report.add_target("omap3530-7567")
				self.report.add_target("omap4430-9095")
				self.report.add_target("omap4430-9221")
				self.report.add_target("omap5432-es2-2206")
				self.report.add_target("omap5432-es2-2716")
				self.report.add_target("panda-12659")
				self.report.add_target("panda-12660")
				self.report.add_target("panda-12676")
				self.report.add_target("panda-12677")
				self.report.add_target("pcm9562-8166")
				self.report.add_target("qnet02")
				self.report.add_target("qnet04")
				self.report.add_target("qnet05")
				self.report.add_target("sandybridge-001")
				self.report.add_target("smpmpxpii")
				self.report.add_target("tolapai-6109")

				if self.connect():
					self._copy_projects()
					self.process_on_exec()
				else:
					self._error_macro("Failed to connect to the old DB")

				self.report.commit()
			else:
				self._error_macro("Failed to conenct to the new DB")
		else:
			self._error_macro("Failed to create reporter object")


convert = Convert("serenity.bts.rim.net", user.sql_name, user.sql_password, db_name="qa_db")

convert.go("serenity.bts.rim.net", user.sql_name, user.sql_password, "result_db")


