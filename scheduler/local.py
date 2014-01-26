import multiprocessing
import os
import queue
import signal
import subprocess
import threading

import constants
import task
from scheduler import abstract
from scheduler import common

class LocalScheduler(abstract.AbstractScheduler):
	CPU_COUNT = multiprocessing.cpu_count()

	def __init__(self):
		self.tasks = queue.Queue(self.CPU_COUNT)

		self.run_thread = threading.Thread(target=self.run)
		self.run_thread.daemon = True
		self.wait_thread = threading.Thread(target=self.wait)
		self.wait_thread.daemon = True
		self.running = dict()
	
		#synchonization primitives
		#lock to guard self.running dictionary
		self.running_lock = threading.Lock()
		#semaphore to control the amount of process, running simultaneously
		self.running_semaphore = threading.Semaphore(self.CPU_COUNT)

		self.run_thread.start()		
		self.wait_thread.start()
	
	def schedule(self, workflow, progress_func=common.empty_progress_func):
		"""
		Creates a separate thread to schedule workflow
		"""
		thread = threading.Thread(
			target=self.schedule_thread, 
			args=[workflow, progress_func])
		thread.start()
		thread.join()
	
	def schedule_thread(self, workflow, progress_func):
		"""
		Runs in a separate thread, performs single workflow scheduling
		"""
		def callback(task_data, exit_status):
			print("Within callback")
			if exit_status == constants.EXIT_STATUS_OK:
				workflow.update(task_data.task_, task.TaskStatus.Finished)
			else:
				workflow.update(task_data.task_, task.TaskStatus.Failed)
			workflow.pending_tasks.task_done()
			#TODO: call progress_func here
			
		while not workflow.finished:
			task_ = workflow.get_pending_task()
			if task_ is not None:
				command = task_.command_line()
				task_data = common.TaskData(task_, callback)
				self.tasks.put(task_data)

	def run(self):
		"""
		Performs infinite scheduling of pending tasks 
		"""
		while True:
			task_data = self.tasks.get()
			self.running_semaphore.acquire()

			pid = subprocess.Popen(task_data.command).pid
			task_data.task_.update(task.TaskStatus.Running)
			with self.running_lock:
				print("Started program with pid {0}".format(pid))
				self.running[pid] = task_data

	def wait(self):
		while True:
			print("Waiting")
			try:
				(pid, exit_status) = os.waitpid(-1, 0)
				exit_status >>= 8
			except OSError:
				print("Got error")
				#when wait is called, and there is no child processes
				#OSError is being raised
				#it's good to wait for sigwait, but it's unavailable before python-3.3
				#signal.sigwait(signal.SIGCHILD)
				import time
				time.sleep(1)				
				continue
			
			print("Wait program with pid {0}".format(pid))
			#releasing resources allocated by
			self.running_semaphore.release()
			with self.running_lock:
				task_data = self.running.pop(pid)
			
			task_data.callback(task_data, exit_status)
