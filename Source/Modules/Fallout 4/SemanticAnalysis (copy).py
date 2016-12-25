import os

# PLATFORM_WINDOWS is used to determine how to look for scripts in the filesystem. Unix-based OSes often have case-sensitive filesystems.
PLATFORM_WINDOWS = os.name == "nt"

#3: Semantic analysis

class SemanticError(Exception):
	def __init__(self, aMessage, aLine):
	# aMessage: string
	# aLine: int
		self.message = aMessage
		self.line = aLine

class Script(object):
	__slots__ = ["name", "starts", "flags", "parent", "docstring", "imports", "customEvents", "variables", "properties",  "groups", "functions", "events", "states", "structs", "identifier", "parentIdentifier"]
	def __init__(self, aName, aStarts, aFlags, aParent, aDocstring, aImports, aCustomEvents, aVariables, aProperties, aGroups, aFunctions, aEvents, aStates, aStructs):
	# aName: List of string
	# aStarts: int
	# aFlags: List of TokenEnum
	# aParent: List of string
	# aDocstring: string
	# aImports: List of string
	# aCustomEvents: Dictionary of CustomEvent
	# aVariables: Dictionary of Variable
	# aProperties: Dictionary of Property
	# aGroups: Dictionary of Group
	# aFunctions: Dictionary of Function
	# aEvents: Dictionary of Event
	# aStates: Dictionary of State
	# aStructs: Dictionary of Struct
		self.name = [e.upper() for e in aName]
		self.identifier = aName
		self.starts = aStarts
		self.flags = aFlags
		commonParent = "SCRIPTOBJECT"
		if not aParent and not (len(self.name) == 1 and self.name[0] == commonParent):
			self.parent = [commonParent]
			self.parentIdentifier = ["ScriptObject"]
		elif aParent:
			self.parent = [e.upper() for e in aParent]
			self.parentIdentifier = aParent
		else:
			self.parent = None
			self.parentIdentifier = None
		self.docstring = aDocstring
		self.imports = aImports
		self.customEvents = aCustomEvents
		self.variables = aVariables
		self.properties = aProperties
		self.groups = aGroups
		self.functions = aFunctions
		self.events = aEvents
		self.states = aStates
		self.structs = aStructs

class Property(object):
	__slots__ = ["name", "flags", "type", "value", "docstring", "getFunction", "setFunction", "starts", "ends", "identifier"]
	def __init__(self, aName, aIdentifier, aFlags, aType, aValue, aDocstring, aGetFunction, aSetFunction, aStarts, aEnds):
	# aName: string
	# aIdentifier: string
	# aFlags: List of TokenEnum
	# aType: Type
	# aValue: Expression
	# aDocstring: string
	# aGetFunction: Function
	# aSetFunction: Function
	# aStarts: int
	# aEnd: int
		self.name = aName
		self.identifier = aIdentifier
		self.flags = aFlags
		self.type = aType
		self.value = aValue
		self.docstring = aDocstring
		self.getFunction = aGetFunction
		self.setFunction = aSetFunction
		self.starts = aStarts
		self.ends = aEnds

class Group(object):
	__slots__ = ["name", "flags", "properties", "starts", "ends", "identifier"]
	def __init__(self, aName, aIdentifier, aFlags, aProperties, aStarts, aEnds):
	# aName: string
	# aIdentifier: string
	# aFlags: List of TokenEnum
	# aProperties: Dictionary of Property
	# aStarts: int
	# aEnds: int
		self.name = aName
		self.identifier = aIdentifier
		self.flags = aFlags
		self.properties = aProperties
		self.starts = aStarts
		self.ends = aEnds

#
#		StructMember
#			.name
#				String
#			.flags (cannot be CONST)
#			.type
#				.namespace
#				.name (cannot be VAR nor another Struct)
#				.array (must always be false)
#			.value
#				ExpressionNode (has to be a constant)
#			
class StructMember(object):
	__slots__ = ["line", "name", "flags", "type", "value", "docstring", "identifier"]
	def __init__(self, aLine, aIdentifier, aName, aFlags, aType, aValue, aDocstring):
		self.line = aLine
		self.name = aName
		self.identifier = aIdentifier
		self.flags = aFlags
		self.type = aType
		self.value = aValue
		self.docstring = aDocstring

#
#		Struct
#			.members
#				Dict of StructMember
class Struct(object):
	__slots__ = ["name", "members", "starts", "ends", "identifier"]
	def __init__(self, aName, aIdentifier, aMembers, aStarts, aEnds):
		self.name = aName
		self.identifier = aIdentifier
		self.members = aMembers
		self.starts = aStarts
		self.ends = aEnds

	def __str__(self):
		members = {}
		if self.members:
			members = self.members
		return """
===== Object =====
Type: Struct
Name: %s
Members: %s
Starts: %d
Ends: %d
""" % (
		self.name,
		", ".join([m for m in members]),
		self.starts,
		self.ends
	)

#
#		Function
#			.name
#				String
#			.flags
#				List of KeywordEnum
#			.type
#				.namespace
#					List of Token
#				.name
#					Token
#				.array
#					Bool
#			.parameters
#				Dict of Parameter
#			.docstring
#				String
#			.body
#				List of Statement
#			.starts
#				Int
#			.ends
#				Int
class Function(object):
	__slots__ = ["name", "flags", "type", "parameters", "docstring", "body", "starts", "ends", "identifier"]
	def __init__(self, aName, aIdentifier, aFlags, aType, aParameters, aDocstring, aBody, aStarts, aEnds):
		self.name = aName
		self.identifier = aIdentifier
		self.flags = aFlags
		self.type = aType
		self.parameters = aParameters
		self.docstring = aDocstring
		self.body = aBody
		self.starts = aStarts
		self.ends = aEnds

#
#		Event
#			.name
#				String
#			.flags
#				List of KeywordEnum
#			.remote
#				.namespace
#				.name
#			.parameters
#				Dict of Parameter
#			.docstring
#				String
#			.body
#				List of Statement
#			.starts
#				Int
#			.ends
#				Int
class Event(object):
	__slots__ = ["name", "flags", "remote", "parameters", "docstring", "body", "starts", "ends", "identifier"]
	def __init__(self, aName, aIdentifier, aFlags, aRemote, aParameters, aDocstring, aBody, aStarts, aEnds):
		self.name = aName
		self.identifier = aIdentifier
		self.flags = aFlags
		self.remote = aRemote
		self.parameters = aParameters
		self.docstring = aDocstring
		self.body = aBody
		self.starts = aStarts
		self.ends = aEnds

#
#		State
#			.name
#				String
#			.auto
#				Bool
#			.functions
#				Dict of Function
#			.events
#				Dict of Event
class State(object):
	__slots__ = ["name", "auto", "functions", "events", "starts", "ends", "identifier"]
	def __init__(self, aName, aAuto, aFunctions, aEvents, aStarts, aEnds):
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.auto = aAuto
		self.functions = aFunctions
		self.events = aEvents
		self.starts = aStarts
		self.ends = aEnds

	def __str__(self):
		functions = {}
		if self.functions:
			functions = self.functions
		events = {}
		if self.events:
			events = self.events
		return """
===== Object =====
Type: State
Name: %s
Auto: %s
Functions: %s
Events: %s
Starts: %d
Ends: %d
""" % (
		self.name,
		self.auto,
		", ".join([f for f in functions]),
		", ".join([e for e in events]),
		self.starts,
		self.ends
	)


