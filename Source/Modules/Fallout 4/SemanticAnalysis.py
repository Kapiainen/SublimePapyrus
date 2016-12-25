import os, sys
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
	import imp
	root, module = os.path.split(os.getcwd())

	lexicalModule = os.path.join(root, module, "LexicalAnalysis.py")
	imp.load_source("LexicalAnalysis", lexicalModule)

	syntacticModule = os.path.join(root, module, "SyntacticAnalysis.py")
	imp.load_source("SyntacticAnalysis", Module)

	#from LexicalAnalysis import *
	#from SyntacticAnalysis import *
	import LexicalAnalysis
	import SyntacticAnalysis

	# Cleaning up
	del root
	del module
	del coreModule
	del lexicalModule
	del syntacticModule
elif PYTHON_VERSION[0] >= 3:
	#from .LexicalAnalysis import *
	#from .SyntacticAnalysis import *
	from . import LexicalAnalysis
	from . import SyntacticAnalysis

class ScopeEnum(object):
	ELSE = 0
	ELSEIF = 1
	EVENT = 2
	FUNCTION = 3
	GROUP = 4
	IF = 5
	PROPERTY = 6
	SCRIPT = 7
	STATE = 8
	STRUCT = 9
	WHILE = 10
	#Caprica extensions
	SWITCHCASE = 11
	SWITCHDEFAULT = 12
	DO = 13
	FOR = 14
	FOREACH = 15
	SWITCH = 16

ScopeDescription = [
	"ELSE",
	"ELSEIF",
	"EVENT",
	"FUNCTION",
	"GROUP",
	"IF",
	"PROPERTY",
	"SCRIPT",
	"STATE",
	"STRUCT",
	"WHILE",
	#Caprica extensions
	"SWITCHCASE",
	"SWITCHDEFAULT",
	"DO",
	"FOR",
	"FOREACH",
	"SWITCH"
]

class SemanticError(Exception):
	def __init__(self, aMessage, aLine):
	# aMessage: string
	# aLine: int
		self.message = aMessage
		self.line = aLine

