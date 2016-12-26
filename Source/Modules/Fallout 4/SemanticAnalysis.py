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

class SemanticError(Exception):
	def __init__(self, aMessage, aLine):
	# aMessage: string
	# aLine: int
		self.message = aMessage
		self.line = aLine

# First phase of semantic analysis
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

class SemanticFirstPhase(object):
	__slots__ = [
		"capricaExtensions", # bool
		"currentScope", # ScopeEnum
		"stack", # list of objects
		"pendingDocstring" # function
	]

	def __init__(self):
		pass

	def Reset(self, aCaprica):
		self.capricaExtensions = aCaprica
		self.currentScope = [-1]
		self.stack = []
		self.pendingDocstring = None

# ==================== Empty state/script ====================
	def EnterEmptyStateScope(self, aStat):
		self.currentScope.append(ScopeEnum.SCRIPT)
		self.stack.append([aStat])

	def EmptyStateScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.CustomEventStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EventSignatureStatement):
			self.EnterEventScope()
		elif isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope()
		elif isinstance(aStat, SyntacticAnalysis.GroupSignatureStatement):
			self.EnterGroupScope()
		elif isinstance(aStat, SyntacticAnalysis.ImportStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.PropertySignatureStatement):
			self.EnterPropertyScope()
		elif isinstance(aStat, SyntacticAnalysis.StateSignatureStatement):
			self.EnterStateScope()
		elif isinstance(aStat, SyntacticAnalysis.StructSignatureStatement):
			self.EnterStructScope()
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		else:
			raise SemanticError("Illegal statement in the empty state scope.", aStat.line)

	def LeaveEmptyStateScope(self):
		pass

# ==================== State ====================
	def EnterStateScope(self, aStat):
		self.currentScope.append(ScopeEnum.STATE)
		self.stack.append([aStat])

	def StateScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.EventSignatureStatement):
			self.EnterEventScope()
		elif isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope()
		elif isinstance(aStat, SyntacticAnalysis.EndStateStatement):
			self.LeaveStateScope()
		else:
			raise SemanticError("Illegal statement in the state scope.", aStat.line)

	def LeaveStateScope(self, aStat):
		self.currentScope.pop()

# ==================== Function ====================
	def EnterFunctionScope(self, aStat):
		self.currentScope.append(ScopeEnum.FUNCTION)
		self.stack.append([aStat])
		if aStat.flags.isNative:
			self.pendingDocstring = self.LeaveFunctionScope

	def FunctionScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.EndFunctionStatement):
			self.LeaveFunctionScope()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def LeaveFunctionScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		docstring = None
		if scope and isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
			docstring = scope.pop(0)
		for statement in scope:
			# Docstring validation.
			if isinstance(statement, SyntacticAnalysis.DocstringStatement):
				if docstring:
					raise SemanticError("This function already has a docstring.", statement.line)
				else:
					raise SemanticError("A docstring has to be the next statement after the function signature.", statement.line)
			# Partial return statement validation.
			elif isinstance(statement, SyntacticAnalysis.ReturnStatement):
				if signature.type:
					if not statement.expression:
						if signature.type.isArray:
							raise SemanticError("This function has to return a(n) '%s' array." % signature.type.identifier, statement.line)
						else:
							raise SemanticError("This function has to return a(n) '%s' value." % signature.type.identifier, statement.line)
				else:
					if statement.expression:
						raise SemanticError("This function does not have a return type.", statement.line)
		if not scope:
			scope = None
		# Native function: signature + optional docstring
		if signature.flags.isNative:
			self.stack[-1].append(FunctionObject(signature, scope, signature.line))
		# Non-native function: signature + optional docstring + function body
		else:
			self.stack[-1].append(FunctionObject(signature, scope, aStat.line))
		self.currentScope.pop()

# ==================== Event ====================
	def EnterEventScope(self, aStat):
		self.currentScope.append(ScopeEnum.EVENT)
		self.stack.append([aStat])

	def EventScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.EndEventStatement):
			self.LeaveEventScope()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def LeaveEventScope(self, aStat):
		self.currentScope.pop()