class Semantic(object):
	def __init__(self):
		# Scopes
		#	0 = Empty state
		#	1 = State
		#	2 = Function
		#	3 = Event
		#	4 = Property
		#	5 = Group
		#	6 = Struct
		#	7 = StructMember
		self.paths = None
		self.scriptExtension = ".psc"
		self.cache = {}
		self.scope = [0]
		self.definition = [[]]
		self.line = None
		self.script = None

	def Reset(self, aCaprica):
		pass

	def EmptyStateScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.CUSTOMEVENT:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.DOCSTRING:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.EVENTSIGNATURE:
			self.scope.append(3)
			self.definition.append([aStat])
		elif typ == StatementEnum.FUNCTIONSIGNATURE:
			self.scope.append(2)
			self.definition.append([aStat])
		elif typ == StatementEnum.GROUPSIGNATURE:
			self.scope.append(5)
			self.definition.append([aStat])
		elif typ == StatementEnum.IMPORT:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.PROPERTYSIGNATURE:
			self.scope.append(4)
			self.definition.append([aStat])
		elif typ == StatementEnum.SCRIPTSIGNATURE:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.STATESIGNATURE:
			self.scope.append(1)
			self.definition.append([aStat])
		elif typ == StatementEnum.STRUCTSIGNATURE:
			self.scope.append(6)
			self.definition.append([aStat])
		elif typ == StatementEnum.VARIABLE:
			self.definition[-1].append(aStat)
		else:
			if typ == StatementEnum.ENDEVENT:
				raise SemanticError("There is no open 'Event' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDFUNCTION:
				raise SemanticError("There is no open 'Function' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDGROUP:
				raise SemanticError("There is no open 'Group' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDPROPERTY:
				raise SemanticError("There is no open 'Property' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDSTATE:
				raise SemanticError("There is no open 'State' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDSTRUCT:
				raise SemanticError("There is no open 'Struct' scope to terminate.", aStat.line)
			else:
				raise SemanticError("Illegal statement in the empty state.", aStat.line)

	def StateScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.ENDSTATE:
			#self.scope.pop()
			self.EndStateScope(aStat.line)
		elif typ == StatementEnum.EVENTSIGNATURE:
			self.scope.append(3)
			self.definition.append([aStat])
		elif typ == StatementEnum.FUNCTIONSIGNATURE:
			self.scope.append(2)
			self.definition.append([aStat])
		else:
			signature = self.definition[-1][0]
			if typ == StatementEnum.ENDEVENT:
				raise SemanticError("There is no open 'Event' scope to terminate.", aStat.line)
			elif typ == StatementEnum.ENDFUNCTION:
				raise SemanticError("There is no open 'Function' scope to terminate.", aStat.line)
			else:
				raise SemanticError("Illegal statement in a state definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndStateScope(self, aEndLine):
		stateDef = self.definition.pop()
		signature = stateDef.pop(0)
		functions = None
		events = None
		for s in stateDef:
			name = s.name.upper()
			if type(s) is Function:
				if not functions:
					functions = {name: s}
				else:
					existing = functions.get(name, None)
					if existing:
						raise SemanticError("A function called '%s' has already been declared in the '%s' state on line %d." % (s.name, signature.name, existing.starts), s.starts)
					functions[name] = s
			elif type(s) is Event:
				if not events:
					events = {name: s}
				else:
					existing = events.get(name, None)
					if existing:
						raise SemanticError("A function called '%s' has already been declared in the '%s' state on line %d." % (s.name, signature.name, existing.starts), s.starts)
					events[name] = s
		self.definition[-1].append(State(signature.name, signature.auto, functions, events, signature.line, aEndLine))
		self.scope.pop()

	def FunctionEventScope(self, aStat):
		typ = aStat.statementType
		signature = self.definition[-1][0]
		if signature.flags and TokenEnum.kNATIVE in signature.flags:
			if typ == StatementEnum.DOCSTRING:
				self.definition[-1].append(aStat)
				self.EndFunctionEventScope(signature.line)
			else:
				self.EndFunctionEventScope(signature.line)
				currentScope = self.scope[-1]
				if currentScope == 0: # Empty state
					self.EmptyStateScope(aStat)
				elif currentScope == 1: # State
					self.StateScope(aStat)
				elif currentScope == 1: # Property
					self.PropertyScope(aStat)
		else:
			if typ == StatementEnum.ASSIGNMENT:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.DOCSTRING:
				if self.scope[-1] == 2 and self.definition[-1][-1].statementType != StatementEnum.FUNCTIONSIGNATURE:
					raise SemanticError("Docstrings may only follow immediately after the function signature in function definitions.", aStat.line)
				elif self.scope[-1] == 3 and self.definition[-1][-1].statementType != StatementEnum.EVENTSIGNATURE:
					raise SemanticError("Docstrings may only follow immediately after the event signature in event definitions.", aStat.line)
				else:
					self.definition[-1].append(aStat)
			elif typ == StatementEnum.ELSE:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.ELSEIF:
				self.definition[-1].append(aStat)
			elif self.scope[-1] == 2 and typ == StatementEnum.ENDFUNCTION:
				self.EndFunctionEventScope(aStat.line)
			elif self.scope[-1] == 3 and typ == StatementEnum.ENDEVENT:
				self.EndFunctionEventScope(aStat.line)
			elif typ == StatementEnum.ENDIF:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.ENDWHILE:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.EXPRESSION:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.IF:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.RETURN:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.VARIABLE:
				self.definition[-1].append(aStat)
			elif typ == StatementEnum.WHILE:
				self.definition[-1].append(aStat)
			else:
				if self.scope[-1] == 2:
					raise SemanticError("Illegal statement in a function definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)
				else:
					raise SemanticError("Illegal statement in an event definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndFunctionEventScope(self, aEndLine):
		functionEventDef = self.definition.pop()
		signature = functionEventDef.pop(0)
		docstring = None
		if functionEventDef and functionEventDef[0].statementType == StatementEnum.DOCSTRING:
			docstring = functionEventDef.pop(0)
		body = functionEventDef
		if signature.statementType == StatementEnum.FUNCTIONSIGNATURE:
			self.definition[-1].append(Function(signature.name, signature.identifier, signature.flags, signature.type, signature.parameters, docstring, body, signature.line, aEndLine))
		else:
			self.definition[-1].append(Event(signature.name, signature.identifier, signature.flags, signature.remote, signature.parameters, docstring, body, signature.line, aEndLine))
		self.scope.pop()

	def PropertyScope(self, aStat):
		typ = aStat.statementType
		signature = self.definition[-1][0]
		if signature.flags and (TokenEnum.kAUTO in signature.flags or TokenEnum.kAUTOREADONLY in signature.flags):
			if typ == StatementEnum.DOCSTRING:
				if len(self.definition[-1]) == 1:
					self.definition[-1].append(aStat)
				else:
					raise SemanticError("The '%s' property already has a docstring." % self.definition[-1][0].name, aStat.line)
			else:
				self.EndPropertyScope(False, None)
				currentScope = self.scope[-1]
				if currentScope == 0: # Empty state
					self.EmptyStateScope(aStat)
				elif currentScope == 5: # Group, only PropertySignatures are allowed
					self.GroupScope(aStat)
		else:
			if typ == StatementEnum.DOCSTRING:
				if len(self.definition[-1]) == 1:
					self.definition[-1].append(aStat)
				else:
					raise SemanticError("The '%s' property already has a docstring." % self.definition[-1][0].name, aStat.line)
			elif typ == StatementEnum.FUNCTIONSIGNATURE:
				name = aStat.name.upper()
				if name == "SET" or name == "GET":
					self.scope.append(2)
					self.definition.append([aStat])
				else:
					raise SemanticError("Property definitions may only contain GET and SET functions.", aStat.line)
			elif typ == StatementEnum.ENDPROPERTY:
				self.EndPropertyScope(True, aStat.line)
			else:
				raise SemanticError("Illegal statement in a property definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndPropertyScope(self, aFullProperty, aEndLine):
		propertyDefinition = self.definition.pop()
		signature = propertyDefinition.pop(0)
		docstring = None
		if propertyDefinition and isinstance(propertyDefinition[0], Statement) and propertyDefinition[0].statementType == StatementEnum.DOCSTRING:
			docstring = propertyDefinition.pop(0)
		setFunc = None
		getFunc = None
		for s in propertyDefinition:
			name = s.name.upper()
			if name == "SET":
				setFunc = s
			elif name == "GET":
				getFunc = s
			else:
				raise SemanticError("Only SET and GET functions are allowed in property definitions.", s.starts)
		if aFullProperty:
			if not setFunc and not getFunc:
				raise SemanticError("The '%s' property has to at least have a GET or a SET function." % signature.name, signature.line)
		if aFullProperty:
			self.definition[-1].append(Property(signature.name, signature.identifier, signature.flags, signature.type, signature.value, docstring, getFunc, setFunc, signature.line, aEndLine))
		else:
			self.definition[-1].append(Property(signature.name, signature.identifier, signature.flags, signature.type, signature.value, docstring, getFunc, setFunc, signature.line, signature.line))
		self.scope.pop()

	def GroupScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.DOCSTRING:
			if len(self.definition[-1]) == 1:
				self.definition[-1].append(aStat)
			else:
				raise SemanticError("The '%s' group already has a docstring." % self.definition[-1][0].name, aStat.line)
		elif typ == StatementEnum.ENDGROUP:
			self.EndGroupScope(aStat)
		elif typ == StatementEnum.PROPERTYSIGNATURE:
			self.scope.append(4)
			self.definition.append([aStat])
		else:
			signature = self.definition[-1][0]
			raise SemanticError("Illegal statement in a group definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndGroupScope(self, aStat):
		groupDefinition = self.definition.pop()
		signature = groupDefinition.pop(0)
		docstring = None
		if groupDefinition and isinstance(groupDefinition[0], Statement) and groupDefinition[0].statementType == StatementEnum.DOCSTRING:
			docstring = groupDefinition.pop(0)
		properties = None
		for s in groupDefinition:
			name = s.name.upper()
			if not properties:
				properties = {name: s}
			else:
				existing = properties.get(name, None)
				if existing:
					raise SemanticError("A property called '%s' has already been declared in the '%s' group on line %d." % (s.name, signature.name, existing.starts), s.starts)
				properties[name] = s
		if not properties:
			raise SemanticError("The '%s' group does not have any properties." % signature.name, signature.line)
		self.definition[-1].append(Group(signature.name, signature.identifier, signature.flags, properties, signature.line, aStat.line))
		self.scope.pop()

	def StructScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.DOCSTRING:
			previous = self.definition[-1][-1]
			if isinstance(previous, Statement) and previous.statementType != StatementEnum.VARIABLE:
				raise SemanticError("Docstrings may only follow immediately after member definitions in struct definitions.", aStat.line)
		elif typ == StatementEnum.ENDSTRUCT:
			self.EndStructScope(aStat)
		elif typ == StatementEnum.VARIABLE:
			if aStat.type.name[-1] == "VAR":
				raise SemanticError("Struct members cannot have VAR as their type.", aStat.line)
			if aStat.type.array:
				raise SemanticError("Struct members cannot be arrays.", aStat.line)
			self.scope.append(7)
			self.definition.append([aStat])
		else:
			signature = self.definition[-1][0]
			raise SemanticError("Illegal statement in a struct definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndStructScope(self, aStat):
		structDefinition = self.definition.pop()
		signature = structDefinition.pop(0)
		members = None
		for s in structDefinition:
			name = s.name.upper()
			if not members:
				members = {name: s}
			else:
				existing = members.get(name, None)
				if existing:
					raise SemanticError("A struct member called '%s' has already been declared in the '%s' struct on line %d." % (s.name, signature.name, existing.line), s.line)
				members[name] = s
		if not members:
			raise SemanticError("The '%s' struct does not have any members." % signature.name, signature.line)
		self.definition[-1].append(Struct(signature.name, signature.identifier, members, signature.line, aStat.line))
		self.scope.pop()

	def StructMemberScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.DOCSTRING:
			if len(self.definition[-1]) == 1:
				self.definition[-1].append(aStat)
			else:
				signature = self.definition[-1][0]
				raise SemanticError("A docstring has already been declared for the struct member called '%s' on line %d." % (signature.name, signature.line), aStat.line)
		else:
			self.EndStructMemberScope()
			self.StructScope(aStat)

	def EndStructMemberScope(self):
		structMemberDef = self.definition.pop()
		signature = structMemberDef.pop(0)
		docstring = None
		if structMemberDef:
			docstring = structMemberDef.pop(0)
		self.definition[-1].append(StructMember(signature.line, signature.name, signature.identifier, signature.flags, signature.type, signature.value, docstring))
		self.scope.pop()

	def AssembleScript(self, aStat):
		"""Checks the legality of a statement within a scope."""
		currentScope = self.scope[-1]
		if currentScope == 0: # Empty state
			self.EmptyStateScope(aStat)
		elif currentScope == 1: # State
			self.StateScope(aStat)
		elif currentScope == 2 or self.scope[-1] == 3: # Function or event
			self.FunctionEventScope(aStat)
		elif currentScope == 4: # Property
			self.PropertyScope(aStat)
		elif currentScope == 5: # Group
			self.GroupScope(aStat)
		elif currentScope == 6: # Struct
			self.StructScope(aStat)
		elif currentScope == 7: # Struct member
			self.StructMemberScope(aStat)

	def BuildScript(self):
		"""Checks for duplicate definitions and returns a Script object."""
		if len(self.scope) != 1 and self.scope[-1] != 0:
			line = self.definition[-1][0].line
			if self.scope[-1] == 1:
				raise SemanticError("Unterminated state definition.", line)
			elif self.scope[-1] == 2:
				signature = self.definition[-1][0]
				if signature.flags and TokenEnum.kNATIVE in signature.flags:
					self.EndFunctionEventScope(signature.line)
				else:
					raise SemanticError("Unterminated function definition.", line)
			elif self.scope[-1] == 3:
				signature = self.definition[-1][0]
				if signature.flags and TokenEnum.kNATIVE in signature.flags:
					self.EndFunctionEventScope(signature.line)
				else:
					raise SemanticError("Unterminated event definition.", line)
			elif self.scope[-1] == 4:
				signature = self.definition[-1][0]
				if signature.flags and (TokenEnum.kAUTO in signature.flags or TokenEnum.kAUTOREADONLY):
					self.EndPropertyScope(False, signature.line)
				else:
					raise SemanticError("Unterminated property definition.", line)
			elif self.scope[-1] == 5:
				raise SemanticError("Unterminated group definition.", line)
			elif self.scope[-1] == 6:
				raise SemanticError("Unterminated struct definition.", line)
		scriptDef = self.definition.pop()
		result = None
		if scriptDef:
			signature = scriptDef.pop(0)
			if signature.parent and ":".join(signature.name) == ":".join(signature.parent):
				raise SemanticError("A script cannot extend itself.", signature.line)
			docstring = None
			functions = {}
			events = {}
			variables = {}
			properties = {}
			structs = {}
			customEvents = {}
			imports = {}
			groups = {}
			states = {}
			if scriptDef and isinstance(scriptDef[0], Statement) and scriptDef[0].statementType == StatementEnum.DOCSTRING:
				docstring = scriptDef.pop(0)
			for obj in scriptDef:
				if isinstance(obj, Statement):
					if obj.statementType == StatementEnum.IMPORT:
						key = ":".join(obj.name)
						existing = imports.get(key, None)
						if existing:
							raise SemanticError("'%s' has already been imported on line %d." % (key, existing.line), obj.line)
						imports[key] = obj
					elif obj.statementType == StatementEnum.CUSTOMEVENT:
						key = obj.name.upper()
						existing = customEvents.get(key, None)
						if existing:
							raise SemanticError("A CustomEvent called '%s' has already been declared on line %d." % (obj.name, existing.line), obj.line)
						customEvents[key] = obj
					elif obj.statementType == StatementEnum.VARIABLE:
						key = obj.name.upper()
						existing = variables.get(key, None)
						if existing:
							raise SemanticError("A variable called '%s' has already been declared on line %d." % (obj.name, existing.line), obj.line)
						existing = properties.get(key, None)
						if existing:
							raise SemanticError("A property called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.line)
						variables[key] = obj
				else:
					objectType = type(obj)
					if objectType is Property:
						key = obj.name.upper()
						existing = properties.get(key, None)
						if existing:
							raise SemanticError("A property called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						existing = variables.get(key, None)
						if existing:
							raise SemanticError("A variable called '%s' has already been declared on line %d." % (obj.name, existing.line), obj.starts)
						properties[key] = obj
					elif objectType is Group:
						key = obj.name.upper()
						existing = groups.get(key, None)
						if existing:
							raise SemanticError("A group called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						groups[key] = obj
						for key, prop in obj.properties.items():
							existing = properties.get(key, None)
							if existing:
								raise SemanticError("A property called '%s' has already been declared on line %d." % (prop.name, existing.starts), prop.starts)
							existing = variables.get(key, None)
							if existing:
								raise SemanticError("A variable called '%s' has already been declared on line %d." % (prop.name, existing.line), prop.starts)
							properties[key] = prop
					elif objectType is Struct:
						key = obj.name.upper()
						existing = structs.get(key, None)
						if existing:
							raise SemanticError("A struct called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						structs[key] = obj
					elif objectType is Function:
						key = obj.name.upper()
						existing = functions.get(key, None)
						if existing:
							raise SemanticError("A function called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						existing = events.get(key, None)
						if existing:
							raise SemanticError("An event called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						functions[key] = obj
					elif objectType is Event:
						key = None
						if obj.remote:
							key = "%s.%s" % (":".join(obj.remote), obj.name.upper())
						else:
							key = obj.name.upper()
						existing = events.get(key, None)
						if existing:
							raise SemanticError("An event called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						existing = functions.get(key, None)
						if existing:
							raise SemanticError("A function called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						events[key] = obj
					elif objectType is State:
						key = obj.name.upper()
						existing = states.get(key, None)
						if existing:
							raise SemanticError("A state called '%s' has already been declared on line %d." % (obj.name, existing.starts), obj.starts)
						states[key] = obj
			result = Script(signature.name, signature.line, signature.flags, signature.parent, docstring, imports, customEvents, variables, properties, groups, functions, events, states, structs)
		self.scope = [0]
		self.definition = [[]]
		return result

	def ValidateScript(self, aScript):
		"""Validates a Script object when taking into account e.g. the contents of other scripts."""
		self.script = aScript
		self.functions = [{}] # List of dictionaries of Function
		self.events = [{}] # List of dictionaries of Event
		self.groups = [{}] # List of dictionaries of Group
		self.properties = [{}] # List of dictionaries of Property
		self.variables = [{}] # List of dictionaries of Variable
		self.structs = [{}] # List of dictionaries of Struct
		self.states = [{}] # List of dictionaries of State
		self.importedNamespaces = [] # List of list of strings
		self.importedScripts = {} # Dictionary of Script
		self.customEvents = [{}] # List of dictionaries of CustomEvent
		self.parentsToProcess = [] # List of list of string
		print("Starting to validate " + ":".join(aScript.name))
		if self.script.parent:
			parent = self.script.parent
			while parent:
				self.parentsToProcess.insert(0, parent)
				parent = parent.parent
			for parent in self.parentsToProcess:
				print("Merging resources from " + ":".join(parent.name))
				isNative = False
				if parent.flags:
					isNative = TokenEnum.kNATIVE in parent.flags
				# Properties - Cannot be overridden.
				if parent.properties:
					for name, obj in parent.properties.items():
						if self.properties[0].get(name, None):
							for otherParent in self.parentsToProcess:
								if otherParent.properties.get(name, None):
									raise SemanticError("A property called '%s' in '%s' has already been declared in '%s'." % (name, ":".join(parent.name), ":".join(otherParent.name)), self.script.starts)
						else:
							self.properties[0][name] = obj

				# Functions - Can be overridden.
				if parent.functions:
					for name, obj in parent.functions.items():
						if self.functions[0].get(name, None):
							pass # Overriding
						else:
							self.functions[0][name] = obj

				# Events - New events require the script to have the 'Native' keyword, otherwise the event has to be overriding an event declared in a parent script.
				if parent.events:
					for name, obj in parent.events.items():
						if self.events[0].get(name, None):
							pass # Overriding
						else:
							if isNative:
								self.events[0][name] = obj
							else:
								raise SemanticError("Attempt to declare a new event '%s' in '%s' without the 'Native' keyword in the script header." % (name, ":".join(parent.name)), self.script.starts)

				# Structs - Cannot be overridden.
				if parent.structs:
					for name, obj in parent.structs.items():
						if self.structs[0].get(name, None):
							for otherParent in self.parentsToProcess:
								if otherParent.structs.get(name, None):
									raise SemanticError("A struct called '%s' in '%s' has already been declared in '%s'." % (name, ":".join(parent.name), ":".join(otherParent.name)), self.script.starts)
						else:
							self.structs[0][name] = obj

				# CustomEvents - Cannot be overridden.
				if parent.customEvents:
					for name, obj in parent.customEvents.items():
						if self.customEvents[0].get(name, None):
							for otherParent in self.parentsToProcess:
								if otherParent.customEvents.get(name, None):
									raise SemanticError("A CustomEvent called '%s' in '%s' has already been declared in '%s'." % (name, ":".join(parent.name), ":".join(otherParent.name)), self.script.starts)
						else:
							self.customEvents[0][name] = obj

				# States - Merged with states inherited from parents, functions and events have to have been declared in the empty state of the current script or a parent script.
				if parent.states:
					for name, obj in parent.states.items():
						if not self.states[0].get(name, None):
							self.states[0][name] = obj

				# Groups - Merged with groups inherited from parents, inherited properties cannot be overridden.
				if parent.groups:
					for name, obj in parent.groups.items():
						if not self.groups[0].get(name, None):
							self.groups[0][name] = obj

		isNative = False
		if self.script.flags:
			isNative = TokenEnum.kNATIVE in self.script.flags

		self.properties.append({})
		if self.script.properties:
			for name, obj in self.script.properties.items():
				if self.properties[0].get(name, None):
					for parent in self.parentsToProcess:
						if parent.properties.get(name, None):
							raise SemanticError("A property called '%s' has already been declared in '%s'." % (name, ":".join(parent.name)), obj.starts)
				else:
					self.properties[1][name] = obj

		self.functions.append({}) # Check if duplicate declarations have been inherited and handle overrides appropriately, duplicate declarations in the same script have already been checked by this point
		if self.script.functions:
			for name, obj in self.script.functions.items():
				existingFunction = self.functions[0].get(name, None)
				if existingFunction:
					for parent in self.parentsToProcess:
						if parent.functions.get(name, None):
							# Check return type
							if existingFunction.type and obj.type:
								if existingFunction.type.array != obj.type.array or ":".join(existingFunction.type.name) != ":".join(obj.type.name):
									returnType = ":".join(existingFunction.type.name)
									if existingFunction.type.array:
										returnType = returnType + "[]"
									raise SemanticError("The function header inherited from '%s' requires that '%s' returns a(n) '%s' value." % (":".join(parent.name), name, returnType), obj.starts)
							elif existingFunction.type:
								returnType = ":".join(existingFunction.type.name)
								if existingFunction.type.array:
									returnType = returnType + "[]"
								raise SemanticError("The function header inherited from '%s' requires that '%s' returns a(n) '%s' value." % (":".join(parent.name), name, returnType), obj.starts)
							elif obj.type:
								raise SemanticError("The function header inherited from '%s' requires that '%s' does not return a value." % (":".join(parent.name), name), obj.starts)

							# Check parameter types and defaults
							if existingFunction.parameters and obj.parameters:
								if len(existingFunction.parameters) != len(obj.parameters):
									raise SemanticError("The function header inherited from '%s' requires that '%s' has %d parameters." % (":".join(parent.name), name, len(existingFunction.parameters)), obj.starts)
								else:
									i = 0
									paramCount = len(existingFunction.parameters)
									while i < paramCount:
										existingParam = existingFunction.parameters[i]
										overridingParam = obj.parameters[i]
										if existingParam.type.array != overridingParam.type.array:
											if existingParam.type.array:
												raise SemanticError("Expected the '%s' parameter to be an array." % (overridingParam.identifier), obj.starts)
											else:
												raise SemanticError("Expected the '%s' parameter to not be an array." % (overridingParam.identifier), obj.starts)
										elif ":".join(existingParam.type.name) != ":".join(overridingParam.type.name):
											raise SemanticError("Expected the '%s' parameter's type to be '%s'." % (overridingParam.identifier, ":".join(existingParam.type.identifier)), obj.starts)
										else:
											if existingParam.value and overridingParam.value:
												pass # TODO: Use the NodeVisitor to get the default value's type and actual value
											elif existingParam.value:
												raise SemanticError("Expected the '%s' parameter to have a default value." % (overridingParam.name), obj.starts)
											elif overridingParam.value:
												raise SemanticError("Expected the '%s' parameter to not have a default value." % (overridingParam.name), obj.starts)
										i += 1
							elif existingFunction.parameters:
								raise SemanticError("The function header inherited from '%s' requires that '%s' has %d parameters." % (":".join(parent.identifier), name, len(existingFunction.parameters)), obj.starts)
							elif obj.parameters:
								raise SemanticError("The function header inherited from '%s' requires that '%s' does not have any parameters." % (":".join(parent.identifier), name), obj.starts)
							break
				if self.events[0].get(name, None):
					for parent in self.parentsToProcess:
						if parent.events.get(name, None):
							raise SemanticError("An event called '%s' has been inherited from '%s'." % (name, ":".join(parent.identifier)), obj.starts)
				# TODO: Also check that the default values of parameters are actually literals (unary minus is allowed to precede ints and floats).
				self.functions[1][name] = obj

		self.events.append({}) # Check if duplicate declarations have been inherited and handle overrides appropriately, duplicate declarations in the same script have already been checked by this point
		if self.script.events:
			for name, obj in self.script.events.items():
				print("Looking for event", name, obj.name)
				if obj.remote: # Remote or CustomEvent
					remote = self.GetCachedScript(obj.remote, obj.starts)
					if remote.events.get(obj.name, None):
						print("Remote event", obj.name)
						remoteEvent = remote.events[obj.name]
						# First parameter: Type has to be the same as the script containing the Event declaration (already checked earlier)
						# Remaining parameters, if any: Same types as the parameters in the Event declaration
						if len(obj.parameters) == len(remoteEvent.parameters) + 1:
							i = 0
							while i < len(remoteEvent.parameters):
								if obj.parameters[i + 1].type.array != remoteEvent.parameters[i].type.array:
									if remoteEvent.parameters[i].type.array:
										raise SemanticError("Expected the parameter called '%s' to be an array." % (obj.parameters[i + 1].identifier), obj.starts)
									else:
										raise SemanticError("Expected the parameter called '%s' to not be an array." % (obj.parameters[i + 1].identifier), obj.starts)
								elif ":".join(obj.parameters[i + 1].type.name) != ":".join(remoteEvent.parameters[i].type.name):
									raise SemanticError("Expected the parameter called '%s' to have the type '%s'." % (obj.parameters[i + 1].identifier, ":".join(remoteEvent.parameters[i].type.identifier)), obj.starts)
								i += 1
						else:
							raise SemanticError("The event header in '%s' requires there to be %d parameters in addition to the sender parameter." % (":".join(remote.identifier), len(remoteEvent.parameters)), obj.starts)
						self.events[1][name] = obj
					elif remote.customEvents.get(obj.name, None):
						print("CustomEvent", obj.name)
						if len(obj.parameters) == 2:
						# First parameter: Type has to be the same as the script containing the CustomEvent declaration (already checked earlier)
						# Second, and final, parameter: Type is Var[]
							if obj.parameters[1].type.array and ":".join(obj.parameters[1].type.name) == "VAR":
								pass
							elif not obj.parameters[1].type.array:
								raise SemanticError("Expected the second parameter to be an array.", obj.starts)
							else:
								raise SemanticError("Expected the second parameter's type to be 'Var'.", obj.starts)
						else:
							raise SemanticError("Incorrect amount of parameters. Expected two parameters.", obj.starts)
						self.events[1][name] = obj
					else:
						raise SemanticError("No event or CustomEvent declaration exists for '%s' in '%s'." % (obj.name, ":".join(obj.remote)), obj.starts)
				else: # Regular event
					if self.events[0].get(name, None): # Overriding, check that the signature is the same
						for parent in self.parentsToProcess:
							if parent.events.get(name, None):
								event = parent.events[name]
								if obj.parameters and event.parameters and len(obj.parameters) == len(event.parameters):
									i = 0
									while i < len(event.parameters):
										if obj.parameters[i].type.array != event.parameters[i].type.array:
											if event.parameters[i].type.array:
												raise SemanticError("Expected the parameter called '%s' to be an array." % (obj.parameters[i].identifier), obj.starts)
											else:
												raise SemanticError("Expected the parameter called '%s' to not be an array." % (obj.parameters[i].identifier), obj.starts)
										elif ":".join(obj.parameters[i].type.name) != ":".join(event.parameters[i].type.name):
											raise SemanticError("Expected the parameter called '%s' to have the type '%s'." % (obj.parameters[i].identifier, ":".join(event.parameters[i].type.identifier)), obj.starts)
										i += 1
								else:
									if not event.parameters and obj.parameters:
										raise SemanticError("The event header inherited from '%s' requires that '%s' does not have any parameters." % (":".join(parent.identifier), name), obj.starts)
									elif event.parameters:
										raise SemanticError("The event header inherited from '%s' requires that '%s' has %d parameters." % (":".join(parent.identifier, name, len(event.parameters)), obj.starts))
								self.events[1][name] = obj
								break
					elif self.functions[0].get(name, None):
						for parent in self.parentsToProcess:
							raise SemanticError("A function called '%s' has been inherited from '%s'." % (name, ":".join(parent.identifier)), obj.starts)
					else:
						if isNative: # Script header has the 'Native' flag
							self.events[1][name] = obj
						else: # Illegal event declaration
							raise SemanticError("The ability to declare new events requires the script header to have the 'Native' flag.", obj.starts)

		self.structs.append({}) # Check if duplicate declarations have been inherited, duplicate declarations in the same script have already been checked by this point
		if self.script.structs:
			for name, obj in self.script.structs.items():
				if self.structs[0].get(name, None):
					for parent in self.parentsToProcess:
						if parent.structs.get(name, None):
							raise SemanticError("A struct called '%s' has already been declared in '%s'." % (name, ":".join(parent.name)), obj.starts)
				else:
					self.structs[1][name] = obj

		self.customEvents.append({}) # Check if duplicate declarations have been inherited, duplicate declarations in the same script have already been checked by this point
		if self.script.customEvents:
			for name, obj in self.script.customEvents.items():
				if self.customEvents[0].get(name, None):
					for parent in self.parentsToProcess:
						if parent.customEvents.get(name, None):
							raise SemanticError("A CustomEvent called '%s' has already been declared in '%s'." % (name, ":".join(parent.name)), obj.line)
				else:
					self.customEvents[1][name] = obj
		
		if self.script.states: # States are merged, duplicate declarations in the same script have already been checked by this point
			self.states.append(self.script.states)
		else:
			self.states.append({})

		if self.script.groups: # Groups are merged, duplicate declarations in the same script have already been checked by this point
			self.groups.append(self.script.groups)
		else:
			self.groups.append({})

		self.variables.append({}) # Check if variable names conflict with property names, duplicate declarations in the same script have already been checked by this point
		for name, obj in self.script.variables.items():
			if self.properties[0].get(name, None):
				for parent in self.parentsToProcess:
					if parent.properties.get(name, None):
						raise SemanticError("A property called '%s' has already been declared in '%s'." % (name, ":".join(parent.name)), obj.line)
			elif self.properties[1].get(name, None):
				raise SemanticError("A property called '%s' has already been declared in this script." % name, obj.line)
			else:
				self.variables[1][name] = obj

		print("\n========== Inherited ==========")
		print("Functions", list(self.functions[0]))
		print("Events", list(self.events[0]))
		print("Groups", list(self.groups[0]))
		print("Properties", list(self.properties[0]))
		print("Properties", list(self.variables[0]))
		print("Structs", list(self.structs[0]))
		print("States", list(self.states[0]))
		print("CustomEvents", list(self.customEvents[0]))
		print("\n\n========== Current script ==========")
		print("Functions", list(self.functions[1]))
		print("Events", list(self.events[1]))
		print("Groups", list(self.groups[1]))
		print("Properties", list(self.properties[1]))
		print("Properties", list(self.variables[1]))
		print("Structs", list(self.structs[1]))
		print("States", list(self.states[1]))
		print("CustomEvents", list(self.customEvents[1]))
		print("")

		# Imported scripts and namespaces
		for key, value in self.script.imports.items():
			isFile = False
			isDir = False
			for impPath in self.paths:
				path = "%s" % os.path.join(impPath, *(value.name))
				if os.path.isdir(path):
					self.importedNamespaces.append(os.path.join(*(value.name)))
					isDir = True
					break
				elif os.path.isfile(path + self.scriptExtension):
					result = self.GetCachedScript(value.name, value.line)
					self.importedScripts[key] = result
					isFile = True
					break
			if not isFile and not isDir:
				raise SemanticError("'%s' is neither a script nor a valid namespace." % key, value.line)
		print("Imported scripts", self.importedScripts)
		print("Imported namespaces", self.importedNamespaces)

		# Process statements inside of functions and events
		for name, obj in self.functions[1].items():
			self.FunctionValidator(obj)
		for name, obj in self.events[1].items():
			self.FunctionValidator(obj)
		for name, obj in self.properties[1].items():
			if obj.getFunction:
				self.FunctionValidator(obj.getFunction)
			if obj.setFunction:
				self.FunctionValidator(obj.setFunction)
		return

	def FunctionValidator(self, aFunction):
	# aFunction: Function
	# TODO: Implement a check that makes sure that functions that return a value actually have a return statement somewhere(?)
		self.line = aFunction.starts
		returnsValue = False
		isFunction = False
		if isinstance(aFunction, Function):
			print("\nFunction", aFunction.name, aFunction.type)
			if aFunction.type:
				returnsValue = True
			isFunction = True
		elif isinstance(aFunction, Event):
			print("\nEvent", aFunction.name)
		localScopes = []
		def AppendLocalScope(aStat):
			newType = aStat.statementType
			if len(localScopes) > 0:
				currentType = localScopes[-1].statementType
				if newType == StatementEnum.ELSEIF or newType == StatementEnum.ELSE:
					if not (currentType == StatementEnum.IF or currentType == StatementEnum.ELSEIF):
						if newType == StatementEnum.ELSEIF:
							raise SemanticError("Illegal declaration of an 'ElseIf' scope.", self.line)
						else:
							raise SemanticError("Illegal declaration of an 'Else' scope.", self.line)
					else:
						localScopes.pop()
						self.PopVariableScope()
			else:
				if newType == StatementEnum.ELSEIF:
					raise SemanticError("Illegal declaration of an 'ElseIf' scope.", self.line)
				elif newType == StatementEnum.ELSE:
					raise SemanticError("Illegal declaration of an 'Else' scope.", self.line)
			localScopes.append(aStat)
			self.PushVariableScope()

		def PopLocalScope(aStat):
			endType = aStat.statementType
			if len(localScopes) > 0:
				startType = localScopes[-1].statementType
				if startType == StatementEnum.WHILE and not endType == StatementEnum.ENDWHILE:
					raise SemanticError("Expected 'EndWhile'.", self.line)
				elif startType == StatementEnum.IF and not (endType == StatementEnum.ELSEIF or endType == StatementEnum.ELSE or endType == StatementEnum.ENDIF):
					raise SemanticError("Expected 'ElseIf', 'Else', or 'EndIf'.", self.line)
				elif startType == StatementEnum.ELSEIF and not (endType == StatementEnum.ELSEIF or endType == StatementEnum.ELSE or endType == StatementEnum.ENDIF):
					raise SemanticError("Expected 'ElseIf', 'Else', or 'EndIf'.", self.line)
				elif startType == StatementEnum.ELSE and not endType == StatementEnum.END:
					raise SemanticError("Expected 'EndIf'.", self.line)
				# TODO: Implement Caprica extensions
				localScopes.pop()
				self.PopVariableScope()
			else:
				if endType == StatementEnum.ENDIF:
					raise SemanticError("There is no open 'If', 'ElseIf', or 'Else' scope to terminate.", self.line)
				elif endType == StatementEnum.ENDWHILE:
					raise SemanticError("There is no open 'While' scope to terminate.", self.line)
				# TODO: Implement Caprica extensions

		# Function/event parameters
		self.PushVariableScope()
		if aFunction.parameters:
			for parameter in aFunction.parameters:
				self.AddVariableToScope(parameter)

		for statement in aFunction.body:
			self.line = statement.line
			print("\t", statement)
			# TODO: Arrange in the optimal order
			if statement.statementType == StatementEnum.ASSIGNMENT:
				# TODO: Implement
				print("Assignment, left side", self.NodeVisitor(statement.leftExpression))
				print("Assignment, right side", self.NodeVisitor(statement.rightExpression))
			elif statement.statementType == StatementEnum.ELSE:
				AppendLocalScope(statement)
			elif statement.statementType == StatementEnum.ELSEIF:
				AppendLocalScope(statement)
				print("ElseIf statement", self.NodeVisitor(statement.expression))
			elif statement.statementType == StatementEnum.ENDIF:
				PopLocalScope(statement)
			elif statement.statementType == StatementEnum.ENDWHILE:
				PopLocalScope(statement)
			elif statement.statementType == StatementEnum.EXPRESSION:
				#pass # TODO: Implement
				print("Expression statement", self.NodeVisitor(statement.expression))
			elif statement.statementType == StatementEnum.IF:
				AppendLocalScope(statement)
				print("If statement", self.NodeVisitor(statement.expression))
			elif statement.statementType == StatementEnum.RETURN:
				if statement.expression and returnsValue:
					value = self.NodeVisitor(statement.expression)
					print("Return statement", value) # TODO: Check that the expression returns the same type of value as the function is supposed to return
					if aFunction.type.array != value.type.array:
						if aFunction.type.array:
							raise SemanticError("Expected a(n) '%s' array to be returned." % (":".join(aFunction.type.identifier)), self.line)
						else:
							raise SemanticError("Expected a '%s' value to be returned." % (":".join(aFunction.type.identifier)), self.line)
					elif aFunction.type.struct != value.type.struct:
						if aFunction.type.struct:
							raise SemanticError("Expected a(n) '%s' struct to be returned." % (":".join(aFunction.type.identifier)), self.line)
						else:
							raise SemanticError("Expected a non-struct value to be returned.", self.line)
					elif ":".join(aFunction.type.name) != ":".join(value.type.name):
						if aFunction.type.array:
							raise SemanticError("Expected a(n) '%s' array to be returned." % (":".join(aFunction.type.identifier)), self.line)
						else:
							raise SemanticError("Expected a(n) '%s' value to be returned." % (":".join(aFunction.type.identifier)), self.line)
				elif statement.expression and not returnsValue:
					if isFunction:
						raise SemanticError("This function does not return a value.", statement.line)
					else:
						raise SemanticError("Events cannot return values.", statement.line)
				elif not statement.expression and returnsValue:
					raise SemanticError("This function has to return a(n) '%s' value." % (":".join(aFunction.type.identifier)), statement.line)
			elif statement.statementType == StatementEnum.VARIABLE:
				self.AddVariableToScope(statement)
				if statement.value:
					print("Variable declaration default value", self.NodeVisitor(statement.value))
					# TODO: Check if expression returns the same type as the variable.
			elif statement.statementType == StatementEnum.WHILE:
				AppendLocalScope(statement)
				print("While statement", self.NodeVisitor(statement.expression))
			else:
				raise SemanticError("This statement type is not yet supported: %s" % StatementDescription[statement.statementType], statement.line)
		if len(localScopes) > 0:
			scopeStart = localScopes.pop()
			if scopeStart.statementType == StatementEnum.IF:
				raise SemanticError("Unterminated 'If' scope.", scopeStart.line)
			elif scopeStart.statementType == StatementEnum.ELSEIF:
				raise SemanticError("Unterminated 'ElseIf' scope.", scopeStart.line)
			elif scopeStart.statementType == StatementEnum.ELSE:
				raise SemanticError("Unterminated 'Else' scope.", scopeStart.line)
			elif scopeStart.statementType == StatementEnum.WHILE:
				raise SemanticError("Unterminated 'While' scope.", scopeStart.line)
			# TODO: Implement Caprica extensions
			else:
				raise Exception("Unterminated unknown scope.")
		self.PopVariableScope()

	def AddVariableToScope(self, aStatement):
		for scope in reversed(self.variables): # Variable declared in current script
			var = scope.get(aStatement.name, None)
			if var:
				raise SemanticError("A variable called '%s' has already been declared on line %d." % (var.identifier, var.line), self.line)
		prop = self.properties[-1].get(aStatement.name, None) # Property declared in current script
		if prop:
			raise SemanticError("A property called '%s' has already been declared on line %d." % (prop.identifier, prop.line), self.line)
		prop = self.properties[0].get(aStatement.name, None) # Property declared in a parent script
		if prop:
			for parent in self.parentsToProcess:
				prop = parent.properties.get(aStatement.name, None)
				if prop:
					raise SemanticError("A property called '%s' has already been declared in '%s' on line %d." % (prop.identifier, ":".join(parent.identifier), prop.line), self.line)
		self.variables[-1][aStatement.name] = aStatement

	def PushVariableScope(self):
		self.variables.append({})

	def PopVariableScope(self):
		if len(self.variables) > 2:
			self.variables.pop()
		else:
			raise Exception("DEBUG: Attempting to pop the variable scope once too many.")

	def NodeVisitor(self, aNode, aExpected = None):
		print("aNode", aNode)
		print("aExpected", aExpected)
		result = None
		# Node
		# self.type
		if aNode.type == NodeEnum.ARRAYATOM:
			# aNode.child
			# aNode.expression
			if aNode.expression:
				childResult = self.NodeVisitor(aNode.child, aExpected)
				exprResult = self.NodeVisitor(aNode.expression, aExpected)
				if ":".join(exprResult.type.name) == "INT" and exprResult.object and not exprResult.type.array and not exprResult.type.struct:
					result = NodeResult(Type(childResult.type.identifier, False, childResult.type.struct), childResult.object)
				else:
					raise SemanticError("Array elements can only be accessed with expressions that evaluate to 'Int'.", self.line)
			else:
				result = childResult
		elif aNode.type == NodeEnum.ARRAYCREATION:
			# aNode.arrayType
			# aNode.size
			print("Array creation node", aNode.arrayType, aNode.size)
			# Check if aNode.arrayType is a script or a struct
			name = ":".join(aNode.arrayType).upper()
			if name == "BOOL":
				result = NodeResult(Type(["Bool"], True, False), True)
			elif name == "FLOAT":
				result = NodeResult(Type(["Float"], True, False), True)
			elif name == "INT":
				result = NodeResult(Type(["Int"], True, False), True)
			elif name == "STRING":
				result = NodeResult(Type(["String"], True, False), True)
			elif name == "VAR":
				result = NodeResult(Type(["Var"], True, False), True)
			else:
				if len(aNode.arrayType) == 1:
					pass
	#				for scope in reversed(self.structs):
	#					if scope.get(name, None):
	#						result = NodeResult(Type(aNode.arrayType, True, True), True)
	#						print("Array of local or inherited struct", aNode.arrayType)
	#						break
	#				if not result: # Check for script
	#					if self.GetCachedScript(aNode.arrayType, self.line):
	#						result = NodeResult(Type(aNode.arrayType, True, False), True)
	#						print("Array of script", aNode.arrayType)
	#				if not result: # Structs in imported scripts
	#					for name, script in self.importedScripts.items():
	#						struct = script.structs.get(name, None)
	#						if struct:
	#							result = NodeResult(Type(script.identifier[:].extend(struct.identifier), True, True), True)
	#							print("Array of struct from imported script")
	#							break
	#				if not result: # Scripts in imported namespaces
	#					for namespace in self.importedNamespaces:
	#						nameArray = namespace[:].extend(aNode.arrayType)
	#						print("Looking for imported namespace script", nameArray)
	#						script = self.GetCachedScript(nameArray, self.line)
	#						if script:
	#							result = NodeResult(Type(nameArray, True, False), True)
	#							print("Array of script from imported namespace")
	#							break
				else:
					pass
	#				try: # Script
	#					print("Script in a specific namespace", aNode.arrayType)
	#					script = self.GetCachedScript(aNode.arrayType, self.line)
	#					result = NodeResult(Type(aNode.arrayType, True, False), True)
	#				except MissingScript:
	#					print("Struct in another script", aNode.arrayType)
	#					try: # Struct in another script
	#						script = self.GetCachedScript(aNode.arrayType[0:-1], self.line)
	#						if script.structs.get(name, None):
	#							result = NodeResult(Type(aNode.arrayType, True, True), True)
	#						else:
	#							raise SemanticError("'%s' does not have a struct called '%s'." % (":".join(aNode.arrayType[0:-1]), aNode.arrayType[-1]), self.line)
	#					except MissingScript:
	#						pass
			if not result:
				raise SemanticError("'%s' is not a known type nor a struct." % (name), self.line)
		elif aNode.type == NodeEnum.ARRAYFUNCORID:
			# aNode.child
			# aNode.expression
			result = self.NodeVisitor(aNode.child, aExpected)
			if result and result.type.array and aNode.expression:
				exprResult = self.NodeVisitor(aNode.expression, aExpected)
				if ":".join(exprResult.type.name) != "INT":
					raise SemanticError("ARRAY EXPRESSION IS NOT INT", self.line) # TODO: Finalize error message
				elif exprResult.type.array:
					raise SemanticError("ARRAY EXPRESSION IS AN ARRAY", self.line) # TODO: Finalize error message
				result = NodeResult(Type(result.type.identifier, False, result.type.struct), True)
		elif aNode.type == NodeEnum.BINARYOPERATOR:
			# aNode.operator
			# aNode.leftOperand
			# aNode.rightOperand
			print("Binary operator", aNode.operator)
			leftResult = self.NodeVisitor(aNode.leftOperand, aExpected)
			print("leftResult", leftResult)
			if aNode.operator.type == TokenEnum.EQUAL or aNode.operator.type == TokenEnum.NOTEQUAL or aNode.operator.type == TokenEnum.GREATERTHAN or aNode.operator.type == TokenEnum.GREATERTHANOREQUAL or aNode.operator.type == TokenEnum.LESSTHAN or aNode.operator.type == TokenEnum.LESSTHANOREQUAL or aNode.operator.type == TokenEnum.NOT or aNode.operator.type == TokenEnum.OR or aNode.operator.type == TokenEnum.AND or aNode.operator.type == TokenEnum.kIS: # Logical operators
				rightResult = self.NodeVisitor(aNode.rightOperand, aExpected)
				print("rightResult", rightResult)
				result = NodeResult(Type(["Bool"], False, False), True)
			elif aNode.operator.type == TokenEnum.DOT: # Function, event, property, struct, struct member
				print("Dot operator")
				aExpected = leftResult
				rightResult = self.NodeVisitor(aNode.rightOperand, aExpected)
				print("rightResult", rightResult)
				result = rightResult
			elif aNode.operator.type == TokenEnum.ADDITION or aNode.operator.type == TokenEnum.SUBTRACTION or aNode.operator.type == TokenEnum.MULTIPLICATION or aNode.operator.type == TokenEnum.DIVISION or aNode.operator.type == TokenEnum.MODULUS: # Arithmetic operators
				rightResult = self.NodeVisitor(aNode.rightOperand, aExpected)
				print("rightResult", rightResult)
				# Check that the operand types support the operator
				if not leftResult.object:
					raise SemanticError("The left-hand side expression evaluates to a type instead of a value.", self.line)
				elif not rightResult.object:
					raise SemanticError("The right-hand side expression evaluates to a type instead of a value.", self.line)
				elif leftResult.type.array:
					raise SemanticError("The left-hand side expression evaluates to an array, which do not support arithmetic operators.", self.line)
				elif rightResult.type.array:
					raise SemanticError("The right-hand side expression evaluates to an array, which do not support arithmetic operators.", self.line)
				elif leftResult.type.struct:
					raise SemanticError("The left-hand side expression evaluates to a struct, which do not support arithmetic operators.", self.line)
				elif rightResult.type.struct:
					raise SemanticError("The right-hand side expression evaluates to a struct, which do not support arithmetic operators.", self.line)
				else:
					leftResultKey = ":".join(leftResult.type.name)
					rightResultKey = ":".join(rightResult.type.name)
					if leftResultKey == rightResultKey:
						result = rightResult
					else:
						if leftResultKey == "STRING":
							result = leftResult
						elif rightResultKey == "STRING":
							result = rightResult
						else:
							if self.CanAutoCast(leftResult, rightResult):
								result = rightResult
							elif self.CanAutoCast(rightResult, leftResult):
								result = leftResult
							else:
								raise SemanticError("'%s' cannot be auto-cast to '%s' nor vice versa." % (":".join(leftResult.type.identifier), ":".join(rightResult.type.identifier)), self.line)
					if result:
						resultKey = ":".join(result.type.name)
						if resultKey == "BOOL":
							pass
						elif resultKey == "FLOAT":
							if aNode.operator.type == TokenEnum.MODULUS:
								raise SemanticError("'Float' does not support the modulus operator.", self.line)
						elif resultKey == "INT":
							pass
						elif resultKey == "STRING":
							if aNode.operator.type != TokenEnum.ADDITION:
								raise SemanticError("The only arithmetic operator supported by 'String' is the addition operator.", self.line)
#						elif resultKey == "VAR":
#							raise SemanticError("'Var' does not support any arithmetic operators.", self.line)
						else:
							raise SemanticError("'%s' does not support any arithmetic operators." % (":".join(result.type.identifier)), self.line)
			elif aNode.operator.type == TokenEnum.ASSIGN or aNode.operator.type == TokenEnum.ASSIGNADDITION or aNode.operator.type == TokenEnum.ASSIGNSUBTRACTION or aNode.operator.type == TokenEnum.ASSIGNMULTIPLICATION or aNode.operator.type == TokenEnum.ASSIGNDIVISION or aNode.operator.type == TokenEnum.ASSIGNMODULUS: # Assignment operators
				rightResult = self.NodeVisitor(aNode.rightOperand, aExpected)
				print("rightResult", rightResult)
				# Check that the operand types match or can be auto-cast
				if leftResult.type.array != rightResult.type.array:
					if leftResult.type.array:
						raise SemanticError("The left-hand expression evaluates to an array, but the right-hand expression does not.", self.line)
					else:
						raise SemanticError("The left-hand expression does not evaluate to an array, but the right-hand expression does.", self.line)
				elif leftResult.type.struct != rightResult.type.struct:
					if leftResult.type.struct:
						raise SemanticError("The left-hand expression evaluates to a struct, but the right-hand expression does not.", self.line)
					else:
						raise SemanticError("The left-hand expression does not evaluate to a struct, but the right-hand expression does.", self.line)
				elif leftResult.object != rightResult.object:
					if leftResult.object:
						raise SemanticError("The left-hand expression evaluates to a value, but the right-hand expression evaluates to a type.", self.line)
					else:
						raise SemanticError("The left-hand expression evaluates to a type, but the right-hand expression evaluates to a value.", self.line)
				if ":".join(leftResult.type.name) == ":".join(rightResult.type.name) or self.CanAutoCast(rightResult, leftResult):
					result = leftResult
				else:
					raise SemanticError("'%s' cannot be auto-cast to '%s'." % (":".join(rightResult.type.identifier), ":".join(leftResult.type.identifier)), self.line)
			elif aNode.operator.type == TokenEnum.kAS: # Cast as right operand
				rightResult = self.NodeVisitor(aNode.rightOperand, aExpected)
				print("rightResult", rightResult)
				result = rightResult
				if result.object:
					raise SemanticError("'%s' is an object and not a type." % (":".join(result.type.identifier)), self.line)
				elif result.type.struct:
					raise SemanticError("'%s' is a struct." % (":".join(result.type.identifier)), self.line)
				elif result.type.array:
					raise SemanticError("", self.line)
				else:
					name = ":".join(result.type.name)
					if name == "BOOL":
						result = NodeResult(Type(["Bool"], False, False), True)
					elif name == "FlOAT":
						result = NodeResult(Type(["Float"], False, False), True)
					elif name == "INT":
						result = NodeResult(Type(["Int"], False, False), True)
					elif name == "STRING":
						result = NodeResult(Type(["String"], False, False), True)
					elif name == "VAR":
						result = NodeResult(Type(["Var"], False, False), True)
					elif not self.GetCachedScript(result.type.name):
						raise SemanticError("'%s' is not a type that exists." % (":".join(result.type.identifier)))
			# Check for valid use of operators with types
		elif aNode.type == NodeEnum.CONSTANT:
			# aNode.value
			if aNode.value.type == TokenEnum.kTRUE or aNode.value.type == TokenEnum.kFALSE:
				result = NodeResult(Type(["Bool"], False, False), True)
			elif aNode.value.type == TokenEnum.kNONE:
				result = NodeResult(Type(["None"], False, False), True)
			elif aNode.value.type == TokenEnum.FLOAT:
				result = NodeResult(Type(["Float"], False, False), True)
			elif aNode.value.type == TokenEnum.INT:
				result = NodeResult(Type(["Int"], False, False), True)
			elif aNode.value.type == TokenEnum.STRING:
				result = NodeResult(Type(["String"], False, False), True)
			else:
				raise SemanticError("Unknown literal type", aNode.value.line)
		elif aNode.type == NodeEnum.EXPRESSION:
			result = self.NodeVisitor(aNode.child, aExpected)
		elif aNode.type == NodeEnum.FUNCTIONCALL: # Return function's return type (type, array, struct, object)
			# aNode.name
			# aNode.identifier
			# aNode.arguments
			print("Function call node", aNode.name)
			print("Expected", aExpected)
			if aExpected:
				# TODO: Special cases for SELF and PARENT
				expectedKey = ":".join(aExpected.type.name)
				if expectedKey == "SELF":
					function = self.functions[-1].get(aNode.name, None)
					if function:
						pass # TODO: Implement
					else:
						event = self.events[-1].get(aNode.name, None)
						if event:
							pass # TODO: Implement
				elif expectedKey == "PARENT":
					function = self.functions[0].get(aNode.name, None)
					if function:
						pass # TODO: Implement
					else:
						event = self.events[0].get(aNode.name, None)
						if event:
							pass # TODO: Implement
				else:
					if aExpected.type.array:
						raise SemanticError("Cannot call function/event on an array.", self.line)
					elif aExpected.type.struct:
						raise SemanticError("Cannot call function/event on a struct.", self.line)
					if aExpected.object:
						pass # TODO: Implement
					else: # Referencing the script name directly, can only call global functions
						script = self.GetCachedScript(aExpected.type.identifier, self.line)
						if script:
							function = script.functions.get(aNode.name, None)
							if function:
								if TokenEnum.kGLOBAL in function.flags:
									# TODO: Validate arguments against the function's parameters
									if function.type:
										isStruct = function.type.struct
										# TODO: Figure out if function returns a struct
										result = NodeResult(Type(function.type.identifier, function.type.array, isStruct), True)
									else:
										result = NodeResult(Type(["None"], False, False), True)
								else:
									raise SemanticError("Can only call global functions when referencing a type by its name.", self.line)
							else:
								raise SemanticError("'%s' does not have a global function called '%s'." % (":".join(aExpected.type.identifier), aNode.identifier), self.line)
			else: # Local, inherited, or imported function
				for scope in reversed(self.functions): # Local or inherited function
					function = scope.get(aNode.name, None)
					if function:
						# TODO: Validate arguments against the function's parameters
						if function.type:
							isStruct = function.type.struct
							# TODO: Figure out if function returns a struct
							result = NodeResult(Type(function.type.identifier, function.type.array, isStruct), True)
						else:
							result = NodeResult(Type(["None"], False, False), True)
						break
				if not result:
					for scope in reversed(self.events):
						event = scope.get(aNode.name, None)
						if event:
							# TODO: Validate arguments agains the event's parameters
							result = NodeResult(Type(["None"], False, False), True)
							break
				if not result: # Imported function
					for script in self.importedScripts:
						function = script.functions.get(aNode.name, None)
						if function:
							if TokenEnum.kGLOBAL in function.flags:
								# TODO: Validate arguments against the function's parameters
								if function.type:
									isStruct = function.type.struct
									# TODO: Figure out if function returns a struct
									result = NodeResult(Type(function.type.identifier, function.type.array, isStruct), True)
								else:
									result = NodeResult(Type(["None"], False, False), True)
							break
				if not result:
					raise SemanticError("'%s' is not a function or event that exists in this scope." % aNode.identifier, self.line)
			#result = NodeResult(function.type, True)
		elif aNode.type == NodeEnum.FUNCTIONCALLARGUMENT:
			# aNode.name
			# aNode.identifier
			# aNode.expression
			print("Function call argument node", aNode.identifier)
		elif aNode.type == NodeEnum.IDENTIFIER:
			# aNode.name
			# aNode.identifier
			print("Identifier node", aNode.name)
			if not aExpected:
				if len(aNode.name) == 1:
					name = aNode.name[0]
					if name == "SELF":
						result = NodeResult(Type(["SELF"], False, False), True)
					elif name == "PARENT":
						if not self.script.parent:
							raise SemanticError("This script does not have a parent script.", self.line)
						result = NodeResult(Type([self.script.parent.name], False, False), True)
					else:
						for scope in reversed(self.variables):
							var = scope.get(name, None)
							if var:
								print("Found a variable with matching name")
								result = NodeResult(var.type, True)
								break
						if not result:
							for scope in reversed(self.properties):
								prop = scope.get(name, None)
								if prop:
									print("Found a property with matching name")
									result = NodeResult(prop.type, True)
									break
						if not result:
							script = self.GetCachedScript(aNode.identifier, self.line)
							if script:
								print("Found a script with matching name")
								result = NodeResult(Type(script.identifier, False, False), False)
						if not result:
							for namespace in self.importedNamespaces:
								script = self.GetCachedScript(namespace[:].extend(aNode.identifier), self.line)
								if script:
									print("Found a script with matching name in an imported namespace")
									result = NodeResult(Type(script.identifier, False, False), False)
						if not result:
							raise SemanticError("'%s' is not a variable that exists in this scope nor a type." % (":".join(aNode.identifier)), self.line)
				else:
					print("Identifier refers to another script")
			else:
				pass
			# Check if identifier exists (variable, property, struct member, etc.), use aExpected when needed
			
		elif aNode.type == NodeEnum.LENGTH:
			result = NodeResult(Type(["Int"], False, False), True)
		elif aNode.type == NodeEnum.STRUCTCREATION:
			# aNode.structType
#			print("Struct creation node", aNode.structType)
			# TODO: Check if aNode.structType conflicts with identifiers
			result = NodeResult(Type(aNode.structType, False, True), True)
		elif aNode.type == NodeEnum.UNARYOPERATOR:
			# aNode.operator
			# aNode.operand
			result = self.NodeVisitor(aNode.operand, aExpected)
			if aNode.operator.type == TokenEnum.NOT:
				result = NodeResult(Type(["Bool"], False, False), True)
			elif aNode.operator.type == TokenEnum.SUBTRACTION:
				if result.type.array:
					raise SemanticError("Arrays do not support the unary minus operator.", self.line)
				elif result.type.struct:
					raise SemanticError("Structs do not support the unary minus operator.", self.line)
				elif not result.object:
					raise SemanticError("Only values support the unary minus operator.", self.line)
				if len(result.type.name) == 1:
					if result.type.name[0] == "FLOAT":
						result = NodeResult(Type(["Float"], False, False), True)
					elif result.type.name[0] == "INT":
						result = NodeResult(Type(["Int"], False, False), True)
					else:
						raise SemanticError("Only 'Float' and 'Int' support the unary minus operator.", self.line)
			else:
				raise Exception("DEBUG: Unsupported unary operator.")
		else:
			raise Exception("DEBUG: Unsupported node type.")
		if not result:
			raise Exception("DEBUG: NodeVisitor returns None.")
		return result
		# NodeResult
		# aType: Type
		# aObject: bool

	def CanAutoCast(self, aFrom, aTo):
	# aFrom: NodeResult
	# aTo: NodeResult
		if not aFrom:
			raise Exception("DEBUG: CanAutoCast's aFrom parameter is None.")
		elif not aTo:
			raise Exception("DEBUG: CanAutoCast's aTo parameter is None.")
		if aTo.type.array:
			raise SemanticError("Cannot auto-cast to an array.", self.line)
		elif aTo.type.struct and toKey != "VAR":
			raise SemanticError("Cannot auto-cast to a struct.", self.line)
		elif not aTo.object:
			raise SemanticError("Cannot auto-cast to a type/non-value.", self.line)
		elif not aFrom.object:
			raise SemanticError("Cannot auto-cast from a type/non-value.", self.line)
		toKey = ":".join(aTo.type.name)
		if toKey == "BOOL": # Anything
			return True
		elif toKey == "FLOAT": # Int only
			if ":".join(aFrom.type.name) == "INT":
				return True
			else:
				return False
		elif toKey == "INT": # Nothing
			return False
		elif toKey == "STRING": # Anything
			return True
		elif toKey == "VAR": # Anything but arrays
			if aFrom.type.array:
				return False
			else:
				return True
		else: # From child objects
			print("Auto-cast object", aFrom.type.name, aTo.type.name)
			raise Exception("Auto-cast object") # TODO: Clean this up
			raise SemanticError("Auto-cast object", self.line)
			return False

	def GetCachedScript(self, aType, aLine):
		self.line = aLine
		key = ":".join(aType).upper()
		result = self.cache.get(key, None)
		if result:
			return result
		if PLATFORM_WINDOWS:
			for impPath in self.paths:
				path = "%s%s" % (os.path.join(impPath, *aType), self.scriptExtension)
				if os.path.isfile(path):
					try:
						result = self.CacheScript(path)
					except LexicalError as e:
						raise LexicalError("Lexical error in '%s' script." % key, self.line, 0)
					except SyntacticError as e:
						raise SyntacticError("Syntactic error in '%s' script." % key, self.line)
					#= self.cache.get(key, None)
					if result:
						return result
					else:
						break
		# Unix - Implemented to enable development of package on Unix-based OSes. Is a bit slow.
		else:
			fileName = (aType.pop()+self.scriptExtension).upper()
			for impPath in self.paths:
				subFolders = [f.upper() for f in aType]
				def getFolder(aRoot):
					if len(subFolders) > 0:
						for element in os.listdir(aRoot):
							if element.upper() == subFolders[0]:
								subFolders.pop(0)
								return getFolder(os.path.join(aRoot, element))
					else:
						for element in os.listdir(aRoot):
							if element.upper() == fileName:
								return os.path.join(aRoot, element)
				finalPath = getFolder(impPath)
				if finalPath:
					try:
						result = self.CacheScript(finalPath)
					except LexicalError as e:
						raise LexicalError("Lexical error in '%s' script." % key, self.line, 0)
					except SyntacticError as e:
						raise SyntacticError("Syntactic error in '%s' script." % key, self.line)
					if result:
						return result
					else:
						break
		# EndUnix
		raise MissingScript("Cannot find a script called '%s'." % key, self.line)

	def CacheScript(self, aPath):
		signature = None
		parent = None
		source = None
		with open(aPath, "r") as f:
			source = f.read()
		if not source:
			raise SemanticError("Failed to read source of %s." % aPath, self.line)
		tokens = []
		for token in self.lex.Process(source):
			tokenType = token.type
			if tokenType == TokenEnum.NEWLINE:
				if tokens:
					stat = self.syn.Process(tokens)
					if stat:
						self.AssembleScript(stat)
					tokens = []
			elif tokenType != TokenEnum.COMMENTLINE and tokenType != TokenEnum.COMMENTBLOCK:
				tokens.append(token)
		script = self.BuildScript()
		self.cache[":".join(script.name)] = script
		return script

	def GetContext(self, aScript, aLine):
		pass

	def Process(self, aLex, aSyn, aSource, aPaths):
		self.lex = aLex
		self.syn = aSyn
		self.scope = [0]
		self.definition = [[]]
		self.paths = aPaths
		self.line = None
		self.script = None
		tokens = []
		for token in aLex.Process(aSource):
			if token.type == TokenEnum.NEWLINE:
				if tokens:
					#stat = aSyn.Process(tokens)
					#if stat:
					#	self.AssembleScript(stat)
					print(tokens)
					tokens = []
			elif token.type != TokenEnum.COMMENTLINE and token.type != TokenEnum.COMMENTBLOCK:
				tokens.append(token)
		return None
		script = self.BuildScript()
		if script:
			if script.parent:
				script.parent = self.GetCachedScript(script.parent, script.starts)
				parent = script.parent
				while parent.parent:
					if isinstance(parent.parent, list):
						parent.parent = self.GetCachedScript(parent.parent, parent.starts)
					parent = parent.parent
			self.ValidateScript(script)
#			# Add to cache
#			self.cache[":".join(script.name)] = script
			print("Cached scripts", self.cache)
			return script
		return None

class NodeResult(object):
	__slots__ = ["type", "object"]
	def __init__(self, aType, aObject):
	# aType: Type
	# aObject: bool
		self.type = aType
		self.object = aObject

	def __str__(self):
		return """
===== NodeResult =====
Type name: %s
Type identifier: %s
Array: %s
Struct: %s
Object: %s
""" % (":".join(self.type.name), ":".join(self.type.identifier), self.type.array, self.type.struct, self.object)

class MissingScript(Exception):
	def __init__(self, aMessage, aLine):
	# aMessage: string
	# aLine: int
		self.message = aMessage
		self.line = aLine

# TODO: Replace ":".join(*) functions by overriding the __eq__ function in affected classes
#	class Type(object):
#		def __eq__(self, aOther):
#			if isinstance(other, Type):
#				# return True or False based on comparisons made here
#				return (self.nameJoined == other.nameJoined and self.array == other.array and self.struct == other.array)
#			return NotImplemented
# TODO: Implement Caprica extensions
# TODO: Investigate if Caprica extensions can be toggleable with minimal performance impact