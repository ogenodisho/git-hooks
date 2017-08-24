#!/usr/bin/env python
import json

def validate_json_file(json_file):
	"""Validates the syntax of a json file.

	Args:
		json_file_path: the path to the json file.
	Returns:
		a list of errors.
	"""

	file_status, json_file_path = json_file

	with open(json_file_path, "r") as fp:
		try:
			json.load(fp)
		except ValueError as e:
			return ["[ERROR] Errors exist in " + json_file_path, "\t- Could not parse the file! " + str(e)]

	return []