# ==================== Function/event sub-scopes ====================
	def IfScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ElseIfStatement):
			self.currentScope.pop()
			self.currentScope.append(ScopeEnum.ELSEIF)
		elif isinstance(aStat, SyntacticAnalysis.ElseStatement):
			self.currentScope.pop()
			self.currentScope.append(ScopeEnum.ELSE)
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def ElseIfScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ElseIfStatement):
			self.currentScope.pop()
			self.currentScope.append(ScopeEnum.ELSEIF)
		elif isinstance(aStat, SyntacticAnalysis.ElseStatement):
			self.currentScope.pop()
			self.currentScope.append(ScopeEnum.ELSE)
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def ElseScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def WhileScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndWhileStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	#Caprica extensions
	def SwitchScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndSwitchStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def SwitchCaseScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.CaseStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.DefaultStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndSwitchStatement):
			pass
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def SwitchDefaultScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndSwitchStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def DoScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.LoopWhileStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def ForScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.IfStatement):
			self.currentScope.append(ScopeEnum.IF)
		elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
			self.currentScope.append(ScopeEnum.WHILE)
		elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
			self.currentScope.append(ScopeEnum.SWITCH)
		elif isinstance(aStat, SyntacticAnalysis.ForStatement):
			self.currentScope.append(ScopeEnum.FOR)
		elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
			self.currentScope.append(ScopeEnum.FOREACH)
		elif isinstance(aStat, SyntacticAnalysis.DoStatement):
			self.currentScope.append(ScopeEnum.DO)
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndForStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the function/event scope.", aStat.line)

	def ForEachScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.AssignmentStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.ExpressionStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.IfStatement):
				self.currentScope.append(ScopeEnum.IF)
			elif isinstance(aStat, SyntacticAnalysis.ReturnStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.WhileStatement):
				self.currentScope.append(ScopeEnum.WHILE)
			elif isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.EndForEachStatement):
				self.currentScope.pop()
			else:
				raise SemanticError("Illegal statement in the function/event scope.", aStat.line)
	#End of Caprica extensions

# ==================== Property ====================
	def EnterPropertyScope(self, aStat):
		self.currentScope.append(ScopeEnum.PROPERTY)
		self.stack.append([aStat])
		if aStat.flags.isAuto or aStat.flags.isAutoReadOnly:
			self.pendingDocstring = self.LeavePropertyScope

	def PropertyScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope()
		elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.EndPropertyStatement):
			self.LeavePropertyScope()
		else:
			raise SemanticError("Illegal statement in the property scope.", aStat.line)

	def LeavePropertyScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		docstring = None
		getFunction = None
		setFunction = None
		if scope and isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
			docstring = scope.pop(0)
		for element in scope:
			# Docstring validation
			if isinstance(element, SyntacticAnalysis.DocstringStatement):
				if docstring:
					raise SemanticError("Properties can only have one docstring.", element.line)
				else:
					raise SemanticError("A docstring has to be the next statement after the property signature.", element.line)
			# Function validation (name and return type)
			elif isinstance(element, FunctionObject):
				name = str(element.identifier).upper()
				if name == "GET":
					if getFunction:
						raise SemanticError("This property already has a 'Get' function.", element.starts)
					else:
						if signature.type.identifier == element.type.identifier and signature.type.isArray == element.type.isArray:
							getFunction = element
						else:
							if signature.type.isArray:
								raise SemanticError("Expected 'Get' function to return a(n) '%s' array." % signature.type.identifier, element.starts)
							else:
								raise SemanticError("Expected 'Get' function to return a(n) '%s' value." % signature.type.identifier, element.starts)
				elif name == "SET":
					if setFunction:
						raise SemanticError("This property already has a 'Set' function.", element.starts)
					else:
						setFunction = element
				else:
					raise SemanticError("Properties can only have 'Get' and 'Set' functions.", element.starts)
			else:
				raise Exception("Unsupported property element:", type(element))
		# Auto or AutoReadOnly property: signature + optional docstring
		if signature.flags.isAuto or signature.flags.isAutoReadOnly:
			self.stack[-1].append(PropertyObject(signature, setFunction, getFunction, signature.line))
		# Full property: signature + optional docstring + property body
		else:
			# Function validation (at least a Set or a Get function)
			if not setFunction and not getFunction:
				raise SemanticError("This property has to have at least a 'Set' or a 'Get' function.", signature.line)
			self.stack[-1].append(PropertyObject(signature, setFunction, getFunction, aStat.line))
		self.currentScope.pop()

