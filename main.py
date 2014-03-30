#!/usr/bin/env python3

import workflow
import scheduler

w = workflow.AbstractWorkflow.from_xml_file("examples/copier/copier.xml")
s = scheduler.LocalScheduler()

s.schedule(w)
if w.failed:
	print("Schedule failed")
else:
	print("Schedule completed successfully")
