import errors

class TaskType(object):
	unknown = 0
	local = 1
	
	@staticmethod
	def from_string(str):
		if str == "local":
			return TaskType.local
		else:
			return TaskType.unknown
			

class Task(object):
	"""
	Class representing single workflow task
	"""
	def __init__(self, type, path, input_datasets, output_datasets, description):
		self.type = type
		self.path = path
		self.description = description		
	
	@staticmethod	
	def from_xml_node(node):
		"""
		Returns single value dictionary (id -> Task)
		"""
		id = node.attrib["id"]
		type = TaskType.from_string(node.attrib["type"])
		path = node.xpath("/path")[0]
		description = node.xpath("/description")[0]
		command_args = node.xpath("/command-args")
		
		inputs_nodes = node.xpath("/inputs")
		if len(inputs_nodes) > 1:
			raise errors.ParseError("Multiple 'inputs' nodes found")
		dataset_nodes = inputs_nodes.xpath("/dataset")
		
		input_datasets = set()
		for node in dataset_nodes:
			id = node.attrib["id"]
			input_datasets.add(id)
		
		outputs_nodes = node.xpath("/outputs")
		if len(inputs_nodes) > 1:
			raise errors.ParseError("Multiple 'outputs' nodes found")
		dataset_nodes = outputs_nodes.xpath("/dataset")
		
		output_datasets = set()
		for node in dataset_nodes:
			id = node.attrib["id"]
			output_datasets.add(id)
			
		return {id: Task(type, path, input_datasets, output_datasets, description)}