# ==================== Struct ====================
	def EnterStructScope(self, aStat):
		self.currentScope.append(ScopeEnum.STRUCT)
		self.stack.append([aStat])

	def StructScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.EndStructStatement):
			self.LeaveStructScope()
		else:
			raise SemanticError("Illegal statement in the struct scope.", aStat.line)

	def LeaveStructScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		if scope:
			members = {}
			memberStack = []

			def ReduceMember():
				var = memberStack.pop(0)
				doc = None
				if memberStack:
					doc = memberStack.pop()
				key = str(var.identifier).upper()
				if members.get(key, None):
					raise SemanticError("This struct already has a member called '%s'." % var.identifier, var.line)
				members[key] = StructMember(var, doc)

			while scope:
				if isinstance(aStat, SyntacticAnalysis.VariableStatement):
					if memberStack:
						ReduceMember()
					memberStack.append(scope.pop(0))
				elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
					if memberStack:
						memberStack.append(scope.pop(0))
					else:
						raise SemanticError("Illegal docstring in the struct scope.", scope[0].line)
			if memberStack:
				ReduceMember()
			self.stack[-1].append(StructObject(signature, members, aStat.line))
		else:
			self.stack[-1].append(StructObject(signature, None, aStat.line))
		self.currentScope.pop()

# ==================== Group ====================
	def EnterGroupScope(self, aStat):
		self.currentScope.append(ScopeEnum.GROUP)
		self.stack.append([aStat])

	def GroupScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			self.stack[-1].append(aStat)
		elif isinstance(aStat, SyntacticAnalysis.PropertySignatureStatement):
			self.EnterPropertyScope()
		elif isinstance(aStat, SyntacticAnalysis.EndGroupStatement):
			self.LeaveGroupScope()
		else:
			raise SemanticError("Illegal statement in the group scope.", aStat.line)

	def LeaveGroupScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		if scope:
			members = {}
			docstring = None
			if isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
				docstring = scope.pop(0)
			for element in scope:
				# Docstring validation
				if isinstance(element, SyntacticAnalysis.DocstringStatement):
					if docstring:
						raise SemanticError("Groups can only have one docstring.", element.line)
					else:
						raise SemanticError("A docstring has to be the next statement after the group signature.", element.line)
				elif: isinstance(element, PropertyObject):
					key = str(element.identifier).upper()
					if members.get(key, None):
						raise SemanticError("This group already has a member called '%s'." % element.identifier, element.starts)
					members[key] = element
			if not members:
				members = None
			self.stack[-1].append(GroupObject(signature, docstring, members, aStat.line))
		else:
			self.stack[-1].append(GroupObject(signature, None, None, aStat.line))
		self.currentScope.pop()

# ==================== Assembling ====================
	def Assemble(self, aStat):
		print("Current scope: %s" % ScopeDescription[self.currentScope[-1]])
		if self.pendingDocstring:
			if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
				self.stack[-1].append(aStat)
				self.pendingDocstring(aStat)
				self.pendingDocstring = None
				return
			else:
				self.pendingDocstring(aStat)
				self.pendingDocstring = None
			print("Dropping down to: %s" % ScopeDescription[self.currentScope[-1]])
		currentScope = self.currentScope[-1]
		if currentScope == -1:
			print(type(aStat))
			if isinstance(aStat, SyntacticAnalysis.ScriptSignatureStatement):
				self.EnterEmptyStateScope()
			else:
				raise SemanticError("Expected the first statement to be the script header.", aStat.line)
		elif currentScope == ScopeEnum.ELSE:
			self.ElseScope(aStat)
		elif currentScope == ScopeEnum.ELSEIF:
			self.ElseIfScope(aStat)
		elif currentScope == ScopeEnum.EVENT:
			self.EventScope(aStat)
		elif currentScope == ScopeEnum.FUNCTION:
			self.FunctionScope(aStat)
		elif currentScope == ScopeEnum.GROUP:
			self.GroupScope(aStat)
		elif currentScope == ScopeEnum.IF:
			self.IfScope(aStat)
		elif currentScope == ScopeEnum.PROPERTY:
			self.PropertyScope(aStat)
		elif currentScope == ScopeEnum.SCRIPT:
			self.EmptyStateScope(aStat)
		elif currentScope == ScopeEnum.STATE:
			self.StateScope(aStat)
		elif currentScope == ScopeEnum.STRUCT:
			self.StructScope(aStat)
		elif currentScope == ScopeEnum.WHILE:
			self.WhileScope(aStat)
		#Caprica extensions
		elif self.capricaExtensions:
			if currentScope == ScopeEnum.SWITCHCASE:
				self.SwitchCaseScope(aStat)
			elif currentScope == ScopeEnum.SWITCHDEFAULT:
				self.SwitchDefaultScope(aStat)
			elif currentScope == ScopeEnum.DO:
				self.DoScope(aStat)
			elif currentScope == ScopeEnum.FOR:
				self.ForScope(aStat)
			elif currentScope == ScopeEnum.FOREACH:
				self.ForEachScope(aStat)
			elif currentScope == ScopeEnum.SWITCH:
				self.SwitchScope(aStat)
			else:
				raise SemanticError("Unsupported scope ('%s')." % ScopeDescription[currentScope], aStat.line)
		else:
			raise SemanticError("Unsupported scope ('%s')." % ScopeDescription[currentScope], aStat.line)

