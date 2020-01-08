#!/usr/bin/env python
from __future__ import print_function


import ospsurvey.probes.stack

if __name__ == "__main__":

  stacks = ospsurvey.probes.stack.list_stacks()
  stack_env = ospsurvey.probes.stack.get_environment(stacks[0].Stack_Name)
