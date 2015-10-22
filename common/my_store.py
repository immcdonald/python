from my_log import *

class my_store():
	def __init__(self, log=None):
		self.store = {}
		if log is None:
			self.log = my_log()
		else:
			self.log = log

	def add_store(self, name, value, value_type=None, override=False):
		if value_type is not None:
			if override is False:
				if type(value) != value_type:
					self.log.out("Value (%s) does not match the type (%s)" % (value, value_type), ERROR)
					return False

		if name not in self.store:
			self.store[name]={}
			self.store[name]["value_type"] = value_type
			self.store[name]["value"] = value				
		else:
			self.log.out("The name (%s) already exists." % name, ERROR)
			return False
		return True

	def delete_store(self, name):
		if name in self.store:
			self.store.pop(name)
		else:
			self.log.out("The name (%s) was not found" % name, EXCEPTION)
			return None

	def get_value(self, name):
		if name in self.store:
			return self.store[name]["value"];
		else:
			self.log.out("The name (%s) was not found" % name, EXCEPTION)
			return None
	
	def get_type(self, name):
		if name in self.store:
			return self.store[name]["value_type"];
		else:
			self.log.out("The name (%s) was not found" % name, EXCEPTION)
			return None

	def update_store(self, name, value, value_type=None, override=False):
		if value_type is not None:
			if override is False:
				if type(value) != value_type:
					self.log.out("Value (%s) does not match the type (%s)" % (value, value_type), ERROR)
					return False
		if name in self.store:
			self.store[name]={}
			self.store[name]["value_type"] = value_type
			self.store[name]["value"] = value				
		else:
			self.log.out("The name (%s) was not found" % name, EXCEPTION)
			return False
		return True