import argparse
import sys, os, shutil, time
import re
import user
from TestReporter import TestReporter, DEBUG, ERROR, WARNING

from pprint import pformat

# Debug Levels
# 8 - Show all output lines for sum file
# 7 - Show lines that were not processed by the parser for the sum file
# 6 - Show all output lines for log file
# 5 - Show lines that were not processed by the parser for the log file

test_point_prefix = ["METRIC",
					 "START",
					 "STOP",
					 "POINT",
					 "PASSX",
					 "PASS",
					 "FAILX",
					 "FAIL",
					 "UNRES",
					 "UNRESOLVED",
					 "UNSUP",
					 "UNSUPPORTED",
					 "UNTESTED",
					 "BOOT",
					 "boot",
					 "WARN",
					 "ERR",
					 "ERROR",
					 "NOTE",
					 "ABORT"]

arch_type_file_path_breaks = ["$PROCTYPE",
							  "aarch64",
							  "arm",
							  "x86",
							  "x86_64",
							  "ssh",
							  "mips",
							  "ppc"
							]

def dmdty2time(input_string):
	# convert this format (Fri May 29 22:18:39 2015) to python time
	return time.strptime(input_string, "%a %b %d %H:%M:%S %Y")

def generate_regex_prefix():
	start = []
	middle = []
	end = []

	max_middle_size = 0
	min_middle_size = 10000000000

	for prefix in test_point_prefix:
		size = len(prefix)

		size = size - 2;

		if (size - 2) > max_middle_size:
			max_middle_size = size

		if size < min_middle_size:
			min_middle_size = size

		if prefix[0] not in start:
			start.append(prefix[0])

		if prefix[-1] not in end:
			end.append(prefix[-1])

		# Reminder range works from param_0 to param_1 - 1
		# We should subtract a second 1 because this is used
		# as a conversion of a length to a list index (starting at 0)
		# but above we already removed 2 so instead add 1
		for index in range(1, size + 1):
			if prefix[index] not in middle:
				middle.append(prefix[index])

	return "[" + "|".join(sorted(start)) + "][" + "|".join(sorted(middle)) + "]{" + str(min_middle_size) + "," + str(max_middle_size) + "}[" + "|".join(sorted(end)) + "]:\s"


def add_project(args, log):
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
		"host_system",
		"log_start_time_stamp",
		"boot",
		"boot_failure"
		"reboot"
		"download",
		"test_suite",
		"test",
		"exec"
		"stop",
		"final",
		"error",
		"memory fault",
		"ldd fault",
		"timeout",
		"never_started",
		"bad transfer",
		"bug_ref",
		"sigsegv",
		"sigill",
		"sigbus",
		"shutdown",
		"kdump",
		"stack_smashing",
		"failed_library_load",
		"log_end_time_stamp",
		"assertion_failure"
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
					log.out("Failed to connect to the mysql database.", ERROR)
					return False
			else:
				log.out("Child name is to short", ERROR)
				return False
		else:
			log.out("Project name is to short.", ERROR)
			return False
	else:
		return False

