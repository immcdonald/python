import os, sys
import argparse
import gzip
from pprint import pformat
import user
import json


parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *
from my_ftp import *


def build_tree(args):
	table = "project"
	get_list = ["id", "name"]
	fields = None
	data = None

	projects = args["sql"].select(get_list, table, fields, data)

	for project in projects:
		project_path = os.path.join(args["destination"], project[1].capitalize())

		if os.path.exists(project_path) == False:
			# Create the project directory
			os.makedirs(project_path)

		table = "exec_tracker"
		get_list = ["id", "user_name", "created", "description"];

		fields = ["project_id"]
		data = [project[0]]

		exec_ids = args["sql"].select(get_list, table, fields, data)


		for exec_id in exec_ids:
			exec_path = os.path.join(project_path, "%0.9d" % exec_id[0])

			if os.path.exists(exec_path) == False:
				# Create the project directory
				os.makedirs(exec_path)

			table = "sources"
			fields = ["exec_id"]
			data = [exec_id[0]]

			get_list = ["type", "src_desc", "url", "unique_id"]

			source_info = args["sql"].select(get_list, table, fields, data)

			if len(source_info) > 0:
				general_info_path = os.path.join(exec_path, "!!!_general")

				with open(general_info_path + ".json", "w") as fp_out_json:
					with open(general_info_path + ".txt", "w") as fp_out_text:
						json_data = {}

						json_data["user_name"] = exec_id[1]
						json_data["date"] = str(exec_id[2])
						json_data["description"] = exec_id[3]
						json_data["sources"] = []
						for source in source_info:
							temp = {}
							temp[]






						fp_out_json.write(json.dumps(json_data))











def main(argv=None):

	if argv is None:
		# If argv is not passed then use the system args
		# Remove the first element in the list because
		# that is the execution name which we don't care about.
		argv = sys.argv[1:]


	parser = argparse.ArgumentParser(description='Regress tree data builder')
	parser.add_argument('-d', '--destination', help='', default="./local/")
	parser.add_argument('-s', '--source', help='')

	args = vars(parser.parse_args())
	args["sql"] = My_SQL(user.sql_host, user.sql_user_name, user.sql_password, "qa_db")

	if args["sql"]:
		if args["sql"].connect():
			build_tree(args)


if __name__ == "__main__":
	sys.exit(main())

