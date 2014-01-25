from scheduler import common

class AbstractScheduler(object):
	
	def schedule(workflow, progress_func=common.empty_progress_func):
		raise NotImplemented()