class SemanticFirstPhase(object):
	__slots__ = [
		"capricaExtensions", # bool
		"currentScope", # ScopeEnum
		"statementStack" # list of list of statements
	]

	def __init__(self):
		pass

	def Reset(self, aCaprica):
		self.capricaExtensions = aCaprica
		self.currentScope = [-1]

	def EnterEmptyStateScope(self):
		self.currentScope.append(ScopeEnum.SCRIPT)

	def EnterStateScope(self):
		self.currentScope.append(ScopeEnum.STATE)

	def LeaveStateScope(self):
		self.currentScope.pop()

	def EnterFunctionScope(self):
		self.currentScope.append(ScopeEnum.FUNCTION)

	def LeaveFunctionScope(self):
		self.currentScope.pop()

	def EnterEventScope(self):
		self.currentScope.append(ScopeEnum.EVENT)

	def LeaveEventScope(self):
		self.currentScope.pop()

	def EnterPropertyScope(self):
		self.currentScope.append(ScopeEnum.PROPERTY)

	def LeavePropertyScope(self):
		self.currentScope.pop()

	def EnterStructScope(self):
		self.currentScope.append(ScopeEnum.STRUCT)

	def LeaveStructScope(self):
		self.currentScope.pop()

	def EnterGroupScope(self):
		self.currentScope.append(ScopeEnum.GROUP)

	def LeaveGroupScope(self):
		self.currentScope.pop()


	def Assemble(self, aStat):
		currentScope = self.currentScope[-1]
		if currentScope == -1:
			print(type(aStat))
			if isinstance(aStat, SyntacticAnalysis.ScriptSignatureStatement):
				self.EnterEmptyStateScope()
			else:
				raise SemanticError("Expected the first statement to be the script header.", aStat.line)
		elif currentScope == ScopeEnum.ELSE:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, EndIfStatement):
				self.currentScope.pop()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		elif currentScope == ScopeEnum.ELSEIF:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, ElseIfStatement):
				self.currentScope.append(ScopeEnum.ELSEIF)
			elif isinstance(aStat, ElseStatement):
				self.currentScope.append(ScopeEnum.ELSE)
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, EndIfStatement):
				self.currentScope.pop()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		elif currentScope == ScopeEnum.EVENT:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, DocstringStatement):
				pass
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, EndEventStatement):
				self.LeaveEventScope()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		elif currentScope == ScopeEnum.FUNCTION:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, DocstringStatement):
				pass
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, EndFunctionStatement):
				self.LeaveFunctionScope()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		elif currentScope == ScopeEnum.GROUP:
			if isinstance(aStat, DocstringStatement):
				pass
			elif isinstance(aStat, PropertySignatureStatement):
				self.EnterPropertyScope()
			else:
				raise SemanticError("Illegal statement in the group scope.", aStat.line)
		elif currentScope == ScopeEnum.IF:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, ElseIfStatement):
				self.currentScope.append(ScopeEnum.ELSEIF)
			elif isinstance(aStat, ElseStatement):
				self.currentScope.append(ScopeEnum.ELSE)
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, EndIfStatement):
				self.currentScope.pop()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		elif currentScope == ScopeEnum.PROPERTY:
			if isinstance(aStat, FunctionSignatureStatement):
				self.EnterFunctionScope()
			elif isinstance(aStat, EndPropertyStatement):
				self.LeavePropertyScope()
			else:
				raise SemanticError("Illegal statement in the property scope.", aStat.line)
		elif currentScope == ScopeEnum.SCRIPT:
			if isinstance(aStat, CustomEventStatement):
				pass
			elif isinstance(aStat, DocstringStatement):
				pass
			elif isinstance(aStat, EventSignatureStatement):
				self.EnterEventScope()
			elif isinstance(aStat, FunctionSignatureStatement):
				self.EnterFunctionScope()
			elif isinstance(aStat, GroupSignatureStatement):
				self.EnterGroupScope()
			elif isinstance(aStat, ImportStatement):
				pass
			elif isinstance(aStat, PropertySignatureStatement):
				self.EnterPropertyScope()
			elif isinstance(aStat, StateSignatureStatement):
				self.EnterStateScope()
			elif isinstance(aStat, StructSignatureStatement):
				self.EnterStructScope()
			elif isinstance(aStat, VariableStatement):
				pass
			else:
				raise SemanticError("Illegal statement in the empty state scope.", aStat.line)
		elif currentScope == ScopeEnum.STATE:
			if isinstance(aStat, EventSignatureStatement):
				self.EnterEventScope()
			elif isinstance(aStat, FunctionSignatureStatement):
				self.EnterFunctionScope()
			elif isinstance(aStat, EndStateStatement):
				self.LeaveStateScope()
			else:
				raise SemanticError("Illegal statement in the state scope.", aStat.line)
		elif currentScope == ScopeEnum.STRUCT:
			if isinstance(aStat, DocstringStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, EndStructStatement):
				self.LeaveStructScope()
			else:
				raise SemanticError("Illegal statement in the struct scope.", aStat.line)
		elif currentScope == ScopeEnum.WHILE:
			if isinstance(aStat, AssignmentStatement):
				pass
			elif isinstance(aStat, ExpressionStatement):
				pass
			elif isinstance(aStat, IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, ReturnStatement):
				pass
			elif isinstance(aStat, VariableStatement):
				pass
			elif isinstance(aStat, WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, BreakStatement):
				pass
			elif isinstance(aStat, ContinueStatement):
				pass
			elif isinstance(aStat, EndWhileStatement):
				self.currentScope.pop()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
		#Caprica extensions
		elif self.capricaExtensions:
			if currentScope == ScopeEnum.SWITCHCASE:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, CaseStatement):
					pass
				elif isinstance(aStat, DefaultStatement):
					pass
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, EndSwitchStatement):
					pass
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			elif currentScope == ScopeEnum.SWITCHDEFAULT:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, EndSwitchStatement):
					self.currentScope.pop()
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			elif currentScope == ScopeEnum.DO:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, LoopWhileStatement):
					self.currentScope.pop()
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			elif currentScope == ScopeEnum.FOR:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, EndForStatement):
					self.currentScope.pop()
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			elif currentScope == ScopeEnum.FOREACH:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, EndForEachStatement):
					self.currentScope.pop()
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			elif currentScope == ScopeEnum.SWITCH:
				if isinstance(aStat, AssignmentStatement):
					pass
				elif isinstance(aStat, ExpressionStatement):
					pass
				elif isinstance(aStat, IfStatement):
					self.currentScope.append(ScopeEnum.IF)
				elif isinstance(aStat, ReturnStatement):
					pass
				elif isinstance(aStat, VariableStatement):
					pass
				elif isinstance(aStat, WhileStatement):
					self.currentScope.append(ScopeEnum.WHILE)
				elif isinstance(aStat, SwitchStatement):
					self.currentScope.append(ScopeEnum.SWITCH)
				elif isinstance(aStat, ForStatement):
					self.currentScope.append(ScopeEnum.FOR)
				elif isinstance(aStat, ForEachStatement):
					self.currentScope.append(ScopeEnum.FOREACH)
				elif isinstance(aStat, DoStatement):
					self.currentScope.append(ScopeEnum.DO)
				elif isinstance(aStat, BreakStatement):
					pass
				elif isinstance(aStat, ContinueStatement):
					pass
				elif isinstance(aStat, EndSwitchStatement):
					self.currentScope.pop()
				else:
					raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
			else:
				raise SemanticError("Unsupported scope ('%s')." % ScopeDescription[currentScope], aStat.line)
		else:
			raise SemanticError("Unsupported scope ('%s')." % ScopeDescription[currentScope], aStat.line)


	def BuildScript(self):
		"""Returns a Script"""
		pass

class SemanticSecondPhase(object):
	__slots__ = [
		"capricaExtensions" # bool
	]

	def __init__(self):
		pass

	def Reset(self, aCaprica):
		self.capricaExtensions = aCaprica

	def Process(self, aScript):
		pass

class FunctionObject(object):
	__slots__ = [
		"identifier",
		"type",
		"parameters",
		"flags",
		"line"
	]

	def __init__(self):
		pass