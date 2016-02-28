import argparse
import sys, os, shutil, json
from datetime import datetime
import re
import user
from TestReporter import TestReporter, DEBUG, ERROR, WARNING, EXCEPTION

from pprint import pformat


scan_enum = {"NOTHING": 0,
			 "DOWNLOAD_START": 1,
		     "SEND_TEST": 2,
			 "DOWNLOAD_STOP": 3,
			 "EXEC_START": 4,
			 "FREE_FOR_ALL": 5,
			 "EXEC_STOP": 6,
			 "FINAL": 7
			}

# Debug Levels
# 8 - Show all output lines for sum file
# 7 - Show lines that were not processed by the parser for the sum file
# 6 - Show all output lines for log file
# 5 - Show lines that were not processed by the parser for the log file


test_point_prefix = [
					# METRIC: is purposely keep out of this list and handled seperately.
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


arch_type_file_path_breaks = ["tests",
							  "$PROCTYPE",
							]

expected_sub_strings = ["(timeout) where is the STOP message?",
						"(timeout) kermit not responsive",
						"Assertion failed",
						"program crashed",
						"premature exit",
						"no pass",
						"no point",
						"kernel crash",
						"test not found",
						"never started",
						"kernel crash kdump",
						"No such file or directory",
						"cannot transfer file to target"]

valid_execution_types = ["daily", "weekend", "sanity"]


def dmdty2time(input_string):
	# convert this format (Fri May 29 22:18:39 2015) to python time
	return datetime.strptime(input_string, "%a %b %d %H:%M:%S %Y")

def get_test_parts(full_test_path):
	test_path = "."
	test_name = None
	test_params = None

	full_test_path = full_test_path.strip()
	full_test_path = full_test_path.replace("\\", "/")

	# Find the last occurance of /
	pos = full_test_path.rfind("/")
	if pos >= 0:

		test_path = full_test_path[0:pos].strip("/").strip()
		if len(test_path) > 3:
			if test_path[-3:] == "bin":
				test_path = test_path[0:-3].strip("/")

			if len(test_path) == 0:
				test_path = "."
		else:
			test_path = "."


		full_test_path = full_test_path[(pos+1):]

	# find the first occurance of " "
	pos = full_test_path.find(" ")

	if pos > 0:
		test_params = full_test_path[(pos+1):].strip()
		full_test_path = full_test_path[0:pos].strip()

	test_name = full_test_path
	return test_path, test_name, test_params



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
		"untested",
		"error"
	]


	crash_types = [
		"sigsegv",
		"sigill",
		"sigbus",
		"sigtrap",
		"shutdown",
		"kdump",
		"kernel_start"
	]

	line_markers = [
		"assertion_failure",
		"boot",
		"boot_failure",
		"buffer_overflow",
		"bug_ref",
		"download",
		"error",
		"exec",
		"execute",
		"exec_format_error",
		"failed_library_load",
		"full_test",
		"host_system",
		"kdump",
		"kermit_send",
		"kernel_start",
		"ldd_fault",
		"log_end_time_stamp",
		"log_start_time_stamp",
		"memory_fault",
		"mem_proc",
		"malloc_check_fail",
		"metric",
		"process_seg",
		"reboot",
		"send-class",
		"shutdown",
		"stack_smashing",
		"stop",
		"yoyo_log",
		"yoyo_sum",
		"test_suite",
		"test_point",   # for none final test results
		"timeout",

		# Test ones are for final results only
		"pass",
		"fail",
		"xpass",
		"xfail",
		"unresolved",
		"untested",
		"unsupported",
		"error"
	]

	line_marker_sub_types = [
		"Assertion failed",
		"program crashed",
		"premature exit",
		"no pass",
		"no point",
		"bad transfer",
		"kernel crash",
		"test not found",
		"never started",
		"kernel crash kdump",
		"No such file or directory",
		"sigbus",
		"sigill",
		"sigsegv",
		"sigtrap",
		"timeout",
		"start",
		"stop",
		"point",
		"err",
		"error",
		"warn",
		"boot",

		# These are for none final test results
		"start",
		"stop",
		"pass",
		"fail",
		"passx",
		"failx",
		"unres",
		"untested",
		"unsup"
	]

	if args["reporter"].check_ftp_path(args["ftp_host"], args["ftp_user_name"], args["ftp_password"], args["set_storage_path"]):

		if len(args["project"]) > 0:
			if len(args["child"]) > 0:
				if args["reporter"].connect():

					args["reporter"].fix_auto_inc()

					args["reporter"].set_now_override_string("2015-05-26 15:01:15")

					if args["reporter"].add_project_root(args["project"]) < 0:
						return -1

					if args["reporter"].add_project_child(args["child"],
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

					for line_marker_sub_type in line_marker_sub_types:
						if args["reporter"].add_line_marker_sub_type(line_marker_sub_type) < 0:
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

					if args["reporter"].add_attachment_type("pid", "plain/text", "yoyo pid file") < 0:
						return -1

					# Create one test_suite as a catch all in case one is not defined.
					if args["reporter"].add_test_suite("lost_and_found") < 0:
						return -1

					args["reporter"].commit()
					args["reporter"].close_connection()

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


def clean_line(line):
	# Strip extra white space from the left side
	line = line.lstrip()
	if len(line) > 0:
		# Look to see if the first character is a #
		if line[0] == "#":
			# Remove the # and strip from the left again
			line = line[1:].lstrip()
	return line

def fix_test_point_over_writes(args, log, src_path):

	do_not_fix = ["boot"]

	log.out("Scanning for testpoint fixs ups in " + src_path, DEBUG, v=1)
	regex_test_point_prefix = generate_regex_prefix()

	# regular expresssion to look for any test point prefix that
	# does't start the line.
	regex_pattern = "(?P<testpnt>" + generate_regex_prefix() + ")(?P<the_rest>.*\n)"
	line_2_pattern = "^(?P<testpnt>" + generate_regex_prefix() + ")(?P<the_rest>.*\n)"

	tstpnt_regex = re.compile(regex_pattern)
	line_2_regex = re.compile(line_2_pattern)
	if os.path.exists(src_path):
		file_data = []
		changed = False

		with open(src_path, "Ur") as fp_in:
			# use this one so the lines have "\n" at the end.
			file_data = fp_in.readlines()

		index = 0

		num_of_lines = len(file_data)

		while index < num_of_lines:
			line = clean_line(file_data[index])

			# Set to something that is not going to match the line 2 regex, but can not be None
			line_2 = ""

			if index + 1 < num_of_lines:
				line_2 = clean_line(file_data[index+1])

			if len(line) <= 0:
				index = index + 1
				continue

			if line[0] == "\n":
				index = index + 1
				continue

			still_to_process = line

			while still_to_process:
				result = tstpnt_regex.search(still_to_process)
				still_to_process = None

				if result:
					matches = result.groupdict()

					if "testpnt" in matches:

						# Check to see if the prefix we found (minus ': ')
						# is in the list of known test point prefixes
						if matches["testpnt"][0:-2] in test_point_prefix:

							tst_pnt_str = matches["testpnt"]

							if "the_rest" in matches:
								tst_pnt_str = tst_pnt_str + matches["the_rest"]
								still_to_process = matches["the_rest"]

							# ones not to fix
							if matches["testpnt"][:-2] in do_not_fix:
								index = index + 1
								continue

							# Occassionaly a line will have unexpected ord()=0 characters in it, so lets remove them.
							temp = []
							for char in line:
								if ord(char) > 0:
									temp.append(char)

							line = ''.join(temp)

							#Check to see if the testpoint line is at the start of the line.
							if line.find(tst_pnt_str) > 2:
								# Calculate the size of the test point string + 1 to account for the \n
								size = len(tst_pnt_str) + 1

								log.out("Bad Testpoint line to be repaired [" + str(index) + "]: " + file_data[index])

								if (index + 1) < num_of_lines:
									if line_2_regex.search(line_2):
										file_data[index] = file_data[index][0: ((size-1) * -1)]
										upper_part = file_data[(index+1):]
										file_data = file_data[0:index+1]
										file_data.append(tst_pnt_str)
										file_data = file_data + upper_part
										# go back and go over it again.
										index =  index - 1

										changed = True
									elif file_data[index+1].find("<QADEBUG>") == 0:
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
		if changed and args["no_mod"] == False:
			log.out("Writing out test point fix updates: " + src_path, DEBUG, v=1)
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

		max_lines = len(file_data)

		while index < max_lines:
			next_line = index + 1

			if len(file_data[index]) == 0 or file_data[index]=="\n":
				index = index + 1
				continue

			empty_line_counter = 0
			while next_line < max_lines:

				if len(file_data[next_line]) == 0 or file_data[next_line]=="\n":
					next_line = next_line + 1
					empty_line_counter = empty_line_counter + 1
					continue

				if file_data[index] != file_data[next_line]:
					dup_line_count = (next_line - index - empty_line_counter)
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

			log.out("Writing out dup line changes to " + src_path)

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

def truncate_test_line(args, log, test_line):
	test_line = test_line.replace("\\", "/")
	for word in arch_type_file_path_breaks:
		pos = test_line.rfind("/"+word+"/")
		if pos >= 0:
			test_line = test_line[(pos+len("/"+word+"/")):]
		if len(test_line) > 0:
			if test_line[0] == "/":
				test_line = test_line[1:]
	return test_line.strip()

def truncate_test_suite(test_suite):
	temp = test_suite.replace("\\", "/")
	pos = temp.rfind("/")

	if pos > 0:
		return temp[(pos+1):]
	else:
		return None

def process_yoyo_sum(args, log, yoyo_sum_path, line_regex):
	report = {}

	# Use a list and index so that items stay in the order they are found
	report["time_stamp_indexes"] = []
	report["parsed_lines"] = []

	with open(os.path.join(yoyo_sum_path, "yoyo.sum"), "Ur") as fp_in:
		# Read in striping new lines this time.
		sum_file_data = fp_in.read().splitlines()
		index = 0
		size = len(sum_file_data)

		none_error_counter = 0
		while index < size:
			if len(sum_file_data[index]) == 0:
				index = index + 1
				continue

			no_match = True

			result = line_regex["general_tst_pnt"].search(sum_file_data[index])
			if result:
				matches = result.groupdict()

				if matches["testpnt"][:-2] in test_point_prefix:
					if matches["testpnt"][:-2] == "ERROR":
						temp_string = matches["the_rest"].replace("\\", "/")

						if temp_string.find("/") == -1:
							matches["the_rest"] = "/error/tests/error/error error:" + matches["the_rest"]
					else:
						none_error_counter = none_error_counter + 1

					matches["the_rest"] = truncate_test_line(args, log, matches["the_rest"])
					report["parsed_lines"].append({"type": "TestPoint", "matches": matches, "start":  index, "end": index})

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
					matches = result.groupdict()

					test_suite_name = truncate_test_suite(matches["test_suite"])

					if test_suite_name:
						report["parsed_lines"].append({"type": "test_suite", "test_suite_name": test_suite_name, "matches": matches, "start":  index, "end": index})
						no_match = False
					else:
						log.out("Truncating the test suit string (" + matches["test_suite"] + ") has failed", EXCEPTION)

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

	if none_error_counter == 0:
		log.out("                                                            ADDING BOOTING ERROR BECAUSE OF SUM RESULTS!!!!!")


		result = line_regex["test_suite"].search("../../lost_and_found.exp ...")
		if result:
			matches = result.groupdict()

			test_suite_name = matches["test_suite"]
			test_suite_name = test_suite_name.replace("\\", "/")
			pos = test_suite_name.rfind("/")

			if pos > 0:
				test_suite_name = test_suite_name[(pos+1):]

			report["parsed_lines"].append({"type": "test_suite", "test_suite_name": test_suite_name, "matches": matches, "start":  index, "end": index})

		result = line_regex["general_tst_pnt"].search("FAIL: /home/tests/non/test/bad_boot")
		if result:
			matches = result.groupdict()
			if matches["testpnt"][:-2] in test_point_prefix:
				matches["the_rest"] = truncate_test_line(args, log, matches["the_rest"])
				report["parsed_lines"].append({"type": "TestPoint", "matches": matches, "start":  -1, "end": -1})
	return report

def process_yoyo_log(args, log, yoyo_sum_path, line_regex, sum_data):

	last_test_suite = "lost_and_found"

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
					"cd /tmp ",
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
					"-------------------------------------",
					"# cd $OLDPWD "
				   ]

	ignore_starts_with = ["Connecting to host",
						  "chmod a+rx",
						  "(Back at",
						  "gzip -fd <",
						  "rm -fv",
						  "rm: Removing file",
						  "ls -sd /proc"
						 ]


	with open(os.path.join(yoyo_sum_path, "yoyo.log"), "Ur") as fp_in:
		# Read in striping new lines this time.
		yoyo_file_data = fp_in.read().splitlines()

		last_matched_index = -1

		index = 0

		max_lines = len(yoyo_file_data)

		b_extra_debug = False
		none_error_counter = 0

		while index < max_lines:

			yoyo_file_data[index] = clean_line(yoyo_file_data[index])

			if len(yoyo_file_data[index]) == 0 or yoyo_file_data[index]== "\n":
				index = index + 1
				continue

			for ignore_start in ignore_starts_with:
				pos = yoyo_file_data[index].find(ignore_start)

				if pos >= 0 and pos < 1:
					index = index + 1
					continue

			if yoyo_file_data[index] in ignore_lines:
				index = index + 1
				continue

			log.out(yoyo_file_data[index]+"||", DEBUG, v=100)

			no_match = True

			# Cycle threw the define regexs for each line.
			for key, regex in line_regex.iteritems():
				# Search each line for multiple matches.
				# BECARE ABOUT WHICH LINES YOU MATCH AND EXECUTE A BREAK FROM. REMEMBER MULTIPLE PATTERNS CAN EXIST ON A LINE.

				result = regex.search(yoyo_file_data[index])
				if result:
					matches = result.groupdict()

					if key == "download":
						matches["test_path"] = truncate_test_line(args, log, matches["test_path"])
						report["parsed_lines"].append({"type": key, "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
						no_match = False
						break

					elif key == "execute":
						matches["test_path"] = truncate_test_line(args, log, matches["test_path"])
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
					elif key == "process_seg":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "kermit_send":
						matches["path"], test_name, test_params = get_test_parts(truncate_test_line(args, log, matches["path"]))
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "test_suite" :
						test_suite_name = truncate_test_suite(matches["test_suite"])

						if test_suite_name:
							report["parsed_lines"].append({"type": key, "test_suite": test_suite_name, "matches": matches ,"start":  index, "end": index })

							no_match = False
							break
						else:
							log.out("Truncation of test suite string (" + matches["test_suite"] + ") has failed", EXCEPTION)

					elif key == "test_suite_2":

						test_suite_name = truncate_test_suite(matches["test_suite"])

						if test_suite_name:
							report["parsed_lines"].append({"type": key, "test_suite": test_suite_name, "matches": matches ,"start":  index, "end": index })

							no_match = False
							break
						else:
							log.out("Truncation of test suite string (" + matches["test_suite"] + ") has failed", EXCEPTION)

					elif key == "reboot":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "metric":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "user_time_stamp":
						report["time_stamp_indexes"].append(len(report["parsed_lines"]))
						report["parsed_lines"].append({"type": key, "matches": matches, "date": dmdty2time(matches["date"]),"start":  index, "end": index })
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
					elif key == "ldd_fault":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "memory_fault":
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
					elif key == "keyboard_interrupt":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "user_interrupted":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
						break
					elif key == "kernel_start":
						# Determine the line scope of the shutdown later.
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "kdump":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "general_tst_pnt":
						if matches["testpnt"][:-2] in test_point_prefix:
							final_flag = False

							if matches["testpnt"][:-2] == "ERROR":
								temp_string = matches["the_rest"].replace("\\", "/")
								if temp_string.find("/") == -1:
									matches["the_rest"] = "/error/tests/error/error:" + matches["the_rest"]

							# Certain test point keys are not final results
							if matches["testpnt"][:-2] != "START" and  matches["testpnt"][:-2] != "STOP" and matches["testpnt"][:-2] != "NOTE" and matches["testpnt"][:-2] != "BOOT" and matches["testpnt"][:-2] != "boot" and matches["testpnt"][:-2] != "POINT":
								# The diffference between a final testpoint and a result test point can be very small.
								# The easiest way to tell is to look at the sum results and see if we have a match and then it is final test point
								for sum_regex in sum_data["parsed_lines"]:
									if sum_regex["type"] == "TestPoint":
										if sum_regex["matches"]["testpnt"] == matches["testpnt"]:
											the_rest = truncate_test_line(args, log, matches["the_rest"])
											if sum_regex["matches"]["the_rest"] == the_rest:
												if matches["testpnt"] != "ERROR: ":
													none_error_counter = none_error_counter + 1
												matches["the_rest"] = the_rest
												final_flag = True
												break

							report["parsed_lines"] .append({"type": "TestPoint", "final_flag": final_flag, "test_suite_name":	last_test_suite, "matches": matches, "start":  index, "end": index})
							no_match = False
					elif key == "bug_ref":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "assertion_failure":
						report["parsed_lines"].append({"type": key, "matches": matches ,"start":  index, "end": index })
						no_match = False
					elif key == "shutdown":
						# Determine the line scope of the shutdown later.
						report["parsed_lines"].append({"type": key, "matches": matches,   "start":  index, "end": max_lines })
						no_match = False
					else:
						log.out("Regex match for unhandled key " + key, ERROR)
						return None

			if no_match:
				log.out("Ignored LOG line["+ str(index) +"]: (" + yoyo_file_data[index]+")", DEBUG, v=7)
			else:
				log.out(yoyo_file_data[index], DEBUG, v=8)
			index = index + 1

	if none_error_counter == 0:
		log.out("                                                            ADDING BOOTING ERROR BECAUSE OF LOG RESULTS!!!!!")

		result = line_regex["test_suite"].search("../../lost_and_found.exp ...")
		if result:
			matches = result.groupdict()
			test_suite_name = matches["test_suite"]
			test_suite_name = test_suite_name.replace("\\", "/")
			pos = test_suite_name.rfind("/")

			if pos > 0:
				test_suite_name = test_suite_name[(pos+1):]

			report["parsed_lines"].append({"type": "test_suite", "test_suite_name": test_suite_name, "matches": matches, "start":  -1, "end": -1})

		result = line_regex["general_tst_pnt"].search("FAIL: /home/tests/non/test/bad_boot")
		if result:
			matches = result.groupdict()
			if matches["testpnt"][:-2] in test_point_prefix:
				matches["the_rest"] = truncate_test_line(args, log, matches["the_rest"])
				report["parsed_lines"].append({"type": "TestPoint", "final_flag": True,  "matches": matches, "start":  -1, "end": -1})

	return report

def print_list(log, the_list, pre_fix=""):
	for data in the_list["parsed_lines"]:
		if data["type"] == "TestPoint":
			log.out(str(pre_fix) + str(data["start"]) + ", " + str(data["end"]) + " " + data["matches"]["testpnt"] + data["matches"]["the_rest"])

def get_subtype(args, log, search_string):
	# Lets not look for : with in quotes on the command line.

	double_qoute_pos = search_string.rfind('"')
	single_qoute_pos = search_string.rfind("'")

	max_quote = max(double_qoute_pos, single_qoute_pos)

	#blahblah/test param:kdumper.0000

	if max_quote > 0:
		temp = search_string[(max_quote +1):]
	else:
		temp = search_string
		max_quote = 0

	splitter_position = temp.rfind(":")

	if splitter_position > 0:
		sub_string = temp[splitter_position+1:].strip()

		# Looking now for kernel crash kdump.00000
		period_pos = sub_string.rfind(".")

		if period_pos > 0:
			sub_string = sub_string[0:period_pos]

		if sub_string in expected_sub_strings:
			if sub_string == "(timeout) where is the STOP message?":
				return "timeout", search_string[:max_quote+splitter_position]
			elif sub_string == "(timeout) kermit not responsive":
				return "bad transfer", search_string[:max_quote+splitter_position]
			elif sub_string == "cannot transfer file to target":
				return "bad transfer", search_string[:max_quote+splitter_position]
			else:
				return sub_string, search_string[:max_quote+splitter_position]
		else:
			log.out("(" + sub_string + ") found after ':', but is not a recognised sub type value) [" + search_string + "]", EXCEPTION)
			return None, search_string[:max_quote+splitter_position]
	else:
		return None, search_string


def init_test_structure():
	return {"test_path": None, "test_name": None, "test_params": None, "test_suite": None, "log_parse_line_indexes":[], "last_log_match": scan_enum["NOTHING"], "exec_time": -1, "download_time": -1,"log_start":-1, "log_end":-1, "revision": None, "mem_before":-1, "mem_after":-1}

def is_new_test(args, logs, last_match, current_match):
	if last_match == scan_enum["DOWNLOAD_START"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		else:
			return False

	if last_match == scan_enum["SEND_TEST"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		if current_match == scan_enum["SEND_TEST"]:
			return True
		else:
			return False

	if last_match == scan_enum["DOWNLOAD_STOP"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		elif current_match == scan_enum["SEND_TEST"]:
			return True
		elif current_match == scan_enum["DOWNLOAD_STOP"]:
			return True
		else:
			return False


	if last_match == scan_enum["EXEC_START"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		elif current_match == scan_enum["SEND_TEST"]:
			return True
		elif current_match == scan_enum["DOWNLOAD_STOP"]:
			return True
		elif current_match == scan_enum["EXEC_START"]:
			return True
		else:
			return False

	if last_match == scan_enum["FREE_FOR_ALL"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		elif current_match == scan_enum["SEND_TEST"]:
			return True
		elif current_match == scan_enum["DOWNLOAD_STOP"]:
			return True
		elif current_match == scan_enum["EXEC_START"]:
			return True
		else:
			return False

	if last_match == scan_enum["EXEC_STOP"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		elif current_match == scan_enum["SEND_TEST"]:
			return True
		elif current_match == scan_enum["DOWNLOAD_STOP"]:
			return True
		elif current_match == scan_enum["EXEC_START"]:
			return True
		elif current_match == scan_enum["EXEC_STOP"]:
			return True

		# The STOP and FINAL testpoint are some times interchanged in the log so do not start a new test if there order is wrong.


		else:
			return False

	if last_match == scan_enum["FINAL"]:
		if current_match == scan_enum["DOWNLOAD_START"]:
			return True
		elif current_match == scan_enum["SEND_TEST"]:
			return True
		elif current_match == scan_enum["DOWNLOAD_STOP"]:
			return True
		elif current_match == scan_enum["EXEC_START"]:
			return True
		elif current_match == scan_enum["EXEC_STOP"]:
			return True
		elif current_match == scan_enum["FREE_FOR_ALL"]:
			return True

		# The STOP and FINAL testpoint are some times interchanged in the log so do not start a new test if there order is wrong.

		elif current_match == scan_enum["FINAL"]:
			return True
		else:
			return False

	return False


def find_next_match_index(test_list, current_test_index, test_path, test_name, test_params):
	test_list_length = len(test_list)

	for offset in range(current_test_index+1, test_list_length):
		if test_list[offset]["test_path"] == test_path and test_list[offset]["test_name"] == test_name and test_list[offset]["test_params"] == test_params:
			return offset
	return -1

def process_tests(args, log, sum_results, log_results, variant):

	kdump_regex = re.compile("^kdump.(?P<index>\d{5,10})\.elf.gz$")
	kdump_index_regex = re.compile("^kdump.(?P<index>\d{5,10})$")
	test_point_regex = re.compile("(?P<testpnt>" + generate_regex_prefix() + ")(?P<the_rest>.*)")


	last_test_suite = "lost_and_found"

	submit_dict = {}

	submit_dict["tests"] = []
	submit_dict["test_suites"] = []

	start_time = None
	end_time = None
	user_name = None

	if variant[-1] == "/":
		variant = variant[0:-1]

	variant_parts = variant.split("/")

	if len(variant_parts) >= 3:
		submit_dict["target"] = variant_parts[-3]
		submit_dict["arch"] = variant_parts[-2]
		submit_dict["variant"] = variant_parts[-1]
	else:
		log.out("Failed to resovle variant parts from variant: " + variant)

	# First see if we have two timestamp index:
	if "time_stamp_indexes" in sum_results:
		list_length = len(sum_results["time_stamp_indexes"])

		if list_length == 1:
			data = sum_results["parsed_lines"][sum_results["time_stamp_indexes"][0]]
			if user_name == None:
				user_name = data["matches"]["user_name"]

		elif list_length == 2:
			data_1 = sum_results["parsed_lines"][sum_results["time_stamp_indexes"][0]]
			data_2 = sum_results["parsed_lines"][sum_results["time_stamp_indexes"][1]]

			if data_1["matches"]["user_name"] == data_2["matches"]["user_name"]:
				start_time =  data_1["date"]
				end_time =  data_2["date"]

				if user_name == None:
					user_name = data_1["matches"]["user_name"]
				else:
					log.out("Miss match user name with in the yoyo.sum file", ERROR)

	# first see if we have two timestamp index:
	if "time_stamp_indexes" in log_results:
		list_length = len(log_results["time_stamp_indexes"])
		if list_length == 1:
			data = log_results["parsed_lines"][log_results["time_stamp_indexes"][0]]
			if user_name == None:
				user_name = data["matches"]["use_name"]

		elif list_length == 2:
			data_1 = log_results["parsed_lines"][log_results["time_stamp_indexes"][0]]
			data_2 = log_results["parsed_lines"][log_results["time_stamp_indexes"][1]]

			if data_1["matches"]["user_name"] == data_2["matches"]["user_name"]:
				if start_time is None:
					start_time =  data_1["date"]

				if end_time is None:
					end_time =  data_2["date"]

				if user_name == None:
					user_name = data["matches"]["user_name"]
			else:
				log.out("Miss match user name with in the yoyo.log file", ERROR)

	if user_name:
		submit_dict["user_name"] = user_name
	else:
		submit_dict["user_name"] = "unknown"

	if start_time and end_time:
		submit_dict["exec_time"] = (end_time-start_time).total_seconds()
	else:
		submit_dict["exec_time"] =-1

	index = 0
	max_index = len(sum_results["parsed_lines"])
	test_index = -1

	while index < max_index:
		regex_data = sum_results["parsed_lines"][index]

		if regex_data["type"] == "test_suite":
			last_test_suite = regex_data["test_suite_name"]
			submit_dict["test_suites"].append(last_test_suite)



		elif regex_data["type"] == "host":
			if "sum_host_index" not in  submit_dict:
				submit_dict["sum_host_index"] = index

		elif regex_data["type"] == "TestPoint":

			if regex_data["matches"]["testpnt"] != "boot: " and  regex_data["matches"]["testpnt"] != "BOOT: " and regex_data["matches"]["testpnt"] != "NOTE: " and regex_data["matches"]["testpnt"] != "POINT: ":
				regex_data["matches"]["the_rest"] = regex_data["matches"]["the_rest"].replace("\\", "/")

				sub_type, full_test_path = get_subtype(args, log, regex_data["matches"]["the_rest"])

				if sub_type is None:
					sub_type = "general"

 				test_path, test_name, test_params = get_test_parts(full_test_path)

				submit_dict["tests"].append(init_test_structure())
				test_index = test_index + 1

				if submit_dict["tests"][test_index]["test_suite"] is None:
					submit_dict["tests"][test_index]["test_suite"] = last_test_suite

				if submit_dict["tests"][test_index]["test_name"] is None:
					submit_dict["tests"][test_index]["test_name"] = test_name
					submit_dict["tests"][test_index]["sub_type"] = sub_type

				if submit_dict["tests"][test_index]["test_path"] is None:
					submit_dict["tests"][test_index]["test_path"] = test_path

				if submit_dict["tests"][test_index]["test_params"] is None and test_params is not None:
					submit_dict["tests"][test_index]["test_params"] = test_params


				submit_dict["tests"][test_index]["sum_index"] = index

		elif regex_data["type"] ==	"user_time_stamp":
			pass
		else:
			log.out(regex_data["type"] + " is not handled.........................", DEBUG, v=1)
			print pformat(sum_results["parsed_lines"][index])

		index = index + 1


	# We used yoyo.sum log to create a list of results and tests to sumbit.
	# Now we need to look at yoyo.log and add extra information.


	# This index tracks where we are in the submit list index
	# Start at -1 since no matches have been found yet.
	submit_test_index = -1

	# This value should also start at -1
	last_found_test_index = -1
	index = 0

	last_mem_proc = -1

	max_index = len(log_results["parsed_lines"])

	# Loop over the yoyo.log lines that have been parsed.

	while index < max_index:
		regex_data = log_results["parsed_lines"][index]

		# check to see if this current parsed  line is a test suite line.
		if regex_data["type"] == "test_suite" or regex_data["type"] == "test_suite_2":
			last_test_suite = regex_data["matches"]["test_suite"]

		# check to see if the current parsed line is a testpoint line.
		elif regex_data["type"] == "TestPoint":

			# check to see if this is a general test point line or a final result test point line.
			if regex_data["final_flag"]:

				regex_data["matches"]["the_rest"] = regex_data["matches"]["the_rest"].replace("\\", "/")

				# Break up the line if it is int he format of <TEST POINT KEY>: <test path>/<test name> <test params>:<sub type information>
				sub_type, full_test_path = get_subtype(args, log, regex_data["matches"]["the_rest"])

				if sub_type is None:
					sub_type = "general"

				regex_data["sub_type"] = sub_type

 				test_path, test_name, test_params = get_test_parts(full_test_path)

 				if submit_dict["tests"][submit_test_index]["test_name"] == test_name and submit_dict["tests"][submit_test_index]["test_path"] == test_path and submit_dict["tests"][submit_test_index]["test_params"] == test_params:

 					# check to see if this is a new test or part of one we are working on.
 					if is_new_test(args, log, submit_dict["tests"][submit_test_index]["last_log_match"], scan_enum["FINAL"]) is False:

						# Keep track of where we find the last line
						submit_dict["tests"][submit_test_index]["log_index"] = index
						submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
						submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

			else:
				# This is a general test point so just note it.
				if submit_test_index > 0:
					submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
					submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "bug_ref":

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "process_seg":
			# Sometimes we will have multiple process segments in a row that are the same type
			for offset in range(index+1, max_index):
				regex_data_2 = log_results["parsed_lines"][offset]

				if regex_data_2["type"] == "process_seg":
					if regex_data["matches"]["type"] == regex_data_2["matches"]["type"]:
						regex_data["repeated_end"] = regex_data_2["end"]
						index = offset
				else:
					break

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "download":
			# Get the path, name, and test parameters
			test_path, test_name, test_params = get_test_parts(regex_data["matches"]["test_path"])

			#Set the this is a new test flag to false.
			b_new_test = False

			# check to see if the current "Submit_test_index" has the same test name parameters as this test.
			if submit_dict["tests"][submit_test_index]["test_name"] == test_name and submit_dict["tests"][submit_test_index]["test_path"] == test_path and submit_dict["tests"][submit_test_index]["test_params"] == test_params:
				# It is the same...
				# check to see if this is a test start or a test end.
				if regex_data["matches"]["mode"] == 'Start':

					# if it is a test start then look and see if we have already passed a state that would be the start.
					if is_new_test(args, log, submit_dict["tests"][submit_test_index]["last_log_match"], scan_enum["DOWNLOAD_START"]):
						b_new_test = True
				else:
					# Check to see if we are at a stat in a test were stop should not appear.
					if is_new_test(args, log, submit_dict["tests"][submit_test_index]["last_log_match"], scan_enum["DOWNLOAD_STOP"]):
						b_new_test = True
			else:
				b_new_test = True

			# check to see if we think that this is a new test.
			if b_new_test:

				# The current log_results["parsed_lines"][index] appears to be a new test..
				# So look in the submit_dict["tests"] and try and find a test that matches it.
				submit_test_index = find_next_match_index(submit_dict["tests"], last_found_test_index, test_path, test_name, test_params)

				if submit_test_index >= 0:
					last_found_test_index = submit_test_index
					submit_dict["tests"][submit_test_index]["log_start"] = regex_data["start"]
				else:
					# It is possible for a test to appear in yoyo.log but not in sum.log
					# for instance if a test is running and the user aboarts.
					# The start of the test will appear in yoyo.log but no record of it will appear
					# in yoyo.sum even tho yoyo.sum will finishing writting out and provide the final tally.
					# so here we check to see if this test index would be great then the sum tests we found.

					list_lenght =  len(submit_dict["tests"])

					if (last_found_test_index + 1) < list_lenght:
						# if it isn't then generate and exeception
						if test_params:
							log.out("No match could be found for " + test_path + " " + test_name + " " + test_params, EXCEPTION)
						else:
							log.out("No match could be found for " + test_path + " " + test_name, EXCEPTION)
					else:

						end_line = -1

						if len(sum_results["parsed_lines"]) > 0:
							end_line = sum_results["parsed_lines"][-1]["end"]

						fake_sum = {'end':end_line, "start":-1, "type":"TestPoint", "matches": {'testpnt': "UNRESOLVED: ", 'the_rest': regex_data["matches"]["test_path"]} }

						sum_results["parsed_lines"].append(fake_sum)

						submit_structure = init_test_structure()
						submit_structure["test_path"] = test_path
						submit_structure["test_name"] = test_name
						submit_structure["test_params"] = test_params
						submit_structure["sum_index"] = len(sum_results["parsed_lines"])-1
						submit_structure["log_start"] = regex_data["start"]
						submit_structure["sub_type"] = "premature exit"
						submit_structure["test_suite"] = truncate_test_suite(last_test_suite)

						submit_dict["tests"].append(submit_structure)
						submit_test_index = list_lenght

			if regex_data["matches"]["mode"] == 'Start':
				submit_dict["tests"][submit_test_index]["last_log_match"] = scan_enum["DOWNLOAD_START"]
				submit_dict["tests"][submit_test_index]["d_start_time"] = regex_data["date"]
			else:
				submit_dict["tests"][submit_test_index]["last_log_match"] = scan_enum["DOWNLOAD_STOP"]
				if "d_start_time" in submit_dict["tests"][submit_test_index]:
					submit_dict["tests"][submit_test_index]["download_time"] = (regex_data["date"] - submit_dict["tests"][submit_test_index]["d_start_time"]).total_seconds()
					del submit_dict["tests"][submit_test_index]["d_start_time"]

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "execute":
			test_path, test_name, test_params = get_test_parts(regex_data["matches"]["test_path"])

			b_new_test = False

			if submit_dict["tests"][submit_test_index]["test_name"] == test_name and submit_dict["tests"][submit_test_index]["test_path"] == test_path and submit_dict["tests"][submit_test_index]["test_params"] == test_params:
				if regex_data["matches"]["mode"] == 'Start':
					if is_new_test(args, log, submit_dict["tests"][submit_test_index]["last_log_match"], scan_enum["EXEC_START"]):
						b_new_test = True
				else:
					if is_new_test(args, log, submit_dict["tests"][submit_test_index]["last_log_match"], scan_enum["EXEC_STOP"]):
						b_new_test = True
			else:
				b_new_test = True

			if b_new_test:
				submit_test_index = find_next_match_index(submit_dict["tests"], last_found_test_index, test_path, test_name, test_params)

				if submit_test_index >= 0:
					last_found_test_index = submit_test_index
					submit_dict["tests"][submit_test_index]["log_start"] = regex_data["start"]
				else:
					# It is possible for a test to appear in yoyo.log but not in sum.log
					# for instance if a test is running and the user aboarts.
					# The start of the test will appear in yoyo.log but no record of it will appear
					# in yoyo.sum even tho yoyo.sum will finishing writting out and provide the final tally.
					# so here we check to see if this test index would be great then the sum tests we found.

					list_lenght =  len(submit_dict["tests"])

					if (last_found_test_index + 1) < list_lenght:
						# if it isn't then generate and exeception
						if test_params:
							log.out("No match could be found for " + test_path + " " + test_name + " " + test_params, EXCEPTION)
						else:
							log.out("No match could be found for " + test_path + " " + test_name, EXCEPTION)
					else:
						end_line = -1

						if len(sum_results["parsed_lines"]) > 0:
							end_line = sum_results["parsed_lines"][-1]["end"]

						fake_sum = {'end':end_line, "start":-1, "type":"TestPoint", "matches": {'testpnt': "UNRESOLVED: ", 'the_rest': regex_data["matches"]["test_path"]} }

						sum_results["parsed_lines"].append(fake_sum)

						submit_structure = init_test_structure()
						submit_structure["test_path"] = test_path
						submit_structure["test_name"] = test_name
						submit_structure["test_params"] = test_params
						submit_structure["sum_index"] = len(sum_results["parsed_lines"])-1
						submit_structure["log_start"] = regex_data["start"]
						submit_structure["sub_type"] = "premature exit"

						submit_structure["test_suite"] = truncate_test_suite(last_test_suite)
						submit_dict["tests"].append(submit_structure)
						submit_test_index = list_lenght

			if regex_data["matches"]["mode"] == 'Start':
				submit_dict["tests"][submit_test_index]["last_log_match"] = scan_enum["EXEC_START"]
				submit_dict["tests"][submit_test_index]["e_start_time"] = regex_data["date"]
			else:
				submit_dict["tests"][submit_test_index]["last_log_match"] = scan_enum["EXEC_STOP"]

				if "e_start_time" in submit_dict["tests"][submit_test_index]:
					submit_dict["tests"][submit_test_index]["exec_time"] = (regex_data["date"] - submit_dict["tests"][submit_test_index]["e_start_time"]).total_seconds()
					del submit_dict["tests"][submit_test_index]["e_start_time"]

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]


		elif regex_data["type"] == "kernel_start":

			# see if we can determine the end line for this kernel start..
			for offset in range(index + 1, max_index):
				local_regex = log_results["parsed_lines"][offset]
				if local_regex["type"] != "shutdown" and local_regex["type"] != "TestPoint"  and local_regex["type"] != "kdump":
					regex_data["end"] = local_regex["start"] -1
					break

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "kdump":
			# see if we can determine the end line for this kernel start..
			for offset in range(index + 1, max_index):
				local_regex = log_results["parsed_lines"][offset]
				regex_data["end"] = local_regex["start"] -1

				if local_regex["type"] != "shutdown" and local_regex["type"] != "TestPoint":
					break

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "shutdown":
			# see if we can determine the end line for this shutdown..
			for offset in range(index + 1, max_index):
				local_regex = log_results["parsed_lines"][offset]
				regex_data["end"] = local_regex["start"] -1
				if local_regex["type"] != "TestPoint":
					break

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "reboot":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "mem_proc":

			if last_mem_proc > 0:
				submit_dict["tests"][submit_test_index]["mem_before"] = last_mem_proc

			mem_proc = -1
			try:
				mem_proc = int(regex_data["matches"]["proc_memory"])
			except:
				mem_proc = -1

			if mem_proc > 0:
				submit_dict["tests"][submit_test_index]["mem_after"] = mem_proc

			last_mem_proc = mem_proc

			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]
		elif regex_data["type"] == "kermit_send":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "exec":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "metric":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "buffer_overflow":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "memory_fault":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "assertion_failure":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "send-class":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "exec_format_error":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] == "malloc_check_fail":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]

		elif regex_data["type"] ==	"user_time_stamp":
			pass
		elif regex_data["type"] ==	"host":
			pass
		elif regex_data["type"] ==	"stack_smashing":
			if submit_test_index > 0:
				submit_dict["tests"][submit_test_index]["log_parse_line_indexes"].append(index)
				submit_dict["tests"][submit_test_index]["log_end"] = regex_data["end"]
		else:
			log.out(regex_data["type"] + " is not handled.........................", DEBUG, v=1)
			#print pformat(log_results["parsed_lines"][index])

		index = index + 1


	# print "=" * 80
	# print " SUMBIT DIC AFTER PROCESSING SUM AND LOG"
	# print "=" * 80

	# print pformat(submit_dict)

	if args["reporter"].connect():

		report = args["reporter"]

		rc = 1

		if "general_file_info" in args:
			if "info" in  args["general_file_info"]:
				if "date" in args["general_file_info"]["info"]:
					if report.set_now_override_string(args["general_file_info"]["info"]["date"]):
						rc = 1
					else:
						rc = -1

		# Set the use name
		if rc > 0:
			if user_name:
				rc = report.set_user_name(user_name)

		# Select the project the use name
		if rc > 0:
			rc = report.select_project_root(args["project"])

		# Select the child project
		if rc > 0:
			rc = report.select_project_child(args["child"])

		# Figure out if this is a daily or weekend regression from the
		# general file.
		# Use a set exec ID or get a new one
		if rc > 0:
			if args["exec_id"] <= 0:
				if "general_file_info" in args:
					if "info" in args["general_file_info"]:
						if "description" in args["general_file_info"]["info"]:
							exec_type = None

							pos = args["general_file_info"]["info"]["description"].find("daily")

							if pos != -1:
								exec_type = "daily"
							else:
								exec_type = "weekend"

							if exec_type:
								args["exec_id"] = report.register_exec(exec_type, comment=args["general_file_info"]["info"]["description"])

								if args["exec_id"] <= 0:
									log.out(str(args["exec_id"]) + " returned as the exec id", ERROR)
								else:
									report.disable_pre_check()

							else:
								log.out("Unable to determine execution type.", ERROR)
								rc = -1
						else:
							log.out("description dictionary missing from general info log file.", ERROR)
							rc = -1
					else:
						log.out("info dictionary missing from general info log file.", ERROR)
						rc = -1
				else:
					args["exec_id"] = report.register_exec("weekend")
					report.disable_pre_check()
			else:
				rc = report.set_exec_id(args["exec_id"])
				# precheck is enabled by default. So if we startup and have an exec id it should be on already
				# if insteasd the first time we import a variant we would use the regist the exec id. Then for the next
				# variant we would use the exec we already register and hit this point. But we don't want to enable precheck here.



		# see if we have source information in the general file.
		if rc > 0:
			log.out("Execute ID: " + str(args["exec_id"]))

			if "general_file_info" in args:
				info_length = len(args["general_file_info"])

				# Have to do length -1 here becuase there is a none numeric value ('info') in the dictionary.
				for index in range(0, info_length-1):
					src_data = args["general_file_info"][str(index)]

					rc = report.add_src(src_data["type"], src_data["url"], src_data["unique_id"], src_data["src_desc"])

					if rc <= 0:
						log.out("Adding src has failed.", ERROR)
			else:
				log.out("TODO: GET SOURCE INFOMATION FROM NONE GENERAL FILE SOURCE!!!", ERROR)
				rc = -1

		# Make sure that if the variant is not .smp that it is .uni
		if rc > 0:
			smp_pos = submit_dict["variant"].find("smp")
			uni_pos = submit_dict["variant"].find("uni")

			if smp_pos == -1 and uni_pos == -1:
				pos = submit_dict["variant"].find(".")
				if pos > 0:
					tmp = submit_dict["variant"]
					submit_dict["variant"] = tmp[0:pos] + ".uni" + tmp[pos:]

			rc = report.add_variant_root(submit_dict["target"], submit_dict["arch"], submit_dict["variant"])

			if rc > 0:
				if 'exec_time' in submit_dict:
					rc = report.add_variant_exec(submit_dict["target"], submit_dict["arch"], submit_dict["variant"], time=submit_dict["exec_time"])
				else:
					rc = report.add_variant_exec(submit_dict["target"], submit_dict["arch"], submit_dict["variant"])

				if rc <= 0:
					log.out("Adding variant exec failed.", ERROR)
			else:
				log.out("Adding variant root failed.", ERROR)

		# Write all the test suites we are going to use, to the database.
		if rc > 0:
			if 'test_suites' in submit_dict:
				# add test suites

				for test_suite in submit_dict["test_suites"]:
					log.out("Import Test Suite (" +  test_suite + ").... ", DEBUG, v=5)
					rc = report.add_test_suite(test_suite)

					if rc <= 0:
						break

		# Keep track of the sumbit id for the yoyo.log and yoyo.sum files
		yoyo_log_id = -1
		yoyo_sum_id = -1

		# Write the files that are in the current variant directory to the database and storage.
		if rc > 0:
			log.out("Import Files....", DEBUG, v=5)
			for item in os.listdir(args["full_root"]):
				file_name = os.path.join(args["full_root"], item)
				if os.path.isfile(file_name):
					if item == "yoyo.log":
						rc  = report.add_attachment("yoyo_log", file_name)

						if rc > 0:
							yoyo_log_id = rc
					elif item == "yoyo.sum":
						rc = report.add_attachment("yoyo_sum",  file_name)
						if rc > 0:
							yoyo_sum_id = rc
					elif item == "image.txt":
						rc = report.add_attachment("image_build",  file_name)
					elif item == "site.exp":
						rc = report.add_attachment("site", file_name)
					elif item == "yoyo.pid":
						report.add_attachment("pid", file_name)
					elif item.find(".build") != -1:
						rc = report.add_attachment("build", file_name)
					elif item.find(".sym") != -1:
						rc = report.add_attachment("symbol", file_name)
					elif item.find("kdump.elf.gz") != -1:
						rc = report.add_attachment("kdump_raw", file_name)
					else:
						result = kdump_regex.search(item)
						if result:
							rc = report.add_attachment("kdump",  file_name)
						else:
							result = kdump_index_regex.search(item)
							if result:
								rc = report.add_attachment("kdump_index", file_name)
				if rc < 0:
					print "Attachments Failed!!!!!!!!!!!!!!!!!"
					break



		if yoyo_log_id <= 0:
			log.out("yoyo.log database id was less then zero", ERROR)
			rc = -1

		if yoyo_sum_id <= 0:
			log.out("yoyo.sum database id was less then zero", ERROR)
			rc = -1

		# Now we need to write the actual test results to the database.
		# Then we should right any line markers for intersting lines in the yoyo.log
		if rc > 0:
			log.out("Import Sum and Log Info Data ....", DEBUG, v=5)

			# Go over all the tests that are in the submit test list.
			for test in submit_dict["tests"]:
				test_root_id  = -1
				test_exec_id = -1
				exec_time = None
				extra_time = None

				log.out("\tImport %s - %s %s ...." % (test["test_suite"], os.path.join(test["test_path"], test["test_name"]), test["test_params"]), DEBUG, v=5)

				# First we need to get a Test id to assocaite all this data too.

				# So start out by making sure the current test revision is in the database.
				rc = report.add_test_revision(test["test_path"], test["test_name"],  test["test_params"], revision_string=test["revision"])

				if rc > 0:
					# The test result should be stored in the sum file parsed line so get to that by:
					if test["sum_index"] > 0:

						sum_index = test["sum_index"]
						sum_line = sum_results["parsed_lines"][sum_index]

						test_result = sum_line["matches"]["testpnt"][:-2]

						# Check to make sure this test root has been added.
						# keep the test root id as we may need it later when looking for known crashes of a test.
						test_root_id = report.add_test_root(test["test_path"], test["test_name"],  test["test_params"])

						if test_root_id > 0:
							test_exec_id = report.add_test_exec(test_result.lower(), test["test_suite"], test["test_path"], test["test_name"],  test["test_params"], revision_string=test["revision"], exec_time=test["exec_time"], extra_time=test["download_time"], mem_before=test["mem_before"], mem_after=test["mem_after"])

					else:
						log.out("sum index was unexpectedly not greater then 0", ERROR)


				if test_exec_id > 0:

					# Write out the position of this tests final result in the yoyo.sum file.
					sum_index = test["sum_index"]
					sum_line = sum_results["parsed_lines"][sum_index]
					rc = report.add_line_marker(yoyo_sum_id, "yoyo_sum", sum_line["start"], end_line=sum_line["end"], test_exec_id=test_exec_id, sub_type=test["sub_type"])

					if rc > 0:
						# Write out the entire test range
						rc = report.add_line_marker(yoyo_log_id, "full_test", test["log_start"], end_line=test["log_end"], test_exec_id=test_exec_id, sub_type=test["sub_type"])

					if rc > 0:
						# Look at the log_parse_line_indexes and write key information to the file.
						for parsed_log_index in test["log_parse_line_indexes"]:
							log_regex = log_results["parsed_lines"][parsed_log_index]


							if log_regex["type"] == "TestPoint":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)

								if log_regex["final_flag"]:
									rc = report.add_line_marker(yoyo_log_id, "yoyo_log", log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id, sub_type=log_regex["sub_type"])
								else:

									if args["line_marker_level"] >= 1:
										if (log_regex["matches"]["testpnt"] != "NOTE: ") and (log_regex["matches"]["testpnt"] != "START: ") and (log_regex["matches"]["testpnt"] != "STOP: "):
											line_type = log_regex["matches"]["testpnt"][:-2].lower()
											rc = report.add_line_marker(yoyo_log_id, "test_point", log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id, sub_type=line_type)

									elif args["line_marker_level"] >= 2:
										if (log_regex["matches"]["testpnt"] != "NOTE: "):
											line_type = log_regex["matches"]["testpnt"][:-2].lower()
											rc = report.add_line_marker(yoyo_log_id, "test_point", log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id, sub_type=line_type)

									elif args["line_marker_level"] >= 3:
											line_type = log_regex["matches"]["testpnt"][:-2].lower()
											rc = report.add_line_marker(yoyo_log_id, "test_point", log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id, sub_type=line_type)
									else:
										# Don't import any test point lines except for the final
										pass


							elif log_regex["type"] == "process_seg":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=1)

								# add the process seg line marker...
								line_marker_id = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id, sub_type=log_regex["matches"]["type"].lower())

								if line_marker_id > 0:
									crash_known_id = None;

									# Get the known crashes for this test and this crash type.
									known_crashes_rows = report.get_known_crashes_for_test(test_root_id, log_regex["matches"]["type"].lower())

									if known_crashes_rows:
										if isinstance(known_crashes_rows, list):
											# Read from the log file the data we are interested in
											with open(os.path.join(variant, "yoyo.log"),"Ur") as fp_in:
												# Load the lines without the new lines
												lines = fp_in.read().splitlines()

												count = 0
												max_lines = len(lines)

												# We want some lines before and after the crash part.. in order to match against..
												for line_index in range(log_regex["end"], max_lines):

													if len(lines[line_index]) > 1:
														count = count + 1

													# check to see if we have gone ahead ten lines
													if count >= 2:
														break

												lines = lines[:line_index + 1]

												count = 0
												for line_index in range(log_regex["start"], 0, -1):
													if len(lines[line_index]) > 1:
														count = count + 1
													if count >= 2:
														break

												lines = lines[line_index:]

												# Removing any white space from the start or end of the lines
												# Remove any empty lines
												temp_lines = []
												for line in lines:
													line = line.strip()
													if len(line) > 0:
														temp_lines.append(line)

												lines = temp_lines

												max_lines = len(lines)

												text_block = "".join(lines)

											#	print "="*80
											#	print "\n".join(lines)
											#	print "="*80

												# compare lines to known crashes
												for known_crash_row in known_crashes_rows:
													pattern_id = known_crash_row[0]
													pattern = str(known_crash_row[1])

													#print "-" * 80
													#print pattern
													#print "-" * 80

													# Index 1 should be the regex string pattern, index 0 should be the table id for the pattern.
													# We want to remove new_lines from the pattern
													regex_pattern_lines = pattern.splitlines()

													# remove any extra preceeding and endind white space from each line
													# remove any empty lines.
													temp_lines = []
													for line in regex_pattern_lines:
														line = line.strip()
														if len(line) > 0:
															temp_lines.append(line)

													regex_pattern_lines = temp_lines

													# Compile the regex pattern
													regex = re.compile("".join(regex_pattern_lines))

													#print "*"*80
													#print "".join(regex_pattern_lines)
													#print "=-"*40

													result = regex.search(text_block)

													if result:
														log.out("REGEX PATTERN MATCH FOUND FOR process_seg: " + str(pattern_id), DEBUG, v=25)
														known_crash_id = pattern_id
														break

										else:
											log.out("Get known crashes returned a Non list.", ERROR);

									else:
										log.out("Get known crash returned nothing.", DEBUG, v=25)

									crash_exec_id = report.add_crash_exec(line_marker_id, log_regex["matches"]["type"].lower(), crash_known_id)

									rc = crash_exec_id
								else:
									rc = line_marker_id
							elif log_regex["type"] == "download":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								if args["line_marker_level"] >= 1:
									rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "kermit_send":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								if args["line_marker_level"] >=2:
									rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "execute":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)

								if args["line_marker_level"] >=2:
									rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "exec":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								if args["line_marker_level"] >=1:
									rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "mem_proc":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "mem_proc":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "metric":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

								if rc > 0:
									log_regex = log_results["parsed_lines"][parsed_log_index]
									rc = report.add_test_metric(rc, log_regex["matches"]["value"], log_regex["matches"]["units"], log_regex["matches"]["desc"])

							elif log_regex["type"] == "bug_ref":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)

								log_regex["matches"]["bug_type"] = log_regex["matches"]["bug_type"].lower()
								if log_regex["matches"]["bug_type"] == "jira":
									log_regex["matches"]["bug_type"] = "ji"

								# Make sure that the bug root exists
								rc = report.add_bug_root(log_regex["matches"]["bug_type"], log_regex["matches"]["value"])

								# Make sure the project bug is added
								if rc > 0:
									rc = report.add_project_bug(log_regex["matches"]["bug_type"], log_regex["matches"]["value"])

								# Now track where it was seen within the log file.
								if rc > 0:
									rc = report.add_line_marker(yoyo_log_id, "bug_ref", log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

								# track that the bug occured during this execution and use the log marker above.
								if rc > 0:
									rc = report.add_bug_exec(rc, log_regex["matches"]["bug_type"], log_regex["matches"]["value"])
							elif log_regex["type"] == "kdump":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=1)

								# add the kdump line marker...
								line_marker_id = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

								if line_marker_id > 0:
									crash_exec_id = report.add_crash_exec(line_marker_id, log_regex["type"], None)

									if crash_exec_id > 0:
										kdump_file_name = "kdump."+str(log_regex["matches"]["index"])
										full_attached_path = os.path.join(variant, kdump_file_name)

										# get the attachment id for this index file.
										kdump_index_id = report.get_attachment_id(full_attached_path)

										if kdump_index_id > 0:
											# Open the local kdump index file
												with open(full_attached_path,"Ur") as fp_in:
													# read in with new lines
													lines = fp_in.readlines()

												kdump_line_index = 0
												max_lines = len(lines)
												shutdown_found_line_index  = -1

												for kdump_line_index in range(0, len(lines)):
													# scan for the shutdown message
													if lines[kdump_line_index].find("Shutdown[") != -1:
														shutdown_found_line_index = kdump_line_index
														break

												if shutdown_found_line_index != -1:
													shutdown_line_marker_id = report.add_line_marker(kdump_index_id, 'shutdown', shutdown_found_line_index, end_line=max_lines, test_exec_id=test_exec_id)

													if shutdown_line_marker_id > 0:

														log.out("TODO: Compare the shutdown and GDB stuff to known crash patterns and update if this is known", EXCEPTION)



														shutdown_crash_exec_id = report.add_crash_exec(shutdown_line_marker_id, 'shutdown', None)
														if shutdown_crash_exec_id > 0:
															pass



														else:
															rc = shutdown_crash_exec_id
													else:
														rc = shutdown_line_marker_id
										else:
											log.out("Failed to find attachment id for kdump." + str(log_regex["matches"]["index"]), ERROR)
									else:
										rc = crash_exec_id
								else:
									rc = line_marker_id

							elif log_regex["type"] == "shutdown":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=1)
								line_marker_id = report.add_line_marker(yoyo_log_id, log_regex["type"],  log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

								if line_marker_id > 0:

									log.out("TODO: Compare the shutdown known crash patterns and update if this is known", EXCEPTION);

									crash_exec_id = report.add_crash_exec(line_marker_id, log_regex["matches"]["type"].lower(), None)
									if crash_exec_id:

										pass




									else:
										rc = crash_exec_id
								else:
									rc = line_marker_id

							elif log_regex["type"] == "kernel_start":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=1)
								line_marker_id = report.add_line_marker(yoyo_log_id, log_regex["type"],  log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)


								if line_marker_id > 0:
									crash_exec_id = report.add_crash_exec(line_marker_id,log_regex["type"], None)
									if crash_exec_id:
										pass
									else:
										rc = crash_exec_id
								else:
									rc = line_marker_id

							elif log_regex["type"] == "assertion_failure":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "buffer_overflow":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "memory_fault":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "malloc_check_fail":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "reboot":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "exec_format_error":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "ldd_fault":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "send-class":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "to_man_retries":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							elif log_regex["type"] == "stack_smashing":
								log.out("++++++++++++++++++++++++++++++++ " + str(log_regex["type"]) + " ++++++++++++++++++++++++++++++++", DEBUG, v=25)
								rc = report.add_line_marker(yoyo_log_id, log_regex["type"], log_regex["start"], end_line=log_regex["end"], test_exec_id=test_exec_id)

							else:
								log.out("-------------------------------- " + str(log_regex["type"]) + " --------------------------------", DEBUG, v=1)

							if rc <= 0:
								log.out("An error (" + str(rc) +") occurred while processing " + log_regex["type"] + " exiting the line marker loop" , ERROR)
								break
				else:
					rc = -1

				if rc <= 0:
					if test["test_params"]:
						log.out("An error (" + str(rc) +") occurred while processing " + test["test_path"] + "/" + test["test_name"] + " " + test["test_params"] + " exiting the test processing loop" , ERROR)
					else:
						log.out("An error (" + str(rc) +") occurred while processing " + test["test_path"] + "/" + test["test_name"]+ " exiting the test processing loop" , ERROR)
					break


		args["reporter"].commit()
		args["reporter"].close_connection()

	# print rc, "=" * 80


