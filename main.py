#!/usr/bin/env python

import workflow
import scheduler

w = workflow.AbstractWorkflow.from_xml_file("examples/copier/copier.xml")
s = scheduler.LocalScheduler()

s.schedule(w)
print("Schedule done")
