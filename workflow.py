import codecs
import os.path

from lxml import etree

import dataset
import errors
import task

# Classes 
class AbstractWorkflow(object):
	"""
	Describes scientific workflow
	"""
	def __init__(self, datasets, tasks):
		"""
		Allows to create scientific workflow from a:
		
		* dict of datasets (id -> dataset)
		* dict of tasks (id -> task)
		"""
		self.datasets = datasets
		self.tasks = tasks
		#self.update_tasks

	def update_tasks(self):
		"""
		Visits all tasks and updates their status.
		Assumes that all tasks have "parsed" status at the beginning
		"""
		#for id_, task_ in self.tasks.iteritems():
		#	task_.update_status(self.datasets)
		#pass

	@staticmethod
	def from_xml_file(path):
		"""
		Parses xml file and returns a  workflow instance
		"""
		if not os.path.isfile(path):
			raise OSError("Path to file expected")
		
		basepath = os.path.abspath(path)
		dirname = os.path.dirname(basepath)

		with open(path, "r+b") as input_file:
			str_data = input_file.read()
			#trimming utf-8 byte order mark
			if str_data.startswith(codecs.BOM_UTF8):
				str_data = str_data[len(codecs.BOM_UTF8):].decode()
			else:
				print("Warning: File at {0} is not in utf-8".format(path))
				str_data = str_data.decode()
			return AbstractWorkflow.from_xml_string(str_data, dirname)

	@staticmethod
	def from_xml_string(string, dirname):
		"""
		Parses xml string and returns a workflow instance
		"""
		xml = etree.fromstring(string)
		
		datasets_nodes = xml.xpath("/workflow/datasets")
		if len(datasets_nodes) != 1:
			raise errors.ParseError("Exactly one 'datasets' node expected")
		dataset_nodes = datasets_nodes[0].xpath("./dataset")
		
		datasets = {}
		for node in dataset_nodes:
			datasets.update(dataset.Dataset.from_xml_node(node, dirname))
		
		tasks_nodes = xml.xpath("/workflow/tasks")
		if len(tasks_nodes) != 1:
			raise errors.ParseError("Exactly one 'tasks' node expected")	
		task_nodes = tasks_nodes[0].xpath("./task")
		
		tasks = {}
		for node in task_nodes:
			tasks.update(task.Task.from_xml_node(node))
			
		return AbstractWorkflow(datasets, tasks)
