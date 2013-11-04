import codecs
import os.path

from lxml import etree

from dataset import Dataset
from errors import ParseError
from task import Task

# Classes 
class ParsedWorkflow(object):
	"""
	Describes scientific workflow
	"""
	def __init__(self, datasets, tasks):
		"""
		Allows to create scientific workflow from a:
		
		* map of datasets (id -> dataset)
		* map of tasks (id -> task)
		"""
		self.datasets = datasets
		self.tasks = tasks
	

# Methods
def from_xml_file(path):
	"""
	Parses xml file and returns a  workflow instance
	"""
	if not os.path.isfile(path):
		raise OSError("Path to file expected")
		
	with open(path, "r+b") as input_file:
		str_data = input_file.read()
		#trimming utf-8 byte order mark
		if str_data.startswith(codecs.BOM_UTF8):
			str_data = str_data[len(codecs.BOM_UTF8):].decode()
		else:
			print("Warning: File at {0} is not in utf-8".format(path))
			str_data = str_data.decode()
		return from_xml_string(str_data)

		
def from_xml_string(str):
	"""
	Parses xml string and returns a workflow instance
	"""
	xml = etree.fromstring(str)
	
	datasets_nodes = xml.xpath("/workflow/datasets")
	if len(datasets_nodes) != 1:
		raise ParseError("Exactly one 'datasets' node expected")
	dataset_nodes = datasets_nodes[0].xpath("/dataset")
	
	datasets = {}
	for node in dataset_nodes:
		datasets.update(Dataset.from_xml_node(node))
	
	tasks_nodes = xml.xpath("/workflow/tasks")
	if len(tasks_nodes) != 1:
		raise ParseError("Exactly one 'tasks' node expected")	
	task_nodes = tasks_nodes[0].xpath("/task")	
	
	tasks = {}
	for node in task_nodes:
		tasks.update(Task.from_xml_node(node))
		
	return ParsedWorkflow(datasets, tasks)