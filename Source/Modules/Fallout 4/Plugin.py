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
		self.validScope = "source.papyrus.fallout4"
		self.linterQueue = 0
		self.linterErrors = {}
		self.linterRunning = False
		self.completionRunning = False

	def IsValidScope(self, view):
		if self.validScope:
			return self.validScope in view.scope_name(0)
		return False

	def on_post_save(self, view):
		if self.IsValidScope(view):
			# Check if extension is .psc and in one of the import folders or the scripts folder
			#	Yes -> Check if the completions for script types needs to be updated
			print("\nSublimePapyrus - Fallout 4 - OnPostSave: %s" % view.file_name())
			scriptContents = view.substr(sublime.Region(0, view.size()))
			try:
				scriptName = Linter.GetScriptName(scriptContents)
			except LexicalAnalysis.LexicalError as e:
				return
			except SyntacticAnalysis.SyntacticError as e:
				return
			if scriptName:
				Linter.ClearCache(":".join(scriptName).upper())
			else:
				return

			return
			region = view.find("^\s*scriptname\s+([_a-z0-9:]+)\s", 0, sublime.IGNORECASE)
			if region:
				scriptName = view.substr(region).trim()
				scriptName = scriptName[10:].trim()
				print("ScriptName:", scriptName, scriptName.split(":"))
			else:
				print("Could not find ScriptName.")

	def on_modified(self, view):
		if self.IsValidScope(view):
			settings = SublimePapyrus.GetSettings()
			print("Fallout 4 script modified")
			# Tooltips
			global SUBLIME_VERSION
			if SUBLIME_VERSION >= 3070 and settings.get("tooltip_function_parameters", True):
				if self.linterRunning:
					return
				elif self.completionRunning:
					return
			# Linter
			if settings and settings.get("linter_on_modified", True):
				self.QueueLinter(view)

	def QueueLinter(self, view):
		if self.linterRunning: # If an instance of the linter is running, then cancel
			return
		self.linterQueue += 1 # Add to queue
		settings = SublimePapyrus.GetSettings()
		delay = 0.500
		if settings:
			delay = settings.get("linter_delay", 500)/1000.0
			if delay < 0.050:
				delay = 0.050
		self.bufferID = view.buffer_id()
		if self.bufferID:
			SublimePapyrus.ClearLinterHighlights(view)
			modules = settings.get("modules", None)
			if modules:
				moduleSettings = modules.get("fallout4", None)
				if moduleSettings:
					sourcePaths = SublimePapyrus.GetSourcePaths(view)
					#scripts = moduleSettings.get("scripts", None)
					#if scripts:
						#sourcePaths.insert(0, scripts)
					lineNumber, columnNumber = view.rowcol(view.sel()[0].begin())
					lineNumber += 1
					scriptContents = view.substr(sublime.Region(0, view.size()))						
					args = None
					caprica = "fallout4.caprica" in view.scope_name(0)
					if PYTHON_VERSION[0] == 2:
						args = {"aView": None, "aLineNumber": lineNumber, "aSource": scriptContents, "aPaths": sourcePaths, "aCaprica": caprica}
					elif PYTHON_VERSION[0] >= 3:
						args = {"aView": view, "aLineNumber": lineNumber, "aSource": scriptContents, "aPaths": sourcePaths, "aCaprica": caprica}
					if args:
						t = threading.Timer(delay, self.RunLinter, kwargs=args)
						t.daemon = True
						t.start()

	def RunLinter(self, aView, aLineNumber, aSource, aPaths, aCaprica):
	# aView: A sublime.View object, possibly has the value None
	# aLineNumber: Line that contains the cursor as an int
	# aSource: Script to process as a string
	# aPaths: List of paths to import folders
	# aCaprica: True if Caprica extensions should be used, otherwise False
		self.linterQueue -= 1 # Remove from queue
		if self.linterQueue > 0: # If there is a queue, then cancel
			return
		elif self.completionRunning: # If completions are being generated, then cancel
			return
		self.linterRunning = True # Block further attempts to run the linter until this instance has finished
		start = time.time() #DEBUG
		def Run():
			print("Running linter")
			try:
				Linter.Process(aSource, aPaths, aCaprica)
			except LexicalAnalysis.LexicalError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d, column %d: %s" % (e.line, e.column, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line, e.column)
				return False
			except SyntacticAnalysis.SyntacticError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line)
				return False
			except SemanticAnalysis.SemanticError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line)
				return False
			except SemanticAnalysis.RemoteError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", e.message)
					SublimePapyrus.HighlightLinter(aView, e.line)
				return False
#			except Linter.MissingScript as e:
#				print(e.message)
#				if aView:
#					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
#					SublimePapyrus.HighlightLinter(aView, e.line)
#				return False
			return True

#			global LEX
#			global SYN
#			global SEM
#			try:
#				script = SEM.Process(LEX, SYN, aSource, aPaths)
#			except Linter.LexicalError as e:
#				print(e.message)
#				if aView:
#					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d, column %d: %s" % (e.line, e.column, e.message))
#					SublimePapyrus.HighlightLinter(aView, e.line, e.column)
#				return False
#			except Linter.SyntacticError as e:
#				print(e.message)
#				if aView:
#					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
#					SublimePapyrus.HighlightLinter(aView, e.line)
#				return False
#			except Linter.SemanticError as e:
#				print(e.message)
#				if aView:
#					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
#					SublimePapyrus.HighlightLinter(aView, e.line)
#				return False
#			except Linter.MissingScript as e:
#				print(e.message)
#				if aView:
#					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
#					SublimePapyrus.HighlightLinter(aView, e.line)
#				return False
#			#except Exception as e:
#			#	print("SublimePapyrus - Fallout 4 - %s" % e)
#			#	if aView:
#			#		SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Fallout 4 - %s" % e)
#			return True

		if Run():
			if aView:
				SublimePapyrus.ClearStatus(aView, "sublimepapyrus-linter")
		print("Linter: Finished in %f milliseconds and releasing lock..." % ((time.time()-start)*1000.0)) #DEBUG
		self.linterRunning = False
