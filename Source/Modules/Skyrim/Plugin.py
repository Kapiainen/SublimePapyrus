# API for accessing the core plugin of SublimePapyrus
import sublime, sublime_plugin, sys, os, json, threading, time
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
	# Skyrim linter module
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

VALID_SCOPE = "source.papyrus.skyrim"

def plugin_loaded():
	global SUBLIME_VERSION
	SUBLIME_VERSION = int(sublime.version())

# Completion generation
class SublimePapyrusSkyrimGenerateCompletionsCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view:
			self.paths = SublimePapyrus.GetSourcePaths(view)
			if self.paths:
				if PYTHON_VERSION[0] == 2:
					self.window.show_quick_panel(self.paths, self.on_select, 0, -1)
				elif PYTHON_VERSION[0] >= 3:
					self.window.show_quick_panel(self.paths, self.on_select, 0, -1, None)

	def on_select(self, index):
		if index >= 0:
			self.path = self.paths[index]
			thread = threading.Thread(target=self.generate_completions)
			thread.start()

	def generate_completions(self):
		outputFolder = os.path.join(sublime.packages_path(), "User")
		lex = Linter.Lexical()
		syn = Linter.Syntactic()
		sem = Linter.Semantic()
		files = [f for f in os.listdir(self.path) if ".psc" in f]
		for file in files:
			path = os.path.join(self.path, file)
			scriptName = file[:-4]
			with open(path) as fi:
				scriptContents = fi.read()
				if scriptContents:
					lines = []
					tokens = []
					try:
						for token in lex.Process(scriptContents):
							if token.type == lex.NEWLINE:
								if tokens:
									lines.append(tokens)
								tokens = []
							elif token.type != lex.COMMENT_LINE and token.type != lex.COMMENT_BLOCK:
								tokens.append(token)
					except Linter.LexicalError as e:
						if PYTHON_VERSION[0] == 2:
							print("SublimePapyrus - Lexical error on line %d, column %d in '%s': %s" % (e.line, e.column, path, e.message))
						elif PYTHON_VERSION[0] >= 3:
							SublimePapyrus.ShowMessage("Error on line %d, column %d in '%s': %s" % (e.line, e.column, path, e.message))
						return
					if lines:
						statements = []
						for line in lines:
							try:
								stat = syn.Process(line)
								if stat and (stat.type == sem.STAT_FUNCTIONDEF or stat.type == sem.STAT_EVENTDEF):
									statements.append(stat)
							except Linter.SyntacticError as e:
								if PYTHON_VERSION[0] == 2:
									print("SublimePapyrus - Syntactic error on line %d in '%s': %s" % (e.line, path, e.message))
								elif PYTHON_VERSION[0] >= 3:
									SublimePapyrus.ShowMessage("Error on line %d in '%s': %s" % (e.line, path, e.message))
								return
						scriptNameLower = scriptName.lower()
						completions = [{"trigger": "%s\t%s" % (scriptNameLower, "script"), "contents": scriptName}]
						for stat in statements:
							if stat.type == sem.STAT_FUNCTIONDEF:
								temp = SublimePapyrus.MakeFunctionCompletion(stat, sem, script=scriptNameLower)
								completions.append({"trigger": temp[0], "contents": temp[1]})
							elif stat.type == sem.STAT_EVENTDEF:
								temp = SublimePapyrus.MakeEventCompletion(stat, sem, calling=False, script=scriptNameLower)
								completions.append({"trigger": temp[0], "contents": temp[1]})
						output = {
							"scope": VALID_SCOPE,
							"completions": completions
						}
						with open(os.path.join(outputFolder, "SublimePapyrus - Skyrim - %s.sublime-completions" % scriptName), "w") as fo:
							json.dump(output, fo, indent=2)
		print("SublimePapyrus - Finished generating completions for scripts in '%s'" % self.path)

linterCache = {}
completionCache = {}
cacheLock = threading.RLock()
lex = Linter.Lexical()
syn = Linter.Syntactic()
sem = Linter.Semantic()

class EventListener(sublime_plugin.EventListener):
	def __init__(self):
		super(EventListener,self).__init__()
		self.linterQueue = 0
		self.linterRunning = False
		self.linterErrors = {}
		self.completionRunning = False
		self.validScope = "source.papyrus.skyrim"
		self.completionKeywordAs = ("as\tcast", "As ",)
		self.completionKeywordAuto = ("auto\tkeyword", "Auto",)
		self.completionKeywordAutoReadOnly = ("autoreadonly\tkeyword", "AutoReadOnly",)
		self.completionKeywordConditional = ("conditional\tkeyword", "Conditional",)
		self.completionKeywordExtends = ("extends\tkeyword", "Extends ",)
		self.completionKeywordGlobal = ("global\tkeyword", "Global",)
		self.completionKeywordHidden = ("hidden\tkeyword", "Hidden",)
		self.completionKeywordNative = ("native\tkeyword", "Native",)
		self.completionKeywordParent = ("parent\tkeyword", "Parent",)
		self.completionKeywordSelf = ("self\tkeyword", "Self",)
		self.completionKeywordFalse = ("false\tkeyword", "False",)
		self.completionKeywordNone = ("none\tkeyword", "None",)
		self.completionKeywordTrue = ("true\tkeyword", "True",)

	# Clear cache in order to force an update
	def on_close(self, view):
		if self.IsValidScope(view):
			bufferID = view.buffer_id()
			if bufferID:
				if self.linterErrors.get(bufferID, None):
					del self.linterErrors[bufferID]
				self.ClearLinterCache(bufferID)

	# Linter
	def on_post_save(self, view):
		if self.IsValidScope(view):
			settings = SublimePapyrus.GetSettings()
			if settings and settings.get("linter_on_save", True):
				filePath = view.file_name()
				if filePath:
					folderPath, fileName = os.path.split(filePath)
					scriptName = fileName[:fileName.rfind(".")].upper()
					if self.linterRunning:
						return
					self.ClearSemanticAnalysisCache(scriptName)
					self.ClearCompletionCache(scriptName)
					self.bufferID = view.buffer_id()
					if self.bufferID:
						self.linterQueue += 1
						lineNumber, columnNumber = view.rowcol(view.sel()[0].begin())
						lineNumber += 1
						self.Linter(view, lineNumber)

	def on_modified(self, view):
		if self.IsValidScope(view):
			settings = SublimePapyrus.GetSettings()

			global SUBLIME_VERSION
			if SUBLIME_VERSION >= 3070 and settings.get("tooltip_function_parameters", True):
				if self.linterRunning:
					return
				elif self.completionRunning:
					return
				global cacheLock
				global lex
				global syn
				global sem
				with cacheLock:
					locations = [view.sel()[0].begin()]
					prefix = view.word(locations[0])
					line, column = view.rowcol(locations[0])
					line += 1
					lineString = view.substr(sublime.Region(view.line(locations[0]).begin(), locations[0]-len(prefix))).strip()
					bufferID = view.buffer_id()
					if bufferID:
						currentScript = self.GetScript(bufferID)
						if currentScript:
							try:
								sem.GetContext(currentScript, line)
							except Linter.FunctionDefinitionCancel as e:
								tokens = []
								try:
									for token in lex.Process(lineString):
										if token.type != lex.NEWLINE:
											tokens.append(token)
									if tokens and tokens[-1].type != lex.COMMENT_LINE:
										try:
											syn.Process(tokens)
										except Linter.ExpectedIdentifierError as f:
											if tokens[-1].type != lex.OP_DOT:
												stack = syn.stack[:]
												arguments = []
												for item in reversed(stack):
													if item.type == sem.NODE_FUNCTIONCALLARGUMENT:
														arguments.insert(0, stack.pop())
													elif item.type == sem.LEFT_PARENTHESIS:
														break
												stackLength = len(stack)
												func = None
												if stackLength >= 2 and stack[-2].type == sem.IDENTIFIER:
													name = stack[-2].value.upper()
													if stackLength >= 4 and stack[-3].type == sem.OP_DOT:
														try:
															result = sem.NodeVisitor(stack[-4])
															if result.type != sem.KW_SELF:
																try:
																	script = sem.GetCachedScript(result.type)
																	func = script.functions.get(name, None)
																except Linter.SemanticError as e:
																	return
															else:
																for scope in reversed(e.functions):
																	func = scope.get(name, None)
																	if func:
																		break
														except Linter.SemanticError as e:
															return
													else:
														for scope in reversed(e.functions):
															func = scope.get(name, None)
															if func:
																break
														for imp in e.imports:
															script = sem.GetCachedScript(imp)
															temp = script.functions.get(name, None)
															if temp:
																if func:
																	func = None
																else:
																	func = temp
																break
												if func and func.data.parameters:
													self.ShowFunctionInfo(view, tokens, func, len(arguments))
										except Linter.SyntacticError as f:
											pass
								except Linter.LexicalError as f:
									pass
							except Linter.SemanticError as e:
								pass

			if settings and settings.get("linter_on_modified", True):
				self.QueueLinter(view)

	def ShowFunctionInfo(self, view, tokens, func, argumentCount):
		funcName = func.data.identifier
		currentParameter = None
		if len(tokens) > 2 and tokens[-1].type == lex.OP_ASSIGN and tokens[-2].type == lex.IDENTIFIER:
			currentParameter = tokens[-2].value.upper()
		paramIndex = 0
		funcParameters = []
		for param in func.data.parameters:
			paramName = param.identifier
			paramType = param.typeIdentifier
			if param.array:
				paramType = "%s[]" % paramType
			paramContent = None
			if param.expression:
				paramDefaultValue = sem.GetLiteral(param.expression, True)
				paramContent = "%s %s = %s" % (paramType, paramName, paramDefaultValue)
			else:
				paramContent = "%s %s" % (paramType, paramName)
			if currentParameter:
				if currentParameter == paramName.upper():
					paramContent = "<b>%s</b>" % paramContent
			else:
				if paramIndex == argumentCount:
					paramContent = "<b>%s</b>" % paramContent
				paramIndex += 1
			funcParameters.append(paramContent)
		settings = SublimePapyrus.GetSettings()
		backgroundColor = settings.get("tooltip_background_color", "#393939")
		bodyTextColor = settings.get("tooltip_body_text_color", "#747369")
		bodyFontSize = settings.get("tooltip_font_size", "12")
		boldTextColor = settings.get("tooltip_bold_text_color", "#ffffff")
		headingTextColor = settings.get("tooltip_heading_text_color", "#bfbfbf")
		headingFontSize = settings.get("tooltip_heading_font_size", "14")
		css = """<style>
html {
	background-color: %s;
}

body {
    font-size: %spx;
    color: %s;
}

b {
    color: %s;
}

h1 {
    color: %s;
    font-size: %spx;
}
</style>""" % (backgroundColor, bodyFontSize, bodyTextColor, boldTextColor, headingTextColor, headingFontSize)
		content = "%s<h1>%s</h1>%s" % (css, funcName, "<br>".join(funcParameters))
		if view.is_popup_visible():
			view.update_popup(content)
		else:
			view.show_popup(content, flags=sublime.COOPERATE_WITH_AUTO_COMPLETE, max_width=int(settings.get("tooltip_max_width", 600)), max_height=int(settings.get("tooltip_max_height", 300)))

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
			lineNumber, columnNumber = view.rowcol(view.sel()[0].begin())
			lineNumber += 1
			if PYTHON_VERSION[0] == 2:
				self.scriptContents = view.substr(sublime.Region(0, view.size()))			
				self.sourcePaths = SublimePapyrus.GetSourcePaths(view)
				SublimePapyrus.ClearLinterHighlights(view)
				t = threading.Timer(delay, self.Linter, kwargs={"view": None, "lineNumber": lineNumber})
				t.daemon = True
				t.start()
			elif PYTHON_VERSION[0] >= 3:
				t = threading.Timer(delay, self.Linter, kwargs={"view": view, "lineNumber": lineNumber})
				t.daemon = True
				t.start()

	def Linter(self, view, lineNumber):
		self.linterQueue -= 1 # Remove from queue
		if self.linterQueue > 0: # If there is a queue, then cancel
			return
		elif self.completionRunning: # If completions are being generated, then cancel
			return
		self.linterRunning = True # Block further attempts to run the linter until this instance has finished
		if view:
			SublimePapyrus.ClearLinterHighlights(view)
		#start = None #DEBUG
		def Exit():
			#print("Linter: Finished in %f milliseconds and releasing lock..." % ((time.time()-start)*1000.0)) #DEBUG
			self.linterRunning = False
			return False
		global cacheLock
		global lex
		global syn
		global sem
		global SUBLIME_VERSION
		with cacheLock:
			if not self.linterErrors.get(self.bufferID, None):
				self.linterErrors[self.bufferID] = {}
			#start = time.time() #DEBUG
			settings = None
			if view:
				settings = SublimePapyrus.GetSettings()
			if SUBLIME_VERSION >= 3103 and view.is_auto_complete_visible(): # If a list of completions is visible, then cancel
				return Exit()
			if view:
				SublimePapyrus.SetStatus(view, "sublimepapyrus-linter", "The linter is running...")
			#lexSynStart = time.time() #DEBUG
			scriptContents = None
			if view:
				scriptContents = view.substr(sublime.Region(0, view.size()))
			else:
				scriptContents = self.scriptContents
			lineCount = scriptContents.count("\n") + 1
			statements = []
			lines = []
			tokens = []
			currentLine = None
			try:
				for token in lex.Process(scriptContents):
					if token.type == lex.NEWLINE:
						if tokens:
							if currentLine:
								stat = syn.Process(tokens)
								if stat:
									statements.append(stat)
							elif token.line >= lineNumber:
								currentLine = syn.Process(tokens)
								if currentLine:
									while lines:
										stat = syn.Process(lines.pop(0))
										if stat:
											statements.append(stat)
									statements.append(currentLine)
								currentLine = True
							else:
								lines.append(tokens)
							tokens = []
						else:
							if token.line >= lineNumber:
								while lines:
									stat = syn.Process(lines.pop(0))
									if stat:
										statements.append(stat)
								currentLine = True
					elif token.type != lex.COMMENT_LINE and token.type != lex.COMMENT_BLOCK:
						tokens.append(token)
			except Linter.LexicalError as e:
				if view:
					error = self.linterErrors[self.bufferID].get(e.message, None)
					if error and error.message == e.message and abs(error.line - e.line) < settings.get("linter_error_line_threshold", 2) + 1:
						SublimePapyrus.HighlightLinter(view, e.line, e.column, False)
					else:
						SublimePapyrus.HighlightLinter(view, e.line, e.column)
					self.linterErrors[self.bufferID][e.message] = e
					SublimePapyrus.SetStatus(view, "sublimepapyrus-linter", "Error on line %d, column %d: %s" % (e.line, e.column, e.message))
					if settings.get("linter_panel_error_messages", False):
						view.window().show_quick_panel([[e.message, "Line %d, column %d" % (e.line, e.column)]], None)
				return Exit()
			except Linter.SyntacticError as e:
				if view:
					error = self.linterErrors[self.bufferID].get(e.message, None)
					if error and error.message == e.message and abs(error.line - e.line) < settings.get("linter_error_line_threshold", 2) + 1:
						SublimePapyrus.HighlightLinter(view, e.line, center=False)
					else:
						SublimePapyrus.HighlightLinter(view, e.line)
					self.linterErrors[self.bufferID][e.message] = e
					SublimePapyrus.SetStatus(view, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message))
					if settings.get("linter_panel_error_messages", False):
						view.window().show_quick_panel([[e.message, "Line %d" % e.line]], None)
				return Exit()
			#print("Linter: Finished lexical and syntactic in %f milliseconds..." % ((time.time()-lexSynStart)*1000.0)) #DEBUG
			#semStart = time.time() #DEBUG
			if statements:
				try:
					script = None
					if view:
						script = sem.Process(statements, SublimePapyrus.GetSourcePaths(view))
					else:
						script = sem.Process(statements, self.sourcePaths)
					if script:
						self.SetScript(self.bufferID, script)
				except Linter.SemanticError as e:
					if view:
						error = self.linterErrors[self.bufferID].get(e.message, None)
						if error and error.message == e.message and abs(error.line - e.line) < settings.get("linter_error_line_threshold", 2) + 1:
							SublimePapyrus.HighlightLinter(view, e.line, center=False)
						else:
							SublimePapyrus.HighlightLinter(view, e.line)
						self.linterErrors[self.bufferID][e.message] = e
						SublimePapyrus.SetStatus(view, "sublimepapyrus-linter", "Error on line %d: %s" % (e.line, e.message)) 
						if settings.get("linter_panel_error_messages", False):
							view.window().show_quick_panel([[e.message, "Line %d" % e.line]], None)
					return Exit()
				#print("Linter: Finished semantic in %f milliseconds..." % ((time.time()-semStart)*1000.0)) #DEBUG
				if view:
					SublimePapyrus.ClearStatus(view, "sublimepapyrus-linter")
				if self.linterErrors.get(self.bufferID, None):
					del self.linterErrors[self.bufferID]
		return Exit()

	# Completions
	def on_query_completions(self, view, prefix, locations):
		if self.IsValidScope(view):
			settings = SublimePapyrus.GetSettings()
			if settings and settings.get("intelligent_code_completion", True):
				if self.completionRunning:
					return
				elif self.linterRunning:
					return
				self.completionRunning = True
				#start = time.time() #DEBUG
				completions = None
				if not view.find("scriptname", 0, sublime.IGNORECASE):
					path = view.file_name()
					if path:
						_, name = os.path.split(path)
						completions = [("scriptname\tscript header", "ScriptName %s" % name[:name.rfind(".")],)]
					else:
						completions = [("scriptname\tscript header", "ScriptName ",)]
				else:					
					completions = self.Completions(view, prefix, locations)
				if completions:
					completions = list(set(completions))
				elif completions == None:
					completions = []
				completions = (completions, sublime.INHIBIT_WORD_COMPLETIONS|sublime.INHIBIT_EXPLICIT_COMPLETIONS,)
				#print("Completions: Finished in %f milliseconds and releasing lock..." % ((time.time()-start)*1000.0)) #DEBUG
				self.completionRunning = False
				return completions

	def Completions(self, view, prefix, locations):
		SublimePapyrus.ClearLinterHighlights(view)
		completions = []
		flags = None
		global cacheLock
		global lex
		global syn
		global sem
		with cacheLock:
			bufferID = view.buffer_id()
			if not bufferID:
				return
			currentScript = self.GetScript(bufferID)
			if not currentScript:
				SublimePapyrus.ShowMessage("Run the linter once...")
				return
			line, column = view.rowcol(locations[0])
			line += 1
			lineString = view.substr(sublime.Region(view.line(locations[0]).begin(), locations[0]-len(prefix))).strip()
			settings = SublimePapyrus.GetSettings()
			settingFunctionEventParameters = settings.get("intelligent_code_completion_function_event_parameters", True)
			try:
				sem.GetContext(currentScript, line)
			except Linter.EmptyStateCancel as e:
				if not lineString:
					# Inherited functions/events
					for name, obj in e.functions[0].items():
						if obj.type == syn.STAT_FUNCTIONDEF:
							completions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, False, "parent"))
						elif obj.type == syn.STAT_EVENTDEF:
							completions.append(SublimePapyrus.MakeEventCompletion(obj, sem, False, "parent"))
					completions.append(("import\timport statement", "Import ${0:$SELECTION}",))
					completions.append(("property\tproperty def.", "${1:Type} Property ${2:PropertyName} ${3:Auto}",))
					completions.append(("fullproperty\tfull property def.", "${1:Type} Property ${2:PropertyName}\n\t${1:Type} Function Get()\n\t\t${3}\n\tEndFunction\n\n\tFunction Set(${1:Type} Variable)\n\t\t${4}\n\tEndFunction\nEndProperty",))
					completions.append(("autostate\tauto state def.", "Auto State ${1:StateName}\n\t${0}\nEndState",))
					completions.append(("state\tstate def.", "State ${1:StateName}\n\t${0}\nEndState",))
					completions.append(("event\tevent def.", "Event ${1:EventName}(${2:Parameters})\n\t${0}\nEndEvent",))
					completions.append(("function\tfunction def.", "${1:Type} Function ${2:FunctionName}(${3:Parameters})\n\t${0}\nEndFunction",))
					# Types to facilitate variable declarations
					completions.extend(self.GetTypeCompletions(view, True))
					return completions
				else:
					tokens = []
					try:
						for token in lex.Process(lineString):
							if token.type != lex.NEWLINE:
								tokens.append(token)
					except Linter.LexicalError as f:
						return
					if tokens:
						if tokens[-1].type != lex.COMMENT_LINE:
							try:
								stat = syn.Process(tokens)
								# Optional flags
								if stat.type == syn.STAT_SCRIPTHEADER:
									if not stat.data.parent:
										completions.append(self.completionKeywordExtends)
									if not lex.KW_CONDITIONAL in stat.data.flags:
										completions.append(self.completionKeywordConditional)
									if not lex.KW_HIDDEN in stat.data.flags:
										completions.append(self.completionKeywordHidden)
								elif stat.type == syn.STAT_PROPERTYDEF:
									if not lex.KW_AUTO in stat.data.flags and not syn.KW_AUTOREADONLY in stat.data.flags:
										completions.append(self.completionKeywordAuto)
									if not lex.KW_AUTOREADONLY in stat.data.flags and not syn.KW_AUTO in stat.data.flags:
										completions.append(self.completionKeywordAutoReadOnly)
									if not lex.KW_CONDITIONAL in stat.data.flags:
										completions.append(self.completionKeywordConditional)
									if not lex.KW_HIDDEN in stat.data.flags:
										completions.append(self.completionKeywordHidden)
								elif stat.type == syn.STAT_VARIABLEDEF:
									if not lex.KW_CONDITIONAL in stat.data.flags:
										completions.append(self.completionKeywordConditional)
								elif stat.type == syn.STAT_FUNCTIONDEF:
									if not lex.KW_NATIVE in stat.data.flags:
										completions.append(self.completionKeywordNative)
									if not lex.KW_GLOBAL in stat.data.flags:
										completions.append(self.completionKeywordGlobal)
								elif stat.type == syn.STAT_EVENTDEF:
									if not lex.KW_NATIVE in stat.data.flags:
										completions.append(self.completionKeywordNative)
								return completions
							except Linter.ExpectedTypeError as f:
								completions.extend(self.GetTypeCompletions(view, f.baseTypes))
								return completions
							except Linter.ExpectedKeywordError as f:
								# Mandatory property flags when initializing a property with a literal
								if syn.KW_AUTO in e.keywords:
									completions.append(("auto\tkeyword", "Auto",))
								if syn.KW_AUTOREADONLY in e.keywords:
									completions.append(("autoreadonly\tkeyword", "AutoReadOnly",))
								return completions
							except Linter.ExpectedLiteralError as f:
								# Literals when initializing a property
								if tokens[1].type == lex.KW_PROPERTY:
									if tokens[0].type == lex.IDENTIFIER:
										completions.append(self.completionKeywordNone)
									elif tokens[0].type == lex.KW_BOOL:
										completions.append(self.completionKeywordTrue)
										completions.append(self.completionKeywordFalse)
									elif tokens[0].type == lex.KW_STRING:
										completions.append(("stringliteral\tstring literal", "\"${0}\""))
									return completions
								elif tokens[1].type == lex.LEFT_BRACKET and tokens[2].type == lex.RIGHT_BRACKET and tokens[3].type == lex.KW_PROPERTY:
									completions.append(self.completionKeywordNone)
									return completions
							except Linter.SyntacticError as f:
								return
				return
			except Linter.StateCancel as e:
				# Functions/events that have not yet been defined in the state.
				if not lineString:
					# Functions/events defined in the empty state.
					for name, stat in e.functions[1].items():
						if stat.type == syn.STAT_EVENTDEF and not e.functions[2].get(name, False):
							completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, False, "self"))
						elif stat.type == syn.STAT_FUNCTIONDEF and not e.functions[2].get(name, False):
							completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "self"))
					# Inherited functions/events.
					for name, stat in e.functions[0].items():
						if stat.type == syn.STAT_EVENTDEF and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
							completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, False, "parent"))
						elif stat.type == syn.STAT_FUNCTIONDEF and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
							completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "parent"))
					return completions
				else:
					tokens = []
					try:
						for token in lex.Process(lineString):
							if token.type != lex.NEWLINE:
								tokens.append(token)
					except Linter.LexicalError as f:
						return
					if tokens:
						if tokens[-1].type != lex.COMMENT_LINE:
							tokenCount = len(tokens)
							# Functions without return types and events
							if tokenCount == 1:
								if tokens[0].type == lex.KW_FUNCTION:
									# Functions/events defined in the empty state.
									for name, stat in e.functions[1].items():
										if stat.type == syn.STAT_FUNCTIONDEF and not stat.data.type and not e.functions[2].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "self", True))
									# Inherited functions/events.
									for name, stat in e.functions[0].items():
										if stat.type == syn.STAT_FUNCTIONDEF and not stat.data.type and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "parent", True))
									return completions
								elif tokens[0].type == lex.KW_EVENT:
									# Functions/events defined in the empty state.
									for name, stat in e.functions[1].items():
										if stat.type == syn.STAT_EVENTDEF and not e.functions[2].get(name, False):
											completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, False, "self", True))
									# Inherited functions/events.
									for name, stat in e.functions[0].items():
										if stat.type == syn.STAT_EVENTDEF and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
											completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, False, "parent", True))
									return completions
							# Functions with non-array return types
							elif tokenCount == 2 and tokens[1].type == lex.KW_FUNCTION:
								if tokens[0].type == lex.IDENTIFIER or tokens[0].type == lex.KW_BOOL or tokens[0].type == lex.KW_FLOAT or tokens[0].type == lex.KW_INT or tokens[0].type == lex.KW_STRING:
									# Functions/events defined in the empty state.
									funcType = tokens[0].value.upper()
									for name, stat in e.functions[1].items():
										if stat.type == syn.STAT_FUNCTIONDEF and not stat.data.array and stat.data.type == funcType and not e.functions[2].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "self", True))
									# Inherited functions/events.
									for name, stat in e.functions[0].items():
										if stat.type == syn.STAT_FUNCTIONDEF and not stat.data.array and stat.data.type == funcType and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "parent", True))
									return completions 
							# Functions with array return types
							elif tokenCount == 4 and tokens[3].type == lex.KW_FUNCTION and tokens[1].type == lex.LEFT_BRACKET and tokens[2].type == lex.RIGHT_BRACKET:
								if tokens[0].type == lex.IDENTIFIER or tokens[0].type == lex.KW_BOOL or tokens[0].type == lex.KW_FLOAT or tokens[0].type == lex.KW_INT or tokens[0].type == lex.KW_STRING:
									# Functions/events defined in the empty state.
									funcType = tokens[0].value.upper()
									for name, stat in e.functions[1].items():
										if stat.type == syn.STAT_FUNCTIONDEF and stat.data.array and stat.data.type == funcType and not e.functions[2].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "self", True))
									# Inherited functions/events.
									for name, stat in e.functions[0].items():
										if stat.type == syn.STAT_FUNCTIONDEF and stat.data.array and stat.data.type == funcType and not e.functions[2].get(name, False) and not e.functions[1].get(name, False):
											completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, False, "parent", True))
									return completions
				return
			except Linter.FunctionDefinitionCancel as e:
				if not lineString:
					# Flow control
					completions.append(("if\tif", "If ${1:$SELECTION}\n\t${0}\nEndIf",))
					completions.append(("elseif\telse-if", "ElseIf ${1:$SELECTION}\n\t${0}",))
					completions.append(("else\telse", "Else\n\t${0}",))
					completions.append(("while\twhile-loop", "While ${1:$SELECTION}\n\t${0}\nEndWhile",))
					completions.append(("for\tpseudo for-loop", "Int ${1:iCount} = 0\nWhile ${1:iCount} < ${2:maxSize}\n\t${0}\n\t${1:iCount} += 1\nEndWhile",))
					if e.signature.data.type:
						completions.append(("return\tstat.", "Return ",))
					else:
						completions.append(("return\tstat.", "Return",))
					# Special variables
					if not sem.KW_GLOBAL in e.signature.data.flags:
						completions.append(self.completionKeywordSelf)
						completions.append(self.completionKeywordParent)
					# Inherited properties
					for name, stat in e.variables[0].items():
						if stat.type == syn.STAT_PROPERTYDEF:
							completions.append(SublimePapyrus.MakePropertyCompletion(stat, "parent"))
					# Properties and variables declared in the empty state
					for name, stat in e.variables[1].items():
						if stat.type == syn.STAT_VARIABLEDEF:
							completions.append(SublimePapyrus.MakeVariableCompletion(stat))
						elif stat.type == syn.STAT_PROPERTYDEF:
							completions.append(SublimePapyrus.MakePropertyCompletion(stat, "self"))
					# Function/event parameters and variables declared in the function
					for name, stat in e.variables[2].items():
						if stat.type == syn.STAT_VARIABLEDEF:
							completions.append(SublimePapyrus.MakeVariableCompletion(stat))
						elif stat.type == syn.STAT_PARAMETER:
							completions.append(SublimePapyrus.MakeParameterCompletion(stat))
					# Variables declared in if, elseif, else, and while scopes
					if len(e.variables) > 3:
						for scope in e.variables[3:]:
							for name, stat in scope.items():
								if stat.type == syn.STAT_VARIABLEDEF:
									completions.append(SublimePapyrus.MakeVariableCompletion(stat))
					if len(e.functions) > 2:
						#Functions/events defined in the non-empty state
						for name, stat in e.functions[2].items():
							if stat.type == syn.STAT_FUNCTIONDEF:
								completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
							elif stat.type == syn.STAT_EVENTDEF:
								completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
						# Functions/events defined in the empty state
						for name, stat in e.functions[1].items():
							if stat.type == syn.STAT_FUNCTIONDEF and not e.functions[2].get(name, None):
								completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
							elif stat.type == syn.STAT_EVENTDEF and not e.functions[2].get(name, None):
								completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
						# Inherited functions/events
						for name, stat in e.functions[0].items():
							if stat.type == syn.STAT_FUNCTIONDEF and not e.functions[1].get(name, None) and not e.functions[2].get(name, None):
								completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, True, "parent", parameters=settingFunctionEventParameters))
							elif stat.type == syn.STAT_EVENTDEF and not e.functions[1].get(name, None) and not e.functions[2].get(name, None):
								completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, True, "parent", parameters=settingFunctionEventParameters))
					else:
						# Functions/events defined in the empty state
						for name, stat in e.functions[1].items():
							if stat.type == syn.STAT_FUNCTIONDEF:
								completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
							elif stat.type == syn.STAT_EVENTDEF:
								completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, True, "self", parameters=settingFunctionEventParameters))
						# Inherited functions/events
						for name, stat in e.functions[0].items():
							if stat.type == syn.STAT_FUNCTIONDEF and not e.functions[1].get(name, None):
								completions.append(SublimePapyrus.MakeFunctionCompletion(stat, sem, True, "parent", parameters=settingFunctionEventParameters))
							elif stat.type == syn.STAT_EVENTDEF and not e.functions[1].get(name, None):
								completions.append(SublimePapyrus.MakeEventCompletion(stat, sem, True, "parent", parameters=settingFunctionEventParameters))
					# Imported global functions
					for imp in e.imports:
						functions = self.GetFunctionCompletions(imp, True)
						if not functions:
							try:
								script = sem.GetCachedScript(imp)
								if script:
									functions = []
									impLower = imp.lower()
									for name, obj in script.functions.items():
										if lex.KW_GLOBAL in obj.data.flags:
											functions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, impLower, parameters=settingFunctionEventParameters))
									self.SetFunctionCompletions(imp, functions, True)
							except:
								return
						if functions:
							completions.extend(functions)
					# Types to facilitate variable declarations
					completions.extend(self.GetTypeCompletions(view, True))
					return completions
				else:
					tokens = []
					try:
						for token in lex.Process(lineString):
							if token.type != lex.NEWLINE:
								tokens.append(token)
					except Linter.LexicalError as f:
						return
					if tokens:
						if tokens[-1].type != lex.COMMENT_LINE:
							try:
								stat = syn.Process(tokens)
								if stat.type == syn.STAT_VARIABLEDEF:
									completions.append(self.completionKeywordAs)
									return completions
								elif stat.type == syn.STAT_ASSIGNMENT:
									completions.append(self.completionKeywordAs)
									return completions
								elif stat.type == syn.STAT_EXPRESSION:
									completions.append(self.completionKeywordAs)
									return completions
							except Linter.ExpectedTypeError as f:
								completions.extend(self.GetTypeCompletions(view, f.baseTypes))
								return completions
							except Linter.ExpectedIdentifierError as f:
								if tokens[-1].type == lex.OP_DOT: # Accessing properties and functions
									try:
										result = sem.NodeVisitor(syn.stack[-2])
										#print(result.type)
										#print(result.array)
										#print(result.object)
										if result.type == lex.KW_SELF:
											for name, obj in e.functions[0].items():
												if obj.type == syn.STAT_FUNCTIONDEF:
													completions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, "parent", parameters=settingFunctionEventParameters))
												elif obj.type == syn.STAT_EVENTDEF:
													completions.append(SublimePapyrus.MakeEventCompletion(obj, sem, True, "parent", parameters=settingFunctionEventParameters))
											for name, obj in e.functions[1].items():
												if obj.type == syn.STAT_FUNCTIONDEF:
													completions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, "self", parameters=settingFunctionEventParameters))
												elif obj.type == syn.STAT_EVENTDEF:
													completions.append(SublimePapyrus.MakeEventCompletion(obj, sem, True, "self", parameters=settingFunctionEventParameters))
											for name, obj in e.variables[0].items():
												if obj.type == syn.STAT_PROPERTYDEF:
													completions.append(SublimePapyrus.MakePropertyCompletion(obj, "parent"))
											for name, obj in e.variables[1].items():
												if obj.type == syn.STAT_PROPERTYDEF:
													completions.append(SublimePapyrus.MakePropertyCompletion(obj, "self"))
											return completions
										elif result.array:
											typ = result.type.capitalize()
											completions.append(("find\tint func.", "Find(${1:%s akElement}, ${2:Int aiStartIndex = 0})" % typ,))
											completions.append(("rfind\tint func.", "RFind(${1:%s akElement}, ${2:Int aiStartIndex = -1})" % typ,))
											completions.append(("length\tkeyword", "Length",))
											return completions
										else:
											# None and types that do not have properties nor functions/events
											if result.type == lex.KW_NONE or result.type == lex.KW_BOOL or result.type == lex.KW_FLOAT or result.type == lex.KW_INT or result.type == lex.KW_STRING:
												return
											if not result.object: #Global <TYPE> functions
												functions = self.GetFunctionCompletions(result.type, True)
												if not functions:
													try:
														script = sem.GetCachedScript(result.type)
														if script:
															functions = []
															typeLower = result.type.lower()
															for name, obj in script.functions.items():
																if lex.KW_GLOBAL in obj.data.flags:
																	functions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, typeLower, parameters=settingFunctionEventParameters))
															self.SetFunctionCompletions(result.type, functions, True)
													except:
														return
												if functions:
													completions.extend(functions)
												return completions
											else: # Non-global functions, events, and properties
												functions = self.GetFunctionCompletions(result.type, False)
												if not functions:
													try:
														script = sem.GetCachedScript(result.type)
														if script:
															functions = []
															typeLower = result.type.lower()
															for name, obj in script.functions.items():
																if lex.KW_GLOBAL not in obj.data.flags:
																	functions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, typeLower, parameters=settingFunctionEventParameters))
															self.SetFunctionCompletions(result.type, functions, False)
													except:
														return
												if functions:
													completions.extend(functions)
												properties = self.GetPropertyCompletions(result.type)
												if not properties:
													try:
														script = sem.GetCachedScript(result.type)
														if script:
															properties = []
															typeLower = result.type.lower()
															for name, obj in script.properties.items():
																properties.append(SublimePapyrus.MakePropertyCompletion(obj, typeLower))
															self.SetPropertyCompletions(result.type, properties)
													except:
														return
												if properties:
													completions.extend(properties)
												return completions
										return
									except Linter.SemanticError as g:
										return
									return completions
								else: # Not following a dot
									for name, obj in e.functions[0].items():
										if obj.type == syn.STAT_FUNCTIONDEF:
											completions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, "parent", parameters=settingFunctionEventParameters))
										elif obj.type == syn.STAT_EVENTDEF:
											completions.append(SublimePapyrus.MakeEventCompletion(obj, sem, True, "parent", parameters=settingFunctionEventParameters))
									for name, obj in e.functions[1].items():
										if obj.type == syn.STAT_FUNCTIONDEF:
											completions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, "self", parameters=settingFunctionEventParameters))
										elif obj.type == syn.STAT_EVENTDEF:
											completions.append(SublimePapyrus.MakeEventCompletion(obj, sem, True, "self", parameters=settingFunctionEventParameters))
									for name, obj in e.variables[0].items():
										if obj.type == syn.STAT_PROPERTYDEF:
											completions.append(SublimePapyrus.MakePropertyCompletion(obj, "parent"))
									for name, obj in e.variables[1].items():
										if obj.type == syn.STAT_PROPERTYDEF:
											completions.append(SublimePapyrus.MakePropertyCompletion(obj, "self"))
										elif obj.type == syn.STAT_VARIABLEDEF:
											completions.append(SublimePapyrus.MakeVariableCompletion(obj))
									for scope in e.variables[2:]:
										for name, obj in scope.items():
											if obj.type == syn.STAT_VARIABLEDEF:
												completions.append(SublimePapyrus.MakeVariableCompletion(obj))
											elif obj.type == syn.STAT_PARAMETER:
												completions.append(SublimePapyrus.MakeParameterCompletion(obj))
									completions.extend(self.GetTypeCompletions(view, False))
									completions.append(self.completionKeywordFalse)
									completions.append(self.completionKeywordTrue)
									completions.append(self.completionKeywordNone)
									completions.append(self.completionKeywordAs)
									if not sem.KW_GLOBAL in e.signature.data.flags:
										completions.append(self.completionKeywordSelf)
										completions.append(self.completionKeywordParent)

									# Imported global functions
									for imp in e.imports:
										functions = self.GetFunctionCompletions(imp, True)
										if not functions:
											try:
												script = sem.GetCachedScript(imp)
												if script:
													functions = []
													impLower = imp.lower()
													for name, obj in script.functions.items():
														if lex.KW_GLOBAL in obj.data.flags:
															functions.append(SublimePapyrus.MakeFunctionCompletion(obj, sem, True, impLower, parameters=settingFunctionEventParameters))
													self.SetFunctionCompletions(imp, functions, True)
											except:
												return
										if functions:
											completions.extend(functions)

									# Show info about function/event parameters
									stack = syn.stack[:]
									arguments = []
									for item in reversed(stack):
										if item.type == sem.NODE_FUNCTIONCALLARGUMENT:
											arguments.insert(0, stack.pop())
										elif item.type == sem.LEFT_PARENTHESIS:
											break
									stackLength = len(stack)
									func = None
									if stackLength >= 2 and stack[-2].type == sem.IDENTIFIER:
										name = stack[-2].value.upper()
										if stackLength >= 4 and stack[-3].type == sem.OP_DOT:
											try:
												result = sem.NodeVisitor(stack[-4])
												if result.type != sem.KW_SELF:
													try:
														script = sem.GetCachedScript(result.type)
														func = script.functions.get(name, None)
													except Linter.SemanticError as e:
														return
												else:
													for scope in reversed(e.functions):
														func = scope.get(name, None)
														if func:
															break
											except Linter.SemanticError as e:
												return
										else:
											for scope in reversed(e.functions):
												func = scope.get(name, None)
												if func:
													break
											for imp in e.imports:
												script = sem.GetCachedScript(imp)
												temp = script.functions.get(name, None)
												if temp:
													if func:
														func = None
													else:
														func = temp
													break
									if func and func.data.parameters:
										for param in func.data.parameters:
											completions.append(SublimePapyrus.MakeParameterCompletion(Linter.Statement(sem.STAT_PARAMETER, 0, param)))
										global SUBLIME_VERSION
										if SUBLIME_VERSION >= 3070 and prefix == "" and settings.get("tooltip_function_parameters", True):
											if not view.is_popup_visible():
												self.ShowFunctionInfo(view, tokens, func, len(arguments))

									return completions
							except Linter.SyntacticError as f:
								if syn.stack and syn.stack[-2].type == syn.LEFT_PARENTHESIS and syn.stack[-1].type != syn.RIGHT_PARENTHESIS: # Expression enclosed by parentheses
									completions.append(self.completionKeywordAs)
									return completions
								return
				return
			except Linter.PropertyDefinitionCancel as e:
				if not lineString:
					typ = None
					if e.array:
						typ = "%s[]" % e.type.capitalize()
					else:
						typ = "%s" % e.type.capitalize()
					if not "GET" in e.functions:
						completions.append(("get\t%s func." % typ, "%s Function Get()\n\t${0}\nEndFunction" % typ,))
					if not "SET" in e.functions:
						completions.append(("set\tfunc.", "Function Set(%s aParameter)\n\t${0}\nEndFunction" % typ,))
					return completions
				else:
					tokens = []
					try:
						for token in lex.Process(lineString):
							if token.type != lex.NEWLINE:
								tokens.append(token)
					except Linter.LexicalError as f:
						return
					if tokens:
						if tokens[-1].type != lex.COMMENT_LINE:
							pass
				return
			except Linter.SemanticError as e:
				return
			return

	def IsValidScope(self, view):
		if self.validScope:
			return self.validScope in view.scope_name(0)
		return False

	def ClearCompletionCache(self, script):
		global cacheLock
		with cacheLock:
			global completionCache
			if completionCache.get("properties", None):
				if completionCache["properties"].get(script, None):
					del completionCache["properties"][script]
			if completionCache.get("functions", None):
				if completionCache["functions"].get(script, None):
					del completionCache["functions"][script]

	def ClearLinterCache(self, script):
		global cacheLock
		with cacheLock:
			global linterCache
			if linterCache.get(script, None):
				del linterCache[script]

	def ClearSemanticAnalysisCache(self, script):
		global cacheLock
		global sem
		with cacheLock:
			if sem:
				if sem.cache.get(script, None):
					del sem.cache[script]
				children = []
				for name, obj in sem.cache.items():
					if script in obj.extends:
						children.append(name)
				for child in children:
					del sem.cache[child]

	def GetScript(self, bufferID):
		global cacheLock
		with cacheLock:
			global linterCache
			return linterCache.get(bufferID, None)
	
	def SetScript(self, bufferID, script):
		global cacheLock
		with cacheLock:
			global linterCache
			linterCache[bufferID] = script

	def GetFunctionCompletions(self, script, glob = False):
		global cacheLock
		with cacheLock:
			global completionCache
			functions = completionCache.get("functions", None)
			if functions:
				functions = functions.get(script, False)
				if not functions:
					return None
				if glob:
					return functions.get("global", None)
				else:
					return functions.get("nonglobal", None)
			else:
				return None

	def SetFunctionCompletions(self, script, obj, glob = False):
		global cacheLock
		with cacheLock:
			global completionCache
			functions = completionCache.get("functions", None)
			if not functions:
				completionCache["functions"] = {}
				functions = completionCache.get("functions", None)
			if not functions.get(script, False):
				functions[script] = {}
			if glob:
				functions[script]["global"] = obj
			else:
				functions[script]["nonglobal"] = obj

	def GetPropertyCompletions(self, script):
		global cacheLock
		with cacheLock:
			global completionCache
			properties = completionCache.get("properties", None)
			if properties:
				return properties.get(script, None)

	def SetPropertyCompletions(self, script, obj):
		global cacheLock
		with cacheLock:
			global completionCache
			properties = completionCache.get("properties", None)
			if not properties:
				completionCache["properties"] = {}
				properties = completionCache.get("properties", None)
			properties[script] = obj

	def GetTypeCompletions(self, view, baseTypes = True):
		global cacheLock
		with cacheLock:
			global completionCache
			scripts = completionCache.get("types", None)
			if not scripts:
				scripts = []
				paths = SublimePapyrus.GetSourcePaths(view)
				for path in paths:
					if os.path.isdir(path):
						files = [f for f in os.listdir(path) if ".psc" in f]
						for file in files:
							scripts.append(("%s\tscript" % file[:-4].lower(), "%s" % file[:-4]))
				scripts = list(set(scripts))
				self.SetTypeCompletions(scripts)
			if baseTypes:
				scripts.extend([("bool\ttype", "Bool",), ("float\ttype", "Float",), ("int\ttype", "Int",), ("string\ttype", "String",)])
			return scripts

	def SetTypeCompletions(self, obj):
		global cacheLock
		with cacheLock:
			global completionCache
			completionCache["types"] = obj

