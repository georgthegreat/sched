def empty_progress_func(progress):
	pass

class TaskData(object):
	def __init__(self, task_, callback):
		self._task = task_
		self.callback = callback
		
	@property
	def command(self):
		return self._task.command_line
		
	@property
	def stdout(self):
		return self._task.stdout
		
	@property
	def stderr(self):
		return self._task.stderr
		
	@property
	def task_(self):
		return self._task
