import math
import os
import queue
import threading

from . import common
from . import abstract
#from . import local
from . import llapi
from .. import constants
from .. import task
from ..config import config

class LoadLevelerScheduler(abstract.AbstractScheduler):
	@staticmethod
	def get_nodes_count():
		machine_info = llapi.MachineInfo()
		return machine_info.total_nodes
	
	#commands are arranged according to their priority
	SUPPORTED_COMMAND_TYPES = [
		task.CommandType.Mpi,
#		task.CommandType.MpiFileDivisible,
#		task.CommandType.FileDivisible,
#		task.CommandType.Local,
	]

	def __init__(self):
		self.NODES_COUNT = self.get_nodes_count()

		self.tasks = queue.Queue()

		self.run_thread = threading.Thread(target=self.run)
		self.run_thread.daemon = True
		self.wait_thread = threading.Thread(target=self.wait)
		self.wait_thread.daemon = True
		self.running = dict()

		self.internal_resource_reqs = 0

		#synchonization primitives
		#lock to guard self.running dictionary
		self.running_lock = threading.Lock()
		self.internal_resource_reqs_lock = threading.Lock()

		self.job_monitor = llapi.JobMonitor(os.path.join(
			os.path.dirname(__file__),
			"llapi"
		))

		self.run_thread.start()
		self.wait_thread.start()

	def schedule(self, workflow, progress_func=common.empty_progress_func):
		"""
		Creates a separate thread to schedule workflow
		"""
		thread = threading.Thread(
			target=self.schedule_thread,
			args=[workflow, progress_func]
		)
		thread.start()
		thread.join()

	def choose_command(self, task_, datasets):
		def appeal(total_nodes, allocated_nodes, internalqcpus, tasks_len, running_len, args_len):
			#MAGIC FORMULA
			return 0
			return float(tasks_len + running_len + args_len) / float(total_cpus)

		def get_allocated_nodes():
			"""
			Calculates the number of computing nodes now in use
			"""
			jobs_info = llapi.JobsInfo(llapi.StepState.Running)
			result = 0
			for i in range(0, len(jobs_info)):
				result += jobs_info[i].cpus_allocated
			return result

		def get_external_queue_nodes():
			"""
			Calculates the total amount of resource requirements in LoadLeveler queue
			"""
			jobs_info = llapi.JobsInfo([
				llapi.StepState.Idle,
				llapi.StepState.Pending
			])
			result = 0
			for i in range(0, len(jobs_info)):
				result += jobs_info[i].cpus_requested
			return result

		tasks_len = self.tasks.qsize()

		allocated_nodes = get_allocated_nodes()
		external_queue_nodes = get_external_queue_nodes()
		internal_queue_nodes = self.internal_resource_reqs

		augmented_free_nodes = (
			(self.NODES_COUNT - allocated_nodes) - 
			config.loadleveler.internal_resource_weight * internal_queue_nodes -
			config.loadleveler.external_resource_weight * external_queue_nodes
		)
		
		print("Allocated: " + str(allocated_nodes))
		print("External: " + str(external_queue_nodes))
		print("Internal: " + str(internal_queue_nodes))
		print("Augmented: " + str(augmented_free_nodes))


		#list of tuples (appeal, command)
		chosen_command = None
		chosen_command_nodes = 0
		for command_type in self.SUPPORTED_COMMAND_TYPES:
			command = task_.commands.get(command_type, None)
			if command is None:
				continue

			command_nodes = max(
				min(
					augmented_free_nodes,
					command.max_nodes
				),
				command.min_nodes
			)

			chosen_command = command
			chosen_command_nodes = command_nodes

			if command.min_nodes < command_nodes:
				#best fitting command was found	
				break
		
		chosen_command_nodes = config.loadleveler.partition_size * math.floor(
			chosen_command_nodes / config.loadleveler.partition_size
		)

		return (chosen_command, chosen_command_nodes)

	def schedule_thread(self, workflow, progress_func):
		"""
		Runs in a separate thread, performs single workflow scheduling
		"""
		def mpi_callback(task_data, exit_status):
			print("Within mpi_callback for {id}".format(
				id=task_data.id
			))
			if exit_status == constants.EXIT_STATUS_OK:
				task_data.mark_finished()
				if (task_data.unfinished_count == 0):
					workflow.update(task_data.task, task.TaskStatus.Finished)
			else:
				task_data.mark_failed()
				if (task_data.fail_count < config.scheduler.reschedule_attempts):
					print("Task {id} failed. Rescheduling".format(id=task_data.id))
					self.tasks.put(task_data)
				else:
					print("Task {id} failed. Marking workflow as failed".format(id=task_data.id))
					workflow.update(task_data.task, task.TaskStatus.Failed)
			#TODO: call progress_func here

		while not (workflow.finished or workflow.failed):
			task_ = workflow.get_pending_task()
			if task_ is not None:
				command, command_nodes = self.choose_command(task_, workflow.datasets)
				if command is None:
					raise RuntimeError("Failed to choose command")

				total_args = command.eval_args(workflow.datasets)
				#using semaphore as shared counter
				unfinished_count = threading.Semaphore(len(total_args))
				
				#FIXME
				time_limit_seconds = 180
				
				for args in total_args:
					task_data = common.TaskData(
						task_,
						args,
						unfinished_count,
						command_nodes,
						time_limit_seconds,
						mpi_callback
					)
					
					self.tasks.put(task_data)
					with self.internal_resource_reqs_lock:
						self.internal_resource_reqs += task_data.nodes_count

	def run(self):
		"""
		Performs infinite scheduling of pending tasks
		"""
		while True:

			task_data = self.tasks.get()
			with self.internal_resource_reqs_lock:
				self.internal_resource_reqs -= task_data.nodes_count

			stdout = task_data.stdout or "/dev/null"
			stderr = task_data.stderr or "/dev/null"
			
			submit_info = llapi.SubmitInfo(
			    task_data.args,
				stdout,
				stderr,
				task_data.nodes_count,
				task_data.time_limit_seconds
			)
			
			try:
				print("Submitting job")
				job_id = self.job_monitor.submit_job(submit_info)
			except Exception as ex:
				# Submission failed
				print(ex)
				task_data.callback(task_data, constants.EXIT_STATUS_FAIL)
				continue

			task_data.task.update(task.TaskStatus.Running)

			with self.running_lock:
				print("Submitted job with id {job_id}".format(
					job_id=job_id
				))
				self.running[job_id] = task_data

	def wait(self):
		while True:
			print("Waiting")
			wait_result = self.job_monitor.wait()
			job_id = wait_result.get_job_id()
			#there is exactly one succesful exit status
			exit_status = (
				0
				if (wait_result.step_state == llapi.StepState.Completed)
				else 1
			)


			print("Wait job with id {0}".format(job_id))
			#releasing resources allocated by
			with self.running_lock:
				task_data = self.running.pop(job_id)

			task_data.callback(task_data, exit_status)

