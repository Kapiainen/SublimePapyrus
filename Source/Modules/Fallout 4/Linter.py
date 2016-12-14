import re, os

#1: Lexical analysis
class TokenEnum(object):
	"""Types of tokens."""
	COLON = 0
	COMMA = 1
	COMMENTBLOCK = 2
	COMMENTLINE = 3
	DOCSTRING = 4
	FLOAT = 5
	IDENTIFIER = 6
	INT = 7
	KEYWORD = 8
	LEFTBRACKET = 9
	LEFTPARENTHESIS = 10
	MULTILINE = 11
	NEWLINE = 12
	RIGHTBRACKET = 13
	RIGHTPARENTHESIS = 14
	STRING = 15
	UNMATCHED = 16
	WHITESPACE = 17
	# Operators
	ADDITION = 18
	AND = 19
	ASSIGN = 20
	ASSIGNADDITION = 21
	ASSIGNDIVISION = 22
	ASSIGNMODULUS = 23
	ASSIGNMULTIPLICATION = 24
	ASSIGNSUBTRACTION = 25
	DIVISION = 26
	DOT = 27
	EQUAL = 28
	GREATERTHAN = 29
	GREATERTHANOREQUAL = 30
	LESSTHAN = 31
	LESSTHANOREQUAL = 32
	MODULUS = 33
	MULTIPLICATION = 34
	NOT = 35
	NOTEQUAL = 36
	OR = 37
	SUBTRACTION = 	38
	# Keywords
	kAS = 39
	kAUTO = 40
	kAUTOREADONLY = 41
	kBETAONLY = 42
	kBOOL = 43
	kCOLLAPSED = 44
	kCOLLAPSEDONBASE = 45
	kCOLLAPSEDONREF = 46
	kCONDITIONAL = 47
	kCONST = 48
	kCUSTOMEVENT = 49
	kDEBUGONLY = 50
	kDEFAULT = 51
	kELSE = 52
	kELSEIF = 53
	kENDEVENT = 54
	kENDFUNCTION = 55
	kENDGROUP = 56
	kENDIF = 57
	kENDPROPERTY = 58
	kENDSTATE = 59
	kENDSTRUCT = 60
	kENDWHILE = 61
	kEVENT = 62
	kEXTENDS = 63
	kFALSE = 64
	kFLOAT = 65
	kFUNCTION = 66
	kGLOBAL = 67
	kGROUP = 68
	kHIDDEN = 69
	kIF = 70
	kIMPORT = 71
	kINT = 72
	kIS = 73
	kLENGTH = 74
	kMANDATORY = 75
	kNATIVE = 76
	kNEW = 77
	kNONE = 78
	kPARENT = 79
	kPROPERTY = 80
	kRETURN = 81
	kSCRIPTNAME = 82
	kSELF = 83
	kSTATE = 84
	kSTRING = 85
	kSTRUCT = 86
	kTRUE = 87
	kVAR = 88
	kWHILE = 89

