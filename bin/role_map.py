#!/usr/bin/env python
from __future__ import print_function

import re

import ospsurvey.probes.nodes
import ospsurvey.probes.stack

if __name__ == "__main__":

  # list the stacks and get the environment
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_name = stacks[0].Stack_Name
  stack_env = ospsurvey.probes.stack.get_environment(stack_name)

  # find all of the hints

  hints = {k:v for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}

  print(hints)

  
  node_patterns = {stack_name + '-' + v['capabilities:node']:re.sub('\SchedulerHints$','',k) for (k,v) in hints.items()}

  print(node_patterns)
  