class SublimePapyrusSkyrimClearCache(sublime_plugin.WindowCommand):
	def run(self):
		global cacheLock
		global sem
		global linterCache
		global completionCache
		with cacheLock:
			linterCache = {}
			completionCache = {} 
			sem.cache = {}

class SublimePapyrusSkyrimActorValueSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"Aggression": "Aggression",
		"Alchemy": "Alchemy",
		"Alteration modifier": "AlterationMod",
		"Alteration power modifier": "AlterationPowerMod",
		"Alteration": "Alteration",
		"Armor perks": "ArmorPerks",
		"Assistance": "Assistance",
		"Attack damage multiplier": "AttackDamageMult",
		"Block": "Block",
		"Bow speed bonus": "BowSpeedBonus",
		"Brain condition": "BrainCondition",
		"Bypass vendor keyword check": "BypassVendorKeywordCheck",
		"Bypass vendor stolen check": "BypassVendorStolenCheck",
		"Carry weight": "CarryWeight",
		"Combat health regeneration multiplier modifier": "CombatHealthRegenMultMod",
		"Combat health regeneration multiplier power modifier": "CombatHealthRegenMultPowerMod",
		"Confidence": "Confidence",
		"Conjuration modifier": "ConjurationMod",
		"Conjuration power modifier": "ConjurationPowerMod",
		"Conjuration": "Conjuration",
		"Critical chance": "CritChance",
		"Damage resistance": "DamageResist",
		"Destruction modifier": "DestructionMod",
		"Destruction power modifier": "DestructionPowerMod",
		"Destruction": "Destruction",
		"Detect life range": "DetectLifeRange",
		"Disease resistance": "DiseaseResist",
		"Dragon souls": "DragonSouls",
		"Enchanting": "Enchanting",
		"Endurance condition": "EnduranceCondition",
		"Energy": "Energy",
		"Equipped item charge": "EquippedItemCharge",
		"Equipped staff charge": "EquippedStaffCharge",
		"Fame": "Fame",
		"Favor active": "FavorActive",
		"Favor points bonus": "FavorPointsBonus",
		"Favors per day timer": "FavorsPerDayTimer",
		"Favors per day": "FavorsPerDay",
		"Fire resistance": "FireResist",
		"Frost resistance": "FrostResist",
		"Heal rate": "HealRate",
		"Health": "Health",
		"Heavy armor": "HeavyArmor",
		"Ignore crippled limbs": "IgnoreCrippledLimbs",
		"Illusion modifier": "IllusionMod",
		"Illusion power modifier": "IllusionPowerMod",
		"Illusion": "Illusion",
		"Infamy": "Infamy",
		"Inventory weight": "InventoryWeight",
		"Invisibility": "Invisibility",
		"Jumping bonus": "JumpingBonus",
		"Last bribed or intimidated": "LastBribedIntimidated",
		"Last flattered": "LastFlattered",
		"Left attack condition": "LeftAttackCondition",
		"Left mobility condition": "LeftMobilityCondition",
		"Light armor": "LightArmor",
		"Lockpicking": "Lockpicking",
		"Magic resistance": "MagicResist",
		"Magicka rate": "MagickaRate",
		"Magicka": "Magicka",
		"Marksman": "Marksman",
		"Mass": "Mass",
		"Melee damage": "MeleeDamage",
		"Mood": "Mood",
		"Morality": "Morality",
		"Night eye": "NightEye",
		"One-handed": "OneHanded",
		"Paralysis": "Paralysis",
		"Perception condition": "PerceptionCondition",
		"Pickpocket": "Pickpocket",
		"Poison resistance": "PoisonResist",
		"Restoration modifier": "RestorationMod",
		"Restoration power modifier": "RestorationPowerMod",
		"Restoration": "Restoration",
		"Right attack condition": "RightAttackCondition",
		"Right mobility condition": "RightMobilityCondition",
		"Shield perks": "ShieldPerks",
		"Shock resistance": "ElectricResist",
		"Shout recovery multiplier": "ShoutRecoveryMult",
		"Smithing": "Smithing",
		"Sneak": "Sneak",
		"Speech": "Speechcraft",
		"Speed multiplier": "SpeedMult",
		"Stamina rate": "StaminaRate",
		"Stamina": "Stamina",
		"Two-handed": "TwoHanded",
		"Unarmed damage": "UnarmedDamage",
		"Variable 01": "Variable01",
		"Variable 02": "Variable02",
		"Variable 03": "Variable03",
		"Variable 04": "Variable04",
		"Variable 05": "Variable05",
		"Variable 06": "Variable06",
		"Variable 07": "Variable07",
		"Variable 08": "Variable08",
		"Variable 09": "Variable09",
		"Variable 10": "Variable10",
		"Voice points": "VoicePoints",
		"Voice rate": "VoiceRate",
		"Waiting for player": "WaitingForPlayer",
		"Ward deflection": "WardDeflection",
		"Ward power": "WardPower",
		"Water breating": "WaterBreathing",
		"Water walking": "WaterWalking",
		"Weapon speed multiplier": "WeaponSpeedMult",
		}
		return items

class SublimePapyrusSkyrimFormTypeSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"(TLOD)": 74,
		"(TOFT)": 86,
		"Acoustic Space (ASPC)": 16,
		"Action (AACT)": 6,
		"Activator (ACTI)": 24,
		"Actor (NPC_)": 43,
		"ActorValueInfo (AVIF)": 95,
		"Addon Node (ADDN)": 94,
		"AI Package (PACK)": 79,
		"Ammo (AMMO)": 42,
		"Animated Object (ANIO)": 83,
		"Apparatus (APPA)": 33,
		"Armor (ARMO)": 26,
		"Armor Addon (ARMA)": 102,
		"Arrow Projectile (PARW)": 64,
		"Art Object (ARTO)": 125,
		"Association Type (ASTP)": 123,
		"Barrier Projectile (PBAR)": 69,
		"Beam Projectile (PBEA)": 66,
		"Body Part Data (BPTD)": 93,
		"Book (BOOK)": 27,
		"Camera Path (CPTH)": 97,
		"Camera Shot (CAMS)": 96,
		"Cell (CELL)": 60,
		"Character": 62,
		"Class (CLAS)": 10,
		"Climate (CLMT)": 55,
		"Collision Layer (COLL)": 132,
		"Color Form (CLFM)": 133,
		"Combat Style (CSTY)": 80,
		"Cone/Voice Projectile (PCON)": 68,
		"Constructible Object (COBJ)": 49,
		"Container (CONT)": 28,
		"Debris (DEBR)": 88,
		"Default Object Manager (DOBJ)": 107,
		"Dialog View (DLVW)": 117,
		"Dialogue Branch (DLBR)": 115,
		"Door (DOOR)": 29,
		"Dual Cast Data (DUAL)": 129,
		"Effect Setting": 18,
		"Effect Shader (EFSH)": 85,
		"Enchantment (ENCH)": 21,
		"Encounter Zone (ECZN)": 103,
		"Equip Slot (EQUP)": 120,
		"Explosion (EXPL)": 87,
		"Eyes (EYES)": 13,
		"Faction (FACT)": 11,
		"Flame Projectile (PLFA)": 67,
		"Flora (FLOR)": 39,
		"Footstep (FSTP)": 110,
		"Footstep Set (FSTS)": 111,
		"FormID List (FLST)": 91,
		"Furniture (FURN)": 40,
		"Game Setting (GMST)": 3,
		"Global Variable (GLOB)": 9,
		"Grass (GRAS)": 37,
		"Grenade Projectile (PGRE)": 65,
		"Group (GRUP)": 2,
		"Hazard (HAZD)": 51,
		"Head Part (HDPT)": 12,
		"Idle (IDLE)": 78,
		"Idle Marker (IDLM)": 47,
		"Image Space (IMGS)": 89,
		"Image Space Modifier (IMAD)": 90,
		"Impact Data (IPCT)": 100,
		"Impact Data Set (IPDS)": 101,
		"Ingredient (INGR)": 30,
		"Key (KEYM)": 45,
		"Keyword (KYWD)": 4,
		"Land Texture (LTEX)": 20,
		"Landscape (LAND)": 72,
		"Leveled Actor (LVLN)": 44,
		"Leveled Item (LVLI)": 53,
		"Leveled Spell (LVLS)": 82,
		"Light (LIGH)": 31,
		"Lighting Template (LGTM)": 108,
		"Load Screen (LSCR)": 81,
		"Location (LCTN)": 104,
		"Location Reference Type (LCRT)": 5,
		"Main File Header (TES4)": 1,
		"Material Object (MATO)": 126,
		"Material Type (MATT)": 99,
		"Menu Icon": 8,
		"Message (MESG)": 105,
		"Miscellaneous Object (MISC)": 32,
		"Missile Projectile (PMIS)": 63,
		"Movable Static (MSTT)": 36,
		"Movement Type (MOVT)": 127,
		"Music Track (MUST)": 116,
		"Music Type (MUSC)": 109,
		"Navigation (NAVI)": 59,
		"Navigation Mesh (NAVM)": 73,
		"None": 0,
		"Note": 48,
		"Object Reference (REFR)": 61,
		"Outfit (OTFT)": 124,
		"Perk (PERK)": 92,
		"Placed Hazard (PHZD)": 70,
		"Potion (ALCH)": 46,
		"Projectile (PROJ)": 50,
		"Quest (QUST)": 77,
		"Race (RACE)": 14,
		"Ragdoll (RGDL)": 106,
		"Region (REGN)": 58,
		"Relationship (RELA)": 121,
		"Reverb Parameter (REVB)": 134,
		"Scene (SCEN)": 122,
		"Script (SCPT)": 19,
		"Scroll Item (SCRL)": 23,
		"Shader Particle Geometry Data (SPGD)": 56,
		"Shout (SHOU)": 119,
		"Skill": 17,
		"Soul Gem (SLGM)": 52,
		"Sound (SOUN)": 15,
		"Sound Category (SNCT)": 130,
		"Sound Descriptor (SNDR)": 128,
		"Sound Output (SOPM)": 131,
		"Spell (SPEL)": 22,
		"Static (STAT)": 34,
		"Static Collection": 35,
		"Story Manager Branch Node (SMBN)": 112,
		"Story Manager Event Node (SMEN)": 114,
		"Story Manager Quest Node (SMQN)": 113,
		"Talking Activator (TACT)": 25,
		"Texture Set (TXST)": 7,
		"Topic (DIAL)": 75,
		"Topic Info (INFO)": 76,
		"Tree (TREE)": 38,
		"Visual/Reference Effect (RFCT)": 57,
		"Voice Type (VTYP)": 98,
		"Water (WATR)": 84,
		"Weapon (WEAP)": 41,
		"Weather (WTHR)": 54,
		"Word of Power (WOOP)": 118,
		"Worldspace (WRLD)": 71
		}
		return items
"""
class SublimePapyrusSkyrimAnimationEventNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	# http://www.creationkit.com/Animation_Events
	def get_items(self, **args):
		items = {
		# Magic
		"BeginCastRight (magic)": "BeginCastRight",
		"BeginCastLeft (magic)": "BeginCastLeft",
		"MRh_SpellFire_Event (magic)": "MRh_SpellFire_Event",
		"MLh_SpellFire_Event (magic)": "MLh_SpellFire_Event",

		# Hand-to-hand
		"preHitFrame (hand-to-hand)": "preHitFrame",
		"weaponSwing (hand-to-hand)": "weaponSwing",
		"SoundPlay.WPNSwingUnarmed (hand-to-hand)": "SoundPlay.WPNSwingUnarmed",
		"HitFrame (hand-to-hand)": "HitFrame",
		"weaponLeftSwing (hand-to-hand)": "weaponLeftSwing",

		# Bows - Quick draw and shot
		"bowDraw (bows)": "bowDraw",
		"SoundPlay.WPNBowNockSD (bows)": "SoundPlay.WPNBowNockSD",
		"BowZoomStop (bows)": "BowZoomStop",
		"arrowAttach (bows)": "arrowAttach",
		"bowDrawStart (bows)": "bowDrawStart",
		"InitiateWinBegin (bows)": "InitiateWinBegin",
		"BowRelease (bows)": "BowRelease",
		"arrowRelease (bows)": "arrowRelease",
		"tailCombatIdle (bows)": "tailCombatIdle",
		"AttackWinStart (bows)": "AttackWinStart",
		"bowEnd (bows)": "bowEnd",
		"attackStop (bows)": "attackStop",
		"tailCombatState (bows)": "tailCombatState",
		"bowReset (bows)": "bowReset",
		"arrowDetach (bows)": "arrowDetach",
		# Bows - Full draw, held for a moment
		"initiateWinEnd (bows)": "initiateWinEnd",
		"BowDrawn (bows)": "BowDrawn",

		# Blocking
		"tailCombatIdle (blocking)": "tailCombatIdle",
		"SoundPlay.NPCHumanCombatShieldBlock (blocking)": "SoundPlay.NPCHumanCombatShieldBlock",
		"blockStartOut (blocking)": "blockStartOut",
		"SoundPlay.NPCHumanCombatShieldRelease (blocking)": "SoundPlay.NPCHumanCombatShieldRelease",
		"blockStop (blocking)": "blockStop",
		"SoundPlay.NPCHumanCombatShieldBash (blocking)": "SoundPlay.NPCHumanCombatShieldBash",
		"preHitFrame (blocking)": "preHitFrame",
		"HitFrame (blocking)": "HitFrame",
		"FootScuffRight (blocking)": "FootScuffRight",

		# Sneak non-combat
		"tailSneakIdle (sneaking, not in combat)": "tailSneakIdle",
		"tailSneakLocomotion (sneaking, not in combat)": "tailSneakLocomotion",
		"tailMTIdle (sneaking, not in combat)": "tailMTIdle",
		"tailMTLocomotion (sneaking, not in combat)": "tailMTLocomotion",

		# Sneak combat
		"tailSneakIdle (sneaking, in combat)": "tailSneakIdle",
		"tailSneakLocomotion (sneaking, in combat)": "tailSneakLocomotion",
		"tailCombatIdle (sneaking, in combat)": "tailCombatIdle",
		"tailCombatLocomotion (sneaking, in combat)": "tailCombatLocomotion",

		# Water
		"SoundPlay.FSTSwimSwim (swimming)": "SoundPlay.FSTSwimSwim",
		"MTState (swimming)": "MTState",

		# Walking, turning, and jumping
		"Left foot in motion (walking)": "FootLeft",
		"Right foot in motion (walking)": "FootRight",
		"Player begins jumping up (jumping)": "JumpUp",
		"Player begins falling down (jumping/falling)": "JumpFall",
		"Player touches the ground (jumping/falling)": "JumpDown",
		"Player turns left, slowly (turning)": "turnLeftSlow",
		"Player turns left, fast (turning)": "turnLeftFast",
		"Player turns right, slowly (turning)": "turnRightSlow",
		"Player turns right, fast (turning)": "turnRightFast",

		# Sprinting
		"StartAnimatedCameraDelta (sprinting)": "StartAnimatedCameraDelta",
		"attackStop (sprinting)": "attackStop",
		"tailSprint (sprinting)": "tailSprint",
		"FootSprintRight (sprinting)": "FootSprintRight",
		"FootSprintLeft (sprinting)": "FootSprintLeft",
		"EndAnimatedCamera (sprinting)": "EndAnimatedCamera",
		"EndAnimatedCameraDelta (sprinting)": "EndAnimatedCameraDelta",
		}
		return items

"""

class SublimePapyrusSkyrimTrackedStatNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"Locations Discovered": "",
		"Dungeons Cleared": "",
		"Days Passed": "",
		"Hours Slept": "",
		"Hours Waiting": "",
		"Standing Stones Found": "",
		"Gold Found": "",
		"Most Gold Carried": "",
		"Chests Looted": "",
		"Skill Increases": "",
		"Skill Books Read": "",
		"Food Eaten": "",
		"Training Sessions": "",
		"Books Read": "",
		"Horses Owned": "",
		"Houses Owned": "",
		"Stores Invested In": "",
		"Barters": "",
		"Persuasions": "",
		"Bribes": "",
		"Intimidations": "",
		"Diseases Contracted": "",
		"Days as a Vampire": "",
		"Days as a Werewolf": "",
		"Necks Bitten": "",
		"Vampirism Cures": "",
		"Werewolf Transformations": "",
		"Mauls": "",
		"Quests Completed": "",
		"Misc Objectives Completed": "",
		"Main Quests Completed": "",
		"Side Quests Completed": "",
		"The Companions Quests Completed": "",
		"College of Winterhold Quests Completed": "",
		"Thieves' Guild Quests Completed": "",
		"The Dark Brotherhood Quests Completed": "",
		"Civil War Quests Completed": "",
		"Daedric Quests Completed": "",
		"Questlines Completed": "",
		"People Killed": "",
		"Animals Killed": "",
		"Creatures Killed": "",
		"Undead Killed": "",
		"Daedra Killed": "",
		"Automatons Killed": "",
		"Favorite Weapon": "",
		"Critical Strikes": "",
		"Sneak Attacks": "",
		"Backstabs": "",
		"Weapons Disarmed": "",
		"Brawls Won": "",
		"Bunnies Slaughtered": "",
		"Spells Learned": "",
		"Favorite Spell": "",
		"Favorite School": "",
		"Dragon Souls Collected": "",
		"Words Of Power Learned": "",
		"Words Of Power Unlocked": "",
		"Shouts Learned": "",
		"Shouts Unlocked": "",
		"Shouts Mastered": "",
		"Times Shouted": "",
		"Favorite Shout": "",
		"Soul Gems Used": "",
		"Souls Trapped": "",
		"Magic Items Made": "",
		"Weapons Improved": "",
		"Weapons Made": "",
		"Armor Improved": "",
		"Armor Made": "",
		"Potions Mixed": "",
		"Potions Used": "",
		"Poisons Mixed": "",
		"Poisons Used": "",
		"Ingredients Harvested": "",
		"Ingredients Eaten": "",
		"Nirnroots Found": "",
		"Wings Plucked": "",
		"Total Lifetime Bounty": "",
		"Largest Bounty": "",
		"Locks Picked": "",
		"Pockets Picked": "",
		"Items Pickpocketed": "",
		"Times Jailed": "",
		"Days Jailed": "",
		"Fines Paid": "",
		"Jail Escapes": "",
		"Items Stolen": "",
		"Assaults": "",
		"Murders": "",
		"Horses Stolen": "",
		"Trespasses": "",
		"Eastmarch Bounty": "",
		"Falkreath Bounty": "",
		"Haafingar Bounty": "",
		"Hjaalmarch Bounty": "",
		"The Pale Bounty": "",
		"The Reach Bounty": "",
		"The Rift Bounty": "",
		"Tribal Orcs Bounty": "",
		"Whiterun Bounty": "",
		"Winterhold Bounty": ""
		}
		return items

class SublimePapyrusSkyrimBooleanAnimationVariableNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"bMotionDriven": "",
		"IsBeastRace": "",
		"IsSneaking": "",
		"IsBleedingOut": "",
		"IsCastingDual": "",
		"Is1HM": "",
		"IsCastingRight": "",
		"IsCastingLeft": "",
		"IsBlockHit": "",
		"IsPlayer": "",
		"IsNPC": "",
		"bIsSynced": "",
		"bVoiceReady": "",
		"bWantCastLeft": "",
		"bWantCastRight": "",
		"bWantCastVoice": "",
		"b1HM_MLh_attack": "",
		"b1HMCombat": "",
		"bAnimationDriven": "",
		"bCastReady": "",
		"bAllowRotation": "",
		"bMagicDraw": "",
		"bMLh_Ready": "",
		"bMRh_Ready": "",
		"bInMoveState": "",
		"bSprintOK": "",
		"bIdlePlaying": "",
		"bIsDialogueExpressive": "",
		"bAnimObjectLoaded": "",
		"bEquipUnequip": "",
		"bAttached": "",
		"bEquipOK": "",
		"bIsH2HSolo": "",
		"bHeadTracking": "",
		"bIsRiding": "",
		"bTalkable": "",
		"bRitualSpellActive": "",
		"bInJumpState": "",
		"bHeadTrackSpine": "",
		"bLeftHandAttack": "",
		"bIsInMT": "",
		"bHumanoidFootIKEnable": "",
		"bHumanoidFootIKDisable": "",
		"bStaggerPlayerOverride": "",
		"bNoStagger": "",
		"bIsStaffLeftCasting": "",
		"bPerkShieldCharge": "",
		"bPerkQuickShot": "",
		"IsAttacking": "",
		"Isblocking": "",
		"IsBashing": "",
		"IsStaggering": "",
		"IsRecoiling": "",
		"IsEquipping": "",
		"IsUnequipping": ""
		}
		return items

class SublimePapyrusSkyrimFloatAnimationVariableNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"Speed": "",
		"VelocityZ": "",
		"camerafromx": "",
		"camerafromy": "",
		"camerafromz": "",
		"FemaleOffset": "",
		"bodyMorphWeight": "",
		"IsInCastState": "",
		"IsInCastStateDamped": "",
		"blockDown": "",
		"blockLeft": "",
		"blockRight": "",
		"blockUp": "",
		"Direction": "",
		"TurnDelta": "",
		"SpeedWalk": "",
		"SpeedRun": "",
		"fSpeedMin": "",
		"fEquipWeapAdj": "",
		"fIdleTimer": "",
		"fMinSpeed": "",
		"fTwistDirection": "",
		"TurnDeltaDamped": "",
		"TurnMin": "",
		"Pitch": "",
		"PitchLook": "",
		"attackPowerStartTime": "",
		"PitchDefault": "",
		"PitchOverride": "",
		"staggerMagnitude": "",
		"recoilMagnitude": "",
		"SpeedSampled": "",
		"attackComboStartFraction": "",
		"attackIntroLength": "",
		"TimeDelta": "",
		"PitchOffset": "",
		"PitchAcc": "",
		"PitchThresh": "",
		"weapChangeStartFraction": "",
		"RotMax": "",
		"1stPRot": "",
		"1stPRotDamped": "",
		"PitchManualOverride": "",
		"SpeedAcc": ""
		}
		return items

class SublimePapyrusSkyrimIntegerAnimationVariableNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"iSyncIdleLocomotion": "",
		"IsAttackReady_32": "",
		"iRightHandType": "",
		"iWantBlock": "",
		"iAnnotation": "",
		"iSyncTurnState": "",
		"i1stPerson": "",
		"iLeftHandType": "",
		"iState": "",
		"iState_NPCSprinting": "",
		"iState_NPCDefault": "",
		"iState_NPCSneaking": "",
		"iState_NPCBowDrawn :Sets actor in a bow drawn state. *": "",
		"iDualMagicState": "",
		"iState_NPCBlocking": "",
		"iState_NPCBleedout": "",
		"iBlockState": "",
		"iSyncSprintState": "",
		"iIsInSneak": "",
		"iMagicEquipped": "",
		"iEquippedItemState": "",
		"iMagicState": "",
		"iIsDialogueExpressive": "",
		"iSyncIdleState": "",
		"iState_NPC1HM": "",
		"iState_NPC2HM": "",
		"iState_NPCBow": "",
		"iState_NPCMagic": "",
		"iState_NPCMagicCasting": "",
		"iState_NPCHorse": "",
		"iState_HorseSprint": "",
		"iCharacterSelector": "",
		"iCombatStance": "",
		"iSyncTurnDirection": "",
		"iRegularAttack": "",
		"iRightHandEquipped": "",
		"iLeftHandEquipped": "",
		"iIsPlayer": "",
		"iGetUpType": "",
		"iState_NPCAttacking": "",
		"iState_NPCPowerAttacking": "",
		"iState_NPCAttacking2H": "",
		"iDrunkVariable": "",
		"iState_NPCDrunk": "",
		"iTempSwitch": "",
		"iState_NPCBowDrawnQuickShot": "",
		"iState_NPCBlockingShieldCharge": ""
		}
		return items

