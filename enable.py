#!/usr/bin/env python

from __future__ import print_function

import sys

version_of_pip_to_use = "pip" + ("3" if sys.version_info >= (3, 0) else "2")

# check jsonschema module
try:
	import jsonschema
except ImportError:
	print("Git hooks require the jsonschema module but it was not found!\nPlease run '%s" % version_of_pip_to_use + " install jsonschema'")
	sys.exit(1)

# check for javalang module
try:
	import javalang
except ImportError:
	print("Git hooks require the javalang module but it was not found!\nPlease run '%s" % version_of_pip_to_use + " install javalang'")
	sys.exit(1)

# check for gherkin module
try:
	import gherkin
except ImportError:
	print("Git hooks require the gherkin module but it was not found!\nPlease run '%s" % version_of_pip_to_use + " install gherkin-official'")
	sys.exit(1)

from utils import versioned_hooks, print_error, print_success
import os
import subprocess

# delete existing git hooks from the .git folder
os.chdir("../.git/hooks")
for f in os.listdir("."):
	if f in versioned_hooks:
		os.remove(f)

hooks_arg = sys.argv[1:]
for hook in hooks_arg:
	if hook not in versioned_hooks:
		print_error(str(hook) + " is not implemented and cannot be enabled. Terminating...")
		sys.exit(1)

hooks_to_enable = hooks_arg if hooks_arg else versioned_hooks

# make the versioned hooks executable and create symlinks to the hooks in the .git folder
for hook in hooks_to_enable:
	os.chmod("../../git-hooks/" + hook, os.stat("../../git-hooks/" + hook).st_mode | 0o111)
	subprocess.call(["ln", "-s", "-f", "../../git-hooks/" + hook, hook])

print_success("Successfully enabled the following git hooks: " + ", ".join(hooks_to_enable))
