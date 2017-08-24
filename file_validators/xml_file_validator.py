#!/usr/bin/env python
from xml.etree import ElementTree as ET

def validate_xml_file(xml_file):
	"""Validates the syntax of an XML file.

	Args:
		xml_file_path: the path to the XML file.
	Returns:
		a list of errors.
	"""

	file_status, xml_file_path = xml_file

	with open(xml_file_path, "r") as fp:
		contents = fp.read()

	try:
		ET.fromstring(contents)
	except Exception as e:
		return ["[ERROR] Errors exist in " + xml_file_path, "\t- Could not parse the file! " + str(e)]

	return []
