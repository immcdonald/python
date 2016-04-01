import os, sys
import argparse
import gzip
from pprint import pformat
import user
import json
import glob
import subprocess
import shutil


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
			found_regress_data = False
			exec_path = os.path.join(project_path, "%0.9d" % exec_id[0])

			if os.path.exists(exec_path) == False:
				# Create the project directory
				os.makedirs(exec_path)

			partial_regress_data_path = os.path.join(args["source"], "new_db_%d_*.tar.gz" % exec_id[0])

			glob_match = glob.glob(partial_regress_data_path)

			if len(glob_match) == 0:
				found_regress_data = False
			elif len(glob_match) == 1:
				found_regress_data  = True
				cmd = ["tar", "xf", glob_match[0], "--strip=1", "-C", os.path.abspath(exec_path)]
				handle = subprocess.Popen(cmd);
				handle.wait()

				yoyo_path = os.path.join(exec_path,"yoyo.suite/build")
				if os.path.exists(yoyo_path):
					for root, dirs, files in os.walk(yoyo_path):

						if len(files) > 0:
							relative_path =  os.path.relpath(root, yoyo_path)

							test_path = os.path.join(exec_path, relative_path)
							if os.path.exists(test_path):
								for file_name in files:
									shutil.move(os.path.join(root, file_name), os.path.join(test_path, file_name))

					shutil.rmtree(os.path.join(exec_path,"yoyo.suite"))

			else:
				raise Exception("Error: regression data archive search on (" + str(partial_regress_data_path) +  ") return: %s" % pformat(glob_match))

			table = "sources"
			fields = ["exec_id"]
			data = [exec_id[0]]

			get_list = ["type", "src_desc", "url", "unique_id"]

			source_info = args["sql"].select(get_list, table, fields, data)

			if len(source_info) > 0:
				general_info_path = os.path.join(exec_path, "!!!_general")

				with open(general_info_path + ".json", "w") as fp_out_json:
					with open(general_info_path + ".ini", "w") as fp_out_text:
						fp_out_text.write("[Information]\n")
						fp_out_text.write("id: %d\n" %  exec_id[0])
						fp_out_text.write("description: %s\n" %  exec_id[3])
						fp_out_text.write("user_name: %s\n" %  exec_id[1])
						fp_out_text.write("created: %s\n" %  exec_id[2])
						fp_out_text.write("sources: %d\n" % len(source_info))

						json_data = {}

						json_data["user_name"] = exec_id[1]
						json_data["date"] = str(exec_id[2])
						json_data["description"] = exec_id[3]
						json_data["sources"] = []

						counter = 0
						for source in source_info:
							fp_out_text.write("\n[Source_%d]\n" %  counter)
							counter = counter + 1
							fp_out_text.write("type: %s\n" %  source[0])
							fp_out_text.write("src_desc: %s\n" %  source[1])
							fp_out_text.write("url: %s\n" %  source[2])
							fp_out_text.write("unique_id: %s\n" %  source[2])

							source_data = {}
							source_data["type"] = source[0]
							source_data["src_desc"] = source[1]
							source_data["url"] = source[2]
							source_data["unique_id"] = source[3]

							json_data["sources"].append(source_data)

						fp_out_json.write(json.dumps(json_data))



def main(argv=None):

	if argv is None:
		# If argv is not passed then use the system args
		# Remove the first element in the list because
		# that is the execution name which we don't care about.
		argv = sys.argv[1:]


	parser = argparse.ArgumentParser(description='Regress tree data builder')
	parser.add_argument('-d', '--destination', help='', default="./local/")
	parser.add_argument('-s', '--source', help='', required=True)

	args = vars(parser.parse_args())
	args["sql"] = My_SQL(user.sql_host, user.sql_user_name, user.sql_password, "qa_db")

	if args["sql"]:
		if args["sql"].connect():
			build_tree(args)


if __name__ == "__main__":
	sys.exit(main())

