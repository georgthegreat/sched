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
	def __init__(self, id_, type_, path, description):
		self._id = id_
		self.type_ = type_
		self.path = path
		self.description = description
		self._status = DatasetStatus.NotAvailable

		if self.type_ == DatasetType.InputFile:
			self.update(DatasetStatus.Available)
	
	#class member properties
	@property
	def id(self):
		return self._id
		
	#status access properties	
	@property
	def is_available(self):
		return self._status == DatasetStatus.Available
			
	def update(self, new_status):
		"""
		Updates self._status as needed.
		Raises ValidationError if status isn't valid 
		"""
		if self.type_ == DatasetType.InputFile:
			if new_status == DatasetStatus.Available:
				if not os.path.isfile(self.path):
					raise errors.ValidationError("Dataset of type [{0}] isn't accessible"\
						.format(self.type_))
			else:
				raise errors.ValidationError("Dataset of type [{0}] got invalid status [{1}]"\
					.format(self.type_, new_status))
		elif self.type_ == DatasetType.OutputFile:
			if new_status == DatasetStatus.Removed:
				raise errors.ValidationError("Dataset of type [{0}] got invalid status [{1}]"\
					.format(self.type_, new_status))
		else:
			pass
			
		self._status = new_status

	@staticmethod
	def from_xml_node(node, dirname):
		"""
		Returns single value dictionary (id -> Dataset)
		"""
		id_ = node.attrib["id"]
		type_ = DatasetType.from_string(node.attrib["type"])
		path = os.path.join(dirname, node.xpath("./path/text()")[0])
		description = node.xpath("./description/text()")[0]

		return Dataset(id_, type_, path, description)