TokenDescription = [
	"COLON",
	"COMMA",
	"COMMENTBLOCK",
	"COMMENTLINE",
	"DOCSTRING",
	"FLOAT",
	"IDENTIFIER",
	"INT",
	"KEYWORD",
	"LEFTBRACKET",
	"LEFTPARENTHESIS",
	"MULTILINE",
	"NEWLINE",
	"RIGHTBRACKET",
	"RIGHTPARENTHESIS",
	"STRING",
	"UNMATCHED",
	"WHITESPACE",
	"ADDITION",
	"AND",
	"ASSIGN",
	"ASSIGNADDITION",
	"ASSIGNDIVISION",
	"ASSIGNMODULUS",
	"ASSIGNMULTIPLICATION",
	"ASSIGNSUBTRACTION",
	"DIVISION",
	"DOT",
	"EQUAL",
	"GREATERTHAN",
	"GREATERTHANOREQUAL",
	"LESSTHAN",
	"LESSTHANOREQUAL",
	"MODULUS",
	"MULTIPLICATION",
	"NOT",
	"NOTEQUAL",
	"OR",
	"SUBTRACTION",
	"kAS",
	"kAUTO",
	"kAUTOREADONLY",
	"kBETAONLY",
	"kBOOL",
	"kCOLLAPSED",
	"kCOLLAPSEDONBASE",
	"kCOLLAPSEDONREF",
	"kCONDITIONAL",
	"kCONST",
	"kCUSTOMEVENT",
	"kDEBUGONLY",
	"kDEFAULT",
	"kELSE",
	"kELSEIF",
	"kENDEVENT",
	"kENDFUNCTION",
	"kENDGROUP",
	"kENDIF",
	"kENDPROPERTY",
	"kENDSTATE",
	"kENDSTRUCT",
	"kENDWHILE",
	"kEVENT",
	"kEXTENDS",
	"kFALSE",
	"kFLOAT",
	"kFUNCTION",
	"kGLOBAL",
	"kGROUP",
	"kHIDDEN",
	"kIF",
	"kIMPORT",
	"kINT",
	"kIS",
	"kLENGTH",
	"kMANDATORY",
	"kNATIVE",
	"kNEW",
	"kNONE",
	"kPARENT",
	"kPROPERTY",
	"kRETURN",
	"kSCRIPTNAME",
	"kSELF",
	"kSTATE",
	"kSTRING",
	"kSTRUCT",
	"kTRUE",
	"kVAR",
	"kWHILE"
]

class Token(object):
	"""Token objects."""
	__slots__ = ["type", "line", "column", "value"]
	def __init__(self, aType, aValue, aLine, aColumn):
	# aType: TokenEnum
	# aValue: string
	# aLine: int
	# aColumn: int
		self.type = aType
		self.line = aLine
		self.column = aColumn
		self.value = aValue

	def __str__(self):
		return """
===== Token =====
Type: %s
Value: '%s'
Line: %d
Column: %d
""" % (
		TokenDescription[self.type],
		self.value,
		self.line,
		self.column
	)

class LexicalError(Exception):
	"""Lexical error."""
	def __init__(self, aMessage, aLine, aColumn):
	# aMessage: string
	# aLine: int
	# aColumn: int
		self.message = aMessage
		self.line = aLine
		self.column = aColumn

