import argparse
import sys
import user
from TestReporter import TestReporter
from pprint import pformat


def add_project(args):
	arches = ["aarch64", "arm", "mips", "ppc", "sh", "x86", "x86_64"]

	targets = ["adsom-7222",
		"advantech-7226",
		"aimb272-12185",
		"amd64-dual-2",
		"amdk6ii-1",
		"amdk6iii-1",
		"amdk7-1",
		"atom-6354",
		"beagleblack",
		"beaglexm-1",
		"beaglexm-2",
		"bigbertha-8455",
		"bigintel-7990",
		"bigmac",
		"ct11eb",
		"ds81-shuttle-001",
		"hasswell-bc5ff4e8872e",
		"imb-151",
		"imb-151-6336",
		"imb-151-6342",
		"imb-151-6352",
		"imx600044-20015160",
		"imx6q-sabresmart-00049f02e082",
		"imx6q-sabresmart-6115",
		"ivybridge-2554",
		"jasper-8092",
		"kontron-flex-7229",
		"kontron-flex-7230",
		"ktron-uepc-7234",
		"mvdove-7213",
		"mvdove-7791",
		"mx6q-sabrelite-12252",
		"nvidia-7903",
		"nvidia-erista-8091",
		"nvidia-erista-8093",
		"nvidia-loki-6769",
		"nvidia-loki-6790",
		"nvidia-loki-6961",
		"omap3530-6363",
		"omap3530-7098",
		"omap3530-7099",
		"omap3530-7567",
		"omap4430-9095",
		"omap4430-9221",
		"omap5432-es2-2206",
		"omap5432-es2-2716",
		"panda-12659",
		"panda-12660",
		"panda-12676",
		"panda-12677",
		"pcm9562-8166",
		"qnet02",
		"qnet04",
		"qnet05",
		"sandybridge-001",
		"smpmpxpii",
		"tolapai-6109"
	]

	test_results = [
		"pass",
		"xpass",
		"fail",
		"xfail",
		"unresolved",
		"untested"
	]


	crash_types = [
		"sigsegv",
		"sigill",
		"sigbus",
		"shutdown",
		"kdump"
	]


	line_markers = [
		"download",
		"test",
		"stop",
		"final",
		"crash",
		"memory fault",
		"ldd fault",
		"timeout",
		"never_started",
		"bad transfer",
	]

	if args["reporter"].check_ftp_path(args["ftp_host"], args["ftp_user_name"], args["ftp_password"], args["set_storage_path"]):

		project_name = raw_input("Project Name: ")

		if len(project_name) > 0:
			project_child_name = raw_input("Child name: ")
			if len(project_child_name) > 0:
				if args["reporter"].connect():

					args["reporter"].fix_auto_inc()


					if args["reporter"].add_project_root(project_name) < 0:
						return -1

					if args["reporter"].add_project_child(project_child_name,
														  args["set_storage_path"],
														  args["ftp_host"],
														  args["ftp_user_name"],
														  args["ftp_password"]) < 0:
						return -1

					for arch in arches:
						if args["reporter"].add_arch(arch) < 0:
							return -1

					for target in targets:
						if args["reporter"].add_target(target) < 0:
							return -1

					for test_result in test_results:
						if args["reporter"].add_result_tag(test_result) < 0:
							return -1

					for crash_type in crash_types:
						if args["reporter"].add_crash_type(crash_type) < 0:
							return -1

					for line_marker in line_markers:
						if args["reporter"].add_line_marker_type(line_marker) < 0:
							return -1

					if args["reporter"].add_attachment_type("yoyo_log", "plain/text", "Yoyo Log File") < 0:
						return -1

					if args["reporter"].add_attachment_type("yoyo_sum", "plain/text", "Yoyo Sum File") < 0:
						return -1

					if args["reporter"].add_attachment_type("build", "plain/text", "BSP Build File") < 0:
						return -1

					if args["reporter"].add_attachment_type("site", "plain/text", "Dejagnu Site File") < 0:
						return -1

					if args["reporter"].add_attachment_type("symbol", "application/binary", "Qnx Symbol File") < 0:
						return -1

					if args["reporter"].add_attachment_type("kdump_raw", "application/binary", "Raw KDump File") < 0:
						return -1

					if args["reporter"].add_attachment_type("kdump_index", "application/binary", "Kdump Index File") < 0:
						return -1

					if args["reporter"].add_attachment_type("kdump", "application/binary", "Dump file") < 0:
						return -1

					if args["reporter"].add_attachment_type("image_build", "plain/text", "BPS build results") < 0:
						return -1


					args["reporter"].commit()

					return True
				else:
					print "Failed to connect to the mysql database."
					return False
			else:
				print "Child name is to short"
				return False
		else:
			print "Project name is to short."
			return False
	else:
		return False

def main(argv=None):
	parser = argparse.ArgumentParser(description='Qnx Dejagnu parser')


	parser.add_argument('-add_project', '--add_project',
						action='store_true',
						help='')

	parser.add_argument('-set_storage_path', '--set_storage_path',
						default="/media/BackUp/regression_data/logs",
						help='')

	parser.add_argument('-schema', '--schema',
						help='',
						default='project_db')

	parser.add_argument('-exec_id', '--exec_id',
						help='',
						default=-1)

	parser.add_argument('-input_dir', '--input_dir',
						help='')

	parser.add_argument('-mysql_host', '--mysql_host',
						default=user.sql_host,
						help='')

	parser.add_argument('-mysql_user_name', '--mysql_user_name',
						default=user.sql_user_name,
						help='')

	parser.add_argument('-mysql_password', '--mysql_password',
						default=user.sql_password,
						help='')

	parser.add_argument('-jira_user_name', '--jira_user_name',
						default=user.jira_user_name,
						help='')

	parser.add_argument('-jira_password', '--jira_passwort',
						default=user.jira_password,
						help='')

	parser.add_argument('-ftp_host', '--ftp_host',
						default=user.ftp_host,
						help='')

	parser.add_argument('-ftp_user_name', '--ftp_user_name',
						default=user.ftp_user_name,
						help='')

	parser.add_argument('-ftp_password', '--ftp_password',
						default=user.ftp_password,
						help='')

	parser.add_argument('-build_collection', '--build_collection',
						help='')

	parser.add_argument('-v', '--verbosity', action='count', default=0)


	if argv is None:
		# If argv is not passed then use the system args
		# Remove the first element in the list because
		# that is the execution name which we don't care about.
		argv = sys.argv[1:]

	args = vars(parser.parse_args())
	print pformat(args)

	args["reporter"] = TestReporter(args["mysql_host"],  args["mysql_user_name"], args["mysql_password"], args["schema"])

	if args["reporter"]:
		if "add_project" in args:
			print add_project(args)

	else:
		print "Creatation of reporter class failed."
		return -1

if __name__ == "__main__":
	sys.exit(main())
