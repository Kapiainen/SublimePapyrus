# API for accessing the core plugin of SublimePapyrus
import sublime, sublime_plugin, sys, os, threading, time
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
	# Cleaning up
	del root
	del module
	del coreModule
elif PYTHON_VERSION[0] >= 3:
	from SublimePapyrus import Plugin as SublimePapyrus
	from . import Linter

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

LINTER_CACHE = {}
COMPLETION_CACHE = {}
CACHE_LOCK = threading.RLock()
LEX = Linter.Lexical()
SYN = Linter.Syntactic()
SEM = Linter.Semantic()

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
		# Check if extension is .psc and in one of the import folders or the scripts folder
		#	Yes -> Check if the completions for script types needs to be updated
		pass

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
					scripts = moduleSettings.get("scripts", None)
					if scripts:
						sourcePaths.insert(0, scripts)
						lineNumber, columnNumber = view.rowcol(view.sel()[0].begin())
						lineNumber += 1
						scriptContents = view.substr(sublime.Region(0, view.size()))						
						args = None
						if PYTHON_VERSION[0] == 2:
							args = {"aView": None, "aLineNumber": lineNumber, "aSource": scriptContents, "aPaths": sourcePaths}
						elif PYTHON_VERSION[0] >= 3:
							args = {"aView": view, "aLineNumber": lineNumber, "aSource": scriptContents, "aPaths": sourcePaths}
						if args:
							t = threading.Timer(delay, self.RunLinter, kwargs=args)
							t.daemon = True
							t.start()

	def RunLinter(self, aView, aLineNumber, aSource, aPaths):
		self.linterQueue -= 1 # Remove from queue
		if self.linterQueue > 0: # If there is a queue, then cancel
			return
		elif self.completionRunning: # If completions are being generated, then cancel
			return
		self.linterRunning = True # Block further attempts to run the linter until this instance has finished
		start = time.time() #DEBUG
		def Run():
			print("Running linter")
			global LEX
			global SYN
			global SEM
			try:
				script = Linter.Process(LEX, SYN, SEM, aSource)
			except Linter.LexicalError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d, column %d: %s" % (e.line, e.column, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line, e.column)
				return False
			except Linter.SyntacticError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line)
				return False
			except Linter.SemanticError as e:
				print(e.message)
				if aView:
					SublimePapyrus.SetStatus(aView, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					SublimePapyrus.HighlightLinter(aView, e.line)
				return False
			return True

		if Run():
			if aView:
				SublimePapyrus.ClearStatus(aView, "sublimepapyrus-linter")
		print("Linter: Finished in %f milliseconds and releasing lock..." % ((time.time()-start)*1000.0)) #DEBUG
		self.linterRunning = False
