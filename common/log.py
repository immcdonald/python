import os
import logging
from datetime import datetime 
from pprint import pformat
from inspect import currentframe, getframeinfo

INFO="INFO"
DEBUG="DEBUG"
WARNING="WARNING"
ERROR="ERROR"

logging.basicConfig(level=logging.INFO, format='%(message)s');

class my_logger():	
	ALL_MASK = 0xFFFFFFFF
	DEFAULT_DATETIME_FORMAT = '%Y%m%d%H%M%S%Z'

	def __init__(self, verbosity=0, mask=ALL_MASK, mode_list=[DEBUG, WARNING, INFO, ERROR], std=INFO):
		EXCEPTION="EXCEPTION"

		if EXCEPTION not in mode_list:
			mode_list.append(EXCEPTION)

		if type(mode_list) != list:
			raise Exception('mode_list is not of type list')
		self.std = std
		self.mask = mask
		self.modes = {}

		for mode in mode_list:
			if mode not in self.modes: 
				self.modes[mode] = {"enable": True,
									"verbosity":verbosity, 
				                    "show_mode": True, 
				                    "show_file": True, 
				                    "show_line": True, 
				                    "show_time": None}
			else:
				raise Exception(mode + ' is already in the list.')

	def set_verbosity(self, mode, level):
		if mode in self.modes:
			self.modes[mode]["verbosity"] = level
		else:
			raise Exception(mode + ' is an unknown mode')


	def set_datetime_fmt(self, mode, format=DEFAULT_DATETIME_FORMAT):
		if mode in self.modes:
			self.modes[mode]["show_time"] = format
		else:
			raise Exception(mode + ' is an unknown mode')

	def log(self, msg, mode=None, verbosity=0, mask=ALL_MASK,frameinfo=getframeinfo(currentframe()), suppress=False):
		
		if mode is None:
			mode = self.std

		if mode in self.modes:
			if self.modes[mode]["enable"]:
				if (verbosity >= self.modes[mode]["verbosity"]):
					if (self.mask & mask):
						
						output = "";
						if suppress is False:
							prefixed = False

							# Should we prefix the time?
							if self.modes[mode]["show_time"] is not None:
								current = datetime.now()
								output = output + current.strftime(self.modes[mode]["show_time"])
								prefixed = True

							# Should we prefix the file 
							if self.modes[mode]["show_file"] is not None:
								if prefixed:
									output = output + ":"	
								output = output + os.path.basename(frameinfo.filename)
								prefixed = True

							# Should we prefix the line number
							if self.modes[mode]["show_line"] is not None:
								if prefixed:
									output = output + ":"
								output = output + str(frameinfo.lineno)
								prefixed = True

							if self.modes[mode]["show_mode"] is not None:
								if prefixed:
									output = output + ":"
								output = output + str(mode)
								prefixed = True

							if prefixed:
								output = output + ": "

						logging.info(output+msg)
		else:
			raise Exception(mode + ' is an unknown mode')


ian = my_logger()
ian.set_verbosity(INFO, 0)
ian.set_verbosity(DEBUG, 10)
ian.set_datetime_fmt(INFO)

ian.log("Hi", INFO)