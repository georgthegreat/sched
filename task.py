import re

import errors
import dataset

class TaskType(object):
	Local = 0
	
	_dict = {
		"local": Local
	}
	
	@staticmethod
	def from_string(value):
		result = TaskType._dict.get(value, None)
		if result is None:
			raise errors.ParseError("Unknown task type {value}".format(
				value=value
			))
		return result


class TaskStatus(object):
	Waiting = 0
	Pending = 1
	Running = 2
	Finished = 3
	Failed = 4


class Task(object):
	"""
	Class representing single workflow task
	"""
	ARG_REGEXP = re.compile("^\$([\w_][\w\d_]*)")

	def __init__(self, datasets, id_, type_, path, input_datasets, output_datasets, description, args):
		self._datasets = datasets
		
		self._id = id_
		self.type_ = type_
		self.path = path
		self.input_datasets = input_datasets
		self.output_datasets = output_datasets
		self.description = description
		self._status = TaskStatus.Waiting
		self._datasets = datasets
		
		self.args = args.split()
	
	#class member properties
	@property
	def id(self):
		return self._id
	
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
				
				if all(map(available, self.input_datasets)):
					self._status = TaskStatus.Pending
		else:
			self._status = new_status
			if self.is_finished:
				for id in self.output_datasets:
					self._datasets[id].update(dataset.DatasetStatus.Available)

	def command_line(self):
		"""
		Returns list containing task as a command
		"""
		command = []
		command.append(self.path)
		for arg in self.args:
			match = self.ARG_REGEXP.match(arg)
			if match:
				dataset_id = match.group(1)
				command.append(self._datasets[dataset_id].path)
			else:
				command.append(arg)
		return command		

	@staticmethod	
	def from_xml_node(node, datasets):
		"""
		Returns single value dictionary (id -> Task)
		"""
		id_ = node.attrib["id"]
		type_ = TaskType.from_string(node.attrib["type"])
		path = node.xpath("./path/text()")[0]
		description = node.xpath("./description/text()")[0]
		command_args = node.xpath("./args/text()")[0]
		
		id_extractor = lambda node: node.attrib["id"]

		inputs_nodes = node.xpath("./inputs/dataset")
		input_datasets = set(map(id_extractor, inputs_nodes))
		
		outputs_nodes = node.xpath("./outputs/dataset")
		output_datasets = set(map(id_extractor, outputs_nodes))
		
		if (len(input_datasets) == 0) and \
			(len(output_datasets) == 0):
			raise errors.ParseError("Task {id} doesn't have any input or output datasets".format(
				id=id_
			))
		
		return Task(datasets, id_, type_, path, input_datasets, output_datasets, description, command_args)
