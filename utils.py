#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import subprocess
import json
import jsonschema
from file_validators import *

git_hooks = ["applypatch-msg", "pre-applypatch", "pre-rebase", "commit-msg",
			"pre-commit", "prepare-commit-msg", "post-update", "pre-push", "update"]
versioned_hooks = [f for f in os.listdir(".") if f in git_hooks]

is_terminal = True
for key in os.environ:
	if "SourceTree" in os.environ[key] or "SmartGit" in os.environ[key]:
		is_terminal = False
		break;

is_windows = sys.platform == "win32"

is_python3 = sys.version_info >= (3, 0)

def get_validation_errors_in_files(files):
	"""Validates a list of files using the file validators.

	Args:
		files: the list of files to be validated
	Returns:
		a list of all errors
	"""

	errors = []

	# validate changed files that have validators
	for f in files:
		path = f[1]
		if not os.path.isfile(path):
			print_error("Could not find file '%s'" % path)
			continue
		if path.endswith(".java") and validation_enabled(".java") and not is_in_test_directory(path):
			errors.extend(java_file_validator.validate_java_file(f))
		elif path.endswith(".js") and validation_enabled(".js"):
			errors.extend(javascript_file_validator.validate_javascript_file(f))
		elif path.endswith(".json") and validation_enabled(".json"):
			errors.extend(json_file_validator.validate_json_file(f))
		elif path.endswith(".xml") and validation_enabled(".xml"):
			errors.extend(xml_file_validator.validate_xml_file(f))
		elif path.endswith(".feature") and validation_enabled(".feature"):
			errors.extend(feature_file_validator.validate_feature_file(f, get_config()["file_validation"][".feature"]["unallowed_annotations"]))

	return errors

def is_in_test_directory(path):
	for test_directory in get_config()["test_directories"]:
		if path.startswith(test_directory):
			return True
	return False

def validation_enabled(file_extension):
	return get_config()["file_validation"][file_extension]["validate"]

def print_error(message):
	if is_terminal and not is_windows:
		print("\033[31m" + message + "\033[0m") # make error messages red
	else:
		print(message)

def print_success(message):
	if is_terminal and not is_windows:
		print("\033[92m" + message + "\033[0m") # make success messages green
	else:
		print(message)

def get_author_first_name():
	user_name = subprocess.check_output(["git", "config", "user.name"], universal_newlines=True)
	# return with a prepending space so sentences make sense without a name too
	return " " + user_name.split()[0]

def ref_exists(ref):
	"""Checks if a git ref exists or not using git show.

	Args:
		ref: the ref to be checked
	Returns: True if the ref exists, false otherwise
	"""

	try:
		subprocess.check_output(["git", "show", ref], universal_newlines=True)
	except subprocess.CalledProcessError:
		return False
	return True

def get_config():
	if not os.path.isfile("./git-hooks-config.json"):
		print_error("You must have a file named 'git-hooks-config.json' one level outside of your git-hooks submodule directory.")
		sys.exit(1)
	config_schema = json.load(open("./git-hooks/config-schema.json"))
	with open("./git-hooks-config.json") as user_config_file:
		try:
			user_config = json.load(user_config_file)
			if not user_config:
				print_error("'git-hooks-config.json' is empty!")
				sys.exit(1)
			jsonschema.validate(user_config, config_schema)
		except (ValueError, jsonschema.exceptions.ValidationError) as ve:
			print_error(ve.message)
			print_error("Ensure that your 'git-hooks-config.json' file adheres to the schema provided in the git-hooks submodule.")
			sys.exit(1)
		return user_config

if __name__ == '__main__':
	get_config()
