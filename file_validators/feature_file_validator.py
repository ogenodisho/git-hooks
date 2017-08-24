#!/usr/bin/env python
from gherkin.token_scanner import TokenScanner
from gherkin.parser import Parser

def validate_feature_file(feature_file, unallowed_tags):
	"""Validates a feature file.

	Args:
		feature_file_path: the path to the feature file.
	Returns:
		a list of errors.
	"""

	file_status, feature_file_path = feature_file

	with open(feature_file_path, "r") as fp:
		contents = fp.read()

	parser = Parser()
	try:
		feature_file = parser.parse(TokenScanner(contents))
	except Exception as e:
		return ["[ERROR] Errors exist in " + feature_file_path, "\t- Could not parse the file! " + str(e)]

	errors = []
	feature_tag_names = [tag["name"] for tag in feature_file["feature"]["tags"]]
	scenarios = [feature_child for feature_child in feature_file["feature"]["children"] if feature_child['type'] == 'Scenario' or feature_child['type'] == 'ScenarioOutline']

	# validate tags in the feature
	for unallowed_tag in set(unallowed_tags).intersection(feature_tag_names):
		errors.append("\t- Remove the %s tag from the feature before you commit" % unallowed_tag)

	# validate tags in all the scenarios
	for scenario in scenarios:
		for tag in scenario["tags"]:
			if tag["name"] in unallowed_tags:
				errors.append("\t- Before you commit, remove the %s tag from the following scenario:\n\t\t'%s'" % (tag["name"], scenario["name"]))

	# validate scenario numbers
	prev_scenario_num = "0"
	for curr_scenario in scenarios:
		# validate prescence
		if "." not in curr_scenario["name"]:
			errors.append("\t- The following scenario needs to start with a number followed by a period: '%s'" % curr_scenario["name"])
			break
		curr_scenario_num = curr_scenario["name"].split(".")[0].strip()
		if not curr_scenario_num or curr_scenario_num.isalpha():
			errors.append("\t- The following scenario needs to start with a number: '%s'" % curr_scenario["name"])
			break
		# validate ordering
		if prev_scenario_num.isdigit():
			# previous scenario didn't have a letter
			if curr_scenario_num.isdigit():
				# current scenario doesn't have a letter
				if int(curr_scenario_num) != int(prev_scenario_num) + 1:
					errors.append("\t- The ordering of the scenarios breaks down on Scenario '%s'" % curr_scenario_num)
					break
			else:
				# current scenario has a letter
				if curr_scenario_num[-1] != "a":
					errors.append("\t- The ordering of the scenarios breaks down on Scenario '%s'" % curr_scenario_num)
					break
		else:
			# previous scenario had a letter
			prev_scenario_letter = prev_scenario_num[-1]
			if curr_scenario_num.isdigit():
				# current scenario doesn't have a letter
				if int(curr_scenario_num) != int(prev_scenario_num[:-1]) + 1:
					if ord(curr_scenario_num[-1]) != ord(prev_scenario_letter) + 1:
						errors.append("\t- The ordering of the scenarios breaks down on Scenario '%s'" % curr_scenario_num)
						break
			else:
				# current scenario has a letter
				if int(curr_scenario_num[:-1]) != int(prev_scenario_num[:-1]) + 1:
					# number has not been incremented
					if ord(curr_scenario_num[-1]) != ord(prev_scenario_letter) + 1:
						errors.append("\t- The ordering of the scenarios breaks down on Scenario '%s'" % curr_scenario_num)
						break
				else:
					# number has been incremented
					if curr_scenario_num[-1] != "a":
						errors.append("\t- The ordering of the scenarios breaks down on Scenario '%s'" % curr_scenario_num)
						break
		prev_scenario_num = curr_scenario_num

	if errors:
		errors.insert(0, "[ERROR] Errors exist in " + feature_file_path)

	return errors
