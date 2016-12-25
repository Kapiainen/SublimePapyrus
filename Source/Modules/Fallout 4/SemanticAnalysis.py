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
		"currentStatement", # statement
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

	def EnterEmptyStateScope(self):
		self.currentScope.append(ScopeEnum.SCRIPT)
		self.stack.append([self.currentStatement])

	def EnterStateScope(self):
		self.currentScope.append(ScopeEnum.STATE)
		self.stack.append([self.currentStatement])

	def LeaveStateScope(self):
		self.currentScope.pop()

	def EnterFunctionScope(self):
		self.currentScope.append(ScopeEnum.FUNCTION)
		self.stack.append([self.currentStatement])
		if self.currentStatement.flags.isNative:
			self.pendingDocstring = self.LeaveFunctionScope

	def LeaveFunctionScope(self):
		scope = self.stack.pop()
		signature = scope.pop(0)
		docstring = None
		if scope and isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
			docstring = scope.pop(0)
		for statement in scope:
			if isinstance(statement, SyntacticAnalysis.DocstringStatement):
				if docstring:
					raise SemanticError("This function already has a docstring.", statement.line)
				else:
					raise SemanticError("A docstring has to be the next statement after the function signature.", statement.line)
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
		if signature.flags.isNative:
			self.stack[-1].append(FunctionObject(signature, scope, signature.line))
		else:
			self.stack[-1].append(FunctionObject(signature, scope, self.currentStatement.line))
		self.currentScope.pop()

	def EnterEventScope(self):
		self.currentScope.append(ScopeEnum.EVENT)
		self.stack.append([self.currentStatement])

	def LeaveEventScope(self):
		self.currentScope.pop()

	def EnterPropertyScope(self):
		self.currentScope.append(ScopeEnum.PROPERTY)
		self.stack.append([self.currentStatement])
		if self.currentStatement.flags.isAuto or self.currentStatement.flags.isAutoReadOnly:
			self.pendingDocstring = self.LeavePropertyScope

	def LeavePropertyScope(self):
		scope = self.stack.pop()
		signature = scope.pop(0)
		docstring = None
		getFunction = None
		setFunction = None
		if scope and isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
			docstring = scope.pop(0)
		for element in scope:
			if isinstance(element, SyntacticAnalysis.DocstringStatement):
				if docstring:
					raise SemanticError("Properties can only have one docstring.", element.line)
				else:
					raise SemanticError("A docstring has to be the next statement after the property signature.", element.line)
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
		if signature.flags.isAuto or signature.flags.isAutoReadOnly:
			self.stack[-1].append(PropertyObject(signature, setFunction, getFunction, signature.line))
		else:
			if not setFunction and not getFunction:
				raise SemanticError("This property has to have at least a 'Set' or a 'Get' function.", signature.line)
			self.stack[-1].append(PropertyObject(signature, setFunction, getFunction, self.currentStatement.line))
		self.currentScope.pop()

	def EnterStructScope(self):
		self.currentScope.append(ScopeEnum.STRUCT)
		self.stack.append([self.currentStatement])

	def LeaveStructScope(self):
		self.currentScope.pop()

	def EnterGroupScope(self):
		self.currentScope.append(ScopeEnum.GROUP)
		self.stack.append([self.currentStatement])

	def LeaveGroupScope(self):
		self.currentScope.pop()

	def Assemble(self, aStat):
		print("Current scope: %s" % ScopeDescription[self.currentScope[-1]])
		self.currentStatement = aStat
		if self.pendingDocstring:
			if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
				self.stack[-1].append(aStat)
				self.pendingDocstring()
				self.pendingDocstring = None
				return
			else:
				self.pendingDocstring()
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
		elif currentScope == ScopeEnum.ELSEIF:
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
		elif currentScope == ScopeEnum.EVENT:
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
		elif currentScope == ScopeEnum.FUNCTION:
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
		elif currentScope == ScopeEnum.GROUP:
			if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.PropertySignatureStatement):
				self.EnterPropertyScope()
			elif isinstance(aStat, SyntacticAnalysis.EndGroupStatement):
				self.LeaveGroupScope()
			else:
				raise SemanticError("Illegal statement in the group scope.", aStat.line)
		elif currentScope == ScopeEnum.IF:
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
		elif currentScope == ScopeEnum.PROPERTY:
			if isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
				self.EnterFunctionScope()
			elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
				self.stack[-1].append(aStat)
			elif isinstance(aStat, SyntacticAnalysis.EndPropertyStatement):
				self.LeavePropertyScope()
			else:
				raise SemanticError("Illegal statement in the property scope.", aStat.line)
		elif currentScope == ScopeEnum.SCRIPT:
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
		elif currentScope == ScopeEnum.STATE:
			if isinstance(aStat, SyntacticAnalysis.EventSignatureStatement):
				self.EnterEventScope()
			elif isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
				self.EnterFunctionScope()
			elif isinstance(aStat, SyntacticAnalysis.EndStateStatement):
				self.LeaveStateScope()
			else:
				raise SemanticError("Illegal statement in the state scope.", aStat.line)
		elif currentScope == ScopeEnum.STRUCT:
			if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
				pass
			elif isinstance(aStat, SyntacticAnalysis.EndStructStatement):
				self.LeaveStructScope()
			else:
				raise SemanticError("Illegal statement in the struct scope.", aStat.line)
		elif currentScope == ScopeEnum.WHILE:
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
		elif self.capricaExtensions:
			if currentScope == ScopeEnum.SWITCHCASE:
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
			elif currentScope == ScopeEnum.SWITCHDEFAULT:
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
			elif currentScope == ScopeEnum.DO:
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
			elif currentScope == ScopeEnum.FOR:
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
			elif currentScope == ScopeEnum.FOREACH:
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
			elif currentScope == ScopeEnum.SWITCH:
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