def process_variants(args, log, fp, recovery_data):

	line_regex = {}

	line_regex["download"] = re.compile('<QADEBUG>Generic\s+Download\s+(?P<mode>Start|Stop)\s+on\s+<TS>\s*(?P<date>.+)\s*</TS\>\s*<BS>(?P<test_path>.+)\s*</BS></QADEBUG>')

	line_regex["execute"] = re.compile('<QADEBUG>Generic\s+Execute\s+(?P<mode>Start|Stop)\s+on\s+<TS>\s*(?P<date>.+)\s*</TS\>\s*<BS>(?P<test_path>.+)\s*</BS></QADEBUG>')

	line_regex["reboot"] = re.compile('Verbose\s+(?P<time>\d+:\d+:\d+)\s+\{\s+rebooting\s+target:\s+(?P<try>\d+)/(?P<of_tries>\d+)\s+\}')

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

	line_regex["metric"] = re.compile('METRIC: (?P<desc>.+)\sVALUE:\s(?P<value>.+)\sUNITS:\s(?P<units>.+)$')

	line_regex["bug_ref"] = re.compile('(?P<testpnt>PASSX|FAILX|POINT).*(.+\.[a-zA-Z0-9]{1,4}:\d+)*\s*(?P<bug_type>jira|JIRA|JI|PR|ji|pr)[_|:]*\s*(?P<value>\d{5,10})')

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

		args["full_root"] = root

		if len(relative_root) > 0:
			if relative_root[0] == "/":
				relative_root = relative_root[1:]

		if "!!!_general.json" in files:
			with open(os.path.join(root, "!!!_general.json"), "r") as fp_general:
				args["general_file_info"] = json.loads(fp_general.read())

		if "yoyo.sum" in files:
			log.out(root + " yoyo.sum", DEBUG, v=3)
			completed_string = root + " " + "yoyo.sum import completed"
			if completed_string not in recovery_data:
				data[relative_root] = {}
				data[relative_root]["SUM"] = process_yoyo_sum(args, log, root, line_regex)

				if len(data[relative_root]["SUM"]) <= 0:
					log.out("yoyo.sum file did not return any results.", ERROR)
					return False
				else:
					pass
					#print_list(log, data[relative_root]["SUM"], "SUM> ")

		if "yoyo.log" in files:
			log.out(root + " yoyo.log", DEBUG, v=3)
			completed_string = root + " " + "yoyo.log import completed"
			if completed_string not in recovery_data:
				data[relative_root]["LOG"] = process_yoyo_log(args, log, root, line_regex, data[relative_root]["SUM"])


				if data[relative_root]["LOG"]:
					if "SUM" in data[relative_root]:
						if process_tests(args, log, data[relative_root]["SUM"], data[relative_root]["LOG"], root) > 0:
							fp.write(root + " " + "yoyo.sum import completed\n")
							fp.write(root + " " + "yoyo.log import completed\n")
				else:
					log.out("yoyo.log file did not return any results.", ERROR)
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
	parser.add_argument('-line_marker_level', '--line_marker_level', default=0,
						help='')

	parser.add_argument('-set_storage_path', '--set_storage_path',
						default="/media/BackUp/regression_data/logs",
						help='')

	parser.add_argument('-gdb_tools_path', '--gdb_tools_path',
						help='')

	parser.add_argument('-schema', '--schema',
						help='',
						default='project_db')

	parser.add_argument('-exec_id', '--exec_id',
						help='',
						default=-1)

	parser.add_argument('-exec_type', '--exec_type',
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

	args["reporter"] = TestReporter(args["mysql_host"],  args["mysql_user_name"], args["mysql_password"], args["schema"])

	log = args["reporter"].get_log()

	log.set_verbosity(DEBUG, args["verbosity"])

	str_buffer = "Input Parameters\n"

	log.out(str_buffer + ("=" * (len(str_buffer)-1)) + "\n" + pformat(args), DEBUG, v=1)

	if args["reporter"]:

		if args["add_project"]:
			if add_project(args, log):
				pass
			else:
				return -1

		if args["input"]:

			if args["exec_type"] is None:
				log.out("exec_type command line parameter is required when input is specified.")
				return -1

			if args["exec_type"] not in valid_execution_types:
				log.out(args["exec_type"] + " is not a valid execution type. Please choose: " + ",".join(valid_execution_types))
				return -1

			if args["project"] is None:
				log.out("project command line parameter is required when input is specified.")
				return -1

			if args["child"] is None:
				log.out("project command line parameter is required when input is specified.")
				return -1

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
