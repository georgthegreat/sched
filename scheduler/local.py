import multiprocessing
import os
import queue
import threading

import task
from scheduler import abstract

class LocalScheduler(abstract.AbstractScheduler):
	CPU_COUNT = multiprocessing.cpu_count()
	GET_TIMEOUT = 1

	PENDING_TASKS_FILTER = lambda task_obj: task_obj.status == task.TaskStatus.Pending

	def __init__(self):
		self.tasks = queue.Queue(self.CPU_COUNT)
		self.thread = threading.Thread(target=self.run, args=(self))
	
	def schedule(self, workflow, progress_func=abstract.empty_progress_func):
		"""
		Creates a separate thread to schedule workflow
		"""
		def workflow_finished():
			return workflow.finished

		threading.Thread(target=self.schedule_thread, args=(self, workflow, progress_func))
		cv = threading.Condition()
		cv.wait_for(workflow_finished)
	
	def schedule_thread(self, workflow, progress_func):
		"""
		Runs in a separate thread, performs single workflow scheduling
		"""
		for task_ in workflow.pending_tasks:
			self.tasks.put(task_)

	def run(self):
		"""
		Performs infinite scheduling of 
		"""	
		def wait(running_pids):
			(pid, status) = os.waitpid(-1, os.WNOHANG)
			while pid != 0:
				print("Process finished")
				#TODO: process status here
				#TODO: notify someone here
				running_pids.remove(pid)
				(pid, status) = os.waitpid(-1, os.WNOHANG)

		running_pids = set()
		while True:
			while len(running_pids) < self.CPU_COUNT:
				task_ = self.tasks.get()
				print("Executing task {0}".format(task_.description))
				running_pids.add(31337)
				wait(running_pids)

			wait(running_pids)
