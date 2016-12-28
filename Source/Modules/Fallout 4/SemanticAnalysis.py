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

class RemoteError(Exception):
	def __init__(self, aMessage, aLine):
		self.message = aMessage
		self.line = aLine

class FunctionObject(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type (optional)
		"parameters", # list of FunctionParameter (optional)
		"flags", # FunctionFlags
		"docstring", # str
		"body", # list of statements
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aDocstring, aBody, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.FunctionSignatureStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		if aBody: #Prune
			assert isinstance(aBody, list) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		self.parameters = aSignature.parameters
		self.flags = aSignature.flags
		if aDocstring:
			self.docstring = aDocstring.value
		else:
			self.docstring = ""
		self.body = aBody
		self.starts = aSignature.line
		self.ends = aEnds

class PropertyObject(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"value", # ExpressionNode (optional)
		"flags", # PropertyFlags
		"docstring", # str
		"setFunction", # FunctionObject
		"getFunction", # FunctionObject
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aDocstring, aSetFunction, aGetFunction, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.PropertySignatureStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		if aSetFunction: #Prune
			assert isinstance(aSetFunction, FunctionObject) #Prune
		if aGetFunction: #Prune
			assert isinstance(aGetFunction, FunctionObject) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		self.value = aSignature.value
		self.flags = aSignature.flags
		if aDocstring:
			self.docstring = aDocstring.value
		else:
			self.docstring = ""
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

	def __init__(self, aSignature, aBody, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.EventSignatureStatement) #Prune
		if aBody: #Prune
			assert isinstance(aBody, list) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.remote = aSignature.remote
		self.parameters = aSignature.parameters
		self.flags = aSignature.flags
		self.body = aBody
		self.starts = aSignature.line
		self.ends = aEnds

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
		if aDocstring:
			self.docstring = aDocstring.value
		else:
			self.docstring = ""
		self.members = aMembers
		self.starts = aSignature.line
		self.ends = aEnds

class ScriptObject(object):
	__slots__ = [
		"identifier", # Identifier
		"extends", # Identifier
		"flags", # ScriptFlags
		"docstring", # str
		"functions", # dict of FunctionObject
		"events", # dict of EventObject
		"properties", # dict of PropertyObject
		"variables", # dict of VariableStatement
		"groups", # dict of GroupObject
		"structs", # dict of StructObject
		"states", # dict of StateObject
		"importedScripts", # dict of ImportStatement
		"importedNamespaces", # dict of ImportStatement
		"typeMap", # dict of TypeMapEntry
		"lineage", # list of str (most distant parent first, closest parent last -> Actor: ScriptObject, Form, ObjectReference)
		"starts" # int
	]

	def __init__(self, aSignature, aDocstring, aFunctions, aEvents, aProperties, aVariables, aGroups, aStructs, aStates, aImportedScripts, aImportedNamespaces, aTypeMap):
		assert isinstance(aSignature, SyntacticAnalysis.ScriptSignatureStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		if aFunctions: #Prune
			assert isinstance(aFunctions, dict) #Prune
		if aEvents: #Prune
			assert isinstance(aEvents, dict) #Prune
		if aProperties: #Prune
			assert isinstance(aProperties, dict) #Prune
		if aGroups: #Prune
			assert isinstance(aGroups, dict) #Prune
		if aStructs: #Prune
			assert isinstance(aStructs, dict) #Prune
		if aStates: #Prune
			assert isinstance(aStates, dict) #Prune
		if aVariables: #Prune
			assert isinstance(aVariables, dict) #Prune
		if aImportedScripts: #Prune
			assert isinstance(aImportedScripts, dict) #Prune
		if aImportedNamespaces: #Prune
			assert isinstance(aImportedNamespaces, dict) #Prune
		assert isinstance(aTypeMap, dict) #Prune
		self.identifier = aSignature.identifier
		self.extends = aSignature.extends
		self.flags = aSignature.flags
		if aDocstring:
			self.docstring = aDocstring.value
		else:
			self.docstring = ""
		self.functions = aFunctions
		self.events = aEvents
		self.properties = aProperties
		self.variables = aVariables
		self.groups = aGroups
		self.structs = aStructs
		self.states = aStates
		self.importedScripts = aImportedScripts
		self.importedNamespaces = aImportedNamespaces
		self.typeMap = aTypeMap
		self.lineage = []
		self.starts = aSignature.line

class StateObject(object):
	__slots__ = [
		"identifier", # Identifier
		"flags", # StateFlags
		"functions", # dict of FunctionObject
		"events", # dict of EventObject
		"starts", # int
		"ends" # int
	]

	def __init__(self, aSignature, aFunctions, aEvents, aEnds):
		assert isinstance(aSignature, SyntacticAnalysis.StateSignatureStatement) #Prune
		if aFunctions: #Prune
			assert isinstance(aFunctions, dict) #Prune
		if aEvents: #Prune
			assert isinstance(aEvents, dict) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.flags = aSignature.flags
		self.functions = aFunctions
		self.events = aEvents
		self.starts = aSignature.line
		self.ends = aEnds

class StructMember(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"defaultValue", # ExpressionNode
		"docstring", # str
		"line" # int
	]

	def __init__(self, aSignature, aDocstring):
		assert isinstance(aSignature, SyntacticAnalysis.VariableStatement) #Prune
		if aDocstring: #Prune
			assert isinstance(aDocstring, SyntacticAnalysis.DocstringStatement) #Prune
		self.identifier = aSignature.identifier
		self.type = aSignature.type
		if aDocstring:
			self.docstring = aDocstring.value
		else:
			self.docstring = ""
		self.defaultValue = aSignature.value
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
		assert isinstance(aMembers, dict) #Prune
		assert isinstance(aEnds, int) #Prune
		self.identifier = aSignature.identifier
		self.members = aMembers
		self.starts = aSignature.line
		self.ends = aEnds

class NodeResult(object):
	__slots__ = [
		"identifier", # Identifier
		"isArray", # bool
		"isStruct", # bool
		"isConstant", # bool
		"value", # str
		"isObject" # bool
	]

	def __init__(self, aIdentifier, aArray, aStruct, aConstant, aValue, aObject):
		self.identifier = aIdentifier
		self.isArray = aArray
		self.isStruct = aStruct
		self.isConstant = aConstant
		self.value = aValue
		self.isObject = aObject

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

class TypeMapEntry(object):
	__slots__ = [
		"identifier", # Identifier
		"isStruct" # bool
	]

	def __init__(self, aIdentifier, aStruct):
		self.identifier = aIdentifier
		self.isStruct = aStruct

#TODO: Implement auto-casting
#TODO: Move ConstantNodeVisitor, and the code that uses it, to the stage where function and event signatures are checked against the overridden signatures.
def ConstantNodeVisitor(aNode): # ImplementationKeyword: ConstantExpression
	# Implements: A NodeVisitor that can validate expressions used for default values (scriptwide variables, properties, struct members, and parameters)
	if isinstance(aNode, SyntacticAnalysis.ConstantNode):
		identifier = None
		if aNode.value.type == LexicalAnalysis.TokenEnum.kTRUE:
			identifier = SyntacticAnalysis.Identifier(["Bool"])
		elif aNode.value.type == LexicalAnalysis.TokenEnum.kFALSE:
			identifier = SyntacticAnalysis.Identifier(["Bool"])
		elif aNode.value.type == LexicalAnalysis.TokenEnum.FLOAT:
			identifier = SyntacticAnalysis.Identifier(["Float"])
		elif aNode.value.type == LexicalAnalysis.TokenEnum.INT:
			identifier = SyntacticAnalysis.Identifier(["Int"])
		elif aNode.value.type == LexicalAnalysis.TokenEnum.STRING:
			identifier = SyntacticAnalysis.Identifier(["String"])
		elif aNode.value.type == LexicalAnalysis.TokenEnum.kNONE:
			identifier = SyntacticAnalysis.Identifier(["None"])
		else:
			raise Exception("ConstantNodeVisitor: Unsupported constant type.")
		return NodeResult(identifier, False, False, True, aNode.value.value.upper(), True)
	elif isinstance(aNode, SyntacticAnalysis.ExpressionNode):
		return ConstantNodeVisitor(aNode.child)
	elif isinstance(aNode, SyntacticAnalysis.UnaryOperatorNode):
		if aNode.operator.type == LexicalAnalysis.TokenEnum.SUBTRACTION:
			result = ConstantNodeVisitor(aNode.operand)
			if result.isConstant:
				key = str(result.identifier).upper()
				if key == "INT" or key == "FLOAT":
					result.value = "-%s" % result.value
					return result
				else:
					raise SemanticError("The unary minus operator is only allowed in 'Int' or 'Float' constant expressions.", 0)
			else:
				raise SemanticError("Expected a constant expression after the unary minus operator.", 0)
		else:
			raise SemanticError("The unary minus operator is the only unary operator allowed in constant expressions.", 0)
	return None

def ConstantNodeVisitorWrapper(aNode, aLine):
	try:
		return ConstantNodeVisitor(aNode)
	except SemanticError as e:
		raise SemanticError(e.message, aLine)

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
			self.EnterEventScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.GroupSignatureStatement):
			self.EnterGroupScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.ImportStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.PropertySignatureStatement):
			self.EnterPropertyScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.StateSignatureStatement):
			self.EnterStateScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.StructSignatureStatement):
			self.EnterStructScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		else:
			raise SemanticError("Illegal statement in the 'Empty state' scope.", aStat.line)
		self.stack[-1].append(aStat)

	def LeaveEmptyStateScope(self, aGetPath): # ImplementationKeyword: Script
		scope = self.stack.pop()
		signature = scope.pop(0)
		if scope:
			# Implements: Script documentation string.
			docstring = None
			if isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
				docstring = scope.pop(0)
			functions = {}
			events = {}
			properties = {}
			variables = {}
			groups = {}
			structs = {}
			states = {}
			importedScripts = {}
			importedNamespaces = {}
			typeMap = {}
			def AddToTypeMap(aType):
				# 'typeKey' is what a type would be referred to from within the script in the context of any imports that may exist.
				# The info in the TypeMapEntry objects is the full, absolute namespace that does not depend upon the imports.
				# 'typeMap' can be processed once per script and then used to more quickly get to the correct ScriptObject that corresponds to the type.
				typeKey = str(aType.identifier).upper()
				if not typeMap.get(typeKey, None):
					typeMap[typeKey] = TypeMapEntry(aType.identifier, False)

			for element in scope:
				if isinstance(element, SyntacticAnalysis.DocstringStatement): # ImplementationKeyword: Docstring
					if docstring:
						raise SemanticError("This script already has a docstring.", element.line)
					else:
						raise SemanticError("A docstring has to be the next statement after the script signature.", element.line)
				elif isinstance(element, FunctionObject): # ImplementationKeyword: Function
					key = str(element.identifier).upper() #TODO: element.identifier.name.upper() instead?
					# Implements: Proper use of 'Native' flag
					if element.flags.isNative and not signature.flags.isNative:
						raise SemanticError("'Native' functions can only be defined in scripts with the 'Native' flag.", element.line)
					if functions.get(key, None):
						raise SemanticError("This script already has a function called '%s'." % element.identifier, element.starts)
					elif events.get(key, None):
						raise SemanticError("This script already has an event called '%s'." % element.identifier, element.starts)
					functions[key] = element
					if element.type:
						AddToTypeMap(element.type)
					if element.parameters:
						for param in element.parameters:
							AddToTypeMap(param.type)
				elif isinstance(element, EventObject): # ImplementationKeyword: Event
					# Proper use of 'Native' flag
					if element.flags.isNative and not signature.flags.isNative:
						raise SemanticError("'Native' events can only be defined in scripts with the 'Native' flag.", element.line)
					if element.remote:
						key = ("%s.%s" % (element.remote, element.identifier)).upper()
						if events.get(key, None):
							raise SemanticError("This script already has a remote event called '%s.%s'." % (element.remote, element.identifier), element.starts)
					else:
						key = str(element.identifier).upper()
						if events.get(key, None):
							raise SemanticError("This script already has an event called '%s'." % element.identifier, element.starts)
						elif functions.get(key, None):
							raise SemanticError("This script already has a function called '%s'." % element.identifier, element.starts)
					events[key] = element
					if element.parameters:
						for param in element.parameters:
							AddToTypeMap(param.type)
				elif isinstance(element, PropertyObject): # ImplementationKeyword: Property
					key = str(element.identifier).upper()
					if properties.get(key, None):
						raise SemanticError("This script already has a property called '%s'." % element.identifier, element.starts)
					elif variables.get(key, None):
						raise SemanticError("This script already has a variable called '%s'." % element.identifier, element.starts)
					properties[key] = element
					AddToTypeMap(element.type)
				elif isinstance(element, SyntacticAnalysis.VariableStatement): # ImplementationKeyword: Variable
					key = str(element.identifier).upper()
					if variables.get(key, None):
						raise SemanticError("This script already has a variable called '%s'." % element.identifier, element.line)
					elif properties.get(key, None):
						raise SemanticError("This script already has a property called '%s'." % element.identifier, element.line)
					# Implements: Scriptwide variables can only be declared with constant expressions.
					if element.value:
						exprType = ConstantNodeVisitorWrapper(element.value, element.line)
						if exprType:
							variableKey = str(element.type.identifier).upper()
							exprKey = str(exprType.identifier).upper()
							if not element.type.isArray:
								if variableKey == "BOOL" or variableKey == "FLOAT" or variableKey == "INT" or variableKey == "STRING":
									if exprKey != variableKey:
										if self.capricaExtensions and variableKey == "FLOAT" and exprKey == "INT":
											pass
										else:
											raise SemanticError("Expected the initial value to be a(n) '%s' value." % element.type.identifier, element.line)
								elif variableKey == "VAR":
									pass
								else:
									if exprKey != "NONE":
										raise SemanticError("Expected the initial value to be 'None'.", element.line)
							else:
								if exprKey != "NONE":
									raise SemanticError("Expected the initial value to be 'None'.", element.line)
						else:
							raise SemanticError("Scriptwide variables can only be initialized with constant expressions.", element.line)
					variables[key] = element
					AddToTypeMap(element.type)
				elif isinstance(element, GroupObject): # ImplementationKeyword: Group
					key = str(element.identifier).upper()
					if groups.get(key, None):
						raise SemanticError("This script already has a group called '%s'." % element.identifier, element.starts)
					for key, prop in element.members.items():
						if properties.get(key, None):
							raise SemanticError("This script already has a property called '%s'." % element.identifier, prop.starts)
						elif variables.get(key, None):
							raise SemanticError("This script already has a variable called '%s'." % element.identifier, prop.starts)
						properties[key] = prop
					groups[key] = element
					if element.members:
						for key, mem in element.members.items():
							AddToTypeMap(mem.type)
				elif isinstance(element, StructObject): # ImplementationKeyword: Struct
					key = str(element.identifier).upper()
					if structs.get(key, None):
						raise SemanticError("This script already has a struct called '%s'." % element.identifier, element.starts)
					structs[key] = element
					if element.members:
						for key, mem in element.members.items():
							AddToTypeMap(mem.type)
				elif isinstance(element, StateObject): # ImplementationKeyword: State
					key = str(element.identifier).upper()
					if states.get(key, None):
						raise SemanticError("This script already has a state called '%s'." % element.identifier, element.starts)
					states[key] = element
					if element.functions:
						for key, func in element.functions.items():
							if func.type:
								AddToTypeMap(func.type)
							if func.parameters:
								for param in func.parameters:
									AddToTypeMap(param.type)
					if element.events:
						for key, event in element.events.items():
							if event.parameters:
								for param in event.parameters:
									AddToTypeMap(param.type)
				elif isinstance(element, SyntacticAnalysis.ImportStatement): # ImplementationKeyword: Import
					filePath, dirPath = aGetPath(element.identifier)
					key = str(element.identifier).upper()
					if filePath and dirPath:
						raise SemanticError("Ambiguous import, could mean both a script and a namespace.", element.line)
					elif filePath:
						if importedScripts.get(key, None):
							raise SemanticError("This script has already been imported in this script.", element.line)
						importedScripts[key] = element
					elif dirPath:
						if importedNamespaces.get(key, None):
							raise SemanticError("This namespace has already been imported in this script.", element.line)
						importedNamespaces[key] = element
					else:
						raise SemanticError("This identifier does not match any script or namespace.", element.line)
			if not functions:
				functions = None
			if not events:
				events = None
			if not properties:
				properties = None
			if not variables:
				variables = None
			if not groups:
				groups = None
			if not structs:
				structs = None
			if not states:
				states = None
			if not importedScripts:
				importedScripts = None
			if not importedNamespaces:
				importedNamespaces = None
			self.stack.append(ScriptObject(signature, docstring, functions, events, properties, variables, groups, structs, states, importedScripts, importedNamespaces, typeMap))
		else:
			self.stack.append(ScriptObject(signature, None, None, None, None, None, None, None, None, None, None, {}))
		self.currentScope.pop()

