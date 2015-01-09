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
			raise errors.ConfigError("reschedule_smart param wasn't found")
		self.reschedule_smart = (reschedule_smart == "yes")


class LoadLevelerConfig(object):
	def __init__(self, params):
		external_resource_weight = params.get("external_resource_weight", None)
		if external_resource_weight is None:
			raise errors.ConfigError("external_resource_weight param wasn't found")
		self.external_resource_weight = float(external_resource_weight)

		internal_resource_weight = params.get("external_resource_weight", None)
		if internal_resource_weight is None:
			raise errors.ConfigError("internal_resource_weight param wasn't found")
		self.internal_resource_weight = float(internal_resource_weight)

		partition_size = params.get("partition_size", None)
		if partition_size is None:
			raise errors.ConfigError("partition_size param wasn't found")
		self.partition_size = int(partition_size)


class Config(object):
	def __init__(self, path):
		config = configparser.ConfigParser(interpolation=None)
		config.read(path)

		self.scheduler = SchedulerConfig(config["SCHEDULER"])
		self.loadleveler = LoadLevelerConfig(config["LOADLEVELER"])

config = Config(os.environ["CONFIG"])
