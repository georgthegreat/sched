import glob
import os
import re

from . import errors
from . import dataset

ARG_REGEXP = re.compile("^(\$|#)" + dataset.DATASET_ID_PATTERN + "$")
SIMPLE_ARG_REGEXP = re.compile("^\$" + dataset.DATASET_ID_PATTERN + "$")
DIVISIBLE_ARG_REGEXP = re.compile("^#" + dataset.DATASET_ID_PATTERN + "$")

class AbstractCommand(object):
	"""
	Class representing single executable command.
	Any task contains one or more commands
	(only one of which will be actually executed)
	"""
	def __init__(self, command, inputs, outputs):
		self._command = command
		self._args = self._command.split()
		self._inputs = inputs
		self._outputs = outputs
		self._datasets = self._inputs | self._outputs
		
		if len(self._args) == 0:
			raise errors.ValidationError("Command line can't be empty")
		
		if ARG_REGEXP.match(self._args[0]):
			raise errors.ValidationError("First argument of command [{args}] must be executable, not dataset".format(
				args=self._args.join(" ")
			))

		#validating args to be present in self._datasets
		ids = {
			m.group("id")
			for m in map(ARG_REGEXP.match, self._args)
			if m
		}
		if ids > self._datasets:
			raise errors.ValidatinError("Command [{command}] make use of disallowed datasets {datasets}".format(
				command=self._command,
				datasets=self._datasets - ids
			))
		#validation done
		
	@property
	def type(self):
		return CommandType.Abstract
		
	def eval_args(self, datasets):
		"""
		Returns list containing list of command arguments
		"""
		raise NotImplementedError()
		
	def estimate_args_count(self, datasets):
		"""
		Returns approximate number of processes in this command
		"""
		raise NotImplementedError()
	
	@staticmethod
	def from_xml_node(node, inputs, outputs):
		type = CommandType.from_string(node.attrib["type"])
		command = node.text
		
		return CommandType.type_to_class[type](command, inputs, outputs, **node.attrib)

class LocalCommand(AbstractCommand):
	"""
	Class representing local executable command
	"""	
	
	def __init__(self, command, inputs, outputs, **attrib):
		super().__init__(command, inputs, outputs)
	
	@property
	def type(self):
		return CommandType.Local
	
	def eval_args(self, datasets):
		if len(self._args) == 0:
			raise errors.ValidationError("Got empty command line")
		
		total_args = []
		current_args = []
		
		for arg in self._args:
			match = SIMPLE_ARG_REGEXP.match(arg)
			if match:
				current_args.append(datasets[match.group("id")].path)
			else:
				current_args.append(arg)
		
		total_args.append(current_args)
		return total_args
		
	def estimate_args_count(self, datasets):
		#local command always consist of a single process
		return 1

		
class FileDivisibleCommand(AbstractCommand):

	def __init__(self, command, inputs, outputs, **attrib):
		super().__init__(command, inputs, outputs)
		
		#list of tuples (index, id) of datasets to divide task by
		input_divisors = [
			(index, m.group("id"))
			for (index, m) in enumerate(map(DIVISIBLE_ARG_REGEXP.match, self._args))
			if m and (m.group("id") in self._inputs)
		]
		
		if len(input_divisors) != 1:
			raise errors.ValidationError("Divisible commands should be contain exactly one divisor (got {count} for [{args}]".format(
				count=len(input_divisors),
				args=self._command
			))
			
		self._glob = attrib.get("glob", "*")

		self._divisor_index, self._divisor_id = input_divisors[0]
		
	@property
	def type(self):
		return CommandType.FileDivisible
		
	def eval_args(self, datasets):
		if len(self._args) == 0:
			raise errors.ValidationError("Got empty command line")
		
		dirname = datasets[self._divisor_id].path
		
		total_args = []
		for file in glob.iglob(os.path.join(dirname, self._glob)):
			current_args = []
			for index, arg in enumerate(self._args):
				#fill the command line
				match_simple = SIMPLE_ARG_REGEXP.match(arg)
				match_divisible = DIVISIBLE_ARG_REGEXP.match(arg)
				if index == self._divisor_index:
					current_args.append(file)
				elif match_simple:
					current_args.append(datasets[match_simple.group("id")].path)
				elif match_divisible:
					#divisible arg specified as non-divisor dataset
					#using divisor basename as output filename
					current_args.append(os.path.join(
						datasets[match_divisible.group("id")].path,
						os.path.basename(file)
					))
				else:
					current_args.append(arg)

			total_args.append(current_args)
			
		if len(total_args) == 0:
			raise error.ValidationError("Command [{args}] can't be divideds".format(
				args=self._command
			))
			
		return total_args
			
	def estimate_args_count(self, datasets):
		"""
		Returns number of files in divisor dataset 
		(this is the number of args that will be produced by eval_args)
		"""
		return len(os.listdir(datasets[self._divisor_id].path))
	

