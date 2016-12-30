# API for accessing the core plugin of SublimePapyrus
import sublime, sublime_plugin, sys, os, threading, time
PLATFORM_WINDOWS = os.name == "nt"
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
	# Fallout 4 linter
	linterPackage = os.path.join(root, module, "Linter.py")
	imp.load_source("Linter", linterPackage)
	del linterPackage
	import Linter
	# Fallout 4 lexical analysis
	lexicalModule = os.path.join(root, module, "LexicalAnalysis.py")
	imp.load_source("LexicalAnalysis", lexicalModule)
	# Fallout 4 syntactic analysis
	syntacticModule = os.path.join(root, module, "SyntacticAnalysis.py")
	imp.load_source("SyntacticAnalysis", Module)
	# Fallout 4 semantic analysis
	semanticModule = os.path.join(root, module, "SemanticAnalysis.py")
	imp.load_source("SemanticAnalysis", semanticModule)
	import LexicalAnalysis
	import SyntacticAnalysis
	import SemanticAnalysis
	# Cleaning up
	del root
	del module
	del coreModule
	del lexicalModule
	del syntacticModule
	del semanticModule
elif PYTHON_VERSION[0] >= 3:
	from SublimePapyrus import Plugin as SublimePapyrus
	from . import Linter
	from . import LexicalAnalysis
	from . import SyntacticAnalysis
	from . import SemanticAnalysis

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
			temp = []
			for argument_ in arguments:
				if argument_[0] != "-":
					temp.append("-%s" % argument_)
				else:
					temp.append(argument_)
			arguments = temp

		# Build mode (debug, release, etc.)
		mode = args["mode"]
		if not mode:
			return SublimePapyrus.ShowMessage("No build mode.")
		target = None
		if mode == "debug" or mode == "release" or mode == "final": # Single file
			path_1 = args["cmd"].replace("\\", "/").lower()
			path_2 = import_paths[0].replace("\\", "/").lower()
			common_prefix = os.path.commonprefix([path_1, path_2])
			if not common_prefix:
				return SublimePapyrus.ShowMessage("Script is not in the first import folder.")
			relative_path = os.path.relpath(path_1, common_prefix)
			target = args["cmd"].replace("\\", "/")[-len(relative_path):]
		elif mode == "batch" or mode == "batchrecursive": # Batch
			return SublimePapyrus.ShowMessage("Batch build not currently supported")
		else:
			return SublimePapyrus.ShowMessage("Unsupported build mode.")
		if not target:
			return SublimePapyrus.ShowMessage("No compilation target.")

		# Arguments demanded by the build modes
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

		# Put all the arguments together and run the compiler
		args = {"cmd": "\"%s\" \"%s\" -i=\"%s\" -o=\"%s\" -f=\"%s\" %s" % (compiler_path, target, ";".join(import_paths), output_path, flags, " ".join(arguments)), "file_regex": args["file_regex"]}
		self.window.run_command("exec", args)
		return

#LINTER_CACHE = {}
#COMPLETION_CACHE = {}
#CACHE_LOCK = threading.RLock()
#LEX = Linter.Lexical()
#SYN = Linter.Syntactic()
#SEM = Linter.Semantic()

