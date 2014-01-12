def empty_progress_func(progress):
	pass

class AbstractScheduler(object):
	
	def schedule(workflow, progress_func=empty_progress_func):
		raise NotImplemented()