# ==================== State ====================
	def EnterStateScope(self, aStat):
		self.currentScope.append(ScopeEnum.STATE)
		self.stack.append([aStat])

	def StateScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.EventSignatureStatement):
			self.EnterEventScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.EndStateStatement):
			self.LeaveStateScope(aStat)
			return
		else:
			raise SemanticError("Illegal statement in the 'State' scope.", aStat.line)

	def LeaveStateScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		if scope:
			functions = {}
			events = {}
			for element in scope:
				# Validation of duplicate function/event definitions.
				if isinstance(element, FunctionObject):
					key = str(element.identifier).upper()
					if functions.get(key, None):
						raise SemanticError("This state already has a function called '%s'." % element.identifier, element.starts)
					elif events.get(key, None):
						raise SemanticError("This state already has an event called '%s'." % element.identifier, element.starts)
					functions[key] = element
				elif isinstance(element, EventObject):
					key = None
					if element.remote:
						key = ("%s.%s" % (element.remote, element.identifier)).upper()
						if events.get(key, None):
							raise SemanticError("This state already has an event called '%s.%s'." % (element.remote, element.identifier), element.starts)
					else:
						key = str(element.identifier).upper()
						if events.get(key, None):
							raise SemanticError("This state already has an event called '%s'." % element.identifier, element.starts)
						elif functions.get(key, None):
							raise SemanticError("This state already has a function called '%s'." % element.identifier, element.starts)
					events[key] = element
			if not functions:
				functions = None
			if not events:
				events = None
			self.stack[-1].append(StateObject(signature, functions, events, aStat.line))
		else:
			self.stack[-1].append(StateObject(signature, None, None, aStat.line))
		self.currentScope.pop()

