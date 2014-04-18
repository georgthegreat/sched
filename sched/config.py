import configparser
import os

from . import errors

class SchedulerConfig(object):
	def __init__(self, params):
		reschedule_attempts = params.get("reschedule_attempts", None)
		if reschedule_attempts is None:
			raise errors.ConfigError("reschedule_attempts param wasn't found")
		self.reschedule_attempts = int(reschedule_attempts)
		
		reschedule_smart = params.get("reschedule_smart", None)
		if reschedule_smart is None:
			raise error.ConfigError("reschedule_smart param wasn't found")
		self.reschedule_smart = (reschedule_smart == "yes")
	

class Config(object):
	def __init__(self, path):
		config = configparser.ConfigParser(interpolation=None)
		config.read(path)
		
		self.scheduler = SchedulerConfig(config["SCHEDULER"])
		
config = Config(os.environ["CONFIG"])
