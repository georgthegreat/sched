import os.path
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
	Enqueued = 2
	Running = 3
	Finished = 4
	Failed = 5


class Task(object):
	"""
	Class representing single workflow task
	"""
	ARG_REGEXP = re.compile("^\$([\w_][\w\d_]*)")

	def __init__(self, datasets, id, type, _path, inputs, outputs, description, args, stdout, stderr):
		self._datasets = datasets
		
		self._id = id
		self._type = type
		self._path = _path
		self._inputs = inputs
		self._outputs = outputs
		self._description = description
		self._status = TaskStatus.Waiting
		self._datasets = datasets
		self._command_line = self.eval_command_line(args.split())
		
		self._stdout = stdout
		if self._stdout is not None:
			dirname = os.path.dirname(self._stdout)
			os.makedirs(dirname, exist_ok=True)
		
		self._stderr = stderr
		if self._stderr is not None:
			dirname = os.path.dirname(self._stderr)
			os.makedirs(dirname, exist_ok=True)
		
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
	def command_line(self):
		return self._command_line
					
	def eval_command_line(self, args):
		"""
		Returns list containing task as a command
		"""
		command = [self._path]
		used_datasets = set()
		expected_datasets = self._inputs | self._outputs
		for arg in args:
			match = self.ARG_REGEXP.match(arg)
			if match:
				id = match.group(1)
				if (id not in self._inputs) and (id not in self._outputs):
					raise errors.ValidationError("Can't use dataset id {id} in command line. It's neither input nor output dataset of task {task_id}".format(
						id=id,
						task_id=self._id
					))
				used_datasets.add(id)
				command.append(self._datasets[id]._path)
			else:
				command.append(arg)
		if used_datasets != expected_datasets:
			raise errors.ValidationError("Not all datasets were used in command line of task {id}".format(
				id=self._id
			))
		return command		

	@staticmethod
	def from_xml_node(node, datasets, dirname):
		"""
		Returns single value dictionary (id -> Task)
		"""
		id = node.attrib["id"]
		type = TaskType.from_string(node.attrib["type"])
		path = node.xpath("./path/text()")[0]
		description = node.xpath("./description/text()")[0]
		command_args = node.xpath("./args/text()")[0]
		
		id_extractor = lambda node: node.attrib["id"]

		inputs_nodes = node.xpath("./inputs/dataset")
		inputs = set(map(id_extractor, inputs_nodes))
		
		outputs_nodes = node.xpath("./outputs/dataset")
		outputs = set(map(id_extractor, outputs_nodes))
		
		if (len(inputs) == 0) and (len(outputs) == 0):
			raise errors.ParseError("Task {id} doesn't have any input or output datasets".format(
				id=id
			))
			
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
			
		return Task(datasets, id, type, path, inputs, outputs, description, command_args, stdout, stderr)
