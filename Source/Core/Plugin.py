# ST2 uses Python 2.6 and ST3 uses Python 3.3.
import sublime, sublime_plugin, re, os, threading, sys, time
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
	import imp
	root, module = os.path.split(os.getcwd())
	# Build system
	buildPackage = os.path.join(root, "Default", "exec.py")
	imp.load_source("BUILD_SYSTEM", buildPackage)
	del buildPackage
	import BUILD_SYSTEM
elif PYTHON_VERSION[0] >= 3:
	import importlib
	BUILD_SYSTEM = importlib.import_module("Default.exec")

# ST3's API is ready to be used.
#def plugin_loaded():
#	global USER_SETTINGS
#	USER_SETTINGS = sublime.load_settings('SublimePapyrus.sublime-settings')

def GetSettings():
	settings = sublime.load_settings('SublimePapyrus.sublime-settings')
	if settings:
		return settings
	else:
		ShowMessage("Could not load settings...")
		return None

def ShowMessage(message):
	sublime.status_message("SublimePapyrus - %s" % message)

ERROR_HIGHLIGHT_KEY = "sublime_papyrus_error"
ERROR_HIGHLIGHT_SCOPE = "invalid"

def ClearHighlights(view, key):
	view.erase_regions(key)

def ClearLinterHighlights(view):
	ClearHighlights(view, ERROR_HIGHLIGHT_KEY)

def HighlightLinter(view, line, column = None):
	Highlight(view, ERROR_HIGHLIGHT_KEY, ERROR_HIGHLIGHT_SCOPE, line, column)

def Highlight(view, key, scope, line, column = None):
	if view and line:
		regions = view.get_regions(key) #[]
		if column: # Highlight a word
			point = view.text_point(line-1, column)
			regions.append(view.word(sublime.Region(point)))
		else: # Highlight a line
			point = view.text_point(line-1, 0)
			regions.append(view.line(sublime.Region(point)))
		if len(regions) > 0:
			view.add_regions(key, regions, scope)
			settings = GetSettings()
			if settings:
				if settings.get("center_highlighted_line", True):
					view.show_at_center(regions[0])

def GetSourcePaths(view):
	if not view:
		return None
	match = re.search("source\.papyrus\.(\w+).*", view.scope_name(0), re.IGNORECASE)
	if match:
		module = match.group(1)
		settings = GetSettings()
		if settings:
			modules = settings.get("modules", None)
			if modules:
				moduleSettings = modules.get(module, None)
				if moduleSettings:
					paths = moduleSettings.get("import", None)
					if paths:
						fullPath = view.file_name()
						if fullPath:
							folderPath, fileName = os.path.split(fullPath)
							paths.insert(0, folderPath)
						return paths
					else:
						ShowMessage("Could not find import paths for %s." % module.capitalize())
				else:
					ShowMessage("Could not find settings for %s." % module.capitalize())
			else:
				ShowMessage("Could not find settings for any modules.")
	else:
		ShowMessage("SublimePapyrus: Unsupported syntax definition.")

class SublimePapyrusFileSelectionPanelCommand(sublime_plugin.WindowCommand):
	def run(self, **args):
		items = args["items"]
		if items:
			self.items = items
			if PYTHON_VERSION[0] == 2:
				self.window.show_quick_panel(items, self.on_select, 0, -1)
			elif PYTHON_VERSION[0] >= 3:
				self.window.show_quick_panel(items, self.on_select, 0, -1, None)

	def on_select(self, index):
		if index >= 0:
			self.window.open_file(self.items[index])

