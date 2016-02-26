import re
from pprint import pformat

test_exec_pattern = re.compile('^/tmp/(?P<test_name>[a-zA-Z0-9\-\_]+)\s*(?P<params>.*)');
metric_pattern = re.compile('^METRIC: (?P<desc>.+)\sVALUE:\s(?P<value>.+)\sUNITS:\s(?P<units>.+)$')

src_path = "yoyo.log"

metric_data_tests = {}

test_data = None

with open(src_path, "Ur") as fp_in:
	lines = fp_in.readlines()

	for line in lines:
		line = line.strip()

		if len(line) > 2:
			if line[0] == '#':
				line = line[1:].strip()

		if len(line) == 0:
			continue

		result = test_exec_pattern.search(line)

		if result:
			test_data = result.groupdict()
		else:
			result = metric_pattern.search(line)

			if result:
				data = result.groupdict()

				test_key = test_data["test_name"] + "; " + test_data["params"]

				if test_key not in metric_data_tests:
					metric_data_tests[test_key] = {}

				metric_data_tests[test_key][data["desc"]]={}
				metric_data_tests[test_key][data["desc"]]["value"] = data["value"]
				metric_data_tests[test_key][data["desc"]]["units"] = data["units"]

			else:
				print line

for metric_data_test_key in sorted(metric_data_tests):
	for description in sorted(metric_data_tests[metric_data_test_key]):
			print metric_data_test_key + "; " + description + "; " + metric_data_tests[metric_data_test_key][description]["value"] + "; " + metric_data_tests[metric_data_test_key][description]["units"]

