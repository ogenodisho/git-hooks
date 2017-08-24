#!/usr/bin/env python
from __future__ import print_function
from utils import print_success, print_error
import os

enabled_githooks = os.popen("ls -l ../.git/hooks | grep '^l' | sed 's/.*\///'").read().split()

if not enabled_githooks:
	print_error("No git hooks are currently enabled!")
else:
	print_success("Currently enabled git hooks are: %s" % ", ".join(enabled_githooks))