# Base class that is used in the framework for showing a list of valid arguments and then inserting them.
# Libraries that need this functionality should import at least "sublime", "sublime_plugin", "sys", and this module.
# ST2 requires using the "imp" module to load this module first via the "load_source" function. ST3 can simply use "from SublimePapyrus import SublimePapyrus".
# Classes implementing this functionality need to inherit the "PapyrusShowSuggestionsCommand" class and override the "get_items" method.
# "get_items" should return a dictionary where the keys are the descriptions shown to the user and the values are what is inserted into the buffer.
class SublimePapyrusShowSuggestionsCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		selections = self.view.sel()
		if selections != None and len(selections) == 1:
			region = selections[0]
			self.argument = region
		items = self.get_items()
		if items != None:
			sortedKeysAndValues = sorted(zip(list(items.keys()), list(items.values())))
			sortedKeys = [[key, str(value)] for (key, value) in sortedKeysAndValues]
			sortedValues = [value for (key, value) in sortedKeysAndValues]
			self.items = sortedKeys
			self.values = sortedValues
			if PYTHON_VERSION[0] == 2:
				self.view.window().show_quick_panel(self.items, self.on_select, 0, -1)
			else:
				self.view.window().show_quick_panel(self.items, self.on_select, 0, -1, None)

	def get_items(self, **args):
		return None

	def on_select(self, index):
		if index >= 0:
			value = str(self.values[index])
			if value.isdigit() or value != "":
				args = {"region_start": self.argument.a, "region_end": self.argument.b, "replacement": value}
			else:
				args = {"region_start": self.argument.a, "region_end": self.argument.b, "replacement": str(self.items[index][0])}
			self.view.run_command("sublime_papyrus_insert_suggestion", args)

# Inserts the value chosen in the class that inherits "PapyrusShowSuggestionsCommand".
class SublimePapyrusInsertSuggestionCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		region = sublime.Region(args["region_start"], args["region_end"])
		self.view.erase(edit, region)
		if args["replacement"].isdigit():
			self.view.insert(edit, args["region_start"], args["replacement"])
		else:
			self.view.insert(edit, args["region_start"], "\"" + args["replacement"] + "\"")

class SublimePapyrusClearErrorHighlightsCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		if self.view:
			ClearLinterHighlights(self.view)

# Open a script based on input
class SublimePapyrusOpenScriptCommand(sublime_plugin.WindowCommand):
	def run(self):
		text = ""
		view = self.window.active_view()
		self.view = view
		if view:
			for region in view.sel():
				text = view.substr(region)
				break
			self.window.show_input_panel("Open script:", text, self.on_done, None, None)

	def on_done(self, text):
		if not text or not self.view:
			return
		if PYTHON_VERSION[0] == 2:
			self.get_matching_files(text)
		elif PYTHON_VERSION[0] >= 3:
			thread = threading.Thread(target=self.get_matching_files, args=(text,))
			thread.start()

	def get_matching_files(self, text):
		paths = GetSourcePaths(self.view)
		if paths:
			ShowMessage("Looking for matches...")
			candidates = []
			text = text.lower()
			for path in paths:
				for root, dirs, files in os.walk(path):
					for file in files:
						if text in file.lower():
							fullPath = os.path.join(root, file)
							if not fullPath in candidates:
								candidates.append(fullPath)
					break
			i = len(candidates)
			if i == 1:
				ShowMessage("Found 1 match.")
				self.window.open_file(candidates[0])
			elif i > 1:
				ShowMessage("Found %d matches." % i)
				self.window.run_command("sublime_papyrus_file_selection_panel", {"items": candidates})
			else:
				ShowMessage("Found no matches.")

