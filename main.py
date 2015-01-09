#!/usr/bin/env python3

import sys

import opster

from sched import workflow
from sched import scheduler

@opster.command()
def main(
	path=("p", "", "path to XML file with workflow description"),
	scheduler_type=("s", "", "scheduler type to use (local, loadleveler)")
):
	w = workflow.AbstractWorkflow.from_xml_file(path)

	if (scheduler_type == "local"):
		s = scheduler.LocalScheduler()
	elif (scheduler_type == "loadleveler"):
		s = scheduler.LoadLevelerScheduler()
	else:
		print("Unsupported scheduler type {scheduler_type}".format(
			scheduler_type=scheduler_type
		))
		sys.exit(1)

	s.schedule(w)
	if w.failed:
		print("Schedule failed")
	else:
		print("Schedule completed successfully")

if __name__ == "__main__":
	main.command()
