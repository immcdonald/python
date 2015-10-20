import os, sys
parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from log import *



def main():
	ian = log()
	ian.set_verbosity(INFO, 0)
	ian.set_verbosity(DEBUG, 10)
	ian.set_datetime_fmt(INFO)
	ian.log("Hi", INFO)


main()
