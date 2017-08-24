#!/usr/bin/env python
import re

def validate_javascript_file(javascript_file):
	"""Validates a javascript file.

	Args:
		javascript_file_path: the path to the javascript file.
	Returns:
		a list of errors.
	"""

	file_status, javascript_file_path = javascript_file

	with open(javascript_file_path, "r") as fp:
		contents = fp.read()

	if not contents:
		return ["[ERROR] Errors exist in " + javascript_file_path, "\t- File is empty"]

	if re.search("(\s+|;)debugger;*\s+", " %s " % contents, flags=re.MULTILINE) is not None:
		return ["[ERROR] Errors exist in " + javascript_file_path, "\t- Remove the debugger keyword before you commit"]

	return []
