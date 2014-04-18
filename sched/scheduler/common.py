def empty_progress_func(progress):
	pass

class TaskData(object):
	"""
	Auxiliary class to be used within schedulers
	"""
	def __init__(self, task_, args, swarm_size, callback):
		self._task = task_
		self._callback = callback
		self._args = args
		self._args_index = 0
		self._finished = 0
		self._swarm_size = swarm_size

	@property
	def finished(self):
		return self._finished
	
	@finished.setter
	def finished(self, value):
		self._finished = value
	
	@property
	def swarm_size(self):	
		return self._swarm_size
		
	@property
	def args(self):
		"""
		Function returning subsequent args from self._args
		"""
		args = self._args[self._args_index]
		self._args_index += 1
		return args
		
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