def fix_test_point_over_writes(args, log, src_path):
	log.out("Scanning for testpoint fixs ups", DEBUG, v=1)
	regex_test_point_prefix = generate_regex_prefix()
	# regular expresssion to look for any test point prefix that
	# does't start the line.
	regex_pattern = "(?P<testpnt>" + generate_regex_prefix() + ")(?P<the_rest>.*\n)"

	tstpnt_regex = re.compile(regex_pattern)

	if os.path.exists(src_path):
		file_data = []
		changed = False
		with open(src_path, "Ur") as fp_in:
			# use this one so the lines have "\n" at the end.
			file_data = fp_in.readlines()

		index = 0

		num_of_lines = len(file_data)

		while index < num_of_lines:
			result = tstpnt_regex.search(file_data[index])

			if result:
				matches = result.groupdict()

				if "testpnt" in matches:

					# Check to see if the prefix we foudn (minus ': ')
					# is in the list of known test point prefixes
					if matches["testpnt"][0:-2] in test_point_prefix:

						tst_pnt_str = matches["testpnt"]

						if "the_rest" in matches:
							tst_pnt_str = tst_pnt_str + matches["the_rest"]

						#Check to see if the testpoint line is at the start of the line.

						if file_data[index].find(tst_pnt_str) > 0:

							# Calculate the size of the test point string + 1 to account for the \n
							size = len(tst_pnt_str) + 1

							if (index + 1) < num_of_lines:
								if file_data[index+1].find("<QADEBUG>") == 0:
									if (index+2) < num_of_lines:
										# move 2 lines away into the buffer
										str_buffer = file_data[index+2]
										file_data[index+2] = file_data[index+1]
										file_data[index+1] = tst_pnt_str
										file_data[index] = file_data[index][0: ((size-1) * -1)] + str_buffer
									else:
										file_data[index+2] = file_data[index+1]
										file_data[index+1] = tst_pnt_str
								else:
									# Add add the end from the next line
									file_data[index] = file_data[index][0: ((size-1) * -1)] + file_data[index+1]
									# Add the found test point line to the next index.
									file_data[index+1] = tst_pnt_str
							else:
								# Just strip off the test point part.
								file_data[index] = file_data[index][0: ((size-1) * -1)]
								# Add the found test point line to the next index.
								file_data[index+1] = tst_pnt_str

							changed = True
							index = index + 1
			index = index + 1

		if changed and args["no_mod"] == False:
			log.out("Writing out updated:" + src_path, DEBUG, v=1)
			with open(src_path, "w") as fp_out:
				for line in file_data:
					fp_out.write(line)
		return True
	else:
		return False


def scan_for_repeated_lines(args, log, src_path):
	if os.path.exists(src_path):
		file_data = []
		del_lines = []

		changed = False
		with open(src_path, "Ur") as fp_in:
			file_data = fp_in.readlines()

		# Add one extra line so we know that if there are dups
		# to the end of the file they get processed.
		file_data.append("\n")

		index = 0

		while index < len(file_data):
			next_line = index + 1

			if len(file_data[index]) == 0 or file_data[index]=="\n":
				index = index + 1
				continue

			empty_line_counter = 0
			while next_line < len(file_data):
				if len(file_data[next_line]) == 0 or file_data[next_line]=="\n":
					next_line = next_line + 1
					empty_line_counter = empty_line_counter + 1
					continue

				if file_data[index] != file_data[next_line]:
					dup_line_count = (next_line - index)
					if dup_line_count > 2:
						changed = True
						file_data[index+1] = "Post Parsing Edit: Previous line repeated " +  str(dup_line_count - 1 - empty_line_counter) + " additional times. \n"

						for del_index in range(index+2, next_line):
							del_lines.append(del_index)
						index = next_line - 1
					break
				next_line = next_line + 1
			index = index + 1

		# If the file content changed then rewrite the file.
		if changed and args["no_mod"] == False:
			for del_index in reversed(del_lines):
				del file_data[del_index]

			# Remove the extra line we added above.
			del file_data[-1]

			with open(src_path, "w") as fp_out:
				for line in file_data:
					fp_out.write(line)

		return True
	else:
		log.out(src_path + " does not exist", ERROR)
		return False

def cleanup_yoyo_sum(args, log, fp, path):
	if scan_for_repeated_lines(args, log, os.path.join(path,"yoyo.sum")):
		return True
	else:
		return False

def cleanup_yoyo_log(args, log, fp, path):
	if scan_for_repeated_lines(args, log, os.path.join(path,"yoyo.log")):
		if fix_test_point_over_writes(args, log, os.path.join(path,"yoyo.log")):
			return True
		else:
			return False
	else:
		return False

def cleanup_log_files(args, log, fp, recovery_data):
	for root, dirs, files in os.walk(args["input"]):
		if "yoyo.sum" in files:
			completed_string = root + " " + "yoyo.sum cleanup completed"

			if completed_string not in recovery_data:
				if cleanup_yoyo_sum(args, log, fp, root):
					fp.write(completed_string+"\n")
				else:
					return False

		if "yoyo.log" in files:
			completed_string = root + " " + "yoyo.log cleanup completed"

			if completed_string not in recovery_data:
				if cleanup_yoyo_log(args, log, fp, root):
					fp.write(completed_string+"\n")
				else:
					return False
	return True


