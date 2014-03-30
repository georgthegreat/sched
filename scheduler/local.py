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
	SUPPORTED_COMMAND_TYPES = {task.CommandType.Local, task.CommandType.FileDivisible}

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
		
		#semaphore to control the amount of processes running simultaneously
		self.free_cpu_semaphore = threading.Semaphore(self.CPU_COUNT)
		
		#semaphore to control if os.wait* wouldn't throw (i. e. there are child processes)
		self.wait_semaphore = threading.Semaphore(0)

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
		
	def choose_command(self, task_, datasets):
		def appeal(total_cpus, tasks_len, running_len, args_len):
			#MAGIC FORMULA
			return float(tasks_len + running_len + args_len) / float(total_cpus)
			
		tasks_len = self.tasks.qsize()
		#TODO: it's not good to use private field here
		running_len = (self.CPU_COUNT - self.free_cpu_semaphore._value)
		
		#list of tuples (appeal, command)
		command_appeals = []
		for command_type in (self.SUPPORTED_COMMAND_TYPES & task_.commands.keys()):
			command = task_.commands[command_type]
			
			command_appeal = (
				appeal(self.CPU_COUNT, tasks_len, running_len, command.estimate_args_count(datasets)),
				command
			)
			command_appeals.append(command_appeal)
		
		most_appealed = max(command_appeals)
		return most_appealed[1]
			
	def schedule_thread(self, workflow, progress_func):
		"""
		Runs in a separate thread, performs single workflow scheduling
		"""
		def local_callback(task_data, exit_status):
			print("Within local_callback for {id}".format(
				id=task_data.id
			))
			if exit_status == constants.EXIT_STATUS_OK:
				workflow.update(task_data.task, task.TaskStatus.Finished)
			else:
				workflow.update(task_data.task, task.TaskStatus.Failed)
			#TODO: call progress_func here
			
		def file_divisible_callback(task_data, exit_status):
			print("Within file_divisible_callback for {id}".format(
				id=task_data.id
			))
			if exit_status == constants.EXIT_STATUS_OK:
				task_data.finished = task_data.finished + 1
				if task_data.finished == task_data.swarm_size:
					workflow.update(task_data.task, task.TaskStatus.Finished)
			else:
				workflow.update(task_data.task, task.TaskStatus.Failed)
			#TODO: call progress_func here
		
		COMMAND_TYPE_TO_CALLBACK = {
			task.CommandType.Local: local_callback,
			task.CommandType.FileDivisible: file_divisible_callback
		}
		
		while not (workflow.finished or workflow.failed):
			task_ = workflow.get_pending_task()
			if task_ is not None:
				#only local scheduling is possible
				command_types = task_.commands.keys()
				
				if len(command_types & self.SUPPORTED_COMMAND_TYPES) == 0:
					raise RuntimeError("No supported commands can be found for task {id}".format(
						task_.id
					))
				
				command = self.choose_command(task_, workflow.datasets)
				total_args = command.eval_args(workflow.datasets)
				callback = COMMAND_TYPE_TO_CALLBACK[command.type]
				task_data = common.TaskData(task_, total_args, len(total_args), callback)
				for current_args in total_args:
					self.tasks.put(task_data)

	def run(self):
		"""
		Performs infinite scheduling of pending tasks 
		"""
		while True:
			task_data = self.tasks.get()
			self.free_cpu_semaphore.acquire()
			
			stdout = task_data.stdout
			if stdout is not None:
				stdout = open(stdout, "w")
			else:
				#TODO: replace with subprocess.DEVNULL in Python-3.3				
				stdout = open(os.devnull, "w")
				
			stderr = task_data.stderr
			if stderr is not None:
				stderr = open(stderr, "w")
			else:
				#TODO: replace with subprocess.DEVNULL in Python-3.3
				stderr = open(os.devnull, "w")

			try:
				pid = subprocess.Popen(
					args=task_data.args,
					stdout=stdout,
					stderr=stderr
				).pid
			except Exception as ex:
				# No such file
				print(ex)
				task_data.callback(task_data, constants.EXIT_STATUS_FAIL)
				self.free_cpu_semaphore.release()
				continue
			
			task_data.task.update(task.TaskStatus.Running)
			with self.running_lock:
				print("Started program with pid {pid}".format(
					pid=pid
				))
				self.running[pid] = task_data
			self.wait_semaphore.release()

	def wait(self):
		while True:
			self.wait_semaphore.acquire()
			(pid, exit_status) = os.waitpid(-1, 0)
			exit_status >>= 8
		
			
			print("Wait program with pid {0}".format(pid))
			#releasing resources allocated by
			self.free_cpu_semaphore.release()
			with self.running_lock:
				task_data = self.running.pop(pid)
			
			task_data.callback(task_data, exit_status)
