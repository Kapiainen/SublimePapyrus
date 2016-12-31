import sublime, sublime_plugin, sys, os
PLATFORM_WINDOWS = os.name == "nt"
PYTHON_VERSION = sys.version_info
SUBLIME_VERSION = None
if PYTHON_VERSION[0] == 2:
	SUBLIME_VERSION = int(sublime.version())
	import imp
	ROOT, MODULE = os.path.split(os.getcwd())
	CORE_MODULE = "SublimePapyrus"
	# SublimePapyrus core module
	MAIN_PACKAGE = os.path.join(ROOT, CORE_MODULE, "Plugin.py")
	imp.load_source("SublimePapyrus", MAIN_PACKAGE)
	del MAIN_PACKAGE
	import SublimePapyrus
	# Cleaning up
	del ROOT
	del MODULE
	del CORE_MODULE
elif PYTHON_VERSION[0] >= 3:
	from SublimePapyrus import Plugin as SublimePapyrus

VALID_SCOPE = "source.papyrus.fallout4"

def plugin_loaded():
	global SUBLIME_VERSION
	SUBLIME_VERSION = int(sublime.version())

class SublimePapyrusFallout4CompileScriptCommand(sublime_plugin.WindowCommand):
	def run(self, **args):
		# Get user settings for Fallout 4
		settings = SublimePapyrus.GetSettings()
		if not settings:
			return SublimePapyrus.ShowMessage("No settings.")
		modules = settings.get("modules", None)
		if not modules:
			return SublimePapyrus.ShowMessage("No modules.")
		module_settings = modules.get("fallout4", None)
		if not module_settings:
			return SublimePapyrus.ShowMessage("No Fallout 4 module settings.")
		compiler_path = module_settings.get("compiler", None)
		if not compiler_path:
			return SublimePapyrus.ShowMessage("No compiler path.")
		flags = module_settings.get("flags", None)
		if not flags:
			return SublimePapyrus.ShowMessage("No flags file.")
		output_path = module_settings.get("output", None)
		if not output_path:
			return SublimePapyrus.ShowMessage("No output path.")
		import_paths = module_settings.get("import", None)
		if not import_paths:
			return SublimePapyrus.ShowMessage("No import paths.")

		# Arguments in the user settings
		arguments = module_settings.get("arguments", None)
		if arguments:
			if not isinstance(arguments, list):
				return SublimePapyrus.ShowMessage("The 'arguments' setting is expected to be a list of strings.")
			temp = []
			for argument_ in arguments:
				temp.append(argument_)
			arguments = temp

		# Build mode (debug, release, etc.)
		mode = args["mode"]
		if not mode:
			return SublimePapyrus.ShowMessage("No build mode.")
		target = None
		if mode.startswith("caprica_"):
			if mode == "caprica_debug" or mode == "caprica_release" or mode == "caprica_final": # Single file
				# Absolute path to the script source
				target = args["cmd"]
				# Modify output path so that the compiled script goes into the right namespace (i.e. subfolder)
				path_1 = args["cmd"].replace("/", "\\").lower()
				path_2 = import_paths[0].replace("/", "\\").lower()
				common_prefix = os.path.commonprefix([path_1, path_2])
				if not common_prefix:
					return SublimePapyrus.ShowMessage("Script is not in the first import folder.")
				relative_path = os.path.relpath(path_1, common_prefix)
				namespace, tail = os.path.split(args["cmd"].replace("/", "\\")[-len(relative_path):])
				output_path = os.path.join(output_path, namespace)
			else:
				return SublimePapyrus.ShowMessage("Unsupported build mode.")
			if mode == "caprica_release":
				arguments.append("--release")
			elif mode == "caprica_final":
				arguments.append("--final")
			args = {"cmd": "\"%s\" \"%s\" -i \"%s\" -o \"%s\" %s" % (compiler_path, target, "\" -i \"".join(import_paths), output_path, " ".join(arguments)), "file_regex": args["file_regex"]}
		else:
			if mode == "debug" or mode == "release" or mode == "final": # Single file
				# Get the path to the script source relative to the first import path
				path_1 = args["cmd"].replace("/", "\\").lower()
				path_2 = import_paths[0].replace("/", "\\").lower()
				common_prefix = os.path.commonprefix([path_1, path_2])
				if not common_prefix:
					return SublimePapyrus.ShowMessage("Script is not in the first import folder.")
				relative_path = os.path.relpath(path_1, common_prefix)
				target = args["cmd"].replace("/", "\\")[-len(relative_path):]
			else:
				return SublimePapyrus.ShowMessage("Unsupported build mode.")
			if mode == "release":
				if arguments:
					arguments.append("-release")
				else:
					arguments = ["-release"]
			elif mode == "final":
				if arguments:
					arguments.append("-final")
				else:
					arguments = ["-final"]
			args = {"cmd": "\"%s\" \"%s\" -i=\"%s\" -o=\"%s\" -f=\"%s\" %s" % (compiler_path, target, "\";\"".join(import_paths), output_path, flags, " ".join(arguments)), "file_regex": args["file_regex"]}
		if not target:
			return SublimePapyrus.ShowMessage("No compilation target.")

		# Run the compiler
		self.window.run_command("exec", args)
		return