# ==================== Function ====================
	def EnterFunctionScope(self, aStat):
		self.currentScope.append(ScopeEnum.FUNCTION)
		self.stack.append([aStat])
		if aStat.flags.isNative:
			self.pendingDocstring = self.LeaveFunctionScope

	def FunctionScope(self, aStat):
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
		elif isinstance(aStat, SyntacticAnalysis.EndFunctionStatement):
			self.LeaveFunctionScope(aStat)
			return
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			else:
				raise SemanticError("Illegal statement in the 'Function' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'Function' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
			self.stack[-1].append(FunctionObject(signature, docstring, scope, signature.line))
		# Non-native function: signature + optional docstring + function body
		else:
			self.stack[-1].append(FunctionObject(signature, docstring, scope, aStat.line))
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
		elif isinstance(aStat, SyntacticAnalysis.EndEventStatement):
			self.LeaveEventScope(aStat)
			return
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			else:
				raise SemanticError("Illegal statement in the 'Event' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'Event' scope.", aStat.line)
		self.stack[-1].append(aStat)

	def LeaveEventScope(self, aStat):
		scope = self.stack.pop()
		signature = scope.pop(0)
		if scope:
			for statement in scope:
				# Validation of return statements.
				if isinstance(statement, SyntacticAnalysis.ReturnStatement):
					if statement.expression:
						raise SemanticError("Events cannot return a value.", statement.line)
			self.stack[-1].append(EventObject(signature, scope, aStat.line))
		else:
			self.stack[-1].append(EventObject(signature, None, aStat.line))
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
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			else:
				raise SemanticError("Illegal statement in the 'If' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'If' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			else:
				raise SemanticError("Illegal statement in the 'ElseIf' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'ElseIf' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
		elif isinstance(aStat, SyntacticAnalysis.EndIfStatement):
			self.currentScope.pop()
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
				self.currentScope.append(ScopeEnum.SWITCH)
			elif isinstance(aStat, SyntacticAnalysis.ForStatement):
				self.currentScope.append(ScopeEnum.FOR)
			elif isinstance(aStat, SyntacticAnalysis.ForEachStatement):
				self.currentScope.append(ScopeEnum.FOREACH)
			elif isinstance(aStat, SyntacticAnalysis.DoStatement):
				self.currentScope.append(ScopeEnum.DO)
			else:
				raise SemanticError("Illegal statement in the 'Else' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'Else' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
		elif isinstance(aStat, SyntacticAnalysis.EndWhileStatement):
			self.currentScope.pop()
		elif self.capricaExtensions:
			if isinstance(aStat, SyntacticAnalysis.SwitchStatement):
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
			else:
				raise SemanticError("Illegal statement in the 'While' scope.", aStat.line)
		else:
			raise SemanticError("Illegal statement in the 'While' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
		elif isinstance(aStat, SyntacticAnalysis.SwitchCaseStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.SwitchDefaultStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndSwitchStatement):
			self.currentScope.pop()
		else:
			raise SemanticError("Illegal statement in the 'Switch' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
		elif isinstance(aStat, SyntacticAnalysis.SwitchCaseStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.SwitchDefaultStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.BreakStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.ContinueStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndSwitchStatement):
			pass
		else:
			raise SemanticError("Illegal statement in the 'Switch case' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
			raise SemanticError("Illegal statement in the 'Switch default case' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
			raise SemanticError("Illegal statement in the 'Do' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
			raise SemanticError("Illegal statement in the 'For' scope.", aStat.line)
		self.stack[-1].append(aStat)

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
			raise SemanticError("Illegal statement in the 'ForEach' scope.", aStat.line)
		self.stack[-1].append(aStat)
	#End of Caprica extensions

# ==================== Property ====================
	def EnterPropertyScope(self, aStat):
		self.currentScope.append(ScopeEnum.PROPERTY)
		self.stack.append([aStat])
		if aStat.flags.isAuto or aStat.flags.isAutoReadOnly:
			self.pendingDocstring = self.LeavePropertyScope

	def PropertyScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.FunctionSignatureStatement):
			self.EnterFunctionScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndPropertyStatement):
			self.LeavePropertyScope(aStat)
			return
		else:
			raise SemanticError("Illegal statement in the property scope.", aStat.line)
		self.stack[-1].append(aStat)

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
				raise Exception("SublimePapyrus - Fallout 4 - Unsupported property element:", type(element))
		# Auto or AutoReadOnly property: signature + optional docstring
		if signature.flags.isAuto or signature.flags.isAutoReadOnly:
			self.stack[-1].append(PropertyObject(signature, docstring, setFunction, getFunction, signature.line))
		# Full property: signature + optional docstring + property body
		else:
			# Function validation (at least a Set or a Get function)
			if not setFunction and not getFunction:
				raise SemanticError("This property has to have at least a 'Set' or a 'Get' function.", signature.line)
			self.stack[-1].append(PropertyObject(signature, docstring, setFunction, getFunction, aStat.line))
		self.currentScope.pop()

# ==================== Struct ====================
	def EnterStructScope(self, aStat):
		self.currentScope.append(ScopeEnum.STRUCT)
		self.stack.append([aStat])

	def StructScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.VariableStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.EndStructStatement):
			self.LeaveStructScope(aStat)
			return
		else:
			raise SemanticError("Illegal statement in the struct scope.", aStat.line)
		self.stack[-1].append(aStat)

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
				if isinstance(scope[0], SyntacticAnalysis.VariableStatement):
					if memberStack:
						ReduceMember()
					memberStack.append(scope.pop(0))
				elif isinstance(scope[0], SyntacticAnalysis.DocstringStatement):
					if memberStack:
						memberStack.append(scope.pop(0))
					else:
						raise SemanticError("Illegal docstring in the struct scope.", scope[0].line)
				else:
					raise Exception("Unsupported type in LeaveStructScope: %s" % type(scope[0]))
			if memberStack:
				ReduceMember()
			if not members:
				raise SemanticError("This struct does not have any members.", signature.line)
			self.stack[-1].append(StructObject(signature, members, aStat.line))
		else:
			raise SemanticError("This struct does not have any members.", signature.line)
		self.currentScope.pop()

# ==================== Group ====================
	def EnterGroupScope(self, aStat):
		self.currentScope.append(ScopeEnum.GROUP)
		self.stack.append([aStat])

	def GroupScope(self, aStat):
		if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			pass
		elif isinstance(aStat, SyntacticAnalysis.PropertySignatureStatement):
			self.EnterPropertyScope(aStat)
			return
		elif isinstance(aStat, SyntacticAnalysis.EndGroupStatement):
			self.LeaveGroupScope(aStat)
			return
		else:
			raise SemanticError("Illegal statement in the group scope.", aStat.line)
		self.stack[-1].append(aStat)

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
				elif isinstance(element, PropertyObject):
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
	def ClosePendingDocstringScope(self, aStat):
		if aStat and isinstance(aStat, SyntacticAnalysis.DocstringStatement):
			self.stack[-1].append(aStat)
			self.pendingDocstring(aStat)
			self.pendingDocstring = None
			return False
		else:
			self.pendingDocstring(aStat)
			self.pendingDocstring = None
			return True

	def Assemble(self, aStat):
		#print("Current scope: %s" % ScopeDescription[self.currentScope[-1]])
		if self.pendingDocstring:
			continueAssembling = self.ClosePendingDocstringScope(aStat)
			if not continueAssembling:
				return
#			if isinstance(aStat, SyntacticAnalysis.DocstringStatement):
#				self.stack[-1].append(aStat)
#				self.pendingDocstring(aStat)
#				self.pendingDocstring = None
#				return
#			else:
#				self.pendingDocstring(aStat)
#				self.pendingDocstring = None
			#print("Dropping down to: %s" % ScopeDescription[self.currentScope[-1]])
		currentScope = self.currentScope[-1]
		if currentScope == -1:
			if isinstance(aStat, SyntacticAnalysis.ScriptSignatureStatement):
				self.EnterEmptyStateScope(aStat)
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
	def Build(self, aGetPath):
		"""Returns a Script"""
		if self.currentScope[-1] != ScopeEnum.SCRIPT and self.pendingDocstring:
			self.ClosePendingDocstringScope(None)
		self.LeaveEmptyStateScope(aGetPath)
		script = self.stack.pop()
		self.Reset(self.capricaExtensions)
		if isinstance(script, ScriptObject):
			return script
		else:
			raise Exception("SublimePapyrus - Fallout 4 - Failed to build script object.")

# ==================== Validation of pretty much everything except for expressions ====================
	def Validate(self, aScript, aCache, aGetPath, aSourceReader, aBuildScript):
		def ValidateScript(aScriptToProcess):
			lineage = []
			if aScriptToProcess.extends:
				lineage = [aCache.get(e) for e in aScriptToProcess.lineage]
			print("Validating: %s" % aScriptToProcess.identifier)
			# Imported scripts
			# TODO: Check that there are no attempts to import a script from this script's lineage.
			if aScriptToProcess.importedScripts:
				print("Processing imported %d scripts." % len(aScriptToProcess.importedScripts))
				for key, statement in aScriptToProcess.importedScripts.items():
					if not aCache.get(key, None):
						ProcessScript(statement.identifier, statement.line)
			# Update TypeMap
			# Do this immediately after imports and update all Type instances as they are encountered?
			print("Updating TypeMap.")
			for key, entry in aScriptToProcess.typeMap.items():
				namespace = [e.upper() for e in entry.identifier.namespace]
				name = entry.identifier.name.upper()
				candidates = {}
				if namespace: # <namespace1:..:namespaceN>:<name>
					# Script in /namespace1/../namespaceN/
					filePath, dirPath = aGetPath(entry.identifier)
					if filePath:
						candidates[1] = TypeMapEntry(entry.identifier, False)
					filePath = None
					dirPath = None
					# Script in /importednamespace/namespace1/../namespaceN/
					for importedNamespace in aScriptToProcess.importedNamespaces:
						ident = importedNamespace.identifier.namespace[:]
						ident.append(importedNamespace.identifier.name)
						ident.extend(entry.identifier.namespace)
						ident.append(entry.identifier.name)
						ident = SyntacticAnalysis.Identifier(ident)
						filePath, dirPath = aGetPath(ident)
						if filePath:
							if candidates[2]:
								raise SemanticError("'%s' is an ambiguous type that could refer to multiple scripts in multiple imported namespaces." % entry.identifier, 1)
							else:
								candidates[2] = TypeMapEntry(ident, False)
					# Struct in /namespace1/../namespaceN-1/namespaceN.psc
					ident = SyntacticAnalysis.Identifier(entry.identifier.namespace[:])
					filePath, dirPath = aGetPath(ident)
					if filePath:
						source = aSourceReader(filePath)
						if source:
							script = aBuildScript(script)
							if script:
								if script.struct:
									struct = script.structs.get(name, None)
									if struct:
										candidates[3] = TypeMapEntry(entry.identifier, True)
					filePath = None
					dirPath = None
					# Struct in /importednamespace/namespace1/../namespaceN-1/namespaceN.psc
					for importedNamespace in aScriptToProcess.importedNamespaces:
						ident = importedNamespace.identifier.namespace[:]
						ident.append(importedNamespace.identifier.name)
						ident.extend(entry.identifier.namespace)
						#ident.append(entry.identifier.name)
						ident = SyntacticAnalysis.Identifier(ident)
						filePath, dirPath = aGetPath(ident)
						if filePath:
							source = aSourceReader(filePath)
							if source:
								script = aBuildScript(source)
								if script:
									if script.structs:
										struct = script.structs.get(name, None)
										if struct:
											if candidates[3]:
												raise SemanticError("'%s' is an ambiguous type that could refer to multiple structs in multiple imported namespaces." % entry.identifier, 1)
											else:
												temp = ident.identifier.namespace
												temp.append(ident.identifier.name)
												temp.append(entry.identifier.name)
												ident = temp
												candidates[3] = TypeMapEntry(ident, True)
									# TODO: What if multiple namespaces have a corresponding script, but not all of them, or only one, has the struct we are looking for?
				else: # <name>
					# Script directly in an import path
					filePath, dirPath = aGetPath(entry.identifier)
					if filePath:
						candidates[1] = TypeMapEntry(entry.identifier, False)
					filePath = None
					dirPath = None
					# Struct in current or parent script
					struct = aScriptToProcess.structs.get(name, None)
					if struct:
						candidates[2] = TypeMapEntry(entry.identifier, True)
					elif lineage:
						for parent in lineage:
							if parent.structs:
								struct = parent.structs.get(name, None)
								if struct:
									candidates[2] = TypeMapEntry(entry.identifier, True)
									break
					struct = None
					# Struct in imported script
					for importedScript in aScriptToProcess.importedScripts:
						temp = importedScript.structs.get(name, None)
						if temp:
							if candidates[3]:
								raise SemanticError("'%s' is an ambiguous type that could refer to multiple struct definitions found in multiple imported scripts." % entry.identifier, 1)
							else:
								ident = importedScript.identifier[:].append(entry.identifier.name)
								candidates[3] = TypeMapEntry(SyntacticAnalysis.Identifier(ident), True)
					# Script in /importednamespace/
					for importedNamespace in aScriptToProcess.importedNamespaces:
						ident = importedNamespace.identifier.namespace[:]
						ident.append(importedNamespace.name)
						ident.append(entry.identifier.name)
						ident = SyntacticAnalysis.Identifier(ident)
						filePath, dirPath = aGetPath(ident)
						if filePath:
							if candidates[4]:
								raise SemanticError("'%s' is an ambiguous type that could refer to multiple scripts in multiple imported namespaces." % entry.identifier, 1)
							else:
								candidates[4] = TypeMapEntry(ident, False)
				numCandidates = len(candidates)
				if numCandidates > 1:
					raise SemanticError("'%s' is an ambiguous type that could refer to multiple scripts and/or structs." % entry.identifier, 0)
				elif numCandidates == 0:
					raise SemanticError("'%s' could not be resolved to any known scripts nor structs.", 0)
				else:
					for candidateKey, candidateEntry in candidates.items():
						aScriptToProcess.typeMap[key] = candidateEntry
				print(key, type(entry), str(entry.identifier))

			#TODO: Iterate through script and make all .type attributes use one of the Type instances in a small set of Type instances? (Reduce memory usage)

			return True # TODO: Remove this line and finish implementing the parts under this line.

			# Validate inherited objects
			print("Processing inherited objects.")
			if aScriptToProcess.extends:
				#parent = aCache.get(str(aScriptToProcess.extends).upper())
#				lineage = [aCache.get(e) for e in aScriptToProcess.lineage]
				# Functions
				if aScriptToProcess.functions:
					for key, func in aScriptToProcess.functions.items():
						overriding = False
						for parent in lineage: # Check for definition in any parent script. If found and not matching, then raise exception. If found and matching, then break out of loop.
							if parent.functions:
								parentFunc = parent.functions.get(key, None)
								if parentFunc:
									overriding = True
									# Return values should match (remember that imports may vary from script to script)
									if parentFunc.type:
										if func.type:
											if func.type.isArray != parentFunc.type.isArray:
												if parentFunc.type.isArray:
													raise SemanticError("Expected to return an array based on definition inherited from '%s'." % (parentFunc.identifier), func.starts)
												else:
													raise SemanticError("Expected to return a non-array value based on definition inherited from '%s'." % (parentFunc.identifier), func.starts)
											#TODO: Validate identifier and isStruct
										else:
											if parentFunc.type.isArray:
												raise SemanticError("Expected to return a(n) '%s' array based on definition inherited from '%s'." % (parentFunc.type.identifier, parentFunc.identifier), func.starts)
											else:
												raise SemanticError("Expected to return a(n) '%s' value based on definition inherited from '%s'." % (parentFunc.type.identifier, parentFunc.identifier), func.starts)
									else:
										if func.type:
											raise SemanticError("Expected no return value based on definition inherited from '%s'." % (parentFunc.identifier), func.starts)
										else:
											pass # Neither definition returns a value.
									# Parameter counts should match
									if parentFunc.parameters:
										parentParamCount = len(parentFunc.parameters)
										if func.parameters:
											paramCount = len(func.parameters)
											if paramCount != parentParamCount:
												raise SemanticError("Expected %d parameters based on definition inherited from '%s'." % (parentParamCount, parent.identifier), func.starts)
											# Parameter types and default values should match
											i = 0
											while i < paramCount:
												param = func.parameters[i]
												parentParam = parentFunc.parameters[i]
												#Type
												#Default value, have to be constant expressions
												if parentParam.defaultValue:
													if param.defaultValue:
														paramValue = ConstantNodeVisitorWrapper(param.defaultValue, func.starts)
														if not paramValue:
															raise SemanticError("PARAM DEFAULTVALUE IS NONE", func.starts) # TODO: Finalize message
														if param.type.identifier != paramValue.identifier:
															raise SemanticError("MISMATCHING PARAM TYPE AND DEFAULTVALUE TYPE", func.starts) # TODO: Finalize message
														if not paramValue.isConstant:
															raise SemanticError("Expected parameter '%s' to have default value with a constant expression." % (param.identifier),func.starts)
														parentParamValue = ConstantNodeVisitorWrapper(parentParam.defaultValue, func.starts)
														# No need to check internal consistency of parentParam as that has already been done. Just compare the overriding param to parentParam to make sure that they match.
														if paramValue.identifier != parentParamValue.identifier:
															if parentParamValue.isArray:
																pass
#																raise SemanticError("Expected parameter '%s' to be a(n) '%s' array based on definition inherited from '%s'." % (param.identifier, parentParam., func.starts)
															else:
																raise SemanticError("", func.starts)
														if paramValue.isArray != parentParamValue.isArray:
															raise SemanticError("", func.starts)
														if paramValue.value != parentParamValue.value:
															raise SemanticError("", func.starts)
													else:
														raise SemanticError("Expected parameter '%s' to have a default value based on definition inherited from '%s'." % (param.identifier, parent.identifier), func.starts)
												else:
													if param.defaultValue:
														raise SemanticError("Expected parameter '%s' to not have a default value based on definition inherited from '%s'." % (param.identifier, parent.identifier), func.starts)
													else:
														pass # Neither definition of this parameter has a default value.
												
#"identifier", # Identifier
#"isArray", # bool
#"isStruct", # bool
#"isConstant", # bool
#"value", # str
#"isObject" # bool
												i += 1
										else:
											raise SemanticError("Expected %d parameters based on definition inherited from '%s'." % (parentFunc.identifier), func.starts)
									else:
										if func.parameters:
											raise SemanticError("Expected no parameters.", func.starts)
										else:
											pass # Neither definition has parameters.
									
									break
						#Any remaining checks
						if not overriding:
							pass
				# Events
				if aScriptToProcess.events:
					for key, event in aScriptToProcess.events.items():
						overriding = False
						for parent in lineage:
							if parent.events:
								parentEvent = parent.events.get(key, None)
								if parentEvent:
									overriding = True
									break
									pass #TODO: Check that signatures match
									#	Parameters
									#		Amount
									#		Order
									#		Type
									#overriding = True #Signatures match
									#break #Signatures match
									#raise SemanticError()
						if not overriding and not aScriptToProcess.flags.isNative:
							raise SemanticError("New events can only be defined when the script signature has the 'Native' flag.", event.starts)
						#Any remaining checks
				# Structs
				if aScriptToProcess.structs:
					for key, struct in aScriptToProcess.structs.items():
						for parent in lineage: # If struct has not been defined in any parent scripts, then this loop should finish by itself without raising exceptions.
							if parent.structs:
								parentStruct = parent.structs.get(key, None)
								if parentStruct:
									raise SemanticError("A struct called '%s' has already been defined in '%s'." %(struct.identifier, parent.identifier), struct.starts)
			print("Finished validating: %s" % aScriptToProcess.identifier)
			return True

		# Build parent scripts recursively and update a script's lineage
		def ProcessScript(aIdentifier, aLine):
			print("Processing: %s" % aIdentifier)
			script = aCache.get(str(aIdentifier).upper(), None)
			if not script:
				try:
					filePath, dirPath = aGetPath(aIdentifier)
					if filePath and dirPath:
						raise SemanticError("'%s' matches both a script and a namespace." % aIdentifier, aLine)
					elif dirPath:
						raise SemanticError("'%s' only matches a namespace." % aIdentifier, aLine)
					elif not filePath:
						raise SemanticError("'%s' does not match a script." % aIdentifier, aLine)
					print("Reading: %s (%s)" % (aIdentifier, filePath))
					source = aSourceReader(filePath)
					if source:
						print("Building: %s" % aIdentifier)
						script = aBuildScript(source)
						print("Finished building: %s" % aIdentifier)
						if script.extends:
							parent = ProcessScript(script.extends, aLine)
							script.lineage.extend(parent.lineage)
							script.lineage.append(str(script.extends).upper())
							print("%s lineage:" % aIdentifier, script.lineage)
						ValidateScript(script)
						aCache[str(script.identifier).upper()] = script
					else:
						raise SemanticError("'%s' does not contain anything.", aLine)
					print("Finished processing: %s" % aIdentifier)
				except LexicalAnalysis.LexicalError as e:
					raise RemoteError("Error in '%s' on line %d, column %d: %s" % (aIdentifier, e.line, e.column, e.message), aLine)
				except SyntacticAnalysis.SyntacticError as e:
					raise RemoteError("Error in '%s' on line %d: %s" % (aIdentifier, e.line, e.message), aLine)
				except SemanticError as e:
					raise RemoteError("Error in '%s' on line %d: %s" % (aIdentifier, e.line, e.message), aLine)
				except RemoteError as e:
					raise RemoteError(e.message, aLine)
			return script

		if aScript.extends:
			parent = aCache.get(str(aScript.extends).upper(), None)
			if not parent:
				try:
					parent = ProcessScript(aScript.extends, aScript.starts)
				except LexicalAnalysis.LexicalError as e:
					raise RemoteError("Error in '%s' on line %d, column %d: %s" % (aScript.extends, e.line, e.column, e.message), aScript.starts)
				except SyntacticAnalysis.SyntacticError as e:
					raise RemoteError("Error in '%s' on line %d: %s" % (aScript.extends, e.line, e.message), aScript.starts)
				except SemanticError as e:
					raise RemoteError("Error in '%s' on line %d: %s" % (aScript.extends, e.line, e.message), aScript.starts)
				except RemoteError as e:
					raise RemoteError(e.message, aScript.starts)




			aScript.lineage.extend(parent.lineage)
			aScript.lineage.append(str(aScript.extends).upper())
			print("%s lineage:" % aScript.identifier, aScript.lineage)
		ValidateScript(aScript)
			# Validate inherited objects
		# Validate and update TypeMap
#		for key, entry in aScript.typeMap.items():
#			print(key, entry)

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