# API for accessing the core plugin of SublimePapyrus
import sublime, sublime_plugin, sys, os
PYTHON_VERSION = sys.version_info
SUBLIME_VERSION = None
if PYTHON_VERSION[0] == 2:
	SUBLIME_VERSION = int(sublime.version())
	import imp
	root, module = os.path.split(os.getcwd())
	coreModule = "SublimePapyrus"
	# SublimePapyrus core module
	mainPackage = os.path.join(root, coreModule, "Plugin.py")
	imp.load_source("SublimePapyrus", mainPackage)
	del mainPackage
	import SublimePapyrus
	# Cleaning up
	del root
	del module
	del coreModule
elif PYTHON_VERSION[0] >= 3:
	from SublimePapyrus import Plugin as SublimePapyrus

VALID_SCOPE = "source.papyrus.fallout4"

def plugin_loaded():
	global SUBLIME_VERSION
	SUBLIME_VERSION = int(sublime.version())

class SublimePapyrusFallout4CompileScriptCommand(sublime_plugin.WindowCommand):
	def run(self, **args):
		print(args)
		settings = SublimePapyrus.GetSettings()
		if not settings:
			return SublimePapyrus.ShowMessage("No settings.")
		modules = settings.get("modules", None)
		if not modules:
			return SublimePapyrus.ShowMessage("No modules.")
		moduleSettings = modules.get("fallout4", None)
		if not moduleSettings:
			return SublimePapyrus.ShowMessage("No Fallout 4 module settings.")
		scriptsPath = moduleSettings.get("scripts", None)
		if not scriptsPath:
			return SublimePapyrus.ShowMessage("No scripts path.")
		if scriptsPath[-1:] == "\\":
			scriptsPath = scriptsPath[:-1]
		if not scriptsPath in args["cmd"]:
			return SublimePapyrus.ShowMessage("Compilation target not in scripts path.")
		compilerPath = moduleSettings.get("compiler", None)
		if not compilerPath:
			return SublimePapyrus.ShowMessage("No compiler path.")
		flags = moduleSettings.get("flags", None)
		if not flags:
			return SublimePapyrus.ShowMessage("No flags file.")
		outputPath = moduleSettings.get("output", None)
		if not outputPath:
			return SublimePapyrus.ShowMessage("No output path.")
		importPaths = moduleSettings.get("import", None)
		if not importPaths:
			return SublimePapyrus.ShowMessage("No import paths.")
		if not scriptsPath in importPaths:
			importPaths.insert(0, scriptsPath)
		arguments = moduleSettings.get("arguments", None)
		if arguments:
			temp = []
			for a in arguments:
				if a[0] != "-":
					temp.append("-%s" % a)
				else:
					temp.append(a)
			arguments = temp

		mode = args["mode"]
		if not mode:
			return SublimePapyrus.ShowMessage("No build mode.")
		target = None
		if mode == "debug" or mode == "release" or mode == "final":
			target = args["cmd"][len(scriptsPath)+1:]
		elif mode == "batch" or mode == "batchrecursive":
			target = scriptsPath
		else:
			return SublimePapyrus.ShowMessage("Unknown build mode.")
		if not target:
			return SublimePapyrus.ShowMessage("No compilation target.")
		if mode == "debug":
			pass
		elif mode == "release":
			if arguments:
				arguments.append("-release")
			else:
				arguments = ["-release"]
		elif mode == "final":
			if arguments:
				arguments.append("-final")
			else:
				arguments = ["-final"]
		elif mode == "batch":
			if arguments:
				arguments.append("-all")
				arguments.append("-norecurse")
			else:
				arguments = ["-all", "-norecurse"]
		elif mode == "batchrecursive":
			if arguments:
				arguments.append("-all")
			else:
				arguments = ["-all"]
		args = {"cmd": "\"%s\" \"%s\" -i=\"%s\" -o=\"%s\" -f=\"%s\" %s" % (compilerPath, target, ";".join(importPaths), outputPath, flags, " ".join(arguments)), "file_regex": args["file_regex"]}
		self.window.run_command("exec", args)
		return