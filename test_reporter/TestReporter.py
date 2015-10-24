import os, sys
import argparse
parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_sql import *

class TestReporter(My_SQL):
	def junk(self):
		pass

dog = TestReporter("serenity.bts.rim.net", "root", "root");

dog.connect()
print dog.list_tables("qa_db")

#dog.create_db("fred")
#dog.select_db("fred")
#dog.query(" CREATE TABLE MyGuests (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,firstname VARCHAR(30) NOT NULL,lastname VARCHAR(30) NOT NULL, email VARCHAR(50),reg_date TIMESTAMP)");