class SublimePapyrusSkyrimFloatGameSettingNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"fActiveEffectConditionUpdateInterval": "",
		"fActorAlertSoundTimer": "",
		"fActorAlphaFadeSeconds": "",
		"fActorAnimZAdjust": "",
		"fActorArmorDesirabilityDamageMult": "",
		"fActorArmorDesirabilitySkillMult": "",
		"fActorDefaultTurningSpeed": "",
		"fActorLeaveWaterBreathTimer": "",
		"fActorLuckSkillMult": "",
		"fActorStrengthEncumbranceMult": "",
		"fActorSwimBreathBase": "",
		"fActorSwimBreathDamage": "",
		"fActorSwimBreathMult": "",
		"fActorTeleportFadeSeconds": "",
		"fActorWeaponDesirabilityDamageMult": "",
		"fActorWeaponDesirabilitySkillMult": "",
		"fAddictionUsageMonitorThreshold": "",
		"fAiAcquireKillBase": "",
		"fAiAcquireKillMult": "",
		"fAIAcquireObjectDistance": "",
		"fAiAcquirePickBase": "",
		"fAiAcquirePickMult": "",
		"fAiAcquireStealBase": "",
		"fAiAcquireStealMult": "",
		"fAIActivateHeight": "",
		"fAIActivateReach": "",
		"fAIActorPackTargetHeadTrackMod": "",
		"fAIAimBlockedHalfCircleRadius": "",
		"fAIAimBlockedToleranceDegrees": "",
		"fAIAwareofPlayerTimer": "",
		"fAIBestHeadTrackDistance": "",
		"fAICombatFleeScoreThreshold": "",
		"fAICombatNoAreaEffectAllyDistance": "",
		"fAICombatNoTargetLOSPriorityMult": "",
		"fAICombatSlopeDifference": "",
		"fAICombatTargetUnreachablePriorityMult": "",
		"fAICombatUnreachableTargetPriorityMult": "",
		"fAICommentTimeWindow": "",
		"fAIConversationExploreTime": "",
		"fAIDefaultSpeechMult": "",
		"fAIDialogueDistance": "",
		"fAIDistanceRadiusMinLocation": "",
		"fAIDistanceTeammateDrawWeapon": "",
		"fAIDodgeDecisionBase": "",
		"fAIDodgeFavorLeftRightMult": "",
		"fAIDodgeVerticalRangedAttackMult": "",
		"fAIDodgeWalkChance": "",
		"fAIEnergyLevelBase": "",
		"fAIEngergyLevelMult": "",
		"fAIEscortFastTravelMaxDistFromPath": "",
		"fAIEscortHysteresisWidth": "",
		"fAIEscortStartStopDelayTime": "",
		"fAIEscortWaitDistanceExterior": "",
		"fAIEscortWaitDistanceInterior": "",
		"fAIExclusiveGreetingTimer": "",
		"fAIExplosiveWeaponDamageMult": "",
		"fAIExplosiveWeaponRangeMult": "",
		"fAIExteriorSpectatorDetection": "",
		"fAIExteriorSpectatorDistance": "",
		"fAIFaceTargetAnimationAngle": "",
		"fAIFindBedChairsDistance": "",
		"fAIFleeConfBase": "",
		"fAIFleeConfMult": "",
		"fAIFleeHealthMult": "",
		"fAIFleeSuccessTimeout": "",
		"fAIForceGreetingTimer": "",
		"fAIFurnitureDestinationRadius": "",
		"fAIGreetingTimer": "",
		"fAIHeadTrackDialogueOffsetRandomValue": "",
		"fAIHeadTrackDialoguePickNewOffsetTimer": "",
		"fAIHeadTrackDialogueResetPositionTimer": "",
		"fAIHeadTrackDialogueStayInOffsetMax": "",
		"fAIHeadTrackDialogueStayInOffsetMin": "",
		"fAIHeadTrackOffsetRandomValueMax": "",
		"fAIHeadTrackOffsetRandomValueMin": "",
		"fAIHeadTrackPickNewOffsetTimer": "",
		"fAIHeadTrackResetPositionTimer": "",
		"fAIHeadTrackStayInOffsetMax": "",
		"fAIHeadTrackStayInOffsetMin": "",
		"fAIHoldDefaultHeadTrackTimer": "",
		"fAIHorseSearchDistance": "",
		"fAIIdleAnimationDistance": "",
		"fAIIdleAnimationLargeCreatureDistanceMult3.000000": "",
		"fAIIdleWaitTimeComplexScene": "",
		"fAIIdleWaitTime": "",
		"fAIInDialogueModeWithPlayerDistance": "",
		"fAIInDialogueModewithPlayerTimer": "",
		"fAIInteriorHeadTrackMult": "",
		"fAIInteriorSpectatorDetection": "",
		"fAIInteriorSpectatorDistance": "",
		"fAILockDoorsSeenRecentlySeconds": "",
		"fAIMagicSpellMult": "",
		"fAIMagicTimer": "",
		"fAIMarkerDestinationRadius": "",
		"fAIMaxAngleRangeMovingToStartSceneDialogue": "",
		"fAIMaxHeadTrackDistanceFromPC": "",
		"fAIMaxHeadTrackDistance": "",
		"fAIMaxLargeCreatureHeadTrackDistance": "",
		"fAIMaxSmileDistance": "",
		"fAIMaxWanderTime": "",
		"fAIMeleeArmorMult": "",
		"fAIMeleeHandMult": "",
		"fAIMinAngleRangeToStartSceneDialogue": "",
		"fAIMinGreetingDistance": "",
		"fAIMinLocationHeight": "",
		"fAIMoveDistanceToRecalcFollowPath": "",
		"fAIMoveDistanceToRecalcTravelPath": "",
		"fAIMoveDistanceToRecalcTravelToActor": "",
		"fAIPatrolHysteresisWidth": "",
		"fAIPatrolMinSecondsAtNormalFurniture": "",
		"fAIPowerAttackCreatureChance": "",
		"fAIPowerAttackKnockdownBonus": "",
		"fAIPowerAttackNPCChance": "",
		"fAIPowerAttackRecoilBonus": "",
		"fAIPursueDistanceLineOfSight": "",
		"fAIRandomizeInitialLocationMinRadius": "",
		"fAIRangedWeaponMult": "",
		"fAIRangMagicSpellMult": "",
		"fAIRevertToScriptTracking": "",
		"fAIShoutMinAimSeconds": "",
		"fAIShoutRetryDelaySeconds": "",
		"fAIShoutToleranceDegrees": "",
		"fAISocialchanceForConversationInterior": "",
		"fAISocialchanceForConversation": "",
		"fAISocialRadiusToTriggerConversationInterior": "",
		"fAISocialRadiusToTriggerConversation": "",
		"fAISocialTimerForConversationsMax": "",
		"fAISocialTimerForConversationsMin": "",
		"fAISocialTimerToWaitForEvent": "",
		"fAISpectatorCommentTimer": "",
		"fAISpectatorRememberThreatTimer": "",
		"fAISpectatorShutdownDistance": "",
		"fAISpectatorThreatDistExplosion": "",
		"fAISpectatorThreatDistMelee": "",
		"fAISpectatorThreatDistMine": "",
		"fAISpectatorThreatDistRanged": "",
		"fAIStayonScriptHeadtrack": "",
		"fAItalktoNPCtimer": "",
		"fAItalktosameNPCtimer": "",
		"fAITrespassWarningTimer": "",
		"fAIUpdateMovementRestrictionsDistance": "",
		"fAIUseMagicToleranceDegrees": "",
		"fAIUseWeaponAnimationTimeoutSeconds": "",
		"fAIUseWeaponDistance": "",
		"fAIUseWeaponToleranceDegrees": "",
		"fAIWaitingforScriptCallback": "",
		"fAIWalkAwayTimerForConversation": "",
		"fAIWanderDefaultMinDist": "",
		"fAlchemyGoldMult": "",
		"fAlchemyIngredientInitMult": "",
		"fAlchemySkillFactor": "",
		"fAmbushOverRideRadiusforPlayerDetection": "",
		"fArmorBaseFactor": "",
		"fArmorRatingBase": "",
		"fArmorRatingMax": "",
		"fArmorRatingPCBase": "",
		"fArmorRatingPCMax": "",
		"fArmorScalingFactor": "",
		"fArmorWeightLightMaxMod": "",
		"fArrowBounceBlockPercentage": "",
		"fArrowBounceLinearSpeed": "",
		"fArrowBounceRotateSpeed": "",
		"fArrowBowFastMult": "",
		"fArrowBowMinTime": "",
		"fArrowBowSlowMult": "",
		"fArrowFakeMass": "",
		"fArrowGravityBase": "",
		"fArrowGravityMin": "",
		"fArrowGravityMult": "",
		"fArrowMaxDistance": "",
		"fArrowMinBowVelocity": "",
		"fArrowMinDistanceForTrails": "",
		"fArrowMinPower": "",
		"fArrowMinSpeedForTrails": "",
		"fArrowMinVelocity": "",
		"fArrowOptimalDistance": "",
		"fArrowSpeedMult": "",
		"fArrowWeakGravity": "",
		"fAuroraFadeInStart": "",
		"fAuroraFadeOutStart": "",
		"fAutoAimMaxDegrees3rdPerson": "",
		"fAutoAimMaxDegreesMelee": "",
		"fAutoAimMaxDegreesVATS": "",
		"fAutoAimMaxDegrees": "",
		"fAutoAimMaxDistance": "",
		"fAutoAimScreenPercentage": "",
		"fAutomaticWeaponBurstCooldownTime": "",
		"fAutomaticWeaponBurstFireTime": "",
		"fAutoraFadeIn": "",
		"fAutoraFadeOut": "",
		"fAvoidPlayerDistance": "",
		"fBarterBuyMin": "",
		"fBarterMax": "",
		"fBarterMin": "",
		"fBarterSellMax": "",
		"fBeamWidthDefault": "",
		"fBigBumpSpeed": "",
		"fBleedoutCheck": "",
		"fBleedoutDefault": "",
		"fBleedoutMin": "",
		"fBleedoutRate": "",
		"fBleedoutRecover": "",
		"fBlinkDelayMax": "",
		"fBlinkDelayMin": "",
		"fBlinkDownTime": "",
		"fBlinkUpTime": "",
		"fBlockAmountHandToHandMult": "",
		"fBlockAmountWeaponMult": "",
		"fBlockMax": "",
		"fBlockPowerAttackMult": "",
		"fBlockScoreNoShieldMult": "",
		"fBlockSkillBase": "",
		"fBlockSkillMult": "",
		"fBlockWeaponBase": "",
		"fBlockWeaponScaling": "",
		"fBloodSplatterCountBase": "",
		"fBloodSplatterCountDamageBase": "",
		"fBloodSplatterCountDamageMult": "",
		"fBloodSplatterCountRandomMargin": "",
		"fBloodSplatterDuration": "",
		"fBloodSplatterFadeStart": "",
		"fBloodSplatterFlareMult": "",
		"fBloodSplatterFlareOffsetScale": "",
		"fBloodSplatterFlareSize": "",
		"fBloodSplatterMaxOpacity2": "",
		"fBloodSplatterMaxOpacity": "",
		"fBloodSplatterMaxSize": "",
		"fBloodSplatterMinOpacity2": "",
		"fBloodSplatterMinOpacity": "",
		"fBloodSplatterMinSize": "",
		"fBloodSplatterOpacityChance": "",
		"fBowDrawTime": "",
		"fBowHoldTimer": "",
		"fBowNPCSpreadAngle": "",
		"fBowZoomStaminaDrainMult": "",
		"fBowZoomStaminaRegenDelay": "",
		"fBribeBase": "",
		"fBribeCostCurve": "",
		"fBribeMoralityMult": "",
		"fBribeMult": "",
		"fBribeNPCLevelMult": "",
		"fBribeScale": "",
		"fBribeSpeechcraftMult": "",
		"fBumpReactionIdealMoveDist": "",
		"fBumpReactionMinMoveDist": "",
		"fBumpReactionSmallDelayTime": "",
		"fBumpReactionSmallWaitTimer": "",
		"fBuoyancyMultBody": "",
		"fBuoyancyMultExtremity": "",
		"fCameraShakeDistFadeDelta": "",
		"fCameraShakeDistFadeStart": "",
		"fCameraShakeDistMin": "",
		"fCameraShakeExplosionDistMult": "",
		"fCameraShakeFadeTime": "",
		"fCameraShakeMultMin": "",
		"fCameraShakeTime": "",
		"fChaseDetectionTimerSetting": "",
		"fCheckDeadBodyTimer": "",
		"fCheckPositionFallDistance": "",
		"fClosetoPlayerDistance": "",
		"fClothingArmorBase": "",
		"fClothingArmorScale": "",
		"fClothingBase": "",
		"fClothingClassScale": "",
		"fClothingJewelryBase": "",
		"fClothingJewelryScale": "",
		"fCombatAbsoluteMaxRangeMult": "",
		"fCombatAcquirePickupAnimationDelay": "",
		"fCombatAcquireWeaponAmmoMinimumScoreMult": "",
		"fCombatAcquireWeaponAvoidTargetRadius": "",
		"fCombatAcquireWeaponCloseDistanceMax": "",
		"fCombatAcquireWeaponCloseDistanceMin": "",
		"fCombatAcquireWeaponDisarmedAcquireTime": "",
		"fCombatAcquireWeaponDisarmedDistanceMax": "",
		"fCombatAcquireWeaponDisarmedDistanceMin": "",
		"fCombatAcquireWeaponDisarmedTime": "",
		"fCombatAcquireWeaponEnchantmentChargeMult": "",
		"fCombatAcquireWeaponFindAmmoDistance": "",
		"fCombatAcquireWeaponMeleeScoreMult": "",
		"fCombatAcquireWeaponMinimumScoreMult": "",
		"fCombatAcquireWeaponMinimumTargetDistance": "",
		"fCombatAcquireWeaponRangedDistanceMax": "",
		"fCombatAcquireWeaponRangedDistanceMin": "",
		"fCombatAcquireWeaponReachDistance": "",
		"fCombatAcquireWeaponScoreCostMult": "",
		"fCombatAcquireWeaponScoreRatioMax": "",
		"fCombatAcquireWeaponSearchFailedDelay": "",
		"fCombatAcquireWeaponSearchRadiusBuffer": "",
		"fCombatAcquireWeaponSearchSuccessDelay": "",
		"fCombatAcquireWeaponTargetDistanceCheck": "",
		"fCombatAcquireWeaponUnarmedDistanceMax": "",
		"fCombatAcquireWeaponUnarmedDistanceMin": "",
		"fCombatActiveCombatantAttackRangeDistance": "",
		"fCombatActiveCombatantLastSeenTime": "",
		"fCombatAdvanceInnerRadiusMax": "",
		"fCombatAdvanceInnerRadiusMid": "",
		"fCombatAdvanceInnerRadiusMin": "",
		"fCombatAdvanceLastDamagedThreshold": "",
		"fCombatAdvanceNormalAttackChance": "",
		"fCombatAdvanceOuterRadiusMax": "",
		"fCombatAdvanceOuterRadiusMid": "",
		"fCombatAdvanceOuterRadiusMin": "",
		"fCombatAdvancePathRetryTime": "",
		"fCombatAdvanceRadiusStaggerMult": "",
		"fCombatAimDeltaThreshold": "",
		"fCombatAimLastSeenLocationTimeLimit": "",
		"fCombatAimMeleeHighPriorityUpdateTime": "",
		"fCombatAimMeleeUpdateTime": "",
		"fCombatAimProjectileBlockedTime": "",
		"fCombatAimProjectileBlockedTime": "",
		"fCombatAimProjectileGroundMinRadius": "",
		"fCombatAimProjectileRandomOffset": "",
		"fCombatAimProjectileUpdateTime": "",
		"fCombatAimTrackTargetUpdateTime": "",
		"fCombatAngleTolerance": "",
		"fCombatAnticipatedLocationCheckDistance": "",
		"fCombatAnticipateTime": "",
		"fCombatApproachTargetSlowdownDecelerationMult": "",
		"fCombatApproachTargetSlowdownDistance": "",
		"fCombatApproachTargetSlowdownUpdateTime": "",
		"fCombatApproachTargetSlowdownVelocityAngle": "",
		"fCombatApproachTargetSprintStopMovingRange": "",
		"fCombatApproachTargetSprintStopRange": "",
		"fCombatApproachTargetUpdateTime": "",
		"fCombatAreaHoldPositionMinimumRadius": "",
		"fCombatAreaStandardAttackedRadius": "",
		"fCombatAreaStandardAttackedTime": "",
		"fCombatAreaStandardCheckViewConeDistanceMax": "",
		"fCombatAreaStandardCheckViewConeDistanceMin": "",
		"fCombatAreaStandardFlyingRadiusMult": "",
		"fCombatAreaStandardRadius": "",
		"fCombatAttackAllowedOverrunDistance": "",
		"fCombatAttackAnimationDrivenDelayTime": "",
		"fCombatAttackAnticipatedDistanceMin": "",
		"fCombatAttackChanceBlockingMultMax": "",
		"fCombatAttackChanceBlockingMultMin": "",
		"fCombatAttackChanceBlockingSwingMult": "",
		"fCombatAttackChanceLastAttackBonusTime": "",
		"fCombatAttackChanceLastAttackBonus": "",
		"fCombatAttackChanceMax": "",
		"fCombatAttackChanceMin": "",
		"fCombatAttackCheckTargetRangeDistance": "",
		"fCombatAttackMovingAttackDistance": "",
		"fCombatAttackMovingAttackReachMult": "",
		"fCombatAttackMovingStrikeAngleMult": "",
		"fCombatAttackPlayerAnticipateMult": "",
		"fCombatAttackStationaryAttackDistance": "",
		"fCombatAttackStrikeAngleMult": "",
		"fCombatAvoidThreatsChance": "",
		"fCombatBackoffChance": "",
		"fCombatBackoffMinDistanceMult": "",
		"fCombatBashChanceMax": "",
		"fCombatBashChanceMin": "",
		"fCombatBashReach": "",
		"fCombatBashTargetBlockingMult": "",
		"fCombatBetweenAdvanceTimer": "",
		"fCombatBlockAttackChanceMax": "",
		"fCombatBlockAttackChanceMin": "",
		"fCombatBlockAttackReachMult": "",
		"fCombatBlockAttackStrikeAngleMult": "",
		"fCombatBlockChanceMax": "",
		"fCombatBlockChanceMin": "",
		"fCombatBlockChanceWeaponMult": "",
		"fCombatBlockMaxTargetRetreatVelocity": "",
		"fCombatBlockStartDistanceMax": "",
		"fCombatBlockStartDistanceMin": "",
		"fCombatBlockStopDistanceMax": "",
		"fCombatBlockStopDistanceMin": "",
		"fCombatBlockTimeMax": "",
		"fCombatBlockTimeMid": "",
		"fCombatBlockTimeMin": "",
		"fCombatBoundWeaponDPSBonus": "",
		"fCombatBuffMaxTimer": "",
		"fCombatBuffStandoffTimer": "",
		"fCombatCastConcentrationOffensiveMagicCastTimeMax": "",
		"fCombatCastConcentrationOffensiveMagicCastTimeMin": "",
		"fCombatCastConcentrationOffensiveMagicChanceMax": "",
		"fCombatCastConcentrationOffensiveMagicChanceMin": "",
		"fCombatCastConcentrationOffensiveMagicWaitTimeMax": "",
		"fCombatCastConcentrationOffensiveMagicWaitTimeMin": "",
		"fCombatCastImmediateOffensiveMagicChanceMax": "",
		"fCombatCastImmediateOffensiveMagicChanceMin": "",
		"fCombatCastImmediateOffensiveMagicHoldTimeAbsoluteMin": "",
		"fCombatCastImmediateOffensiveMagicHoldTimeMax": "",
		"fCombatCastImmediateOffensiveMagicHoldTimeMinDistance": "",
		"fCombatCastImmediateOffensiveMagicHoldTimeMin": "",
		"fCombatChangeProcessFaceTargetDistance": "",
		"fCombatCircleAngleMax": "",
		"fCombatCircleAngleMin": "",
		"fCombatCircleAnglePlayerMult": "",
		"fCombatCircleChanceMax": "",
		"fCombatCircleChanceMin": "",
		"fCombatCircleDistanceMax": "",
		"fCombatCircleDistantChanceMax": "",
		"fCombatCircleDistantChanceMin": "",
		"fCombatCircleMinDistanceMult": "",
		"fCombatCircleMinDistanceRadiusMult": "",
		"fCombatCircleMinMovementDistance": "",
		"fCombatCircleViewConeAngle": "",
		"fCombatCloseRangeTrackTargetDistance": "",
		"fCombatClusterUpdateTime": "",
		"fCombatCollectAlliesTimer": "",
		"fCombatConfidenceModifierMax": "",
		"fCombatConfidenceModifierMin": "",
		"fCombatCoverAttackMaxWaitTime": "",
		"fCombatCoverAttackOffsetDistance": "",
		"fCombatCoverAttackTimeMax": "",
		"fCombatCoverAttackTimeMid": "",
		"fCombatCoverAttackTimeMin": "",
		"fCombatCoverAvoidTargetRadius": "",
		"fCombatCoverCheckCoverHeightMin": "",
		"fCombatCoverCheckCoverHeightOffset": "",
		"fCombatCoverEdgeOffsetDistance": "",
		"fCombatCoverLedgeOffsetDistance": "",
		"fCombatCoverMaxRangeMult": "",
		"fCombatCoverMidPointMaxRangeBuffer": "",
		"fCombatCoverMinimumActiveRange": "",
		"fCombatCoverMinimumRange": "",
		"fCombatCoverObstacleMovedTime": "",
		"fCombatCoverRangeMaxActiveMult": "",
		"fCombatCoverRangeMaxBufferDistance": "",
		"fCombatCoverRangeMinActiveMult": "",
		"fCombatCoverRangeMinBufferDistance": "",
		"fCombatCoverReservationWidthMult": "",
		"fCombatCoverSearchDistanceMax": "",
		"fCombatCoverSearchDistanceMin": "",
		"fCombatCoverSearchFailedDelay": "",
		"fCombatCoverSecondaryThreatLastSeenTime": "",
		"fCombatCoverSecondaryThreatMinDistance": "",
		"fCombatCoverWaitLookOffsetDistance": "",
		"fCombatCoverWaitTimeMax": "",
		"fCombatCoverWaitTimeMid": "",
		"fCombatCoverWaitTimeMin": "",
		"fCombatCurrentWeaponAbsoluteMaxRangeMult": "",
		"fCombatDamageBonusMeleeSneakingMult": "",
		"fCombatDamageBonusSneakingMult": "",
		"fCombatDamageScale": "",
		"fCombatDeadActorHitConeMult": "",
		"fCombatDetectionDialogueIdleMaxElapsedTime": "",
		"fCombatDetectionDialogueIdleMinElapsedTime": "",
		"fCombatDetectionDialogueMaxElapsedTime": "",
		"fCombatDetectionDialogueMinElapsedTime": "",
		"fCombatDetectionFleeingLostRemoveTime": "",
		"fCombatDetectionLostCheckNoticedDistance": "",
		"fCombatDetectionLostRemoveDistanceTime": "",
		"fCombatDetectionLostRemoveDistance": "",
		"fCombatDetectionLostRemoveTime": "",
		"fCombatDetectionLostTimeLimit": "",
		"fCombatDetectionLowDetectionDistance": "",
		"fCombatDetectionLowPriorityDistance": "",
		"fCombatDetectionNoticedDistanceLimit": "",
		"fCombatDetectionNoticedTimeLimit": "",
		"fCombatDetectionVeryLowPriorityDistance": "",
		"fCombatDialogueAllyKilledDistanceMult": "",
		"fCombatDialogueAllyKilledMaxElapsedTime": "",
		"fCombatDialogueAllyKilledMinElapsedTime": "",
		"fCombatDialogueAttackDistanceMult": "",
		"fCombatDialogueAttackMaxElapsedTime": "",
		"fCombatDialogueAttackMinElapsedTime": "",
		"fCombatDialogueAvoidThreatDistanceMult": "",
		"fCombatDialogueAvoidThreatMaxElapsedTime": "",
		"fCombatDialogueAvoidThreatMinElapsedTime": "",
		"fCombatDialogueBashDistanceMult": "",
		"fCombatDialogueBleedoutDistanceMult": "",
		"fCombatDialogueBleedOutMaxElapsedTime": "",
		"fCombatDialogueBleedOutMinElapsedTime": "",
		"fCombatDialogueBlockDistanceMult": "",
		"fCombatDialogueDeathDistanceMult": "",
		"fCombatDialogueFleeDistanceMult": "",
		"fCombatDialogueFleeMaxElapsedTime": "",
		"fCombatDialogueFleeMinElapsedTime": "",
		"fCombatDialogueGroupStrategyDistanceMult": "",
		"fCombatDialogueHitDistanceMult": "",
		"fCombatDialoguePowerAttackDistanceMult": "",
		"fCombatDialogueTauntDistanceMult": "",
		"fCombatDialogueTauntMaxElapsedTime": "",
		"fCombatDialogueTauntMinElapsedTime": "",
		"fCombatDisarmedFindBetterWeaponInitialTime": "",
		"fCombatDisarmedFindBetterWeaponTime": "",
		"fCombatDismemberedLimbVelocity": "",
		"fCombatDistanceMin": "",
		"fCombatDistance": "",
		"fCombatDiveBombChanceMax": "",
		"fCombatDiveBombChanceMin": "",
		"fCombatDiveBombOffsetPercent": "",
		"fCombatDiveBombSlowDownDistance": "",
		"fCombatDodgeAccelerationMult": "",
		"fCombatDodgeAcceptableThreatScoreMult": "",
		"fCombatDodgeAnticipateThreatTime": "",
		"fCombatDodgeBufferDistance": "",
		"fCombatDodgeChanceMax": "",
		"fCombatDodgeChanceMin": "",
		"fCombatDodgeDecelerationMult": "",
		"fCombatDodgeMovingReactionTime": "",
		"fCombatDodgeReactionTime": "",
		"fCombatDPSBowSpeedMult": "",
		"fCombatDPSMeleeSpeedMult": "",
		"fCombatEffectiveDistanceAnticipateTime": "",
		"fCombatEnvironmentBloodChance": "",
		"fCombatFallbackChanceMax": "",
		"fCombatFallbackChanceMin": "",
		"fCombatFallbackDistanceMax": "",
		"fCombatFallbackDistanceMin": "",
		"fCombatFallbackMaxAngle": "",
		"fCombatFallbackMinMovementDistance": "",
		"fCombatFallbackWaitTimeMax": "",
		"fCombatFallbackWaitTimeMin": "",
		"fCombatFindAllyAttackLocationAllyRadius": "",
		"fCombatFindAllyAttackLocationDistanceMax": "",
		"fCombatFindAllyAttackLocationDistanceMin": "",
		"fCombatFindAttackLocationAvoidTargetRadius": "",
		"fCombatFindAttackLocationDistance": "",
		"fCombatFindAttackLocationKeyAngle": "",
		"fCombatFindAttackLocationKeyHeight": "",
		"fCombatFindBetterWeaponTime": "",
		"fCombatFindLateralAttackLocationDistance": "",
		"fCombatFindLateralAttackLocationIntervalMax": "",
		"fCombatFindLateralAttackLocationIntervalMin": "",
		"fCombatFiringArcStationaryTurnMult": "",
		"fCombatFlankingAngleOffsetCostMult": "",
		"fCombatFlankingAngleOffsetMax": "",
		"fCombatFlankingAngleOffset": "",
		"fCombatFlankingDirectionDistanceMult": "",
		"fCombatFlankingDirectionGoalAngleOffset": "",
		"fCombatFlankingDirectionOffsetCostMult": "",
		"fCombatFlankingDirectionRotateAngleOffset": "",
		"fCombatFlankingDistanceMax": "",
		"fCombatFlankingDistanceMin": "",
		"fCombatFlankingGoalAngleFarMaxDistance": "",
		"fCombatFlankingGoalAngleFarMax": "",
		"fCombatFlankingGoalAngleFarMinDistance": "",
		"fCombatFlankingGoalAngleFarMin": "",
		"fCombatFlankingGoalAngleNear": "",
		"fCombatFlankingGoalCheckDistanceMax": "",
		"fCombatFlankingGoalCheckDistanceMin": "",
		"fCombatFlankingGoalCheckDistanceMult": "",
		"fCombatFlankingLocationGridSize": "",
		"fCombatFlankingMaxTurnAngleGoal": "",
		"fCombatFlankingMaxTurnAngle": "",
		"fCombatFlankingNearDistance": "",
		"fCombatFlankingRotateAngle": "",
		"fCombatFlankingStalkRange": "",
		"fCombatFlankingStalkTimeMax": "",
		"fCombatFlankingStalkTimeMin": "",
		"fCombatFlankingStepDistanceMax": "",
		"fCombatFlankingStepDistanceMin": "",
		"fCombatFlankingStepDistanceMult": "",
		"fCombatFleeAllyDistanceMax": "",
		"fCombatFleeAllyDistanceMin": "",
		"fCombatFleeAllyRadius": "",
		"fCombatFleeCoverMinDistance": "",
		"fCombatFleeCoverSearchRadius": "",
		"fCombatFleeDistanceExterior": "",
		"fCombatFleeDistanceInterior": "",
		"fCombatFleeDoorDistanceMax": "",
		"fCombatFleeDoorTargetCheckDistance": "",
		"fCombatFleeInitialDoorRestrictChance": "",
		"fCombatFleeLastDoorRestrictTime": "",
		"fCombatFleeTargetAvoidRadius": "",
		"fCombatFleeTargetGatherRadius": "",
		"fCombatFleeUseDoorChance": "",
		"fCombatFleeUseDoorRestrictTime": "",
		"fCombatFlightEffectiveDistance": "",
		"fCombatFlightMinimumRange": "",
		"fCombatFlyingAttackChanceMax": "",
		"fCombatFlyingAttackChanceMin": "",
		"fCombatFlyingAttackTargetDistanceThreshold": "",
		"fCombatFollowRadiusBase": "",
		"fCombatFollowRadiusMin": "",
		"fCombatFollowRadiusMult": "",
		"fCombatFollowSneakFollowRadius": "",
		"fCombatForwardAttackChance": "",
		"fCombatGiantCreatureReachMult": "",
		"fCombatGrenadeBounceTimeMax": "",
		"fCombatGrenadeBounceTimeMin": "",
		"fCombatGroundAttackChanceMax": "",
		"fCombatGroundAttackChanceMin": "",
		"fCombatGroundAttackTimeMax": "",
		"fCombatGroundAttackTimeMin": "",
		"fCombatGroupCombatStrengthUpdateTime": "",
		"fCombatGroupOffensiveMultMin": "",
		"fCombatGuardFollowBufferDistance": "",
		"fCombatGuardRadiusMin": "",
		"fCombatGuardRadiusMult": "",
		"fCombatHealthRegenRateMult": "",
		"fCombatHideCheckViewConeDistanceMax": "",
		"fCombatHideCheckViewConeDistanceMin": "",
		"fCombatHideFailedTargetDistance": "",
		"fCombatHideFailedTargetLOSDistance": "",
		"fCombatHitConeAngle": "",
		"fCombatHoverAngleLimit": "",
		"fCombatHoverAngleMax": "",
		"fCombatHoverAngleMin": "",
		"fCombatHoverChanceMax": "",
		"fCombatHoverChanceMin": "",
		"fCombatHoverTimeMax": "",
		"fCombatHoverTimeMin": "",
		"fCombatInTheWayTimer": "",
		"fCombatInventoryDesiredRangeScoreMultMax": "",
		"fCombatInventoryDesiredRangeScoreMultMid": "",
		"fCombatInventoryDesiredRangeScoreMultMin": "",
		"fCombatInventoryDualWieldScorePenalty": "",
		"fCombatInventoryEquipmentMinScoreMult": "",
		"fCombatInventoryEquippedScoreBonus": "",
		"fCombatInventoryMaxRangeEquippedBonus": "",
		"fCombatInventoryMaxRangeScoreMult": "",
		"fCombatInventoryMeleeEquipRange": "",
		"fCombatInventoryMinEquipTimeBlock": "",
		"fCombatInventoryMinEquipTimeDefault": "",
		"fCombatInventoryMinEquipTimeMagic": "",
		"fCombatInventoryMinEquipTimeShout": "",
		"fCombatInventoryMinEquipTimeStaff": "",
		"fCombatInventoryMinEquipTimeTorch": "",
		"fCombatInventoryMinEquipTimeWeapon": "",
		"fCombatInventoryMinRangeScoreMult": "",
		"fCombatInventoryMinRangeUnequippedBonus": "",
		"fCombatInventoryOptimalRangePercent": "",
		"fCombatInventoryRangedScoreMult": "",
		"fCombatInventoryResourceCurrentRequiredMult": "",
		"fCombatInventoryResourceDesiredRequiredMult": "",
		"fCombatInventoryResourceRegenTime": "",
		"fCombatInventoryShieldEquipRange": "",
		"fCombatInventoryShoutMaxRecoveryTime": "",
		"fCombatInventoryTorchEquipRange": "",
		"fCombatInventoryUpdateTimer": "",
		"fCombatIronSightsDistance": "",
		"fCombatIronSightsRangeMult": "",
		"fCombatItemBuffTimer": "",
		"fCombatItemRestoreTimer": "",
		"fCombatKillMoveDamageMult": "",
		"fCombatLandingAvoidActorRadius": "",
		"fCombatLandingSearchDistance": "",
		"fCombatLandingZoneDistance": "",
		"fCombatLineOfSightTimer": "",
		"fCombatLocationTargetRadiusMin": "",
		"fCombatLowFleeingTargetHitPercent": "",
		"fCombatLowMaxAttackDistance": "",
		"fCombatLowTargetHitPercent": "",
		"fCombatMagicArmorDistanceMax": "",
		"fCombatMagicArmorDistanceMin": "",
		"fCombatMagicArmorMinCastTime": "",
		"fCombatMagicBoundItemDistance": "",
		"fCombatMagicBuffDuration": "",
		"fCombatMagicCloakDistanceMax": "",
		"fCombatMagicCloakDistanceMin": "",
		"fCombatMagicCloakMinCastTime": "",
		"fCombatMagicConcentrationAimVariance": "",
		"fCombatMagicConcentrationFiringArcMult": "",
		"fCombatMagicConcentrationMinCastTime": "",
		"fCombatMagicConcentrationScoreDuration": "",
		"fCombatMagicDefaultLongDuration": "",
		"fCombatMagicDefaultMinCastTime": "",
		"fCombatMagicDefaultShortDuration": "",
		"fCombatMagicDisarmDistance": "",
		"fCombatMagicDisarmRestrictTime": "",
		"fCombatMagicDrinkPotionWaitTime": "",
		"fCombatMagicDualCastChance": "",
		"fCombatMagicDualCastInterruptTime": "",
		"fCombatMagicImmediateAimVariance": "",
		"fCombatMagicInvisibilityDistance": "",
		"fCombatMagicInvisibilityMinCastTime": "",
		"fCombatMagickaRegenRateMult": "",
		"fCombatMagicLightMinCastTime": "",
		"fCombatMagicOffensiveMinCastTime": "",
		"fCombatMagicParalyzeDistance": "",
		"fCombatMagicParalyzeMinCastTime": "",
		"fCombatMagicParalyzeRestrictTime": "",
		"fCombatMagicProjectileFiringArc": "",
		"fCombatMagicReanimateDistance": "",
		"fCombatMagicReanimateMinCastTime": "",
		"fCombatMagicReanimateRestrictTime": "",
		"fCombatMagicStaggerDistance": "",
		"fCombatMagicSummonMinCastTime": "",
		"fCombatMagicSummonRestrictTime": "",
		"fCombatMagicTargetEffectMinCastTime": "",
		"fCombatMagicWardAttackRangeDistance": "",
		"fCombatMagicWardAttackReachMult": "",
		"fCombatMagicWardCooldownTime": "",
		"fCombatMagicWardMagickaCastLimit": "",
		"fCombatMagicWardMagickaEquipLimit": "",
		"fCombatMagicWardMinCastTime": "",
		"fCombatMaintainOptimalDistanceMaxAngle": "",
		"fCombatMaintainRangeDistanceMin": "",
		"fCombatMaxHoldScore": "",
		"fCombatMaximumOptimalRangeMax": "",
		"fCombatMaximumOptimalRangeMid": "",
		"fCombatMaximumOptimalRangeMin": "",
		"fCombatMaximumProjectileRange": "",
		"fCombatMaximumRange": "",
		"fCombatMeleeTrackTargetDistanceMax": "",
		"fCombatMeleeTrackTargetDistanceMin": "",
		"fCombatMinEngageDistance": "",
		"fCombatMissileImpaleDepth": "",
		"fCombatMissileStickDepth": "",
		"fCombatMonitorBuffsTimer": "",
		"fCombatMoveToActorBufferDistance": "",
		"fCombatMusicGroupThreatRatioMax": "",
		"fCombatMusicGroupThreatRatioMin": "",
		"fCombatMusicGroupThreatRatioTimer": "",
		"fCombatMusicNearCombatInnerRadius": "",
		"fCombatMusicNearCombatOuterRadius": "",
		"fCombatMusicPlayerCombatStrengthCap": "",
		"fCombatMusicPlayerNearStrengthMult": "",
		"fCombatMusicPlayerTargetedThreatRatio": "",
		"fCombatMusicStopTime": "",
		"fCombatMusicUpdateTime": "",
		"fCombatOffensiveBashChanceMax": "",
		"fCombatOffensiveBashChanceMin": "",
		"fCombatOptimalRangeMaxBufferDistance": "",
		"fCombatOptimalRangeMinBufferDistance": "",
		"fCombatOrbitDistance": "",
		"fCombatOrbitTimeMax": "",
		"fCombatOrbitTimeMin": "",
		"fCombatParalyzeTacticalDuration": "",
		"fCombatPathingAccelerationMult": "",
		"fCombatPathingCurvedPathSmoothingMult": "",
		"fCombatPathingDecelerationMult": "",
		"fCombatPathingGoalRayCastPathDistance": "",
		"fCombatPathingIncompletePathMinDistance": "",
		"fCombatPathingLocationCenterOffsetMult": "",
		"fCombatPathingLookAheadDelta": "",
		"fCombatPathingNormalizedRotationSpeed": "",
		"fCombatPathingRefLocationUpdateDistance": "",
		"fCombatPathingRefLocationUpdateTimeDistanceMax": "",
		"fCombatPathingRefLocationUpdateTimeDistanceMin": "",
		"fCombatPathingRefLocationUpdateTimeMax": "",
		"fCombatPathingRefLocationUpdateTimeMin": "",
		"fCombatPathingRetryWaitTime": "",
		"fCombatPathingRotationAccelerationMult": "",
		"fCombatPathingStartRayCastPathDistance": "",
		"fCombatPathingStraightPathCheckDistance": "",
		"fCombatPathingStraightRayCastPathDistance": "",
		"fCombatPathingUpdatePathCostMult": "",
		"fCombatPerchAttackChanceMax": "",
		"fCombatPerchAttackChanceMin": "",
		"fCombatPerchAttackTimeMax": "",
		"fCombatPerchAttackTimeMin": "",
		"fCombatPerchMaxTargetAngle": "",
		"fCombatPlayerBleedoutHealthDamageMult": "",
		"fCombatPlayerLimbDamageMult": "",
		"fCombatProjectileMaxRangeMult": "",
		"fCombatProjectileMaxRangeOptimalMult": "",
		"fCombatRadiusMinMult": "",
		"fCombatRangedAimVariance": "",
		"fCombatRangedAttackChanceLastAttackBonusTime": "",
		"fCombatRangedAttackChanceLastAttackBonus": "",
		"fCombatRangedAttackChanceMax": "",
		"fCombatRangedAttackChanceMin": "",
		"fCombatRangedAttackHoldTimeAbsoluteMin": "",
		"fCombatRangedAttackHoldTimeMax": "",
		"fCombatRangedAttackHoldTimeMinDistance": "",
		"fCombatRangedAttackHoldTimeMin": "",
		"fCombatRangedAttackMaximumHoldTime": "",
		"fCombatRangedDistance": "",
		"fCombatRangedMinimumRange": "",
		"fCombatRangedProjectileFiringArc": "",
		"fCombatRangedStandoffTimer": "",
		"fCombatRelativeDamageMod": "",
		"fCombatRestoreHealthPercentMax": "",
		"fCombatRestoreHealthPercentMin": "",
		"fCombatRestoreHealthRestrictTime": "",
		"fCombatRestoreMagickaPercentMax": "",
		"fCombatRestoreMagickaPercentMin": "",
		"fCombatRestoreMagickaRestrictTime": "",
		"fCombatRestoreStopCastThreshold": "",
		"fCombatRoundAmount": "",
		"fCombatSearchAreaUpdateTime": "",
		"fCombatSearchCenterRadius": "",
		"fCombatSearchCheckDestinationDistanceMax": "",
		"fCombatSearchCheckDestinationDistanceMid": "",
		"fCombatSearchCheckDestinationDistanceMin": "",
		"fCombatSearchCheckDestinationTime": "",
		"fCombatSearchDoorDistanceLow": "",
		"fCombatSearchDoorDistance": "",
		"fCombatSearchDoorSearchRadius": "",
		"fCombatSearchExteriorRadiusMax": "",
		"fCombatSearchExteriorRadiusMin": "",
		"fCombatSearchIgnoreLocationRadius": "",
		"fCombatSearchInteriorRadiusMax": "",
		"fCombatSearchInteriorRadiusMin": "",
		"fCombatSearchInvestigateTime": "",
		"fCombatSearchLocationCheckDistance": "",
		"fCombatSearchLocationCheckTime": "",
		"fCombatSearchLocationInitialCheckTime": "",
		"fCombatSearchLocationInvestigateDistance": "",
		"fCombatSearchLocationRadius": "",
		"fCombatSearchLookTime": "",
		"fCombatSearchRadiusBufferDistance": "",
		"fCombatSearchRadiusMemberDistance": "",
		"fCombatSearchSightRadius": "",
		"fCombatSearchStartWaitTime": "",
		"fCombatSearchUpdateTime": "",
		"fCombatSearchWanderDistance": "",
		"fCombatSelectTargetSwitchUpdateTime": "",
		"fCombatSelectTargetUpdateTime": "",
		"fCombatShoutHeadTrackingAngleMovingMult": "",
		"fCombatShoutHeadTrackingAngleMult": "",
		"fCombatShoutLongRecoveryTime": "",
		"fCombatShoutMaxHeadTrackingAngle": "",
		"fCombatShoutReleaseTime": "",
		"fCombatShoutShortRecoveryTime": "",
		"fCombatSneakAttackBonusMult": "",
		"fCombatSpeakAttackChance": "",
		"fCombatSpeakHitChance": "",
		"fCombatSpeakHitThreshold": "",
		"fCombatSpeakPowerAttackChance": "",
		"fCombatSpeakTauntChance": "",
		"fCombatSpecialAttackChanceMax": "",
		"fCombatSpecialAttackChanceMin": "",
		"fCombatSplashDamageMaxSpeed": "",
		"fCombatSplashDamageMinDamage": "",
		"fCombatSplashDamageMinRadius": "",
		"fCombatStaffTimer": "",
		"fCombatStaminaRegenRateMult": "",
		"fCombatStealthPointAttackedMaxValue": "",
		"fCombatStealthPointDetectedEventMaxValue": "",
		"fCombatStealthPointDrainMult": "",
		"fCombatStealthPointMax": "",
		"fCombatStealthPointRegenAlertWaitTime": "",
		"fCombatStealthPointRegenAttackedWaitTime": "",
		"fCombatStealthPointRegenDetectedEventWaitTime": "",
		"fCombatStealthPointRegenLostWaitTime": "",
		"fCombatStealthPointRegenMin": "",
		"fCombatStealthPointRegenMult": "",
		"fCombatStepAdvanceDistance": "",
		"fCombatStrafeChanceMax": "",
		"fCombatStrafeChanceMin": "",
		"fCombatStrafeDistanceMax": "",
		"fCombatStrafeDistanceMin": "",
		"fCombatStrafeMinDistanceRadiusMult": "",
		"fCombatStrengthUpdateTime": "",
		"fCombatSurroundDistanceMax": "",
		"fCombatSurroundDistanceMin": "",
		"fCombatTargetEngagedLastSeenTime": "",
		"fCombatTargetLocationAvoidNodeRadiusOffset": "",
		"fCombatTargetLocationCurrentReservationDistanceMult": "",
		"fCombatTargetLocationMaxDistance": "",
		"fCombatTargetLocationMinDistanceMult": "",
		"fCombatTargetLocationPathingRadius": "",
		"fCombatTargetLocationRadiusSizeMult": "",
		"fCombatTargetLocationRepositionAngleMult": "",
		"fCombatTargetLocationSwimmingOffset": "",
		"fCombatTargetLocationWidthMax": "",
		"fCombatTargetLocationWidthMin": "",
		"fCombatTargetLocationWidthSizeMult": "",
		"fCombatTeammateFollowRadiusBase": "",
		"fCombatTeammateFollowRadiusMin": "",
		"fCombatTeammateFollowRadiusMult": "",
		"fCombatThreatAnticipateTime": "",
		"fCombatThreatAvoidCost": "",
		"fCombatThreatBufferRadius": "",
		"fCombatThreatCacheVelocityTime": "",
		"fCombatThreatDangerousObjectHealth": "",
		"fCombatThreatExplosiveObjectThreatTime": "",
		"fCombatThreatExtrudeTime": "",
		"fCombatThreatExtrudeVelocityThreshold": "",
		"fCombatThreatNegativeExtrudeTime": "",
		"fCombatThreatProximityExplosionAvoidTime": "",
		"fCombatThreatRatioUpdateTime": "",
		"fCombatThreatSignificantScore": "",
		"fCombatThreatTimedExplosionLength": "",
		"fCombatThreatUpdateTimeMax": "",
		"fCombatThreatUpdateTimeMin": "",
		"fCombatThreatViewCone": "",
		"fCombatUnarmedCritDamageMult": "",
		"fCombatUnreachableTargetCheckTime": "",
		"fCombatVulnerabilityMod": "",
		"fCombatYieldRetryTime": "",
		"fCombatYieldTime": "",
		"fCommentOnPlayerActionsTimer": "",
		"fCommentOnPlayerKnockingThings": "",
		"fConcussionTimer": "",
		"fConeProjectileEnvironmentDistance": "",
		"fConeProjectileEnvironmentTimer": "",
		"fConeProjectileForceBase": "",
		"fConeProjectileForceMultAngular": "",
		"fConeProjectileForceMultLinear": "",
		"fConeProjectileForceMult": "",
		"fConeProjectileWaterScaleMult": "",
		"fCoveredAdvanceMinAdvanceDistanceMax": "",
		"fCoveredAdvanceMinAdvanceDistanceMin": "",
		"fCoverEvaluationLastSeenExpireTime": "",
		"fCoverFiredProjectileExpireTime": "",
		"fCoverFiringReloadClipPercent": "",
		"fCoverWaitReloadClipPercent": "",
		"fCreatureDefaultTurningSpeed": "",
		"fCreditsScrollSpeed": "",
		"fCrimeAlarmRespMult": "",
		"fCrimeDispAttack": "",
		"fCrimeDispMurder": "",
		"fCrimeDispPersonal": "",
		"fCrimeDispPickpocket": "",
		"fCrimeDispSteal": "",
		"fCrimeDispTresspass": "",
		"fCrimeFavorMult": "",
		"fCrimeGoldSkillPenaltyMult": "",
		"fCrimeGoldSteal": "",
		"fCrimePersonalRegardMult": "",
		"fCrimeRegardMult": "",
		"fCrimeSoundBase": "",
		"fCrimeSoundMult": "",
		"fCrimeWitnessRegardMult": "",
		"fDamageArmConditionBase": "",
		"fDamageArmConditionMult": "",
		"fDamagedAVRegenDelay": "",
		"fDamagedHealthRegenDelay": "",
		"fDamagedMagickaRegenDelay": "",
		"fDamagedStaminaRegenDelay": "",
		"fDamageGunWeapCondBase": "",
		"fDamageGunWeapCondMult": "",
		"fDamageMeleeWeapCondBase": "",
		"fDamageMeleeWeapCondMult": "",
		"fDamagePCSkillMax": "",
		"fDamagePCSkillMin": "",
		"fDamageSkillMax": "",
		"fDamageSkillMin": "",
		"fDamageSneakAttackMult": "",
		"fDamageStrengthBase": "",
		"fDamageStrengthMult": "",
		"fDamageToArmorPercentage": "",
		"fDamageToWeaponEnergyMult": "",
		"fDamageToWeaponGunMult": "",
		"fDamageToWeaponLauncherMult": "",
		"fDamageToWeaponMeleeMult": "",
		"fDamageUnarmedPenalty": "",
		"fDamageWeaponMult": "",
		"fDangerousObjectExplosionDamage": "",
		"fDangerousObjectExplosionRadius": "",
		"fDangerousProjectileExplosionDamage": "",
		"fDangerousProjectileExplosionRadius": "",
		"fDaytimeColorExtension": "",
		"fDeadReactionDistance": "",
		"fDeathForceDamageMax": "",
		"fDeathForceDamageMin": "",
		"fDeathForceForceMax": "",
		"fDeathForceForceMin": "",
		"fDeathForceMassBase": "",
		"fDeathForceMassMult": "",
		"fDeathForceRangedDamageMax": "",
		"fDeathForceRangedDamageMin": "",
		"fDeathForceRangedForceMax": "",
		"fDeathForceRangedForceMin": "",
		"fDeathForceSpellImpactMult": "",
		"fDeathSoundMaxDistance": "",
		"fDebrisFadeTime": "",
		"fDecapitateBloodTime": "",
		"fDefaultAngleTolerance": "",
		"fDefaultBowSpeedBonus": "",
		"fDemandBase": "",
		"fDemandMult": "",
		"fDetectEventDistanceNPC": "",
		"fDetectEventDistancePlayer": "",
		"fDetectEventDistanceVeryLoudMult": "",
		"fDetectEventSneakDistanceVeryLoud": "",
		"fDetectionActionTimer": "",
		"fDetectionCombatNonTargetDistanceMult": "",
		"fDetectionCommentTimer": "",
		"fDetectionEventExpireTime": "",
		"fDetectionLargeActorSizeMult": "",
		"fDetectionLOSDistanceAngle": "",
		"fDetectionLOSDistanceMultExterior": "",
		"fDetectionLOSDistanceMultInterior": "",
		"fDetectionNightEyeBonus": "",
		"fDetectionSneakLightMod": "",
		"fDetectionStateExpireTime": "",
		"fDetectionUpdateTimeMaxComplex": "",
		"fDetectionUpdateTimeMax": "",
		"fDetectionUpdateTimeMinComplex": "",
		"fDetectionUpdateTimeMin": "",
		"fDetectionViewCone": "",
		"fDetectProjectileDistanceNPC": "",
		"fDetectProjectileDistancePlayer": "",
		"fDialogFocalDepthRange": "",
		"fDialogFocalDepthStrength": "",
		"fDialogSpeechDelaySeconds": "",
		"fDialogZoomInSeconds": "",
		"fDialogZoomOutSeconds": "",
		"fDifficultyDamageMultiplier": "",
		"fDifficultyDefaultValue": "",
		"fDifficultyMaxValue": "",
		"fDifficultyMinValue": "",
		"fDiffMultHPByPCE": "",
		"fDiffMultHPByPCH": "",
		"fDiffMultHPByPCL": "",
		"fDiffMultHPByPCN": "",
		"fDiffMultHPByPCVE": "",
		"fDiffMultHPByPCVH": "",
		"fDiffMultHPToPCE": "",
		"fDiffMultHPToPCH": "",
		"fDiffMultHPToPCL": "",
		"fDiffMultHPToPCN": "",
		"fDiffMultHPToPCVE": "",
		"fDiffMultHPToPCVH": "",
		"fDiffMultXPH": "",
		"fDiffMultXPVH": "",
		"fDisarmedPickupWeaponDistanceMult": "",
		"fDisenchantSkillUse": "",
		"fDistanceAutomaticallyActivateDoor": "",
		"fDistanceExteriorReactCombat": "",
		"fDistanceFadeActorAutoLoadDoor": "",
		"fDistanceInteriorReactCombat": "",
		"fDistanceProjectileExplosionDetection": "",
		"fDistancetoPlayerforConversations": "",
		"fDOFDistanceMult": "",
		"fDrinkRepeatRate": "",
		"fDyingTimer": "",
		"fEmbeddedWeaponSwitchChance": "",
		"fEmbeddedWeaponSwitchTime": "",
		"fEnchantingCostExponent": "",
		"fEnchantingSkillCostBase": "",
		"fEnchantingSkillCostMult": "",
		"fEnchantingSkillCostScale": "",
		"fEnchantingSkillFactor": "",
		"fEnchantmentEffectPointsMult": "",
		"fEnchantmentGoldMult": "",
		"fEnchantmentPointsMult": "",
		"fEnemyHealthBarTimer": "",
		"fEssentialDeathTime": "",
		"fEssentialDownCombatHealthRegenMult": "",
		"fEssentialHealthPercentReGain": "",
		"fEssentialNonCombatHealRateBonus": "",
		"fEssentialNPCMinimumHealth": "",
		"fEvaluatePackageTimer": "",
		"fEvaluateProcedureTimer": "",
		"fExplodeLimbRemovalDelayVATS": "",
		"fExplodeLimbRemovalDelay": "",
		"fExplosionForceClutterUpBias": "",
		"fExplosionForceKnockdownMinimum": "",
		"fExplosionForceMultAngular": "",
		"fExplosionForceMultLinear": "",
		"fExplosionImageSpaceSwapPower": "",
		"fExplosionKnockStateExplodeDownTime": "",
		"fExplosionLOSBufferDistance": "",
		"fExplosionLOSBuffer": "",
		"fExplosionMaxImpulse": "",
		"fExplosionSourceRefMult": "",
		"fExplosionSplashRadius": "",
		"fExplosionWaterRadiusRatio": "",
		"fExplosiveProjectileBlockedResetTime": "",
		"fExplosiveProjectileBlockedWaitTime": "",
		"fExpressionChangePerSec": "",
		"fExpressionStrengthAdd": "",
		"fEyeHeadingMaxOffsetEmotionAngry": "",
		"fEyeHeadingMaxOffsetEmotionFear": "",
		"fEyeHeadingMaxOffsetEmotionHappy": "",
		"fEyeHeadingMaxOffsetEmotionNeutral": "",
		"fEyeHeadingMaxOffsetEmotionSad": "",
		"fEyeHeadingMinOffsetEmotionAngry": "",
		"fEyeHeadingMinOffsetEmotionFear": "",
		"fEyeHeadingMinOffsetEmotionHappy": "",
		"fEyeHeadingMinOffsetEmotionNeutral": "",
		"fEyeHeadingMinOffsetEmotionSad": "",
		"fEyePitchMaxOffsetEmotionAngry": "",
		"fEyePitchMaxOffsetEmotionFear": "",
		"fEyePitchMaxOffsetEmotionHappy": "",
		"fEyePitchMaxOffsetEmotionNeutral": "",
		"fEyePitchMaxOffsetEmotionSad": "",
		"fEyePitchMinOffsetEmotionAngry": "",
		"fEyePitchMinOffsetEmotionFear": "",
		"fEyePitchMinOffsetEmotionHappy": "",
		"fEyePitchMinOffsetEmotionNeutral": "",
		"fEyePitchMinOffsetEmotionSad": "",
		"fFallLegDamageMult": "",
		"fFastTravelSpeedMult": "",
		"fFastWalkInterpolationBetweenWalkAndRun": "",
		"fFavorCostActivator": "",
		"fFavorCostAttackCrimeMult": "",
		"fFavorCostAttack": "",
		"fFavorCostLoadDoor": "",
		"fFavorCostNonLoadDoor": "",
		"fFavorCostOwnedDoorMult": "",
		"fFavorCostStealContainerCrime": "",
		"fFavorCostStealContainerMult": "",
		"fFavorCostStealObjectMult": "",
		"fFavorCostTakeObject": "",
		"fFavorCostUnlockContainer": "",
		"fFavorCostUnlockDoor": "",
		"fFavorEventStopDistance": "",
		"fFavorEventTriggerDistance": "",
		"fFavorRequestPickDistance": "",
		"fFavorRequestRadius": "",
		"fFavorRequestWaitTimer": "",
		"fFleeDistanceExterior": "",
		"fFleeDistanceInterior": "",
		"fFleeDoneDistanceExterior": "",
		"fFleeDoneDistanceInterior": "",
		"fFleeIsSafeTimer": "",
		"fFloatQuestMarkerFloatHeight": "",
		"fFloatQuestMarkerMaxDistance": "",
		"fFloatQuestMarkerMinDistance": "",
		"fFlyingActorDefaultTurningSpeed": "",
		"fFollowerSpacingAtDoors": "",
		"fFollowExtraCatchUpSpeedMult": "",
		"fFollowMatchSpeedZoneWidth": "",
		"fFollowRunMaxSpeedupMultiplier": "",
		"fFollowRunMinSlowdownMultiplier": "",
		"fFollowSlowdownZoneWidth": "",
		"fFollowSpaceBetweenFollowers": "",
		"fFollowStartSprintDistance": "",
		"fFollowStopZoneMinMult": "",
		"fFollowWalkMaxSpeedupMultiplier": "",
		"fFollowWalkMinSlowdownMultiplier": "",
		"fFollowWalkZoneMult": "",
		"fFriendHitTimer": "",
		"fFriendMinimumLastHitTime": "",
		"fFurnitureMarkerAngleTolerance": "",
		"fFurnitureScaleAnimDurationNPC": "",
		"fFurnitureScaleAnimDurationPlayer": "",
		"fGameplayImpulseMinMass": "",
		"fGameplayImpulseMultBiped": "",
		"fGameplayImpulseMultClutter": "",
		"fGameplayImpulseMultDebrisLarge": "",
		"fGameplayImpulseMultProp": "",
		"fGameplayImpulseMultTrap": "",
		"fGameplayImpulseScale": "",
		"fGameplayiSpeakingEmotionMaxDeltaChange": "",
		"fGameplayiSpeakingEmotionMinDeltaChange": "",
		"fGameplaySpeakingEmotionMaxChangeValue": "",
		"fGameplaySpeakingEmotionMinChangeValue": "",
		"fGameplayVoiceFilePadding": "",
		"fGetHitPainMult": "",
		"fGrabMaxWeightRunning": "",
		"fGrabMaxWeightWalking": "",
		"fGrenadeAgeMax": "",
		"fGrenadeFriction": "",
		"fGrenadeHighArcSpeedPercentage": "",
		"fGrenadeRestitution": "",
		"fGrenadeThrowHitFractionThreshold": "",
		"fGuardPackageAttackRadiusMult": "",
		"fGunDecalCameraDistance": "",
		"fGunParticleCameraDistance": "",
		"fGunReferenceSkill": "",
		"fGunShellCameraDistance": "",
		"fGunShellDirectionRandomize": "",
		"fGunShellEjectSpeed": "",
		"fGunShellLifetime": "",
		"fGunShellRotateRandomize": "",
		"fGunShellRotateSpeed": "",
		"fGunSpreadArmBase": "",
		"fGunSpreadArmMult": "",
		"fGunSpreadCondBase": "",
		"fGunSpreadCondMult": "",
		"fGunSpreadCrouchBase": "",
		"fGunSpreadCrouchMult": "",
		"fGunSpreadDriftBase": "",
		"fGunSpreadDriftMult": "",
		"fGunSpreadHeadBase": "",
		"fGunSpreadHeadMult": "",
		"fGunSpreadIronSightsBase": "",
		"fGunSpreadIronSightsMult": "",
		"fGunSpreadNPCArmBase": "",
		"fGunSpreadNPCArmMult": "",
		"fGunSpreadRunBase": "",
		"fGunSpreadRunMult": "",
		"fGunSpreadSkillBase": "",
		"fGunSpreadSkillMult": "",
		"fGunSpreadWalkBase": "",
		"fGunSpreadWalkMult": "",
		"fHandDamageSkillBase": "",
		"fHandDamageSkillMult": "",
		"fHandDamageStrengthBase": "",
		"fHandDamageStrengthMult": "",
		"fHandHealthMax": "",
		"fHandHealthMin": "",
		"fHandReachDefault": "",
		"fHazardDropMaxDistance": "",
		"fHazardMaxWaitTime": "",
		"fHazardSpacingMult": "",
		"fHeadingMarkerAngleTolerance": "",
		"fHeadTrackSpeedMaxAngle": "",
		"fHeadTrackSpeedMax": "",
		"fHeadTrackSpeedMinAngle": "",
		"fHeadTrackSpeedMin": "",
		"fHealthRegenDelayMax": "",
		"fHitCasterSizeLarge": "",
		"fHitCasterSizeSmall": "",
		"fHorseMountOffsetX": "",
		"fHorseMountOffsetY": "",
		"fHostileActorExteriorDistance": "",
		"fHostileActorInteriorDistance": "",
		"fHostileFlyingActorExteriorDistance": "",
		"fHUDCompassLocationMaxDist": "",
		"fIdleChatterCommentTimerMax": "",
		"fIdleChatterCommentTimer": "",
		"fIdleMarkerAngleTolerance": "",
		"fImpactShaderMaxDistance": "",
		"fImpactShaderMaxMagnitude": "",
		"fImpactShaderMinMagnitude": "",
		"fIntimidateConfidenceMultAverage": "",
		"fIntimidateConfidenceMultBrave": "",
		"fIntimidateConfidenceMultCautious": "",
		"fIntimidateConfidenceMultCowardly": "",
		"fIntimidateConfidenceMultFoolhardy": "",
		"fIntimidateSpeechcraftCurve": "",
		"fIronSightsDOFDistance": "",
		"fIronSightsDOFRange": "",
		"fIronSightsDOFStrengthCap": "",
		"fIronSightsDOFSwitchSeconds": "",
		"fIronSightsFOVTimeChange": "",
		"fIronSightsGunMotionBlur": "",
		"fIronSightsMotionBlur": "",
		"fItemPointsMult": "",
		"fItemRepairCostMult": "",
		"fJogInterpolationBetweenWalkAndRun": "",
		"fJumpDoubleMult": "",
		"fJumpFallHeightExponentNPC": "",
		"fJumpFallHeightExponent": "",
		"fJumpFallHeightMinNPC": "",
		"fJumpFallHeightMin": "",
		"fJumpFallHeightMultNPC": "",
		"fJumpFallHeightMult": "",
		"fJumpFallRiderMult": "",
		"fJumpFallSkillBase": "",
		"fJumpFallSkillMult": "",
		"fJumpFallVelocityMin": "",
		"fJumpHeightMin": "",
		"fJumpMoveBase": "",
		"fJumpMoveMult": "",
		"fJumpSwimmingMult": "",
		"fKarmaModKillingEvilActor": "",
		"fKarmaModMurderingNonEvilCreature": "",
		"fKarmaModMurderingNonEvilNPC": "",
		"fKarmaModStealing": "",
		"fKillCamBaseOdds": "",
		"fKillCamLevelBias": "",
		"fKillCamLevelFactor": "",
		"fKillCamLevelMaxBias": "",
		"fKillMoveMaxDuration": "",
		"fKillWitnessesTimerSetting": "",
		"fKnockbackAgilBase": "",
		"fKnockbackAgilMult": "",
		"fKnockbackDamageBase": "",
		"fKnockbackDamageMult": "",
		"fKnockbackForceMax": "",
		"fKnockbackTime": "",
		"fKnockdownAgilBase": "",
		"fKnockdownAgilMult": "",
		"fKnockdownBaseHealthThreshold": "",
		"fKnockdownChance": "",
		"fKnockdownCurrentHealthThreshold": "",
		"fKnockdownDamageBase": "",
		"fKnockdownDamageMult": "",
		"fLargeProjectilePickBufferSize": "",
		"fLargeProjectileSize": "",
		"fLevelUpCarryWeightMod": "",
		"fLightRecalcTimerPlayer": "",
		"fLightRecalcTimer": "",
		"fLoadingWheelScale": "",
		"fLockLevelBase": "",
		"fLockLevelMult": "",
		"fLockpickBreakAdept": "",
		"fLockpickBreakApprentice": "",
		"fLockPickBreakBase": "",
		"fLockpickBreakExpert": "",
		"fLockpickBreakMaster": "",
		"fLockPickBreakMult": "",
		"fLockpickBreakNovice": "",
		"fLockpickBreakSkillBase": "",
		"fLockpickBreakSkillMult": "",
		"fLockpickBrokenPicksMult": "",
		"fLockPickQualityBase": "",
		"fLockPickQualityMult": "",
		"fLockpickSkillPartialPickBase": "",
		"fLockpickSkillPartialPickMult": "",
		"fLockpickSkillSweetSpotBase": "",
		"fLockpickSkillSweetSpotMult": "",
		"fLockSkillBase": "",
		"fLockSkillMult": "",
		"fLockTrapGoOffBase": "",
		"fLockTrapGoOffMult": "",
		"fLookDownDisableBlinkingAmt": "",
		"fLowHealthTutorialPercentage": "",
		"fLowLevelNPCBaseHealthMult": "",
		"fLowMagickaTutorialPercentage": "",
		"fLowStaminaTutorialPercentage": "",
		"fMagicAbsorbDistanceReachMult": "",
		"fMagicAbsorbVisualTimer": "",
		"fMagicAccumulatingModifierEffectHoldDuration": "",
		"fMagicAreaBaseCostMult": "",
		"fMagicAreaScaleMax": "",
		"fMagicAreaScaleMin": "",
		"fMagicAreaScale": "",
		"fMagicBarrierDepth": "",
		"fMagicBarrierHeight": "",
		"fMagicBarrierSpacing": "",
		"fMagicBoltDuration": "",
		"fMagicBoltSegmentLength": "",
		"fMagicCasterPCSkillCostBase": "",
		"fMagicCasterPCSkillCostMult": "",
		"fMagicCasterSkillCostBase": "",
		"fMagicCasterSkillCostMult": "",
		"fMagicCEEnchantMagOffset": "",
		"fMagicChainExplosionEffectivenessDelta": "",
		"fMagicCloudAreaMin": "",
		"fMagicCloudDurationMin": "",
		"fMagicCloudFindTargetTime": "",
		"fMagicCloudLifeScale": "",
		"fMagicCloudSizeScale": "",
		"fMagicCloudSlowdownRate": "",
		"fMagicCloudSpeedBase": "",
		"fMagicCloudSpeedScale": "",
		"fMagicCostScale": "",
		"fMagicDefaultAccumulatingModifierEffectRate": "",
		"fMagicDefaultTouchDistance": "",
		"fMagicDiseaseTransferBase": "",
		"fMagicDiseaseTransferMult": "",
		"fMagicDispelMagnitudeMult": "",
		"fMagicDualCastingCostBase": "",
		"fMagicDualCastingCostMult": "",
		"fMagicDualCastingEffectivenessBase": "",
		"fMagicDualCastingEffectivenessMult": "",
		"fMagicDualCastingTimeBase": "",
		"fMagicDualCastingTimeMult": "",
		"fMagicDurMagBaseCostMult": "",
		"fMagicEnchantmentChargeBase": "",
		"fMagicEnchantmentChargeMult": "",
		"fMagicEnchantmentDrainBase": "",
		"fMagicEnchantmentDrainMult": "",
		"fMagicExplosionAgilityMult": "",
		"fMagicExplosionClutterMult": "",
		"fMagicExplosionIncorporealMult": "",
		"fMagicExplosionIncorporealTime": "",
		"fMagicExplosionPowerBase": "",
		"fMagicExplosionPowerMax": "",
		"fMagicExplosionPowerMin": "",
		"fMagicExplosionPowerMult": "",
		"fMagicGuideSpacing": "",
		"fMagickaRegenDelayMax": "",
		"fMagickaReturnBase": "",
		"fMagickaReturnMult": "",
		"fMagicLightForwardOffset": "",
		"fMagicLightHeightOffset": "",
		"fMagicLightRadiusBase": "",
		"fMagicLightSideOffset": "",
		"fMagicNightEyeAmbient": "",
		"fMagicPCSkillCostScale": "",
		"fMagicPlayerMinimumInvisibility": "",
		"fMagicPostDrawCastDelay": "",
		"fMagicProjectileMaxDistance": "",
		"fMagicRangeTargetCostMult": "",
		"fMagicResistActorSkillBase": "",
		"fMagicResistActorSkillMult": "",
		"fMagicResistTargetWillpowerBase": "",
		"fMagicResistTargetWillpowerMult": "",
		"fMagicSkillCostScale": "",
		"fMagicSummonMaxAppearTime": "",
		"fMagicTelekinesiDistanceMult": "",
		"fMagicTelekinesisBaseDistance": "",
		"fMagicTelekinesisComplexMaxForce": "",
		"fMagicTelekinesisComplexObjectDamping": "",
		"fMagicTelekinesisComplexSpringDamping": "",
		"fMagicTelekinesisComplexSpringElasticity": "",
		"fMagicTelekinesisDamageBase": "",
		"fMagicTelekinesisDamageMult": "",
		"fMagicTelekinesisDistanceMin": "",
		"fMagicTelekinesisDualCastDamageMult": "",
		"fMagicTelekinesisDualCastThrowMult": "",
		"fMagicTelekinesisLiftPowerMult": "",
		"fMagicTelekinesisMaxForce": "",
		"fMagicTelekinesisMoveAccelerate": "",
		"fMagicTelekinesisMoveBase": "",
		"fMagicTelekinesisMoveMax": "",
		"fMagicTelekinesisObjectDamping": "",
		"fMagicTelekinesisSpringDamping": "",
		"fMagicTelekinesisSpringElasticity": "",
		"fMagicTelekinesisThrowAccelerate": "",
		"fMagicTelekinesisThrowMax": "",
		"fMagicTelekinesisThrow": "",
		"fMagicTrackingLimitComplex": "",
		"fMagicTrackingLimit": "",
		"fMagicTrackingMultBall": "",
		"fMagicTrackingMultBolt": "",
		"fMagicTrackingMultFog": "",
		"fMagicUnitsPerFoot": "",
		"fMagicVACNoPartTargetedMult": "",
		"fMagicVACPartTargetedMult": "",
		"fMagicWardPowerMaxBase": "",
		"fMagicWardPowerMaxMult": "",
		"fMapMarkerMaxPercentSize": "",
		"fMapMarkerMinFadeAlpha": "",
		"fMapMarkerMinPercentSize": "",
		"fMapQuestMarkerMaxPercentSize": "",
		"fMapQuestMarkerMinFadeAlpha": "",
		"fMapQuestMarkerMinPercentSize": "",
		"fMasserAngleFadeEnd": "",
		"fMasserAngleFadeStart": "",
		"fMasserAngleShadowEarlyFade": "",
		"fMasserSpeed": "",
		"fMasserZOffset": "",
		"fMaxArmorRating": "",
		"fMaximumWind": "",
		"fMaxSandboxRescanSeconds": "",
		"fMaxSellMult": "",
		"fMeleeMovementRestrictionsUpdateTime": "",
		"fMeleeSweepViewAngleMult": "",
		"fMinBuyMult": "",
		"fMinDistanceUseHorse": "",
		"fMineAgeMax": "",
		"fMineExteriorRadiusMult": "",
		"fMinesBlinkFast": "",
		"fMinesBlinkMax": "",
		"fMinesBlinkSlow": "",
		"fMinesDelayMin": "",
		"fMinSandboxRescanSeconds": "",
		"fModelReferenceEffectMaxWaitTime": "",
		"fModifiedTargetAttackRange": "",
		"fMotionBlur": "",
		"fMountedMaxLookingDown": "",
		"fMoveCharRunBase": "",
		"fMoveCharWalkBase": "",
		"fMoveEncumEffectNoWeapon": "",
		"fMoveEncumEffect": "",
		"fMoveFlyRunMult": "",
		"fMoveFlyWalkMult": "",
		"fMovementNearTargetAvoidCost": "",
		"fMovementNearTargetAvoidRadius": "",
		"fMovementTargetAvoidCost": "",
		"fMovementTargetAvoidRadiusMult": "",
		"fMovementTargetAvoidRadius": "",
		"fMoveSprintMult": "",
		"fMoveSwimMult": "",
		"fMoveWeightMax": "",
		"fMoveWeightMin": "",
		"fNPCAttributeHealthMult": "",
		"fNPCBaseMagickaMult": "",
		"fNPCHealthLevelBonus": "",
		"fObjectHitH2HReach": "",
		"fObjectHitTwoHandReach": "",
		"fObjectHitWeaponReach": "",
		"fObjectMotionBlur": "",
		"fObjectWeightPickupDetectionMult": "",
		"fOutOfBreathStaminaRegenDelay": "",
		"fPainDelay": "",
		"fPartialPickAverage": "",
		"fPartialPickEasy": "",
		"fPartialPickHard": "",
		"fPartialPickVeryEasy": "",
		"fPartialPickVeryHard": "",
		"fPCBaseHealthMult": "",
		"fPCBaseMagickaMult": "",
		"fPCHealthLevelBonus": "",
		"fPerceptionMult": "",
		"fPerkHeavyArmorExpertSpeedMult": "",
		"fPerkHeavyArmorJourneymanDamageMult": "",
		"fPerkHeavyArmorMasterSpeedMult": "",
		"fPerkHeavyArmorNoviceDamageMult": "",
		"fPerkHeavyArmorSinkGravityMult": "",
		"fPerkLightArmorExpertSpeedMult": "",
		"fPerkLightArmorJourneymanDamageMult": "",
		"fPerkLightArmorMasterRatingMult": "",
		"fPerkLightArmorNoviceDamageMult": "",
		"fPersAdmireAggr": "",
		"fPersAdmireConf": "",
		"fPersAdmireEner": "",
		"fPersAdmireIntel": "",
		"fPersAdmirePers": "",
		"fPersAdmireResp": "",
		"fPersAdmireStre": "",
		"fPersAdmireWillp": "",
		"fPersBoastAggr": "",
		"fPersBoastConf": "",
		"fPersBoastEner": "",
		"fPersBoastIntel": "",
		"fPersBoastPers": "",
		"fPersBoastResp": "",
		"fPersBoastWillp": "",
		"fPersBullyAggr": "",
		"fPersBullyConf": "",
		"fPersBullyEner": "",
		"fPersBullyIntel": "",
		"fPersBullyPers": "",
		"fPersBullyResp": "",
		"fPersBullyStre": "",
		"fPersBullyWillp": "",
		"fPersJokeAggr": "",
		"fPersJokeConf": "",
		"fPersJokeEner": "",
		"fPersJokeIntel": "",
		"fPersJokePers": "",
		"fPersJokeResp": "",
		"fPersJokeStre": "",
		"fPersJokeWillp": "",
		"fPersuasionAccuracyMaxDisposition": "",
		"fPersuasionAccuracyMaxSelect": "",
		"fPersuasionAccuracyMinDispostion": "",
		"fPersuasionAccuracyMinSelect": "",
		"fPersuasionBaseValueMaxDisposition": "",
		"fPersuasionBaseValueMaxSelect": "",
		"fPersuasionBaseValueMinDispostion": "",
		"fPersuasionBaseValueMinSelect": "",
		"fPersuasionBaseValueShape": "",
		"fPersuasionMaxDisposition": "",
		"fPersuasionMaxInput": "",
		"fPersuasionMaxSelect": "",
		"fPersuasionMinDispostion": "",
		"fPersuasionMinInput": "",
		"fPersuasionMinPercentCircle": "",
		"fPersuasionMinSelect": "",
		"fPersuasionShape": "",
		"fPhysicsDamage1Damage": "",
		"fPhysicsDamage1Mass": "",
		"fPhysicsDamage2Damage": "",
		"fPhysicsDamage2Mass": "",
		"fPhysicsDamage3Damage": "",
		"fPhysicsDamage3Mass": "",
		"fPhysicsDamageSpeedBase": "",
		"fPhysicsDamageSpeedMin": "",
		"fPhysicsDamageSpeedMult": "",
		"fPickLevelBase": "",
		"fPickLevelMult": "",
		"fPickNumBase": "",
		"fPickNumMult": "",
		"fPickPocketActorSkillBase": "",
		"fPickPocketActorSkillMult": "",
		"fPickPocketAmountBase": "",
		"fPickPocketAmountMult": "",
		"fPickPocketDetected": "",
		"fPickPocketMaxChance": "",
		"fPickPocketMinChance": "",
		"fPickpocketSkillUsesCurve": "",
		"fPickPocketTargetSkillBase": "",
		"fPickPocketTargetSkillMult": "",
		"fPickPocketWeightBase": "",
		"fPickPocketWeightMult": "",
		"fPickSpring1": "",
		"fPickSpring2": "",
		"fPickSpring3": "",
		"fPickSpring4": "",
		"fPickSpring5": "",
		"fPickupItemDistanceFudge": "",
		"fPickUpWeaponDelay": "",
		"fPickupWeaponDistanceMinMaxDPSMult": "",
		"fPickupWeaponMeleeDistanceMax": "",
		"fPickupWeaponMeleeDistanceMin": "",
		"fPickupWeaponMeleeWeaponDPSMult": "",
		"fPickupWeaponMinDPSImprovementPercent": "",
		"fPickupWeaponRangedDistanceMax": "",
		"fPickupWeaponRangedDistanceMin": "",
		"fPickupWeaponRangedMeleeDPSRatioThreshold": "",
		"fPickupWeaponTargetUnreachableDistanceMult": "",
		"fPickupWeaponUnarmedDistanceMax": "",
		"fPickupWeaponUnarmedDistanceMin": "",
		"fPlayerDeathReloadTime": "",
		"fPlayerDetectActorValue": "",
		"fPlayerDetectionSneakBase": "",
		"fPlayerDetectionSneakMult": "",
		"fPlayerDropDistance": "",
		"fPlayerHealthHeartbeatFast": "",
		"fPlayerHealthHeartbeatSlow": "",
		"fPlayerMaxResistance": "",
		"fPlayerTargetCombatDistance": "",
		"fPlayerTeleportFadeSeconds": "",
		"fPotionGoldValueMult": "",
		"fPotionMortPestleMult": "",
		"fPotionT1AleDurMult": "",
		"fPotionT1AleMagMult": "",
		"fPotionT1CalDurMult": "",
		"fPotionT1CalMagMult": "",
		"fPotionT1MagMult": "",
		"fPotionT1RetDurMult": "",
		"fPotionT1RetMagMult": "",
		"fPotionT2AleDurMult": "",
		"fPotionT2CalDurMult": "",
		"fPotionT2RetDurMult": "",
		"fPotionT3AleMagMult": "",
		"fPotionT3CalMagMult": "",
		"fPotionT3RetMagMult": "",
		"fPowerAttackCoolDownTime": "",
		"fPowerAttackDefaultBonus": "",
		"fPowerAttackStaminaPenalty": "",
		"fPrecipWindMult": "",
		"fProjectileCollisionImpulseScale": "",
		"fProjectileDefaultTracerRange": "",
		"fProjectileDeflectionTime": "",
		"fProjectileInventoryGrenadeFreakoutTime": "",
		"fProjectileInventoryGrenadeTimer": "",
		"fProjectileKnockMinMass": "",
		"fProjectileKnockMultBiped": "",
		"fProjectileKnockMultClutter": "",
		"fProjectileKnockMultProp": "",
		"fProjectileKnockMultTrap": "",
		"fProjectileMaxDistance": "",
		"fProjectileReorientTracerMin": "",
		"fQuestCinematicCharacterFadeInDelay": "",
		"fQuestCinematicCharacterFadeIn": "",
		"fQuestCinematicCharacterFadeOut": "",
		"fQuestCinematicCharacterRemain": "",
		"fQuestCinematicObjectiveFadeInDelay": "",
		"fQuestCinematicObjectiveFadeIn": "",
		"fQuestCinematicObjectiveFadeOut": "",
		"fQuestCinematicObjectivePauseTime": "",
		"fQuestCinematicObjectiveScrollTime": "",
		"fRandomSceneAgainMaxTime": "",
		"fRandomSceneAgainMinTime": "",
		"fRechargeGoldMult": "",
		"fReEquipArmorTime": "",
		"fReflectedAbsorbChanceReduction": "",
		"fRelationshipBase": "",
		"fRelationshipMult": "",
		"fRemoteCombatMissedAttack": "",
		"fRemoveExcessComplexDeadTime": "",
		"fRemoveExcessDeadTime": "",
		"fRepairMax": "",
		"fRepairMin": "",
		"fRepairScavengeMult": "",
		"fRepairSkillBase": "",
		"fRepairSkillMax": "",
		"fReservationExpirationSeconds": "",
		"fResistArrestTimer": "",
		"fRockitDamageBonusWeightMin": "",
		"fRockitDamageBonusWeightMult": "",
		"fRoomLightingTransitionDuration": "",
		"fRumbleBlockStrength": "",
		"fRumbleBlockTime": "",
		"fRumbleHitBlockedStrength": "",
		"fRumbleHitBlockedTime": "",
		"fRumbleHitStrength": "",
		"fRumbleHitTime": "",
		"fRumblePainStrength": "",
		"fRumblePainTime": "",
		"fRumbleShakeRadiusMult": "",
		"fRumbleShakeTimeMult": "",
		"fRumbleStruckStrength": "",
		"fRumbleStruckTime": "",
		"fSandboxBreakfastMax": "",
		"fSandboxBreakfastMin": "",
		"fSandboxCylinderBottom": "",
		"fSandboxCylinderTop": "",
		"fSandBoxDelayEvalSeconds": "",
		"fSandboxDinnerMax": "",
		"fSandboxDinnerMin": "",
		"fSandboxDurationBase": "",
		"fSandboxDurationMultEatSitting": "",
		"fSandboxDurationMultEatStanding": "",
		"fSandboxDurationMultFurniture": "",
		"fSandboxDurationMultIdleMarker": "",
		"fSandboxDurationMultSitting": "",
		"fSandboxDurationMultSleeping": "",
		"fSandboxDurationMultWandering": "",
		"fSandboxDurationRangeMult": "",
		"fSandboxEnergyMultEatSitting": "",
		"fSandboxEnergyMultEatStanding": "",
		"fSandboxEnergyMultFurniture": "",
		"fSandboxEnergyMultIdleMarker": "",
		"fSandboxEnergyMultSitting": "",
		"fSandboxEnergyMultSleeping": "",
		"fSandboxEnergyMultWandering": "",
		"fSandboxEnergyMult": "",
		"fSandBoxExtraDialogueRange": "",
		"fSandBoxInterMarkerMinDist": "",
		"fSandboxLunchMax": "",
		"fSandboxLunchMin": "",
		"fSandboxMealDurationMax": "",
		"fSandboxMealDurationMin": "",
		"fSandBoxRadiusHysteresis": "",
		"fSandBoxSearchRadius": "",
		"fSandboxSleepDurationMax": "",
		"fSandboxSleepDurationMin": "",
		"fSandboxSleepStartMax": "",
		"fSandboxSleepStartMin": "",
		"fSayOncePerDayInfoTimer": "",
		"fScrollCostMult": "",
		"fSecondsBetweenWindowUpdate": "",
		"fSecundaAngleFadeEnd": "",
		"fSecundaAngleFadeStart": "",
		"fSecundaAngleShadowEarlyFade": "",
		"fSecundaSpeed": "",
		"fSecundaZOffset": "",
		"fShieldBaseFactor": "",
		"fShieldBashMax": "",
		"fShieldBashMin": "",
		"fShieldBashPCMax": "",
		"fShieldBashPCMin": "",
		"fShieldBashSkillUseBase": "",
		"fShieldBashSkillUseMult": "",
		"fShieldScalingFactor": "",
		"fShockBoltGrowWidth": "",
		"fShockBoltsLength": "",
		"fShockBoltSmallWidth": "",
		"fShockBoltsRadiusStrength": "",
		"fShockBoltsRadius": "",
		"fShockBranchBoltsRadiusStrength": "",
		"fShockBranchBoltsRadius": "",
		"fShockBranchLifetime": "",
		"fShockBranchSegmentLength": "",
		"fShockBranchSegmentVariance": "",
		"fShockCastVOffset": "",
		"fShockCoreColorB": "",
		"fShockCoreColorG": "",
		"fShockCoreColorR": "",
		"fShockGlowColorB": "",
		"fShockGlowColorG": "",
		"fShockGlowColorR": "",
		"fShockSegmentLength": "",
		"fShockSegmentVariance": "",
		"fShockSubSegmentVariance": "",
		"fShoutTime1": "",
		"fShoutTime2": "",
		"fShoutTimeout": "",
		"fSittingMaxLookingDown": "",
		"fSkillUsageLockPickAverage": "",
		"fSkillUsageLockPickBroken": "",
		"fSkillUsageLockPickEasy": "",
		"fSkillUsageLockPickHard": "",
		"fSkillUsageLockPickVeryEasy": "",
		"fSkillUsageLockPickVeryHard": "",
		"fSkillUsageRechargeMult": "",
		"fSkillUsageSneakHidden": "",
		"fSkillUsageSneakPerSecond": "",
		"fSkillUseCurve": "",
		"fSmallBumpSpeed": "",
		"fSmithingArmorMax": "",
		"fSmithingConditionFactor": "",
		"fSmithingWeaponMax": "",
		"fSneakActionMult": "",
		"fSneakAlertMod": "",
		"fSneakAmbushNonTargetMod": "",
		"fSneakAmbushTargetMod": "",
		"fSneakAttackSkillUsageMelee": "",
		"fSneakAttackSkillUsageRanged": "",
		"fSneakCombatMod": "",
		"fSneakDetectionSizeLarge": "",
		"fSneakDetectionSizeNormal": "",
		"fSneakDetectionSizeSmall": "",
		"fSneakDetectionSizeVeryLarge": "",
		"fSneakDistanceAttenuationExponent": "",
		"fSneakEquippedWeightBase": "",
		"fSneakEquippedWeightMult": "",
		"fSneakExteriorDistanceMult": "",
		"fSneakFlyingDistanceMult": "",
		"fSneakLightExteriorMult": "",
		"fSneakLightMoveMult": "",
		"fSneakLightMult": "",
		"fSneakLightRunMult": "",
		"fSneakMaxDistance": "",
		"fSneakNoticeMin": "",
		"fSneakPerceptionSkillMax": "",
		"fSneakPerceptionSkillMin": "",
		"fSneakRunningMult": "",
		"fSneakSizeBase": "",
		"fSneakSkillMult": "",
		"fSneakSleepBonus": "",
		"fSneakSleepMod": "",
		"fSneakSoundLosMult": "",
		"fSneakSoundsMult": "",
		"fSneakStealthBoyMult": "",
		"fSortActorDistanceListTimer": "",
		"fSpeechCraftBase": "",
		"fSpeechcraftFavorMax": "",
		"fSpeechcraftFavorMin": "",
		"fSpeechCraftMult": "",
		"fSpeechDelay": "",
		"fSpellCastingDetectionHitActorMod": "",
		"fSpellCastingDetectionMod": "",
		"fSpellmakingGoldMult": "",
		"fSplashScale1": "",
		"fSplashScale2": "",
		"fSplashScale3": "",
		"fSplashSoundHeavy": "",
		"fSplashSoundLight": "",
		"fSplashSoundMedium": "",
		"fSplashSoundOutMult": "",
		"fSplashSoundTimer": "",
		"fSplashSoundVelocityMult": "",
		"fSprintEncumbranceMult": "",
		"fSprintStaminaDrainMult": "",
		"fSprintStaminaWeightBase": "",
		"fSprintStaminaWeightMult": "",
		"fStagger1WeapMult": "",
		"fStagger2WeapMult": "",
		"fStaggerAttackBase": "",
		"fStaggerAttackMult": "",
		"fStaggerBlockAttackBase": "",
		"fStaggerBlockAttackMult": "",
		"fStaggerBlockAttackShieldBase": "",
		"fStaggerBlockAttackShieldMult": "",
		"fStaggerBlockBase": "",
		"fStaggerBlockingMult": "",
		"fStaggerBlockMult": "",
		"fStaggerMassBase": "",
		"fStaggerMassMult": "",
		"fStaggerMassOffsetBase": "",
		"fStaggerMassOffsetMult": "",
		"fStaggerMaxDuration": "",
		"fStaggerMin": "",
		"fStaggerPlayerMassMult": "",
		"fStaggerRecoilingMult": "",
		"fStaggerRunningMult": "",
		"fStaggerShieldMult": "",
		"fStaminaAttackWeaponBase": "",
		"fStaminaAttackWeaponMult": "",
		"fStaminaBashBase": "",
		"fStaminaBlockBase": "",
		"fStaminaBlockDmgMult": "",
		"fStaminaBlockStaggerMult": "",
		"fStaminaPowerBashBase": "",
		"fStaminaRegenDelayMax": "",
		"fStarsRotateDays": "",
		"fStarsRotateXAxis": "",
		"fStarsRotateYAxis": "",
		"fStarsRotateZAxis": "",
		"fStatsCameraFOV": "",
		"fStatsCameraNearDistance": "",
		"fStatsHealthLevelMult": "",
		"fStatsHealthStartMult": "",
		"fStatsLineScale": "",
		"fStatsRotationRampTime": "",
		"fStatsRotationSpeedMax": "",
		"fStatsSkillsLookAtX": "",
		"fStatsSkillsLookAtY": "",
		"fStatsSkillsLookAtZ": "",
		"fStatsStarCameraOffsetX": "",
		"fStatsStarCameraOffsetY": "",
		"fStatsStarCameraOffsetZ": "",
		"fStatsStarLookAtX": "",
		"fStatsStarLookAtY": "",
		"fStatsStarLookAtZ": "",
		"fStatsStarScale": "",
		"fStatsStarXIncrement": "",
		"fStatsStarYIncrement": "",
		"fStatsStarZIncrement": "",
		"fStatsStarZInitialOffset": "",
		"fSubmergedAngularDamping": "",
		"fSubmergedLinearDampingH": "",
		"fSubmergedLinearDampingV": "",
		"fSubmergedLODDistance": "",
		"fSubmergedMaxSpeed": "",
		"fSubmergedMaxWaterDistance": "",
		"fSubSegmentVariance": "",
		"fSubtitleSpeechDelay": "",
		"fSummonDistanceCheckThreshold": "",
		"fSummonedCreatureFadeOutSeconds": "",
		"fSummonedCreatureMaxFollowDist": "",
		"fSummonedCreatureMinFollowDist": "",
		"fSummonedCreatureSearchRadius": "",
		"fSunAlphaTransTime": "",
		"fSunDirXExtreme": "",
		"fSunMinimumGlareScale": "",
		"fSunReduceGlareSpeed": "",
		"fSunXExtreme": "",
		"fSunYExtreme": "",
		"fSunZExtreme": "",
		"fSweetSpotAverage": "",
		"fSweetSpotEasy": "",
		"fSweetSpotHard": "",
		"fSweetSpotVeryEasy": "",
		"fSweetSpotVeryHard": "",
		"fTakeBackTimerSetting": "",
		"fTargetMovedCoveredMoveRepathLength": "",
		"fTargetMovedRepathLengthLow": "",
		"fTargetMovedRepathLength": "",
		"fTeammateAggroOnDistancefromPlayer": "",
		"fTeleportDoorActivateDelayTimer": "",
		"fTemperingSkillUseMult": "",
		"fTimerForPlayerFurnitureEnter": "",
		"fTipImpulse": "",
		"fTorchEvaluationTimer": "",
		"fTorchLightLevelInterior": "",
		"fTorchLightLevelMorning": "",
		"fTorchLightLevelNight": "",
		"fTrackDeadZoneXY": "",
		"fTrackDeadZoneZ": "",
		"fTrackEyeXY": "",
		"fTrackEyeZ": "",
		"fTrackFudgeXY": "",
		"fTrackFudgeZ": "",
		"fTrackJustAcquiredDuration": "",
		"fTrackMaxZ": "",
		"fTrackMinZ": "",
		"fTrackSpeed": "",
		"fTrackXY": "",
		"fTrainingBaseCost": "",
		"fTrainingMultCost": "",
		"fTrapHitEventDelayMS": "",
		"fTriggerAvoidPlayerDistance": "",
		"fUnarmedCreatureDPSMult": "",
		"fUnarmedDamageMult": "",
		"fUnarmedNPCDPSMult": "",
		"fUnderwaterFullDepth": "",
		"fValueofItemForNoOwnership": "",
		"fVATSAutomaticMeleeDamageMult": "",
		"fVATSCameraMinTime": "",
		"fVATSCamTransRBDownStart": "",
		"fVATSCamTransRBRampDown": "",
		"fVATSCamTransRBRampup": "",
		"fVATSCamTransRBStart": "",
		"fVATSCamTransRBStrengthCap": "",
		"fVATSCamZoomInTime": "",
		"fVATSChanceHitMult": "",
		"fVATSCriticalChanceBonus": "",
		"fVATSDamageToWeaponMult": "",
		"fVATSDestructibleMult": "",
		"fVATSDistanceFactor": "",
		"fVATSDOFRange": "",
		"fVATSDOFStrengthCap": "",
		"fVATSDOFSwitchSeconds": "",
		"fVATSGrenadeChanceMult": "",
		"fVATSGrenadeDistAimZMult": "",
		"fVATSGrenadeRangeMin": "",
		"fVATSGrenadeRangeMult": "",
		"fVATSGrenadeSkillFactor": "",
		"fVATSGrenadeSuccessExplodeTimer": "",
		"fVATSGrenadeSuccessMaxDistance": "",
		"fVATSGrenadeTargetArea": "",
		"fVATSGrenadeTargetMelee": "",
		"fVATSH2HWarpDistanceMult": "",
		"fVATSImageSpaceTransitionTime": "",
		"fVATSLimbSelectCamPanTime": "",
		"fVATSMaxChance": "",
		"fVATSMaxEngageDistance": "",
		"fVATSMeleeArmConditionBase": "",
		"fVATSMeleeArmConditionMult": "",
		"fVATSMeleeChanceMult": "",
		"fVATSMeleeMaxDistance": "",
		"fVATSMeleeReachMult": "",
		"fVATSMeleeWarpDistanceMult": "",
		"fVATSMoveCameraLimbMult": "",
		"fVATSMoveCameraLimbPercent": "",
		"fVATSMoveCameraMaxSpeed": "",
		"fVATSMoveCameraXPercent": "",
		"fVATSMoveCameraYPercent": "",
		"fVATSParalyzePalmChance": "",
		"fVATSPlaybackDelay": "",
		"fVATSPlayerDamageMult": "",
		"fVATSPlayerMagicTimeSlowdownMult": "",
		"fVATSPlayerTimeUpdateMult": "",
		"fVATSRadialRampup": "",
		"fVATSRadialStart": "",
		"fVATSRadialStrength": "",
		"fVATSRangeSpreadMax": "",
		"fVATSRangeSpreadUncertainty": "",
		"fVATSScreenPercentFactor": "",
		"fVATSShotBurstTime": "",
		"fVatsShotgunSpreadRatio": "",
		"fVATSShotLongBurstTime": "",
		"fVATSSkillFactor": "",
		"fVATSSmartCameraCheckHeight": "",
		"fVATSSmartCameraCheckStepCount": "",
		"fVATSSmartCameraCheckStepDistance": "",
		"fVATSSpreadMult": "",
		"fVATSStealthMult": "",
		"fVATSStrangerDistance": "",
		"fVATSStrangerOdds": "",
		"fVATSTargetActorHeightPanMult": "",
		"fVATSTargetActorZMultFarDist": "",
		"fVATSTargetActorZMultFar": "",
		"fVATSTargetActorZMultNear": "",
		"fVATSTargetFOVMinDist": "",
		"fVATSTargetFOVMinFOV": "",
		"fVATSTargetFOVMultFarDist": "",
		"fVATSTargetFOVMultFar": "",
		"fVATSTargetFOVMultNear": "",
		"fVATSTargetRotateMult": "",
		"fVATSTargetScanRotateMult": "",
		"fVATSTargetSelectCamPanTime": "",
		"fVATSTargetTimeUpdateMult": "",
		"fVATSThrownWeaponRangeMult": "",
		"fVoiceRateBase": "",
		"fWardAngleForExplosions": "",
		"fWarningTimer": "",
		"fWaterKnockdownSizeLarge": "",
		"fWaterKnockdownSizeNormal": "",
		"fWaterKnockdownSizeSmall": "",
		"fWaterKnockdownSizeVeryLarge": "",
		"fWaterKnockdownVelocity": "",
		"fWeaponBashMax": "",
		"fWeaponBashMin": "",
		"fWeaponBashPCMax": "",
		"fWeaponBashPCMin": "",
		"fWeaponBashSkillUseBase": "",
		"fWeaponBashSkillUseMult": "",
		"fWeaponBlockSkillUseBase": "",
		"fWeaponBlockSkillUseMult": "",
		"fWeaponClutterKnockBipedScale": "",
		"fWeaponClutterKnockMaxWeaponMass": "",
		"fWeaponClutterKnockMinClutterMass": "",
		"fWeaponClutterKnockMult": "",
		"fWeaponConditionCriticalChanceMult": "",
		"fWeaponConditionJam1": "",
		"fWeaponConditionJam2": "",
		"fWeaponConditionJam3": "",
		"fWeaponConditionJam4": "",
		"fWeaponConditionJam5": "",
		"fWeaponConditionJam6": "",
		"fWeaponConditionJam7": "",
		"fWeaponConditionJam8": "",
		"fWeaponConditionJam9": "",
		"fWeaponConditionJam10": "",
		"fWeaponConditionRateOfFire1": "",
		"fWeaponConditionRateOfFire2": "",
		"fWeaponConditionRateOfFire3": "",
		"fWeaponConditionRateOfFire4": "",
		"fWeaponConditionRateOfFire5": "",
		"fWeaponConditionRateOfFire6": "",
		"fWeaponConditionRateOfFire7": "",
		"fWeaponConditionRateOfFire8": "",
		"fWeaponConditionRateOfFire9": "",
		"fWeaponConditionRateOfFire10": "",
		"fWeaponConditionReloadJam1": "",
		"fWeaponConditionReloadJam2": "",
		"fWeaponConditionReloadJam3": "",
		"fWeaponConditionReloadJam4": "",
		"fWeaponConditionReloadJam5": "",
		"fWeaponConditionReloadJam6": "",
		"fWeaponConditionReloadJam7": "",
		"fWeaponConditionReloadJam8": "",
		"fWeaponConditionReloadJam9": "",
		"fWeaponConditionReloadJam10": "",
		"fWeaponConditionSpread1": "",
		"fWeaponConditionSpread2": "",
		"fWeaponConditionSpread3": "",
		"fWeaponConditionSpread4": "",
		"fWeaponConditionSpread5": "",
		"fWeaponConditionSpread6": "",
		"fWeaponConditionSpread7": "",
		"fWeaponConditionSpread8": "",
		"fWeaponConditionSpread9": "",
		"fWeaponConditionSpread10": "",
		"fWeaponTwoHandedAnimationSpeedMult": "",
		"fWeatherFlashAmbient": "",
		"fWeatherFlashDirectional": "",
		"fWeatherFlashDuration": "",
		"fWeatherTransAccel": "",
		"fWeatherTransMax": "",
		"fWeatherTransMin": "",
		"fWortalchmult": "",
		"fWortcraftChanceIntDenom": "",
		"fWortcraftChanceLuckDenom": "",
		"fWortcraftStrChanceDenom": "",
		"fWortcraftStrCostDenom": "",
		"fWortFailSkillUseMagnitude": "",
		"fWortStrMult": "",
		"fXPLevelUpBase": "",
		"fXPLevelUpMult": "",
		"fXPPerSkillRank": "",
		"fZKeyComplexHelperMinDistance": "",
		"fZKeyComplexHelperScale": "",
		"fZKeyComplexHelperWeightMax": "",
		"fZKeyComplexHelperWeightMin": "",
		"fZKeyHeavyWeight": "",
		"fZKeyMaxContactDistance": "",
		"fZKeyMaxContactMassRatio": "",
		"fZKeyMaxForceScaleHigh": "",
		"fZKeyMaxForceScaleLow": "",
		"fZKeyMaxForceWeightHigh": "",
		"fZKeyMaxForceWeightLow": "",
		"fZKeyMaxForce": "",
		"fZKeyObjectDamping": "",
		"fZKeySpringDamping": "",
		"fZKeySpringElasticity": ""
		}
		return items

