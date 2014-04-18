def empty_progress_func(progress):
	pass

class TaskData(object):
	"""
	Auxiliary class to be used within schedulers
	"""
	def __init__(self, task_, args, unfinished_count, callback):
		self._task = task_
		self._callback = callback
		self._args = args
		
		self._unfinished_count = unfinished_count
		self._fail_count = 0

	@property
	def unfinished_count(self):
		"""
		When task was divided into multiple subtasks, this property 
		is the number of unfinished tasks in a swarm
		"""
		return self._unfinished_count._value
		
	@property
	def fail_count(self):
		return self._fail_count
	
	@fail_count.setter
	def fail_count(self, value):
		self._fail_count = value
		
	@property
	def args(self):
		"""
		Function returning subsequent args from self._args
		"""
		return self._args
			
	@property
	def stdout(self):
		return self._task.stdout
		
	@property
	def stderr(self):
		return self._task.stderr
		
	@property
	def id(self):
		return self._task.id
		
	@property
	def task(self):
		return self._task

	@property
	def callback(self):
		return self._callback