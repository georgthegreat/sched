import errors

class TaskType(object):
	Unknown = 0
	Local = 1
	
	@staticmethod
	def from_string(str):
		if str == "local":
			return TaskType.Local
		else:
			return TaskType.Unknown


class TaskStatus(object):
	Parsed = 0
	WaitForDeps = 1
	Pending = 2
	Running = 3
	Finished = 4
	Failed = 5


class Task(object):
	"""
	Class representing single workflow task
	"""
	def __init__(self, type_, path, input_datasets, output_datasets, description, command_args):
		self.type_ = type_
		self.path = path
		self.input_datasets = input_datasets
		self.output_datasets = output_datasets
		self.description = description
		self.status = TaskStatus.Parsed
		self.command_args = command_args

	def update_and_validate(self, new_status, datasets):
		pass

	@property
	def command_line(self):
		"""
		Returns list containing task as a command
		"""
		command = []
		command.append(self.path)


	@staticmethod	
	def from_xml_node(node):
		"""
		Returns single value dictionary (id -> Task)
		"""
		id = node.attrib["id"]
		type = TaskType.from_string(node.attrib["type"])
		path = node.xpath("./path/text()")[0]
		description = node.xpath("./description/text()")[0]
		command_args = node.xpath("./command-args/text()")[0]
		
		id_extractor = lambda node: node.attrib["id"]

		inputs_nodes = node.xpath("./inputs[0]/dataset")
		input_datasets = set(map(id_extractor, inputs_nodes))
		
		outputs_nodes = node.xpath("./outputs[0]/dataset")
		output_datasets = set(map(id_extractor, outputs_nodes))
		
		return {id: Task(type, path, input_datasets, output_datasets, description, command_args)}
