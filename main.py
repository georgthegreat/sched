#!/usr/bin/env python3

import workflow
import scheduler

w = workflow.AbstractWorkflow.from_xml_file("examples/montage/montage.xml")
s = scheduler.LocalScheduler()

s.schedule(w)
print("Schedule done")
