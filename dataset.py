#coding: utf-8
import os

import errors

class DatasetType(object):
	InputFile = 0 
	TemporaryFile = 1
	OutputFile = 2
	
	_dict = {
		"input_file": InputFile,
		"tmp_file": TemporaryFile,
		"output_file": OutputFile
	}
		
	@staticmethod
	def from_string(value):		
		result = DatasetType._dict.get(value, None)
		if result is None:
			raise errors.ParseError("Unknown dataset type {value}".format(
				value=value
			))
		return result


class DatasetStatus(object):
	Available = 0
	NotAvailable = 1
	Removed = 2


class Dataset(object):
	"""
	Class representing input or output dataset
	"""
	def __init__(self, id, type, path, description):
		self._id = id
		self._type = type
		self._path = path
		self._description = description
		self._status = DatasetStatus.NotAvailable
		
		#number of output edges (i. e. number of tasks waiting for this dataset)
		self._descendants = 0

		if self._type == DatasetType.InputFile:
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
		return self._type == DatasetType.TemporaryFile

	def remove(self):
		os.remove(self._path)
		
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
		if self._type == DatasetType.InputFile:
			if new_status == DatasetStatus.Available:
				if not os.path.isfile(self._path):
					raise errors.ValidationError("Dataset of type [{0}] isn't accessible"\
						.format(self._type))
			else:
				raise errors.ValidationError("Dataset of type [{0}] got invalid status [{1}]"\
					.format(self._type, new_status))
		elif self._type == DatasetType.OutputFile:
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
		path = os.path.join(dirname, node.xpath("./path/text()")[0])
		description = node.xpath("./description/text()")[0]

		return Dataset(id, type, path, description)
