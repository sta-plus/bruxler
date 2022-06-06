import sys
import os

def read_file(filename):
	f = open(filename)
	data = f.read()
	f.close()
	return data

def minify(data, ignore_list=None):
	new_data = ""

	for i in data.split("\n"):
		if i.strip() == "" or i.strip().startswith("#") or i.strip().startswith("//"):
			continue

		if i.strip().startswith("donut(\"") and ignore_list != None:
			parsed_filename = i.split("donut(\"")[1].split("\")")[0]
			if parsed_filename in ignore_list:
				continue

		new_data += i.split("//")[0]
		new_data += "\n"
	
	return new_data

class Module:
	def __init__(self, filename, data):
		self.filename = filename
		self.data = data

def load_modules(directory, module):
	modules = []

	for i in module.data.split("\n"):
		if i.strip().startswith("donut(\""):
			parsed_filename = i.split("donut(\"")[1].split("\")")[0]
			try:
				dependency = Module(parsed_filename, read_file(directory + "/" + parsed_filename))
				modules = modules + load_modules(directory, dependency)
				modules.append(dependency)
			except:
				pass # Dynamic donut()

	return modules

def bundle(entrypoint_filename):
	entrypoint_module = Module(entrypoint_filename, read_file(entrypoint_filename))

	modules = load_modules(os.path.dirname(os.path.realpath(entrypoint_filename)), entrypoint_module)

	output_data = ""

	for i in modules:
		output_data += "// " + i.filename + "\n"
		output_data += minify(i.data)

	# Entrypoint data

	ignore_list = []

	for i in modules:
		ignore_list.append(i.filename)

	output_data += "// " + entrypoint_filename + "\n"
	output_data += minify(entrypoint_module.data, ignore_list=ignore_list)

	return output_data

if __name__ == "__main__":
	print(bundle(sys.argv[1]))