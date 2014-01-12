#coding: utf-8
import os

import errors

class DatasetType(object):
	InputFile = 0 
	TemporaryFile = 1
	OutputFile = 2

	@staticmethod
	def from_string(value):
		_dict = {
			"input_file": DatasetType.InputFile,
			"tmpfile": DatasetType.TemporaryFile,
			"output_file": DatasetType.OutputFile
		}	
		
		if value in _dict:
			return _dict[value]
		else:
			raise errors.ParseError("Unknown dataset type")


class DatasetStatus(object):
	Available = 0
	NotAvailable = 1
	Removed = 2


class Dataset(object):
	"""
	Class representing input or output dataset
	"""
	def __init__(self, type_, path, description):
		self.type_ = type_
		self.path = path
		self.description = description
		self.status_ = DatasetStatus.NotAvailable

		if self.type_ == DatasetType.InputFile:
			self.update_and_validate(DatasetStatus.Available)

	def update_and_validate(self, new_status):
		"""
		Updates self.status as needed.
		Raises ValidationError if dataset isn't valid 
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
			self.status_ = new_status


	@staticmethod
	def from_xml_node(node, dirname):
		"""
		Returns single value dictionary (id -> Dataset)
		"""
		id_ = node.attrib["id"]
		type_ = DatasetType.from_string(node.attrib["type"])
		path = os.path.join(dirname, node.xpath("./path/text()")[0])
		description = node.xpath("./description/text()")[0]

		return {id_: Dataset(type_, path, description)}
