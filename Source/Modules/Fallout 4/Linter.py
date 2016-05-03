import re

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
					(TokenEnum.FLOAT, r"(-\d+\.\d+)|(\d+\.\d+)"),
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

	def Process(self, asString):
		"""Generates tokens from a string."""
		line = 1
		column = -1
		for match in self.regex.finditer(asString):
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
		self.statementType = aStatementType
		self.line = aLine

class Keyword(Statement):
	__slots__ = []
	def __init__(self, aStat, aLine):
		super(Keyword, self).__init__(aStat, aLine)

class KeywordExpression(Statement):
	__slots__ = ["expression"]
	def __init__(self, aStat, aLine, aExpression):
		super(KeywordExpression, self).__init__(aStat, aLine)
		self.expression = aExpression

class Type(object):
	__slots__ = ["name", "array"]
	def __init__(self, aName, aArray):
		self.name = aName # String
		self.array = aArray # Bool

class Assignment(Statement):
	__slots__ = ["leftExpression", "rightExpression"]
	def __init__(self, aLine, aLeftExpression, aRightExpression):
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
	__slots__ = ["name"]
	def __init__(self, aLine, aName):
		super(CustomEvent, self).__init__(StatementEnum.CUSTOMEVENT, aLine)
		self.name = aName

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
		super(Docstring, self).__init__(StatementEnum.DOCSTRING, aLine)
		self.value = aValue

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
		super(Expression, self).__init__(StatementEnum.EXPRESSION, aLine)
		self.expression = aExpression

	def __str__(self):
		return """
===== Statement =====
Type: Expression
Line: %d
""" % (self.line)

class ParameterSignature(object):#Statement):
	__slots__ = ["line", "name", "type", "value"]
	def __init__(self, aLine, aName, aType, aValue):
		#super(Parameter, self).__init__(StatementEnum.PARAMETER, aLine)
		self.line = aLine
		self.name = aName # String
		self.type = aType # Instance of Type
		self.value = aValue # Literal expression

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
	__slots__ = ["name", "type", "flags", "parameters"]
	def __init__(self, aLine, aName, aType, aFlags, aParameters):
		super(FunctionSignature, self).__init__(StatementEnum.FUNCTIONSIGNATURE, aLine)
		self.name = aName
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
		":".join([f.value for f in returnType]),
		array,
		parameterCount,
		", ".join([TokenDescription[f] for f in flags]),
		self.line
	)

