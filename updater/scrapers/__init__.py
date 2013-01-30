import inspect, os, sys

my_path = os.path.dirname(inspect.getfile(inspect.currentframe()))

def _import_module_into_scope(modulename):
	module = __import__(modulename)
	
	for name in vars(module):
		data = getattr(module, name)
		globals()[name] = data

sys.path.insert(0, my_path)

for fname in os.listdir(my_path):
	fpath = os.path.join(my_path, fname)
	fbasename, fext = os.path.splitext(fname)
	
	if os.path.isdir(fpath):
		if os.path.isfile(os.path.join(my_path, fname, "__init__.py")):
			# This is a python directory module
			_import_module_into_scope(fname)
	elif os.path.isfile(fpath) and fext == ".py" and fbasename != "__init__":
		# This is a python file module
		_import_module_into_scope(fbasename)

sys.path.remove(my_path)
