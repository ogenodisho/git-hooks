#!/usr/bin/env python
import re
import datetime
import javalang

api_pattern = re.compile("(api|spi)_\d+_\d+")

def validate_java_file(java_file):
	"""Validates a java file.

	Args:
		java_file_path: the path to the java file.
	Returns:
		a list of errors.
	"""

	file_status, java_file_path = java_file

	with open(java_file_path, "r") as fp:
		contents = fp.read()

	if not contents:
		return ["[ERROR] Errors exist in " + java_file_path, "\t- File is empty"]

	try:
		tree = javalang.parse.parse(contents)
	except javalang.parser.JavaSyntaxError:
		print("Javalang failed to parse '%s'. Skipping file..." % java_file_path)
		return []

	errors = []

	is_api = tree.package and api_pattern.search(tree.package.name) is not None
	for path, class_declaration in tree.filter(javalang.tree.ClassDeclaration):
		is_osgi = "OsgiServiceImpl" in [annotation.name for annotation in class_declaration.annotations]
		errors.extend(validate_class(class_declaration, is_api, is_osgi))
	for path, interface_declaration in tree.filter(javalang.tree.InterfaceDeclaration):
		errors.extend(validate_interface(interface_declaration, is_api))
	for path, enum_declaration in tree.filter(javalang.tree.EnumDeclaration):
		errors.extend(validate_enum(enum_declaration, is_api))
	for path, import_declaration in tree.filter(javalang.tree.Import):
		errors.extend(validate_import(import_declaration))
	errors.extend(validate_print_statements(contents))
	if file_status == "A":
		errors.extend(validate_copyright_statement(contents))

	if errors:
		errors.insert(0, "[ERROR] Errors exist in " + java_file_path)

	return errors

def validate_class(class_declaration, is_api, is_osgi):
	errors = []
	if is_osgi:
		osgi_unsetters_by_setters = {}
		for method_declaration in class_declaration.methods:
			if "OsgiServiceReference" in [annotation.name for annotation in method_declaration.annotations]:
				osgi_unsetters_by_setters[method_declaration.name] = None
		for method_declaration in class_declaration.methods:
			for setter in osgi_unsetters_by_setters:
				# @OsgiServiceReference methods can start with 'set' or 'add'
				if method_declaration.name == "un" + setter or method_declaration.name == "remove" + setter:
					osgi_unsetters_by_setters[setter] = method_declaration.name
					break
		errors.extend(help_validate_osgi_class(class_declaration, osgi_unsetters_by_setters))

	if "public" in class_declaration.modifiers:
		if is_api and javadoc_is_missing(class_declaration):
			errors.append("\t- Public API class requires javadoc")
	for method in class_declaration.methods:
		# Overridden don't require javadoc
		if "Override" in [annotation.name for annotation in method.annotations]:
			continue
		# Osgi setters and unsetters don't require javadoc
		if is_osgi and method.name in osgi_unsetters_by_setters.keys() + osgi_unsetters_by_setters.values():
			continue
		if "public" in method.modifiers:
			if is_api and javadoc_is_missing(method):
				method_signature = get_method_signature(method)
				errors.append("\t- Public method '%s' in public API class requires javadoc" % method_signature)
	return errors

def validate_interface(interface_declaration, is_api):
	errors = []
	if is_api and javadoc_is_missing(interface_declaration):
		errors.append("\t- Public API interface requires javadoc")
	if "abstract" in interface_declaration.modifiers:
		errors.append("\t- Interface declaration contains the redundant 'abstract' modifier")
	for method in interface_declaration.methods:
		method_signature = get_method_signature(method)
		is_overridden = "Override" in [annotation.name for annotation in method.annotations]
		if not is_overridden and is_api and javadoc_is_missing(method):
			errors.append("\t- Public method '%s' in public API interface requires javadoc" % method_signature)
		if "public" in method.modifiers:
			errors.append("\t- Method '%s' contains the redundant 'public' modifier" % method_signature)
		if "abstract" in method.modifiers:
			errors.append("\t- Method '%s' contains the redundant 'abstract' modifier" % method_signature)
	for field in interface_declaration.fields:
		declarator_names = [declarator.name for declarator in field.declarators]
		if "public" in method.modifiers:
			errors.append("\t- Field '%s' contains the redundant 'public' modifier" % (", ".join(declarator_names)))
		if "static" in method.modifiers:
			errors.append("\t- Field '%s' contains the redundant 'static' modifier" % (", ".join(declarator_names)))
		if "final" in method.modifiers:
			errors.append("\t- Field '%s' contains the redundant 'final' modifier" % (", ".join(declarator_names)))
	return errors

def validate_enum(enum_declaration, is_api):
	errors = []
	if "public" in enum_declaration.modifiers:
		if is_api and javadoc_is_missing(enum_declaration):
			errors.append("\t- Public API enum requires javadoc")
	for enum_constant in enum_declaration.body.constants:
		if is_api and javadoc_is_missing(enum_constant):
			errors.append("\t- Public enum constant '%s' in public API enum requires javadoc" % enum_constant.name)
	return errors

def validate_import(import_declaration):
	errors = []
	if import_declaration.path.startswith("edu.emory.mathcs.backport.java.util"):
		errors.append("\t- Are you sure you want to be importing something from 'edu.emory' and not 'java.util'? If so, bypass the git hooks!")
	return errors

def validate_print_statements(contents):
	errors = []
	if "System.out.print" in contents:
		errors.append("\t- Print statement found")
	return errors

def validate_copyright_statement(contents):
	if not contents.strip().startswith("/*"):
		return ["\t- Java files must start with a copyright notice."]

	copyright_notice = contents[:contents.index("*/") + 2]
	copyright_end_date = re.search(r"(\d+) - (\d+)", copyright_notice).group(2)
	if int(copyright_end_date) != datetime.datetime.now().year:
		return ["\t- Copyright end date should be '%s'" % datetime.datetime.now().year]
	return []

def help_validate_osgi_class(class_declaration, osgi_unsetters_by_setters):
	errors = []

	has_declared_activator = False
	has_declared_deactivator = False
	for method_declaration in class_declaration.methods:
		if method_declaration.name == "activate" and "protected" in method_declaration.modifiers:
			has_declared_activator = True
		if method_declaration.name == "deactivate" and "protected" in method_declaration.modifiers:
			has_declared_deactivator = True
		if method_declaration.name in osgi_unsetters_by_setters.keys() + osgi_unsetters_by_setters.values():
			if "protected" not in method_declaration.modifiers:
				errors.append("\t- @OsgiServiceReference method '%s' must be declared with the 'protected' visibility modifier" % method_declaration.name)
	if class_declaration.name.endswith("Activator") and not has_declared_activator:
		errors.append("\t- OSGi service activator classes must declare a protected activate method")
	if class_declaration.name.endswith("Activator") and not has_declared_deactivator:
		errors.append("\t- OSGi service activator classes must declare a protected deactivate method")

	for setter in osgi_unsetters_by_setters:
		if osgi_unsetters_by_setters[setter] is None:
			errors.append("\t- @OsgiServiceReference set/unset method '%s' does not have a corresponding unset/remove" % setter)
	return errors

def javadoc_is_missing(declaration):
	if declaration.documentation is None:
		return True
	javadoc = "".join(declaration.documentation.split()) # get rid of all whitespace
	return javadoc.replace("/", "").replace("*", "") == ""

def get_method_signature(method):
	param_types = [param.type.name for param in method.parameters]
	return method.name + "(" + ", ".join(param_types) + ")"
