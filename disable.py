#!/usr/bin/env python
from __future__ import print_function
from utils import versioned_hooks, print_success, print_error
import sys
import os

hooks_arg = sys.argv[1:]
for hook in hooks_arg:
	if hook not in versioned_hooks:
		print_error("'" + str(hook) + "' is not implemented and cannot be disabled. Terminating...")
		sys.exit(1)

hooks_to_disable = hooks_arg if hooks_arg else versioned_hooks

# delete existing symlinks and local unversioned hooks
os.chdir("../.git/hooks")
for f in os.listdir("."):
	if f in hooks_to_disable:
		os.remove(f)

print_success("Successfully disabled the following git hooks: " + ", ".join(hooks_to_disable))
