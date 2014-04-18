#!/usr/bin/env python3

from sched import workflow
from sched import scheduler

#w = workflow.AbstractWorkflow.from_xml_file("examples/copier/copier.xml")
w = workflow.AbstractWorkflow.from_xml_file("examples/montage/montage.xml")
s = scheduler.LocalScheduler()

s.schedule(w)
if w.failed:
	print("Schedule failed")
else:
	print("Schedule completed successfully")
