import os

# It is faster to store Statement type as an attribute in a Statement object than it is to use the isinstance() function.
class StatementEnum(object):
	ASSIGNMENT = 0
	CUSTOMEVENT = 1
	DOCSTRING = 2
	ELSE = 3
	ELSEIF = 4
	ENDEVENT = 5
	ENDFUNCTION = 6
	ENDGROUP = 7
	ENDIF = 8
	ENDPROPERTY = 9
	ENDSTATE = 10
	ENDSTRUCT = 11
	ENDWHILE = 12
	EVENTSIGNATURE = 13
	EXPRESSION = 14
	FUNCTIONSIGNATURE = 15
	GROUPSIGNATURE = 16
	IF = 17
	IMPORT = 18
	PARAMETER = 19
	PROPERTYSIGNATURE = 20
	RETURN = 21
	SCRIPTSIGNATURE = 22
	STATESIGNATURE = 23
	STRUCTSIGNATURE = 24
	VARIABLE = 25
	WHILE = 26
	#Caprica extensions
	BREAK = 27
	CONTINUE = 28
	SWITCH = 29
	CASE = 30
	DEFAULT = 31
	ENDSWITCH = 32
	FOR = 33
	ENDFOR = 34
	FOREACH = 35
	ENDFOREACH = 36
	DO = 37
	LOOPWHILE = 38

StatementDescription = [
	"ASSIGNMENT",
	"CUSTOMEVENT",
	"DOCSTRING",
	"ELSE",
	"ELSEIF",
	"ENDEVENT",
	"ENDFUNCTION",
	"ENDGROUP",
	"ENDIF",
	"ENDPROPERTY",
	"ENDSTATE",
	"ENDSTRUCT",
	"ENDWHILE",
	"EVENTSIGNATURE",
	"EXPRESSION",
	"FUNCTIONSIGNATURE",
	"GROUPSIGNATURE",
	"IF",
	"IMPORT",
	"PARAMETER",
	"PROPERTYSIGNATURE",
	"RETURN",
	"SCRIPTSIGNATURE",
	"STATESIGNATURE",
	"STRUCTSIGNATURE",
	"VARIABLE",
	"WHILE",
	#Caprica extensions
	"BREAK",
	"CONTINUE",
	"SWITCH",
	"CASE",
	"DEFAULT",
	"ENDSWITCH",
	"FOR",
	"ENDFOR",
	"FOREACH",
	"ENDFOREACH",
	"DO",
	"LOOPWHILE"
]

class Statement(object):
	__slots__ = ["statementType", "line"]
	def __init__(self, aStatementType, aLine):
	# aStatementType: StatementEnum
	# aLine: int
		self.statementType = aStatementType
		self.line = aLine

class Keyword(Statement):
	__slots__ = []
	def __init__(self, aStat, aLine):
	# aStat: StatementEnum
	# aLine: int
		super(Keyword, self).__init__(aStat, aLine)

class KeywordExpression(Statement):
	__slots__ = ["expression"]
	def __init__(self, aStat, aLine, aExpression):
	# aStat: StatementEnum
	# aLine: int
	# aExpression: Expression
		super(KeywordExpression, self).__init__(aStat, aLine)
		self.expression = aExpression

class Type(object):
	__slots__ = ["name", "array", "struct", "identifier"]
	def __init__(self, aName, aArray, aStruct):
	# aName: List of string
	# aArray: bool
	# aStruct: bool
		self.name = [e.upper() for e in aName]
		self.identifier = aName
		self.array = aArray
		self.struct = aStruct

class Assignment(Statement):
	__slots__ = ["leftExpression", "rightExpression"]
	def __init__(self, aLine, aLeftExpression, aRightExpression):
	# aLine: int
	# aLeftExpression: Expression
	# aRightExpression: Expression
		super(Assignment, self).__init__(StatementEnum.ASSIGNMENT, aLine)
		self.leftExpression = aLeftExpression
		self.rightExpression = aRightExpression

	def __str__(self):
		return """
===== Statement =====
Type: Assignment
Line: %d
""" % (self.line)