class SublimePapyrusSkyrimIntegerGameSettingNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"iActivatePickLength": "",
		"iActorKeepTurnDegree": "",
		"iActorLuckSkillBase": "",
		"iActorTorsoMaxRotation": "",
		"iAICombatMaxAllySummonCount": "",
		"iAICombatMinDetection": "",
		"iAICombatRestoreHealthPercentage": "",
		"iAICombatRestoreMagickaPercentage": "",
		"iAIFleeMaxHitCount": "",
		"iAIMaxSocialDistanceToTriggerEvent": "",
		"iAimingNumIterations": "",
		"iAINPCRacePowerChance": "",
		"iAINumberActorsComplexScene": "",
		"iAINumberDaysToStayBribed": "",
		"iAINumberDaysToStayIntimidated": "",
		"iAISocialDistanceToTriggerEvent": "",
		"iAlertAgressionMin": "",
		"iAllowAlchemyDuringCombat": "",
		"iAllowRechargeDuringCombat": "",
		"iAllowRepairDuringCombat": "",
		"iAllyHitCombatAllowed": "",
		"iAllyHitNonCombatAllowed": "",
		"iArmorBaseSkill": "",
		"iArmorDamageBootsChance": "",
		"iArmorDamageCuirassChance": "",
		"iArmorDamageGauntletsChance": "",
		"iArmorDamageGreavesChance": "",
		"iArmorDamageHelmChance": "",
		"iArmorDamageShieldChance": "",
		"iArrestOnSightNonViolent": "",
		"iArrestOnSightViolent": "",
		"iArrowInventoryChance": "",
		"iArrowMaxCount": "",
		"iAttackOnSightNonViolent": "",
		"iAttackOnSightViolent": "",
		"iAttractModeIdleTime": "",
		"iAVDAutoCalcSkillMax": "",
		"iAVDhmsLevelup": "",
		"iAVDSkillsLevelUp": "",
		"iAVDSkillStart": "",
		"iAvoidHurtingNonTargetsResponsibility": "",
		"iBallisticProjectilePathPickSegments": "",
		"iBloodSplatterMaxCount": "",
		"iBoneLODDistMult": "",
		"iClassAcrobat": "",
		"iClassAgent": "",
		"iClassArcher": "",
		"iClassAssassin": "",
		"iClassBarbarian": "",
		"iClassBard": "",
		"iClassBattlemage": "",
		"iClassCharactergenClass": "",
		"iClassCrusader": "",
		"iClassHealer": "",
		"iClassKnight": "",
		"iClassMage": "",
		"iClassMonk": "",
		"iClassNightblade": "",
		"iClassPilgrim": "",
		"iClassPriest": "",
		"iClassRogue": "",
		"iClassScout": "",
		"iClassSorcerer": "",
		"iClassSpellsword": "",
		"iClassThief": "",
		"iClassWarrior": "",
		"iClassWitchhunter": "",
		"iCombatAimMaxIterations": "",
		"iCombatCastDrainMinimumValue": "",
		"iCombatCrippledTorsoHitStaggerChance": "",
		"iCombatDismemberPartChance": "",
		"iCombatExplodePartChance": "",
		"iCombatFlankingAngleOffsetCount": "",
		"iCombatFlankingAngleOffsetGoalCount": "",
		"iCombatFlankingDirectionOffsetCount": "",
		"iCombatHighPriorityModifier": "",
		"iCombatHoverLocationCount": "",
		"iCombatSearchDoorFailureMax": "",
		"iCombatStealthPointDetectionThreshold": "",
		"iCombatStealthPointSneakDetectionThreshold": "",
		"iCombatTargetLocationCount": "",
		"iCombatTargetPlayerSoftCap": "",
		"iCombatUnloadedActorLastSeenTimeLimit6": "",
		"iCommonSoulActorLevel": "",
		"iCrimeAlarmLowRecDistance": "",
		"iCrimeAlarmRecDistance": "",
		"iCrimeCommentNumber": "",
		"iCrimeDaysInPrisonMod": "",
		"iCrimeEnemyCoolDownTimer": "",
		"iCrimeFavorBaseValue": "",
		"iCrimeGoldAttack": "",
		"iCrimeGoldEscape": "",
		"iCrimeGoldMinValue": "",
		"iCrimeGoldMurder": "",
		"iCrimeGoldPickpocket": "",
		"iCrimeGoldStealHorse": "",
		"iCrimeGoldTrespass": "",
		"iCrimeGoldWerewolf": "",
		"iCrimeMaxNumberofDaysinJail": "",
		"iCrimeRegardBaseValue": "",
		"iCrimeValueAttackValue": "",
		"iCurrentTargetBonus": "",
		"iDeathDropWeaponChance": "",
		"iDebrisMaxCount": "",
		"iDetectEventLightLevelExterior": "",
		"iDetectEventLightLevelInterior": "",
		"iDialogueDispositionFriendValue": "",
		"iDismemberBloodDecalCount": "",
		"iDispKaramMax": "",
		"iDistancetoAttackedTarget": "",
		"iFallLegDamageChance": "",
		"iFavorAllyValue": "",
		"iFavorConfidantValue": "",
		"iFavorFriendValue": "",
		"iFavorLoverValue": "",
		"iFavorPointsRestore": "",
		"iFriendHitCombatAllowed": "",
		"iFriendHitNonCombatAllowed": "",
		"iGameplayiSpeakingEmotionDeltaChange": "",
		"iGameplayiSpeakingEmotionListenValue": "",
		"iGrandSoulActorLevel": "",
		"iGreaterSoulActorLevel": "",
		"iGuardWarnings": "",
		"iHairColor00": "",
		"iHairColor01": "",
		"iHairColor02": "",
		"iHairColor03": "",
		"iHairColor04": "",
		"iHairColor05": "",
		"iHairColor06": "",
		"iHairColor07": "",
		"iHairColor08": "",
		"iHairColor09": "",
		"iHairColor10": "",
		"iHairColor11": "",
		"iHairColor12": "",
		"iHairColor13": "",
		"iHairColor14": "",
		"iHairColor15": "",
		"iHorseTurnDegreesPerSecond": "",
		"iHorseTurnDegreesRampUpPerSecond": "",
		"iInventoryAskQuantityAt": "",
		"iKarmaMax": "",
		"iKarmaMin": "",
		"iKillCamLevelOffset": "",
		"iLargeProjectilePickCount": "",
		"iLesserSoulActorLevel": "",
		"iLevelUpReminder": "",
		"iLightLevelExteriorMod": "",
		"iLightLevelInteriorMod": "",
		"iLightLevelMax": "",
		"iLowLevelNPCMaxLevel": "",
		"iMagicGuideWaypoints": "",
		"iMagicLightMaxCount": "",
		"iMapMarkerFadeStartDistance": "",
		"iMapMarkerRevealDistance": "",
		"iMapMarkerVisibleDistance": "",
		"iMasserSize": "",
		"iMaxAttachedArrows": "",
		"iMaxCharacterLevel": "",
		"iMaxPlayerRunes": "",
		"iMaxSummonedCreatures": "",
		"iMessCrippledLimbExplodeBonus": "",
		"iMessIntactLimbDismemberChance": "",
		"iMessTargetedLimbExplodeBonus": "",
		"iMessTorsoExplodeChance": "",
		"iMinClipSizeToAddReloadDelay": "",
		"iMineDisarmExperience": "",
		"iMoodFaceValue": "",
		"iNPCBasePerLevelHealthMult": "",
		"iNumberActorsAllowedToFollowPlayer": "",
		"iNumberActorsGoThroughLoadDoorInCombat": "",
		"iNumberActorsInCombatPlayer": "",
		"iNumberGuardsCrimeResponse": "",
		"iNumExplosionDecalCDPoint": "",
		"iPCStartSpellSkillLevel": "",
		"iPerkAttackDisarmChance": "",
		"iPerkBlockDisarmChance": "",
		"iPerkBlockStaggerChance": "",
		"iPerkHandToHandBlockRecoilChance": "",
		"iPerkHeavyArmorJumpSum": "",
		"iPerkHeavyArmorSinkSum": "",
		"iPerkLightArmorMasterMinSum": "",
		"iPerkMarksmanKnockdownChance": "",
		"iPerkMarksmanParalyzeChance": "",
		"iPersuasionAngleMax": "",
		"iPersuasionAngleMin": "",
		"iPersuasionBribeCrime": "",
		"iPersuasionBribeGold": "",
		"iPersuasionBribeRefuse": "",
		"iPersuasionBribeScale": "",
		"iPersuasionDemandDisposition": "",
		"iPersuasionDemandGold": "",
		"iPersuasionDemandRefuse": "",
		"iPersuasionDemandScale": "",
		"iPersuasionInner": "",
		"iPersuasionMiddle": "",
		"iPersuasionOuter": "",
		"iPersuasionPower1": "",
		"iPersuasionPower2": "",
		"iPersuasionPower3": "",
		"iPickPocketWarnings": "",
		"iPlayerCustomClass": "",
		"iPlayerHealthHeartbeatFadeMS": "",
		"iProjectileMaxRefCount": "",
		"iProjectileMineShooterCanTrigger": "",
		"iQuestReminderPipboyDisabledTime": "",
		"iRelationshipAcquaintanceValue": "",
		"iRelationshipAllyValue": "",
		"iRelationshipArchnemesisValue": "",
		"iRelationshipConfidantValue": "",
		"iRelationshipEnemyValue": "",
		"iRelationshipFoeValue": "",
		"iRelationshipFriendValue": "",
		"iRelationshipLoverValue": "",
		"iRelationshipRivalValue": "",
		"iRemoveExcessDeadComplexCount": "",
		"iRemoveExcessDeadComplexTotalActorCount": "",
		"iRemoveExcessDeadCount": "",
		"iRemoveExcessDeadTotalActorCount": "",
		"iSecondsToSleepPerUpdate": "",
		"iSecundaSize": "",
		"iShockBranchNumBolts": "",
		"iShockBranchSegmentsPerBolt": "",
		"iShockDebug": "",
		"iShockNumBolts": "",
		"iShockSegmentsPerBolt": "",
		"iShockSubSegments": "",
		"iSkillPointsTagSkillMult": "",
		"iSkillUsageSneakFullDetection": "",
		"iSkillUsageSneakMinDetection": "",
		"iSneakSkillUseDistance": "",
		"iSoundLevelLoud": "",
		"iSoundLevelNormal": "",
		"iSoundLevelSilent": "",
		"iSoundLevelVeryLoud": "",
		"iSpeechChallengeDifficultyAverage": "",
		"iSpeechChallengeDifficultyEasy": "",
		"iSpeechChallengeDifficultyHard": "",
		"iSpeechChallengeDifficultyVeryEasy": "",
		"iSpeechChallengeDifficultyVeryHard": "",
		"iStaggerAttackChance": "",
		"iStealWarnings": "",
		"iTrainingExpertCost": "",
		"iTrainingExpertSkill": "",
		"iTrainingJourneymanCost": "",
		"iTrainingJourneymanSkill": "",
		"iTrainingMasterCost": "",
		"iTrainingMasterSkill": "",
		"iTrainingNumAllowedPerLevel": "",
		"iTrespassWarnings": "",
		"iVATSCameraHitDist": "",
		"iVATSConcentratedFireBonus": "",
		"iVATSStrangerMaxHP": "",
		"iVoicePointsDefault": "",
		"iWeaponCriticalHitDropChance": "",
		"iXPBase": "",
		"iXPBumpBase": "",
		"iXPRewardDiscoverMapMarker": "",
		"iXPRewardDiscoverSecretArea": "",
		"iXPRewardHackComputer": "",
		"iXPRewardKillOpponent": "",
		"iXPRewardPickLock": ""
		}
		return items