# Build system
class SublimePapyrusCompileScriptCommand(sublime_plugin.WindowCommand):
	def run(self, **args):
		file = args["cmd"]
		filePath, fileName = os.path.split(file)
		regex = args["file_regex"]
		module = args["module"]
		batch = args.get("batch", False)
		settings = GetSettings()
		if settings:
			modules = settings.get("modules", None)
			if modules:
				moduleSettings = modules.get(module, None)
				if moduleSettings:
					compiler = moduleSettings.get("compiler", None)
					if not compiler or compiler == "":
						return ShowMessage("The compiler path setting is undefined or invalid.")
					flags = moduleSettings.get("flags", None)
					if not flags or flags == "":
						return ShowMessage("The flags name setting is undefined or invalid.")
					output = moduleSettings.get("output", "")
					if not output or output == "":
						output, _ = os.path.split(filePath)
						if output[-2:] == ":\\":
							output = output + "\\"
					imports = moduleSettings.get("import", None)
					if imports:
						if (PYTHON_VERSION[0] == 2 and isinstance(imports, list) and all(isinstance(k, basestring) for k in imports) and all(k != "" for k in imports)) or (PYTHON_VERSION[0] >= 3 and isinstance(imports, list) and all(isinstance(k, str) for k in imports) and all(k != "" for k in imports)):
							if not batch:
								if not filePath in imports:
									imports.insert(0, filePath)
							else:
								t = filePath.lower()
								if not all(t != k.lower() for k in imports) and settings.get("batch_compilation_warning", True) and not sublime.ok_cancel_dialog("Are you sure you want to batch compile all script sources in \"%s\"?\n\nThis folder is one of the import folders and may contain script sources that are a part of the base game. Compiling said script sources could lead to unintended behavior if they have been modified." % filePath):
									return
							imports = ";".join(imports)
						else:
							return ShowMessage("The import path(s) setting has to be a list of strings.")
					else:
						return ShowMessage("The import path(s) setting is undefined.")
					arguments = moduleSettings.get("arguments", None)
					if arguments:
						if isinstance(arguments, list) and all(isinstance(k, str) for k in arguments):
							temp = []
							for k in arguments:
								if k[:1] == "-":
									temp.append(k)
								else:
									temp.append("-%s" % k)
							arguments = " ".join(temp)
						else:
							return ShowMessage("The arguments setting has to be a list of strings.")
					else:
						arguments = ""
					if not batch:
						args = {"cmd": "\"%s\" \"%s\" -i=\"%s\" -o=\"%s\" -f=\"%s\" %s" % (compiler, fileName, imports, output, flags, arguments), "file_regex": regex}
					else:
						if filePath[-1:] == "\\":
							filePath = filePath[:-1]
						args = {"cmd": "\"%s\" \"%s\" -i=\"%s\" -o=\"%s\" -f=\"%s\" %s %s" % (compiler, filePath, imports, output, flags, batch, arguments), "file_regex": regex}
					self.window.run_command("exec", args)

# Make completions
def MakeFunctionCompletion(stat, sem, calling = True, script = "", precededByKeyword = False):
	tabTrigger = stat.data.name.lower()
	if script:
		script = " (%s)" % script
	description = ""
	if stat.data.type:
		if stat.data.array:
			description = "%s[] func.%s" % (stat.data.typeIdentifier, script)
		else:
			description = "%s func.%s" % (stat.data.typeIdentifier, script)
	else:
		description = "func.%s" % script
	if calling:
		content = ""
		if stat.data.parameters:
			i = 1
			for param in stat.data.parameters:
				if param.array:
					if param.expression:
						content = content + "${%d:%s[] %s = %s}, " % (i, param.type, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s[] %s}, " % (i, param.typeIdentifier, param.identifier)
				else:
					if param.expression:
						content = content + "${%d:%s %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s %s}, " % (i, param.typeIdentifier, param.identifier)
				i += 1
			content = "%s(%s)" % (stat.data.identifier, content[:-2])
		else:
			content = "%s()" % stat.data.identifier
		return (tabTrigger + "\t" + description.lower(), content,)
	else:
		content = ""
		if stat.data.parameters:
			i = 1
			for param in stat.data.parameters:
				if param.array:
					if param.expression:
						content = content + "${%d:%s[] %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s[] %s}, " % (i, param.typeIdentifier, param.identifier)
				else:
					if param.expression:
						content = content + "${%d:%s %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s %s}, " % (i, param.typeIdentifier, param.identifier)
				i += 1
		if len(content) > 0:
			content = content[:-2]
		if precededByKeyword:
			content = "%s(%s)\n\t${0}\nEndFunction" % (stat.data.identifier, content)
		else:
			typ = ""
			if stat.data.type:
				if stat.data.array:
					typ = "%s[] " % stat.data.typeIdentifier
				else:
					typ = "%s " % stat.data.typeIdentifier
			content = "%sFunction %s(%s)\n\t${0}\nEndFunction" % (typ, stat.data.identifier, content)
		return (tabTrigger + "\t" + description.lower(), content,)