class CustomEvent(Keyword):
	__slots__ = ["name", "identifier"]
	def __init__(self, aLine, aName):
	# aLine: int
	# aName: Token
		super(CustomEvent, self).__init__(StatementEnum.CUSTOMEVENT, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value

	def __str__(self):
		return """
===== Statement =====
Type: CustomEvent signature
Name: %s
Line: %d
""" % (
		self.name,
		self.line
	)

class Docstring(Statement):
	__slots__ = ["value"]
	def __init__(self, aLine, aValue):
	# aLine: int
	# aValue: Token
		super(Docstring, self).__init__(StatementEnum.DOCSTRING, aLine)
		self.value = aValue.value

	def __str__(self):
		return """
===== Statement =====
Type: Docstring
Value: %s
Line: %d
""" % (
		self.value,
		self.line
	)

class Else(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(Else, self).__init__(StatementEnum.ELSE, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: Else
Line: %d
""" % (self.line)

class EndGroup(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndGroup, self).__init__(StatementEnum.ENDGROUP, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndGroup
Line: %d
""" % (self.line)

class ElseIf(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
	# aLine: int
	# aExpression: Expression
		super(ElseIf, self).__init__(StatementEnum.ELSEIF, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: ElseIf
Line: %d
""" % (self.line)

class EndEvent(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndEvent, self).__init__(StatementEnum.ENDEVENT, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndEvent
Line: %d
""" % (self.line)

class EndFunction(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndFunction, self).__init__(StatementEnum.ENDFUNCTION, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndFunction
Line: %d
""" % (self.line)

class EndIf(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndIf, self).__init__(StatementEnum.ENDIF, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndIf
Line: %d
""" % (self.line)

class EndProperty(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndProperty, self).__init__(StatementEnum.ENDPROPERTY, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndProperty
Line: %d
""" % (self.line)

class EndState(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndState, self).__init__(StatementEnum.ENDSTATE, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndState
Line: %d
""" % (self.line)

class EndStruct(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndStruct, self).__init__(StatementEnum.ENDSTRUCT, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndStruct
Line: %d
""" % (self.line)

class EndWhile(Keyword):
	__slots__ = []
	def __init__(self, aLine):
	# aLine: int
		super(EndWhile, self).__init__(StatementEnum.ENDWHILE, aLine)

	def __str__(self):
		return """
===== Statement =====
Type: EndWhile
Line: %d
""" % (self.line)

class Expression(Statement):
	__slots__ = ["expression"]
	def __init__(self, aLine, aExpression):
	# aLine: int
	# aExpression: Expression
		super(Expression, self).__init__(StatementEnum.EXPRESSION, aLine)
		self.expression = aExpression

	def __str__(self):
		return """
===== Statement =====
Type: Expression
Line: %d
""" % (self.line)

class ParameterSignature(object):
	__slots__ = ["line", "name", "type", "value", "identifier"]
	def __init__(self, aLine, aName, aType, aValue):
	# aLine: int
	# aName: Token
	# aType: Type
	# aValue: Expression
		self.line = aLine
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.type = aType
		self.value = aValue

	def __str__(self):
		return """
===== Statement =====
Type: Parameter signature
Name: %s
Parameter type: %s
Array: %s
Line: %d
""" % (
		self.name,
		":".join([f for f in self.type.name]),
		self.type.array,
		self.line
	)

class FunctionSignature(Statement):
	__slots__ = ["name", "type", "flags", "parameters", "identifier"]
	def __init__(self, aLine, aName, aType, aFlags, aParameters):
	# aLine: int
	# aName: Token
	# aType: Type
	# aFlags: List of TokenEnum
	# aParameters: List of ParameterSignature
		super(FunctionSignature, self).__init__(StatementEnum.FUNCTIONSIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.type = aType
		self.flags = aFlags
		self.parameters = aParameters

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		parameterCount = 0
		if self.parameters:
			parameterCount = len(self.parameters)
		returnType = []
		if self.type:
			returnType = self.type.name
		array = False
		if self.type:
			array = self.type.array
		return """
===== Statement =====
Type: Function signature
Name: %s
Return type: %s
Array: %d
#Parameters: %d
Flags: %s
Line: %d
""" % (
		self.name,
		":".join([f for f in returnType]),
		array,
		parameterCount,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class GroupSignature(Statement):
	__slots__ = ["name", "flags", "identifier"]
	def __init__(self, aLine, aName, aFlags):
	# aLine: int
	# aName: Token
	# aFlags: List of TokenEnum
		super(GroupSignature, self).__init__(StatementEnum.GROUPSIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.flags = aFlags

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		return """
===== Statement =====
Type: Group signature
Name: %s
Flags: %s
Line: %d
""" % (
		self.name,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class EventSignature(Statement):
	__slots__ = ["remote", "name", "flags", "parameters", "identifier", "remoteIdentifier"]
	def __init__(self, aLine, aRemote, aName, aFlags, aParameters):
	# aLine: int
	# aRemote: List of string
	# aName: Token
	# aFlags: List of TokenEnum
	# aParameters = List of ParameterSignature
		super(EventSignature, self).__init__(StatementEnum.EVENTSIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.flags = aFlags
		self.parameters = aParameters
		if aRemote:
			self.remote = [e.upper() for e in aRemote]
		else:
			self.remote = None
		self.remoteIdentifier = aRemote

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		parameterCount = 0
		remote = []
		if self.remote:
			remote = self.remote
		if self.parameters:
			parameterCount = len(self.parameters)
		return """
===== Statement =====
Type: Event signature
Name: %s
Remote: %s
#Parameters: %d
Flags: %s
Line: %d
""" % (
		self.name,
		":".join([f for f in remote]),
		parameterCount,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class If(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
	# aLine: int
	# aExpression: Expression
		super(If, self).__init__(StatementEnum.IF, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: If
Line: %d
""" % (self.line)

class Import(Statement):
	__slots__ = ["name", "identifier"]
	def __init__(self, aLine, aName):
	# aLine: int
	# aName: List of string
		super(Import, self).__init__(StatementEnum.IMPORT, aLine)
		self.name = [e.upper() for e in aName]
		self.identifier = aName

	def __str__(self):
		return """
===== Statement =====
Type: Import
Name: %s
Line: %d
""" % (
		":".join([f for f in self.name]),
		self.line
	)

class PropertySignature(Statement):
	__slots__ = ["name", "type", "flags", "value", "identifier"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
	# aLine: int
	# aName: Token
	# aType: Type
	# aFlags: List of TokenEnum
	# aValue: Expression
		super(PropertySignature, self).__init__(StatementEnum.PROPERTYSIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.type = aType
		self.flags = aFlags
		self.value = aValue

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		return """
===== Statement =====
Type: Property signature
Name: %s
Property type: %s
Array: %s
Flags: %s
Line: %d
""" % (
		self.name,
		":".join([f for f in self.type.name]),
		self.type.array,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class Return(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
	# aLine: int
	# aExpression: Expression
		super(Return, self).__init__(StatementEnum.RETURN, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: Return
Expression: %s
Line: %d
""" % (
		self.expression != None,
		self.line
	)

class ScriptSignature(Statement):
	__slots__ = ["name", "identifier", "parent", "flags"]
	def __init__(self, aLine, aName, aParent, aFlags):
	# aLine: int
	# aName: List of string
	# aParent: List of string
	# aFlags: List of TokenEnum
		super(ScriptSignature, self).__init__(StatementEnum.SCRIPTSIGNATURE, aLine)
		self.name = [f.upper() for f in aName]
		self.identifier = aName
		self.parent = aParent
		self.flags = aFlags

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		return """
===== Statement =====
Type: Script signature
Name: %s
Parent: %s
Flags: %s
Line: %d
""" % (
		":".join([f for f in self.name]),
		":".join([f for f in self.parent]),
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class StateSignature(Statement):
	__slots__ = ["name", "auto", "identifier"]
	def __init__(self, aLine, aName, aAuto):
	# aLine: int
	# aName: Token
	# aAuto: bool
		super(StateSignature, self).__init__(StatementEnum.STATESIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.auto = aAuto

	def __str__(self):
		return """
===== Statement =====
Type: State signature
Name: %s
Auto: %s
Line: %d
""" % (
		self.name,
		self.auto,
		self.line
	)

class StructSignature(Statement):
	__slots__ = ["name", "auto", "identifier"]
	def __init__(self, aLine, aName):
	# aLine: int
	# aName: Token
		super(StructSignature, self).__init__(StatementEnum.STRUCTSIGNATURE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value

	def __str__(self):
		return """
===== Statement =====
Type: Struct signature
Name: %s
Line: %d
""" % (
		self.name,
		self.line
	)

class Variable(Statement):
	__slots__ = ["name", "type", "flags", "value", "identifier"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
	# aLine: int
	# aName: Token
	# aType: Type
	# aFlags: List of TokenEnum
	# aValue: Expression
		super(Variable, self).__init__(StatementEnum.VARIABLE, aLine)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.type = aType
		self.flags = aFlags
		self.value = aValue

	def __str__(self):
		flags = self.flags
		if not flags:
			flags = []
		return """
===== Statement =====
Type: Variable definition
Name: %s
Variable type: %s
Array: %s
Flags: %s
Line: %d
""" % (
		self.name,
		":".join([f for f in self.type.name]),
		self.type.array,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class While(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
	# aLine: int
	# aExpression: Expression
		super(While, self).__init__(StatementEnum.WHILE, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: While
Line: %d
""" % (self.line)

class SyntacticError(Exception):
	def __init__(self, aMessage, aLine):
	# aMessage: string
	# aLine: int
		self.message = aMessage
		self.line = aLine

class Syntactic(object):
	def __init__(self):
		self.stack = None

	def Reset(self, aCaprica):
		pass

	def Abort(self, aMessage):
	# aMessage: string
		if self.tokenIndex >= self.tokenCount and self.tokenCount > 0:
			self.tokenIndex -= 1
		raise SyntacticError(aMessage, self.tokens[self.tokenIndex].line)

	def Accept(self, aToken):
	# aToken: Token
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == aToken:
				self.tokenIndex += 1
				return True
		return False

	def Expect(self, aToken):
	# aToken: Token
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == aToken:
				self.tokenIndex += 1
				if self.tokenIndex - 1 < self.tokenCount:
					return self.tokens[self.tokenIndex - 1]
				else:
					return None
			self.Abort("Expected a %s symbol instead of a %s symbol." % (TokenDescription[aToken], TokenDescription[self.tokens[self.tokenIndex].type]))
		self.Abort("Expected a %s symbol but no tokens remain." % (TokenDescription[aToken]))

	def Peek(self, aN = 1):
	# aN: int
		i = self.tokenIndex + aN
		if i < self.tokenCount:
			return self.tokens[i]
		return None

	def PeekBackwards(self, aN = 1):
	# aN: int
		i = self.tokenIndex - aN
		if i >= 0:
			return self.tokens[i]
		return None

	def Consume(self):
		if self.tokenIndex < self.tokenCount:
			self.tokenIndex += 1
			return
		self.Abort("No tokens remain.")

	def AcceptFlags(self, aFlags):
	# aFlags: List of TokenEnum
		if aFlags:
			successfulFlags = []
			attempts = len(aFlags)
			while attempts > 0:
				i = 0
				flagCount = len(aFlags)
				while i < flagCount:
					if self.Accept(aFlags[i]):
						successfulFlags.append(aFlags.pop(i))
						break
					i += 1
				if attempts == len(aFlags):
					if successfulFlags:
						return successfulFlags
					else:
						return None
				attempts -= 1
			return successfulFlags
		return None

	def AcceptType(self, aBaseTypes):
	# aBaseTypes: bool
		result = None
		if self.Accept(TokenEnum.IDENTIFIER):
			result = [self.PeekBackwards().value]
			while self.Accept(TokenEnum.COLON):
				result.append(self.PeekBackwards().value)
			return result
		elif aBaseTypes and (self.Accept(TokenEnum.kBOOL) or self.Accept(TokenEnum.kFLOAT) or self.Accept(TokenEnum.kINT) or self.Accept(TokenEnum.kSTRING) or self.Accept(TokenEnum.kVAR)):
			result = [self.PeekBackwards().value]
			return result
		else:
			return None

	def ExpectType(self, aBaseTypes):
	# aBaseTypes: bool
		if self.Accept(TokenEnum.IDENTIFIER):
			result = [self.PeekBackwards().value]
			while self.Accept(TokenEnum.COLON):
				self.Expect(TokenEnum.IDENTIFIER)
				result.append(self.PeekBackwards().value)
			return result
		elif aBaseTypes and (self.Accept(TokenEnum.kBOOL) or self.Accept(TokenEnum.kFLOAT) or self.Accept(TokenEnum.kINT) or self.Accept(TokenEnum.kSTRING) or self.Accept(TokenEnum.kVAR)):
			return [self.PeekBackwards().value]
		else:
			raise SyntacticError("Expected a type identifier.", self.line)

	def Property(self, aType):
	# aType: Type
		self.Expect(TokenEnum.IDENTIFIER)
		name = self.PeekBackwards()
		value = None
		flags = None
		if self.Accept(TokenEnum.ASSIGN):
			if not self.Expression():
				self.Abort("Expected an expression.")
			value = self.Pop()
			flags = self.AcceptFlags([TokenEnum.kAUTOREADONLY, TokenEnum.kAUTO, TokenEnum.kCONST, TokenEnum.kMANDATORY, TokenEnum.kHIDDEN, TokenEnum.kCONDITIONAL])
			if TokenEnum.kAUTO in flags and TokenEnum.kAUTOREADONLY in flags:
				self.Abort("A property cannot have both the AUTO and the AUTOREADONLY flag.")
			if TokenEnum.kAUTO in flags:
				pass
			elif TokenEnum.kAUTOREADONLY in flags:
				pass
			else:
				self.Abort("Properties initialized with a value require either the AUTO or the AUTOREADONLY flag.")
		else:
			flags = self.AcceptFlags([TokenEnum.kAUTOREADONLY, TokenEnum.kAUTO, TokenEnum.kCONST, TokenEnum.kMANDATORY, TokenEnum.kHIDDEN, TokenEnum.kCONDITIONAL])
		if flags:
			if TokenEnum.kAUTO not in flags:
				if TokenEnum.kCONDITIONAL in flags:
					self.Abort("Only AUTO properties can have the CONDITIONAL flag.")
				elif TokenEnum.kCONST in flags:
					self.Abort("Only AUTO properties can have the CONST flag.")
		return PropertySignature(self.line, name, aType, flags, value)

	def FunctionParameters(self):
		parameters = []
		typ = self.ExpectType(True)
		array = False
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expect(TokenEnum.RIGHTBRACKET)
			array = True
		typ = Type(typ, array, False)
		name = self.Expect(TokenEnum.IDENTIFIER)
		value = None
		if self.Accept(TokenEnum.ASSIGN):
			value = self.ExpectExpression()
		parameters.append(ParameterSignature(self.line, name, typ, value))
		while self.Accept(TokenEnum.COMMA):
			typ = self.ExpectType(True)
			array = False
			if self.Accept(TokenEnum.LEFTBRACKET):
				self.Expect(TokenEnum.RIGHTBRACKET)
				array = True
			typ = Type(typ, array, False)
			name = self.Expect(TokenEnum.IDENTIFIER)
			value = None
			if self.Accept(TokenEnum.ASSIGN):
				value = self.ExpectExpression()
			parameters.append(ParameterSignature(self.line, name, typ, value))
		return parameters

	def EventParameters(self, aRemote):
	# aRemote: List of string
		parameters = []
		typ = self.ExpectType(True)
		array = False
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expect(TokenEnum.RIGHTBRACKET)
			array = True
		if aRemote:
			if array:
				self.Abort("The first parameter in a remote/custom event cannot be an array.")
			if ":".join(typ) != ":".join(aRemote):
				self.Abort("The first parameter in a remote/custom event has to have the same type as the script that emits the event.")
		typ = Type(typ, array, False)
		name = self.Expect(TokenEnum.IDENTIFIER)
		parameters.append(ParameterSignature(self.line, name, typ, None))
		while self.Accept(TokenEnum.COMMA):
			typ = self.ExpectType(True)
			array = False
			if self.Accept(TokenEnum.LEFTBRACKET):
				self.Expect(TokenEnum.RIGHTBRACKET)
				array = True
			typ = Type(typ, array, False)
			name = self.Expect(TokenEnum.IDENTIFIER)
			parameters.append(ParameterSignature(self.line, name, typ, None))
		return parameters

	def Function(self, aType):
	# aType: Type
		self.Expect(TokenEnum.IDENTIFIER)
		name = self.PeekBackwards()
		parameters = None
		nextToken = self.Peek()
		self.Expect(TokenEnum.LEFTPARENTHESIS)
		if nextToken and nextToken.type != TokenEnum.RIGHTPARENTHESIS:
			parameters = self.FunctionParameters()
		self.Expect(TokenEnum.RIGHTPARENTHESIS)
		return FunctionSignature(self.line, name, aType, self.AcceptFlags([TokenEnum.kNATIVE, TokenEnum.kGLOBAL, TokenEnum.kDEBUGONLY, TokenEnum.kBETAONLY]), parameters)

	def Shift(self, aItem = None):
	# aItem: Instance of a class that inherits from Node
		if aItem:
			self.stack.append(aItem)
		else:
			self.stack.append(self.PeekBackwards())

	def Pop(self):
		if len(self.stack) > 0:
			return self.stack.pop()
		else:
			return None

	def ReduceBinaryOperator(self):
		operand2 = self.Pop()
		operator = self.Pop()
		operand1 = self.Pop()
		self.Shift(BinaryOperatorNode(operator, operand1, operand2))

	def ReduceUnaryOperator(self):
		operand = self.Pop()
		operator = self.Pop()
		self.Shift(UnaryOperatorNode(operator, operand))

	def Expression(self):
		def Reduce():
			self.Shift(ExpressionNode(self.Pop()))

		self.AndExpression()
		while self.Accept(TokenEnum.OR):
			self.Shift()
			self.AndExpression()
			self.ReduceBinaryOperator()
		Reduce()
		return True

	def AndExpression(self):
		self.BoolExpression()
		while self.Accept(TokenEnum.AND):
			self.Shift()
			self.BoolExpression()
			self.ReduceBinaryOperator()
		return True

	def BoolExpression(self):
		self.AddExpression()
		while self.Accept(TokenEnum.EQUAL) or self.Accept(TokenEnum.NOTEQUAL) or self.Accept(TokenEnum.GREATERTHANOREQUAL) or self.Accept(TokenEnum.LESSTHANOREQUAL) or self.Accept(TokenEnum.GREATERTHAN) or self.Accept(TokenEnum.LESSTHAN):
			self.Shift()
			self.AddExpression()
			self.ReduceBinaryOperator()
		return True

	def AddExpression(self):
		self.MultExpression()
		while self.Accept(TokenEnum.ADDITION) or self.Accept(TokenEnum.SUBTRACTION):
			self.Shift()
			self.MultExpression()
			self.ReduceBinaryOperator()
		return True

	def MultExpression(self):
		self.UnaryExpression()
		while self.Accept(TokenEnum.MULTIPLICATION) or self.Accept(TokenEnum.DIVISION) or self.Accept(TokenEnum.MODULUS):
			self.Shift()
			self.UnaryExpression()
			self.ReduceBinaryOperator()
		return True

	def UnaryExpression(self):
		unaryOp = False
		if self.Accept(TokenEnum.SUBTRACTION) or self.Accept(TokenEnum.NOT):
			self.Shift()
			unaryOp = True
		self.CastAtom()
		if unaryOp:
			self.ReduceUnaryOperator()
		return True

	def CastAtom(self):
		self.DotAtom()
		if self.Accept(TokenEnum.kAS) or self.Accept(TokenEnum.kIS):
			self.Shift()
			nextToken = self.Peek()
			if nextToken and nextToken.type == TokenEnum.COLON:
				self.Shift(IdentifierNode(self.ExpectType(False)))
			else:
				if self.tokens[self.tokenIndex].type == TokenEnum.IDENTIFIER or self.tokens[self.tokenIndex].type == TokenEnum.kBOOL or self.tokens[self.tokenIndex].type == TokenEnum.kFLOAT or self.tokens[self.tokenIndex].type == TokenEnum.kINT or self.tokens[self.tokenIndex].type == TokenEnum.kSTRING or self.tokens[self.tokenIndex].type == TokenEnum.kVAR:
					self.Consume()
				else:
					self.Abort("Expected a type.")
				self.Shift(IdentifierNode(self.PeekBackwards()))
			self.ReduceBinaryOperator()
		return True

	def DotAtom(self):
		if self.Accept(TokenEnum.kFALSE) or self.Accept(TokenEnum.kTRUE) or self.Accept(TokenEnum.FLOAT) or self.Accept(TokenEnum.INT) or self.Accept(TokenEnum.STRING) or self.Accept(TokenEnum.kNONE):
			self.Shift(ConstantNode(self.PeekBackwards()))
			return True
		elif self.Accept(TokenEnum.SUBTRACTION) and (self.Accept(TokenEnum.INT) or self.Expect(TokenEnum.FLOAT)):
			self.Shift(ConstantNode(UnaryOperatorNode(self.PeekBackwards(2), self.PeekBackwards(1))))
			return True
		elif self.ArrayAtom():
			while self.Accept(TokenEnum.DOT):
				self.Shift()
				self.ArrayFuncOrId()
				self.ReduceBinaryOperator()
			return True

	def ArrayAtom(self):
		def Reduce():
			temp = self.Pop()
			self.Shift(ArrayAtomNode(self.Pop(), temp))

		self.Atom()
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expression()
			self.Expect(TokenEnum.RIGHTBRACKET)
			Reduce()
		return True

	def Atom(self):
		if self.Accept(TokenEnum.kNEW):
			typ = self.ExpectType(True)
			if self.Accept(TokenEnum.LEFTBRACKET):
				size = self.ExpectExpression()
				self.Expect(TokenEnum.RIGHTBRACKET)
				self.Shift(ArrayCreationNode(typ, size))
			else:
				self.Shift(StructCreationNode(typ))
				typ = ":".join(typ)
				typUpper = typ.upper()
				if typUpper == "BOOL" or typUpper == "FLOAT" or typUpper == "INT" or typUpper == "STRING" or typUpper == "VAR":
					raise SyntacticError("'%s' is a type, not a struct." % typ, self.line)
			return True
		elif self.Accept(TokenEnum.LEFTPARENTHESIS):
			self.Shift()
			self.Expression()
			self.Expect(TokenEnum.RIGHTPARENTHESIS)
			expr = self.Pop()
			self.Pop()
			self.Shift(expr)
			return True
		elif self.FuncOrId():
			return True

	def ArrayFuncOrId(self):
		def Reduce():
			temp = self.Pop()
			self.Shift(ArrayFuncOrIdNode(self.Pop(), temp))

		self.FuncOrId()
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expression()
			self.Expect(TokenEnum.RIGHTBRACKET)
			Reduce()
		return True

	def FuncOrId(self):
		nextToken = self.Peek()
		if nextToken and nextToken.type == TokenEnum.LEFTPARENTHESIS:
			self.FunctionCall()
			return True
		elif self.Accept(TokenEnum.kLENGTH):
			self.Shift(LengthNode())
			return True
		elif self.Accept(TokenEnum.IDENTIFIER) or self.Accept(TokenEnum.kSELF) or self.Accept(TokenEnum.kPARENT):
			self.Shift(IdentifierNode(self.PeekBackwards()))
			return True
		else:
			self.Abort("Expected a function call, and identifier, or the LENGTH keyword")

	def FunctionCall(self):
		def Reduce():
			arguments = []
			temp = self.Pop() # Right parenthesis
			temp = self.Pop()
			while temp.type == NodeEnum.FUNCTIONCALLARGUMENT:
				arguments.insert(0, temp)
				temp = self.Pop()
			self.Shift(FunctionCallNode(self.Pop(), arguments))

		def Argument():
			ident = None
			nextToken = self.Peek()
			if nextToken and nextToken.type == TokenEnum.ASSIGN:
				self.Expect(TokenEnum.IDENTIFIER)
				ident = self.PeekBackwards()
				self.Expect(TokenEnum.ASSIGN)
			self.Expression()
			expr = self.Pop()
			self.Shift(FunctionCallArgument(ident, expr))
			return True

		self.Expect(TokenEnum.IDENTIFIER)
		self.Shift()
		self.Expect(TokenEnum.LEFTPARENTHESIS)
		self.Shift()
		if self.Accept(TokenEnum.RIGHTPARENTHESIS):
			self.Shift()
			Reduce()
			return True
		else:
			Argument()
			while self.Accept(TokenEnum.COMMA):
				Argument()
			self.Expect(TokenEnum.RIGHTPARENTHESIS)
			self.Shift()
			Reduce()
			return True

	def ExpressionOrAssignment(self):
		self.Expression()
		left = self.Pop()
		if self.Accept(TokenEnum.ASSIGN) or self.Accept(TokenEnum.ASSIGNADDITION) or self.Accept(TokenEnum.ASSIGNSUBTRACTION) or self.Accept(TokenEnum.ASSIGNMULTIPLICATION) or self.Accept(TokenEnum.ASSIGNDIVISION) or self.Accept(TokenEnum.ASSIGNMODULUS):
			operator = self.PeekBackwards()
			self.Expression()
			right = self.Pop()
			return Assignment(self.line, left, right)
		elif self.tokenIndex >= self.tokenCount or self.tokens[self.tokenIndex] == None:
			return Expression(self.line, left)

	def Variable(self, aType):
	# aType: Type
		self.Expect(TokenEnum.IDENTIFIER)
		name = self.PeekBackwards()
		value = None
		if self.Accept(TokenEnum.ASSIGN):
			self.Expression()
			value = self.Pop()
		return Variable(self.line, name, aType, self.AcceptFlags([TokenEnum.kCONDITIONAL, TokenEnum.kCONST, TokenEnum.kHIDDEN]), value)

	def ExpectExpression(self):
		if not self.Expression():
			self.Abort("Expected an expression")
		return self.Pop()

	def Process(self, aTokens):
	# aTokens: List of Token
		if not aTokens:
			return
		
		result = None
		self.tokens = aTokens
		self.tokenIndex = 0
		self.tokenCount = len(self.tokens)
		self.line = self.tokens[self.tokenIndex].line
		self.stack = []

		tokenType = self.tokens[0].type
		if tokenType == TokenEnum.kBOOL or tokenType == TokenEnum.kFLOAT or tokenType == TokenEnum.kINT or tokenType == TokenEnum.kSTRING or tokenType == TokenEnum.kVAR:
			self.Consume()
			typ = self.PeekBackwards()
			array = False
			if self.Accept(TokenEnum.LEFTBRACKET):
				self.Expect(TokenEnum.RIGHTBRACKET)
				array = True
			typ = Type([typ.value], array, False)
			if self.Accept(TokenEnum.kPROPERTY):
				result = self.Property(typ)
			elif self.Accept(TokenEnum.kFUNCTION):
				result = self.Function(typ)
			else:
				result = self.Variable(typ)
		elif tokenType == TokenEnum.IDENTIFIER:
			typ = None
			nextToken = self.Peek()
			if nextToken:
				if nextToken.type == TokenEnum.COLON:
					typ = self.ExpectType(False)
					if typ:
						array = False
						if self.Accept(TokenEnum.LEFTBRACKET):
							self.Expect(TokenEnum.RIGHTBRACKET)
							array = True
						typ = Type(typ, array, False)
						if self.Accept(TokenEnum.kPROPERTY):
							result = self.Property(typ)
						elif self.Accept(TokenEnum.kFUNCTION):
							result = self.Function(typ)
						else:
							result = self.Variable(typ)
				elif nextToken.type == TokenEnum.LEFTBRACKET:
					nextToken = self.Peek(2)
					if nextToken:
						if nextToken.type == TokenEnum.RIGHTBRACKET:
							typ = Type([self.Expect(TokenEnum.IDENTIFIER).value], True, False)
							self.Consume()
							nextToken = self.Peek()
							self.Consume()
							if nextToken:
								if nextToken.type == TokenEnum.kFUNCTION:
									self.Consume()
									result = self.Function(typ)
								elif nextToken.type == TokenEnum.kPROPERTY:
									self.Consume()
									result = self.Property(typ)
								elif nextToken.type == TokenEnum.IDENTIFIER:
									result = self.Variable(typ)
						else:
							result = self.ExpressionOrAssignment()
				elif nextToken.type == TokenEnum.kPROPERTY:
					typ = Type([self.Expect(TokenEnum.IDENTIFIER).value], False, False)
					self.Consume()
					result = self.Property(typ)
				elif nextToken.type == TokenEnum.kFUNCTION:
					typ = Type([self.Expect(TokenEnum.IDENTIFIER).value], False, False)
					self.Consume()
					result = self.Function(typ)
				elif nextToken.type == TokenEnum.IDENTIFIER:
					result = self.Variable(Type([self.Expect(TokenEnum.IDENTIFIER).value], False, False))
				else:
					result = self.ExpressionOrAssignment()
			else:
				result = self.ExpressionOrAssignment()
		elif tokenType == TokenEnum.kIF:
			self.Consume()
			result = If(self.line, self.ExpectExpression())
		elif tokenType == TokenEnum.kELSE:
			self.Consume()
			result = Else(self.line)
		elif tokenType == TokenEnum.kELSEIF:
			self.Consume()
			result = ElseIf(self.line, self.ExpectExpression())
		elif tokenType == TokenEnum.kENDIF:
			self.Consume()
			result = EndIf(self.line)
		elif tokenType == TokenEnum.kWHILE:
			self.Consume()
			result = While(self.line, self.ExpectExpression())
		elif tokenType == TokenEnum.kENDWHILE:
			self.Consume()
			result = EndWhile(self.line)
		elif tokenType == TokenEnum.kRETURN:
			self.Consume()
			if self.tokenIndex < self.tokenCount:
				result = Return(self.line, self.ExpectExpression())
			else:
				result = Return(self.line, None)
		elif tokenType == TokenEnum.kFUNCTION:
			self.Consume()
			result = self.Function(None)
		elif tokenType == TokenEnum.kENDFUNCTION:
			self.Consume()
			result = EndFunction(self.line)
		elif tokenType == TokenEnum.kEVENT:
			self.Consume()
			nextToken = self.Peek()
			remote = None
			if nextToken and (nextToken.type == TokenEnum.DOT or nextToken.type == TokenEnum.COLON):
				remote = self.ExpectType(False)
				self.Expect(TokenEnum.DOT)
			name = self.Expect(TokenEnum.IDENTIFIER)
			nextToken = self.Peek()
			self.Expect(TokenEnum.LEFTPARENTHESIS)
			parameters = None
			if nextToken and nextToken.type != TokenEnum.RIGHTPARENTHESIS:
				parameters = self.EventParameters(remote)
			if remote and not parameters:
				self.Abort("Remote events and CustomEvents have to have a parameter defining the script that emits the event.")
			self.Expect(TokenEnum.RIGHTPARENTHESIS)
			result = EventSignature(self.line, remote, name, self.AcceptFlags([TokenEnum.kNATIVE]), parameters)
		elif tokenType == TokenEnum.kENDEVENT:
			self.Consume()
			result = EndEvent(self.line)
		elif tokenType == TokenEnum.kENDPROPERTY:
			self.Consume()
			result = EndProperty(self.line)
		elif tokenType == TokenEnum.kCUSTOMEVENT:
			self.Consume()
			result = CustomEvent(self.line, self.Expect(TokenEnum.IDENTIFIER))
		elif tokenType == TokenEnum.kGROUP:
			self.Consume()
			name = self.Expect(TokenEnum.IDENTIFIER)
			result = GroupSignature(self.line, name, self.AcceptFlags([TokenEnum.kCOLLAPSED, TokenEnum.kCOLLAPSEDONBASE, TokenEnum.kCOLLAPSEDONREF]))
		elif tokenType == TokenEnum.kENDGROUP:
			self.Consume()
			result = EndGroup(self.line)
		elif tokenType == TokenEnum.kSTRUCT:
			self.Consume()
			result = StructSignature(self.line, self.Expect(TokenEnum.IDENTIFIER))
		elif tokenType == TokenEnum.kENDSTRUCT:
			self.Consume()
			result = EndStruct(self.line)
		elif tokenType == TokenEnum.kSTATE:
			self.Consume()
			result = StateSignature(self.line, self.Expect(TokenEnum.IDENTIFIER), False)
		elif tokenType == TokenEnum.kAUTO:
			self.Consume()
			self.Expect(TokenEnum.kSTATE)
			result = StateSignature(self.line, self.Expect(TokenEnum.IDENTIFIER), True)
		elif tokenType == TokenEnum.kENDSTATE:
			self.Consume()
			result = EndState(self.line)
		elif tokenType == TokenEnum.kIMPORT:
			self.Consume()
			result = Import(self.line, self.ExpectType(False))
		elif tokenType == TokenEnum.kSCRIPTNAME:
			self.Consume()
			name = self.ExpectType(False)
			parent = None
			if self.Accept(TokenEnum.kEXTENDS):
				parent = self.ExpectType(False)
			flags = self.AcceptFlags([TokenEnum.kHIDDEN, TokenEnum.kCONDITIONAL, TokenEnum.kNATIVE, TokenEnum.kCONST, TokenEnum.kDEBUGONLY, TokenEnum.kBETAONLY, TokenEnum.kDEFAULT])
			result = ScriptSignature(self.line, name, parent, flags)
		elif tokenType == TokenEnum.DOCSTRING:
			self.Consume()
			result = Docstring(self.line, self.PeekBackwards())
		else:
			result = self.ExpressionOrAssignment()
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], KeywordDescription[self.tokens[self.tokenIndex].value]))
			else:
				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], self.tokens[self.tokenIndex].value))
		if not result:
			self.Abort("Could not form a valid statement.")
		return result

## Node types
class NodeEnum(object):
	ARRAYATOM = 0
	ARRAYCREATION = 1
	ARRAYFUNCORID = 2
	BINARYOPERATOR = 3
	CONSTANT = 4
	EXPRESSION = 5
	FUNCTIONCALL = 6
	FUNCTIONCALLARGUMENT = 7
	IDENTIFIER = 8
	LENGTH = 9
	STRUCTCREATION = 10
	UNARYOPERATOR = 11

NodeDescription = [
	"ARRAYATOM",
	"ARRAYCREATION",
	"ARRAYFUNCORID",
	"BINARYOPERATOR",
	"CONSTANT",
	"EXPRESSION",
	"FUNCTIONCALL",
	"FUNCTIONCALLARGUMENT",
	"IDENTIFIER",
	"LENGTH",
	"STRUCTCREATION",
	"UNARYOPERATOR"
]

class Node(object):
	__slots__ = ["type"]
	def __init__(self, aType):
	# aType: NodeEnum
		self.type = aType

class BinaryOperatorNode(Node):
	__slots__ = ["operator", "leftOperand", "rightOperand"]
	def __init__(self, aOperator, aLeftOperand, aRightOperand):
	# aOperator: Token
	# aLeftOperand: Instance of a class that inherits from Node
	# aRightOperand: Instance of a class that inherits from Node
		super(BinaryOperatorNode, self).__init__(NodeEnum.BINARYOPERATOR)
		self.operator = aOperator
		self.leftOperand = aLeftOperand
		self.rightOperand = aRightOperand

	def __str__(self):
		return """
===== Node =====
Type: Binary operator
"""

class UnaryOperatorNode(Node):
	__slots__ = ["operator", "operand"]
	def __init__(self, aOperator, aOperand):
	# aOperator: Token
	# aOperand: Instance of a class that inherits from Node
		super(UnaryOperatorNode, self).__init__(NodeEnum.UNARYOPERATOR)
		self.operator = aOperator
		self.operand = aOperand

	def __str__(self):
		return """
===== Node =====
Type: Unary operator
"""

class ExpressionNode(Node):
	__slots__ = ["child"]
	def __init__(self, aChild):
	# aChild: Instance of a class that inherits from Node
		super(ExpressionNode, self).__init__(NodeEnum.EXPRESSION)
		self.child = aChild

	def __str__(self):
		return """
===== Node =====
Type: Expression
"""

class ArrayAtomNode(Node):
	__slots__ = ["child", "expression"]
	def __init__(self, aChild, aExpression):
	# aChild: Instance of a class that inherits from Node
	# aExpression: Expression
		super(ArrayAtomNode, self).__init__(NodeEnum.ARRAYATOM)
		self.child = aChild
		self.expression = aExpression

	def __str__(self):
		return """
===== Node =====
Type: Array atom
"""

class ArrayFuncOrIdNode(Node):
	__slots__ = ["child", "expression"]
	def __init__(self, aChild, aExpression):
	# aChild: Instance of a class that inherits from Node
	# aExpression: Expression
		super(ArrayFuncOrIdNode, self).__init__(NodeEnum.ARRAYFUNCORID)
		self.child = aChild
		self.expression = aExpression

	def __str__(self):
		return """
===== Node =====
Type: Array, function, or identifier
"""

class ConstantNode(Node):
	__slots__ = ["value"]
	def __init__(self, aValue):
	# aValue: Token
		super(ConstantNode, self).__init__(NodeEnum.CONSTANT)
		self.value = aValue

	def __str__(self):
		return """
===== Node =====
Type: Constant
"""

class FunctionCallNode(Node):
	__slots__ = ["name", "arguments", "identifier"]
	def __init__(self, aName, aArguments):
	# aName: Token
	# aArguments: List of FunctionCallArgument
		super(FunctionCallNode, self).__init__(NodeEnum.FUNCTIONCALL)
		self.name = aName.value.upper()
		self.identifier = aName.value
		self.arguments = aArguments

	def __str__(self):
		return """
===== Node =====
Type: Function call
"""

class FunctionCallArgument(Node):
	__slots__ = ["name", "expression", "identifier"]
	def __init__(self, aName, aExpression):
	# aName: Token
	# aExpression: Expression
		super(FunctionCallArgument, self).__init__(NodeEnum.FUNCTIONCALLARGUMENT)
		if aName:
			self.name = aName.value.upper()
			self.identifier = aName.value
		else:
			self.name = None
			self.identifier = None
		self.expression = aExpression

	def __str__(self):
		return """
===== Node =====
Type: Function call argument
"""

class IdentifierNode(Node):
	__slots__ = ["name", "identifier"]
	def __init__(self, aName):
	# aName: List of string
		super(IdentifierNode, self).__init__(NodeEnum.IDENTIFIER)
		if isinstance(aName, list):
			self.name = [e.upper() for e in aName]
			self.identifier = aName
		else:
			self.name = [aName.value.upper()]
			self.identifier = [aName.value]

	def __str__(self):
		return """
===== Node =====
Type: Identifier
"""

class LengthNode(Node):
	__slots__ = []
	def __init__(self):
		super(LengthNode, self).__init__(NodeEnum.LENGTH)

	def __str__(self):
		return """
===== Node =====
Type: Length
"""

class ArrayCreationNode(Node):
	__slots__ = ["arrayType", "size"]
	def __init__(self, aArrayType, aSize):
	# aArrayType: 
	# aSize: int
		super(ArrayCreationNode, self).__init__(NodeEnum.ARRAYCREATION)
		self.arrayType = aArrayType
		self.size = aSize

	def __str__(self):
		return """
===== Node =====
Type: Array creation
"""

class StructCreationNode(Node):
	__slots__ = ["structType"]
	def __init__(self, aStructType):
	# aStructType: List of string
		super(StructCreationNode, self).__init__(NodeEnum.STRUCTCREATION)
		self.structType = aStructType

	def __str__(self):
		return """
===== Node =====
Type: Struct creation
"""

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