class SublimePapyrusSkyrimStringGameSettingNameSuggestionsCommand(SublimePapyrus.SublimePapyrusShowSuggestionsCommand):
	def get_items(self, **args):
		items = {
		"sAccept": "",
		"sActionMapping": "",
		"sActivateCreatureCalmed": "",
		"sActivateNPCCalmed": "",
		"sActivate": "",
		"sActivationChoiceMessage": "",
		"sActiveEffects": "",
		"sActiveMineDescription": "",
		"sActorFade": "",
		"sAddCrimeGold": "",
		"sAddedEffects": "",
		"sAddedNote": "",
		"sAddItemtoInventory": "",
		"sAddItemtoSpellList": "",
		"sAdd": "",
		"sAlchemyMenuDescription": "",
		"sAlchemy": "",
		"sAllegiance": "",
		"sAllItems": "",
		"sAlreadyKnown": "",
		"sAlreadyPlacedMine": "",
		"sAlteration": "",
		"sAmber": "",
		"sAnimationCanNotEquipArmor": "",
		"sAnimationCanNotEquipWeapon": "",
		"sAnimationCanNotUnequip": "",
		"sApparel": "",
		"sAreaText": "",
		"sArmorEnchantments": "",
		"sArmorRating": "",
		"sArmorSmithing": "",
		"sArmor": "",
		"sAttack": "",
		"sAttributeDamaged": "",
		"sAttributeDrained": "",
		"sAttributesCount": "",
		"sAttributesTitle": "",
		"sAutoLoading": "",
		"sAutosaveAbbrev": "",
		"sAutoSaveDisabledDueToLackOfSpace": "",
		"sAutoSavingLong": "",
		"sAutoSaving": "",
		"sBack": "",
		"sBleedingOutMessage": "",
		"sBloodParticleDefault": "",
		"sBloodParticleMeleeDefault": "",
		"sBloodSplatterAlpha01OPTFilename": "",
		"sBloodSplatterColor01OPTFilename": "",
		"sBloodSplatterFlare01Filename": "",
		"sBloodTextureDefault": "",
		"sBooks": "",
		"sBountyStatString": "",
		"sBounty": "",
		"sBrightness": "",
		"sBroken": "",
		"sButtonLocked": "",
		"sButton": "",
		"sCameraPitch": "",
		"sCancel": "",
		"sCanNotEquipWornEnchantment": "",
		"sCanNotReadBook": "",
		"sCanNotTrainAnymore": "",
		"sCanNotTrainHigher": "",
		"sCantChangeResolution": "",
		"sCantEquipBrokenItem": "",
		"sCantEquipGeneric": "",
		"sCantEquipPowerArmor": "",
		"sCantHotkeyItem": "",
		"sCantQuickLoad": "",
		"sCantQuickSave": "",
		"sCantRemoveWornItem": "",
		"sCantRepairPastMax": "",
		"sCantSaveNow": "",
		"sCantUnequipGeneric": "",
		"sChangeItemSelection": "",
		"sCharGenControlsDisabled": "",
		"sChemsAddicted": "",
		"sChemsWithdrawal": "",
		"sChemsWornOff": "",
		"sChooseSoulGem": "",
		"sChoose": "",
		"sCleared": "",
		"sClearSelections": "",
		"sClose": "",
		"sCombatCannotActivate": "",
		"sConfirmAttribute": "",
		"sConfirmContinue": "",
		"sConfirmDelete": "",
		"sConfirmDisenchant": "",
		"sConfirmLoad": "",
		"sConfirmNew": "",
		"sConfirmSave": "",
		"sConfirmSpendSoul": "",
		"sConfirmWarning": "",
		"sConjuration": "",
		"sConstructibleMenuConfirm": "",
		"sConstructibleMenuDescription": "",
		"sContainerItemsTitle": "",
		"sContainerPlaceChance": "",
		"sContainerStealChance": "",
		"sContinue": "",
		"sContractedDisease": "",
		"sControllerOption": "",
		"sCorruptContentMessage": "",
		"sCraft": "",
		"sCreatedPoisonNamePrefix": "",
		"sCreatedPotionNamePrefix": "",
		"sCreated": "",
		"sCreate": "",
		"sCriticalStrike": "",
		"sCrosshair": "",
		"sCurrentLocation": "",
		"sCurrentObjective": "",
		"sCursorFilename": "",
		"sDaedric": "",
		"sDamage": "",
		"sDefaultMessage": "",
		"sDefaultPlayerName": "",
		"sDeleteSaveGame": "",
		"sDeleteSuccessful": "",
		"sDestruction": "",
		"sDeviceRemoved": "",
		"sDevice": "",
		"sDialogSubtitles": "",
		"sDifficulty": "",
		"sDisableHelp": "",
		"sDisableXBoxController": "",
		"sDiscoveredEffects": "",
		"sDiscoveredIngredientEffectEating": "",
		"sDiscoveredText": "",
		"sDisenchant": "",
		"sDismemberParticleDefault": "",
		"sDismemberRobotParticleDefault": "",
		"sDone": "",
		"sDownloadsAvailable": "",
		"sDownloadsNotAvail": "",
		"sDragonSoulAcquired": "",
		"sDragon": "",
		"sDraugr": "",
		"sDropEquippedItemWarning": "",
		"sDropQuestItemWarning": "",
		"sDungeonCleared": "",
		"sDurationText": "",
		"sDwarven": "",
		"sEbony": "",
		"sEffectAlreadyAdded": "",
		"sEffectsListDisplayHours": "",
		"sEffectsListDisplayHour": "",
		"sEffectsListDisplayMins": "",
		"sEffectsListDisplayMin": "",
		"sEffectsListDisplaySecs": "",
		"sEffectsListDisplaySec": "",
		"sEffectsVolume": "",
		"sElven": "",
		"sEmpty": "",
		"sEnableHelp": "",
		"sEnchantArmorIncompatible": "",
		"sEnchantDeconstructMenuDescription": "",
		"sEnchanting": "",
		"sEnchantInsufficientCharge": "",
		"sEnchantItem": "",
		"sEnchantmentKnown": "",
		"sEnchantmentsLearned": "",
		"sEnchantment": "",
		"sEnchantMenuDescription": "",
		"sEnchantMustChooseItems": "",
		"sEnterItemName": "",
		"sEnterName": "",
		"sEquipItemOnPlayer": "",
		"sEssentialCharacterDown": "",
		"sExitGameAffirm": "",
		"sExit": "",
		"sExpert": "",
		"sExplosionSplashParticles": "",
		"sFailedActivation": "",
		"sFailShouting": "",
		"sFailSpendSoul": "",
		"sFalmer": "",
		"sFastTravelConfirm": "",
		"sFastTravelNoTravelHealthDamage": "",
		"sFavorites": "",
		"sFileNotFound": "",
		"sFindingContentMessage": "",
		"sFirstPersonSkeleton": "",
		"sFood": "",
		"sFootstepsVolume": "",
		"sFor": "",
		"sFullHealth": "",
		"sFurnitureSleep": "",
		"sGeneralSubtitles": "",
		"sGFWLive": "",
		"sGlass": "",
		"sGold": "",
		"sGotAwayWithStealing": "",
		"sGrassFade": "",
		"sHairColor0": "",
		"sHairColor1": "",
		"sHairColor2": "",
		"sHairColor3": "",
		"sHairColor4": "",
		"sHairColor5": "",
		"sHairColor6": "",
		"sHairColor7": "",
		"sHairColor8": "",
		"sHairColor9": "",
		"sHairColor10": "",
		"sHairColor11": "",
		"sHairColor12": "",
		"sHairColor13": "",
		"sHairColor14": "",
		"sHairColor15": "",
		"sHarvest": "",
		"sHealth": "",
		"sHeavyArmorNoJump": "",
		"sHeavyArmorSink": "",
		"sHelp": "",
		"sHide_": "",
		"sHigh": "",
		"sHold": "",
		"sHUDArmorRating": "",
		"sHUDColor": "",
		"sHUDCompleted": "",
		"sHUDDamage": "",
		"sHUDFailed": "",
		"sHUDOpacity": "",
		"sHUDStarted": "",
		"sIllusion": "",
		"sImpactParticleConcreteDefault": "",
		"sImpactParticleMetalDefault": "",
		"sImpactParticleWoodDefault": "",
		"sImperial": "",
		"sImpossibleLock": "",
		"sImprovement": "",
		"sInaccessible": "",
		"sIngredientFail": "",
		"sIngredients": "",
		"sIngredient": "",
		"sInsufficientGoldToTrain": "",
		"sInvalidPickpocket": "",
		"sIron": "",
		"sItemFade": "",
		"sItemTooExpensive": "",
		"sItemTooHeavy": "",
		"sItem": "",
		"sJewelry": "",
		"sJourneyman": "",
		"sJunk": "",
		"sKeyLocked": "",
		"sKeys": "",
		"sKnownEffects": "",
		"sLackRequiredPerksToImprove": "",
		"sLackRequiredPerkToImproveMagical": "",
		"sLackRequiredSkillToImprove": "",
		"sLackRequiredToCreate": "",
		"sLackRequiredToImprove": "",
		"sLarge": "",
		"sLearningEnchantments": "",
		"sLearn": "",
		"sLeather": "",
		"sLeaveMarker": "",
		"sLevelAbbrev": "",
		"sLevelProgress": "",
		"sLevelUpAvailable": "",
		"sLightFade": "",
		"sLoadFromMainMenu": "",
		"sLoadingArea": "",
		"sLoadingContentMessage": "",
		"sLoadingLOD": "",
		"sLoading": "",
		"sLoadWhilePlaying": "",
		"sLockBroken": "",
		"sLocked": "",
		"sLockpickInsufficientPerks": "",
		"sLostController": "",
		"sLow": "",
		"sMagicEffectNotApplied": "",
		"sMagicEffectResisted": "",
		"sMagicEnhanceWeaponNoWeapon": "",
		"sMagicEnhanceWeaponWeaponEnchanted": "",
		"sMagicGuideNoMarker": "",
		"sMagicGuideNoPath": "",
		"sMagicTelekinesisNoRecast": "",
		"sMagnitudeIsLevelText": "",
		"sMagnitudeText": "",
		"sMainMenu": "",
		"sMakeDefaults": "",
		"sMapMarkerAdded": "",
		"sMasterVolume": "",
		"sMaster": "",
		"sMedium": "",
		"sMenuDisplayAutosaveName": "",
		"sMenuDisplayDayString": "",
		"sMenuDisplayLevelString": "",
		"sMenuDisplayNewSave": "",
		"sMenuDisplayNoSaves": "",
		"sMenuDisplayPlayTime": "",
		"sMenuDisplayQuicksaveName": "",
		"sMenuDisplaySave": "",
		"sMenuDisplayShortXBoxSaveMessage": "",
		"sMenuDisplayUnknownLocationString": "",
		"sMenuDisplayXBoxSaveMessage": "",
		"sMiscConstantEffect": "",
		"sMiscPlayerDeadLoadOption": "",
		"sMiscPlayerDeadMenuOption": "",
		"sMiscPlayerDeadMessage": "",
		"sMiscQuestDescription": "",
		"sMiscQuestName": "",
		"sMiscUnknownEffect": "",
		"sMisc": "",
		"sMissingImage": "",
		"sMissingName": "",
		"sMouseSensitivity": "",
		"sMoveMarkerQuestion": "",
		"sMoveMarker": "",
		"sMultipleDragonSoulCount": "",
		"sMusicVolume": "",
		"sMustRestart": "",
		"sName": "",
		"sNeutral": "",
		"sNewSave": "",
		"sNext": "",
		"sNoArrows": "",
		"sNoChargeItems_": "",
		"sNoChildUse": "",
		"sNoDeviceSelected": "",
		"sNoEatQuestItem": "",
		"sNoFastTravelAlarm": "",
		"sNoFastTravelCell": "",
		"sNoFastTravelCombat": "",
		"sNoFastTravelDefault": "",
		"sNoFastTravelHostileActorsNear": "",
		"sNoFastTravelInAir": "",
		"sNoFastTravelOverencumbered": "",
		"sNoFastTravelScriptBlock": "",
		"sNoFastTravelUndiscovered": "",
		"sNoItemsToRepair": "",
		"sNoJumpWarning": "",
		"sNoKeyDropWarning": "",
		"sNoLockPickIfCrimeAlert": "",
		"sNoMoreFollowers": "",
		"sNone": "",
		"sNoPickPocketAgain": "",
		"sNoProfileSelected": "",
		"sNoRepairHostileActorsNear": "",
		"sNoRepairInCombat": "",
		"sNoRestart": "",
		"sNormalWeaponsResisted": "",
		"sNormal": "",
		"sNoSaves": "",
		"sNoSitOnOwnedFurniture": "",
		"sNoSleepDefault": "",
		"sNoSleepHostileActorsNear": "",
		"sNoSleepInAir": "",
		"sNoSleepInCell": "",
		"sNoSleepInOwnedBed": "",
		"sNoSleepTakingHealthDamage": "",
		"sNoSleepTrespass": "",
		"sNoSleepWarnToLeave": "",
		"sNoSleepWhileAlarm": "",
		"sNoSpareParts": "",
		"sNoTalkFleeing": "",
		"sNoTalkUnConscious": "",
		"sNotAllowedToUseAutoDoorsWhileonHorse": "",
		"sNotEnoughRoomWarning": "",
		"sNotEnoughVendorGold": "",
		"sNoWaitDefault": "",
		"sNoWaitHostileActorsNear": "",
		"sNoWaitInAir": "",
		"sNoWaitInCell": "",
		"sNoWaitTakingHealthDamage": "",
		"sNoWaitTrespass": "",
		"sNoWaitWarnToLeave": "",
		"sNoWaitWhileAlarm": "",
		"sNo": "",
		"sNumberAbbrev": "",
		"sObjectFade": "",
		"sObjectInUse": "",
		"sObjectLODFade": "",
		"sOff": "",
		"sOf": "",
		"sOk": "",
		"sOldDownloadsAvailable": "",
		"sOn": "",
		"sOpenedContainer": "",
		"sOpenWithKey": "",
		"sOpen": "",
		"sOptional": "",
		"sOrcish": "",
		"sOr": "",
		"sOutOfLockpicks": "",
		"sOverEncumbered": "",
		"sOwned": "",
		"sPauseText": "",
		"sPCControlsTextNone": "",
		"sPCControlsTextPrefix": "",
		"sPCControlsTriggerPrefix": "",
		"sPCRelationshipNegativeChangeText": "",
		"sPCRelationshipPositiveChangeText": "",
		"sPickpocketFail": "",
		"sPickpocket": "",
		"sPipboyColor": "",
		"sPlaceMarkerUndiscovered": "",
		"sPlaceMarker": "",
		"sPlayerDisarmedMessage": "",
		"sPlayerLeavingBorderRegion": "",
		"sPlayerSetMarkerName": "",
		"sPlayTime": "",
		"sPleaseStandBy": "",
		"sPoisonAlreadyPoisonedMessage": "",
		"sPoisonBowConfirmMessage": "",
		"sPoisonConfirmMessage": "",
		"sPoisoned": "",
		"sPoisonNoWeaponMessage": "",
		"sPoisonUnableToPoison": "",
		"sPotionCreationFailed": "",
		"sPotions": "",
		"sPowers": "",
		"sPressControl": "",
		"sPreviousSelection": "",
		"sPrevious": "",
		"sPrisoner": "",
		"sQuantity": "",
		"sQuestAddedText": "",
		"sQuestCompletedText": "",
		"sQuestFailed": "",
		"sQuestUpdatedText": "",
		"sQuickLoading": "",
		"sQuicksaveAbbrev": "",
		"sQuickSaving": "",
		"sQuitAlchemy": "",
		"sQuitEnchanting": "",
		"sRadioSignalLost": "",
		"sRadioStationDiscovered": "",
		"sRadioVolume": "",
		"sRangeText": "",
		"sRanksText": "",
		"sRead": "",
		"sRemoteActivation": "",
		"sRemoveCrimeGold": "",
		"sRemoveItemFromInventory": "",
		"sRemoveMarker": "",
		"sRemove": "",
		"sRenameItem": "",
		"sRepairAllItems": "",
		"sRepairCost": "",
		"sRepairItem": "",
		"sRepairServicesTitle": "",
		"sRepairSkillTooLow": "",
		"sRepairSkill": "",
		"sRepair": "",
		"sRequirementsText": "",
		"sRequirements": "",
		"sResetToDefaults": "",
		"sResolution": "",
		"sResource": "",
		"sRestartBecauseContentRemoved": "",
		"sRestartSignedOut": "",
		"sRestartToUseNewContent": "",
		"sRestartToUseProfileContent": "",
		"sRestoration": "",
		"sReturn": "",
		"sRewardXPIcon": "",
		"sRewardXP": "",
		"sRide": "",
		"sRSMAge": "",
		"sRSMBody": "",
		"sRSMBrowForward": "",
		"sRSMBrowHeight": "",
		"sRSMBrowTypes": "",
		"sRSMBrowWidth": "",
		"sRSMBrow": "",
		"sRSMCheekboneHeight": "",
		"sRSMCheekboneWidth": "",
		"sRSMCheekColorLower": "",
		"sRSMCheekColor": "",
		"sRSMChinColor": "",
		"sRSMChinForward": "",
		"sRSMChinLength": "",
		"sRSMChinWidth": "",
		"sRSMComplexionColor": "",
		"sRSMComplexion": "",
		"sRSMConfirmDestruction": "",
		"sRSMConfirm": "",
		"sRSMDirtColor": "",
		"sRSMDirt": "",
		"sRSMEyeColor": "",
		"sRSMEyeDepth": "",
		"sRSMEyeHeight": "",
		"sRSMEyelinerColor": "",
		"sRSMEyeSocketLowerColor": "",
		"sRSMEyeSocketUpperColor": "",
		"sRSMEyes": "",
		"sRSMEyeTypes": "",
		"sRSMEyeWidth": "",
		"sRSMFace": "",
		"sRSMFacialHairColorPresets": "",
		"sRSMFacialHairPresets": "",
		"sRSMForeheadColor": "",
		"sRSMHairColorPresets": "",
		"sRSMHairPresets": "",
		"sRSMHair": "",
		"sRSMHeadPresets": "",
		"sRSMHead": "",
		"sRSMJawForward": "",
		"sRSMJawHeight": "",
		"sRSMJawWidth": "",
		"sRSMLaughLines": "",
		"sRSMLipColor": "",
		"sRSMMouthForward": "",
		"sRSMMouthHeight": "",
		"sRSMMouthTypes": "",
		"sRSMMouth": "",
		"sRSMNameWarning": "",
		"sRSMName": "",
		"sRSMNeckColor": "",
		"sRSMNoseColor": "",
		"sRSMNoseHeight": "",
		"sRSMNoseLength": "",
		"sRSMNoseTypes": "",
		"sRSMPaintColor": "",
		"sRSMPaint": "",
		"sRSMRace": "",
		"sRSMScars": "",
		"sRSMSex": "",
		"sRSMSkinColor": "",
		"sRSMTone": "",
		"sRSMWeight": "",
		"sRumble": "",
		"sSaveFailed": "",
		"sSaveGameContentIsMissing": "",
		"sSaveGameCorruptMenuMessage": "",
		"sSaveGameCorrupt": "",
		"sSaveGameDeviceError": "",
		"sSaveGameIsCorrupt": "",
		"sSaveGameNoLongerAvailable": "",
		"sSaveGameNoMasterFilesFound": "",
		"sSaveGameOldVersion": "",
		"sSaveGameOutOfDiskSpace": "",
		"sSaveNotAvailable": "",
		"sSaveOnRest": "",
		"sSaveOnTravel": "",
		"sSaveOnWait": "",
		"sSaveOverSaveGame": "",
		"sSaveSuccessful": "",
		"sSceneBlockingActorActivation": "",
		"sScrollEquipped": "",
		"sScrolls": "",
		"sSearch": "",
		"sSelectItemToRepair": "",
		"sSelect": "",
		"sSelfRange": "",
		"sServeSentenceQuestion": "",
		"sServeTimeQuestion": "",
		"sSexFemalePossessive": "",
		"sSexFemalePronoun": "",
		"sSexFemale": "",
		"sSexMalePossessive": "",
		"sSexMalePronoun": "",
		"sSexMale": "",
		"sShadowFade": "",
		"sShoutAdded": "",
		"sShouts": "",
		"sSingleDragonSoulCount": "",
		"sSit": "",
		"sSkillIncreasedNum": "",
		"sSkillIncreased": "",
		"sSkillsCount": "",
		"sSkillsTitle": "",
		"sSmall": "",
		"sSmithingConfirm": "",
		"sSmithingMenuDescription": "",
		"sSneakAttack": "",
		"sSneakCaution": "",
		"sSneakDanger": "",
		"sSneakDetected": "",
		"sSneakHidden": "",
		"sSortMethod": "",
		"sSoulCaptured": "",
		"sSoulGems": "",
		"sSoulGemTooSmall": "",
		"sSoulGem": "",
		"sSoulLevel": "",
		"sSpace": "",
		"sSpecularityFade": "",
		"sSpeechChallengeFailure": "",
		"sSpeechChallengeSuccess": "",
		"sSpellAdded": "",
		"sSplashParticles": "",
		"sStatsMustSelectPerk": "",
		"sStatsNextRank": "",
		"sStatsPerkConfirm": "",
		"sStealFrom": "",
		"sStealHorse": "",
		"sSteal": "",
		"sSteel": "",
		"sStormcloak": "",
		"sStudded": "",
		"sSuccessfulSneakAttackEnd": "",
		"sSuccessfulSneakAttackMain": "",
		"sTakeAll": "",
		"sTake": "",
		"sTalk": "",
		"sTargetRange": "",
		"sTeammateCantGiveOutfit": "",
		"sTeammateCantTakeOutfit": "",
		"sTeammateOverencumbered": "",
		"sTextureSize": "",
		"sStormcloak": "",
		"sTouchRange": "",
		"sTo": "",
		"sTraitsCount": "",
		"sTraitsTitle": "",
		"sTreeLODFade": "",
		"sTweenDisabledMessage": "",
		"sUnequipItemOnPlayer": "",
		"sUnlock": "",
		"sValue": "",
		"sVatsAimed": "",
		"sVatsAiming": "",
		"sVatsBodyPart": "",
		"sVATSMessageLowAP": "",
		"sVATSMessageNoAmmo": "",
		"sVATSMessageZeroChance": "",
		"sVatsSelect": "",
		"sVatsTarget": "",
		"sVDSGManual": "",
		"sVDSGPlate": "",
		"sVideoChange": "",
		"sViewDistance": "",
		"sVoiceVolume": "",
		"sWaitHere": "",
		"sWeaponBreak": "",
		"sWeaponEnchantments": "",
		"sWeaponSmithing": "",
		"sWeapons": "",
		"sWeight": "",
		"sWhite": "",
		"sWitnessKilled": "",
		"sWood": "",
		"sXSensitivity": "",
		"sYesRestart": "",
		"sYes": "",
		"sYour": "",
		"sYSensitivity": ""
		}
		return items
