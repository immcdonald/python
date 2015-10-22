import os
import logging
from datetime import datetime 
from pprint import pformat
from inspect import currentframe, getframeinfo

INFO="INFO"
DEBUG="DEBUG"
WARNING="WARNING"
ERROR="ERROR"
EXCEPTION="EXCEPTION"
logging.basicConfig(level=logging.INFO, format='%(message)s');
ALL_MASK = 0xFFFFFFFF
DEFAULT_DATETIME_FORMAT = '%Y%m%d%H%M%S%Z'

class my_log():	
	def __init__(self, verbosity=0, mask=ALL_MASK, mode_list=[DEBUG, WARNING, INFO, ERROR, EXCEPTION], std=INFO):

		if EXCEPTION not in mode_list:
			mode_list.append(EXCEPTION)

		if type(mode_list) != list:
			raise Exception('mode_list is not of type list')
		self.std = std
		self.mask = mask
		self.modes = {}

		for mode in mode_list:
			if mode not in self.modes:

				if mode == std:
					self.modes[mode] = {"enable": True,
										"verbosity":verbosity, 
										"show_mode": False, 
										"show_file": False, 
										"show_line": False, 
										"show_time": None}

				elif mode == EXCEPTION:
					self.modes[mode] = {"enable": True,
										"verbosity": 0, 
										"show_mode": False, 
										"show_file": True, 
										"show_line": True, 
										"show_time": DEFAULT_DATETIME_FORMAT}
				
				elif mode == ERROR:
					self.modes[mode] = {"enable": True,
										"verbosity": 0, 
										"show_mode": True, 
										"show_file": True, 
										"show_line": True, 
										"show_time": DEFAULT_DATETIME_FORMAT}
				else:
					self.modes[mode] = {"enable": False,
										"verbosity":verbosity, 
										"show_mode": False, 
										"show_file": False, 
										"show_line": False, 
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

	def set_mode(self, mode, enable=True):
		if (enable is True) or (enable is False):
			if mode in self.modes:
				self.modes[mode]["enable"] = enable
			else:
				raise Exception(enable + ' is not a value value. Should be True or False')
		else:
			raise Exception(mode + ' is an unknown mode')	

	def set_show_mode(self, mode, enable=True):
		if (enable is True) or (enable is False):
			if mode in self.modes:
				self.modes[mode]["show_mode"] = enable
			else:
				raise Exception(enable + ' is not a value value. Should be True or False')
		else:
			raise Exception(mode + ' is an unknown mode')	
	

	def set_show_file(self, mode, enable=True):
		if (enable is True) or (enable is False):
			if mode in self.modes:
				self.modes[mode]["show_file"] = enable
			else:
				raise Exception(enable + ' is not a value value. Should be True or False')
		else:
			raise Exception(mode + ' is an unknown mode')	
	
	def set_show_line_number(self, mode, enable=True):
		if (enable is True) or (enable is False):
			if mode in self.modes:
				self.modes[mode]["show_line"] = enable
			else:
				raise Exception(enable + ' is not a value value. Should be True or False')
		else:
			raise Exception(mode + ' is an unknown mode')	


	def out(self, msg, mode=None, verbosity=0, mask=ALL_MASK,frameinfo=getframeinfo(currentframe()), suppress=False):
		
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
							if self.modes[mode]["show_file"] is not False:
								if prefixed:
									output = output + ":"	
								output = output + os.path.basename(frameinfo.filename)
								prefixed = True

							# Should we prefix the line number
							if self.modes[mode]["show_line"] is not False:
								if prefixed:
									output = output + ":"
								output = output + str(frameinfo.lineno)
								prefixed = True

							if self.modes[mode]["show_mode"] is not False:
								if prefixed:
									output = output + ":"
								output = output + str(mode)
								prefixed = True

							if prefixed:
								output = output + ": "

						if mode != EXCEPTION:
							logging.info(output+msg)
						else:
							raise Exception(output+msg)
		else:
			raise Exception(mode + ' is an unknown mode')
