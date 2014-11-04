#!/usr/bin/env python3

import opster

from sched import workflow
from sched import scheduler

@opster.command()
def main(
	path=("p", "", "path to XML file with workflow description")
):
	w = workflow.AbstractWorkflow.from_xml_file(path)
	s = scheduler.LocalScheduler()

	s.schedule(w)
	if w.failed:
		print("Schedule failed")
	else:
		print("Schedule completed successfully")

if __name__ == "__main__":
	main.command()