class Lexical(object):
	"""Lexical analysis."""
	__slots__ = ["regex"]
	def __init__(self):
		self.regex = re.compile(
			"|".join(
				"(?P<t%s>%s)" % pair for pair in [
					(TokenEnum.COMMENTBLOCK, r";/[\S\s]*?(?=/;)/;"),
					(TokenEnum.COMMENTLINE, r";[^\n]*"),
					(TokenEnum.DOCSTRING, r"{[\S\s]*?(?=})}"),
					(TokenEnum.LEFTPARENTHESIS, r"\("),
					(TokenEnum.RIGHTPARENTHESIS, r"\)"),
					(TokenEnum.LEFTBRACKET, r"\["),
					(TokenEnum.RIGHTBRACKET, r"\]"),
					(TokenEnum.MULTILINE, r"\\[^\n]*?(?=\n)\n"),
					(TokenEnum.COMMA, r","),
					(TokenEnum.DOT, r"\."),
					(TokenEnum.EQUAL, r"=="),
					(TokenEnum.NOTEQUAL, r"!="),
					(TokenEnum.GREATERTHANOREQUAL, r">="),
					(TokenEnum.LESSTHANOREQUAL, r"<="),
					(TokenEnum.GREATERTHAN, r">"),
					(TokenEnum.LESSTHAN, r"<"),
					(TokenEnum.NOT, r"!"),
					(TokenEnum.AND, r"&&"),
					(TokenEnum.OR, r"\|\|"),
					(TokenEnum.ASSIGNADDITION, r"\+="),
					(TokenEnum.ASSIGNSUBTRACTION, r"-="),
					(TokenEnum.ASSIGNMULTIPLICATION, r"\*="),
					(TokenEnum.ASSIGNDIVISION, r"/="),
					(TokenEnum.ASSIGNMODULUS, r"%="),
					(TokenEnum.ASSIGN, r"="),
					(TokenEnum.kAS, r"\bas\b"),
					(TokenEnum.kAUTO, r"\bauto\b"),
					(TokenEnum.kAUTOREADONLY, r"\bautoreadonly\b"),
					(TokenEnum.kBETAONLY, r"\bbetaonly\b"),
					(TokenEnum.kBOOL, r"\bbool\b"),
					(TokenEnum.kCOLLAPSED, r"\bcollapsed\b"),
					(TokenEnum.kCOLLAPSEDONBASE, r"\bcollapsedonbase\b"),
					(TokenEnum.kCOLLAPSEDONREF, r"\bcollapsedonref\b"),
					(TokenEnum.kCONDITIONAL, r"\bconditional\b"),
					(TokenEnum.kCONST, r"\bconst\b"),
					(TokenEnum.kCUSTOMEVENT, r"\bcustomevent\b"),
					(TokenEnum.kDEBUGONLY, r"\bdebugonly\b"),
					(TokenEnum.kDEFAULT, r"\bdefault\b"),
					(TokenEnum.kELSE, r"\belse\b"),
					(TokenEnum.kELSEIF, r"\belseif\b"),
					(TokenEnum.kENDEVENT, r"\bendevent\b"),
					(TokenEnum.kENDFUNCTION, r"\bendfunction\b"),
					(TokenEnum.kENDGROUP, r"\bendgroup\b"),
					(TokenEnum.kENDIF, r"\bendif\b"),
					(TokenEnum.kENDPROPERTY, r"\bendproperty\b"),
					(TokenEnum.kENDSTATE, r"\bendstate\b"),
					(TokenEnum.kENDSTRUCT, r"\bendstruct\b"),
					(TokenEnum.kENDWHILE, r"\bendwhile\b"),
					(TokenEnum.kEVENT, r"\bevent\b"),
					(TokenEnum.kEXTENDS, r"\bextends\b"),
					(TokenEnum.kFALSE, r"\bfalse\b"),
					(TokenEnum.kFLOAT, r"\bfloat\b"),
					(TokenEnum.kFUNCTION, r"\bfunction\b"),
					(TokenEnum.kGLOBAL, r"\bglobal\b"),
					(TokenEnum.kGROUP, r"\bgroup\b"),
					(TokenEnum.kHIDDEN, r"\bhidden\b"),
					(TokenEnum.kIF, r"\bif\b"),
					(TokenEnum.kIMPORT, r"\bimport\b"),
					(TokenEnum.kINT, r"\bint\b"),
					(TokenEnum.kIS, r"\bis\b"),
					(TokenEnum.kLENGTH, r"\blength\b"),
					(TokenEnum.kMANDATORY, r"\bmandatory\b"),
					(TokenEnum.kNATIVE, r"\bnative\b"),
					(TokenEnum.kNEW, r"\bnew\b"),
					(TokenEnum.kNONE, r"\bnone\b"),
					(TokenEnum.kPARENT, r"\bparent\b"),
					(TokenEnum.kPROPERTY, r"\bproperty\b"),
					(TokenEnum.kRETURN, r"\breturn\b"),
					(TokenEnum.kSCRIPTNAME, r"\bscriptname\b"),
					(TokenEnum.kSELF, r"\bself\b"),
					(TokenEnum.kSTATE, r"\bstate\b"),
					(TokenEnum.kSTRING, r"\bstring\b"),
					(TokenEnum.kSTRUCT, r"\bstruct\b"),
					(TokenEnum.kTRUE, r"\btrue\b"),
					(TokenEnum.kVAR, r"\bvar\b"),
					(TokenEnum.kWHILE, r"\bwhile\b"),
					(TokenEnum.IDENTIFIER, r"[a-z_][0-9a-z_]*"),
					(TokenEnum.FLOAT, r"(-\d+\.\d+)|(\d+\.\d+)"), # TODO: Revisit this definition
					(TokenEnum.INT, r"((0x(\d|[a-f])+)|((\d+))(?![a-z_]))"),
					(TokenEnum.ADDITION, r"\+"),
					(TokenEnum.SUBTRACTION, r"-"),
					(TokenEnum.MULTIPLICATION, r"\*"),
					(TokenEnum.DIVISION, r"/"),
					(TokenEnum.MODULUS, r"%"),
					(TokenEnum.STRING, r"\".*?(?:(?<=\\\\)\"|(?<!\\)\")"),
					(TokenEnum.COLON, r"\:"),
					(TokenEnum.NEWLINE, r"[\n\r]"),
					(TokenEnum.WHITESPACE, r"[ \t]"),
					(TokenEnum.UNMATCHED, r"."),
				]
			),
			re.IGNORECASE
		)

	def Process(self, aString):
		"""Generates tokens from a string."""
	# aString: string
		line = 1
		column = -1
		for match in self.regex.finditer(aString):
			t = match.lastgroup
			v = match.group(t)
			t = int(match.lastgroup[1:])
			if t == TokenEnum.WHITESPACE:
				continue
			elif t == TokenEnum.COMMENTLINE:
				yield Token(TokenEnum.COMMENTLINE, None, line, match.start()-column)
				continue
			elif t == TokenEnum.COMMENTBLOCK:
				i = v.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				yield Token(TokenEnum.COMMENTBLOCK, None, line, match.start()-column)
				continue
			elif t == TokenEnum.MULTILINE:
				line += 1
				column = match.end()-1
				continue
			if t == TokenEnum.DOCSTRING or t == TokenEnum.STRING:
				yield Token(t, v[1:-1], line, match.start()-column)
				i = v.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				continue
			elif t == TokenEnum.UNMATCHED:
				raise LexicalError("Encountered an unexpected character ('%s')." % v, line, match.start()-column)
			yield Token(t, v, line, match.start()-column)
			if t == TokenEnum.NEWLINE:
				line += 1
				column = match.end()-1
		yield Token(TokenEnum.NEWLINE, "\n", line, 1)

