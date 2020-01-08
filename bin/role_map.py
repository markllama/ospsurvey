#!/usr/bin/env python
from __future__ import print_function


import ospsurvey.probes.stack

if __name__ == "__main__":

  # list the stacks and get the environment
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_env = ospsurvey.probes.stack.get_environment(stacks[0].Stack_Name)

  # find all of the hints

  hints = {k:v for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}
  
