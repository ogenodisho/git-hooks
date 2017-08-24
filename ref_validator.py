import subprocess
import sys
import os
from optparse import OptionParser
from utils import print_error, print_success, get_validation_errors_in_files, ref_exists

empty_tree_sha1 = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def validate_files(f):
	print_success("Validating the following files:\n\t%s" % "\n\t".join(f))

	os.chdir("..")

	errors = get_validation_errors_in_files(f)

	if errors:
		print_error("\n".join(errors))

	print_success("Done :)")

def validate_repo(ref_1, ref_2="master"):
	print_success("Validating %s against %s" % (ref_1, ref_2))

	diff_output = subprocess.check_output(["git", "diff", "--name-status", ref_1, ref_2], universal_newlines=True)

	all_files = [ f.split("\t") for f in diff_output.split("\n") if f ]

	os.chdir("..")

	errors = get_validation_errors_in_files(all_files)

	if errors:
		print_error("\n".join(errors))

	print_success("Done :)")

if __name__ == "__main__":
	parser = OptionParser(usage="python %s <ref_1> [ref_2] OR python %s --file <list of absolute file paths>" % (__file__, __file__))
	description_lines = ["Validates the diff between two refs (tags, commits, branches) or validates a collection of files using the --file option",
		"When one ref is provided - it will be validated against the master ref.\n\
		NOTE: If the provided ref is the master ref, it will be validated against the empty tree ref.",
		"When two refs are provided - they will be validated against eachother"]
	parser.set_description("\n\t- ".join(description_lines))
	parser.format_description = lambda _: parser.description
	parser.add_option("-f", "--file", action="store_true", dest="file_validation", help="Validate a collection of files")

	(options, args) = parser.parse_args()

	if len(args) == 0:
		parser.print_help()
		sys.exit(1)
	elif options.file_validation:
		validate_files(args)
	elif len(args) == 1:
		ref = args[0]
		if not ref_exists(ref):
			print_error("'%s' ref does not exist" % ref)
			sys.exit(1)
		if ref.endswith("master"):
			validate_repo(ref, empty_tree_sha1)
		else:
			validate_repo(ref)
	elif len(args) == 2:
		ref_1, ref_2 = args[0], args[1]
		if not ref_exists(ref_1):
			print_error("'%s' ref does not exist" % ref_1)
			sys.exit(1)
		elif not ref_exists(ref_2):
			print_error("'%s' ref does not exist" % ref_2)
			sys.exit(1)
		validate_repo(ref_1, ref_2)
	else:
		print_error("You must provide at most 2 arguments representing refs to be validated. Run with --help for help.")
		sys.exit(1)
