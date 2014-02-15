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
	def task_(self):
		return self._task