class EventListener(sublime_plugin.EventListener):
	def __init__(self):
		super(EventListener,self).__init__()
		self.valid_scope = "source.papyrus.fallout4"
		self.linter_queue = 0
		self.linter_errors = {}
		self.linter_running = False
		self.completion_running = False

	def IsValidScope(self, view):
		if self.valid_scope:
			return self.valid_scope in view.scope_name(0)
		return False

	def on_post_save(self, view):
		if self.IsValidScope(view):
			# Check if extension is .psc and in one of the import folders or the scripts folder
			#	Yes -> Check if the completions for script types needs to be updated
			print("\nSublimePapyrus - Fallout 4 - OnPostSave: %s" % view.file_name())
			script_contents = view.substr(sublime.Region(0, view.size()))
			try:
				script_name = Linter.GetScriptName(script_contents)
			except LexicalAnalysis.LexicalError as e:
				return
			except SyntacticAnalysis.SyntacticError as e:
				return
			if script_name:
				Linter.ClearCache(":".join(script_name).upper())
			else:
				return

			return
			region = view.find("^\s*scriptname_ns+([_a-z0-9:]+)\s", 0, sublime.IGNORECASE)
			if region:
				script_name = view.substr(region).trim()
				script_name = script_name[10:].trim()
				print("Script_name:", script_name, script_name.split(":"))
			else:
				print("Could not find Script_name.")

	def on_modified(self, view):
		if self.IsValidScope(view):
			settings = SublimePapyrus.GetSettings()
			print("Fallout 4 script modified")
			# Tooltips
			global SUBLIME_VERSION
			if SUBLIME_VERSION >= 3070 and settings.get("tooltip_function_parameters", True):
				if self.linter_running:
					return
				elif self.completion_running:
					return
			# Linter
			if settings and settings.get("linter_on_modified", True):
				self.QueueLinter(view)

	def QueueLinter(self, view):
		if self.linter_running: # If an instance of the linter is running, then cancel
			return
		self.linter_queue += 1 # Add to queue
		settings = SublimePapyrus.GetSettings()
		delay = 0.500
		if settings:
			delay = settings.get("linter_delay", 500)/1000.0
			if delay < 0.050:
				delay = 0.050
		self.buffer_id = view.buffer_id()
		if self.buffer_id:
			SublimePapyrus.ClearLinterHighlights(view)
			modules = settings.get("modules", None)
			if modules:
				module_settings = modules.get("fallout4", None)
				if module_settings:
					source_paths = SublimePapyrus.GetSourcePaths(view)
					#scripts = module_settings.get("scripts", None)
					#if scripts:
						#source_paths.insert(0, scripts)
					line_number, column_number = view.rowcol(view.sel()[0].begin())
					line_number += 1
					script_contents = view.substr(sublime.Region(0, view.size()))						
					args = None
					caprica = "fallout4.caprica" in view.scope_name(0)
					if PYTHON_VERSION[0] == 2:
						args = {"a_view": None, "a_line_number": line_number, "a_source": script_contents, "a_paths": source_paths, "a_caprica": caprica}
					elif PYTHON_VERSION[0] >= 3:
						args = {"a_view": view, "a_line_number": line_number, "a_source": script_contents, "a_paths": source_paths, "a_caprica": caprica}
					if args:
						t = threading.Timer(delay, self.RunLinter, kwargs=args)
						t.daemon = True
						t.start()

	def RunLinter(self, a_view, a_line_number, a_source, a_paths, a_caprica):
	# a_view: A sublime.View object, possibly has the value None
	# a_line_number: Line that contains the cursor as an int
	# a_source: Script to process as a string
	# a_paths: List of paths to import folders
	# a_caprica: True if Caprica extensions should be used, otherwise False
		self.linter_queue -= 1 # Remove from queue
		if self.linter_queue > 0: # If there is a queue, then cancel
			return
		elif self.completion_running: # If completions are being generated, then cancel
			return
		self.linter_running = True # Block further attempts to run the linter until this instance has finished
		start = time.time() #DEBUG
		def Run():
			print("Running linter")
			try:
				Linter.Process(a_source, a_paths, a_caprica)
			except LexicalAnalysis.LexicalError as e:
				print(e.message)
				if a_view:
					SublimePapyrus.SetStatus(a_view, "sublimepapyrus-linter", "Error on line %d, column %d: %s" % (e.line, e.column, e.message))
					SublimePapyrus.HighlightLinter(a_view, e.line, e.column)
				return False
			except SyntacticAnalysis.SyntacticError as e:
				print(e.message)
				if a_view:
					SublimePapyrus.SetStatus(a_view, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(a_view, e.line)
				return False
			except SemanticAnalysis.SemanticError as e:
				print(e.message)
				if a_view:
					SublimePapyrus.SetStatus(a_view, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(a_view, e.line)
				return False
			except SemanticAnalysis.RemoteError as e:
				print(e.message)
				if a_view:
					SublimePapyrus.SetStatus(a_view, "sublimepapyrus-linter", e.message)
					SublimePapyrus.HighlightLinter(a_view, e.line)
				return False
#			except Linter.MissingScript as e:
#				print(e.message)
#				if a_view:
#					SublimePapyrus.SetStatus(a_view, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
#					SublimePapyrus.HighlightLinter(a_view, e.line)
#				return False
			return True

		if Run():
			if a_view:
				SublimePapyrus.ClearStatus(a_view, "sublimepapyrus-linter")
		print("Linter: Finished in %f milliseconds and releasing lock..." % ((time.time()-start)*1000.0)) #DEBUG
		self.linter_running = False