# ==================== Building ====================
	def BuildScript(self):
		"""Returns a Script"""
		pass

class FunctionObject(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type (optional)
		"parameters", # list of FunctionParameter (optional)
		"flags", # FunctionFlags
		"body", # list of statements
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aBody, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.FunctionSignatureStatement) #Prune
		if aBody: #Prune
			assert isinstance(aBody, list) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		self.parameters = aSignature.parameters
		self.flags = aSignature.flags
		self.body = aBody
		self.starts = aSignature.line
		self.ends = aEnds

class PropertyObject(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"value", # ExpressionNode (optional)
		"flags", #PropertyFlags
		"setFunction", # FunctionObject
		"getFunction", # FunctionObject
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aSetFunction, aGetFunction, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.PropertySignatureStatement) #Prune
		if aSetFunction: #Prune
			assert isinstance(aSetFunction, FunctionObject) #Prune
		if aGetFunction: #Prune
			assert isinstance(aGetFunction, FunctionObject) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		self.value = aSignature.value
		self.flags = aSignature.flags
		self.setFunction = aSetFunction
		self.getFunction = aGetFunction
		self.starts = aSignature.line
		self.ends = aEnds

class EventObject(object):
	__slots__ = [
		"identifier", # Identifier
		"remote", # Identifier
		"parameters", # list of EventParameter (optional)
		"flags", # EventFlags
		"body", # list of statements
		"starts", # int
		"ends" # int
	]

	def __init__(self):
		pass

class GroupObject(object):
	__slots__ = [
		"identifier", # Identifier
		"flags", # GroupFlags
		"docstring", # str
		"members", # dict of PropertyObject
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aDocstring, aMembers, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.GroupSignatureStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		if aMembers: #Prune
			assert isinstance(aMembers, dict) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.flags = aSignature.flags
		self.docstring = aDocstring.value
		self.members = aMembers
		self.starts = aSignature.line
		self.ends = aEnds

class ScriptObject(object):
	__slots__ = [
		"identifier", # Identifier
		"extends", # Identifier
		"flags", # ScriptFlags
		"dosctring", # str
		"functions", # dict of FunctionObject
		"events", # dict of EventObject
		"properties", # dict of PropertyObject
		"variables", # dict of VariableStatement
		"groups", # dict of GroupObject
		"structs", # dict of StructObject
		"states", # dict of StateObject
		"importedScripts", # dict of ImportStatement
		"importedNamespaces", # dict of ImportStatement
		"starts" # int
	]

	def __init__(self):
		pass

class StateObject(object):
	__slots__ = [
		"identifier", # Identifier
		"flags", # StateFlags
		"functions", # dict of FunctionObject
		"events", # dict of EventObject
		"starts", # int
		"ends" # int
	]

	def __init__(self):
		pass

class StructMember(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"docstring", # str
		"line" # int
	]

	def __init__(self, aSignature, aDocstring):
		assert isinstance(aSignature, SyntacticAnalysis.VariableStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		self.docstring = aDocstring.value
		self.line = aSignature.line

class StructObject(object):
	__slots__ = [
		"identifier", # Identifier
		"members", # dict of StructMember
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aMembers, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.StructSignatureStatement) #Prune
		if aMembers: #Prune
			assert isinstance(a, dict) #Prune
		assert isinstance(a, int) #Prune
		self.identifier = aSignature.identifier
		self.members = aMembers
		self.starts = aSignature.line
		self.ends = aEnds

# Second phase of semantic analysis
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