def process_yoyo_sum(args, log, yoyo_sum_path, line_regex):

	report = {}

	# Use a list and index so that items stay in the order they are found
	report["time_stamp_indexes"] = []
	report["test_point_indexes"] = []
	report["parsed_lines"] = []

	with open(os.path.join(yoyo_sum_path, "yoyo.sum"), "Ur") as fp_in:
		# Read in striping new lines this time.
		sum_file_data = fp_in.read().splitlines()
		index = 0
		size = len(sum_file_data)
		while index < size:
			if len(sum_file_data[index]) == 0:
				index = index + 1
				continue

			no_match= True

			result = line_regex["general_tst_pnt"].search(sum_file_data[index])
			if result:
				matches = result.groupdict()
				if matches["testpnt"][:-2] in test_point_prefix:
					report["test_point_indexes"].append({"sum": len(report["parsed_lines"]), "log":None})
					report["parsed_lines"] .append({"type": "TestPoint", "matches": matches, "start":  index, "end": index})
					no_match = False

			if no_match:
				result = line_regex["user_time_stamp"].search(sum_file_data[index])
				if result:
					matches = result.groupdict()
					report["time_stamp_indexes"].append(len(report["parsed_lines"]))
					report["parsed_lines"].append({"type": "user_time_stamp", "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
					no_match = False

			if no_match:
				result = line_regex["test_suite"].search(sum_file_data[index])
				if result:
					report["parsed_lines"].append({"type": "test_suite", "matches": result.groupdict(), "start":  index, "end": index})
					no_match = False

			if no_match:
				result = line_regex["host"].search(sum_file_data[index])
				if result:
					report["parsed_lines"].append({"type": "host", "matches": result.groupdict(), "start":  index, "end": index})
					no_match = False

			if no_match:
				log.out("Ignored SUM line: " + sum_file_data[index], DEBUG, v=7)
			else:
				log.out(sum_file_data[index], DEBUG, v=8)


			index = index + 1
	return report

def process_yoyo_log(args, log, yoyo_sum_path, line_regex, sum_result):
	# Use a list and index so that items stay in the order they are found.
	data = []

	report = {}

	# Use a list and index so that items stay in the order they are found
	report["time_stamp_indexes"] = []
	report["test_point_indexes"] = []
	report["parsed_lines"] = []


	ignore_lines = ["----------------------------------------------------",
					"send -s mkqaphys",
					"mkqaphys",
					"cd /tmp",
					" gkermit -iwqr -e 4096",
					"Type ? or HELP for help.",
					"C-Kermit>c",
					"Escape character: Ctrl-\ (ASCII 28, FS): enabled",
					"Type the escape character followed by C to get back,",
					"or followed by ? to see other options.",
					"?OpenSSL libraries do not match required version:",
					". C-Kermit built with OpenSSL 1.0.0e 6 Sep 2011",
					". Version found  OpenSSL 1.0.1 14 Mar 2012",
					"OpenSSL versions prior to 1.0.0 must be the same.",
					"Set LD_LIBRARY_PATH for OpenSSL 1.0.0e 6 Sep 2011.",
					"Or rebuild C-Kermit from source on this computer to make versions agree.",
					"C-Kermit makefile target: linux+krb5+openssl",
					"Or if that is what you did then try to find out why",
					"the program loader (image activator) is choosing a",
					"different OpenSSL library than the one specified in the build.",
					"All SSL/TLS features disabled.",
					"C-Kermit 9.0.302 OPEN SOURCE:, 20 Aug 2011, for Linux+SSL+KRB5",
					"Copyright (C) 1985, 2011,",
					"Trustees of Columbia University in the City of New York.",
					"echo",
					'No such file or directory',
					"=== yoyo tests ===",
					"=== yoyo Summary ===",
					"---------------------------------",
					"----------------------------",
					"-------------------------------------"
				   ]

	ignore_starts_with = ["Connecting to host",
						  "chmod a+rx",
						  "(Back at",
						  "gzip -fd <",
						  "rm -fv",
						  "rm: Removing file",
						  "cd $OLDPWD",
						  "ls -sd /proc"
						 ]


	with open(os.path.join(yoyo_sum_path, "yoyo.log"), "Ur") as fp_in:
		# Read in striping new lines this time.
		yoyo_file_data = fp_in.read().splitlines()

		last_matched_index = -1

		index = 0

		size = len(yoyo_file_data)

		boot_complete = False

		while index < size:

			if len(yoyo_file_data[index]) == 0 or yoyo_file_data[index]== "\n":
				index = index + 1
				continue

			if yoyo_file_data[index][0] == '#':
				yoyo_file_data[index]= yoyo_file_data[index][0][1:]

			#Remove white space from the start and the end of the string.
			yoyo_file_data[index] = yoyo_file_data[index].strip()

			# We checked it above, but maybe the string has changed size.
			if len(yoyo_file_data[index]) == 0 or yoyo_file_data[index]== "\n":
				index = index + 1
				continue

			for ignore_start in ignore_starts_with:
				pos = yoyo_file_data[index].find(ignore_start)

				if pos >= 0 and pos < 10:
					index = index + 1
					continue

			if len(yoyo_file_data[index]) == 0 or yoyo_file_data[index]== "\n":
				index = index + 1
				continue

			if yoyo_file_data[index] in ignore_lines:
				index = index + 1
				continue

			no_match = True
			# Cycle threw the define regexs for each line.
			for key, regex in line_regex.iteritems():
				# Search each line for multiple matches.
				# BECARE ABOUT WHICH LINES YOU MATCH AND EXECUTE A BREAK FROM. REMEMBER MULTIPLE PATTERNS CAN EXIST ON A LINE.

				result = regex.search(yoyo_file_data[index])
				if result:
					matches = result.groupdict()
					if key == "download":
						report["parsed_lines"].append({"type": key, "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
						no_match = False
						break

					elif key == "execute":
						report["parsed_lines"].append({"type": key, "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
						no_match = False
						break

					elif key == "exec":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "mem_proc":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "user_time_stamp":
						report["time_stamp_indexes"].append(len(report["parsed_lines"]))
						report["parsed_lines"].append({"type": key, "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
						no_match = False
						break
					elif key == "kermit_send":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "test_suite":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "test_suite_2":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "metric":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "host":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "stack_smashing":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "buffer_overflow":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "send-class":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "malloc_check_fail":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "exec_format_error":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "to_man_retries":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "general_tst_pnt":
						if matches["testpnt"][:-2] in test_point_prefix:
							report["test_point_indexes"].append(len(report["parsed_lines"]))
							report["parsed_lines"] .append({"type": "TestPoint", "matches": matches, "start":  index, "end": index})
							no_match = False
					elif key == "bug_ref":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "process_seg":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "assertion_failure":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					#elif key == "shutdown":
					#	report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
					#	no_match = False
					else:
						log.out("Regex match for unhandled key " + key, ERROR)
						return None

			if no_match:
				log.out("Ignored SUM line["+ str(index) +"]: (" + yoyo_file_data[index]+")", DEBUG, v=5)
			else:
				if boot_complete is False:
					report["parsed_lines"].append({"type": "boot", "start":  1, "end": index -1 })
					boot_complete = True

				log.out(yoyo_file_data[index], DEBUG, v=8)


			index = index + 1
	return report


def process_variants(args, log, fp, recovery_data):

	line_regex = {}

	line_regex["download"] = re.compile('<QADEBUG>Generic\s+Download\s+(?P<mode>Start|Stop)\s+on\s+<TS>\s*(?P<date>.+)\s*</TS\>\s*<BS>(?P<test_path>.+)\s*</BS></QADEBUG>')

	line_regex["execute"] = re.compile('<QADEBUG>Generic\s+Execute\s+(?P<mode>Start|Stop)\s+on\s+<TS>\s*(?P<date>.+)\s*</TS\>\s*<BS>(?P<test_path>.+)\s*</BS></QADEBUG>')

	# regular expresssion to look for any test point prefix that
	# does't start the line.
	line_regex["general_tst_pnt"] = re.compile("(?P<testpnt>" + generate_regex_prefix() + ")(?P<the_rest>.*)")

	# Look for time stamp lines in the form of Test Run By iamcdonald on Fri May 29 22:18:39 2015
	line_regex["user_time_stamp"] = re.compile('^Test\s+Run\s+By\s+(?P<user_name>[a-zA-Z0-9\_\-\s]+)\son\s(?P<date>.*)$')

	# Look for test suite start lines in the form of Running ../../../../../yoyo.suite/testware_aps.exp ...
	line_regex["test_suite"] = re.compile('Running\s+(?P<test_suite>[\./\/a-zA-Z0-9\-\_]+)\.(?P<ext>.{3,5})\s\.{3}$')

	line_regex["test_suite_2"] = re.compile('Using\s+list\s+(?P<test_suite>[\./\/a-zA-Z0-9\-\_]+)\.(?P<ext>.{3,5})')

	# Look for host system information in the form of host system: Linux titan 3.8.0-44-generic #66~precise1-Ubuntu SMP Tue Jul 15 04:04:23 UTC 2014 i686 i686 i386 GNU/Linux
	line_regex["host"] = re.compile('^host\ssystem\:\s(?P<host>.*)$')

	# Look for the basic Process SIG<Something> format
	line_regex["process_seg"] = re.compile('Process\s(?P<pid>\d+)\s\((?P<name>.+)\)\sterminated\s(?P<type>.+)\scode=(?P<the_rest>.*)')

	# Look for basic Shutdown message
	line_regex["shutdown"] = re.compile('(?P<shutdown>Shutdown\[)')

	# Look for ldd flault
	line_regex["ldd_fault"] = re.compile('(?P<ldd_fault>ldd:FATAL:)')

	# Look for Memory fault
	line_regex["memory_fault"] = re.compile('(?P<memory_fault>Memory\sfault)')

	# Look for SEND-class
	line_regex["send-class"] = re.compile('(?P<send_class>SEND-class command failed.)')

	line_regex["to_man_retries"] = re.compile('Fatal\s+Kermit\s+Protocol\s+Error:\s+Too\s+many\s+retries')

	line_regex["mem_proc"] = re.compile('^\s*(?P<proc_memory>\d+)\s+\/proc$')

	line_regex["stack_smashing"] = re.compile('(?P<stack_smashing>\*\*\*\s+stack\s+smashing\s+detected\s\*\*\*)')

	line_regex["buffer_overflow"] = re.compile('(?P<buffer_overflow>\*\*\*\s+buffer\s+overflow detected\s\*\*\*)')

	line_regex["kermit_send"] = re.compile('C-Kermit>send\s+(?P<path>.+)/(?P<test_name>.+)')

	line_regex["metric"] = re.compile('^(?P<desc>.+)\sVALUE:\s(?P<value>.+)\sUNITS:\s(?P<units>.+)$')

	line_regex["bug_ref"] = re.compile('(?P<bug_type>JI|PR|ji|pr)[_|:]*\s*(?P<value>\d{5,10})')

	line_regex["kernel_start"] = re.compile('(?P<kernel_dump_start>KERNEL\s+DUMP\s+START)')

	line_regex["kdump"] = re.compile("<QADEBUG>\s*kdumper\s+file\s+kdump\.(?P<index>\d+)\s*<BS>\s*(?P<path>.*)\s*</BS></QADEBUG>")

	line_regex["exec"] = re.compile("^\s*/tmp/(?P<exec>.+)$")

	line_regex["exec_format_error"] = re.compile('(?P<exec_format_error>Exec\s+format\s+error)')

	line_regex["assertion_failure"] = re.compile('Assertion\s+failed:(?P<assertion>.+)')

	line_regex["malloc_check_fail"] = re.compile('Malloc\s+Check\s+Failed:\s+(?P<malloc_check_fail>.+)')

	# Different kinds of user abort
	line_regex["keyboard_interrupt"] = re.compile('(?P<keyboard_intterupt>KeyboardInterrupt)')
	line_regex["user_interrupted"] = re.compile("(?P<user_interrupted>Got\s+a\s+INT\s+signal,\s+interrupted\s+by\s+user)")


	input_lenght = len(args["input"])

	data = {}

	for root, dirs, files in os.walk(args["input"]):

		relative_root = root[input_lenght:]

		if len(relative_root) > 0:
			if relative_root[0] == "/":
				relative_root = relative_root[1:]

		if "yoyo.sum" in files:
			log.out(root + " yoyo.sum", DEBUG, v=3)
			completed_string = root + " " + "yoyo.sum import completed"
			if completed_string not in recovery_data:
				data[relative_root] = {}
				data[relative_root]["SUM"] = process_yoyo_sum(args, log, root, line_regex)

				if len(data[relative_root]["SUM"]) > 0:
					#print pformat(data[relative_root]["SUM"])

					pass

				else:
					return False

		if "yoyo.log" in files:
			log.out(root + " yoyo.log", DEBUG, v=3)
			completed_string = root + " " + "yoyo.log import completed"
			if completed_string not in recovery_data:
				data[relative_root]["LOG"] = process_yoyo_log(args, log, root, line_regex, data[relative_root]["SUM"])

				if data[relative_root]["LOG"]:
					print pformat(data[relative_root]["LOG"])
				else:
					return False

	if args["project"] is None:
		log.out("No project was specified.", ERROR)
		return False

	if args["child"] is None:
		log.out("No child project was specified.", ERROR)
		return False

	return True

def parse(args, log):
	if os.path.exists(str(args["input"])):
		with (open("recovery.txt", "a+")) as fp:
			fp.seek(0, os.SEEK_SET)
			# read in the file and split on newline. (this removes the \n caracter from the end of the line.)
			recovery_data = fp.read().splitlines()

			# Check to see if the recovery file contains a input path
			# Then check to see if is the same as the current one.
			if len(recovery_data) > 0:
				if recovery_data[0] != args["input"]:
					# If they are not the same then reset this recover file for the new data.
					recovery_data = []
					fp.seek(0, os.SEEK_SET)
					fp.write(str(args["input"]) + "\n")
			else:
				fp.write(str(args["input"]) + "\n")

			if cleanup_log_files(args, log, fp,  recovery_data):

				if process_variants(args, log, fp, recovery_data):
					# Do not return from here, so that the recovery
					# file gets deleted if we are still on a success path.
					pass
				else:
					return False

		# If we get here and there are no errors. Then delete the recovery file.
		os.remove("recovery.txt")

	else:
		log.out("(" + args["input"] + ") does not exist or is not accessible", ERROR)
		return False

	return True

def main(argv=None):
	parser = argparse.ArgumentParser(description='Qnx Dejagnu parser')

	parser.add_argument('-add_project', '--add_project',
						action='store_true',
						help='')

	parser.add_argument('-no_mod', '--no_mod',
						action='store_true',
						help='')


	parser.add_argument('-project', '--project',
						help='')

	parser.add_argument('-child', '--child',
						help='')

	parser.add_argument('-input', '--input',
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



	args["reporter"] = TestReporter(args["mysql_host"],  args["mysql_user_name"], args["mysql_password"], args["schema"])

	log = args["reporter"].get_log()

	log.set_verbosity(DEBUG, args["verbosity"])

	str_buffer = "Input Parameters\n"

	log.out(str_buffer + ("=" * (len(str_buffer)-1)) + "\n" + pformat(args), DEBUG, v=1)

	if args["reporter"]:
		if args["add_project"]:
			if add_project(args, log):
				return 0
			else:
				return -1

		elif args["input"]:
			if parse(args, log):
				return 0
			else:
				return -1
		else:
			log.out("No activity command line argument found.", ERROR)
			return -1

	else:
		log.out("Creatation of reporter class failed.", ERROR)
		return -1

if __name__ == "__main__":
	sys.exit(main())
