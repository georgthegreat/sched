#coding: utf-8
import os
import shutil

from . import errors

DATASET_ID_PATTERN = "(?P<id>[\w_][\w\d_]*)"

#TODO: use enum.Enum in Python-3.4
class DatasetType(object):
	InputFile = 0 
	TemporaryFile = 1
	OutputFile = 2
	InputFolder = 3
	TemporaryFolder = 4
	OutputFolder = 5
	
	_dict = {
		"input_file": InputFile,
		"tmp_file": TemporaryFile,
		"output_file": OutputFile,
		"input_folder": InputFolder,
		"tmp_folder": TemporaryFolder,
		"output_folder": OutputFolder
	}
		
	@staticmethod
	def from_string(value):		
		result = DatasetType._dict.get(value, None)
		if result is None:
			raise errors.XmlParseError("Unknown dataset type {value}".format(
				value=value
			))
		return result


#TODO: use enum.Enum in Python-3.4
class DatasetStatus(object):
	Available = 0
	NotAvailable = 1
	Removed = 2


class Dataset(object):
	"""
	Class representing input or output dataset
	"""
	def __init__(self, id, type, path, path_touch, description):
		self._id = id
		self._type = type
		self._path = path
		self._description = description
		self._status = DatasetStatus.NotAvailable
		
		#number of output edges (i. e. number of tasks waiting for this dataset)
		self._descendants = 0

		if path_touch:
			self.touch()
			
		if self.is_input:
			self.update(DatasetStatus.Available)
			
	
	#class member properties
	@property
	def id(self):
		return self._id

	#status access properties	
	@property
	def is_available(self):
		return self._status == DatasetStatus.Available
		
	#type access properties
	@property
	def is_temporary(self):
		return (
			(self._type == DatasetType.TemporaryFile) or
			(self._type == DatasetType.TemporaryFolder)
		)

	@property
	def is_input(self):
		return (
			(self._type == DatasetType.InputFile) or
			(self._type == DatasetType.InputFolder)
		)
		
	@property
	def is_output(self):
		return (
			(self._type == DatasetType.OutputFile) or
			(self._type == DatasetType.OutputFolder)
		)
	
	@property
	def is_file(self):
		return (
			(self._type == DatasetType.InputFile) or
			(self._type == DatasetType.TemporaryFile) or
			(self._type == DatasetType.OutputFile)
		)
		
	@property
	def is_folder(self):
		return (
			(self._type == DatasetType.InputFolder) or
			(self._type == DatasetType.TemporaryFolder) or
			(self._type == DatasetType.OutputFolder)
		)
		
	@property
	def path(self):
		return self._path
		
	def touch(self):
		"""
		Creates empty dataset (file or folder)
		"""
		if self.is_file:
			with open(self._path, "w") as file:
				pass
		elif self.is_folder:
			if not os.path.isdir(self._path):
				os.makedirs(self._path, exist_ok=True)
		else:
			raise NotImplementedError()
	
	#instance methods
	def remove(self):
		if self.is_file:
			os.remove(self._path)
		elif self.is_folder:
			shutil.rmtree(self._path)
		else:
			raise NotImplementedError()
		
	def add_descendant(self, task):
		self._descendants += 1
		
	def on_descendant_finished(self, task):
		self._descendants -= 1
		if (self._descendants == 0) and self.is_temporary:
			self.remove()
			self.update(DatasetStatus.Removed)
		
	def update(self, new_status):
		"""
		Updates self._status as needed.
		Raises ValidationError if status isn't valid 
		"""
		if self.is_input:
			if new_status == DatasetStatus.Available:
				if not os.path.exists(self._path):
					raise errors.ValidationError("Dataset of type [{0}] isn't accessible"\
						.format(self._type))
			else:
				raise errors.ValidationError("Dataset of type [{0}] got invalid status [{1}]"\
					.format(self._type, new_status))
		elif self.is_output:
			if new_status == DatasetStatus.Removed:
				raise errors.ValidationError("Dataset of type [{0}] got invalid status [{1}]"\
					.format(self._type, new_status))
		else:
			pass
			
		self._status = new_status

	@staticmethod
	def from_xml_node(node, dirname):
		"""
		Returns single value dictionary (id -> Dataset)
		"""
		id = node.attrib["id"]
		type = DatasetType.from_string(node.attrib["type"])
		path_node = node.xpath("./path")[0]
		path_touch = (path_node.attrib.get("touch", "false") == "true")
		path = os.path.join(dirname, path_node.text)
		description = node.xpath("./description/text()")[0]

		return Dataset(id, type, path, path_touch, description)