class GroupSignature(Statement):
	__slots__ = ["name", "flags"]
	def __init__(self, aLine, aName, aFlags):
		super(GroupSignature, self).__init__(StatementEnum.GROUPSIGNATURE, aLine)
		self.name = aName
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
	__slots__ = ["remote", "name", "flags", "parameters"]
	def __init__(self, aLine, aRemote, aName, aFlags, aParameters):
		super(EventSignature, self).__init__(StatementEnum.EVENTSIGNATURE, aLine)
		self.name = aName
		self.flags = aFlags
		self.parameters = aParameters
		self.remote = aRemote

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
		super(If, self).__init__(StatementEnum.IF, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: If
Line: %d
""" % (self.line)

class Import(Statement):
	__slots__ = ["name"]
	def __init__(self, aLine, aName):
		super(Import, self).__init__(StatementEnum.IMPORT, aLine)
		self.name = aName

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
	__slots__ = ["name", "type", "flags", "value"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
		super(PropertySignature, self).__init__(StatementEnum.PROPERTYSIGNATURE, aLine)
		self.name = aName # String
		self.type = aType # Instance of Type
		self.flags = aFlags # List of Lex.KeywordEnum properties
		self.value = aValue # Literal expression

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
	__slots__ = ["name", "auto"]
	def __init__(self, aLine, aName, aAuto):
		super(StateSignature, self).__init__(StatementEnum.STATESIGNATURE, aLine)
		self.name = aName
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
	__slots__ = ["name", "auto"]
	def __init__(self, aLine, aName):
		super(StructSignature, self).__init__(StatementEnum.STRUCTSIGNATURE, aLine)
		self.name = aName

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
	__slots__ = ["name", "type", "flags", "value"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
		super(Variable, self).__init__(StatementEnum.VARIABLE, aLine)
		self.name = aName # String
		self.type = aType # Instance of Type
		self.flags = aFlags # List of Lex.KeywordEnum properties
		self.value = aValue # Expression

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
		super(While, self).__init__(StatementEnum.WHILE, aLine, aExpression)

	def __str__(self):
		return """
===== Statement =====
Type: While
Line: %d
""" % (self.line)

class SyntacticError(Exception):
	def __init__(self, aMessage, aLine):
		self.message = aMessage
		self.line = aLine

class Syntactic(object):
	def __init__(self):
		self.stack = None

	def Abort(self, aMessage):
		if self.tokenIndex >= self.tokenCount and self.tokenCount > 0:
			self.tokenIndex -= 1
#		if self.stack:
#			print(self.stack)
#			for s in self.stack:
#				print(TokenDescription[s.type])
#		print(TokenDescription[self.tokens[self.tokenIndex].type])
		raise SyntacticError(aMessage, self.tokens[self.tokenIndex].line)

	def Accept(self, aToken):
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == aToken:
				self.tokenIndex += 1
				return True
		return False

	def Expect(self, aToken):
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
		i = self.tokenIndex + aN
		if i < self.tokenCount:
			return self.tokens[i]
		return None

	def PeekBackwards(self, aN = 1):
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
		if aFlags:
#			print("Looking for the following flags on line %d: %s" % (self.line, ", ".join([TokenDescription[f] for f in aFlags])))
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
#					print("No flags were accepted on line %d" % self.line)
#					print("Remaining attempts: %d" % attempts)
					if successfulFlags:
						return successfulFlags
					else:
						return None
				attempts -= 1
#			print("Found following flags on line %d: %s" % (self.line, ", ".join([TokenDescription[f] for f in successfulFlags])))
			return successfulFlags
#		print("No flags were given to test for on line %d" % self.line)
		return None

	def AcceptType(self, aBaseTypes):
		result = None
		if self.Accept(TokenEnum.IDENTIFIER):
			result = [self.PeekBackwards().value.upper()]
			while self.Accept(TokenEnum.COLON):
				result.append(self.PeekBackwards().value.upper())
			return result
		elif aBaseTypes and (self.Accept(TokenEnum.kBOOL) or self.Accept(TokenEnum.kFLOAT) or self.Accept(TokenEnum.kINT) or self.Accept(TokenEnum.kSTRING) or self.Accept(TokenEnum.kVAR)):
			result = [self.PeekBackwards()]
			return result
		else:
			return None

	def ExpectType(self, aBaseTypes):
		result = None
		if self.Accept(TokenEnum.IDENTIFIER):
			result = [self.PeekBackwards().value.upper()]
			while self.Accept(TokenEnum.COLON):
				self.Expect(TokenEnum.IDENTIFIER)
				result.append(self.PeekBackwards().value.upper())
			return result
		elif aBaseTypes and (self.Accept(TokenEnum.kBOOL) or self.Accept(TokenEnum.kFLOAT) or self.Accept(TokenEnum.kINT) or self.Accept(TokenEnum.kSTRING) or self.Accept(TokenEnum.kVAR)):
			result = [self.PeekBackwards().value.upper()]
			return result
		else:
			raise SyntacticError("Expected a type identifier.", self.line)

	def Property(self, aType):
		#self.Expect(TokenEnum.kPROPERTY)
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
				self.Abort("A property cannot have both the AUTO and the AUTOREADONLY keyword.")
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
		return PropertySignature(self.line, name.value, aType, flags, value)

	def FunctionParameters(self):
		parameters = []
		typ = self.ExpectType(True)
		array = False
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expect(TokenEnum.RIGHTBRACKET)
			array = True
		typ = Type(typ, array)
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
			typ = Type(typ, array)
			name = self.Expect(TokenEnum.IDENTIFIER)
			value = None
			if self.Accept(TokenEnum.ASSIGN):
				value = self.ExpectExpression()
			parameters.append(ParameterSignature(self.line, name.value, typ, value))
		return parameters

	def Function(self, aType):
		self.Expect(TokenEnum.IDENTIFIER)
		name = self.PeekBackwards()
		parameters = None
		nextToken = self.Peek()
		self.Expect(TokenEnum.LEFTPARENTHESIS)
		if nextToken and nextToken.type != TokenEnum.RIGHTPARENTHESIS:
			parameters = self.FunctionParameters()
		self.Expect(TokenEnum.RIGHTPARENTHESIS)
		return FunctionSignature(self.line, name.value, aType, self.AcceptFlags([TokenEnum.kNATIVE, TokenEnum.kGLOBAL, TokenEnum.kDEBUGONLY, TokenEnum.kBETAONLY]), parameters)

	def Shift(self, aItem = None):
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
#		print(1)
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
#		print(2)
		self.BoolExpression()
		while self.Accept(TokenEnum.AND):
			self.Shift()
			self.BoolExpression()
			self.ReduceBinaryOperator()
		return True

	def BoolExpression(self):
#		print(3)
		self.AddExpression()
		while self.Accept(TokenEnum.EQUAL) or self.Accept(TokenEnum.NOTEQUAL) or self.Accept(TokenEnum.GREATERTHANOREQUAL) or self.Accept(TokenEnum.LESSTHANOREQUAL) or self.Accept(TokenEnum.GREATERTHAN) or self.Accept(TokenEnum.LESSTHAN):
			self.Shift()
			self.AddExpression()
			self.ReduceBinaryOperator()
		return True

	def AddExpression(self):
#		print(4)
		self.MultExpression()
		while self.Accept(TokenEnum.ADDITION) or self.Accept(TokenEnum.SUBTRACTION):
			self.Shift()
			self.MultExpression()
			self.ReduceBinaryOperator()
		return True

	def MultExpression(self):
#		print(5)
		self.UnaryExpression()
		while self.Accept(TokenEnum.MULTIPLICATION) or self.Accept(TokenEnum.DIVISION) or self.Accept(TokenEnum.MODULUS):
			self.Shift()
			self.UnaryExpression()
			self.ReduceBinaryOperator()
		return True

	def UnaryExpression(self):
#		print(6)
		unaryOp = False
		if self.Accept(TokenEnum.SUBTRACTION) or self.Accept(TokenEnum.NOT):
			self.Shift()
			unaryOp = True
		self.CastAtom()
		if unaryOp:
			self.ReduceUnaryOperator()
		return True

	def CastAtom(self):
#		print(7)
		self.DotAtom()
		if self.Accept(TokenEnum.kAS) or self.Accept(TokenEnum.kIS):
			self.Shift()
			if self.tokens[self.tokenIndex].type == TokenEnum.IDENTIFIER or self.tokens[self.tokenIndex].type == TokenEnum.kBOOL or self.tokens[self.tokenIndex].type == TokenEnum.kFLOAT or self.tokens[self.tokenIndex].type == TokenEnum.kINT or self.tokens[self.tokenIndex].type == TokenEnum.kSTRING:
				self.Consume()
			else:
				self.Abort("Expected a type.")
			self.Shift(IdentifierNode(self.PeekBackwards()))
			self.ReduceBinaryOperator()
		return True

	def DotAtom(self):
#		print(8)
		#if self.AcceptLiteral():
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
#		print(9)
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
#		print(10)
		if self.Accept(TokenEnum.kNEW):
			self.ExpectType(True)
			typ = self.PeekBackwards()
			self.Expect(TokenEnum.LEFTBRACKET)
			if not self.Accept(TokenEnum.INT):
				self.Abort("Expected an int literal.")
			size = self.PeekBackwards()
			self.Expect(TokenEnum.RIGHTBRACKET)
			self.Shift(ArrayCreationNode(typ, size))
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
#		print(11)
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
#		print(12)
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
#		print(13)
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
#		print("Variable def")
		self.Expect(TokenEnum.IDENTIFIER)
		name = self.PeekBackwards()
		value = None
		if self.Accept(TokenEnum.ASSIGN):
			self.Expression()
			value = self.Pop()
		return Variable(self.line, name.value, aType, self.AcceptFlags([TokenEnum.kCONDITIONAL, TokenEnum.kCONST, TokenEnum.kHIDDEN]), value)

	def ExpectExpression(self):
		if not self.Expression():
			self.Abort("Expected an expression")
		return self.Pop()

	def EventParameters(self):
		parameters = []
		typ = self.ExpectType(True)
		array = False
		if self.Accept(TokenEnum.LEFTBRACKET):
			self.Expect(TokenEnum.RIGHTBRACKET)
			array = True
		typ = Type(typ, array)
		name = self.Expect(TokenEnum.IDENTIFIER)
		parameters.append(ParameterSignature(self.line, name, typ, None))
		while self.Accept(TokenEnum.COMMA):
			typ = self.ExpectType(True)
			array = False
			if self.Accept(TokenEnum.LEFTBRACKET):
				self.Expect(TokenEnum.RIGHTBRACKET)
				array = True
			typ = Type(typ, array)
			name = self.Expect(TokenEnum.IDENTIFIER)
			parameters.append(ParameterSignature(self.line, name.value, typ, None))
		return parameters

	def Process(self, aTokens):
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
			typ = Type([typ.value.upper()], array)
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
						typ = Type(typ, array)
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
							typ = Type([self.Expect(TokenEnum.IDENTIFIER).value.upper()], True)
							self.Consume()
							nextToken = self.Peek()
							self.Consume()
							if nextToken:
#								print(nextToken)
								if nextToken.type == TokenEnum.kFUNCTION:
									self.Consume()
									result = self.Function(typ)
								elif nextToken.type == TokenEnum.kPROPERTY:
									self.Consume()
									result = self.Property(typ)
#								elif nextToken.type == TokenEnum.IDENTIFIER:
#									result = self.Variable(typ)
						else:
							result = self.ExpressionOrAssignment()
				elif nextToken.type == TokenEnum.kPROPERTY:
					typ = Type([self.Expect(TokenEnum.IDENTIFIER).value.upper()], False)
					self.Consume()
					result = self.Property(typ)
				elif nextToken.type == TokenEnum.kFUNCTION:
					typ = Type([self.Expect(TokenEnum.IDENTIFIER).value.upper()], False)
					self.Consume()
					result = self.Function(typ)
				elif nextToken.type == TokenEnum.IDENTIFIER:
					result = self.Variable(Type([self.Expect(TokenEnum.IDENTIFIER).value.upper()], False))
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
				parameters = self.EventParameters()
			self.Expect(TokenEnum.RIGHTPARENTHESIS)
			result = EventSignature(self.line, remote, name.value, self.AcceptFlags([TokenEnum.kNATIVE]), parameters)
		elif tokenType == TokenEnum.kENDEVENT:
			self.Consume()
			result = EndEvent(self.line)
		elif tokenType == TokenEnum.kENDPROPERTY:
			self.Consume()
			result = EndProperty(self.line)
		elif tokenType == TokenEnum.kCUSTOMEVENT:
			self.Consume()
			result = CustomEvent(self.line, self.Expect(TokenEnum.IDENTIFIER).value)
		elif tokenType == TokenEnum.kGROUP:
			self.Consume()
			name = self.Expect(TokenEnum.IDENTIFIER)
			result = GroupSignature(self.line, name.value, self.AcceptFlags([TokenEnum.kCOLLAPSED, TokenEnum.kCOLLAPSEDONBASE, TokenEnum.kCOLLAPSEDONREF]))
		elif tokenType == TokenEnum.kENDGROUP:
			self.Consume()
			result = EndGroup(self.line)
		elif tokenType == TokenEnum.kSTRUCT:
			self.Consume()
			result = StructSignature(self.line, self.Expect(TokenEnum.IDENTIFIER).value)
		elif tokenType == TokenEnum.kENDSTRUCT:
			self.Consume()
			result = EndStruct(self.line)
		elif tokenType == TokenEnum.kSTATE:
			self.Consume()
			result = StateSignature(self.line, self.Expect(TokenEnum.IDENTIFIER).value, False)
		elif tokenType == TokenEnum.kAUTO:
			self.Consume()
			self.Expect(TokenEnum.kSTATE)
			result = StateSignature(self.line, self.Expect(TokenEnum.IDENTIFIER).value, True)
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
			result = Docstring(self.line, self.PeekBackwards().value)
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
	UNARYOPERATOR = 10

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
	"UNARYOPERATOR"
]

class Node(object):
	__slots__ = ["type"]
	def __init__(self, aType):
		self.type = aType

class BinaryOperatorNode(Node):
	__slots__ = ["operator", "leftOperand", "rightOperand"]
	def __init__(self, aOperator, aLeftOperand, aRightOperand):
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
		super(ConstantNode, self).__init__(NodeEnum.CONSTANT)
		self.value = aValue

	def __str__(self):
		return """
===== Node =====
Type: Constant
"""

class FunctionCallNode(Node):
	__slots__ = ["name", "arguments"]
	def __init__(self, aName, aArguments):
		super(FunctionCallNode, self).__init__(NodeEnum.FUNCTIONCALL)
		self.name = aName
		self.arguments = aArguments

	def __str__(self):
		return """
===== Node =====
Type: Function call
"""

class FunctionCallArgument(Node):
	__slots__ = ["name", "expression"]
	def __init__(self, aName, aExpression):
		super(FunctionCallArgument, self).__init__(NodeEnum.FUNCTIONCALLARGUMENT)
		self.name = aName
		self.expression = aExpression

	def __str__(self):
		return """
===== Node =====
Type: Function call argument
"""

class IdentifierNode(Node):
	__slots__ = ["value"]
	def __init__(self, aValue):
		super(IdentifierNode, self).__init__(NodeEnum.IDENTIFIER)
		self.value = aValue

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
		super(ArrayCreationNode, self).__init__(NodeEnum.ARRAYCREATION)
		self.arrayType = aArrayType
		self.size = aSize

	def __str__(self):
		return """
===== Node =====
Type: Array creation
"""

#3: Semantic analysis

class SemanticError(Exception):
	def __init__(self, aMessage, aLine):
		self.message = aMessage
		self.line = aLine

#	Objects
#
#		Script
#			.name
#			.flags
#				List of KeywordEnum
#			.parent
#				Script
#			.docstring
#				String
#			.imports
#				List of String
#			.customEvents
#				List of String
#			.variables
#				Dict of Variable
#			.properties
#				Dict of Property
#			.groups
#				Dict of Group
#					Dict of Property
#			.structs
#				Dict of Struct
#			.functions
#				Dict of Function
#			.events
#				Dict of Event
#			.states
#				Dict of State
class Script(object):
	__slots__ = ["name", "flags", "parent", "docstring", "imports", "customEvents", "variables", "properties",  "groups", "functions", "events", "states", "structs"]
	def __init__(self, aName, aFlags, aParent, aDocstring, aImports, aCustomEvents, aVariables, aProperties, aGroups, aFunctions, aEvents, aStates, aStructs):
		self.name = aName
		self.flags = aFlags
		self.parent = aParent
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

#
#		Property
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
#			.value
#				ExpressionNode
#			.docstring
#				String
#			.functions
#				List of Function
class Property(object):
	__slots__ = ["name", "flags", "type", "value", "docstring", "getFunction", "setFunction", "starts", "ends"]
	def __init__(self, aName, aFlags, aType, aValue, aDocstring, aGetFunction, aSetFunction, aStarts, aEnds):
		self.name = aName
		self.flags = aFlags
		self.type = aType
		self.value = aValue
		self.docstring = aDocstring
		self.getFunction = aGetFunction
		self.setFunction = aSetFunction
		self.starts = aStarts
		self.ends = aEnds

#
#		Group
#			.name
#				String
#			.flags
#				List of KeywordEnum
#			.properties
#				Dict of Property
#			.starts
#				Int
#			.ends
#				Int
class Group(object):
	__slots__ = ["name", "flags", "properties", "starts", "ends"]
	def __init__(self, aName, aFlags, aProperties, aStarts, aEnds):
		self.name = aName
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
	__slots__ = ["line", "name", "flags", "type", "value", "docstring"]
	def __init__(self, aLine, aName, aFlags, aType, aValue, aDocstring):
		self.line = aLine
		self.name = aName
		self.flags = aFlags
		self.type = aType
		self.value = aValue
		self.docstring = aDocstring

#
#		Struct
#			.members
#				Dict of StructMember
class Struct(object):
	__slots__ = ["name", "members", "starts", "ends"]
	def __init__(self, aName, aMembers, aStarts, aEnds):
		self.name = aName
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
	__slots__ = ["name", "flags", "type", "parameters", "docstring", "body", "starts", "ends"]
	def __init__(self, aName, aFlags, aType, aParameters, aDocstring, aBody, aStarts, aEnds):
		self.name = aName
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
	__slots__ = ["name", "flags", "remote", "parameters", "docstring", "body", "starts", "ends"]
	def __init__(self, aName, aFlags, aRemote, aParameters, aDocstring, aBody, aStarts, aEnds):
		self.name = aName
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
	__slots__ = ["name", "auto", "functions", "events", "starts", "ends"]
	def __init__(self, aName, aAuto, aFunctions, aEvents, aStarts, aEnds):
		self.name = aName
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
		self.scope = [0]
		self.definition = [[]]

	def Reset(self):
		self.scope = [0]
		self.definition = [[]]

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
			self.scope.pop()
		elif typ == StatementEnum.EVENTSIGNATURE:
			self.scope.append(3)
			self.definition.append([aStat])
		elif typ == StatementEnum.FUNCTIONSIGNATURE:
			self.scope.append(2)
			self.definition.append([aStat])
		else:
			signature = self.definition[-1][0]
			raise SemanticError("Illegal statement in a state definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndStateScope(self, aStat):
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
		self.definition[-1].append(State(signature.name, signature.auto, functions, events, signature.line, aStat.line))
#		print(self.definition[-1])
		self.scope.pop()

	def FunctionEventScope(self, aStat):
		typ = aStat.statementType
		if typ == StatementEnum.ASSIGNMENT:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.DOCSTRING:
			if self.scope[-1] == 2 and self.definition[-1][-1].type != StatementEnum.FUNCTIONSIGNATURE:
				raise SemanticError("Docstrings may only follow immediately after the function signature in function definitions.", aStat.line)
			elif self.scope[-1] == 3 and self.definition[-1][-1].type != StatementEnum.EVENTSIGNATURE:
				raise SemanticError("Docstrings may only follow immediately after the event signature in event definitions.", aStat.line)
			else:
				self.definition[-1].append(aStat)
		elif typ == StatementEnum.ELSE:
			self.definition[-1].append(aStat)
		elif typ == StatementEnum.ELSEIF:
			self.definition[-1].append(aStat)
		elif self.scope[-1] == 2 and typ == StatementEnum.ENDFUNCTION:
			self.EndFunctionEventScope(aStat)
		elif self.scope[-1] == 3 and typ == StatementEnum.ENDEVENT:
			self.EndFunctionEventScope(aStat)
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
			signature = self.definition[-1][0]
			if self.scope[-1] == 2:
				raise SemanticError("Illegal statement in a function definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)
			else:
				raise SemanticError("Illegal statement in an event definition called '%s' that starts on line %d." % (signature.name, signature.line), aStat.line)

	def EndFunctionEventScope(self, aStat):
		functionEventDef = self.definition.pop()
		signature = functionEventDef.pop(0)
		docstring = None
		if functionEventDef and functionEventDef[0].statementType == StatementEnum.DOCSTRING:
			docstring = functionEventDef.pop(0)
		if signature.statementType == StatementEnum.FUNCTIONSIGNATURE:
			self.definition[-1].append(Function(signature.name, signature.flags, signature.type, signature.parameters, docstring, functionEventDef, signature.line, aStat.line))
		else:
			self.definition[-1].append(Event(signature.name, signature.flags, signature.remote, signature.parameters, docstring, functionEventDef, signature.line, aStat.line))
			#aName, aFlags, aRemote, aParameters, aDocstring, aBody, aStarts, aEnds
#		print(self.definition[-1])
		self.scope.pop()

	def PropertyScope(self, aStat):
		typ = aStat.statementType
		signature = self.definition[-1][0]
#		print(signature)
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
				EndPropertyScope(True, aStat.line)
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
			self.definition[-1].append(Property(signature.name, signature.flags, signature.type, signature.value, docstring, getFunc, setFunc, signature.line, aEndLine))
		else:
			self.definition[-1].append(Property(signature.name, signature.flags, signature.type, signature.value, docstring, getFunc, setFunc, signature.line, signature.line))
#		print(self.definition[-1])
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
		self.definition[-1].append(Group(signature.name, signature.flags, properties, signature.line, aStat.line))
#		print(self.definition[-1])
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
		self.definition[-1].append(Struct(signature.name, members, signature.line, aStat.line))
#		print(self.definition[-1])
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
		self.definition[-1].append(StructMember(signature.line, signature.name, signature.flags, signature.type, signature.value, docstring))
#		print(self.definition[-1])
		self.scope.pop()

	def AssembleScript(self, aStat):
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
		if len(self.scope) != 1 and self.scope[-1] != 0:
			line = self.definition[-1][0].line
			if self.scope[-1] == 1:
				raise SemanticError("Unterminated state definition.", line)
			elif self.scope[-1] == 2:
				raise SemanticError("Unterminated function definition.", line)
			elif self.scope[-1] == 3:
				raise SemanticError("Unterminated event definition.", line)
			elif self.scope[-1] == 4:
				raise SemanticError("Unterminated property definition.", line)
			elif self.scope[-1] == 5:
				raise SemanticError("Unterminated group definition.", line)
			elif self.scope[-1] == 6:
				raise SemanticError("Unterminated struct definition.", line)
		scriptDef = self.definition.pop()
		if scriptDef:
			signature = scriptDef.pop(0)
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
				print(obj)
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
							print(key)
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
			return Script(signature.name, signature.flags, signature.parent, docstring, imports, customEvents, variables, properties, groups, functions, events, states, structs)

	def ValidateScript(self, aScript):
		# Recursively process parent script(s)
		# Process imported script(s)
		# Process properties
		# Process variables
		# Process functions
		# Process events
		# Process states
		# Process structs
		pass

	def GetContext(self, aScript, aLine):
		pass

#4: Putting it all together
def Process(aLex, aSyn, aSem, aSource):
	aSem.Reset()
	tokens = []
	for token in aLex.Process(aSource):
		if token.type == TokenEnum.NEWLINE:
			if tokens:
				stat = aSyn.Process(tokens)
				#print(stat)
				if stat:
					aSem.AssembleScript(stat)
				tokens = []
		elif token.type != TokenEnum.COMMENTLINE and token.type != TokenEnum.COMMENTBLOCK:
			tokens.append(token)
			#print(token)
	script = aSem.BuildScript()
	if script:
		aSem.ValidateScript(script)
		# Add to cache
		return script
	return None

#	Script
#		.name
#		.flags
#			List of KeywordEnum
#		.parent
#			Script
#		.docstring
#			String
#		.imports
#			List of String
#		.customEvents
#			List of String
#		.variables
#			Dict of Variable
#		.properties
#			Dict of Property
#		.groups
#			Dict of Group
#				Dict of Property
#		.structs
#			Dict of Struct
#		.functions
#			Dict of Function
#		.events
#			Dict of Event
#		.states
#			Dict of State