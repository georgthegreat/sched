from . import common

class AbstractScheduler(object):
	
	def schedule(workflow, progress_func=common.empty_progress_func):
		raise NotImplementedError()
		
	def choose_command(self, task_, datasets):
		raise NotImplementedError()