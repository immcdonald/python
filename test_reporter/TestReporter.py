import os, sys
import argparse
parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *

class TestReporter(My_SQL):

	def create_project_table(self, ine="IF NOT EXISTS"):
		query = "CREATE TABLE " + ine + " `project` ("\
				"`id` int(11) NOT NULL AUTO_INCREMENT,"\
 				"`name` varchar(60) NOT NULL,"\
				"`comment` text,"\
				"`created` datetime NOT NULL,"\
				"PRIMARY KEY (`id`),"\
				"UNIQUE KEY `name_UNIQUE` (`name`)"\
				") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
		return self.query(query)

	def setup_database(self, db_name=None):
		data_bases = self.list_databases()

		if data_bases is not None:
			rc = True

			if db_name not in data_bases:
				rc = self.create_db(db_name)

			if rc:
				rc = self.select_db(db_name)

			if rc:
				rc = self.create_project_table();

			return rc
		else:
			return False


dog = TestReporter("serenity.bts.rim.net", <user_name>, <password>);

dog.connect()
print dog.setup_database("fred")

#dog.create_db("fred")
#dog.select_db("fred")
#dog.query(" CREATE TABLE MyGuests (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,firstname VARCHAR(30) NOT NULL,lastname VARCHAR(30) NOT NULL, email VARCHAR(50),reg_date TIMESTAMP)");