#2: Syntactic analysis
# Statement types
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
	"WHILE"
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
	__slots__ = ["name", "parent", "flags"]
	def __init__(self, aLine, aName, aParent, aFlags):
	# aLine: int
	# aName: List of string
	# aParent: List of string
	# aFlags: List of TokenEnum
		super(ScriptSignature, self).__init__(StatementEnum.SCRIPTSIGNATURE, aLine)
		self.name = aName
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
				if self.tokens[self.tokenIndex].type == TokenEnum.IDENTIFIER or self.tokens[self.tokenIndex].type == TokenEnum.kBOOL or self.tokens[self.tokenIndex].type == TokenEnum.kFLOAT or self.tokens[self.tokenIndex].type == TokenEnum.kINT or self.tokens[self.tokenIndex].type == TokenEnum.kSTRING:
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
			nextToken = self.Peek()
			if nextToken and nextToken.type == TokenEnum.LEFTBRACKET:
				typ = self.ExpectType(True)
				self.Expect(TokenEnum.LEFTBRACKET)
				self.ExpectExpression()
				size = self.Pop()
				self.Expect(TokenEnum.RIGHTBRACKET)
				self.Shift(ArrayCreationNode(typ, size))
			else:
				typ = self.ExpectType(False)
				self.Shift(StructCreationNode(typ))
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
	# aSize: 
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
	# aStructType: 
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
		body = None
		if body:
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
								break
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
		return

	def GetCachedScript(self, aType, aLine):
		self.line = aLine
		key = ":".join(aType)
		result = self.cache.get(key, None)
		if result:
			return result
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
		raise SemanticError("Cannot find a script called '%s'." % key, self.line)

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
					stat = aSyn.Process(tokens)
					if stat:
						self.AssembleScript(stat)
					tokens = []
			elif token.type != TokenEnum.COMMENTLINE and token.type != TokenEnum.COMMENTBLOCK:
				tokens.append(token)
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
			print(self.cache)
			return script
		return None
