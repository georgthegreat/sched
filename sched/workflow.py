import codecs
import os.path
import queue

from lxml import etree

from . import dataset
from . import errors
from . import task

# Classes 
class AbstractWorkflow(object):
	"""
	Describes scientific workflow
	"""
	def __init__(self, datasets, tasks):
		"""
		Allows to create scientific workflow from:
		* dict of datasets (id -> dataset)
		* dict of tasks (id -> task)
		"""
		self.datasets = datasets
		self.tasks = tasks
		self.pending_tasks = queue.Queue()
		
		self.unfinished_count = len(tasks)
		self.has_failed = False
		
		self.update()

	def update(self, task_=None, new_status=None):
		"""
		Marks task_ to have new_status.
		Visits all tasks and updates their status.
		Pushes new tasks into pending_tasks queue.
		"""
		if new_status == task.TaskStatus.Failed:
			self.has_failed = True
			self.pending_tasks.put(None)
			
		if task_ is not None:
			task_.update(new_status)
			if task_.is_finished or task_.is_failed:
				self.unfinished_count -= 1			
			if self.finished:
				self.pending_tasks.put(None)
			
		for t in self.tasks.values():
			t.update()
			if t.is_pending:
				t.update(task.TaskStatus.Enqueued)
				self.pending_tasks.put(t)


	@property
	def finished(self):
		return self.unfinished_count == 0
		
	@property
	def failed(self):
		return self.has_failed
		
	def get_pending_task(self):
		return self.pending_tasks.get()
				
	@staticmethod
	def from_xml_file(path):
		"""
		Parses xml file and returns a  workflow instance
		"""
		if not os.path.isfile(path):
			raise OSError("Path to file expected")
		
		abspath = os.path.abspath(path)
		dirname = os.path.dirname(abspath)

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
			raise errors.XmlParseError("Exactly one 'datasets' node expected")
		dataset_nodes = datasets_nodes[0].xpath("./dataset")
		
		datasets = dict()
		for node in dataset_nodes:
			dataset_ = dataset.Dataset.from_xml_node(node, dirname)
			id_ = dataset_.id
			if id_ in datasets:
				raise errors.XmlParseError("Dataset id {id} isn't unique".format(
					id=id_
				))
			datasets[id_] = dataset_
		
		tasks_nodes = xml.xpath("/workflow/tasks")
		if len(tasks_nodes) != 1:
			raise errors.XmlParseError("Exactly one 'tasks' node expected")
		task_nodes = tasks_nodes[0].xpath("./task")
		
		tasks = dict()
		for node in task_nodes:
			task_ = task.Task.from_xml_node(node, datasets, dirname)
			id_ = task_.id
			if id_ in tasks:
				raise errors.XmlParseError("Task id {id} isn't unique".format(
					id=id_
				))
			tasks[id_] = task_
			
		return AbstractWorkflow(datasets, tasks)