#TODO: use enum.Enum in Python-3.4
class CommandType(object):
	Abstract = 0,
	Local = 1,
	FileDivisible = 2

	_dict = {
		"local": Local,
		"file-divisible": FileDivisible
	}
	
	@staticmethod
	def from_string(value):
		result = CommandType._dict.get(value, None)
		if result is None:
			raise errors.XmlParseError("Unknown task type {value}".format(
				value=value
			))
		return result
		
	type_to_class = {
		Local: LocalCommand,
		FileDivisible: FileDivisibleCommand
	}
	
#TODO: use enum.Enum in Python-3.4
class TaskStatus(object):
	Waiting = 0
	Pending = 1
	Enqueued = 2
	Running = 3
	Finished = 4
	Failed = 5


class Task(object):
	"""
	Class representing single workflow task
	"""
	def __init__(self, datasets, id, inputs, outputs, description, stdout, stderr, commands):
		self._datasets = datasets
		
		self._id = id
		self._inputs = inputs
		self._outputs = outputs
		self._description = description
		self._status = TaskStatus.Waiting
		self._datasets = datasets
		
		self._commands = {}
		for command in commands:
			if command.type in self._commands:
				raise errors.ValidationError("Got more than one command with type {type}".format(
					type=command.type
				))
			self._commands[command.type] = command
		
		self._stdout = stdout
		if self._stdout is not None:
			dirname = os.path.dirname(self._stdout)
			if not os.path.isdir(dirname):
				os.makedirs(dirname, exist_ok=True)
		
		self._stderr = stderr
		if self._stderr is not None:
			dirname = os.path.dirname(self._stderr)
			if not os.path.isdir(dirname):
				os.makedirs(dirname, exist_ok=True)
		
		if (len(self._inputs) == 0) and (len(self._outputs) == 0):
			raise errors.ValidationError("Task {id} doesn't have any input or output datasets".format(
				id=self._id
			))
		
		if len(self._commands) == 0:
			raise errors.ValidationError("Task {id} doesn't have any commands defined".format(
				id=self._id
			))
			
		for id in inputs:
			self._datasets[id].add_descendant(self)
		
	
	#class member properties
	@property
	def id(self):
		return self._id
		
	@property
	def stdout(self):
		return self._stdout
	
	@property
	def stderr(self):
		return self._stderr
	
	#status access properties
	@property
	def is_waiting(self):
		return self._status == TaskStatus.Waiting
	
	@property
	def is_pending(self):
		return self._status == TaskStatus.Pending
		
	@property
	def is_finished(self):
		return self._status == TaskStatus.Finished
	
	@property
	def is_failed(self):
		return self._status == TaskStatus.Failed
	
	def update(self, new_status=None):
		"""
		Updates task status. If new_status is None, attempts to autodetect it
		"""
		if new_status is None:
			if self.is_waiting:
				available = lambda dataset_: self._datasets[dataset_].is_available
				
				if all(map(available, self._inputs)):
					self._status = TaskStatus.Pending
		else:
			self._status = new_status
			if self.is_finished:
				for id in self._outputs:
					self._datasets[id].update(dataset.DatasetStatus.Available)
					
				for id in self._inputs:
					self._datasets[id].on_descendant_finished(self)

	@property
	def commands(self):
		return self._commands

	@staticmethod
	def from_xml_node(node, datasets, dirname):
		"""
		Returns single value dictionary (id -> Task)
		"""
		id = node.attrib["id"]
		description = node.xpath("./description/text()")[0]
		
		id_extractor = lambda node: node.attrib["id"]

		inputs_nodes = node.xpath("./inputs/dataset")
		inputs = set(map(id_extractor, inputs_nodes))
		
		outputs_nodes = node.xpath("./outputs/dataset")
		outputs = set(map(id_extractor, outputs_nodes))
			
		stdout = node.xpath("./stderr/text()")
		if len(stdout) > 0:
			stdout = os.path.join(dirname, stdout[0])
		else:
			stdout = None

		stderr = node.xpath("./stdout/text()")
		if len(stderr) > 0:
			stderr = os.path.join(dirname, stderr[0])
		else:
			stderr = None
			
		command_nodes = node.xpath("./commands/command")
		commands = []
		for command_node in command_nodes:
			commands.append(AbstractCommand.from_xml_node(command_node, inputs, outputs))

		return Task(datasets, id, inputs, outputs, description, stdout, stderr, commands)
