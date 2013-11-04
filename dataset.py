class DatasetType(object):
	unknown = 0
	file = 1
	
	@staticmethod
	def from_string(str):
		if str == "file":
			return DatasetType.file
		else:
			return DatasetType.unknown
		

class Dataset(object):
	"""
	Class representing input or output dataset
	"""
	def __init__(self, type, path, description):
		self.type = type
		self.path = path
		self.description = description
	
	@staticmethod
	def from_xml_node(node):
		"""
		Returns single value dictionary (id -> Dataset)
		"""
		id = node.attrib["id"]
		type = DatasetType.from_string(node.attrib["type"])
		path = node.xpath("/path")[0]
		description = node.xpath("/description")[0]
		
		return {id: Dataset(type, path, description)}