def MakeEventCompletion(stat, sem, calling = True, script = "", precededByKeyword = False):
	tabTrigger = stat.data.name.lower()
	if script:
		script = " (%s)" % script
	description = "event%s" % script
	if calling:
		content = ""
		if stat.data.parameters:
			i = 1
			for param in stat.data.parameters:
				if param.array:
					if param.expression:
						content = content + "${%d:%s[] %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s[] %s}, " % (i, param.typeIdentifier, param.identifier)
				else:
					if param.expression:
						content = content + "${%d:%s %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s %s}, " % (i, param.typeIdentifier, param.identifier)
				i += 1
			content = "%s(%s)" % (stat.data.identifier, content[:-2])
		else:
			content = "%s()" % stat.data.identifier
		return (tabTrigger + "\t" + description.lower(), content,)
	else:
		content = ""
		if stat.data.parameters:
			i = 1
			for param in stat.data.parameters:
				if param.array:
					if param.expression:
						content = content + "${%d:%s[] %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s[] %s}, " % (i, param.typeIdentifier, param.identifier)
				else:
					if param.expression:
						content = content + "${%d:%s %s = %s}, " % (i, param.typeIdentifier, param.identifier, sem.GetLiteral(param.expression, True))
					else:
						content = content + "${%d:%s %s}, " % (i, param.typeIdentifier, param.identifier)
				i += 1
		if len(content) > 0:
			content = content[:-2]
		if precededByKeyword:
			content = "%s(%s)\n\t${0}\nEndEvent" % (stat.data.identifier, content)
		else:
			content = "Event %s(%s)\n\t${0}\nEndEvent" % (stat.data.identifier, content)
		return (tabTrigger + "\t" + description.lower(), content,)

def MakePropertyCompletion(stat, script = ""):
	tabTrigger = stat.data.name.lower()
	description = ""
	if script:
		script = " (%s)" % script
	if stat.data.array:
		description = "%s[] prop.%s" % (stat.data.typeIdentifier, script)
	else:
		description = "%s prop.%s" % (stat.data.typeIdentifier, script)
	content = stat.data.identifier
	return (tabTrigger + "\t" + description.lower(), content,)

def MakeVariableCompletion(stat):
	tabTrigger = stat.data.name.lower()
	description = ""
	if stat.data.array:
		description = "%s[] var." % (stat.data.typeIdentifier)
	else:
		description = "%s var." % (stat.data.typeIdentifier)
	content = stat.data.identifier
	return (tabTrigger + "\t" + description.lower(), content,)

def MakeParameterCompletion(stat):
	tabTrigger = stat.data.name.lower()
	description = ""
	if stat.data.array:
		description = "%s[] param." % (stat.data.typeIdentifier)
	else:
		description = "%s param." % (stat.data.typeIdentifier)
	content = stat.data.identifier
	return (tabTrigger + "\t" + description.lower(), content,)

# Checks the build result for errors and, depending on the settings, highlights lines that caused errors and/or hides the build results when there are no errors.
class ExecCommand(BUILD_SYSTEM.ExecCommand):
	def finish(self, proc):
		view = sublime.active_window().active_view()
		if view:
			if "source.papyrus" in view.scope_name(0):
				view.erase_regions(ERROR_HIGHLIGHT_KEY)
				userSettings = GetSettings()
				if userSettings:
					if userSettings.get('highlight_build_errors', True):
						output = self.output_view.substr(sublime.Region(0, self.output_view.size()))
						if output:
							pattern = self.output_view.settings().get("result_file_regex")
							if pattern:
								errors = self.GetErrors(output, pattern)
								if errors:
									regions = self.GetRegions(view, errors)
									if regions:
										view.add_regions(ERROR_HIGHLIGHT_KEY, regions, ERROR_HIGHLIGHT_SCOPE)
										if userSettings.get("center_highlighted_line", True):
											view.show_at_center(regions[0])
								elif userSettings.get('hide_successful_build_results', False):
									self.window.run_command("hide_panel", {"panel": "output.exec"})

	def GetErrors(self, output, pattern):
		lines = output.rstrip().split('\n')
		matches = []
		regex = re.compile(pattern)
		for line in lines:
			match = regex.findall(line)
			if len(match) > 0:
				matches.append(match)
		if len(matches) > 0:
			return matches
		else:
			return None

	def GetRegions(self, view, errors):
		regions  = []
		for error in errors:
			region = view.line(sublime.Region(view.text_point(int(error[0][1]) - 1, 0)))
			regions.append(region)
			del region
		if len(regions) > 0:
			return regions
		else:
			return None