#!/usr/bin/env python

import workflow
import scheduler

w = workflow.AbstractWorkflow.from_xml_file("examples/example.xml")
s = scheduler.LocalScheduler()

s.schedule(w)
print("Schedule done")
